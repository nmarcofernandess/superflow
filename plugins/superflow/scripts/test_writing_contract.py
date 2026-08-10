#!/usr/bin/env python3
"""Verify the human-facing writing contract shipped by Superflow."""

from __future__ import annotations

from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]


def read(relative: str) -> str:
    path = PLUGIN_ROOT / relative
    if not path.exists():
        raise AssertionError(f"missing required writing artifact: {relative}")
    return path.read_text(encoding="utf-8")


def require(text: str, markers: list[str], context: str) -> None:
    for marker in markers:
        if marker not in text:
            raise AssertionError(f"{context} missing marker: {marker}")


def main() -> int:
    writing = read("skills/writing-clearly-and-concisely/SKILL.md")
    elements = read("skills/writing-clearly-and-concisely/elements-of-style.md")
    router = read("skills/superflow/SKILL.md")
    html = read("skills/html-didatico/SKILL.md")
    recipe = read("skills/html-didatico/references/receita.md")

    require(writing, ["name: writing-clearly-and-concisely", "Use active voice", "Omit needless words"], "writing skill")
    require(elements, ["# The Elements of Style", "Rule 10. Use the active voice.", "Rule 13. Omit needless words."], "style reference")
    require(router, ["writing-clearly-and-concisely", "human-facing prose"], "Superflow router")
    require(
        html,
        [
            "REQUIRED SUB-SKILL",
            "writing-clearly-and-concisely",
            "Clareza sem burocracia",
            "O motor funciona em pequena escala; a execução completa continua bloqueada.",
        ],
        "HTML writing contract",
    )
    require(recipe, ["aspect-ratio: 1", "flex: 0 0", "fundo deve definir também a cor do texto"], "HTML recipe")

    print("OK: Superflow writing contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
