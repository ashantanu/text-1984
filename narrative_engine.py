"""
Narrative Engine for 1984 CLI Game
Handles loading and navigating the narrative graph
"""

import json
from typing import Dict, Any, Optional, List


class NarrativeEngine:
    """Manages narrative graph navigation and story flow"""

    def __init__(self, graph_file: str = "narrative-graph.json"):
        self.graph_file = graph_file
        self.graph: Optional[Dict[str, Any]] = None
        self.load_graph()

    def load_graph(self) -> bool:
        """Load the narrative graph from file"""
        try:
            with open(self.graph_file, 'r') as f:
                self.graph = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading narrative graph: {e}")
            return False

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific node from the graph"""
        if self.graph is None:
            return None

        return self.graph.get("nodes", {}).get(node_id)

    def get_current_scene(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get the current scene data"""
        return self.get_node(node_id)

    def get_choices(self, node_id: str) -> List[Dict[str, Any]]:
        """Get available choices for a node"""
        node = self.get_node(node_id)
        if node is None:
            return []

        return node.get("choices", [])

    def apply_choice_effects(self, choice: Dict[str, Any], state_manager) -> None:
        """Apply the effects of a choice to the game state"""
        effects = choice.get("effects", {})

        # Apply stat changes
        stat_changes = {}
        if "partyLoyalty" in effects:
            stat_changes["partyLoyalty"] = effects["partyLoyalty"]
        if "suspicion" in effects:
            stat_changes["suspicionLevel"] = effects["suspicion"]
        if "thoughtcrime" in effects:
            stat_changes["thoughtcrimeIndex"] = effects["thoughtcrime"]

        if stat_changes:
            state_manager.update_stats(stat_changes)

        # Set flags
        if "flags" in effects:
            state_manager.set_flags(effects["flags"])

        # Update relationships
        if "relationships" in effects:
            for npc, changes in effects["relationships"].items():
                if "trustLevel" in changes:
                    # This would need a relationship update method in state_manager
                    pass

    def get_next_node(self, choice: Dict[str, Any]) -> str:
        """Get the ID of the next node based on choice"""
        return choice.get("nextNode", "")

    def check_requirements(self, choice: Dict[str, Any], state_manager) -> bool:
        """Check if a choice's requirements are met"""
        requirements = choice.get("requirements", {})

        # If no requirements, choice is available
        if not requirements:
            return True

        # Check flag requirements
        if "flags" in requirements:
            required_flags = requirements["flags"]
            for flag in required_flags:
                if not state_manager.check_flag(flag):
                    return False

        # Check stat requirements
        stats = state_manager.get_stats()
        if "minPartyLoyalty" in requirements:
            if stats.get("partyLoyalty", 0) < requirements["minPartyLoyalty"]:
                return False

        if "maxSuspicion" in requirements:
            if stats.get("suspicionLevel", 0) > requirements["maxSuspicion"]:
                return False

        return True

    def get_available_choices(self, node_id: str, state_manager) -> List[Dict[str, Any]]:
        """Get all available choices for current node that meet requirements"""
        all_choices = self.get_choices(node_id)
        return [choice for choice in all_choices if self.check_requirements(choice, state_manager)]

    def is_terminal_node(self, node_id: str) -> bool:
        """Check if a node is a terminal (ending) node"""
        node = self.get_node(node_id)
        if node is None:
            return False

        # A node is terminal if it has no choices or is marked as an ending
        return len(node.get("choices", [])) == 0 or node.get("type") == "ending"

    def get_ascii_art_template(self, node_id: str) -> Optional[str]:
        """Get the ASCII art template name for a node"""
        node = self.get_node(node_id)
        if node is None:
            return None

        return node.get("ascii_art_template")
