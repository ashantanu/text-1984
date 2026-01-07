"""
World Definitions for 1984 Game
Defines locations, NPCs, items, and world rules that make up Oceania
"""

from dataclasses import dataclass
from typing import List, Dict, Set, Optional


@dataclass
class Location:
    """Represents a location in the game world"""
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
    """Represents a non-player character"""
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
    """Represents an obtainable item"""
    id: str
    name: str
    description: str
    obtainable_at: List[str]  # Location IDs
    requires_flags: List[str]
    effects: Dict[str, int]  # Stat changes when obtained


# =============================================================================
# LOCATION DEFINITIONS
# =============================================================================

LOCATIONS = {
    "winston_flat": Location(
        id="winston_flat",
        name="Victory Mansions - Flat 7",
        description="Winston's sparse apartment on the seventh floor. The lift rarely works. A telescreen on the wall monitors constantly, but there's an alcove to one side where you cannot be seen.",
        features=["alcove", "telescreen", "window", "table", "bed", "drawer"],
        npcs_possible=[],
        safety_level="moderate",
        actions_allowed={"write", "read", "sleep", "look", "hide", "think", "exercise", "rest"},
        connected_to={
            "victory_mansions_hallway": "through the door",
            "window_view": "looking out the window"
        },
        requires_flags=[]
    ),

    "victory_mansions_hallway": Location(
        id="victory_mansions_hallway",
        name="Victory Mansions - Hallway",
        description="The hallway smells of boiled cabbage and old rag mats. A huge poster of Big Brother watches from one wall. The stairs lead up and down - the lift is broken as usual.",
        features=["big_brother_poster", "stairs", "broken_lift", "telescreen"],
        npcs_possible=["parsons"],
        safety_level="dangerous",
        actions_allowed={"walk", "observe", "talk", "climb"},
        connected_to={
            "winston_flat": "into your flat",
            "parsons_flat": "to Parsons' flat",
            "street": "out to the street"
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
            "ministry_exterior": "through the entrance",
            "obriens_office": "to O'Brien's office"
        },
        requires_flags=[]
    ),

    "records_department": Location(
        id="records_department",
        name="Ministry of Truth - Records Department",
        description="Your workplace. Rows of desks with speakwrites. Workers alter historical records to match the Party's current reality. The Memory Hole stands ready to devour inconvenient truths.",
        features=["speakwrite", "memory_hole", "desk", "documents", "telescreen"],
        npcs_possible=["syme", "parsons"],
        safety_level="dangerous",
        actions_allowed={"work", "alter_records", "observe", "talk"},
        connected_to={
            "ministry_corridor": "out to the corridor"
        },
        requires_flags=[]
    ),

    "ministry_canteen": Location(
        id="ministry_canteen",
        name="Ministry of Truth - Canteen",
        description="A vast canteen serving ersatz coffee, Victory Gin, and barely edible meals. Telescreens broadcast news and propaganda. Workers gather here during breaks.",
        features=["tables", "food_counter", "telescreen", "gin_dispenser"],
        npcs_possible=["julia", "syme", "parsons"],
        safety_level="dangerous",
        actions_allowed={"eat", "drink", "talk", "observe", "sit"},
        connected_to={
            "ministry_corridor": "back to the corridor"
        },
        requires_flags=[]
    ),

    "prole_district": Location(
        id="prole_district",
        name="Prole District",
        description="The rundown quarters where the proletariat live. Crumbling houses, dirty streets, and pubs. Less surveillance here - the Party barely watches the proles. They are beneath notice.",
        features=["pub", "junk_shop", "market", "dingy_streets", "prole_women"],
        npcs_possible=["proles", "charrington", "prole_woman"],
        safety_level="high",
        actions_allowed={"explore", "buy", "talk", "hide", "observe", "drink", "wander"},
        connected_to={
            "charringtons_shop": "into the junk shop on the corner",
            "prole_pub": "into the smoky pub",
            "street": "back toward the Party district"
        },
        requires_flags=[]
    ),

    "charringtons_shop": Location(
        id="charringtons_shop",
        name="Mr. Charrington's Antique Shop",
        description="A dusty shop filled with forgotten relics of the past. Glass paperweights, picture frames, old books. Mr. Charrington, an elderly prole, runs the shop with a gentle manner. There's a room upstairs.",
        features=["antiques", "counter", "paperweight", "upstairs_room", "old_prints", "dust"],
        npcs_possible=["charrington"],
        safety_level="high",
        actions_allowed={"buy", "examine", "talk", "rent", "browse", "ask"},
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
        actions_allowed={"talk_freely", "write", "read", "be_intimate", "plan", "rest", "sleep"},
        connected_to={
            "charringtons_shop": "down the stairs"
        },
        requires_flags=["rented_room"]
    ),

    "prole_pub": Location(
        id="prole_pub",
        name="The Chestnut Tree Café",
        description="A dingy pub frequented by proles. Cheap gin, stale beer, and the occasional song. The Party doesn't care what happens here.",
        features=["bar", "tables", "gin", "beer", "dartboard"],
        npcs_possible=["proles", "old_man"],
        safety_level="high",
        actions_allowed={"drink", "talk", "observe", "listen", "ask"},
        connected_to={
            "prole_district": "out to the street"
        },
        requires_flags=[]
    ),

    "countryside": Location(
        id="countryside",
        name="The Countryside",
        description="Beyond the city limits. Green fields, woods, and a clearing with bluebells. The air smells different here - fresh, alive. No telescreens can see you. True freedom - temporary and fragile.",
        features=["clearing", "woods", "stream", "bluebells", "birdsong", "trees"],
        npcs_possible=["julia"],
        safety_level="very_high",
        actions_allowed={"talk_freely", "kiss", "plan", "rest", "be_intimate", "breathe", "explore"},
        connected_to={
            "train_station": "back to the train"
        },
        requires_flags=[]
    ),

    "victory_square": Location(
        id="victory_square",
        name="Victory Square",
        description="A large public square with monuments to the Party's victories. Crowds gather here during public events. Telescreens are everywhere, watching.",
        features=["monument", "crowd", "telescreen", "statue"],
        npcs_possible=["julia", "parsons", "proles", "party_members"],
        safety_level="dangerous",
        actions_allowed={"observe", "walk", "talk", "wait", "blend_in"},
        connected_to={
            "street": "to the surrounding streets"
        },
        requires_flags=[]
    ),

    "obriens_apartment": Location(
        id="obriens_apartment",
        name="O'Brien's Apartment (Inner Party)",
        description="Luxurious by Oceania standards. Carpets, good furniture, wine, real coffee. The telescreen can be turned off - a privilege only Inner Party members have. Or so O'Brien claims.",
        features=["telescreen_off", "wine", "coffee", "books", "servant", "luxury"],
        npcs_possible=["obrien", "obriens_servant"],
        safety_level="unknown",  # Could be sanctuary or trap
        actions_allowed={"talk", "drink", "join_brotherhood", "receive_book", "observe"},
        connected_to={
            "inner_party_district": "out to the street"
        },
        requires_flags=["knows_obriens_address"]
    ),

    "ministry_of_love": Location(
        id="ministry_of_love",
        name="Ministry of Love",
        description="A vast maze of windowless corridors and cells. The place where there is no darkness. Where they mend thoughts. Where you learn to love Big Brother.",
        features=["cells", "torture_rooms", "room_101", "bright_lights"],
        npcs_possible=["obrien", "guards"],
        safety_level="very_dangerous",
        actions_allowed={"endure", "confess", "resist", "break", "survive"},
        connected_to={},  # No escape
        requires_flags=["arrested"]
    ),

    "room_101": Location(
        id="room_101",
        name="Room 101",
        description="The worst place in the world. The place where they confront you with your deepest fear. The place where everyone breaks.",
        features=["cage", "rats", "fear"],
        npcs_possible=["obrien"],
        safety_level="very_dangerous",
        actions_allowed={"face_fear", "break", "betray"},
        connected_to={
            "ministry_of_love": "back to the cells (if you survive)"
        },
        requires_flags=["sent_to_room_101"]
    )
}

