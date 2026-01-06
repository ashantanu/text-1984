# 1984 Game State Management System

## Overview

This document describes the state management system for the 1984 CLI game. The system uses JSON files stored in the current working directory to maintain game state, track history, and enable save/load functionality.

## Data Structure Architecture

### 1. Current Game State (`game-state.json`)

The primary state file that represents the current snapshot of the game. This is a **single source of truth** for the active game session.

```json
{
  "version": "1.0.0",
  "lastUpdated": "2026-01-03T10:30:00Z",
  "gameId": "uuid-generated-on-new-game",
  "player": {
    "name": "Winston Smith",
    "partyLoyalty": 80,
    "suspicionLevel": 30,
    "location": {
      "id": "ministry_of_truth_records",
      "name": "Ministry of Truth - Records Department",
      "description": "A vast hall filled with pneumatic tubes and speakwrites"
    },
    "inventory": [
      {
        "id": "diary",
        "name": "Worn diary",
        "description": "A forbidden journal with cream-colored pages",
        "hidden": true,
        "discoveredAt": "chapter_1_scene_3"
      },
      {
        "id": "victory_gin",
        "name": "Victory Gin ration",
        "description": "A small bottle of cheap gin",
        "hidden": false
      }
    ],
    "attributes": {
      "health": 85,
      "sanity": 70,
      "doublethinkCapacity": 45
    }
  },
  "world": {
    "currentDate": "1984-04-04",
    "timeOfDay": "morning",
    "chapter": 1,
    "scene": 5,
    "warStatus": "war_with_eastasia"
  },
  "relationships": {
    "julia": {
      "name": "Julia",
      "status": "trusted_ally",
      "trustLevel": 85,
      "suspicionOfPlayer": 10,
      "metAt": "chapter_1_scene_7",
      "lastInteraction": "chapter_2_scene_3",
      "secretsShared": ["diary_existence", "hatred_of_party"]
    },
    "obrien": {
      "name": "O'Brien",
      "status": "enigmatic_superior",
      "trustLevel": 50,
      "suspicionOfPlayer": 30,
      "metAt": "chapter_1_scene_2",
      "lastInteraction": "chapter_2_scene_1",
      "secretsShared": []
    },
    "parsons": {
      "name": "Parsons",
      "status": "neutral_colleague",
      "trustLevel": 40,
      "suspicionOfPlayer": 20,
      "metAt": "prologue",
      "lastInteraction": "chapter_1_scene_9",
      "secretsShared": []
    }
  },
  "flags": {
    "hasMetJulia": true,
    "hasDiary": true,
    "knowsAboutBrotherhood": false,
    "hasBeenToRoom101": false,
    "wasArrested": false,
    "completedTwoMinutesHate": true,
    "discoveredHidingPlace": true
  },
  "currentScenario": {
    "id": "ministry_routine_work",
    "title": "A Day at the Ministry",
    "description": "Another day of rewriting history for the Party",
    "availableChoices": [
      {
        "id": "choice_1",
        "text": "Alter the production statistics as instructed",
        "impact": {
          "partyLoyalty": 5,
          "suspicion": -5
        }
      },
      {
        "id": "choice_2",
        "text": "Keep the original numbers, risking detection",
        "impact": {
          "partyLoyalty": -10,
          "suspicion": 15
        }
      }
    ]
  },
  "metadata": {
    "playTime": 3600,
    "choicesMade": 12,
    "scenesCompleted": 5,
    "deathCount": 0,
    "endings": []
  }
}
```

### 2. Game History (`game-history.json`)

An **append-only log** that records every significant decision, event, and state change. This enables:
- Reviewing past choices
- Analyzing narrative branches taken
- Implementing replay functionality
- Debugging game progression

