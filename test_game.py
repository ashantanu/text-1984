#!/usr/bin/env python3
"""
Quick test script to verify the game initializes correctly
"""

import sys

print("Testing game imports...")

try:
    from state_manager import StateManager
    print("✓ StateManager imported")

    from narrative_engine import NarrativeEngine
    print("✓ NarrativeEngine imported")

    from display import Display
    print("✓ Display imported")

    from llm_processor import LLMProcessor
    print("✓ LLMProcessor imported")

    print("\nTesting initialization...")

    # Test state manager
    sm = StateManager()
    state = sm.load_state()
    print(f"✓ State loaded - Current node: {state.get('currentNode')}")

    # Test narrative engine
    ne = NarrativeEngine()
    current_scene = ne.get_current_scene(state.get('currentNode'))
    if current_scene:
        print(f"✓ Scene loaded: {current_scene.get('title')}")

    # Test display
    display = Display()
    print("✓ Display initialized")

    # Test LLM processor (might fail if no API key)
    try:
        llm = LLMProcessor()
        print("✓ LLM processor initialized with API key")
    except ValueError as e:
        print(f"⚠ LLM processor failed (expected without API key): {e}")

    print("\n" + "="*60)
    print("ALL CORE SYSTEMS WORKING!")
    print("="*60)

    print("\nGame stats preview:")
    stats = sm.get_stats()
    resources = sm.get_resources()
    print(f"  Party Loyalty: {stats.get('partyLoyalty')}/100")
    print(f"  Suspicion: {stats.get('suspicionLevel')}/100")
    print(f"  Thoughtcrime: {stats.get('thoughtcrimeIndex')}/100")
    print(f"  Resources: Razors({resources.get('razors')}), Cigarettes({resources.get('cigarettes')}), Chocolate({resources.get('chocolate')})")

    print("\nAvailable choices in first scene:")
    choices = ne.get_available_choices(state.get('currentNode'), sm)
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice.get('text')}")

    print("\n✓ Game is ready to play!")

except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