# =============================================================================
# NPC DEFINITIONS
# =============================================================================

NPCS = {
    "julia": NPC(
        id="julia",
        name="Julia",
        role="Member of Fiction Department / Secret Rebel",
        personality="Practical, sensual, rebellious in a personal way (not ideological). Wears the scarlet Junior Anti-Sex League sash as camouflage. Loves breaking rules for pleasure, not politics.",
        dialogue_style="Direct, energetic, pragmatic. Uses prole slang. Not interested in theory - interested in action and pleasure. Speaks in whispers when plotting.",
        default_locations=["ministry_corridor", "fiction_department", "ministry_canteen"],
        relationship_start=0,
        secrets_can_learn=["julia_rebellion", "julia_many_affairs", "julia_practical_rebel"]
    ),

    "obrien": NPC(
        id="obrien",
        name="O'Brien",
        role="Inner Party Member / Thought Police / False Brotherhood Contact",
        personality="Intelligent, urbane, terrifyingly perceptive. Appears sympathetic to rebellion but is actually orchestrating Winston's downfall. Master manipulator.",
        dialogue_style="Thoughtful, philosophical, probing. Speaks in measured tones. Asks questions that seem to understand your thoughts. Intellectually engaging.",
        default_locations=["ministry_corridor", "obriens_apartment"],
        relationship_start=0,
        secrets_can_learn=["obrien_trap", "obrien_thought_police", "obrien_wrote_goldstein_book"]
    ),

    "parsons": NPC(
        id="parsons",
        name="Parsons",
        role="Neighbor / Party Zealot",
        personality="Loud, enthusiastic supporter of the Party. Naive and good-natured. Eventually betrayed by his own children for thoughtcrime committed in his sleep.",
        dialogue_style="Loud, cheerful, filled with Party slogans and enthusiasm. Calls everyone 'old man'. Talks about his children constantly. Sweats profusely.",
        default_locations=["victory_mansions", "ministry_corridor", "records_department"],
        relationship_start=30,
        secrets_can_learn=["parsons_children_spies", "parsons_arrested_by_daughter"]
    ),

    "syme": NPC(
        id="syme",
        name="Syme",
        role="Philologist Working on Newspeak Dictionary",
        personality="Brilliant, enthusiastic about Newspeak. Too intelligent - will be vaporized. Doesn't realize his own danger. Genuinely excited about destroying language.",
        dialogue_style="Intellectual, passionate about language destruction. Talks excitedly about eliminating words. Uses precise vocabulary.",
        default_locations=["ministry_canteen", "records_department"],
        relationship_start=20,
        secrets_can_learn=["syme_too_smart", "syme_will_be_vaporized", "syme_doomed"]
    ),

    "charrington": NPC(
        id="charrington",
        name="Mr. Charrington",
        role="Antique Shop Owner / Secret Thought Police",
        personality="Appears as kindly elderly prole. Quotes old rhymes and poems. Actually a disguised Thought Police officer running a honeypot operation.",
        dialogue_style="Gentle, nostalgic, quotes old rhymes. Seems harmless and friendly. Discusses the past fondly. Very convincing as a harmless old man.",
        default_locations=["charringtons_shop"],
        relationship_start=40,
        secrets_can_learn=["charrington_thought_police", "charrington_trap", "charrington_not_old"]
    ),

    "prole_woman": NPC(
        id="prole_woman",
        name="Prole Woman",
        role="Washerwoman / Symbol of Hope",
        personality="Simple, hardworking, sings while working. Represents the potential of the proles - 'If there is hope, it lies in the proles.'",
        dialogue_style="Simple, sings songs, talks about everyday concerns. No political awareness.",
        default_locations=["prole_district"],
        relationship_start=0,
        secrets_can_learn=["prole_strength", "prole_hope"]
    )
}

