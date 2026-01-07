# Implementation Plan: LLM Open-World Transformation

## Overview

This document provides a detailed, file-by-file implementation plan to transform the 1984 game from a branching narrative to an LLM-driven open-world experience.

---

## Current vs. New File Structure

### Files to CREATE
```
story_beats.json          # Story beat definitions (CREATED)
game_master.py            # NEW - Core LLM game master
world_definitions.py      # NEW - Locations, NPCs, items
action_validator.py       # NEW - Validates player actions
ending_manager.py         # NEW - Handles ending detection and narratives
```

### Files to HEAVILY REFACTOR
```
llm_processor.py          # Transform from input mapper to game master
narrative_engine.py       # Transform from graph navigator to beat tracker
state_manager.py          # Enhance with world state tracking
main.py                   # Change game loop for open-ended input
```

### Files to LIGHTLY MODIFY
```
display.py                # Minor updates for new narrative format
```

### Files to KEEP AS-IS
```
ascii_art/               # No changes needed
requirements.txt         # Might add new dependencies
```

### Files to DEPRECATE
```
narrative-graph.json     # Will be replaced by story_beats.json
                        # Keep for reference during transition
```

---

## Implementation Phases

### Phase 1: Foundation (New Core Systems)

#### 1.1 Create `world_definitions.py`

**Purpose**: Define the static world of 1984 - locations, NPCs, items

