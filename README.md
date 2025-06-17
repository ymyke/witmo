# Calls

python ./witmo.py -i "C:\code\witmo\history\elden-ring\cap_20250615_222200.jpg" -nc -s all=high story=none -g "elden ring" -l DEBUG
python ./witmo.py -d -s all=high story=none -g "elden ring"


# TODO

- remove openapi key from entire history
- review all the messages/prints
- clean up all dependencies and produce a nice requirements.txt or poetry file.
- commands:
- add voice
- have a command that displays the full prompt pack? (e.g. "?")
- get rid of archive after having voice option
- save history file more often? -- or turn it into a context mgr as well so it gets saved no matter what.

-----------------------------------

# New interaction model

- set up: camera, history, ...
- mainloop:
  - show menu
    - <space> - image flow
    - <enter> - text flow = which is also follow-up to last prompt/response
    - "^" - pick another prompt from the preconfigured list TODO
    - "!" - switch voice on/off (maybe also have a cli arg?) TODO
    - "." - choose model: 3=o3, 4=4o, 5=4.5 TODO
    - <backspace> - resend last prompt (e.g., after changing the model) TODO
    - <esc> - quit
  - image flow:
    - get image via capture (<space>) 
    - choose a prompt or enter (<enter>) own prompt
      - (jump here directly initially if image is passed from command line)
    - send to llm
    - review response
  - text flow:
    - send to llm
    - review response


-----------------------------------

# Overall application logic

- set up: camera, history, ...
- mainloop: three options:
  - capture a new picture (<space> key) and start a chatloop with it and a choice of
    pre-configured prompts (mapped to keys) or with a new prompt (<enter> key) [1]
  - only in the very first iteration of the mainloop and if a picture is passed from the
    command line: jump into prompt selection above directly and start a chatloop from
    there
  - start a chatloop without a picture
- chatloop:
  - send image and prompt to model, display response
  - user can ask follow-up questions
  - user can capture a new picture (for the same chatloop)
  - user can quit

[1] ask if prompt should be added to a list of pre-configured prompts afterwards?


-----------------------------------

# readme / manual notes

- list requirements
- explain how to enable debug mode

## Spoiler Settings (CLI)

You can control what types of spoilers Witmo is allowed to reveal using the `--spoilers` flag:

Examples:

    python witmo.py --spoilers all=low story=none halo

- `all=low` sets all categories to low spoilers.
- `story=none` overrides the story category to no spoilers.
- The last positional argument is always the game name.
- Default: `all=none` (no spoilers).

Categories: items, locations, enemies, bosses, story, lore, mechanics
Levels: none, low, medium, high

You can combine as many category=level pairs as you want:

    python witmo.py --spoilers items=high bosses=medium mechanics=low halo

## Usage Example (with explicit game name)

    python witmo.py --game halo --spoilers all=low story=none

- The game name is now specified with --game or -g.
- Spoiler settings can be given in any order.


