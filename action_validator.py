"""
Action Validation System
Determines if player actions are physically/logically possible given current world state
"""

from typing import Dict, Any, Tuple, Optional, List
from world_definitions import (
    LOCATIONS, NPCS, ITEMS, WORLD_RULES, ACTION_CATEGORIES,
    get_location, get_npc, get_item, is_action_allowed
)


class ActionValidator:
    """Validates player actions against world state"""

    def __init__(self, world_state: Dict[str, Any]):
        self.world_state = world_state

    def validate_action(self, action: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate if action is possible

        Args:
            action: The player's input action

        Returns:
            Tuple of (is_valid, reason_if_invalid, context_for_llm)
        """
        # Parse action intent
        intent = self._parse_action_intent(action)

        # Check physical possibility
        is_possible, reason = self._is_physically_possible(intent)
        if not is_possible:
            return False, reason, {}

        # Check location allows this
        is_allowed, reason = self._location_allows_action(intent)
        if not is_allowed:
            return False, reason, {}

        # Check prerequisites (flags, items, etc.)
        has_prereqs, reason = self._check_prerequisites(intent)
        if not has_prereqs:
            return False, reason, {}

        # Action is valid - return context for LLM
        context = self._build_action_context(intent)
        return True, "", context

    def _parse_action_intent(self, action: str) -> Dict[str, Any]:
        """
        Parse player input into structured intent

        Returns:
            {
                "raw": original action,
                "type": action category,
                "target": what is being acted upon,
                "keywords": important words
            }
        """
        action_lower = action.lower()
        keywords = action_lower.split()

        # Determine action type
        action_type = "unknown"
        for category, verbs in ACTION_CATEGORIES.items():
            if any(verb in action_lower for verb in verbs):
                action_type = category
                break

        # Try to identify target
        target = None
        current_location = self.world_state.get("location", "")
        location = get_location(current_location)

        if location:
            # Check for location features
            for feature in location.features:
                if feature.replace("_", " ") in action_lower:
                    target = feature

            # Check for NPCs
            for npc_id in location.npcs_possible:
                npc = get_npc(npc_id)
                if npc and npc.name.lower() in action_lower:
                    target = npc_id

        # Check for items in inventory
        inventory = self.world_state.get("inventory", [])
        for item_id in inventory:
            item = get_item(item_id)
            if item and item.name.lower() in action_lower:
                target = item_id

        return {
            "raw": action,
            "type": action_type,
            "target": target,
            "keywords": keywords,
            "verb": self._extract_primary_verb(action_lower)
        }

    def _extract_primary_verb(self, action: str) -> Optional[str]:
        """Extract the primary verb from the action"""
        # Common action verbs in order of priority
        priority_verbs = [
            "write", "read", "go", "walk", "run", "talk", "speak", "look", "examine",
            "take", "grab", "buy", "give", "hide", "throw", "destroy", "kiss", "hug",
            "hit", "kill", "flee", "escape", "drink", "eat", "sleep", "rest"
        ]

        words = action.split()
        for verb in priority_verbs:
            if verb in words:
                return verb

        # Return first word if no verb found
        return words[0] if words else None

    def _is_physically_possible(self, intent: Dict) -> Tuple[bool, str]:
        """
        Check if action is physically possible in the world

        Returns:
            (is_possible, reason_if_not)
        """
        verb = intent.get("verb", "")
        raw_action = intent.get("raw", "")

        # Impossible actions
        impossible_actions = [
            ("fly", "You cannot fly. You are not a bird."),
            ("teleport", "Teleportation is not possible."),
            ("turn off telescreen", "Only Inner Party members can turn off telescreens. You cannot."),
            ("kill big brother", "Big Brother cannot be killed. Big Brother is eternal."),
            ("destroy party", "You alone cannot destroy the Party. It is too vast."),
            ("magic", "There is no magic in Oceania. Only the Party's power."),
            ("wish", "Wishes change nothing. Only actions matter."),
        ]

        for trigger, reason in impossible_actions:
            if trigger in raw_action.lower():
                return False, reason

        # Check for items that don't exist
        if "gun" in raw_action or "weapon" in raw_action:
            if "gun" not in self.world_state.get("inventory", []):
                return False, "You have no weapon. The Party controls all weapons."

        # Telescreen-specific rules
        if "turn off" in raw_action and "telescreen" in raw_action:
            current_location = self.world_state.get("location", "")
            if current_location != "obriens_apartment":
                return False, "Only Inner Party members can turn off telescreens. You are Outer Party."

        return True, ""

    def _location_allows_action(self, intent: Dict) -> Tuple[bool, str]:
        """
        Check if current location allows this action

        Returns:
            (is_allowed, reason_if_not)
        """
        current_location = self.world_state.get("location", "")
        location = get_location(current_location)

        if not location:
            return False, f"Invalid location: {current_location}"

        action_type = intent.get("type", "unknown")

        # Special handling for movement
        if action_type == "movement":
            # Movement is generally allowed, but we'll check destinations
            return True, ""

        # Check if action type is allowed at this location
        if action_type in location.actions_allowed or action_type == "meta":
            return True, ""

        # Check specific action categories
        verb = intent.get("verb", "")

        # Meta actions (think, remember, feel) are always allowed
        if action_type == "meta":
            return True, ""

        # Observation is generally allowed everywhere
        if action_type == "observation":
            return True, ""

        # Check by specific verbs if type didn't match
        allowed_verbs = set()
        for allowed in location.actions_allowed:
            allowed_verbs.update(allowed.split("_"))

        if verb in allowed_verbs:
            return True, ""

        # Default: not specifically allowed
        return False, f"You cannot do that here in {location.name}."

    def _check_prerequisites(self, intent: Dict) -> Tuple[bool, str]:
        """
        Check if prerequisites are met (flags, items, relationships)

        Returns:
            (has_prereqs, reason_if_not)
        """
        verb = intent.get("verb", "")
        target = intent.get("target")
        raw_action = intent.get("raw", "")

        # Check item prerequisites
        if verb in ["write"] and "diary" in raw_action:
            if "diary" not in self.world_state.get("inventory", []):
                return False, "You don't have a diary to write in."

        if verb in ["read"] and "book" in raw_action:
            if "goldsteins_book" not in self.world_state.get("inventory", []):
                return False, "You don't have Goldstein's book."

        # Check NPC presence for interactions
        if verb in ["talk", "speak", "ask", "kiss", "hug"] and target:
            current_location = self.world_state.get("location", "")
            location = get_location(current_location)

            if location and target in NPCS:
                if target not in location.npcs_possible:
                    npc = get_npc(target)
                    return False, f"{npc.name} is not here."

        # Check flag prerequisites for locations
        if verb in ["go", "enter"] and target:
            target_location = get_location(target)
            if target_location:
                for required_flag in target_location.requires_flags:
                    if not self.world_state.get("flags", {}).get(required_flag):
                        return False, f"You cannot access that location yet."

        # Check relationship prerequisites
        if "julia" in raw_action and verb in ["kiss", "meet"]:
            if not self.world_state.get("flags", {}).get("met_julia"):
                return False, "You haven't met Julia yet. You don't know her."

        # Check for renting room
        if "rent" in raw_action and "room" in raw_action:
            if not self.world_state.get("flags", {}).get("visited_charringtons"):
                return False, "You need to visit the shop first and build trust with Charrington."

        return True, ""

    def _build_action_context(self, intent: Dict) -> Dict[str, Any]:
        """
        Build context about the action for the LLM

        Returns:
            Context dictionary with relevant information
        """
        current_location = self.world_state.get("location", "")
        location = get_location(current_location)

        context = {
            "intent": intent,
            "location": current_location,
            "location_name": location.name if location else "Unknown",
            "location_safety": location.safety_level if location else "unknown",
            "npcs_present": location.npcs_possible if location else [],
            "features_available": location.features if location else [],
            "inventory": self.world_state.get("inventory", []),
            "flags": self.world_state.get("flags", {}),
            "stats": self.world_state.get("stats", {}),
        }

        # Add NPC details if interacting with one
        if intent.get("target") in NPCS:
            npc = get_npc(intent["target"])
            if npc:
                context["target_npc"] = {
                    "id": npc.id,
                    "name": npc.name,
                    "personality": npc.personality,
                    "dialogue_style": npc.dialogue_style
                }

        # Add item details if interacting with one
        if intent.get("target") in ITEMS:
            item = get_item(intent["target"])
            if item:
                context["target_item"] = {
                    "id": item.id,
                    "name": item.name,
                    "description": item.description
                }

        # Add telescreen warning if relevant
        if location and "telescreen" in location.features:
            telescreen_safe = current_location in ["winston_flat", "countryside", "room_above_shop"]
            context["telescreen_watching"] = not telescreen_safe

        return context

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get a summary of current validation state"""
        current_location = self.world_state.get("location", "")
        location = get_location(current_location)

        return {
            "location": current_location,
            "location_name": location.name if location else "Unknown",
            "allowed_actions": list(location.actions_allowed) if location else [],
            "npcs_present": location.npcs_possible if location else [],
            "features": location.features if location else [],
            "has_diary": "diary" in self.world_state.get("inventory", []),
            "has_goldsteins_book": "goldsteins_book" in self.world_state.get("inventory", []),
            "can_write": "write" in (location.actions_allowed if location else set()),
            "telescreen_present": "telescreen" in (location.features if location else [])
        }


def quick_validate(action: str, world_state: Dict[str, Any]) -> bool:
    """
    Quick validation for simple checks

    Args:
        action: Player action
        world_state: Current world state

    Returns:
        True if action seems valid, False otherwise
    """
    validator = ActionValidator(world_state)
    is_valid, _, _ = validator.validate_action(action)
    return is_valid
