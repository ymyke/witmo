from typing import List, Dict

DEFAULT_CATEGORIES: List[str] = [
    "items",
    "locations",
    "enemies",
    "bosses",
    "story",
    "lore",
    "mechanics",
]

DEFAULT_LEVEL: str = "none"
VALID_LEVELS: List[str] = ["none", "low", "medium", "high"]

SPOILER_RULES: str = """\
Spoiler Levels

- none: generic advice; no names/locations/items/bosses. Example "Pay attention to the
  dialogue—it may clue you in on what's coming next."  

- low: broad hints; indirect, no proper nouns. Example "Some characters' backstories
  become important later—keep an ear out for their personal details."  

- medium: concrete strategies; names, item categories, exploits. Example "After you meet
  the Silver Regent in Act II, her true motives will shape the final chapters—remember
  her promise about the lost heirloom."  

- high: full deep details; stats, coordinates, plot twists, item locations. Example "In
  Chapter 5 you'll discover that the Mentor was the antagonist all along—he orchestrated
  the betrayal at Dawnbridge."  

If it's clear where the player currently is in the game's progression, you may freely
reference any content up to that point (past). Only details beyond that point (future)
are subject to the spoiler-level rules below. Always give rich, local detail—only future
content is gated by spoilers. 

On all levels above "low," you should mention any key items, quests, or mechanics the
user absolutely shouldn't miss for later in the game.  

"""


def parse_spoiler_args(spoiler_args: List[str]) -> Dict[str, str]:
    """Parse a list of key=level pairs (e.g., ["all=low", "story=none"]) into a dict.
    Raises ValueError for malformed pairs or invalid levels/categories.

    - "all" sets every category to the given level.
    - Individual categories override the "all" setting.
    """
    settings: Dict[str, str] = {cat: DEFAULT_LEVEL for cat in DEFAULT_CATEGORIES}

    for arg in spoiler_args:
        if "=" not in arg:
            raise ValueError(
                f"Malformed spoiler argument '{arg}', expected format key=level"
            )

        key, val = map(str.strip, arg.lower().split("=", 1))

        if val not in VALID_LEVELS:
            raise ValueError(
                f"Invalid spoiler level '{val}'. Must be one of {VALID_LEVELS}."
            )

        if key == "all":
            for cat in DEFAULT_CATEGORIES:
                settings[cat] = val
        elif key in settings:
            settings[key] = val
        else:
            raise ValueError(
                f"Unknown spoiler category '{key}'. Valid categories: {DEFAULT_CATEGORIES}."
            )

    return settings


def generate_spoiler_prompt(settings: Dict[str, str]) -> str:

    template = """\
Spoiler rules:

{spoiler_rules}

The user's spoiler preferences:

{spoiler_prefs}

When generating advice, obey the spoiler rules and configuration strictly.
"""

    spoiler_prefs = ""
    for cat in DEFAULT_CATEGORIES:
        level = settings.get(cat, DEFAULT_LEVEL)
        spoiler_prefs += f"- {cat.capitalize()}: {level}\n"

    s = template.format(spoiler_rules=SPOILER_RULES, spoiler_prefs=spoiler_prefs)

    return s
