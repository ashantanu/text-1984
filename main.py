#!/usr/bin/env python3
"""
1984: A CLI Interactive Game
Main game loop and entry point
"""

import sys
import os
from typing import Optional, Dict, Any, List

from state_manager import StateManager
from narrative_engine import NarrativeEngine
from display import Display, Colors
from llm_processor import LLMProcessor


class Game:
    """Main game controller"""

    def __init__(self):
        self.state_manager = StateManager()
        self.narrative_engine = NarrativeEngine()
        self.display = Display()
        self.llm_processor = None
        self.running = False

    def initialize(self) -> bool:
        """Initialize the game systems"""
        try:
            # Try to initialize LLM processor
            self.llm_processor = LLMProcessor()
            return True
        except ValueError as e:
            self.display.print_error(str(e))
            self.display.print_warning("The game will run without natural language processing.")
            self.display.print_warning("You can still play using numbered choices.")
            input("\nPress Enter to continue...")
            return True
        except Exception as e:
            self.display.print_error(f"Failed to initialize game: {e}")
            return False

    def show_title_screen(self):
        """Display the title screen"""
        self.display.clear_screen()
        self.display.render_title_screen()

    def show_main_menu(self) -> str:
        """Show main menu and get user choice"""
        print(f"{Colors.BOLD}Main Menu:{Colors.RESET}\n")

        # Check if save file exists
        save_exists = os.path.exists("game-state.json")

        if save_exists:
            print(f"{Colors.YELLOW}1.{Colors.RESET} Continue Game")
            print(f"{Colors.YELLOW}2.{Colors.RESET} New Game (overwrites current save)")
            print(f"{Colors.YELLOW}3.{Colors.RESET} Exit")
            print()

            choice = input(f"{Colors.CYAN}> {Colors.RESET}").strip()

            if choice == "1":
                return "continue"
            elif choice == "2":
                confirm = input(f"{Colors.RED}Are you sure? This will delete your current save (y/n): {Colors.RESET}").strip().lower()
                if confirm == 'y':
                    return "new"
                return self.show_main_menu()
            elif choice == "3":
                return "exit"
        else:
            print(f"{Colors.YELLOW}1.{Colors.RESET} New Game")
            print(f"{Colors.YELLOW}2.{Colors.RESET} Exit")
            print()

            choice = input(f"{Colors.CYAN}> {Colors.RESET}").strip()

            if choice == "1":
                return "new"
            elif choice == "2":
                return "exit"

        return self.show_main_menu()

    def start_game(self):
        """Start the game"""
        self.show_title_screen()

        menu_choice = self.show_main_menu()

        if menu_choice == "exit":
            self.display.print_message("\nBIG BROTHER IS WATCHING YOU.", Colors.RED)
            return

        if menu_choice == "new":
            state = self.state_manager.create_new_state()
            self.state_manager.save_state()
            self.display.print_success("\nNew game started.")
            input(f"{Colors.DIM}Press Enter to begin...{Colors.RESET}")
        else:  # continue
            state = self.state_manager.load_state()
            self.display.print_success("\nGame loaded.")
            input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")

        self.running = True
        self.game_loop()

    def game_loop(self):
        """Main game loop"""
        while self.running:
            # Check for game over conditions
            game_over_type = self.state_manager.check_game_over()
            if game_over_type:
                self.handle_game_over(game_over_type)
                break

            # Get current node
            current_node_id = self.state_manager.state.get("currentNode", "prologue_start")
            current_scene = self.narrative_engine.get_current_scene(current_node_id)

            if current_scene is None:
                # Smart LLM fallback for missing scenes
                fallback_node = self.handle_missing_scene(current_node_id)
                if fallback_node:
                    self.state_manager.set_current_node(fallback_node)
                    continue
                else:
                    self.display.print_error(f"Error: Unable to recover from missing scene '{current_node_id}'")
                    break

            # Check if this is a terminal node (ending)
            if self.narrative_engine.is_terminal_node(current_node_id):
                self.handle_ending(current_scene)
                break

            # Get available choices
            available_choices = self.narrative_engine.get_available_choices(
                current_node_id, self.state_manager
            )

            if not available_choices:
                self.display.print_error("No available choices! This might be a bug.")
                break

            # Render the scene with choices
            self.render_scene_with_choices(current_scene, available_choices)

            # Get player input and process choice
            choice_made = self.get_player_choice(available_choices, current_scene)

            if choice_made is None:
                continue  # Special command was processed, loop again

            # Apply choice effects
            self.narrative_engine.apply_choice_effects(choice_made, self.state_manager)

            # Record the choice
            self.state_manager.record_choice(
                choice_made.get("id", ""),
                choice_made.get("text", ""),
                current_node_id
            )

            # Move to next node
            next_node_id = self.narrative_engine.get_next_node(choice_made)
            self.state_manager.set_current_node(next_node_id)

            # Save state
            self.state_manager.save_state()

            # Brief pause to let user see any effects/narrative
            print()  # Just add a blank line for visual spacing

    def render_scene_with_choices(self, scene: Dict, choices: List[Dict]):
        """Render a scene with choices using split-screen layout"""
        self.display.clear_screen()

        # Get state data for right panel
        stats = self.state_manager.get_stats()
        resources = self.state_manager.get_resources()
        location = self.state_manager.state.get("location", "")

        # Build left panel content
        left_content = []

        # Add ASCII art if available
        art_template = self.narrative_engine.get_ascii_art_template(scene.get("id", ""))
        if art_template:
            art_lines = self._get_ascii_art_lines(art_template)
            left_content.extend(art_lines)
            left_content.append("")  # Blank line

        # Add scene title
        title = scene.get("title", "")
        if title:
            left_content.append(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}")
            left_content.append(f"{Colors.BOLD}{Colors.CYAN}{title.center(70)}{Colors.RESET}")
            left_content.append(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}")
            left_content.append("")

        # Add narrative text (word-wrapped)
        narrative = scene.get("narrative", "")
        wrapped_lines = self._wrap_text(narrative, 70)
        left_content.extend(wrapped_lines)
        left_content.append("")
        left_content.append("")

        # Add choices
        left_content.append(f"{Colors.BOLD}{Colors.YELLOW}Available Actions:{Colors.RESET}")
        left_content.append("")
        for i, choice in enumerate(choices, 1):
            choice_text = choice.get("text", "")
            # Wrap long choice text
            if len(choice_text) > 65:
                choice_text = choice_text[:62] + "..."
            left_content.append(f"{Colors.YELLOW}{i}.{Colors.RESET} {choice_text}")

        left_content.append("")
        left_content.append(f"{Colors.DIM}Enter a number or describe your action:{Colors.RESET}")
        left_content.append(f"{Colors.DIM}(Type '/dossier' for stats, '/quit' to exit){Colors.RESET}")

        # Render split screen
        self.display.render_split_screen(left_content, stats, resources, location)

    def _get_ascii_art_lines(self, art_name: str) -> List[str]:
        """Get ASCII art as list of lines"""
        art_path = os.path.join(self.display.art_dir, f"{art_name}.txt")
        if os.path.exists(art_path):
            with open(art_path, 'r', encoding='utf-8') as f:
                return f.read().strip().split('\n')
        return []

    def _wrap_text(self, text: str, width: int) -> List[str]:
        """Wrap text to specified width"""
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += word + " "
            else:
                if current_line:
                    lines.append(current_line.rstrip())
                current_line = word + " "

        if current_line:
            lines.append(current_line.rstrip())

        return lines

    def get_player_choice(self, available_choices: list, current_scene: dict) -> Optional[dict]:
        """Get and process player choice"""
        while True:
            user_input = input(f"\n{Colors.CYAN}> {Colors.RESET}").strip()

            if not user_input:
                continue

            # Check for special commands
            if user_input.lower() in ['/quit', '/exit', 'quit', 'exit']:
                confirm = input(f"{Colors.YELLOW}Quit game? Progress will be saved. (y/n): {Colors.RESET}").strip().lower()
                if confirm == 'y':
                    self.state_manager.save_state()
                    self.display.print_message("\nGame saved. BIG BROTHER IS WATCHING YOU.", Colors.RED)
                    self.running = False
                    sys.exit(0)
                continue

            if user_input.lower() in ['/dossier', '/status', '/stats']:
                self.display.render_detailed_dossier(self.state_manager.state)
                self.render_scene(current_scene)
                self.display.render_choices(available_choices)
                continue

            # Check if it's a simple number choice
            if user_input.isdigit():
                choice_num = int(user_input)
                if 1 <= choice_num <= len(available_choices):
                    return available_choices[choice_num - 1]
                else:
                    self.display.print_error(f"Invalid choice. Please enter 1-{len(available_choices)}.")
                    continue

            # Use LLM to process natural language if available
            if self.llm_processor:
                result = self.llm_processor.process_user_input(
                    user_input, available_choices, current_scene, self.state_manager.state
                )

                if result["type"] == "choice":
                    # Show the LLM's narrative response if any
                    if result.get("response"):
                        print(f"\n{Colors.GRAY}{result['response']}{Colors.RESET}\n")

                    return available_choices[result["choice_index"]]

                elif result["type"] == "clarification_needed":
                    self.display.print_warning(result["response"])
                    continue

            else:
                # No LLM available, require numbered input
                self.display.print_error(f"Please enter a number (1-{len(available_choices)}).")
                continue

    def handle_missing_scene(self, missing_node_id: str) -> Optional[str]:
        """
        Smart LLM fallback for missing scenes
        Uses Claude to bridge the narrative gap and transition to a valid scene
        """
        self.display.print_warning(f"\n⚙ The story continues...")

        # Find a suitable fallback scene (go back to last known good state)
        fallback_candidates = [
            "prologue_inside_flat",  # Safe hub scene
            "prologue_start",  # Restart point
        ]

        # Try to find a fallback that exists
        fallback_node = None
        for candidate in fallback_candidates:
            if self.narrative_engine.get_node(candidate):
                fallback_node = candidate
                break

        if not fallback_node:
            return None

        # If LLM is available, generate bridging narrative
        if self.llm_processor:
            try:
                current_stats = self.state_manager.get_stats()
                previous_choices = self.state_manager.state.get("choiceHistory", [])
                last_choice = previous_choices[-1] if previous_choices else {}

                prompt = f"""You are narrating a 1984 interactive game. The player took an action that led to an undefined scene ('{missing_node_id}').

Current situation:
- Missing scene ID: {missing_node_id}
- Last choice: {last_choice.get('choiceText', 'unknown')}
- Party Loyalty: {current_stats.get('partyLoyalty', 0)}/100
- Suspicion: {current_stats.get('suspicionLevel', 0)}/100
- Thoughtcrime: {current_stats.get('thoughtcrimeIndex', 0)}/100

Write a brief (2-3 sentences) narrative bridge in Orwell's style that:
1. Acknowledges what just happened
2. Maintains immersion and doesn't break the 4th wall
3. Naturally transitions to Winston being back in his flat
4. Reflects the current mood based on stats (high suspicion = paranoia, etc.)

Keep it atmospheric and true to 1984's tone. DO NOT mention technical errors or missing scenes."""

                response = self.llm_processor.client.messages.create(
                    model=self.llm_processor.model,
                    max_tokens=200,
                    temperature=0.8,
                    messages=[{"role": "user", "content": prompt}]
                )

                bridge_narrative = response.content[0].text.strip()

                # Display the bridging narrative
                print(f"\n{Colors.GRAY}{bridge_narrative}{Colors.RESET}\n")

            except Exception as e:
                # Fallback to generic narrative if LLM fails
                print(f"\n{Colors.GRAY}You find yourself back in your flat, the moment passing like a half-remembered dream. The telescreen drones on with its endless statistics.{Colors.RESET}\n")

        else:
            # No LLM, use generic narrative
            print(f"\n{Colors.GRAY}Time passes. You find yourself back in your flat at Victory Mansions.{Colors.RESET}\n")

        input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")
        return fallback_node

    def handle_game_over(self, ending_type: str):
        """Handle game over"""
        self.display.render_game_over(ending_type)
        input(f"{Colors.DIM}Press Enter to exit...{Colors.RESET}")

    def handle_ending(self, ending_scene: dict):
        """Handle reaching an ending"""
        self.display.clear_screen()

        # Show final stats
        stats = self.state_manager.get_stats()
        resources = self.state_manager.get_resources()
        self.display.render_stats_panel(stats, resources)

        # Show ending scene
        self.display.render_scene(ending_scene)

        print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'THE END'.center(70)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}\n")

        # Show choice history summary
        choice_count = len(self.state_manager.state.get("choiceHistory", []))
        print(f"{Colors.DIM}You made {choice_count} choices in your journey through Oceania.{Colors.RESET}\n")

        input(f"{Colors.DIM}Press Enter to exit...{Colors.RESET}")


def main():
    """Main entry point"""
    game = Game()

    if not game.initialize():
        print("Failed to initialize game.")
        sys.exit(1)

    try:
        game.start_game()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.RED}BIG BROTHER IS WATCHING YOU.{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}An error occurred: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
