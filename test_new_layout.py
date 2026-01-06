#!/usr/bin/env python3
"""
Test the new split-screen layout
"""

from display import Display, Colors

# Create display
display = Display()

# Test stats
stats = {
    "partyLoyalty": 65,
    "suspicionLevel": 42,
    "thoughtcrimeIndex": 28
}

resources = {
    "razors": 2,
    "cigarettes": 3,
    "chocolate": 0
}

# Create sample left content
left_content = [
    "",
    "    ╔═══════════════════════════════════════════════════════════╗",
    "    ║                   VICTORY MANSIONS                        ║",
    "    ╚═══════════════════════════════════════════════════════════╝",
    "",
    f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}",
    f"{Colors.BOLD}{Colors.CYAN}{'The Clocks Were Striking Thirteen'.center(70)}{Colors.RESET}",
    f"{Colors.BOLD}{Colors.CYAN}{'═' * 70}{Colors.RESET}",
    "",
    "It was a bright cold day in April, and the clocks were striking",
    "thirteen. Winston Smith, his chin nuzzled into his breast in an",
    "effort to escape the vile wind, slipped quickly through the glass",
    "doors of Victory Mansions.",
    "",
    "The hallway smelt of boiled cabbage and old rag mats.",
    "",
    "",
    f"{Colors.BOLD}{Colors.YELLOW}Available Actions:{Colors.RESET}",
    "",
    f"{Colors.YELLOW}1.{Colors.RESET} Stop and observe the Big Brother poster carefully",
    f"{Colors.YELLOW}2.{Colors.RESET} Hurry inside to your flat, avoiding attention",
    f"{Colors.YELLOW}3.{Colors.RESET} Glance nervously at the telescreen",
    "",
    f"{Colors.DIM}Enter a number or describe your action:{Colors.RESET}",
    f"{Colors.DIM}(Type '/dossier' for stats, '/quit' to exit){Colors.RESET}",
]

# Clear and render
display.clear_screen()
display.render_split_screen(left_content, stats, resources, "Victory Mansions")

print("\n")
print(f"{Colors.CYAN}> {Colors.RESET}", end="")
