"""
State Manager for 1984 CLI Game
Handles loading, saving, and updating game state
"""

import json
import os
from typing import Dict, Any, Optional
from datetime import datetime
import uuid


class StateManager:
    """Manages game state persistence and updates"""

    def __init__(self, state_file: str = "game-state.json"):
        self.state_file = state_file
        self.state: Optional[Dict[str, Any]] = None

    def load_state(self) -> Dict[str, Any]:
        """Load game state from file, or create new state if file doesn't exist"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    self.state = json.load(f)
                return self.state
            except json.JSONDecodeError:
                print("Warning: Corrupted save file. Starting new game.")
                return self.create_new_state()
        else:
            return self.create_new_state()

    def create_new_state(self) -> Dict[str, Any]:
        """Create a fresh game state"""
        self.state = {
            "gameId": str(uuid.uuid4()),
            "player": {
                "name": "Winston Smith",
                "occupation": "Records Department, Ministry of Truth"
            },
            "stats": {
                "partyLoyalty": 50,
                "suspicionLevel": 15,
                "thoughtcrimeIndex": 10
            },
            "resources": {
                "razors": 2,
                "cigarettes": 5,
                "chocolate": 0
            },
            "relationships": {
                "julia": {"status": "unknown", "trustLevel": 0, "met": False, "secrets_known": []},
                "obrien": {"status": "distant_superior", "trustLevel": 0, "met": False, "secrets_known": []},
                "parsons": {"status": "neighbor", "trustLevel": 30, "met": True, "secrets_known": []},
                "syme": {"status": "acquaintance", "trustLevel": 20, "met": True, "secrets_known": []},
                "charrington": {"status": "unknown", "trustLevel": 0, "met": False, "secrets_known": []}
            },
            "inventory": [
                "Victory Gin ration card",
                "Work assignment papers"
            ],
            "flags": {
                "diaryPurchased": False,
                "diaryWritten": False,
                "juliaNotReceived": False,
                "juliaMet": False,
                "obrienContact": False,
                "brotherhoodJoined": False,
                "goldsteinBookRead": False,
                "arrested": False,
                "room101": False,
                # New flags for open-world
                "has_diary": False,
                "diary_started": False,
                "met_julia": False,
                "received_note": False,
                "rented_room": False,
                "knows_obriens_address": False,
                "joined_brotherhood": False,
                "visited_charringtons": False
            },
            # New: Use location ID instead of full name
            "location": "winston_flat",
            "date": "April 4, 1984",
            "time": "Morning",
            # New fields for open-world
            "time_of_day": "morning",  # morning, afternoon, evening, night
            "chapter": 1,
            "recent_actions": [],  # Last 10 actions
            "completed_beats": [],  # Story beats completed
            # Backward compatibility
            "currentNode": "prologue_start",
            "choiceHistory": [],
            "gameStarted": datetime.now().isoformat(),
            "lastSaved": datetime.now().isoformat()
        }
        return self.state

    def save_state(self) -> bool:
        """Save current state to file"""
        if self.state is None:
            return False

        try:
            self.state["lastSaved"] = datetime.now().isoformat()
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving state: {e}")
            return False

    def update_stats(self, changes: Dict[str, int]) -> None:
        """Update player stats with given changes"""
        if self.state is None:
            return

        for stat, change in changes.items():
            if stat in self.state["stats"]:
                new_value = self.state["stats"][stat] + change
                # Clamp values between 0 and 100
                self.state["stats"][stat] = max(0, min(100, new_value))

    def set_flags(self, flags: list) -> None:
        """Set game flags to True"""
        if self.state is None:
            return

        for flag in flags:
            if flag in self.state["flags"]:
                self.state["flags"][flag] = True

    def check_flag(self, flag: str) -> bool:
        """Check if a flag is set"""
        if self.state is None:
            return False
        return self.state["flags"].get(flag, False)

    def add_to_inventory(self, item: str) -> None:
        """Add item to player inventory"""
        if self.state is None:
            return

        if item not in self.state["inventory"]:
            self.state["inventory"].append(item)

    def update_location(self, location: str) -> None:
        """Update player's current location"""
        if self.state is None:
            return
        self.state["location"] = location

    def set_current_node(self, node_id: str) -> None:
        """Set the current narrative node"""
        if self.state is None:
            return
        self.state["currentNode"] = node_id

    def record_choice(self, choice_id: str, choice_text: str, node_id: str) -> None:
        """Record a choice in the history"""
        if self.state is None:
            return

        self.state["choiceHistory"].append({
            "timestamp": datetime.now().isoformat(),
            "nodeId": node_id,
            "choiceId": choice_id,
            "choiceText": choice_text,
            "stats": self.state["stats"].copy()
        })

    def get_stats(self) -> Dict[str, int]:
        """Get current player stats"""
        if self.state is None:
            return {}
        return self.state["stats"].copy()

    def get_resources(self) -> Dict[str, int]:
        """Get current player resources"""
        if self.state is None:
            return {}
        return self.state["resources"].copy()

    def check_game_over(self) -> Optional[str]:
        """Check if game over conditions are met"""
        if self.state is None:
            return None

        stats = self.state["stats"]

        # Critical suspicion level
        if stats["suspicionLevel"] >= 90:
            return "arrested_high_suspicion"

        # Other game over conditions can be added here

        return None

    # =============================================================================
    # NEW METHODS FOR OPEN-WORLD SYSTEM
    # =============================================================================

    def record_action(self, action: str, result: Dict[str, Any]) -> None:
        """
        Record an action and its result

        Args:
            action: The player's action
            result: The result from GameMaster
        """
        if self.state is None:
            return

        if "recent_actions" not in self.state:
            self.state["recent_actions"] = []

        self.state["recent_actions"].append({
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "location": self.state.get("location", "unknown"),
            "result_summary": result.get("narrative", "")[:100]  # First 100 chars
        })

        # Keep only last 10 actions
        if len(self.state["recent_actions"]) > 10:
            self.state["recent_actions"] = self.state["recent_actions"][-10:]

    def complete_beat(self, beat_id: str) -> None:
        """
        Mark a story beat as completed

        Args:
            beat_id: ID of the completed beat
        """
        if self.state is None:
            return

        if "completed_beats" not in self.state:
            self.state["completed_beats"] = []

        if beat_id not in self.state["completed_beats"]:
            self.state["completed_beats"].append(beat_id)

    def update_relationship(self, npc_id: str, field: str, value: Any) -> None:
        """
        Update a relationship field for an NPC

        Args:
            npc_id: ID of the NPC
            field: Field to update (status, trustLevel, met, secrets_known)
            value: New value
        """
        if self.state is None:
            return

        if "relationships" not in self.state:
            self.state["relationships"] = {}

        if npc_id not in self.state["relationships"]:
            self.state["relationships"][npc_id] = {
                "status": "unknown",
                "trustLevel": 0,
                "met": False,
                "secrets_known": []
            }

        self.state["relationships"][npc_id][field] = value

    def unset_flags(self, flags: list) -> None:
        """
        Unset game flags (set to False)

        Args:
            flags: List of flag names to unset
        """
        if self.state is None:
            return

        for flag in flags:
            if flag in self.state.get("flags", {}):
                self.state["flags"][flag] = False
            else:
                # Create the flag and set to False
                self.state["flags"][flag] = False

    def remove_from_inventory(self, item: str) -> None:
        """
        Remove item from player inventory

        Args:
            item: Item ID to remove
        """
        if self.state is None:
            return

        if item in self.state.get("inventory", []):
            self.state["inventory"].remove(item)

    def apply_changes(self, state_changes: Dict[str, Any]) -> None:
        """
        Apply state changes from GameMaster result

        Args:
            state_changes: Dictionary of changes to apply
        """
        if self.state is None:
            return

        # Apply stat changes
        if "stats" in state_changes:
            self.update_stats(state_changes["stats"])

        # Set flags
        if "flags_set" in state_changes:
            self.set_flags(state_changes["flags_set"])

        # Unset flags
        if "flags_unset" in state_changes:
            self.unset_flags(state_changes["flags_unset"])

        # Add inventory items
        if "inventory_add" in state_changes:
            for item in state_changes["inventory_add"]:
                self.add_to_inventory(item)

        # Remove inventory items
        if "inventory_remove" in state_changes:
            for item in state_changes["inventory_remove"]:
                self.remove_from_inventory(item)

        # Update location
        if "location" in state_changes and state_changes["location"]:
            self.update_location(state_changes["location"])

        # Advance time
        if "time_advance" in state_changes and state_changes["time_advance"]:
            self._advance_time(state_changes["time_advance"])

        # Update relationships
        if "relationships" in state_changes:
            for npc_id, changes in state_changes["relationships"].items():
                for field, value in changes.items():
                    self.update_relationship(npc_id, field, value)

    def _advance_time(self, time_str: str) -> None:
        """
        Advance game time

        Args:
            time_str: Time to advance (e.g., "1 hour", "2 hours", "1 day")
        """
        if self.state is None:
            return

        # Simple time advancement
        time_parts = time_str.lower().split()
        if len(time_parts) < 2:
            return

        try:
            amount = int(time_parts[0])
            unit = time_parts[1]

            if "hour" in unit:
                # Advance hours
                time_of_day = self.state.get("time_of_day", "morning")
                times = ["morning", "afternoon", "evening", "night"]
                current_idx = times.index(time_of_day) if time_of_day in times else 0

                # Each time period is roughly 6 hours
                periods_to_advance = amount // 6
                new_idx = (current_idx + periods_to_advance) % 4

                self.state["time_of_day"] = times[new_idx]

            elif "day" in unit:
                # Advance days
                self.state["time_of_day"] = "morning"
                # Could also update the date here

        except (ValueError, IndexError):
            pass  # Ignore invalid time strings

    def get_completed_beats(self) -> list:
        """Get list of completed story beats"""
        if self.state is None:
            return []
        return self.state.get("completed_beats", [])

    def get_recent_actions(self) -> list:
        """Get list of recent actions"""
        if self.state is None:
            return []
        return self.state.get("recent_actions", [])

    def get_chapter(self) -> int:
        """Get current chapter"""
        if self.state is None:
            return 1
        return self.state.get("chapter", 1)

    def set_chapter(self, chapter: int) -> None:
        """Set current chapter"""
        if self.state is None:
            return
        self.state["chapter"] = chapter

    def get_time_of_day(self) -> str:
        """Get current time of day"""
        if self.state is None:
            return "morning"
        return self.state.get("time_of_day", "morning")

    def get_location(self) -> str:
        """Get current location ID"""
        if self.state is None:
            return "winston_flat"
        return self.state.get("location", "winston_flat")