**Contents**:
```python
"""
World Definitions for 1984
Defines locations, NPCs, items, and world rules
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional

@dataclass
class Location:
    id: str
    name: str
    description: str
    features: List[str]
    npcs_possible: List[str]
    safety_level: str  # "very_high", "high", "moderate", "dangerous", "very_dangerous"
    actions_allowed: Set[str]
    connected_to: Dict[str, str]  # {location_id: transition_description}
    requires_flags: List[str]  # Flags needed to access this location

@dataclass
class NPC:
    id: str
    name: str
    role: str
    personality: str
    dialogue_style: str
    default_locations: List[str]
    relationship_start: int  # Starting trust level
    secrets_can_learn: List[str]

@dataclass
class Item:
    id: str
    name: str
    description: str
    obtainable_at: List[str]  # Location IDs
    requires_flags: List[str]
    effects: Dict[str, int]  # Stat changes when obtained

# Location Definitions
LOCATIONS = {
    "winston_flat": Location(
        id="winston_flat",
        name="Victory Mansions - Flat 7",
        description="Winston's sparse apartment on the seventh floor. The lift rarely works. A telescreen on the wall monitors constantly, but there's an alcove to one side where you cannot be seen.",
        features=["alcove", "telescreen", "window", "table", "bed", "drawer"],
        npcs_possible=[],
        safety_level="moderate",
        actions_allowed={"write", "read", "sleep", "look", "hide", "think", "exercise"},
        connected_to={
            "victory_mansions_hallway": "through the door",
            "window_view": "looking out the window"
        },
        requires_flags=[]
    ),

    "ministry_corridor": Location(
        id="ministry_corridor",
        name="Ministry of Truth - Corridor",
        description="A long white corridor with pneumatic tubes hissing overhead. Telescreens mounted at intervals. Party members hurry to their departments. The atmosphere is one of constant surveillance and purposeful activity.",
        features=["pneumatic_tubes", "telescreen", "party_posters", "windows"],
        npcs_possible=["julia", "parsons", "syme", "obrien"],
        safety_level="dangerous",
        actions_allowed={"walk", "talk", "observe", "work", "wait"},
        connected_to={
            "records_department": "through the main doors",
            "ministry_canteen": "down the stairs",
            "ministry_exterior": "through the entrance"
        },
        requires_flags=[]
    ),

    "prole_district": Location(
        id="prole_district",
        name="Prole District",
        description="The rundown quarters where the proletariat live. Crumbling houses, dirty streets, and pubs. Less surveillance here - the Party barely watches the proles. They are beneath notice.",
        features=["pub", "junk_shop", "market", "dingy_streets"],
        npcs_possible=["proles", "charrington", "prole_woman"],
        safety_level="high",
        actions_allowed={"explore", "buy", "talk", "hide", "observe", "drink"},
        connected_to={
            "charringtons_shop": "the junk shop on the corner",
            "prole_pub": "into the smoky pub",
            "victory_mansions": "back toward the Party district"
        },
        requires_flags=[]
    ),

    "charringtons_shop": Location(
        id="charringtons_shop",
        name="Mr. Charrington's Antique Shop",
        description="A dusty shop filled with forgotten relics of the past. Glass paperweights, picture frames, old books. Mr. Charrington, an elderly prole, runs the shop. There's a room upstairs.",
        features=["antiques", "counter", "paperweight", "upstairs_room", "old_prints"],
        npcs_possible=["charrington"],
        safety_level="high",
        actions_allowed={"buy", "examine", "talk", "rent", "browse"},
        connected_to={
            "prole_district": "out to the street",
            "room_above_shop": "up the stairs (if rented)"
        },
        requires_flags=[]
    ),

    "room_above_shop": Location(
        id="room_above_shop",
        name="The Room Above Charrington's Shop",
        description="A private room with a double bed, gateleg table, old prints on the wall. Mr. Charrington claimed there's no telescreen. The ultimate sanctuary - or the ultimate trap.",
        features=["bed", "table", "window", "engraving", "hidden_telescreen"],
        npcs_possible=["julia"],
        safety_level="very_high",  # Seems safe, but is actually a trap
        actions_allowed={"talk_freely", "write", "read", "be_intimate", "plan", "rest"},
        connected_to={
            "charringtons_shop": "down the stairs"
        },
        requires_flags=["rented_room"]
    ),

    "countryside": Location(
        id="countryside",
        name="Countryside",
        description="Beyond the city limits. Green fields, woods, and a clearing with bluebells. The air smells different here. No telescreens can see you. True freedom - temporary and fragile.",
        features=["clearing", "woods", "stream", "bluebells", "birdsong"],
        npcs_possible=["julia"],
        safety_level="very_high",
        actions_allowed={"talk_freely", "kiss", "plan", "rest", "be_intimate", "breathe"},
        connected_to={
            "train_station": "back to the train"
        },
        requires_flags=[]
    ),

    "obriens_apartment": Location(
        id="obriens_apartment",
        name="O'Brien's Apartment (Inner Party)",
        description="Luxurious by Oceania standards. Carpets, good furniture, wine, real coffee. The telescreen can be turned off - a privilege only Inner Party members have. Or so O'Brien claims.",
        features=["telescreen_off", "wine", "coffee", "books", "servant"],
        npcs_possible=["obrien", "obriens_servant"],
        safety_level="unknown",  # Could be sanctuary or trap
        actions_allowed={"talk", "drink", "join_brotherhood", "receive_book"},
        connected_to={
            "inner_party_district": "out to the street"
        },
        requires_flags=["knows_address"]
    ),

    "ministry_of_love": Location(
        id="ministry_of_love",
        name="Ministry of Love",
        description="A vast maze of windowless corridors and cells. The place where there is no darkness. Where they mend thoughts. Where you learn to love Big Brother.",
        features=["cells", "torture_rooms", "room_101"],
        npcs_possible=["obrien", "guards"],
        safety_level="very_dangerous",
        actions_allowed={"endure", "confess", "resist", "break"},
        connected_to={},  # No escape
        requires_flags=["arrested"]
    )
}

# NPC Definitions
NPCS = {
    "julia": NPC(
        id="julia",
        name="Julia",
        role="Member of Fiction Department / Secret Rebel",
        personality="Practical, sensual, rebellious in a personal way (not ideological). Wears the scarlet Junior Anti-Sex League sash as camouflage. Loves breaking rules for pleasure, not politics.",
        dialogue_style="Direct, energetic, pragmatic. Uses prole slang. Not interested in theory - interested in action and pleasure.",
        default_locations=["ministry_corridor", "fiction_department"],
        relationship_start=0,
        secrets_can_learn=["julia_rebellion", "julia_many_affairs", "julia_practical_rebel"]
    ),

    "obrien": NPC(
        id="obrien",
        name="O'Brien",
        role="Inner Party Member / Thought Police / False Brotherhood Contact",
        personality="Intelligent, urbane, terrifyingly perceptive. Appears sympathetic to rebellion but is actually orchestrating Winston's downfall. Master manipulator.",
        dialogue_style="Thoughtful, philosophical, probing. Speaks in measured tones. Asks questions that seem to understand your thoughts.",
        default_locations=["ministry_corridor", "obriens_apartment"],
        relationship_start=0,
        secrets_can_learn=["obrien_trap", "obrien_thought_police"]
    ),

    "parsons": NPC(
        id="parsons",
        name="Parsons",
        role="Neighbor / Party Zealot",
        personality="Loud, enthusiastic supporter of the Party. Naive and good-natured. Eventually betrayed by his own children for thoughtcrime committed in his sleep.",
        dialogue_style="Loud, cheerful, filled with Party slogans and enthusiasm. Calls everyone 'old man'. Talks about his children constantly.",
        default_locations=["victory_mansions", "ministry_corridor"],
        relationship_start=30,
        secrets_can_learn=["parsons_children_spies", "parsons_arrested"]
    ),

    "syme": NPC(
        id="syme",
        name="Syme",
        role="Philologist Working on Newspeak Dictionary",
        personality="Brilliant, enthusiastic about Newspeak. Too intelligent - will be vaporized. Doesn't realize his own danger.",
        dialogue_style="Intellectual, passionate about language destruction. Talks excitedly about eliminating words.",
        default_locations=["ministry_canteen", "records_department"],
        relationship_start=20,
        secrets_can_learn=["syme_too_smart", "syme_vaporized"]
    ),

    "charrington": NPC(
        id="charrington",
        name="Mr. Charrington",
        role="Antique Shop Owner / Secret Thought Police",
        personality="Appears as kindly elderly prole. Quotes old rhymes and poems. Actually a disguised Thought Police officer running a honeypot operation.",
        dialogue_style="Gentle, nostalgic, quotes old rhymes. Seems harmless and friendly. Discusses the past fondly.",
        default_locations=["charringtons_shop"],
        relationship_start=40,
        secrets_can_learn=["charrington_thought_police", "charrington_trap"]
    )
}

# Item Definitions
ITEMS = {
    "diary": Item(
        id="diary",
        name="Cream-Colored Diary",
        description="A beautiful blank book with cream-colored pages. Smooth paper from the past. Forbidden and dangerous.",
        obtainable_at=["charringtons_shop"],
        requires_flags=[],
        effects={"thoughtcrime": 8, "suspicion": 5, "partyLoyalty": -5}
    ),

    "pen": Item(
        id="pen",
        name="Old-Fashioned Pen",
        description="A real pen with a nib, not a speakwrite. For putting forbidden thoughts on paper.",
        obtainable_at=["charringtons_shop", "winston_flat"],
        requires_flags=[],
        effects={}
    ),

    "paperweight": Item(
        id="paperweight",
        name="Glass Paperweight",
        description="A piece of glass with a pink rose suspended in it. Beautiful and useless. A relic of a dead world.",
        obtainable_at=["charringtons_shop"],
        requires_flags=[],
        effects={"thoughtcrime": 5}
    ),

    "goldsteins_book": Item(
        id="goldsteins_book",
        name="The Theory and Practice of Oligarchical Collectivism",
        description="Emmanuel Goldstein's forbidden book explaining the truth about the Party's control.",
        obtainable_at=["obriens_apartment"],
        requires_flags=["joined_brotherhood"],
        effects={"thoughtcrime": 15}
    ),

    "julias_note": Item(
        id="julias_note",
        name="Julia's Note",
        description="A crumpled scrap of paper with three words: 'I love you'",
        obtainable_at=["ministry_corridor"],
        requires_flags=[],
        effects={"thoughtcrime": 20, "suspicion": 3}
    )
}

# World Rules
WORLD_RULES = {
    "telescreen_privacy": {
        "rule": "Telescreens monitor all speech and movement except in specific blind spots",
        "blind_spots": ["winston_flat_alcove", "countryside", "room_above_shop_supposed"],
        "consequence": "Speaking thoughtcrime aloud near telescreen → +30 suspicion"
    },

    "prole_freedom": {
        "rule": "Proles are largely unmonitored by the Party",
        "effect": "Actions in prole_district have -50% suspicion gain"
    },

    "thought_police": {
        "rule": "Thought Police arrest at 100 suspicion or after gathering evidence",
        "triggers": ["suspicion >= 100", "sufficient_evidence_collected"]
    },

    "party_membership": {
        "rule": "Winston is Outer Party, limited privileges",
        "restrictions": ["Cannot access Inner Party areas without invitation",
                       "Rations are limited",
                       "Must attend mandatory events"]
    }
}

# Action Categories
ACTION_CATEGORIES = {
    "movement": ["go", "walk", "run", "travel", "enter", "leave", "climb", "descend"],
    "observation": ["look", "examine", "watch", "observe", "read", "search"],
    "interaction": ["talk", "speak", "ask", "tell", "whisper", "shout"],
    "physical": ["take", "grab", "buy", "give", "hide", "throw", "write"],
    "social": ["kiss", "hug", "hit", "threaten"],
    "thoughtcrime": ["write diary", "speak against party", "plan rebellion", "have sex"],
    "meta": ["think", "remember", "feel"]
}
```