```json
{
  "version": "1.0.0",
  "gameId": "uuid-matching-game-state",
  "timeline": [
    {
      "id": "event_001",
      "timestamp": "2026-01-03T10:15:00Z",
      "type": "game_start",
      "chapter": 0,
      "scene": 0,
      "description": "New game started",
      "stateSnapshot": {
        "partyLoyalty": 75,
        "suspicionLevel": 15
      }
    },
    {
      "id": "event_002",
      "timestamp": "2026-01-03T10:18:30Z",
      "type": "choice_made",
      "chapter": 1,
      "scene": 1,
      "choice": {
        "id": "prologue_choice_1",
        "text": "Participate enthusiastically in Two Minutes Hate",
        "selectedOption": 1
      },
      "consequences": {
        "partyLoyalty": 5,
        "suspicion": -3,
        "flagsSet": ["completedTwoMinutesHate"],
        "narrative": "Your fervent display of hatred toward Goldstein was noted by the telescreen. Parsons nodded approvingly."
      },
      "stateSnapshot": {
        "partyLoyalty": 80,
        "suspicionLevel": 12
      }
    },
    {
      "id": "event_003",
      "timestamp": "2026-01-03T10:22:15Z",
      "type": "item_acquired",
      "chapter": 1,
      "scene": 3,
      "item": {
        "id": "diary",
        "name": "Worn diary"
      },
      "location": "charrington_shop",
      "consequences": {
        "suspicion": 5,
        "flagsSet": ["hasDiary"],
        "narrative": "You purchased the diary from Mr. Charrington's shop. A dangerous acquisition."
      },
      "stateSnapshot": {
        "partyLoyalty": 80,
        "suspicionLevel": 17
      }
    },
    {
      "id": "event_004",
      "timestamp": "2026-01-03T10:25:40Z",
      "type": "relationship_change",
      "chapter": 1,
      "scene": 7,
      "npc": "julia",
      "previousStatus": "unknown",
      "newStatus": "trusted_ally",
      "trustChange": 50,
      "event": "first_meeting",
      "consequences": {
        "partyLoyalty": -5,
        "flagsSet": ["hasMetJulia"],
        "narrative": "Julia slipped you a note in the corridor. Everything changed."
      },
      "stateSnapshot": {
        "partyLoyalty": 75,
        "suspicionLevel": 17
      }
    },
    {
      "id": "event_005",
      "timestamp": "2026-01-03T10:30:00Z",
      "type": "location_change",
      "chapter": 2,
      "scene": 5,
      "from": "victory_mansions",
      "to": "ministry_of_truth_records",
      "narrative": "You arrived at the Ministry for another day of altering the past.",
      "stateSnapshot": {
        "partyLoyalty": 75,
        "suspicionLevel": 17
      }
    }
  ],
  "statistics": {
    "totalChoices": 12,
    "loyaltyChoices": 7,
    "rebelliousChoices": 5,
    "neutralChoices": 0,
    "itemsAcquired": 2,
    "itemsLost": 0,
    "locationsVisited": 8,
    "npcsEncountered": 5
  }
}
```

### 3. Narrative Graph (`narrative-graph.json`)

A **graph structure** that maps out all possible narrative nodes, their connections, and branching logic. This serves as the game's "map" and enables dynamic narrative generation.

