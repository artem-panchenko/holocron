"""Render stream using Jinja2 template engine."""

import os

import jinja2
import jsonpointer

from .. import source
from .._misc import parameters


@parameters(
    jsonschema={
        "type": "object",
        "properties": {
            "template": {"type": "string"},
            "context": {"type": "object"},
            "themes": {"type": "array", "items": {"type": "string"}},
        },
    },
)
def process(app, stream, *, template="item.j2", context={}, themes=None):
    if themes is None:
        themes = [os.path.join(os.path.dirname(__file__), "theme")]

    env = jinja2.Environment(loader=jinja2.ChoiceLoader([
        # Jinja2 processor may receive a list of themes, and we want to look
        # for templates in passed order. The rationale here is to provide
        # a way to override templates or populate a list of supported ones.
        jinja2.FileSystemLoader(os.path.join(theme, "templates"))
        for theme in themes
    ]))
    env.filters["jsonpointer"] = jsonpointer.resolve_pointer

    for item in stream:
        item["content"] = \
            env.get_template(item.get("template", template)).render(
                item=item,
                metadata=app.metadata,
                **context)
        yield item

    # Themes may optionally come with various statics (e.g. css, images) they
    # depend on. That's why we need to inject these statics to the stream;
    # otherwise, rendered items may look improperly.
    for theme in themes:
        yield from source.process(app, [], path=theme, pattern=r"static/")