**Implementation Notes**:
- This is a static data file
- Used by all other systems for world consistency
- Can be expanded with more locations/NPCs as needed

---

#### 1.2 Create `action_validator.py`

**Purpose**: Validate whether a player action is possible given current world state

**Key Functions**:
```python
"""
Action Validation System
Determines if player actions are physically/logically possible
"""

from typing import Dict, Any, Tuple
from world_definitions import LOCATIONS, NPCS, ITEMS, WORLD_RULES

class ActionValidator:
    """Validates player actions against world state"""

    def __init__(self, world_state: Dict[str, Any]):
        self.world_state = world_state

    def validate_action(self, action: str) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate if action is possible

        Returns:
            (is_valid, reason_if_invalid, context_for_llm)
        """
        # Parse action intent
        intent = self._parse_action_intent(action)

        # Check physical possibility
        if not self._is_physically_possible(intent):
            return False, "That action is not physically possible in your current situation.", {}

        # Check location allows this
        if not self._location_allows_action(intent):
            return False, f"You cannot do that in {self.world_state['location']}.", {}

        # Check prerequisites (flags, items, etc.)
        if not self._check_prerequisites(intent):
            return False, "You don't have what you need to do that.", {}

        # Action is valid - return context for LLM
        context = self._build_action_context(intent)
        return True, "", context

    def _parse_action_intent(self, action: str) -> Dict[str, Any]:
        """Parse player input into structured intent"""
        # This uses simple keyword matching initially
        # Could be enhanced with its own LLM call for complex parsing
        pass

    def _is_physically_possible(self, intent: Dict) -> bool:
        """Check if action is physically possible"""
        # Can't shoot Big Brother if you have no gun
        # Can't fly
        # etc.
        pass

    def _location_allows_action(self, intent: Dict) -> bool:
        """Check if current location allows this action"""
        current_loc = LOCATIONS[self.world_state['location']]
        action_type = intent['type']
        return action_type in current_loc.actions_allowed

    def _check_prerequisites(self, intent: Dict) -> bool:
        """Check flags, items, relationships needed"""
        # e.g., can't write in diary if don't have diary
        # can't meet Julia if haven't received note
        pass
```

