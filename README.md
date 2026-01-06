# 1984: A CLI Interactive Game

An immersive command-line interactive experience based on George Orwell's dystopian masterpiece *1984*. Play as Winston Smith and navigate the oppressive world of Oceania where every choice matters and Big Brother is always watching.

## Features

- **LLM-Powered Interaction**: Uses Claude AI to interpret natural language input, allowing you to type what you want to do instead of just selecting numbered choices
- **Dynamic Stats System**: Track your Party Loyalty, Suspicion Level, and Thoughtcrime Index
- **Branching Narrative**: Multiple paths and endings based on your choices
- **ASCII Art**: Immersive visual elements throughout the game
- **Persistent State**: Auto-save system so you can continue your journey anytime
- **nvidia-smi Style Stats Panel**: Real-time monitoring of your character's status

## Installation

1. Clone or download this repository

2. Install dependencies (using the ofa conda environment):
```bash
/opt/anaconda3/envs/ofa/bin/pip install -r requirements.txt
```

Or if you're using a different Python environment:
```bash
pip install -r requirements.txt
```

3. Set up your Anthropic API key:

Create a `.env` file in the project root:
```bash
cp .env.example .env
```

Then edit `.env` and add your actual API key:
```
ANTHROPIC_API_KEY=your-actual-api-key-here
```

Get your API key from: https://console.anthropic.com/

## How to Play

**Using the provided run script (recommended):**
```bash
./run_game.sh
```

**Or run directly with Python:**
```bash
/opt/anaconda3/envs/ofa/bin/python main.py
```

**Or with your system Python:**
```bash
python3 main.py
```

### Controls

- **Numbered choices**: Type `1`, `2`, `3`, etc. to select an option
- **Natural language**: Type what you want to do (e.g., "look at the poster", "go inside quickly")
- **Special commands**:
  - `/dossier` or `/stats` - View detailed character information
  - `/quit` - Save and exit the game

## Game Mechanics

### Stats

- **Party Loyalty (0-100)**: How devoted you appear to Big Brother and the Party
- **Suspicion Level (0-100)**: How closely the Thought Police are watching you
  - ⚠️ Warning at 70+
  - 🚨 Critical at 90+ (arrest imminent)
- **Thoughtcrime Index (0-100)**: Severity of your crimes against the Party
  - 60+ unlocks the Rebellion path

### Resources

- **Razors**: Scarce luxury items for trading
- **Cigarettes**: Social currency and bribes
- **Chocolate**: Extremely rare, high-value items

## Project Structure

```
1984-game/
├── main.py                    # Main game loop
├── state_manager.py           # State persistence
├── narrative_engine.py        # Story navigation
├── display.py                 # Visual output
├── llm_processor.py           # AI integration
├── ascii_art/                 # ASCII art files
├── game-state.json            # Your save file (auto-generated)
├── narrative-graph.json       # Story structure
└── requirements.txt           # Dependencies
```

## Tips for Playing

1. **Balance is key**: Too much loyalty makes you conformist, too much rebellion gets you arrested
2. **Watch your suspicion**: Keep it under 70 to avoid dangerous attention
3. **Resources are valuable**: Use them strategically
4. **Experiment with input**: The LLM understands various phrasings
5. **Save often**: The game auto-saves after each choice

## Credits

- **Based on**: *1984* by George Orwell
- **Powered by**: Anthropic's Claude AI
- **Game Design**: See 1984-game-design-document.docx

## License

This is a fan project based on George Orwell's *1984*. Not for commercial use.

---

*BIG BROTHER IS WATCHING YOU*
