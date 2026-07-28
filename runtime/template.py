import re

from runtime.context import ActionContext


_PATTERN = re.compile(r"\{\{\s*(.*?)\s*\}\}")


def render(text: str, context: ActionContext) -> str:
    """
    Render template variables inside a string.

    Supported:

        {{user}}
        {{company}}
        {{project.name}}
    """

    def replace(match):
        key = match.group(1)

        if key.startswith("project."):
            value = context.project

            for part in key.split(".")[1:]:
                value = value.get(part)

                if value is None:
                    return ""

            return str(value)

        return str(
            context.get_variable(
                key,
                "",
            )
        )

    return _PATTERN.sub(replace, text)