**Implementation Priority**: High (needed before game master can work)

---

#### 1.3 Create `game_master.py`

**Purpose**: The core LLM-driven game master that processes actions and generates consequences

**Key Class Structure**:
```python
"""
LLM Game Master
The brain of the open-world system
Processes actions, generates consequences, nudges story
"""

from typing import Dict, Any, Optional, Tuple
from anthropic import Anthropic
import json

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
                      next_beat: Optional[Dict]) -> Dict[str, Any]:
        """
        Main processing function

        Returns:
            {
                "narrative": str,  # What happens (in Orwell's style)
                "state_changes": dict,  # Stats, flags, inventory, location
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
        response = self.client.messages.create(
            model=self.model_main,
            max_tokens=1500,
            temperature=0.8,  # Higher for creative narrative
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse structured response
        result = self._parse_gm_response(response.content[0].text)

        return result

    def _build_llm_context(self, world_state, story_progress, next_beat):
        """Build comprehensive context for LLM"""
        return {
            "location": world_state["location"],
            "location_details": LOCATIONS[world_state["location"]],
            "time": world_state["date"] + " " + world_state["time"],
            "stats": world_state["stats"],
            "inventory": world_state["inventory"],
            "flags": world_state["flags"],
            "relationships": world_state["relationships"],
            "recent_actions": world_state.get("recent_actions", [])[-5:],
            "completed_beats": story_progress.get("completed_beats", []),
            "next_beat": next_beat,
            "chapter": world_state.get("chapter", 1)
        }

    def _create_game_master_prompt(self, action, context):
        """Create the master prompt for Claude"""
        return f"""You are the Game Master for an interactive 1984 game. The player (Winston Smith) can take any action they choose. Your job is to:

1. Determine realistic consequences in the world of 1984
2. Generate narrative in George Orwell's distinctive style (dark, oppressive, precise)
3. Update game state based on consequences
4. Subtly nudge toward the next story beat (WITHOUT forcing)
5. Detect if an ending has been triggered

CURRENT WORLD STATE:
Location: {context['location']} - {context['location_details'].description}
Date/Time: {context['time']}
Chapter: {context['chapter']}

WINSTON'S STATS:
- Party Loyalty: {context['stats']['partyLoyalty']}/100
- Suspicion Level: {context['stats']['suspicionLevel']}/100 {"⚠️ DANGER" if context['stats']['suspicionLevel'] >= 70 else ""}
- Thoughtcrime Index: {context['stats']['thoughtcrimeIndex']}/100

WINSTON'S INVENTORY: {', '.join(context['inventory']) if context['inventory'] else 'Empty'}

IMPORTANT FLAGS: {[f for f,v in context['flags'].items() if v]}

RECENT ACTIONS: {context['recent_actions'][-3:] if context['recent_actions'] else 'None'}

STORY PROGRESS:
- Completed Beats: {', '.join(context['completed_beats'])}
- Next Suggested Beat: {context['next_beat']['title'] if context['next_beat'] else 'Open'}
  {context['next_beat']['description'] if context['next_beat'] else ''}

PLAYER ACTION:
"{action}"

RESPOND IN THIS EXACT JSON FORMAT:
{{
    "narrative": "2-3 paragraphs in Orwell's style describing what happens",
    "state_changes": {{
        "stats": {{"partyLoyalty": 0, "suspicionLevel": 0, "thoughtcrimeIndex": 0}},
        "flags_set": ["flag1", "flag2"],
        "flags_unset": ["flag3"],
        "inventory_add": ["item1"],
        "inventory_remove": ["item2"],
        "location": "new_location_id or null",
        "time_advance": "minutes/hours/days passed or null",
        "relationships": {{"npc_id": {{"trust_change": 10}}}}
    }},
    "beat_completed": "beat_id or null",
    "ending_triggered": "ending_id or null",
    "nudge": "Subtle environmental cue toward next beat or null"
}}

CRITICAL RULES:
- Big Brother is always watching (except specific safe locations)
- Thoughtcrime is severely punished - suspicion builds gradually
- At suspicion >= 100, Winston is arrested (ending)
- Maintain consistency with established world state
- Narrative must feel like Orwell wrote it
- Don't break 4th wall or mention game mechanics in narrative
- NPCs behave according to their personality (Julia = practical rebel, O'Brien = enigmatic, etc.)
- Consequences must be realistic to 1984's totalitarian world

TONE: Oppressive, dark, heavy with dread, precise language, Orwellian

Generate your response now:"""

    def _parse_gm_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Claude's JSON response"""
        try:
            # Claude should return valid JSON
            result = json.loads(response_text)
            return result
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "narrative": response_text,
                "state_changes": {},
                "beat_completed": None,
                "ending_triggered": None,
                "nudge": None
            }

    def generate_scene_description(self, location_id: str, context: Dict) -> str:
        """Generate rich scene description for location"""
        location = LOCATIONS[location_id]

        prompt = f"""You are narrating a scene in an interactive 1984 game.

Generate a vivid description of this location in George Orwell's style:

LOCATION: {location.name}
DESCRIPTION: {location.description}
FEATURES: {', '.join(location.features)}
TIME: {context.get('time', 'unknown')}
RECENT EVENTS: {context.get('recent_events', 'None')}

Generate 2-3 paragraphs that:
1. Describe what Winston sees, hears, smells
2. Capture the oppressive atmosphere
3. Note any NPCs present
4. Reflect Winston's current emotional state (based on stats)

Stats for mood: Loyalty={context['stats']['partyLoyalty']}, Suspicion={context['stats']['suspicionLevel']}, Thoughtcrime={context['stats']['thoughtcrimeIndex']}

Write in Orwell's precise, dark style:"""

        response = self.client.messages.create(
            model=self.model_main,
            max_tokens=600,
            temperature=0.8,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text.strip()
```

