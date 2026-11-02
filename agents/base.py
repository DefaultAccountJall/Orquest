from typing import Type
from pydantic import BaseModel
from Orquest.core.llm import ask_structured
import Orquest.config as config

class Agent:
    name: str = "agent"
    system_prompt: str = ""
    output_schema: Type[BaseModel]
    model: str | None = None

    def render(self, **context) -> str:
        parts = []
        for k, v in context.items():
            if isinstance(v, dict):
                body = "\n\n".join(
                    f"### {path}\n```\n{content}\n```" for path, content in v.items()
                )
                parts.append(f"## {k}\n{body}")
            else:
                parts.append(f"## {k}\n{v}")
        return "\n\n".join(parts)

    def run(self, **context) -> BaseModel:
        user = self.render(**context)
        return ask_structured(
            self.system_prompt, user, self.output_schema,
            model=self.model or config.MODEL,
        )