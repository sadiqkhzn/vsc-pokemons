#!/usr/bin/env python3
"""
Set originalSpriteSize per pokemon based on real Pokedex height.

Reference: Bulbasaur at 0.7m -> 32 (matches how Gen 1-4 already renders).
Formula:   size = clamp(round(32 * (h_m / 0.7) ** (1/3)), 22, 58)

Cube-root scaling with a tight [22, 58] cap. Cube root preserves proportional
spread at mid-range so similar-height pokemon (Gligar 1.1m vs Snorlax 2.1m)
look distinctly different, while the 58-pixel cap prevents giants (Wailord
14.5m, Onix 8.8m) from dominating the panel. All huge legendaries cluster at
58 which is a fair tradeoff for realistic mid-range proportions.

Updates only Gen 5 and Gen 6 entries. Skips Gen 1-4 which are already tuned.
Skips size 32 (extension default) so we don't add redundant fields.

Caches PokeAPI heights to /tmp/pokemon_heights_cache.json to make re-runs fast.
"""
from __future__ import annotations
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "src" / "common" / "pokemon-data.ts"
CACHE = Path("/tmp/pokemon_heights_cache.json")

REF_H = 0.7
REF_S = 32
UA = "vsc-pokemons-sizer/1.0 (github.com/sadiqkhzn/vsc-pokemons)"


def size_for(h_m: float) -> int:
    return max(22, min(58, round(REF_S * (h_m / REF_H) ** (1 / 3))))


def load_cache() -> dict[str, float]:
    if CACHE.exists():
        return json.loads(CACHE.read_text())
    return {}


def save_cache(cache: dict[str, float]) -> None:
    CACHE.write_text(json.dumps(cache))


def fetch_h(dex: int, cache: dict[str, float]) -> float | None:
    key = str(dex)
    if key in cache:
        return cache[key]
    req = urllib.request.Request(
        f"https://pokeapi.co/api/v2/pokemon/{dex}/", headers={"User-Agent": UA}
    )
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=15) as r:
                h = json.loads(r.read().decode())["height"] / 10.0
                cache[key] = h
                return h
        except Exception:
            if i < 2:
                time.sleep(1 + i)
    return None


def parse_entries(content: str) -> list[tuple[str, int, int]]:
    """Return [(key, dex, gen), ...] for Gen 5 and Gen 6 entries."""
    out: list[tuple[str, int, int]] = []
    seen = set()
    # Single-line
    for m in re.finditer(
        r"^\s+(\w+): \{ id: (\d+),[^\n]*PokemonGeneration\.Gen(\d)",
        content, flags=re.MULTILINE,
    ):
        key, dex, gen = m.group(1), int(m.group(2)), int(m.group(3))
        if key not in seen:
            out.append((key, dex, gen))
            seen.add(key)
    # Multi-line
    for m in re.finditer(
        r"^\s+(\w+): \{\n\s+id: (\d+),(?:[^{}]*?)generation: PokemonGeneration\.Gen(\d)",
        content, flags=re.MULTILINE,
    ):
        key, dex, gen = m.group(1), int(m.group(2)), int(m.group(3))
        if key not in seen:
            out.append((key, dex, gen))
            seen.add(key)
    return out


def apply_size(content: str, key: str, new_size: int) -> tuple[str, str]:
    """Returns (updated_content, action) where action is 'replace' / 'insert' /
    'remove' / 'noop' / 'miss'."""
    # Single-line replace existing
    pat1 = rf"(^\s+{re.escape(key)}: \{{[^\n]+originalSpriteSize:\s*)\d+([^\n]*\}},\s*$)"
    if new_size == REF_S:
        rem1 = rf"(^\s+{re.escape(key)}: \{{[^\n]+?), originalSpriteSize:\s*\d+( [^\n]*\}},\s*$)"
        c2, n = re.subn(rem1, r"\g<1>\g<2>", content, flags=re.MULTILINE)
        if n > 0:
            return c2, "remove"
    c2, n = re.subn(pat1, rf"\g<1>{new_size}\g<2>", content, flags=re.MULTILINE)
    if n > 0:
        return c2, "replace"
    # Single-line insert
    if new_size != REF_S:
        ins1 = rf"(^\s+{re.escape(key)}: \{{[^\n]+possibleColors: \[[^\]]+\](?:, isFlying: true)?)( \}},\s*$)"
        c2, n = re.subn(
            ins1, rf"\g<1>, originalSpriteSize: {new_size}\g<2>", content, flags=re.MULTILINE
        )
        if n > 0:
            return c2, "insert"
    # Multi-line replace
    ml_r = rf"(^\s+{re.escape(key)}: \{{\n(?:[^\n]+\n)*?\s+originalSpriteSize:\s*)\d+"
    c2, n = re.subn(ml_r, rf"\g<1>{new_size}", content, flags=re.MULTILINE)
    if n > 0:
        return c2, "replace"
    # Multi-line insert
    if new_size != REF_S:
        ml_i = rf"(^\s+{re.escape(key)}: \{{\n(?:[^\n]+\n)*?\s+possibleColors: \[[^\]]+\],\n)(  \}},)"
        c2, n = re.subn(ml_i, rf"\g<1>    originalSpriteSize: {new_size},\n\g<2>", content, flags=re.MULTILINE)
        if n > 0:
            return c2, "insert"
    return content, "noop" if new_size == REF_S else "miss"


def main() -> int:
    content = DATA.read_text()
    entries = parse_entries(content)
    print(f"parsed {len(entries)} Gen5+6 entries")

    cache = load_cache()
    heights: dict[str, tuple[int, float, int]] = {}
    failed: list[str] = []
    for i, (key, dex, gen) in enumerate(entries):
        h = fetch_h(dex, cache)
        if h is None:
            failed.append(key)
            continue
        heights[key] = (dex, h, size_for(h))
    save_cache(cache)
    print(f"got heights: {len(heights)}/{len(entries)} (failed: {failed})")

    counts = {"replace": 0, "insert": 0, "remove": 0, "noop": 0, "miss": 0}
    for key, (dex, h, size) in heights.items():
        content, action = apply_size(content, key, size)
        counts[action] += 1

    DATA.write_text(content)
    print(f"actions: {counts}")

    # Show a sample of the changes for spot-checking
    for k in ("snivy", "serperior", "zekrom", "reshiram", "dialga", "chandelure",
              "wailord", "yveltal", "xerneas", "kyurem", "chespin", "greninja",
              "chesnaught", "sylveon"):
        if k in heights:
            dex, h, size = heights[k]
            print(f"  {k:14s} #{dex}  h={h:>4.1f}m  size={size}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