**Implementation Priority**: CRITICAL (this is the core of the new system)

---

#### 1.4 Create `ending_manager.py`

**Purpose**: Detect and handle game endings

**Key Functions**:
```python
"""
Ending Manager
Detects ending conditions and generates ending narratives
"""

from typing import Optional, Dict, Any
import json

class EndingManager:
    """Manages game ending detection and narratives"""

    def __init__(self):
        # Load alternate endings from story_beats.json
        with open('story_beats.json', 'r') as f:
            beats_data = json.load(f)
            self.alternate_endings = beats_data['alternate_endings']

    def check_ending(self, world_state: Dict, recent_action: str) -> Optional[Dict]:
        """
        Check if an ending has been triggered

        Returns ending data if triggered, None otherwise
        """

        # Check stat-based endings
        if world_state['stats']['suspicionLevel'] >= 100:
            return self._get_ending('arrested_early')

        # Check flag-based endings
        if world_state['flags'].get('room_101_completed'):
            return self._get_ending('canonical_ending')

        # Check action-based endings
        if any(keyword in recent_action.lower() for keyword in ['kill myself', 'suicide', 'jump']):
            if world_state['stats']['thoughtcrimeIndex'] >= 60:
                return self._get_ending('suicide')

        # Check escape attempts
        if 'escape' in recent_action.lower() or 'flee' in recent_action.lower():
            if world_state['stats']['suspicionLevel'] >= 70:
                return self._get_ending('escape_attempt')

        return None

    def _get_ending(self, ending_id: str) -> Dict:
        """Get ending data"""
        if ending_id in self.alternate_endings:
            return self.alternate_endings[ending_id]
        return None

    def generate_ending_narrative(self, ending_data: Dict, final_state: Dict) -> str:
        """Generate full ending narrative"""
        # Could enhance with LLM to personalize based on journey
        return ending_data['narrative']
```

