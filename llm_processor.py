"""
LLM Processor for 1984 CLI Game
Handles Claude API integration for processing natural language input
"""

import os
from typing import Dict, Any, List, Optional
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMProcessor:
    """Processes user input using Claude API to map to game actions"""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the LLM processor with Anthropic API key"""
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found. Please create a .env file with your API key.")

        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def process_user_input(self, user_input: str, available_choices: List[Dict[str, Any]],
                          current_scene: Dict[str, Any], game_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process user's natural language input and map to game action

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
        """Build the prompt for Claude to interpret user input"""

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
        """Parse Claude's response into a structured result"""

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
        """Generate additional contextual narrative based on player's journey"""

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
