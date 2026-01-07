"""
Ending Manager
Detects ending conditions and generates ending narratives for 1984 game
"""

import json
from typing import Optional, Dict, Any


class EndingManager:
    """Manages game ending detection and narratives"""

    def __init__(self, beats_file: str = "story_beats.json"):
        self.beats_file = beats_file
        self.alternate_endings = self._load_alternate_endings()
        self.canonical_ending = self._load_canonical_ending()

    def _load_alternate_endings(self) -> Dict[str, Any]:
        """Load alternate ending definitions from story_beats.json"""
        try:
            with open(self.beats_file, 'r') as f:
                beats_data = json.load(f)
                return beats_data.get('alternate_endings', {})
        except Exception as e:
            print(f"Error loading alternate endings: {e}")
            return {}

    def _load_canonical_ending(self) -> Optional[Dict]:
        """Load the canonical ending from story_beats.json"""
        try:
            with open(self.beats_file, 'r') as f:
                beats_data = json.load(f)
                beats = beats_data.get('beats', {})
                return beats.get('canonical_ending')
        except Exception as e:
            print(f"Error loading canonical ending: {e}")
            return None

    def check_ending(self, world_state: Dict, recent_action: str = "") -> Optional[Dict]:
        """
        Check if an ending has been triggered

        Args:
            world_state: Current complete world state
            recent_action: The action the player just took

        Returns:
            Ending data dictionary if triggered, None otherwise
        """

        flags = world_state.get('flags', {})
        stats = world_state.get('stats', {})
        location = world_state.get('location', '')

        # 1. CHECK CANONICAL ENDING (Room 101 complete)
        if flags.get('room_101_completed') or flags.get('loves_big_brother'):
            return self._get_ending('canonical_ending')

        # 2. CHECK CRITICAL SUSPICION (Arrested Early)
        if stats.get('suspicionLevel', 0) >= 95:
            # If not already arrested, this triggers early arrest
            if not flags.get('arrested'):
                return self._get_ending('arrested_early')

        # 3. CHECK SUICIDE ENDING
        suicide_keywords = ['kill myself', 'suicide', 'jump', 'end it', 'die']
        if any(keyword in recent_action.lower() for keyword in suicide_keywords):
            # Only trigger if thoughtcrime is high enough (indicates awareness)
            if stats.get('thoughtcrimeIndex', 0) >= 60:
                return self._get_ending('suicide')

        # 4. CHECK ESCAPE ATTEMPT
        escape_keywords = ['escape', 'flee', 'run away', 'leave oceania', 'get out']
        if any(keyword in recent_action.lower() for keyword in escape_keywords):
            # Escape is nearly impossible
            if stats.get('suspicionLevel', 0) >= 60:
                return self._get_ending('escape_attempt')

        # 5. CHECK DISAPPEAR AMONG PROLES
        if location == 'prole_district' and flags.get('abandoned_identity'):
            if stats.get('suspicionLevel', 0) >= 70:
                return self._get_ending('disappear_proles')

        # 6. CHECK ARREST IN ROOM (The Trap Triggers)
        if location == 'room_above_shop' and flags.get('read_goldsteins_book'):
            # The room was always a trap - trigger arrest
            return self._get_ending('arrest')

        # No ending triggered
        return None

    def _get_ending(self, ending_id: str) -> Optional[Dict]:
        """
        Get ending data by ID

        Args:
            ending_id: The ID of the ending

        Returns:
            Ending dictionary with type, title, narrative
        """

        # Check canonical ending first
        if ending_id == 'canonical_ending':
            if self.canonical_ending:
                return {
                    "id": "canonical_ending",
                    "type": "canonical",
                    "title": self.canonical_ending.get('title', 'He Loved Big Brother'),
                    "narrative": self.canonical_ending.get('ending_data', {}).get('narrative', ''),
                    "achievement": self.canonical_ending.get('ending_data', {}).get('achievement', ''),
                    "stats_shown": True
                }

        # Check alternate endings
        if ending_id in self.alternate_endings:
            ending = self.alternate_endings[ending_id]
            return {
                "id": ending_id,
                "type": ending.get('type', 'alternate'),
                "title": ending.get('title', 'The End'),
                "narrative": ending.get('narrative', 'Your story ends here.'),
                "stats_shown": True
            }

        # Fallback endings
        return self._get_fallback_ending(ending_id)

    def _get_fallback_ending(self, ending_id: str) -> Dict:
        """
        Provide fallback endings if not defined in JSON

        Args:
            ending_id: The ending type

        Returns:
            Basic ending dictionary
        """

        fallbacks = {
            "arrested_early": {
                "id": "arrested_early",
                "type": "arrest",
                "title": "Vaporized",
                "narrative": "Your suspicion level reached critical. The Thought Police came in the night.\n\nYou were arrested before the major events could unfold. After interrogation in the Ministry of Love, you were vaporized. You never existed. All records of Winston Smith have been destroyed.\n\nBig Brother is eternal.",
                "stats_shown": True
            },

            "arrest": {
                "id": "arrest",
                "type": "arrest",
                "title": "The Trap Springs",
                "narrative": "The telescreen in the room above the shop comes to life. It was there all along, hidden behind the picture.\n\n'You are the dead,' it says.\n\nMr. Charrington appears at the door, transformed. Gone is the old prole. Before you stands a Thought Police officer, younger than you thought, cold-eyed and efficient.\n\nIt was all a trap. The room, the shop, the kindly old man - all a honeypot to catch rebels.\n\nYou and Julia are arrested.",
                "stats_shown": True
            },

            "suicide": {
                "id": "suicide",
                "type": "death",
                "title": "Final Act of Rebellion",
                "narrative": "In your last moment, you are free.\n\nYou throw yourself from the roof of the Ministry of Truth. The wind rushes past. For just a second, you feel liberation - your thoughts still your own, unbroken by Room 101.\n\nThe Party cannot break you. You die with your mind intact.\n\nIt is a small victory, but it is yours.",
                "stats_shown": True
            },

            "escape_attempt": {
                "id": "escape_attempt",
                "type": "death",
                "title": "Death While Fleeing",
                "narrative": "You attempt to flee Oceania. It is impossible. The Party controls everything.\n\nYou don't make it far. A Thought Police patrol intercepts you at the checkpoint. You run. They shoot.\n\nA quick death - perhaps a mercy compared to Room 101.\n\nYour body is left where it falls as a warning to others.",
                "stats_shown": True
            },

            "disappear_proles": {
                "id": "disappear_proles",
                "type": "survival",
                "title": "Lost Among the Proles",
                "narrative": "You disappear into the prole districts, abandoning your identity as Winston Smith.\n\nThe Party searches but cannot find you among the masses. You live in obscurity, poor but free in a way Party members can never be.\n\nYou are always looking over your shoulder. The Thought Police could come at any time. But for now, you breathe free air.\n\nIf there is hope, it lies in the proles. Perhaps you have found it.",
                "stats_shown": True
            }
        }

        return fallbacks.get(ending_id, {
            "id": ending_id,
            "type": "unknown",
            "title": "The End",
            "narrative": "Your story ends here, in the shadow of Big Brother.",
            "stats_shown": True
        })

    def get_ending_summary(self, ending_data: Dict, final_state: Dict) -> str:
        """
        Generate a complete ending summary with stats

        Args:
            ending_data: The ending data
            final_state: Final game state

        Returns:
            Formatted ending summary
        """

        title = ending_data.get('title', 'THE END')
        narrative = ending_data.get('narrative', '')
        stats = final_state.get('stats', {})
        choice_count = len(final_state.get('choiceHistory', []))

        summary = f"\n{'═' * 70}\n"
        summary += f"{title.center(70)}\n"
        summary += f"{'═' * 70}\n\n"
        summary += f"{narrative}\n\n"
        summary += f"{'═' * 70}\n"
        summary += f"{'FINAL STATISTICS'.center(70)}\n"
        summary += f"{'═' * 70}\n\n"
        summary += f"Party Loyalty: {stats.get('partyLoyalty', 0)}/100\n"
        summary += f"Suspicion Level: {stats.get('suspicionLevel', 0)}/100\n"
        summary += f"Thoughtcrime Index: {stats.get('thoughtcrimeIndex', 0)}/100\n\n"
        summary += f"Choices Made: {choice_count}\n"
        summary += f"Story Beats Completed: {len(final_state.get('completed_beats', []))}\n\n"
        summary += f"{'═' * 70}\n"
        summary += f"{'BIG BROTHER IS WATCHING YOU'.center(70)}\n"
        summary += f"{'═' * 70}\n"

        return summary

    def is_ending_triggered(self, world_state: Dict, recent_action: str = "") -> bool:
        """
        Quick check if any ending is triggered

        Args:
            world_state: Current world state
            recent_action: Recent player action

        Returns:
            True if an ending should trigger, False otherwise
        """
        return self.check_ending(world_state, recent_action) is not None

    def get_all_possible_endings(self) -> List[Dict]:
        """
        Get list of all possible endings

        Returns:
            List of ending dictionaries
        """
        endings = []

        # Add canonical
        if self.canonical_ending:
            endings.append({
                "id": "canonical_ending",
                "title": self.canonical_ending.get('title', 'He Loved Big Brother'),
                "type": "canonical"
            })

        # Add alternates
        for ending_id, ending_data in self.alternate_endings.items():
            endings.append({
                "id": ending_id,
                "title": ending_data.get('title', 'Unknown'),
                "type": ending_data.get('type', 'alternate')
            })

        return endings