---

### Phase 2: Refactor Existing Systems

#### 2.1 Refactor `llm_processor.py` → Game Master Integration

**Current Role**: Maps natural language to numbered choices

**New Role**: Interface to GameMaster class

**Changes**:
```python
# BEFORE (current):
def process_user_input(self, user_input: str, available_choices: List[Dict], ...):
    # Maps input to choice 1, 2, or 3

# AFTER (new):
def process_user_input(self, user_input: str, world_state: Dict, story_progress: Dict):
    """Process open-ended user input"""

    # 1. Validate action
    validator = ActionValidator(world_state)
    is_valid, reason, context = validator.validate_action(user_input)

    if not is_valid:
        return {"type": "invalid", "message": reason}

    # 2. Get next beat
    next_beat = self.story_tracker.get_next_beat(world_state, story_progress)

    # 3. Process with Game Master
    game_master = GameMaster(self.api_key)
    result = game_master.process_action(user_input, world_state, story_progress, next_beat)

    return result
```

**Implementation Notes**:
- Keep backward compatibility initially
- Gradual migration from old to new system

---

#### 2.2 Refactor `narrative_engine.py` → Beat Tracker

**Current Role**: Navigate narrative graph

**New Role**: Track story beats and suggest next steps

**Changes**:
```python
# BEFORE:
class NarrativeEngine:
    def __init__(self, graph_file: str = "narrative-graph.json"):
        # Load fixed graph

    def get_current_scene(self, node_id: str):
        # Return predefined scene

    def get_available_choices(self, node_id: str):
        # Return predefined choices

# AFTER:
class NarrativeEngine:
    """Story beat tracker and progression manager"""

    def __init__(self, beats_file: str = "story_beats.json"):
        self.beats_file = beats_file
        self.beats = self._load_beats()

    def _load_beats(self) -> Dict:
        """Load story beats"""
        with open(self.beats_file, 'r') as f:
            return json.load(f)['beats']

    def get_next_suggested_beat(self, world_state: Dict, completed_beats: List[str]) -> Optional[Dict]:
        """
        Determine what story beat to nudge toward next
        Based on:
        - What's been completed
        - Current stats/flags
        - Current location
        - Story priority
        """

        # Find highest priority incomplete beat whose prerequisites are met
        candidates = []
        for beat_id, beat in self.beats.items():
            if beat_id in completed_beats:
                continue  # Already done

            if self._check_beat_prerequisites(beat, world_state):
                candidates.append(beat)

        if not candidates:
            return None

        # Sort by priority
        candidates.sort(key=lambda b: self._priority_value(b['priority']), reverse=True)
        return candidates[0]

    def _check_beat_prerequisites(self, beat: Dict, world_state: Dict) -> bool:
        """Check if beat prerequisites are met"""
        prereqs = beat.get('prerequisites', {})

        # Check min stats
        if 'min_thoughtcrime' in prereqs:
            if world_state['stats']['thoughtcrimeIndex'] < prereqs['min_thoughtcrime']:
                return False

        # Check required flags
        if 'flags_required' in prereqs:
            for flag in prereqs['flags_required']:
                if not world_state['flags'].get(flag):
                    return False

        # Check forbidden flags
        if 'flags_forbidden' in prereqs:
            for flag in prereqs['flags_forbidden']:
                if world_state['flags'].get(flag):
                    return False

        return True

    def check_beat_completion(self, beat_id: str, world_state: Dict, action: str) -> bool:
        """Check if recent action completed a beat"""
        beat = self.beats.get(beat_id)
        if not beat:
            return False

        triggers = beat.get('triggers', {})

        # Check keywords
        if 'keywords' in triggers:
            if any(kw in action.lower() for kw in triggers['keywords']):
                # Additional conditions may apply
                return self._check_trigger_conditions(beat, world_state)

        return False

    def get_nudge_for_beat(self, beat: Dict, world_state: Dict) -> str:
        """Get a subtle nudge toward this beat"""
        nudges = beat.get('nudges', [])
        if not nudges:
            return None

        # Could use LLM to make nudges contextual
        # For now, pick random one
        import random
        return random.choice(nudges)
```

