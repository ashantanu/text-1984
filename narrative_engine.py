"""
Narrative Engine for 1984 CLI Game (Refactored for Open-World)
Manages story beat tracking and progression instead of fixed graph navigation
"""

import json
import random
from typing import Dict, Any, Optional, List


class NarrativeEngine:
    """Manages story beat tracking and progression"""

    def __init__(self, beats_file: str = "story_beats.json", graph_file: str = "narrative-graph.json"):
        self.beats_file = beats_file
        self.graph_file = graph_file  # Keep for backward compatibility

        # Load new beat system
        self.beats: Dict[str, Any] = {}
        self.load_beats()

        # Keep old graph for fallback/migration
        self.graph: Optional[Dict[str, Any]] = None
        self.load_graph()

    def load_beats(self) -> bool:
        """Load the story beats from file"""
        try:
            with open(self.beats_file, 'r') as f:
                beats_data = json.load(f)
                self.beats = beats_data.get('beats', {})
            return True
        except Exception as e:
            print(f"Error loading story beats: {e}")
            return False

    def load_graph(self) -> bool:
        """Load the old narrative graph (for backward compatibility)"""
        try:
            with open(self.graph_file, 'r') as f:
                self.graph = json.load(f)
            return True
        except Exception as e:
            # Not critical - graph is optional now
            return False

    # =============================================================================
    # NEW BEAT-BASED METHODS
    # =============================================================================

    def get_next_suggested_beat(self, world_state: Dict, completed_beats: List[str]) -> Optional[Dict]:
        """
        Determine what story beat to nudge toward next

        Based on:
        - What's been completed
        - Current stats/flags
        - Current location
        - Story priority

        Args:
            world_state: Current world state
            completed_beats: List of beat IDs already completed

        Returns:
            Beat dictionary or None if no suitable beat
        """

        # Find highest priority incomplete beat whose prerequisites are met
        candidates = []

        for beat_id, beat in self.beats.items():
            # Skip if already completed
            if beat_id in completed_beats:
                continue

            # Skip ending beats (they trigger automatically)
            if beat.get('type') in ['ending', 'ending_trigger']:
                continue

            # Check if prerequisites are met
            if self._check_beat_prerequisites(beat, world_state):
                candidates.append((beat_id, beat))

        if not candidates:
            return None

        # Sort by priority (critical > high > medium > low)
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        candidates.sort(
            key=lambda x: priority_order.get(x[1].get('priority', 'medium'), 2),
            reverse=True
        )

        # Return the highest priority beat
        beat_id, beat = candidates[0]
        beat['id'] = beat_id  # Add ID to the beat dict
        return beat

    def _check_beat_prerequisites(self, beat: Dict, world_state: Dict) -> bool:
        """
        Check if beat prerequisites are met

        Args:
            beat: The beat to check
            world_state: Current world state

        Returns:
            True if prerequisites met, False otherwise
        """
        prereqs = beat.get('prerequisites', {})
        stats = world_state.get('stats', {})
        flags = world_state.get('flags', {})
        location = world_state.get('location', '')

        # Check minimum stats
        if 'min_thoughtcrime' in prereqs:
            if stats.get('thoughtcrimeIndex', 0) < prereqs['min_thoughtcrime']:
                return False

        if 'min_chapter' in prereqs:
            if world_state.get('chapter', 1) < prereqs['min_chapter']:
                return False

        # Check required flags
        if 'flags_required' in prereqs:
            for required_flag in prereqs['flags_required']:
                if not flags.get(required_flag):
                    return False

        # Check forbidden flags (must NOT have these)
        if 'flags_forbidden' in prereqs:
            for forbidden_flag in prereqs['flags_forbidden']:
                if flags.get(forbidden_flag):
                    return False

        # Check location requirement
        if 'location' in prereqs:
            if location != prereqs['location']:
                return False

        return True

    def check_beat_completion(self, beat_id: str, world_state: Dict, action: str) -> bool:
        """
        Check if recent action completed a beat

        Args:
            beat_id: ID of the beat to check
            world_state: Current world state
            action: The player's recent action

        Returns:
            True if beat was completed, False otherwise
        """
        beat = self.beats.get(beat_id)
        if not beat:
            return False

        triggers = beat.get('triggers', {})
        flags = world_state.get('flags', {})
        location = world_state.get('location', '')

        # Check keyword triggers
        if 'keywords' in triggers:
            if not any(kw in action.lower() for kw in triggers['keywords']):
                return False

        # Check location triggers
        if 'locations' in triggers:
            if location not in triggers['locations']:
                return False

        # Check NPC presence if needed
        if 'npc_present' in triggers:
            # This would need to be validated by the game master
            pass

        # Check additional conditions
        if 'conditions' in triggers:
            conditions = triggers['conditions']
            if 'alone' in conditions and conditions['alone']:
                # Check if in a private location
                if location not in ['winston_flat', 'room_above_shop', 'countryside']:
                    return False

        # If all trigger conditions match, the beat is completed
        return True

    def get_nudge_for_beat(self, beat: Dict, world_state: Dict) -> Optional[str]:
        """
        Get a subtle nudge toward a story beat

        Args:
            beat: The beat to nudge toward
            world_state: Current world state

        Returns:
            Nudge string or None
        """
        nudges = beat.get('nudges', [])
        if not nudges:
            return None

        # Environmental cues are context-sensitive
        env_cues = beat.get('environmental_cues', [])
        location = world_state.get('location', '')

        # If in a relevant location, prefer environmental cues
        if env_cues and location in beat.get('triggers', {}).get('locations', []):
            return random.choice(env_cues)

        # Otherwise use general nudges
        return random.choice(nudges)

    def apply_beat_completion(self, beat_id: str, state_manager) -> None:
        """
        Apply the effects of completing a beat

        Args:
            beat_id: ID of the completed beat
            state_manager: State manager instance
        """
        beat = self.beats.get(beat_id)
        if not beat:
            return

        completion = beat.get('completion', {})

        # Set flags
        if 'flags_set' in completion:
            state_manager.set_flags(completion['flags_set'])

        # Update stats
        if 'stats' in completion:
            state_manager.update_stats(completion['stats'])

        # Add inventory items
        if 'inventory_add' in completion:
            for item in completion['inventory_add']:
                state_manager.add_to_inventory(item)

        # Update relationships
        if 'relationships' in completion:
            for npc_id, changes in completion['relationships'].items():
                if 'status' in changes:
                    state_manager.update_relationship(npc_id, 'status', changes['status'])
                if 'trust_level' in changes:
                    state_manager.update_relationship(npc_id, 'trustLevel', changes['trust_level'])

        # Update location if specified
        if 'location' in completion:
            state_manager.update_location(completion['location'])

    def get_beat(self, beat_id: str) -> Optional[Dict]:
        """Get a beat by ID"""
        beat = self.beats.get(beat_id)
        if beat:
            beat['id'] = beat_id
        return beat

    def get_all_beats(self) -> Dict[str, Dict]:
        """Get all beats"""
        return self.beats

    # =============================================================================
    # BACKWARD COMPATIBILITY METHODS (for old graph-based system)
    # =============================================================================

    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific node from the OLD graph (backward compatibility)"""
        if self.graph is None:
            return None
        return self.graph.get("nodes", {}).get(node_id)

    def get_current_scene(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get the current scene data (backward compatibility)"""
        return self.get_node(node_id)

    def get_choices(self, node_id: str) -> List[Dict[str, Any]]:
        """Get available choices for a node (backward compatibility)"""
        node = self.get_node(node_id)
        if node is None:
            return []
        return node.get("choices", [])

    def apply_choice_effects(self, choice: Dict[str, Any], state_manager) -> None:
        """Apply the effects of a choice to the game state (backward compatibility)"""
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
        """Get the ID of the next node based on choice (backward compatibility)"""
        return choice.get("nextNode", "")

    def check_requirements(self, choice: Dict[str, Any], state_manager) -> bool:
        """Check if a choice's requirements are met (backward compatibility)"""
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
        """Get all available choices for current node that meet requirements (backward compatibility)"""
        all_choices = self.get_choices(node_id)
        return [choice for choice in all_choices if self.check_requirements(choice, state_manager)]

    def is_terminal_node(self, node_id: str) -> bool:
        """Check if a node is a terminal (ending) node (backward compatibility)"""
        node = self.get_node(node_id)
        if node is None:
            return False

        # A node is terminal if it has no choices or is marked as an ending
        return len(node.get("choices", [])) == 0 or node.get("type") == "ending"

    def get_ascii_art_template(self, node_id: str) -> Optional[str]:
        """Get the ASCII art template name for a node (backward compatibility)"""
        node = self.get_node(node_id)
        if node is None:
            return None

        return node.get("ascii_art_template")
