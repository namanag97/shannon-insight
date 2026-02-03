#!/usr/bin/env python3
"""
Example usage of the spec generation agent.

This demonstrates how to use the agent programmatically
instead of through the CLI.
"""

from agent import generate_spec

# Example 1: Simple idea
idea1 = "A task management app for remote teams"

# Example 2: More specific idea
idea2 = """
A platform where freelance designers can showcase their portfolios,
and clients can browse, compare, and hire designers for projects.
Budget: $50k, Timeline: 6 months, Target: 10k users in year 1.
"""

# Example 3: Technical idea
idea3 = """
A real-time collaborative code editor (like Google Docs but for code).
Must support: syntax highlighting, multiple languages, WebSocket sync,
and conflict resolution. Scale: 1000 concurrent users per session.
"""

if __name__ == "__main__":
    print("=" * 60)
    print("Spec Generation Agent - Examples")
    print("=" * 60)
    print("\nAvailable examples:")
    print("1. Task management app")
    print("2. Designer portfolio platform")
    print("3. Real-time code editor")
    print()

    choice = input("Select example (1-3) or enter custom idea: ").strip()

    if choice == "1":
        idea = idea1
    elif choice == "2":
        idea = idea2
    elif choice == "3":
        idea = idea3
    else:
        idea = choice

    print(f"\nGenerating spec for: {idea}\n")

    generate_spec(idea, output_file=f"example_spec.md")

    print("\n✅ Done! Check example_spec.md for the full specification.")
