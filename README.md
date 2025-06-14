
while True:
    wait for any key press
    if key == "q":
        quit
    # (start here directly if image passed from command line)
    capture picture
    ask for prompt
    start chat with picture, prompt, and history


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

# prompt ideas

- what can i safely sell (because there's a lot of it in the world) and what should i definitely keep?