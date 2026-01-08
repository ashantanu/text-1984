"""
LLM Processor for 1984 CLI Game (Refactored for Open-World)
Handles Claude API integration - now integrates with GameMaster for open-world actions
"""

import os
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# Import new systems
from game_master import GameMaster
from action_validator import ActionValidator

# Load environment variables from .env file
load_dotenv()


class LLMProcessor:
    """Processes user input using Claude API - now with open-world support"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM processor with Anthropic API key"""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Please create a .env file with your API key.")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

        # Initialize GameMaster for open-world processing
        self.game_master = GameMaster(self.api_key)

    # =============================================================================
    # NEW OPEN-WORLD METHODS
    # =============================================================================

    def process_open_world_action(self, user_input: str, world_state: Dict[str, Any],
                                   story_progress: Dict[str, Any], next_beat: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Process open-world user action (NEW METHOD)

        Args:
            user_input: What the player wants to do
            world_state: Complete current world state
            story_progress: Story beat progression
            next_beat: Next suggested story beat

        Returns:
            {
                "type": "success" | "invalid" | "error",
                "narrative": str,
                "state_changes": dict,
                "beat_completed": str | None,
                "ending_triggered": str | None,
                "nudge": str | None,
                "reason": str (if invalid)
            }
        """

        # 1. Validate the action
        validator = ActionValidator(world_state)
        is_valid, reason, context = validator.validate_action(user_input)

        if not is_valid:
            return {
                "type": "invalid",
                "narrative": reason,
                "reason": reason,
                "state_changes": {},
                "beat_completed": None,
                "ending_triggered": None,
                "nudge": None
            }

        # 2. Process with Game Master
        try:
            result = self.game_master.process_action(
                user_input,
                world_state,
                story_progress,
                next_beat
            )

            result["type"] = "success"
            return result

        except Exception as e:
            print(f"Error in open-world processing: {e}")
            return {
                "type": "error",
                "narrative": f"You attempt to {user_input}. The moment passes, heavy with the oppressive weight of Oceania.",
                "state_changes": {},
                "beat_completed": None,
                "ending_triggered": None,
                "nudge": None,
                "reason": str(e)
            }

    def generate_scene_description(self, location_id: str, world_state: Dict[str, Any]) -> str:
        """
        Generate scene description for current location

        Args:
            location_id: Current location ID
            world_state: Current world state

        Returns:
            Scene narrative in Orwell's style
        """
        try:
            context = {
                'time': world_state.get('date', 'April 4, 1984') + " " + world_state.get('time_of_day', 'morning'),
                'stats': world_state.get('stats', {}),
                'recent_events': [a.get('action', '') for a in world_state.get('recent_actions', [])][-3:]
            }

            return self.game_master.generate_scene_description(location_id, context)

        except Exception as e:
            print(f"Error generating scene: {e}")
            from world_definitions import get_location
            location = get_location(location_id)
            return location.description if location else "You find yourself in an unfamiliar place."

    # =============================================================================
    # BACKWARD COMPATIBILITY METHODS (for old choice-based system)
    # =============================================================================

    def process_user_input(self, user_input: str, available_choices: List[Dict[str, Any]],
                          current_scene: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user's natural language input and map to game action (OLD METHOD - backward compatibility)

        Returns:
            {
                "type": "choice" | "command" | "clarification_needed",
                "choice_index": int (if type is "choice"),
                "command": str (if type is "command"),
                "response": str (narrative response to show user)
            }
        """

        # First check if input is a number
        if user_input.strip().isdigit():
            choice_num = int(user_input.strip())
            if 1 <= choice_num <= len(available_choices):
                return {
                    "type": "choice",
                    "choice_index": choice_num - 1,
                    "response": ""
                }

        # Build the prompt for Claude
        prompt = self._build_prompt(user_input, available_choices, current_scene, game_state)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=0.7,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            result_text = response.content[0].text.strip()

            # Parse Claude's response
            return self._parse_llm_response(result_text, available_choices)

        except Exception as e:
            print(f"Error calling Claude API: {e}")
            return {
                "type": "clarification_needed",
                "response": "I'm having trouble understanding. Please try rephrasing or enter a number (1, 2, 3, etc.)"
            }

    def _build_prompt(self, user_input: str, available_choices: List[Dict[str, Any]],
                     current_scene: Dict[str, Any], game_state: Dict[str, Any]) -> str:
        """Build the prompt for Claude to interpret user input (OLD METHOD)"""

        scene_title = current_scene.get("title", "")
        scene_narrative = current_scene.get("narrative", "")
        stats = game_state.get("stats", {})

        # Format choices for the prompt
        choices_text = ""
        for i, choice in enumerate(available_choices, 1):
            choices_text += f"{i}. {choice.get('text', '')}\n"

        prompt = f"""You are the game master for a 1984 (George Orwell) interactive CLI game. The player has just typed something, and you need to interpret their intent and map it to one of the available game actions.

CURRENT SCENE: {scene_title}
CONTEXT: {scene_narrative[:200]}...

PLAYER STATS:
- Party Loyalty: {stats.get('partyLoyalty', 0)}/100
- Suspicion Level: {stats.get('suspicionLevel', 0)}/100
- Thoughtcrime Index: {stats.get('thoughtcrimeIndex', 0)}/100

AVAILABLE ACTIONS:
{choices_text}

PLAYER INPUT: "{user_input}"

Your task:
1. Interpret what the player wants to do
2. Map their intent to one of the numbered choices above
3. If their input doesn't clearly match any choice, ask for clarification
4. Stay in character as the omniscient narrator of 1984

Respond in this EXACT format:

CHOICE: [number 1-{len(available_choices)}]
RESPONSE: [A brief narrative response (1-2 sentences) that acknowledges their action in the style of Orwell's 1984]

OR if you need clarification:

CLARIFICATION: [Ask the player to be more specific about their intent]

Examples:
- If player says "look at the poster" and choice 1 is about observing the poster → "CHOICE: 1\\nRESPONSE: You pause, your eyes drawn to the enormous face gazing down from the wall."
- If player says "I don't trust this" and it's unclear → "CLARIFICATION: What specifically do you want to do? You can observe the poster, hurry inside, or check the telescreen."
"""

        return prompt

    def _parse_llm_response(self, response_text: str, available_choices: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse Claude's response into a structured result (OLD METHOD)"""

        lines = response_text.strip().split('\n')

        # Check for CHOICE response
        if response_text.startswith("CHOICE:"):
            try:
                # Extract choice number
                choice_line = [line for line in lines if line.startswith("CHOICE:")][0]
                choice_num = int(choice_line.split(":")[1].strip())

                # Extract narrative response
                response_lines = [line for line in lines if line.startswith("RESPONSE:")]
                narrative_response = ""
                if response_lines:
                    narrative_response = response_lines[0].split(":", 1)[1].strip()

                # Validate choice number
                if 1 <= choice_num <= len(available_choices):
                    return {
                        "type": "choice",
                        "choice_index": choice_num - 1,
                        "response": narrative_response
                    }
            except (ValueError, IndexError):
                pass

        # Check for CLARIFICATION response
        if response_text.startswith("CLARIFICATION:"):
            clarification = response_text.split(":", 1)[1].strip()
            return {
                "type": "clarification_needed",
                "response": clarification
            }

        # Fallback: couldn't parse response
        return {
            "type": "clarification_needed",
            "response": "I'm not sure what you want to do. Please choose a numbered option or be more specific."
        }

    def generate_contextual_narrative(self, scene: Dict[str, Any], previous_choice: str,
                                     game_state: Dict[str, Any]) -> str:
        """Generate additional contextual narrative based on player's journey (OLD METHOD)"""

        scene_title = scene.get("title", "")
        stats = game_state.get("stats", {})

        prompt = f"""You are narrating a 1984 interactive game. The player just made this choice: "{previous_choice}"

They are now at: {scene_title}

Current stats:
- Party Loyalty: {stats.get('partyLoyalty', 0)}/100
- Suspicion Level: {stats.get('suspicionLevel', 0)}/100
- Thoughtcrime: {stats.get('thoughtcrimeIndex', 0)}/100

Generate a brief (1-2 sentences) transitional narrative in Orwell's style that:
1. Acknowledges the consequence of their previous action
2. Sets the mood for the current scene
3. Reflects their current standing (high suspicion = paranoia, high thoughtcrime = defiance, etc.)

Keep it atmospheric and true to the novel's tone."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                temperature=0.8,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"Error generating narrative: {e}")
            return ""
