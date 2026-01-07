# LLM-Driven Open-World Architecture for 1984 Game

## Executive Summary

This document outlines the transformation of the 1984 CLI game from a **branching narrative** with fixed choices to a **true open-world LLM-driven experience** where players can take arbitrary actions while the AI Game Master guides them through the story of 1984.

---

## Current vs. Desired Architecture

### Current Implementation (Branching Narrative)
```
Player Input → LLM maps to choice (1, 2, or 3)
             → Navigate to predefined scene in graph
             → Present 2-3 new fixed choices
             → Repeat
```

**Limitations:**
- Player constrained to 2-3 predefined choices
- All scenes pre-written in narrative-graph.json
- LLM only used for input interpretation
- Linear/branching structure, not open-world

### Desired Implementation (Open-World)
```
Player Input (arbitrary action) → LLM Game Master validates
                                → Generates consequence
                                → Updates world state
                                → Generates narrative
                                → Nudges toward story progression
                                → Accepts next arbitrary action
```

**Advantages:**
- True player freedom - any action possible
- LLM generates narrative dynamically
- Story progression through "beats" not fixed paths
- Multiple endings based on player choices
- Immersive, responsive world

---

## Core Design Philosophy

### The Three Pillars

1. **Freedom**: Players can attempt ANY action
   - "examine the telescreen"
   - "throw the diary out the window"
   - "kiss Julia"
   - "punch Parsons"
   - "run away from the Ministry"

2. **Guidance**: LLM nudges toward 1984 story beats
   - Not forced - nudged
   - Environmental cues
   - NPC suggestions
   - Consequences that create opportunities

3. **Consequence**: Every action has realistic outcomes
   - Aligned with 1984's world and tone
   - Affects stats (Loyalty, Suspicion, Thoughtcrime)
   - Can trigger endings (arrest, death, rebellion, etc.)
   - Consistent with established state

---

## System Components

### 1. Story Beat System