---

#### 2.3 Enhance `state_manager.py`

**Changes Needed**:
1. Add `location` tracking (currently minimal)
2. Add `recent_actions` history (last 10 actions)
3. Add `completed_beats` list
4. Add `chapter` tracking
5. Enhance `relationships` structure
6. Add `time_of_day` tracking

**Code Changes**:
```python
def create_new_state(self) -> Dict[str, Any]:
    """Create a fresh game state"""
    self.state = {
        # ... existing fields ...

        # NEW FIELDS:
        "location": "winston_flat",  # Current location ID
        "chapter": 1,
        "time_of_day": "morning",  # morning, afternoon, evening, night
        "recent_actions": [],  # Last 10 actions taken
        "completed_beats": [],  # Beat IDs completed
        "story_progress": {
            "current_beat": None,
            "next_suggested_beat": "buy_diary"
        },

        # Enhanced relationships
        "relationships": {
            "julia": {
                "status": "unknown",
                "trustLevel": 0,
                "met": False,
                "secrets_known": []
            },
            # ... etc
        }
    }

def record_action(self, action: str, result: Dict):
    """Record an action and its result"""
    self.state["recent_actions"].append({
        "action": action,
        "timestamp": datetime.now().isoformat(),
        "location": self.state["location"],
        "result_summary": result.get("narrative", "")[:100]
    })

    # Keep only last 10
    if len(self.state["recent_actions"]) > 10:
        self.state["recent_actions"] = self.state["recent_actions"][-10:]

def complete_beat(self, beat_id: str):
    """Mark a story beat as completed"""
    if beat_id not in self.state["completed_beats"]:
        self.state["completed_beats"].append(beat_id)
```

---

#### 2.4 Refactor `main.py` → Open-Ended Game Loop

**Major Changes**:

**BEFORE**:
```python
# Get available choices
available_choices = self.narrative_engine.get_available_choices(...)

# Render scene with choices
self.render_scene_with_choices(current_scene, available_choices)

# Get player choice (1, 2, or 3)
choice_made = self.get_player_choice(available_choices)
```

**AFTER**:
```python
def game_loop(self):
    """Main game loop - now open-ended"""
    while self.running:
        # Check for ending
        ending = self.ending_manager.check_ending(self.state_manager.state)
        if ending:
            self.handle_ending(ending)
            break

        # Get current world state
        world_state = self.state_manager.state

        # Generate current scene description (LLM generated)
        scene_narrative = self.game_master.generate_scene_description(
            world_state['location'],
            {
                'time': world_state['date'] + " " + world_state['time_of_day'],
                'stats': world_state['stats'],
                'recent_events': world_state['recent_actions'][-3:]
            }
        )

        # Display scene and stats
        self.display.render_open_world_scene(
            scene_narrative,
            world_state['location'],
            world_state['stats'],
            world_state['resources']
        )

        # Get open-ended player input
        player_action = self.get_player_action()

        # Process action through LLM Game Master
        result = self.llm_processor.process_user_input(
            player_action,
            world_state,
            {"completed_beats": world_state['completed_beats']}
        )

        # Show narrative result
        self.display.print_narrative(result['narrative'])

        # Apply state changes
        self.state_manager.apply_changes(result['state_changes'])

        # Record action
        self.state_manager.record_action(player_action, result)

        # Check beat completion
        if result.get('beat_completed'):
            self.state_manager.complete_beat(result['beat_completed'])

        # Show nudge if any
        if result.get('nudge'):
            self.display.print_nudge(result['nudge'])

        # Save state
        self.state_manager.save_state()

def get_player_action(self) -> str:
    """Get open-ended player input"""
    print(f"\n{Colors.BOLD}What do you do?{Colors.RESET}")
    print(f"{Colors.DIM}(Type any action, or /dossier for stats, /quit to exit){Colors.RESET}")

    user_input = input(f"\n{Colors.CYAN}> {Colors.RESET}").strip()

    # Handle special commands
    if user_input.lower() in ['/quit', '/exit']:
        # ... quit logic

    if user_input.lower() in ['/dossier', '/stats']:
        # ... show stats
        return self.get_player_action()  # Ask again

    return user_input
```

---

### Phase 3: Display Updates

#### 3.1 Add New Display Methods to `display.py`