```json
{
  "version": "1.0.0",
  "nodes": {
    "prologue_start": {
      "id": "prologue_start",
      "type": "scene",
      "chapter": 0,
      "title": "The Clocks Were Striking Thirteen",
      "description": "Winston Smith enters Victory Mansions on a cold April day",
      "requiredFlags": [],
      "ascii_art_template": "victory_mansions_exterior",
      "narrative": "It was a bright cold day in April, and the clocks were striking thirteen...",
      "choices": [
        {
          "id": "choice_observe_poster",
          "text": "Stop and observe the Big Brother poster",
          "nextNode": "prologue_poster_observation",
          "requirements": {},
          "effects": {
            "suspicion": 2,
            "flags": ["observed_poster"]
          }
        },
        {
          "id": "choice_hurry_inside",
          "text": "Hurry inside to avoid the cold wind",
          "nextNode": "prologue_inside_building",
          "requirements": {},
          "effects": {
            "suspicion": -1
          }
        }
      ]
    },
    "prologue_poster_observation": {
      "id": "prologue_poster_observation",
      "type": "scene",
      "chapter": 0,
      "title": "Big Brother Is Watching You",
      "description": "The enormous face gazes down from every commanding corner",
      "requiredFlags": ["observed_poster"],
      "ascii_art_template": "big_brother_poster",
      "narrative": "The black-mustachio'd face gazed down from every commanding corner. BIG BROTHER IS WATCHING YOU, the caption said...",
      "choices": [
        {
          "id": "choice_show_reverence",
          "text": "Look up with appropriate reverence",
          "nextNode": "prologue_inside_building",
          "requirements": {},
          "effects": {
            "partyLoyalty": 3,
            "suspicion": -2
          }
        },
        {
          "id": "choice_avert_eyes",
          "text": "Avert your eyes and proceed inside",
          "nextNode": "prologue_inside_building",
          "requirements": {},
          "effects": {
            "partyLoyalty": -2,
            "suspicion": 3
          }
        }
      ]
    },
    "chapter1_two_minutes_hate": {
      "id": "chapter1_two_minutes_hate",
      "type": "scene",
      "chapter": 1,
      "title": "The Two Minutes Hate",
      "description": "The daily ritual of hatred begins",
      "requiredFlags": [],
      "ascii_art_template": "telescreen_goldstein",
      "narrative": "The Hate had started. As usual, the face of Emmanuel Goldstein had flashed onto the screen...",
      "choices": [
        {
          "id": "choice_enthusiastic_participation",
          "text": "Participate enthusiastically, shouting with the crowd",
          "nextNode": "chapter1_after_hate_accepted",
          "requirements": {},
          "effects": {
            "partyLoyalty": 5,
            "suspicion": -3,
            "flags": ["completedTwoMinutesHate", "enthusiastic_hater"]
          }
        },
        {
          "id": "choice_minimal_participation",
          "text": "Participate minimally, just enough to avoid suspicion",
          "nextNode": "chapter1_after_hate_neutral",
          "requirements": {},
          "effects": {
            "partyLoyalty": 0,
            "suspicion": 2,
            "flags": ["completedTwoMinutesHate"]
          }
        },
        {
          "id": "choice_observe_obrien",
          "text": "Focus your attention on O'Brien during the Hate",
          "nextNode": "chapter1_obrien_noticed",
          "requirements": {},
          "effects": {
            "partyLoyalty": 2,
            "suspicion": 1,
            "flags": ["completedTwoMinutesHate", "noticed_obrien"],
            "relationships": {
              "obrien": {
                "trustLevel": 5
              }
            }
          }
        }
      ]
    }
  },
  "edges": [
    {
      "from": "prologue_start",
      "to": "prologue_poster_observation",
      "condition": "choice_observe_poster"
    },
    {
      "from": "prologue_start",
      "to": "prologue_inside_building",
      "condition": "choice_hurry_inside"
    },
    {
      "from": "prologue_poster_observation",
      "to": "prologue_inside_building",
      "condition": "always"
    }
  ],
  "metadata": {
    "totalNodes": 127,
    "totalEdges": 284,
    "endingNodes": 12,
    "criticalPathNodes": 45
  }
}
```

### 4. Save Slots (`save-slots/`)

Directory containing multiple save files for different playthroughs:

```
save-slots/
├── slot_1_autosave.json      # Automatic save
├── slot_2_manual.json         # Manual save 1
├── slot_3_manual.json         # Manual save 2
└── slot_metadata.json         # Quick info about each save
```

Each save slot file contains a complete copy of `game-state.json` and `game-history.json`:

```json
{
  "saveId": "save_uuid",
  "slotNumber": 1,
  "saveType": "autosave",
  "timestamp": "2026-01-03T10:30:00Z",
  "gameState": { /* full game-state.json content */ },
  "gameHistory": { /* full game-history.json content */ },
  "preview": {
    "playerName": "Winston Smith",
    "chapter": 2,
    "scene": 5,
    "location": "Ministry of Truth - Records Department",
    "partyLoyalty": 75,
    "suspicionLevel": 17,
    "playTime": 3600
  }
}
```

