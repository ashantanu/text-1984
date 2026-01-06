#!/usr/bin/env python3
"""
Test playthrough to check game flow and find missing scenes
"""

from state_manager import StateManager
from narrative_engine import NarrativeEngine
from display import Display

print("Testing game flow...\n")

sm = StateManager()
ne = NarrativeEngine()
display = Display()

# Start new game
state = sm.create_new_state()

print(f"Starting at: {state['currentNode']}\n")

# Test each scene and check if next nodes exist
scenes_to_test = []
current_node_id = state['currentNode']

visited = set()
to_visit = [current_node_id]

while to_visit:
    node_id = to_visit.pop(0)
    if node_id in visited:
        continue
    visited.add(node_id)

    scene = ne.get_node(node_id)
    if scene is None:
        print(f"❌ MISSING SCENE: {node_id}")
        continue

    print(f"\n✓ Scene exists: {node_id} - '{scene.get('title')}'")

    choices = scene.get('choices', [])
    print(f"  Has {len(choices)} choices:")

    for i, choice in enumerate(choices, 1):
        choice_text = choice.get('text', '')
        next_node = choice.get('nextNode', '')

        # Check if next node exists
        next_scene = ne.get_node(next_node)
        status = "✓" if next_scene else "❌ MISSING"

        print(f"    {i}. {choice_text[:50]}...")
        print(f"       → {next_node} {status}")

        if next_scene and next_node not in visited:
            to_visit.append(next_node)

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total scenes found: {len(visited)}")
print(f"\nAll referenced scenes:")

# Find all referenced but missing scenes
all_referenced = set()
for node_id in visited:
    scene = ne.get_node(node_id)
    if scene:
        for choice in scene.get('choices', []):
            all_referenced.add(choice.get('nextNode'))

missing = all_referenced - visited
if missing:
    print(f"\n❌ MISSING SCENES ({len(missing)}):")
    for scene_id in sorted(missing):
        print(f"  - {scene_id}")
else:
    print("\n✓ All referenced scenes exist!")
