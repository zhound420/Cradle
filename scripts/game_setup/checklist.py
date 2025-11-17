"""Interactive checklist system for manual setup steps."""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ChecklistItem:
    """A single checklist item."""
    id: str
    title: str
    description: str
    instructions: List[str]
    optional: bool = False
    image_path: Optional[str] = None
    completed: bool = False


class InteractiveChecklist:
    """Interactive checklist for manual game setup steps."""

    def __init__(self, game_name: str, items: List[ChecklistItem]):
        """Initialize checklist with items."""
        self.game_name = game_name
        self.items = items
        self.current_index = 0

    def display_header(self):
        """Display checklist header."""
        print("\n" + "=" * 70)
        print(f"  🎮 {self.game_name.upper()} SETUP CHECKLIST")
        print("=" * 70)

        completed = sum(1 for item in self.items if item.completed)
        total = len(self.items)
        print(f"\nProgress: {completed}/{total} steps completed\n")

    def display_item(self, item: ChecklistItem, index: int):
        """Display a single checklist item."""
        marker = "✓" if item.completed else " "
        optional = " (Optional)" if item.optional else ""

        print(f"\n[{marker}] Step {index + 1}/{len(self.items)}: {item.title}{optional}")
        print("-" * 70)

        if item.description:
            print(f"\n{item.description}\n")

        if item.instructions:
            print("Instructions:")
            for i, instruction in enumerate(item.instructions, 1):
                print(f"  {i}. {instruction}")

        if item.image_path and os.path.exists(item.image_path):
            print(f"\n📷 Reference image: {item.image_path}")

        print()

    def run_interactive(self, skip_completed: bool = True) -> bool:
        """
        Run interactive checklist.

        Args:
            skip_completed: Skip items already marked as completed

        Returns:
            True if all required items completed, False otherwise
        """
        self.display_header()

        for i, item in enumerate(self.items):
            if skip_completed and item.completed:
                continue

            self.display_item(item, i)

            while True:
                if item.optional:
                    response = input("✓ Mark as done  ⏭️  Skip  ❌ Quit (d/s/q): ").lower().strip()
                else:
                    response = input("✓ Mark as done  ❌ Quit (d/q): ").lower().strip()

                if response in ['d', 'done', 'y', 'yes', '']:
                    item.completed = True
                    print("  ✓ Marked as completed\n")
                    break
                elif response in ['s', 'skip'] and item.optional:
                    print("  ⏭️  Skipped (optional step)\n")
                    break
                elif response in ['q', 'quit', 'exit']:
                    print("\n⚠️  Setup interrupted")
                    return False
                else:
                    if item.optional:
                        print("  Invalid input. Use 'd' (done), 's' (skip), or 'q' (quit)")
                    else:
                        print("  Invalid input. Use 'd' (done) or 'q' (quit)")

        # Check completion
        required_items = [item for item in self.items if not item.optional]
        required_completed = sum(1 for item in required_items if item.completed)

        self.display_header()

        if required_completed == len(required_items):
            print("✅ All required setup steps completed!\n")
            return True
        else:
            print(f"⚠️  {len(required_items) - required_completed} required steps still incomplete\n")
            return False

    def run_display_only(self):
        """Display checklist without interaction (for documentation)."""
        self.display_header()

        for i, item in enumerate(self.items):
            self.display_item(item, i)

            status = "✓ Completed" if item.completed else "⏳ Pending"
            print(f"Status: {status}\n")

    def get_completion_status(self) -> Dict[str, any]:
        """Get completion statistics."""
        total = len(self.items)
        completed = sum(1 for item in self.items if item.completed)
        required = sum(1 for item in self.items if not item.optional)
        required_completed = sum(1 for item in self.items if item.completed and not item.optional)

        return {
            'total': total,
            'completed': completed,
            'required': required,
            'required_completed': required_completed,
            'all_required_done': required_completed == required,
            'all_done': completed == total,
        }

    def save_progress(self, filepath: str):
        """Save checklist progress to file."""
        import json

        data = {
            'game_name': self.game_name,
            'items': [
                {
                    'id': item.id,
                    'completed': item.completed,
                }
                for item in self.items
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

    def load_progress(self, filepath: str):
        """Load checklist progress from file."""
        import json

        if not os.path.exists(filepath):
            return

        with open(filepath, 'r') as f:
            data = json.load(f)

        # Update completion status
        completed_ids = {item['id'] for item in data['items'] if item['completed']}

        for item in self.items:
            if item.id in completed_ids:
                item.completed = True
