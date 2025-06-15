- need some completion abstraction or sth?
- history:
  - why does history work at all if there's no global var called history?
  - try w empty history
  - are images saved and sent again?
  - should we save timestamps?
  - are new entries saved? I think not...
  - is prevented that the entire history gets saved with every new entry?
  - do we have a clear separator between prompt and history?



- add the name of the game to the system prompt instead of each new use prompt

- add test mode with pseudocamera?
- use camera.start, camera.stop, camera.capture as the simplest interface?
    - do we need the encoding stuff in there?
    - maybe use a context mgr for the camera?

- make sure the camera app is running!
- make foto deletion optional

- add spoiler settings / levels

- make sure the image is part of the history
- how to cope with ever longer history -- with different threads and images?
- can we get really useful info?
- work well w history?

- store prompts somehow?
- prompt packs per game + a generic pack (or generic packs per genre)?
- try to get video capture via ps5 app, identify key frames, send to llm and get tipps from that.
- give the model some sources to check out? (e.g. wikis, guides, etc.) -- in the system prompt?

- "What is the most important, non-trivial hint you can give for this situation?"
  - both 3o and 4.5 give good results here.

- in general, better use 3o or 4.5?

- add the possibility to add more captures during a chat session?

- remove openapi key from entire history

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

# commands

- have a command that cycles through the models that are supported: o3, 4.5, both, ...
- have a command prefix "v" that will produce voice output for the next completion. Or
  that simply enables/disables voice output?

# prompt improvements

don't just read out everything.
        "text": "Elden Ring: Describe what we see here and help me understand what's happening. Do not just read out what is there. I can read the screen myself. Focus on giving me insights, help me understand, provide truly useful information."
    "content": "for the current level of my character, is this a good weapon or should i be able to find sth much better?"

system prompt:
  - make sure to get the latest versions of all sources by reloading them!
  - revise in general to make max effective

# prompt ideas

- what can i safely sell (because there's a lot of it in the world) and what should i definitely keep?