# =============================================================================
# ITEM DEFINITIONS
# =============================================================================

ITEMS = {
    "diary": Item(
        id="diary",
        name="Cream-Colored Diary",
        description="A beautiful blank book with cream-colored pages. Smooth paper from the past. Forbidden and dangerous.",
        obtainable_at=["charringtons_shop"],
        requires_flags=[],
        effects={"thoughtcrimeIndex": 8, "suspicionLevel": 5, "partyLoyalty": -5}
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
        description="A piece of glass with a pink coral suspended in it. Beautiful and useless. A relic of a dead world.",
        obtainable_at=["charringtons_shop"],
        requires_flags=[],
        effects={"thoughtcrimeIndex": 5}
    ),

    "goldsteins_book": Item(
        id="goldsteins_book",
        name="The Theory and Practice of Oligarchical Collectivism",
        description="Emmanuel Goldstein's forbidden book explaining the truth about the Party's control.",
        obtainable_at=["obriens_apartment"],
        requires_flags=["joined_brotherhood"],
        effects={"thoughtcrimeIndex": 15}
    ),

    "julias_note": Item(
        id="julias_note",
        name="Julia's Note",
        description="A crumpled scrap of paper with three words: 'I love you'",
        obtainable_at=["ministry_corridor"],
        requires_flags=[],
        effects={"thoughtcrimeIndex": 20, "suspicionLevel": 3}
    ),

    "victory_gin": Item(
        id="victory_gin",
        name="Victory Gin",
        description="Cheap, harsh gin. Tastes like nitric acid. The Party's gift to forget.",
        obtainable_at=["ministry_canteen", "prole_pub"],
        requires_flags=[],
        effects={}
    ),

    "chocolate": Item(
        id="chocolate",
        name="Real Chocolate",
        description="Actual chocolate, not the usual substitute. Rare and valuable.",
        obtainable_at=["charringtons_shop", "obriens_apartment"],
        requires_flags=[],
        effects={}
    )
}