## File Locations

All state files are stored in the current working directory:

- `/game-state.json` - Current game state
- `/game-history.json` - Complete event history
- `/narrative-graph.json` - Narrative structure (read-only, defines game structure)
- `/save-slots/` - Directory for save files
- `/save-slots/slot_metadata.json` - Quick metadata about all saves

## State Management Operations

### Starting a New Game

1. Generate new `gameId` (UUID)
2. Create `game-state.json` with initial values
3. Create `game-history.json` with single "game_start" event
4. Load first node from `narrative-graph.json`

### Saving the Game

1. Create save slot file in `save-slots/`
2. Copy current `game-state.json` and `game-history.json`
3. Update `slot_metadata.json`
4. Return confirmation with save details

### Loading a Game

1. Read save slot file
2. Replace `game-state.json` with saved state
3. Replace `game-history.json` with saved history
4. Resume from current scenario

### Making a Choice

1. Read current choice from `game-state.json`
2. Look up consequences in `narrative-graph.json`
3. Update `game-state.json` with new values
4. Append event to `game-history.json` timeline
5. Load next node from narrative graph
6. Present new scenario to player

### Displaying Status

1. Read `game-state.json`
2. Format and display player stats, location, inventory, relationships
3. Include current chapter/scene info

**Command**: `/dossier` (thematic alternative to avoid conflicts with system status commands)

## Data Integrity

### Validation Rules

- `game-state.json` must always have valid schema
- `gameId` must match between state and history files
- History events must be chronologically ordered
- All referenced nodes in state must exist in narrative graph
- Stats must stay within bounds (0-100)

### Backup Strategy

- Auto-save every 5 minutes or after significant events
- Keep last 3 auto-saves in rotation
- Manual saves persist until explicitly deleted
- State files are human-readable JSON for easy debugging

## Usage by the Game Master Agent

The agent should:

1. **On initialization**: Check if `game-state.json` exists
   - If yes: Load existing game
   - If no: Prompt to start new game or load from save slot

2. **After every player choice**:
   - Update `game-state.json`
   - Append to `game-history.json`
   - Auto-save if threshold reached

3. **When loading narrative**:
   - Consult `narrative-graph.json` for scene structure
   - Use current node ID from `game-state.json`
   - Follow edges based on player choices

4. **For save/load commands**:
   - Manage files in `save-slots/`
   - Validate file integrity
   - Provide user feedback

## Example Workflow

```
Player starts game
  → Create game-state.json with initial state
  → Create game-history.json with game_start event
  → Load prologue_start from narrative-graph.json
  → Display ASCII art and narrative
  → Present choices

Player makes choice
  → Record choice in game-history.json
  → Update stats in game-state.json
  → Look up next node in narrative-graph.json
  → Display consequences and new scenario

Player types "/dossier"
  → Read game-state.json
  → Format and display Party personnel file (status panel)

Player types "/save slot 2"
  → Create save-slots/slot_2_manual.json
  → Copy current state and history
  → Confirm save successful

Game auto-saves
  → Check if 5 minutes or major event
  → Update save-slots/slot_1_autosave.json
  → Continue gameplay
```

## Benefits of This Architecture

1. **Persistence**: All progress saved to disk
2. **Debuggable**: Human-readable JSON files
3. **Flexible**: Easy to modify state or add new fields
4. **Historical**: Complete audit trail of decisions
5. **Branching**: Graph structure supports complex narratives
6. **Multi-save**: Support multiple concurrent playthroughs
7. **Recoverable**: Can always load from save if state corrupts
8. **Analyzable**: History enables post-game analysis and statistics

## Future Enhancements

- Compression for large history files
- Export history as narrative summary
- Visualization of narrative path taken through graph
- Achievement system based on history analysis
- Difficulty modifiers affecting state changes
- Cloud sync for save files