Instead of a fixed narrative graph, we track **story beats** - key moments from the 1984 novel that we want players to experience (but don't force).

#### Story Beats (Examples)
```json
{
  "beats": {
    "buy_diary": {
      "id": "buy_diary",
      "title": "Purchase the Diary",
      "description": "Winston buys a forbidden diary from Charrington's shop",
      "chapter": 1,
      "priority": "high",
      "prerequisites": {
        "flags": [],
        "minThoughtcrime": 5
      },
      "triggers": {
        "location": ["prole_district", "charringtons_shop"],
        "keywords": ["buy", "shop", "diary", "book", "paper"]
      },
      "nudges": [
        "You notice a dusty shop window with antique items",
        "You remember seeing a junk shop in the prole district",
        "An old paperbound book catches your eye"
      ],
      "completion_flags": ["has_diary"],
      "next_beats": ["write_in_diary"],
      "skip_consequences": {
        "description": "Winston may find another way to express his thoughts",
        "alternate_beats": ["meet_julia_early"]
      }
    },
    "write_in_diary": {
      "id": "write_in_diary",
      "title": "First Thoughtcrime",
      "description": "Winston commits his first act of rebellion by writing",
      "chapter": 1,
      "priority": "high",
      "prerequisites": {
        "flags": ["has_diary"],
        "location": "winston_flat"
      },
      "triggers": {
        "keywords": ["write", "diary", "pen", "thoughts"],
        "alone": true
      },
      "nudges": [
        "The diary sits in your drawer, its blank pages waiting",
        "You find yourself alone in the alcove, invisible to the telescreen",
        "The pen feels heavy with possibility"
      ],
      "completion_flags": ["diary_started", "first_thoughtcrime"],
      "effects": {
        "thoughtcrime": 20,
        "suspicion": 10,
        "partyLoyalty": -15
      },
      "next_beats": ["meet_julia", "notice_obrien"]
    },
    "meet_julia": {
      "id": "meet_julia",
      "title": "The Note",
      "description": "Julia slips Winston a note saying 'I love you'",
      "chapter": 2,
      "priority": "high",
      "prerequisites": {
        "thoughtcrime": 15,
        "chapter": 1
      },
      "triggers": {
        "location": ["ministry_corridor", "ministry_canteen"],
        "keywords": ["julia", "girl", "dark-haired"]
      },
      "nudges": [
        "You notice the dark-haired girl from the Fiction Department watching you",
        "Someone brushes past you in the corridor",
        "A piece of paper falls near your feet"
      ],
      "completion_flags": ["met_julia", "received_note"],
      "effects": {
        "thoughtcrime": 30,
        "suspicion": 5
      },
      "next_beats": ["julia_meeting", "affair_begins"]
    },
    "arrested": {
      "id": "arrested",
      "title": "Arrest by Thought Police",
      "description": "The Thought Police come for Winston",
      "chapter": -1,
      "type": "ending",
      "priority": "critical",
      "triggers": {
        "suspicion": 100
      },
      "narrative_template": "arrest_sequence",
      "ending_type": "caught_early"
    }
  }
}
```

### 2. LLM Game Master

The heart of the new system. A sophisticated AI that:

#### Responsibilities

**A. Action Validation**
```python
def validate_action(player_action, world_state):
    """
    Determine if action is possible given current state
    Returns: {
        "valid": bool,
        "reason": str  # if invalid
    }
    """
```

Examples:
- "shoot Big Brother" → Invalid (no weapon, no opportunity)
- "write in diary" → Valid if has diary and alone
- "kiss Julia" → Valid only if met Julia and in private

**B. Consequence Generation**
```python
def generate_consequence(player_action, world_state):
    """
    Generate what happens as result of action
    Returns: {
        "narrative": str,  # Description of what happens
        "state_changes": dict,  # Stats, flags, inventory changes
        "new_location": str,  # If location changes
        "npcs_affected": list,  # NPCs involved
        "ending_triggered": str  # If action causes ending
    }
    """
```

**C. Story Nudging**
```python
def nudge_toward_beat(current_state, next_beat):
    """
    Subtly guide player toward next story beat
    Returns: {
        "environmental_cue": str,  # Something Winston notices
        "npc_suggestion": str,  # NPC hints at something
        "internal_thought": str  # Winston's thought
    }
    """
```

**D. Narrative Generation**
```python
def generate_scene_narrative(location, recent_actions, world_state):
    """
    Generate rich narrative description
    Considers: location, time of day, weather, NPCs present, recent events
    Returns: str  # Orwellian prose describing current situation
    """
```

### 3. World State (Enhanced State Management)

#### Locations
Define key locations from 1984 that players can visit:

```python
LOCATIONS = {
    "winston_flat": {
        "name": "Victory Mansions - Flat 7",
        "description": "Winston's sparse apartment",
        "features": ["alcove", "telescreen", "window", "table"],
        "npcs_possible": [],
        "safety_level": "moderate",  # Telescreen watches
        "actions_allowed": ["write", "look", "rest", "exercise"]
    },
    "ministry_corridor": {
        "name": "Ministry of Truth - Corridor",
        "description": "Long white corridor with telescreens",
        "features": ["pneumatic_tubes", "telescreen", "poster"],
        "npcs_possible": ["julia", "parsons", "syme", "obrien"],
        "safety_level": "dangerous",
        "actions_allowed": ["walk", "talk", "work", "observe"]
    },
    "prole_district": {
        "name": "Prole District",
        "description": "Rundown area where the proles live",
        "features": ["pub", "junk_shop", "street"],
        "npcs_possible": ["proles", "charrington"],
        "safety_level": "high",  # Less surveillance
        "actions_allowed": ["explore", "buy", "talk", "hide"]
    },
    "charringtons_shop": {
        "name": "Mr. Charrington's Antique Shop",
        "description": "A dusty shop filled with forgotten relics",
        "features": ["diary", "paperweight", "upstairs_room"],
        "npcs_possible": ["charrington"],
        "safety_level": "high",
        "actions_allowed": ["buy", "examine", "talk", "rent_room"]
    },
    "countryside": {
        "name": "Countryside",
        "description": "Open fields away from the city",
        "features": ["woods", "clearing", "stream"],
        "npcs_possible": ["julia"],
        "safety_level": "very_high",
        "actions_allowed": ["meet", "talk_freely", "be_intimate", "plan"]
    }
}
```

#### NPCs (Non-Player Characters)
```python
NPCS = {
    "julia": {
        "name": "Julia",
        "role": "Potential ally and lover",
        "personality": "Rebellious, practical, sensual",
        "trust_level": 0,
        "knows_secrets": [],
        "locations": ["ministry_corridor", "countryside"],
        "dialogue_style": "Direct, conspiratorial, passionate"
    },
    "obrien": {
        "name": "O'Brien",
        "role": "Inner Party member (ambiguous loyalty)",
        "personality": "Intelligent, enigmatic, powerful",
        "trust_level": 0,
        "knows_secrets": [],
        "locations": ["ministry_corridor", "obriens_apartment"],
        "dialogue_style": "Thoughtful, probing, philosophical"
    },
    "parsons": {
        "name": "Parsons",
        "role": "Neighbor, loyal Party member",
        "personality": "Enthusiastic, obedient, naive",
        "trust_level": 30,
        "knows_secrets": [],
        "locations": ["victory_mansions", "ministry_corridor"],
        "dialogue_style": "Loud, cheerful, conventional"
    }
}
```

### 4. LLM Prompting Strategy

#### Multi-Tier Prompting

**Tier 1: Action Validation (Fast, Cheap)**
```
Model: claude-3-haiku (fast, inexpensive)
Purpose: Quick validation
Prompt: "Given current state X, is action Y possible? Yes/No + reason"
```

**Tier 2: Consequence Generation (Main)**
```
Model: claude-3-5-sonnet (balanced)
Purpose: Generate what happens
Prompt: Detailed context + action → consequences + narrative
```

**Tier 3: Scene Generation (Rich)**
```
Model: claude-3-5-sonnet
Purpose: Generate immersive narrative
Prompt: Full world state → Orwellian prose describing scene
```

#### Prompt Template Example

```
You are the Game Master for an interactive 1984 game. The player (Winston Smith) can take any action. Your job is to:
1. Determine realistic consequences
2. Generate narrative in Orwell's style
3. Subtly nudge toward the next story beat
4. Maintain world consistency

CURRENT STATE:
- Location: {location}
- Time: {time_of_day}, {date}
- Recent actions: {last_3_actions}
- Stats: Loyalty={loyalty}, Suspicion={suspicion}, Thoughtcrime={thoughtcrime}
- Inventory: {inventory}
- Flags: {important_flags}
- NPCs present: {npcs_in_location}

STORY CONTEXT:
- Current chapter: {chapter}
- Next suggested beat: {next_beat}
- Completed beats: {completed_beats}

PLAYER ACTION: "{player_input}"

Generate a response with:
1. VALIDITY: Is this action possible? (yes/no + reason if no)
2. CONSEQUENCE: What happens when Winston does this?
3. NARRATIVE: Describe the outcome in 2-3 paragraphs (Orwell's style)
4. STATE_CHANGES: Stats, flags, inventory, location changes
5. NUDGE: Subtle environmental cue toward next beat (if appropriate)
6. ENDING_CHECK: Does this trigger an ending? (yes/no + which one)

TONE: Dark, oppressive, Orwellian. Everything has weight.
REMEMBER: Big Brother is always watching. Thoughtcrime is dangerous.
```

### 5. Ending System

Multiple possible endings based on player choices:

```python
ENDINGS = {
    "arrested_early": {
        "trigger": {"suspicion": 95},
        "description": "Arrested before major events",
        "narrative": "arrest_early_template"
    },
    "arrested_after_affair": {
        "trigger": {"flags": ["affair_with_julia"], "suspicion": 90},
        "description": "Arrested during affair with Julia",
        "narrative": "arrest_with_julia_template"
    },
    "room_101_broken": {
        "trigger": {"flags": ["arrested", "room_101"]},
        "description": "Broken in Room 101, loves Big Brother",
        "narrative": "canonical_ending_template"
    },
    "escape_to_proles": {
        "trigger": {"location": "prole_district", "flags": ["gave_up_identity"]},
        "description": "Disappeared into the prole districts",
        "narrative": "escape_ending_template"
    },
    "rebel_death": {
        "trigger": {"thoughtcrime": 100, "flags": ["confronted_party"]},
        "description": "Died resisting",
        "narrative": "death_resisting_template"
    },
    "vaporized": {
        "trigger": {"flags": ["arrested"], "suspicion": 100},
        "description": "You never existed",
        "narrative": "vaporized_template"
    }
}
```

---

## Implementation Plan

### Phase 1: Core Infrastructure
1. Create `story_beats.json` with 1984 plot beats
2. Create `game_master.py` with LLM Game Master class
3. Create `world_state.py` with locations, NPCs, items
4. Refactor `llm_processor.py` for multi-tier prompting

### Phase 2: Integration
5. Refactor `narrative_engine.py` to use beats instead of graph
6. Update `main.py` for open-ended input loop
7. Update `state_manager.py` for enhanced world state
8. Create ending detection system

### Phase 3: Content
9. Write story beat definitions for all major 1984 moments
10. Create narrative templates for endings
11. Define all locations, NPCs, items from novel
12. Write nudging strategies for each beat

### Phase 4: Polish
13. Add contextual narrative generation
14. Improve LLM prompts based on testing
15. Balance stats and difficulty
16. Add more alternate paths and endings

---

## Technical Challenges & Solutions

### Challenge 1: LLM Cost/Latency
**Problem**: Every action requires LLM call, expensive and slow

**Solutions**:
- Use Haiku for validation (cheap/fast)
- Use Sonnet for narrative (balanced)
- Cache repeated queries
- Batch state updates

### Challenge 2: Consistency
**Problem**: LLM might generate inconsistent narratives

**Solutions**:
- Provide rich context in every prompt
- Track all important state in world_state
- Validate LLM responses
- Use structured output format

### Challenge 3: Story Progression
**Problem**: Player might wander aimlessly, miss key beats

**Solutions**:
- Nudging system (subtle hints)
- Environmental cues
- NPC suggestions
- Consequence chains that create opportunities
- Time-based events (e.g., Two Minutes Hate happens daily)

### Challenge 4: Balancing Freedom vs. Guardrails
**Problem**: Too much freedom = chaos, too little = not open-world

**Solutions**:
- World rules (can't do physically impossible things)
- Consequences (can try anything, but face realistic outcomes)
- Soft guidance (nudges not forces)
- Multiple valid paths to each beat

---

## Example Gameplay Flow

```
SCENE: Winston's Flat (Morning)
NARRATIVE: The telescreen barks its morning statistics. You sit in the alcove,
           invisible to its eye. The diary lies hidden in your drawer.

PLAYER: > examine the diary more closely

GM PROCESSING:
  1. Validate: Has diary? ✓ In private location? ✓ Valid action ✓
  2. Generate consequence: Winston looks at the diary, feels tempted to write
  3. Check beat: "write_in_diary" is next beat → gentle nudge
  4. Update state: Add "examined_diary" flag

RESPONSE: You pull out the diary and run your fingers over its blank pages.
          The cream-colored paper seems to call out for words, for truth,
          for thoughtcrime. The pen lies beside it. You could write now,
          while the telescreen cannot see. But once you start, there is no
          going back.

PLAYER: > write "DOWN WITH BIG BROTHER"

GM PROCESSING:
  1. Validate: Has diary ✓ Has pen ✓ In alcove ✓ Valid ✓
  2. Beat completed: "write_in_diary" → Mark complete
  3. Major consequences: +20 thoughtcrime, +10 suspicion, -15 loyalty
  4. Generate narrative: First thoughtcrime committed
  5. Next beat: "meet_julia" or "notice_obrien"
  6. Ending check: Suspicion only 25, not arrested yet

RESPONSE: Your hand moves almost of its own accord. DOWN WITH BIG BROTHER.
          The words stare back at you from the page, irrevocable.
          The thoughtcrime has been committed. Death was certain now, but
          when? The Thought Police could take years or minutes to find you.

          You hide the diary back in its spot. Your hands tremble slightly.
          Everything has changed.

          [+20 Thoughtcrime, +10 Suspicion, -15 Party Loyalty]

PLAYER: > go to work at the Ministry

GM PROCESSING:
  1. Validate: Normal work day ✓ Can travel ✓ Valid ✓
  2. Location change: winston_flat → ministry_corridor
  3. Nudge toward "meet_julia": Julia is in the corridor
  4. Generate scene with environmental cue

RESPONSE: You make your way through the cold morning to the Ministry of Truth,
          its white pyramid looming against the sky. In the corridor, the usual
          crowd shuffles toward their departments.

          You notice the dark-haired girl from the Fiction Department. She's
          been around more often lately. She glances your way, then quickly
          looks away. Something about the quickness of it seems... deliberate?

PLAYER: > approach the dark-haired girl

[And so on... the game responds to ANY action, generates consequences,
 and nudges toward story beats while allowing complete freedom]
```

---

## Success Criteria

The implementation is successful if:

1. ✓ Player can take arbitrary actions (not limited to choices)
2. ✓ LLM generates contextually appropriate consequences
3. ✓ Story naturally progresses through key 1984 beats
4. ✓ Multiple endings are possible based on choices
5. ✓ Narrative maintains Orwell's tone and style
6. ✓ World state remains consistent
7. ✓ Game feels open-world, not on-rails
8. ✓ Player can deviate from story and face consequences

---

## Next Steps

1. Review this architecture with user
2. Refine based on feedback
3. Begin implementation with Phase 1
4. Test with sample gameplay scenarios
5. Iterate on prompts and beat definitions

