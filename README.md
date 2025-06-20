
# rich interface

- welcome screen: displayed just once, nice and fancy.
- llm requests: part of main loop, prominent but not super prominent
- llm responses: main outcome of the entire app, prominent, premium, good to read, render as markdown
- system messages/updates: regular, subdued, medium grey?
- menus: all menus as nice tables of key/menu pairs
  - main menu: capture screens etc.; often
  - select prompt menu: to select prompt to send along with image; often
  - utility menus: any other menu of minor importance; rarely, make "unaufgeregt"
- user text input: for custom prompts; regularly, clear and readable



# README notes

- mention that it currently supports ER but can be extended used for any game, esp when adding a prompt pack. cf ...

# Calls

python ./witmo.py -i "C:\code\witmo\history\elden-ring\cap_20250615_222200.jpg" -nc -s all=high story=none -g "elden ring" -l DEBUG
python ./witmo.py -tc -s all=low story=none -g "elden ring" -c -l TRACE
python ./witmo.py -c -d -s all=high story=none -g "elden ring"


# TODO

- make the markdown output able to handle " • " as bullet points
- maybe print 2-column output if the response is too long?
- remove openapi key from entire history
- review all the messages/prints
- clean up all dependencies and produce a nice requirements.txt or poetry file.
- display capture again
- generic prompt pack for any game w/o specific pack?
- android app?

-----------------------------------

# New interaction model

- set up: camera, history, session, ...
- mainloop:
  - show menu
    - <space> - image flow
    - <enter> - text flow (which is also follow-up to last prompt/response)
    - ".", "!", "?" etc. commands
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