# =============================================================================
# WORLD RULES
# =============================================================================

WORLD_RULES = {
    "telescreen_privacy": {
        "rule": "Telescreens monitor all speech and movement except in specific blind spots",
        "blind_spots": ["winston_flat_alcove", "countryside", "room_above_shop_apparent"],
        "consequence": "Speaking thoughtcrime aloud near telescreen → +30 suspicion",
        "note": "The room above the shop APPEARS safe but actually has a hidden telescreen"
    },

    "prole_freedom": {
        "rule": "Proles are largely unmonitored by the Party",
        "effect": "Actions in prole_district have -50% suspicion gain",
        "note": "The Party doesn't care what proles do - they're beneath notice"
    },

    "thought_police_arrest": {
        "rule": "Thought Police arrest at critical suspicion or after gathering evidence",
        "triggers": ["suspicion >= 95", "sufficient_evidence_collected", "trapped_in_room"],
        "inevitability": "Arrest is eventually inevitable if you rebel"
    },

    "party_membership": {
        "rule": "Winston is Outer Party, limited privileges",
        "restrictions": [
            "Cannot access Inner Party areas without invitation",
            "Rations are limited",
            "Must attend mandatory events (Two Minutes Hate, etc.)",
            "Cannot turn off telescreen"
        ]
    },

    "doublethink": {
        "rule": "The Party requires holding contradictory beliefs simultaneously",
        "examples": [
            "WAR IS PEACE",
            "FREEDOM IS SLAVERY",
            "IGNORANCE IS STRENGTH",
            "2 + 2 = 5 (if the Party says so)"
        ]
    },

    "vaporization": {
        "rule": "Enemies of the Party are 'vaporized' - they never existed",
        "effect": "All records destroyed, person becomes unperson",
        "note": "Syme will be vaporized, Parsons will be arrested by his daughter"
    }
}

# =============================================================================
# ACTION CATEGORIES
# =============================================================================

ACTION_CATEGORIES = {
    "movement": ["go", "walk", "run", "travel", "enter", "leave", "climb", "descend", "flee", "escape"],
    "observation": ["look", "examine", "watch", "observe", "read", "search", "find", "check"],
    "interaction": ["talk", "speak", "ask", "tell", "whisper", "shout", "discuss", "confide"],
    "physical": ["take", "grab", "buy", "give", "hide", "throw", "write", "destroy", "tear"],
    "social": ["kiss", "hug", "hit", "threaten", "love", "betray", "trust"],
    "thoughtcrime": ["write diary", "speak against party", "plan rebellion", "have sex", "express doubt"],
    "meta": ["think", "remember", "feel", "doubt", "question"],
    "work": ["alter records", "work", "attend", "participate", "perform exercises"],
    "consumption": ["eat", "drink", "smoke", "consume"]
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_location(location_id: str) -> Optional[Location]:
    """Get a location by ID"""
    return LOCATIONS.get(location_id)

def get_npc(npc_id: str) -> Optional[NPC]:
    """Get an NPC by ID"""
    return NPCS.get(npc_id)

def get_item(item_id: str) -> Optional[Item]:
    """Get an item by ID"""
    return ITEMS.get(item_id)

def get_npcs_at_location(location_id: str) -> List[NPC]:
    """Get all NPCs that could be at a location"""
    location = get_location(location_id)
    if not location:
        return []

    return [get_npc(npc_id) for npc_id in location.npcs_possible if get_npc(npc_id)]

def get_connected_locations(location_id: str) -> Dict[str, str]:
    """Get locations connected to this one"""
    location = get_location(location_id)
    if not location:
        return {}

    return location.connected_to

def is_action_allowed(location_id: str, action_type: str) -> bool:
    """Check if an action type is allowed at a location"""
    location = get_location(location_id)
    if not location:
        return False

    return action_type in location.actions_allowed

def get_safety_level(location_id: str) -> str:
    """Get the safety level of a location"""
    location = get_location(location_id)
    if not location:
        return "unknown"

    return location.safety_level
