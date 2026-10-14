#!/usr/bin/env python3
"""Render the profile header as two SVGs, one per GitHub theme.

Standard library only. Run from the repository root:

    python scripts/make_header.py
"""

from pathlib import Path

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "panel": "#161b22",
        "border": "#30363d",
        "text": "#e6edf3",
        "muted": "#7d8590",
        "accent": "#3fb950",
        "accent2": "#2ea043",
        "accent3": "#238636",
        "eye": "#e6edf3",
        "pupil": "#0d1117",
    },
    "light": {
        "bg": "#ffffff",
        "panel": "#f6f8fa",
        "border": "#d1d9e0",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#1a7f37",
        "accent2": "#2da44e",
        "accent3": "#4ac26b",
        "eye": "#ffffff",
        "pupil": "#1f2328",
    },
}

WIDTH, HEIGHT = 900, 230
FONT = "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace"


def caterpillar(c: dict) -> str:
    """Pixel-ish caterpillar on the right, body segments bob in a wave."""
    parts = []
    base_x, base_y = 640, 128
    segments = 6
    shades = [c["accent3"], c["accent2"]]
    for i in range(segments):
        x = base_x + i * 26
        delay = (segments - i) * 0.12
        fill = shades[i % 2]
        parts.append(
            f'<g class="seg" style="animation-delay:-{delay:.2f}s">'
            f'<line x1="{x + 9}" y1="{base_y + 26}" x2="{x + 7}" y2="{base_y + 36}" '
            f'stroke="{c["muted"]}" stroke-width="3" stroke-linecap="round"/>'
            f'<line x1="{x + 21}" y1="{base_y + 26}" x2="{x + 23}" y2="{base_y + 36}" '
            f'stroke="{c["muted"]}" stroke-width="3" stroke-linecap="round"/>'
            f'<rect x="{x}" y="{base_y}" width="30" height="30" rx="10" fill="{fill}"/>'
            f"</g>"
        )
    hx = base_x + segments * 26
    hy = base_y - 14
    parts.append(
        f'<g class="seg head" style="animation-delay:0s">'
        f'<line x1="{hx + 12}" y1="{hy + 2}" x2="{hx + 6}" y2="{hy - 16}" '
        f'stroke="{c["accent"]}" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="{hx + 6}" cy="{hy - 18}" r="4" fill="{c["accent"]}"/>'
        f'<line x1="{hx + 26}" y1="{hy + 2}" x2="{hx + 32}" y2="{hy - 16}" '
        f'stroke="{c["accent"]}" stroke-width="3" stroke-linecap="round"/>'
        f'<circle cx="{hx + 32}" cy="{hy - 18}" r="4" fill="{c["accent"]}"/>'
        f'<rect x="{hx}" y="{hy}" width="40" height="40" rx="13" fill="{c["accent"]}"/>'
        f'<g class="blink">'
        f'<circle cx="{hx + 27}" cy="{hy + 15}" r="6" fill="{c["eye"]}"/>'
        f'<circle cx="{hx + 29}" cy="{hy + 16}" r="3" fill="{c["pupil"]}"/>'
        f"</g>"
        f"</g>"
    )
    # Ground line the caterpillar walks on.
    parts.append(
        f'<line x1="{base_x - 20}" y1="{base_y + 38}" x2="{hx + 70}" y2="{base_y + 38}" '
        f'stroke="{c["border"]}" stroke-width="2" stroke-dasharray="2 8" stroke-linecap="round"/>'
    )
    return "\n    ".join(parts)


def render(c: dict) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">
  <title id="title">dxmoc</title>
  <desc id="desc">Small tools that do one thing, need nothing and keep working.</desc>
  <style>
    text {{ font-family: {FONT}; }}
    .seg {{ animation: bob 1.4s ease-in-out infinite; transform-box: fill-box; }}
    .blink {{ animation: blink 5s steps(1) infinite; transform-box: fill-box; transform-origin: center; }}
    .cursor {{ animation: cursor 1.1s steps(1) infinite; }}
    @keyframes bob {{ 0%, 100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-7px); }} }}
    @keyframes blink {{ 0%, 96% {{ transform: scaleY(1); }} 97%, 99% {{ transform: scaleY(0.1); }} }}
    @keyframes cursor {{ 0%, 50% {{ opacity: 1; }} 51%, 100% {{ opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{ .seg, .blink, .cursor {{ animation: none; }} }}
  </style>
  <rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="14" fill="{c["panel"]}" stroke="{c["border"]}" stroke-width="2"/>

  <text x="44" y="58" font-size="15" fill="{c["muted"]}">~ $ whoami</text>
  <text x="42" y="118" font-size="56" font-weight="700" fill="{c["text"]}" letter-spacing="-1">dxmoc</text>
  <rect class="cursor" x="222" y="76" width="26" height="46" rx="2" fill="{c["accent"]}"/>

  <text x="44" y="156" font-size="17" fill="{c["text"]}">Small tools that do one thing, need nothing</text>
  <text x="44" y="180" font-size="17" fill="{c["text"]}">and keep working.</text>

  <text x="44" y="210" font-size="13" fill="{c["muted"]}">python  /  c#  /  css</text>

  {caterpillar(c)}
</svg>
"""


def main() -> None:
    out = Path("assets")
    out.mkdir(exist_ok=True)
    for name, colors in THEMES.items():
        path = out / f"header-{name}.svg"
        path.write_text(render(colors), encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
