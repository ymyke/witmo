import textwrap
import re


def pw(text, width=100, **kwargs):
    "Print wrapped"
    if not isinstance(text, str):
        text = str(text)
    bullet_regex = re.compile(r"^(\s*)([\d]+[.)]|[\-•])\s+")
    for line in text.splitlines():
        match = bullet_regex.match(line)
        if match:
            # Indent wrapped lines to align with the text after bullet/number
            prefix = match.group(0)
            indent = " " * len(prefix)
            print(textwrap.fill(line, width=width, subsequent_indent=indent), **kwargs)
        else:
            print(textwrap.fill(line, width=width), **kwargs)
