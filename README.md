# TODO

- add the name of the game to the system prompt instead of each new use prompt
- add spoiler settings / levels: initially just as a simple add-on to the system prompt?
- can we get really useful info?
- work well w history?
- store prompts somehow?
- prompt packs per game + a generic pack (or generic packs per genre)?
- try to get video capture via ps5 app, identify key frames, send to llm and get tipps from that.
- give the model some sources to check out? (e.g. wikis, guides, etc.) -- in the system prompt?
- in general, better use 3o or 4.5?
- add colors to outputs? (e.g., make system messages grey, user input sth, llm output sth etc.)
- add better support for longer input? e.g., via prompt_toolkit or so?
  - maybe allow user to edit prompt after choosing one and before it gets sent to llm?
- remove openapi key from entire history
- review all the messages/prints
- clean up all dependencies and produce a nice 
  requirements.txt or poetry file.
- should there be an aliases_map that maps, e.g., "ER" to "Elden Ring"?
- put this part from the prompt map to  the system prompt? "Focus on giving me insights, help me understand, provide truly useful information."
- break lines in output
- have some "working..." animation
- commands:
  - have a command that cycles through the models that are supported: o3, 4.5, both, ...
  - have a command prefix "v" that will produce voice output for the next completion. Or
    that simply enables/disables voice output?

## prompt improvements

don't just read out everything.
        "text": "Elden Ring: Describe what we see here and help me understand what's happening. Do not just read out what is there. I can read the screen myself. Focus on giving me insights, help me understand, provide truly useful information."
    "content": "for the current level of my character, is this a good weapon or should i be able to find sth much better?"

system prompt:
  - make sure to get the latest versions of all sources by reloading them!
  - revise in general to make max effective

## prompt ideas

- what can i safely sell (because there's a lot of it in the world) and what should i definitely keep?
- "What is the most important, non-trivial hint you can give for this situation?"
  - both 3o and 4.5 give good results here.


-------------------

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
  - user can capture a new picture (for the same chatloop) [2]
  - user can quit

[1] ask if prompt should be added to a list of pre-configured prompts afterwards?
[2] not implemented yet


