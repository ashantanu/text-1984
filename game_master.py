"""
LLM Game Master
The brain of the open-world system
Processes actions, generates consequences, maintains narrative consistency
"""

import json
from typing import Dict, Any, Optional, List
from anthropic import Anthropic
from world_definitions import LOCATIONS, NPCS, get_location, get_npc


class GameMaster:
    """LLM-powered game master that runs the 1984 world"""

    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model_main = "claude-3-5-sonnet-20241022"
        self.model_quick = "claude-3-haiku-20240307"

    def process_action(self,
                      player_action: str,
                      world_state: Dict[str, Any],
                      story_progress: Dict[str, Any],
                      next_beat: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Main processing function - the heart of the game master

        Args:
            player_action: What the player wants to do
            world_state: Complete current world state
            story_progress: Story beat progression data
            next_beat: Next suggested story beat (if any)

        Returns:
            {
                "narrative": str,  # What happens (in Orwell's style)
                "state_changes": dict,  # Stats, flags, inventory, location changes
                "ending_triggered": Optional[str],
                "beat_completed": Optional[str],
                "nudge": Optional[str]  # Subtle guidance toward next beat
            }
        """

        # Build rich context for LLM
        context = self._build_llm_context(world_state, story_progress, next_beat)

        # Create prompt
        prompt = self._create_game_master_prompt(player_action, context)

        # Call Claude
        try:
            response = self.client.messages.create(
                model=self.model_main,
                max_tokens=1500,
                temperature=0.8,  # Higher for creative narrative
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse structured response
            result = self._parse_gm_response(response.content[0].text)

            # Validate result
            result = self._validate_and_fix_result(result)

            return result

        except Exception as e:
            print(f"Error in GameMaster: {e}")
            # Fallback response
            return {
                "narrative": f"You attempt to {player_action}. The moment passes, heavy with the weight of Oceania's oppression.",
                "state_changes": {},
                "ending_triggered": None,
                "beat_completed": None,
                "nudge": None
            }

    def _build_llm_context(self, world_state: Dict, story_progress: Dict, next_beat: Optional[Dict]) -> Dict:
        """Build comprehensive context for LLM"""
        location_id = world_state.get("location", "winston_flat")
        location = get_location(location_id)

        # Get recent actions for context
        recent_actions = world_state.get("recent_actions", [])[-5:]
        recent_summary = [action.get("action", "") for action in recent_actions] if recent_actions else []

        context = {
            "location": location_id,
            "location_name": location.name if location else "Unknown",
            "location_description": location.description if location else "",
            "location_features": location.features if location else [],
            "location_safety": location.safety_level if location else "unknown",
            "npcs_possible": location.npcs_possible if location else [],
            "time": world_state.get("date", "April 4, 1984") + " - " + world_state.get("time_of_day", "morning"),
            "stats": world_state.get("stats", {}),
            "inventory": world_state.get("inventory", []),
            "flags": {k: v for k, v in world_state.get("flags", {}).items() if v},  # Only true flags
            "relationships": world_state.get("relationships", {}),
            "recent_actions": recent_summary,
            "completed_beats": story_progress.get("completed_beats", []),
            "next_beat": next_beat,
            "chapter": world_state.get("chapter", 1)
        }

        return context

    def _create_game_master_prompt(self, action: str, context: Dict) -> str:
        """Create the master prompt for Claude"""

        stats = context['stats']
        suspicion_warning = ""
        if stats.get('suspicionLevel', 0) >= 80:
            suspicion_warning = "⚠️ CRITICAL - ARREST IMMINENT"
        elif stats.get('suspicionLevel', 0) >= 60:
            suspicion_warning = "⚠️ HIGH DANGER"

        # Build NPC context if any are present
        npc_context = ""
        if context['npcs_possible']:
            npc_list = []
            for npc_id in context['npcs_possible']:
                npc = get_npc(npc_id)
                if npc:
                    npc_list.append(f"- {npc.name}: {npc.personality}")
            if npc_list:
                npc_context = "\n\nNPCs WHO MIGHT BE PRESENT:\n" + "\n".join(npc_list)

        # Build next beat context
        beat_context = ""
        if context.get('next_beat'):
            beat = context['next_beat']
            beat_context = f"""
NEXT STORY BEAT (GUIDANCE):
- Title: {beat.get('title', 'Unknown')}
- Description: {beat.get('description', '')}
- Priority: {beat.get('priority', 'medium')}
- Possible Nudges: {', '.join(beat.get('nudges', [])[:2])}

NOTE: This is a SUGGESTED beat, not a requirement. If the player's action naturally progresses toward this beat, complete it. If not, respond to their action organically. DO NOT force the beat."""

        completed_beats_str = ', '.join(context['completed_beats']) if context['completed_beats'] else "None yet"

        prompt = f"""You are the Game Master for an interactive 1984 game. The player (Winston Smith) can take any action they choose. Your job is to:

1. Determine realistic consequences in the oppressive world of 1984
2. Generate narrative in George Orwell's distinctive style (dark, oppressive, precise prose)
3. Update game state based on consequences
4. Subtly nudge toward the next story beat ONLY IF NATURAL (do not force)
5. Detect if an ending has been triggered

CURRENT WORLD STATE:
═══════════════════════════════════════════════════════════════
Location: {context['location_name']}
Description: {context['location_description']}
Features: {', '.join(context['location_features'])}
Safety Level: {context['location_safety']}
Date/Time: {context['time']}
Chapter: {context['chapter']}

WINSTON'S STATS:
═══════════════════════════════════════════════════════════════
- Party Loyalty: {stats.get('partyLoyalty', 50)}/100
- Suspicion Level: {stats.get('suspicionLevel', 15)}/100 {suspicion_warning}
- Thoughtcrime Index: {stats.get('thoughtcrimeIndex', 10)}/100

WINSTON'S STATE:
═══════════════════════════════════════════════════════════════
Inventory: {', '.join(context['inventory']) if context['inventory'] else 'Empty pockets'}
Important Flags: {', '.join(context['flags'].keys()) if context['flags'] else 'None'}
Recent Actions: {', '.join(context['recent_actions'][-3:]) if context['recent_actions'] else 'None'}
{npc_context}

STORY PROGRESS:
═══════════════════════════════════════════════════════════════
Completed Beats: {completed_beats_str}
{beat_context}

PLAYER ACTION:
═══════════════════════════════════════════════════════════════
"{action}"

═══════════════════════════════════════════════════════════════

RESPOND IN THIS EXACT JSON FORMAT (IMPORTANT - MUST BE VALID JSON):
{{
    "narrative": "2-3 paragraphs in Orwell's style describing what happens. Use his precise, dark, oppressive prose. Show don't tell. Make the reader FEEL the weight of the Party's surveillance.",

    "state_changes": {{
        "stats": {{
            "partyLoyalty": 0,
            "suspicionLevel": 0,
            "thoughtcrimeIndex": 0
        }},
        "flags_set": [],
        "flags_unset": [],
        "inventory_add": [],
        "inventory_remove": [],
        "location": null,
        "time_advance": null,
        "relationships": {{}}
    }},

    "beat_completed": null,
    "ending_triggered": null,
    "nudge": null
}}

CRITICAL RULES FOR YOUR RESPONSE:
═══════════════════════════════════════════════════════════════

1. NARRATIVE STYLE:
   - Write like George Orwell - precise, dark, oppressive
   - Short, declarative sentences when tension is high
   - Show physical sensations (varicose ulcer, telescreen static, gin burning throat)
   - Emphasize surveillance, fear, doublethink
   - NO modern slang, NO game-y language, NO breaking 4th wall
   - Make the reader feel the totalitarian oppression

2. WORLD CONSISTENCY:
   - Big Brother is always watching (except in specific safe locations)
   - Thoughtcrime is dangerous - suspicion builds gradually
   - At suspicion >= 95, set ending_triggered to "arrested_early"
   - The Party controls everything - escape is nearly impossible
   - Proles are ignored by the Party (lower suspicion in prole_district)
   - Telescreens hear everything in most locations

3. STAT CHANGES:
   - Thoughtcrime actions: +5 to +30 thoughtcrime, -5 to -20 loyalty
   - Risky actions in public: +5 to +20 suspicion
   - Loyal actions: +5 to +15 loyalty, -2 to -5 suspicion
   - Actions in private/alcove: minimal suspicion change
   - Actions in prole district: 50% less suspicion

4. BEAT COMPLETION:
   - Only set beat_completed if the action clearly fulfills that beat
   - Don't force beats - let them happen naturally
   - Check prerequisites from the beat definition

5. NUDGING:
   - Only provide nudge if natural and not intrusive
   - Nudges are environmental cues, not instructions
   - Examples: "You notice...", "A thought surfaces...", "Something catches your eye..."
   - Can be null if no nudge is appropriate

6. ENDINGS:
   - arrested_early: suspicion >= 95
   - suicide: player kills themselves
   - escape_attempt: player tries to flee and fails
   - Check for these triggers

7. JSON FORMAT:
   - MUST be valid JSON - use double quotes, escape special characters
   - All fields must be present, use null for empty values
   - stat changes are DELTAS (changes), not absolute values

EXAMPLES OF GOOD NARRATIVE:
"The words burn on your tongue. You glance at the telescreen - its red light glows steadily, watching, recording. The impulse to speak dies. You swallow it down like Victory Gin, bitter and corrosive."

"Your hand moves to the diary in your drawer. The blank pages seem to accuse you of cowardice. But the telescreen drones on just meters away. To write would be to sign your death warrant. Or perhaps you've already signed it simply by wanting to."

Now generate your response for the player's action:"""

        return prompt

    def _parse_gm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response"""
        try:
            # Claude should return valid JSON
            # Clean up any markdown code blocks if present
            cleaned = response_text.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.startswith("```"):
                cleaned = cleaned[3:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()

            result = json.loads(cleaned)
            return result

        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Response text: {response_text[:500]}")

            # Fallback: try to extract narrative at least
            return {
                "narrative": response_text if len(response_text) < 1000 else response_text[:1000],
                "state_changes": {},
                "beat_completed": None,
                "ending_triggered": None,
                "nudge": None
            }

    def _validate_and_fix_result(self, result: Dict) -> Dict:
        """Validate and fix the LLM result if needed"""
        # Ensure all required fields exist
        if "narrative" not in result:
            result["narrative"] = "The moment passes in silence."

        if "state_changes" not in result:
            result["state_changes"] = {}

        if "stats" not in result["state_changes"]:
            result["state_changes"]["stats"] = {}

        # Ensure stat changes are reasonable (-50 to +50)
        for stat in ["partyLoyalty", "suspicionLevel", "thoughtcrimeIndex"]:
            if stat in result["state_changes"]["stats"]:
                value = result["state_changes"]["stats"][stat]
                result["state_changes"]["stats"][stat] = max(-50, min(50, value))

        # Ensure lists exist
        for list_field in ["flags_set", "flags_unset", "inventory_add", "inventory_remove"]:
            if list_field not in result["state_changes"]:
                result["state_changes"][list_field] = []

        # Ensure optional fields exist
        if "beat_completed" not in result:
            result["beat_completed"] = None

        if "ending_triggered" not in result:
            result["ending_triggered"] = None

        if "nudge" not in result:
            result["nudge"] = None

        return result

    def generate_scene_description(self, location_id: str, context: Dict) -> str:
        """
        Generate rich scene description for a location

        Args:
            location_id: The location to describe
            context: Context including time, recent events, stats

        Returns:
            Orwellian prose describing the scene
        """
        location = get_location(location_id)
        if not location:
            return "You find yourself in an unfamiliar place."

        stats = context.get('stats', {})
        recent_events = context.get('recent_events', [])

        prompt = f"""You are narrating a scene in an interactive 1984 game.

Generate a vivid description of this location in George Orwell's distinctive style.

LOCATION:
Name: {location.name}
Description: {location.description}
Features: {', '.join(location.features)}

CONTEXT:
Time: {context.get('time', 'Unknown time')}
Recent Events: {', '.join(recent_events) if recent_events else 'None'}

WINSTON'S CURRENT STATE:
- Party Loyalty: {stats.get('partyLoyalty', 50)}/100
- Suspicion: {stats.get('suspicionLevel', 15)}/100
- Thoughtcrime: {stats.get('thoughtcrimeIndex', 10)}/100

Generate 2-3 paragraphs that:
1. Describe what Winston sees, hears, smells
2. Capture the oppressive atmosphere of Oceania
3. Note any NPCs or significant features
4. Reflect Winston's current emotional state based on his stats
5. Use Orwell's precise, dark, minimalist style

HIGH SUSPICION = paranoia, watching shadows, fear
HIGH THOUGHTCRIME = defiance, awareness of lies, rebellion simmering
LOW LOYALTY = disconnection from Party slogans, doubt

Write in Orwell's style - short sentences when tense, sensory details, oppressive atmosphere:"""

        try:
            response = self.client.messages.create(
                model=self.model_main,
                max_tokens=600,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"Error generating scene: {e}")
            return location.description

    def generate_npc_dialogue(self, npc_id: str, context: str, player_said: str = "") -> str:
        """
        Generate dialogue for an NPC

        Args:
            npc_id: The NPC speaking
            context: Context of the conversation
            player_said: What the player said (if anything)

        Returns:
            The NPC's response
        """
        npc = get_npc(npc_id)
        if not npc:
            return "..."

        prompt = f"""Generate dialogue for {npc.name} in the 1984 game.

NPC: {npc.name}
Role: {npc.role}
Personality: {npc.personality}
Dialogue Style: {npc.dialogue_style}

Context: {context}
Player said: "{player_said if player_said else 'Nothing yet'}"

Generate 1-3 sentences of dialogue that:
1. Matches the character's personality and speech patterns
2. Fits the 1984 world (totalitarian, oppressive)
3. Advances or responds to the situation
4. Sounds natural for this character

Do not use quotation marks in your response - just the dialogue text.

Examples:
- Julia (if plotting): "We can meet Sunday in the countryside. Nobody watches the proles there."
- Parsons (enthusiastic): "Did you hear, old man? We're winning the war! My kids caught a spy yesterday!"
- O'Brien (enigmatic): "We shall meet again in a place where there is no darkness."

Generate {npc.name}'s dialogue now:"""

        try:
            response = self.client.messages.create(
                model=self.model_main,
                max_tokens=200,
                temperature=0.9,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"Error generating dialogue: {e}")
            return "..."
