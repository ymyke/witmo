from loguru import logger
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
Game Progress Context  

If it's clear where the player currently is in the game's progression, you may freely reference any content up to that point (past). Only details beyond that point (future) are subject to the spoiler-level rules below.  
On all levels above “low,” you should mention any key items, quests, or mechanics the user absolutely shouldn't miss for later in the game.  

Spoiler Levels

- none: Provide only generic advice. No names, no locations, no item or boss references.  
Examples:  
  • “You might experiment with different weapon types.”  
  • “Pay attention to the dialogue—it may clue you in on what's coming next.”

- low: Offer broad hints and reframed guidance. Indirect clues, no explicit mechanics or proper nouns.  
Examples:  
  • “Consider exploiting elemental weaknesses.”  
  • “You might try using a ranged weapon.”  
  • “Some characters' backstories become important later—keep an ear out for their personal details.”

- medium: Share concrete strategies and identifiers. Boss or enemy names, item categories, known exploits.  
Examples:  
  • “The Forest Guardian is vulnerable to fire spells.”  
  • “You can farm Rare Mushrooms in the Misty Cavern to craft health potions.”  
  • “After you meet the Silver Regent in Act II, her true motives will shape the final chapters—remember her promise about the lost heirloom.”

- high: Full disclosure, deep details. Exact stats, map coordinates, plot twists, item locations.  
Examples:  
  • “The hidden chest in level 3 sits at X=24, Y=12 and holds the Flame Sword.”  
  • “The boss's health pool is 10,000 HP.”  
  • “In Chapter 5 you'll discover that the Mentor was the antagonist all along—he orchestrated the betrayal at Dawnbridge.”  

"""


def parse_spoiler_args(spoiler_args: List[str]) -> Dict[str, str]:
    """
    Parse a list of key=level pairs (e.g., ["all=low", "story=none"]) into a dict.
    Raises ValueError for malformed pairs or invalid levels/categories.

    - "all" sets every category to the given level.
    - Individual categories override the "all" setting.

    Logs warnings for malformed items before raising exceptions.
    """
    settings: Dict[str, str] = {cat: DEFAULT_LEVEL for cat in DEFAULT_CATEGORIES}

    for arg in spoiler_args:
        if "=" not in arg:
            logger.warning(
                f"Malformed spoiler argument '{arg}', expected format key=level"
            )
            raise ValueError(
                f"Malformed spoiler argument '{arg}', expected format key=level"
            )

        key, val = map(str.strip, arg.lower().split("=", 1))

        if val not in VALID_LEVELS:
            logger.warning(
                f"Invalid spoiler level '{val}'. Must be one of {VALID_LEVELS}."
            )
            raise ValueError(
                f"Invalid spoiler level '{val}'. Must be one of {VALID_LEVELS}."
            )

        if key == "all":
            for cat in DEFAULT_CATEGORIES:
                settings[cat] = val
        elif key in settings:
            settings[key] = val
        else:
            logger.warning(
                f"Unknown spoiler category '{key}'. Valid categories: {DEFAULT_CATEGORIES}."
            )
            raise ValueError(
                f"Unknown spoiler category '{key}'. Valid categories: {DEFAULT_CATEGORIES}."
            )

    return settings


def generate_spoiler_prompt(settings: Dict[str, str]) -> str:
    """
    Format the spoiler settings as a preamble for the system prompt.

    This groups categories into Narrative vs Gameplay,
    and provides a brief example of what each level entails:

    - none: no explicit names or details (e.g., “avoid mentioning the boss name”).
    - low: hints or indirect guidance (e.g., “you might try using a ranged weapon”).
    - medium: moderate disclosure (e.g., “the boss is weak to fire spells”).
    - high: full spoilers (e.g., “the boss's health pool is 10,000 HP”).
    """

    template = """\
Spoiler rules:

{spoiler_rules}

The user's spoiler preferences:

Use the user's per-category levels (below) to filter your response.

{spoiler_prefs}

When generating advice, obey the spoiler rules and configuration strictly.
"""

    spoiler_prefs = ""
    for cat in DEFAULT_CATEGORIES:
        level = settings.get(cat, DEFAULT_LEVEL)
        spoiler_prefs += f"- {cat.capitalize()}: {level}\n"

    s = template.format(spoiler_rules=SPOILER_RULES, spoiler_prefs=spoiler_prefs)

    return s
