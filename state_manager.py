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
                "julia": {"status": "unknown", "trustLevel": 0},
                "obrien": {"status": "distant_superior", "trustLevel": 0},
                "parsons": {"status": "neighbor", "trustLevel": 0},
                "syme": {"status": "acquaintance", "trustLevel": 0},
                "charrington": {"status": "unknown", "trustLevel": 0}
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
                "room101": False
            },
            "location": "Victory Mansions - Flat 7",
            "date": "April 4, 1984",
            "time": "Morning",
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
