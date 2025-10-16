#!/usr/bin/env python3
"""
Generate a coverage badge for the README.md file.
This script reads the coverage.xml file and generates a shields.io badge.
"""

import xml.etree.ElementTree as ET
import re
import sys
from pathlib import Path


def get_coverage_percentage():
    """Extract coverage percentage from coverage.xml"""
    coverage_file = Path("coverage.xml")
    if not coverage_file.exists():
        print("coverage.xml not found. Run tests first.", file=sys.stderr)
        return None

    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        line_rate = float(root.get("line-rate", 0))
        return round(line_rate * 100, 1)
    except Exception as e:
        print(f"Error parsing coverage.xml: {e}", file=sys.stderr)
        return None


def get_badge_color(percentage):
    """Get badge color based on coverage percentage"""
    if percentage >= 90:
        return "brightgreen"
    elif percentage >= 80:
        return "green"
    elif percentage >= 70:
        return "yellowgreen"
    elif percentage >= 60:
        return "yellow"
    else:
        return "red"


def update_readme_badge(percentage, color):
    """Update the coverage badge in README.md"""
    readme_path = Path("README.md")
    if not readme_path.exists():
        print("README.md not found.", file=sys.stderr)
        return False

    # Read current README
    with open(readme_path, 'r') as f:
        content = f.read()

    # Create new badge
    new_badge = f"[![Coverage](https://img.shields.io/badge/coverage-{percentage}%25-{color}.svg)](coverage.xml)"

    # Replace existing coverage badge or add new one
    badge_pattern = r'\[!\[Coverage\].*?\]\(.*?\)'
    if re.search(badge_pattern, content):
        content = re.sub(badge_pattern, new_badge, content)
    else:
        # Add after the first line (title)
        lines = content.split('\n')
        lines.insert(1, new_badge)
        content = '\n'.join(lines)

    # Write back to README
    with open(readme_path, 'w') as f:
        f.write(content)

    print(f"Updated README.md with coverage badge: {percentage}%")
    return True


def main():
    percentage = get_coverage_percentage()
    if percentage is None:
        sys.exit(1)

    color = get_badge_color(percentage)
    if update_readme_badge(percentage, color):
        print(f"Coverage badge updated: {percentage}% ({color})")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