```python
def render_open_world_scene(self, narrative: str, location: str, stats: Dict, resources: Dict):
    """Render an open-world scene"""
    self.clear_screen()

    # Build left panel (narrative)
    left_content = []

    # Location header
    loc_name = LOCATIONS[location].name
    left_content.append(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}")
    left_content.append(f"{Colors.BOLD}{Colors.CYAN}{loc_name.center(70)}{Colors.RESET}")
    left_content.append(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}")
    left_content.append("")

    # Narrative
    wrapped = self._wrap_text(narrative, 70)
    left_content.extend(wrapped)
    left_content.append("")

    # Render split screen with stats on right
    self.render_split_screen(left_content, stats, resources, loc_name)

def print_narrative(self, narrative: str):
    """Print narrative result"""
    print(f"\n{Colors.GRAY}{narrative}{Colors.RESET}\n")

def print_nudge(self, nudge: str):
    """Print a subtle story nudge"""
    print(f"{Colors.DIM}{Colors.YELLOW}⚬ {nudge}{Colors.RESET}\n")
```

---

## Implementation Timeline

### Week 1: Foundation
- Day 1-2: Create `world_definitions.py` with all locations, NPCs, items
- Day 3-4: Create `action_validator.py` and test
- Day 5-7: Create core `game_master.py` class and test with mock data

### Week 2: Integration
- Day 8-9: Refactor `llm_processor.py` to use GameMaster
- Day 10-11: Refactor `narrative_engine.py` to beat tracker
- Day 12-14: Enhance `state_manager.py` with new fields

### Week 3: Game Loop & Display
- Day 15-17: Refactor `main.py` game loop for open-ended input
- Day 18-19: Update `display.py` with new rendering methods
- Day 20-21: Create `ending_manager.py` and integrate

### Week 4: Testing & Polish
- Day 22-24: End-to-end testing, fix bugs
- Day 25-26: Prompt tuning for better LLM responses
- Day 27-28: Balance stats, test all story paths

---

## Testing Strategy

### Unit Tests
- Test `ActionValidator` with various inputs
- Test `EndingManager` trigger conditions
- Test state management functions

### Integration Tests
- Test full action → consequence → state update flow
- Test beat completion detection
- Test ending triggers

### Playthrough Tests
- Multiple complete playthroughs
- Test alternate paths (skip beats, early arrest, etc.)
- Test all endings

### LLM Response Tests
- Ensure narrative quality (Orwellian tone)
- Ensure JSON parsing doesn't fail
- Test consistency across multiple actions

---

## Migration Path

### Option A: Clean Slate (Recommended)
1. Create new branch `feature/llm-open-world`
2. Implement all new systems
3. Keep old system in `main` branch until new is ready
4. Test thoroughly
5. Merge when complete

### Option B: Gradual Migration
1. Add new systems alongside old
2. Create feature flag: `USE_OPEN_WORLD = True/False`
3. Run both systems in parallel
4. Gradually migrate
5. Remove old system once confident

---

## Risk Mitigation

### Risk: LLM Costs Too High
**Mitigation**:
- Use Haiku for validation (cheap)
- Cache common responses
- Implement rate limiting
- Consider batching state updates

### Risk: LLM Inconsistency
**Mitigation**:
- Provide extensive context
- Use structured JSON output
- Validate all responses
- Have fallback narratives

### Risk: Players Break the Game
**Mitigation**:
- Robust action validation
- Impossible actions get realistic "you can't do that" responses
- Ending triggers catch extreme cases
- LLM prompted to maintain consistency

### Risk: Story Goes Off Rails
**Mitigation**:
- Strong nudging system
- Consequence chains that create opportunities
- Some beats trigger automatically (arrest at 100 suspicion)
- Multiple valid paths to same beats

---

## Success Metrics

### Technical Success
- ✓ LLM response time < 3 seconds avg
- ✓ JSON parse success rate > 95%
- ✓ No crashes during 10 complete playthroughs
- ✓ State always remains consistent

### Gameplay Success
- ✓ Players can complete game via multiple paths
- ✓ All major beats can be reached through different routes
- ✓ Arbitrary actions get meaningful responses
- ✓ Narrative feels like Orwell's 1984
- ✓ Story progresses naturally without feeling forced

### Player Experience Success
- ✓ Players feel freedom to experiment
- ✓ Consequences feel realistic and meaningful
- ✓ Story remains engaging despite open-world nature
- ✓ Multiple playthroughs reveal different content

---

## Next Steps

1. **Review this plan with user** - Get feedback and approval
2. **Refine based on feedback** - Adjust priorities, scope
3. **Set up development branch** - Create clean workspace
4. **Begin Phase 1** - Start with `world_definitions.py`
5. **Iterative development** - Build, test, iterate
6. **Regular playtesting** - Test frequently during development

