"""
Display Module for 1984 CLI Game
Handles all visual output including stats panel, ASCII art, and text formatting
"""

import os
from typing import Dict, Any, List, Optional


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

    # Text colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'

    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'


class Display:
    """Handles all visual output for the game"""

    def __init__(self, art_dir: str = "ascii_art"):
        self.art_dir = art_dir
        self.width = 70  # Standard terminal width for formatting
        self.left_panel_width = 75  # Width for left panel (content)
        self.right_panel_width = 40  # Width for right panel (stats + eye)
        self.total_width = self.left_panel_width + self.right_panel_width + 3

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def print_separator(self, char: str = "═", width: int = None):
        """Print a separator line"""
        if width is None:
            width = self.width
        print(char * width)

    def print_title_card(self, title: str):
        """Print a formatted title card"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}╔{'═' * (self.width - 2)}╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{title.center(self.width - 2)}║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}╚{'═' * (self.width - 2)}╝{Colors.RESET}\n")

    def render_stats_panel(self, stats: Dict[str, int], resources: Dict[str, int],
                           location: str = "", date: str = ""):
        """Render the stats panel (nvidia-smi style)"""
        print(f"{Colors.BOLD}{Colors.GREEN}╔{'═' * (self.width - 2)}╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}║{' MINISTRY OF TRUTH - PERSONNEL FILE: WINSTON SMITH'.ljust(self.width - 2)}║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}╠{'═' * (self.width - 2)}╣{Colors.RESET}")

        # Location and date
        if location:
            loc_line = f" Location: {location}"
            print(f"{Colors.GREEN}║{Colors.RESET}{loc_line.ljust(self.width - 2)}{Colors.GREEN}║{Colors.RESET}")
        if date:
            date_line = f" Date: {date}"
            print(f"{Colors.GREEN}║{Colors.RESET}{date_line.ljust(self.width - 2)}{Colors.GREEN}║{Colors.RESET}")

        if location or date:
            print(f"{Colors.GREEN}╠{'═' * (self.width - 2)}╣{Colors.RESET}")

        # Party Loyalty
        loyalty = stats.get("partyLoyalty", 0)
        loyalty_bar = self._create_bar(loyalty, 100, 30)
        loyalty_color = Colors.GREEN if loyalty >= 50 else Colors.YELLOW
        print(f"{Colors.GREEN}║{Colors.RESET} Party Loyalty:      {loyalty_color}{loyalty_bar} {str(loyalty).rjust(3)}/100{Colors.RESET}".ljust(self.width + 20) + f"{Colors.GREEN}║{Colors.RESET}")

        # Suspicion Level
        suspicion = stats.get("suspicionLevel", 0)
        suspicion_bar = self._create_bar(suspicion, 100, 30)

        # Color code based on danger level
        if suspicion >= 90:
            suspicion_color = Colors.RED
            warning = f"{Colors.BG_RED}{Colors.WHITE} CRITICAL {Colors.RESET}"
        elif suspicion >= 70:
            suspicion_color = Colors.YELLOW
            warning = f"{Colors.YELLOW}⚠ DANGER{Colors.RESET}"
        elif suspicion >= 40:
            suspicion_color = Colors.YELLOW
            warning = f"{Colors.YELLOW}⚠ WATCHED{Colors.RESET}"
        else:
            suspicion_color = Colors.GREEN
            warning = ""

        suspicion_line = f"{Colors.GREEN}║{Colors.RESET} Suspicion Level:    {suspicion_color}{suspicion_bar} {str(suspicion).rjust(3)}/100{Colors.RESET} {warning}"
        print(suspicion_line.ljust(self.width + 45) + f"{Colors.GREEN}║{Colors.RESET}")

        # Thoughtcrime Index
        thoughtcrime = stats.get("thoughtcrimeIndex", 0)
        thoughtcrime_bar = self._create_bar(thoughtcrime, 100, 30)
        thoughtcrime_color = Colors.RED if thoughtcrime >= 60 else Colors.YELLOW if thoughtcrime >= 30 else Colors.GREEN

        path_marker = f" {Colors.RED}[REBELLION PATH]{Colors.RESET}" if thoughtcrime >= 60 else ""
        thoughtcrime_line = f"{Colors.GREEN}║{Colors.RESET} Thoughtcrime Index: {thoughtcrime_color}{thoughtcrime_bar} {str(thoughtcrime).rjust(3)}/100{Colors.RESET}{path_marker}"
        print(thoughtcrime_line.ljust(self.width + 50) + f"{Colors.GREEN}║{Colors.RESET}")

        # Resources
        razors = resources.get("razors", 0)
        cigarettes = resources.get("cigarettes", 0)
        chocolate = resources.get("chocolate", 0)

        resources_line = f" Resources: Razors({razors}) Cigarettes({cigarettes}) Chocolate({chocolate})"
        print(f"{Colors.GREEN}║{Colors.RESET}{resources_line.ljust(self.width - 2)}{Colors.GREEN}║{Colors.RESET}")

        print(f"{Colors.BOLD}{Colors.GREEN}╚{'═' * (self.width - 2)}╝{Colors.RESET}\n")

    def _create_bar(self, value: int, max_value: int, bar_length: int = 30) -> str:
        """Create a progress bar visualization"""
        filled = int((value / max_value) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        return f"[{bar}]"

    def render_scene(self, node: Dict[str, Any]):
        """Render a scene with title and narrative"""
        title = node.get("title", "")
        narrative = node.get("narrative", "")

        # Print title
        if title:
            self.print_title_card(title)

        # Print narrative text with word wrapping
        self._print_wrapped_text(narrative, width=self.width)
        print()

    def render_choices(self, choices: List[Dict[str, Any]]):
        """Render available choices"""
        print(f"{Colors.BOLD}{Colors.CYAN}Available Actions:{Colors.RESET}\n")

        for i, choice in enumerate(choices, 1):
            choice_text = choice.get("text", "")
            print(f"{Colors.YELLOW}{i}.{Colors.RESET} {choice_text}")

        print(f"\n{Colors.DIM}Enter a number or describe your action in your own words:{Colors.RESET}")
        print(f"{Colors.DIM}(Type '/dossier' to view detailed stats, '/quit' to exit){Colors.RESET}")

    def render_ascii_art(self, art_name: str) -> bool:
        """Render ASCII art from file"""
        art_path = os.path.join(self.art_dir, f"{art_name}.txt")

        if not os.path.exists(art_path):
            return False

        try:
            with open(art_path, 'r', encoding='utf-8') as f:
                art = f.read()
                print(f"{Colors.CYAN}{art}{Colors.RESET}")
            return True
        except Exception as e:
            print(f"Error loading art: {e}")
            return False

    def render_title_screen(self):
        """Render the game title screen"""
        success = self.render_ascii_art("title")
        if not success:
            # Fallback if art file doesn't exist
            self.clear_screen()
            print(f"\n{Colors.BOLD}{Colors.RED}")
            print("  ╔═══════════════════════════════════════════════════════════════╗")
            print("  ║                                                               ║")
            print("  ║                        1 9 8 4                                ║")
            print("  ║                                                               ║")
            print("  ║            A CLI Interactive Experience                      ║")
            print("  ║                                                               ║")
            print("  ║              BIG BROTHER IS WATCHING YOU                      ║")
            print("  ║                                                               ║")
            print("  ╚═══════════════════════════════════════════════════════════════╝")
            print(f"{Colors.RESET}\n")

    def _print_wrapped_text(self, text: str, width: int = 70, indent: int = 0):
        """Print text with word wrapping"""
        words = text.split()
        lines = []
        current_line = " " * indent

        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                current_line += word + " "
            else:
                lines.append(current_line.rstrip())
                current_line = " " * indent + word + " "

        if current_line.strip():
            lines.append(current_line.rstrip())

        for line in lines:
            print(line)

    def print_message(self, message: str, color: str = Colors.WHITE):
        """Print a colored message"""
        print(f"{color}{message}{Colors.RESET}")

    def print_error(self, message: str):
        """Print an error message"""
        print(f"{Colors.RED}✗ {message}{Colors.RESET}")

    def print_success(self, message: str):
        """Print a success message"""
        print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

    def print_warning(self, message: str):
        """Print a warning message"""
        print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

    def render_game_over(self, ending_type: str):
        """Render game over screen"""
        self.clear_screen()
        print(f"\n{Colors.BOLD}{Colors.RED}")
        print("  ╔═══════════════════════════════════════════════════════════════╗")
        print("  ║                                                               ║")
        print("  ║                     GAME OVER                                 ║")
        print("  ║                                                               ║")

        if ending_type == "arrested_high_suspicion":
            print("  ║          THE THOUGHT POLICE HAVE ARRESTED YOU                 ║")
            print("  ║                                                               ║")
            print("  ║              You have been vaporized.                         ║")

        print("  ║                                                               ║")
        print("  ╚═══════════════════════════════════════════════════════════════╝")
        print(f"{Colors.RESET}\n")

    def render_detailed_dossier(self, state: Dict[str, Any]):
        """Render detailed player dossier"""
        self.clear_screen()

        stats = state.get("stats", {})
        resources = state.get("resources", {})
        inventory = state.get("inventory", [])
        relationships = state.get("relationships", {})

        print(f"{Colors.BOLD}{Colors.CYAN}╔{'═' * (self.width - 2)}╗{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}║{'PARTY DOSSIER - WINSTON SMITH'.center(self.width - 2)}║{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}╠{'═' * (self.width - 2)}╣{Colors.RESET}")

        # Stats
        print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}Statistics:{Colors.RESET}".ljust(self.width + 13) + f"{Colors.CYAN}║{Colors.RESET}")
        for stat_name, value in stats.items():
            stat_display = stat_name.replace("partyLoyalty", "Party Loyalty") \
                                    .replace("suspicionLevel", "Suspicion Level") \
                                    .replace("thoughtcrimeIndex", "Thoughtcrime Index")
            print(f"{Colors.CYAN}║{Colors.RESET}   {stat_display}: {value}/100".ljust(self.width + 13) + f"{Colors.CYAN}║{Colors.RESET}")

        print(f"{Colors.CYAN}╠{'═' * (self.width - 2)}╣{Colors.RESET}")

        # Inventory
        print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}Inventory:{Colors.RESET}".ljust(self.width + 13) + f"{Colors.CYAN}║{Colors.RESET}")
        for item in inventory:
            print(f"{Colors.CYAN}║{Colors.RESET}   • {item}".ljust(self.width + 13) + f"{Colors.CYAN}║{Colors.RESET}")

        print(f"{Colors.CYAN}╠{'═' * (self.width - 2)}╣{Colors.RESET}")

        # Relationships
        print(f"{Colors.CYAN}║{Colors.RESET} {Colors.BOLD}Known Associates:{Colors.RESET}".ljust(self.width + 13) + f"{Colors.CYAN}║{Colors.RESET}")
        for npc, data in relationships.items():
            status = data.get("status", "unknown")
            trust = data.get("trustLevel", 0)
            npc_display = npc.capitalize()
            print(f"{Colors.CYAN}║{Colors.RESET}   {npc_display}: {status} (Trust: {trust})".ljust(self.width + 13) + f"{Colors.CYAN}║{Colors.RESET}")

        print(f"{Colors.BOLD}{Colors.CYAN}╚{'═' * (self.width - 2)}╝{Colors.RESET}\n")

        input(f"{Colors.DIM}Press Enter to continue...{Colors.RESET}")

    def render_split_screen(self, left_content: List[str], stats: Dict[str, int],
                           resources: Dict[str, int], location: str = ""):
        """Render split-screen layout with content on left, persistent panel on right"""
        # Get right panel lines
        right_panel = self._build_right_panel(stats, resources, location)

        # Ensure both panels have same height
        max_height = max(len(left_content), len(right_panel))

        # Pad shorter panel
        while len(left_content) < max_height:
            left_content.append(" " * self.left_panel_width)
        while len(right_panel) < max_height:
            right_panel.append(" " * self.right_panel_width)

        # Render line by line
        for left_line, right_line in zip(left_content, right_panel):
            # Ensure proper width
            left_padded = left_line[:self.left_panel_width].ljust(self.left_panel_width)
            right_padded = right_line[:self.right_panel_width].ljust(self.right_panel_width)
            print(f"{left_padded} │ {right_padded}")

    def _build_right_panel(self, stats: Dict[str, int], resources: Dict[str, int],
                           location: str) -> List[str]:
        """Build the persistent right panel with eye and stats"""
        lines = []

        # Top border
        lines.append(f"{Colors.RED}╔{'═' * (self.right_panel_width - 2)}╗{Colors.RESET}")
        lines.append(f"{Colors.RED}║{' ' * (self.right_panel_width - 2)}║{Colors.RESET}")

        # Load and display Big Brother eye
        eye_art = self._load_eye_art()
        for eye_line in eye_art:
            # Center the eye in the panel
            eye_padded = eye_line.center(self.right_panel_width - 2)
            lines.append(f"{Colors.RED}║{Colors.RESET}{eye_padded}{Colors.RED}║{Colors.RESET}")

        # "BIG BROTHER IS WATCHING YOU" text
        lines.append(f"{Colors.RED}║{' ' * (self.right_panel_width - 2)}║{Colors.RESET}")
        watching_text = "BIG BROTHER IS"
        watching_text2 = "WATCHING YOU"
        lines.append(f"{Colors.RED}║{Colors.RESET}{Colors.BOLD}{watching_text.center(self.right_panel_width - 2)}{Colors.RESET}{Colors.RED}║{Colors.RESET}")
        lines.append(f"{Colors.RED}║{Colors.RESET}{Colors.BOLD}{watching_text2.center(self.right_panel_width - 2)}{Colors.RESET}{Colors.RED}║{Colors.RESET}")
        lines.append(f"{Colors.RED}║{' ' * (self.right_panel_width - 2)}║{Colors.RESET}")

        # Divider
        lines.append(f"{Colors.RED}╠{'═' * (self.right_panel_width - 2)}╣{Colors.RESET}")

        # Stats with colorful bars
        lines.append(f"{Colors.RED}║{Colors.RESET} {Colors.BOLD}REAL-TIME MONITORING{Colors.RESET}".ljust(self.right_panel_width + 10) + f"{Colors.RED}║{Colors.RESET}")
        lines.append(f"{Colors.RED}╠{'═' * (self.right_panel_width - 2)}╣{Colors.RESET}")

        # Party Loyalty
        loyalty = stats.get("partyLoyalty", 0)
        loyalty_bar = self._create_colored_bar(loyalty, 20, "loyalty")
        lines.append(f"{Colors.RED}║{Colors.RESET} Loyalty: {loyalty_bar}".ljust(self.right_panel_width + 20) + f"{Colors.RED}║{Colors.RESET}")

        # Suspicion Level
        suspicion = stats.get("suspicionLevel", 0)
        suspicion_bar = self._create_colored_bar(suspicion, 20, "suspicion")
        warning = ""
        if suspicion >= 90:
            warning = f" {Colors.BG_RED}{Colors.WHITE}CRITICAL{Colors.RESET}"
        elif suspicion >= 70:
            warning = f" {Colors.YELLOW}⚠DANGER{Colors.RESET}"
        lines.append(f"{Colors.RED}║{Colors.RESET} Suspicion: {suspicion_bar}{warning}".ljust(self.right_panel_width + 35) + f"{Colors.RED}║{Colors.RESET}")

        # Thoughtcrime
        thoughtcrime = stats.get("thoughtcrimeIndex", 0)
        thoughtcrime_bar = self._create_colored_bar(thoughtcrime, 20, "thoughtcrime")
        tc_warning = f" {Colors.RED}[REBEL]{Colors.RESET}" if thoughtcrime >= 60 else ""
        lines.append(f"{Colors.RED}║{Colors.RESET} Thoughtcrime: {thoughtcrime_bar}{tc_warning}".ljust(self.right_panel_width + 30) + f"{Colors.RED}║{Colors.RESET}")

        lines.append(f"{Colors.RED}╠{'═' * (self.right_panel_width - 2)}╣{Colors.RESET}")

        # Resources
        razors = resources.get("razors", 0)
        cigarettes = resources.get("cigarettes", 0)
        chocolate = resources.get("chocolate", 0)

        lines.append(f"{Colors.RED}║{Colors.RESET} {Colors.BOLD}Resources:{Colors.RESET}".ljust(self.right_panel_width + 13) + f"{Colors.RED}║{Colors.RESET}")
        lines.append(f"{Colors.RED}║{Colors.RESET}  Razors: {Colors.CYAN}{razors}{Colors.RESET}".ljust(self.right_panel_width + 13) + f"{Colors.RED}║{Colors.RESET}")
        lines.append(f"{Colors.RED}║{Colors.RESET}  Cigarettes: {Colors.CYAN}{cigarettes}{Colors.RESET}".ljust(self.right_panel_width + 13) + f"{Colors.RED}║{Colors.RESET}")
        lines.append(f"{Colors.RED}║{Colors.RESET}  Chocolate: {Colors.CYAN}{chocolate}{Colors.RESET}".ljust(self.right_panel_width + 13) + f"{Colors.RED}║{Colors.RESET}")

        # Bottom border
        lines.append(f"{Colors.RED}╚{'═' * (self.right_panel_width - 2)}╝{Colors.RESET}")

        return lines

    def _load_eye_art(self) -> List[str]:
        """Load the Big Brother eye ASCII art"""
        eye_path = os.path.join(self.art_dir, "big_brother_eye.txt")
        if os.path.exists(eye_path):
            with open(eye_path, 'r', encoding='utf-8') as f:
                lines = f.read().strip().split('\n')
                # Scale down the eye to fit in the panel (take every other line)
                return [line[:30] for i, line in enumerate(lines) if i % 2 == 0][:8]
        return ["     👁️      "]  # Fallback emoji

    def _create_colored_bar(self, value: int, bar_length: int, stat_type: str) -> str:
        """Create a colorful progress bar based on stat type"""
        filled = int((value / 100) * bar_length)

        # Choose color based on stat type and value
        if stat_type == "loyalty":
            if value >= 70:
                color = Colors.GREEN
            elif value >= 40:
                color = Colors.YELLOW
            else:
                color = Colors.RED
        elif stat_type == "suspicion":
            if value >= 70:
                color = Colors.RED
            elif value >= 40:
                color = Colors.YELLOW
            else:
                color = Colors.GREEN
        elif stat_type == "thoughtcrime":
            if value >= 60:
                color = Colors.MAGENTA
            elif value >= 30:
                color = Colors.YELLOW
            else:
                color = Colors.CYAN
        else:
            color = Colors.WHITE

        bar = f"{color}{'█' * filled}{'░' * (bar_length - filled)}{Colors.RESET}"
        return f"[{bar}] {value:>3}"
