#!/usr/bin/env python3
"""
Download PMD SpriteCollab Idle + Walk animations for Gen 5 pokemon and
regenerate the sprite GIFs so they visually match Gen 1-4 (pixel art, 32x32-ish).

Fixes two problems introduced when Gen 5 was first added:
  1. default_walk_8fps.gif was a copy of the idle GIF -> "sliding" walk.
  2. Idle and walk came from different sources (Showdown for idle, none for
     walk), so a mismatch would appear the moment we regenerated walk alone.

Right-facing frames are extracted (row 2 of the PMD 8-direction sheet).

Requires: python3, PIL (Pillow), internet access.
Usage:    python3 scripts/download-pmd-walk-gen5.py [--dry-run] [--only 495,527]
"""

from __future__ import annotations

import argparse
import io
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image

# ----------------------------------------------------------------------
# PMD sprite sheet convention: rows correspond to 8 movement directions.
# We extract row 2 (Right) so the walk faces right by default.
# 0=Down 1=DownRight 2=Right 3=UpRight 4=Up 5=UpLeft 6=Left 7=DownLeft
# ----------------------------------------------------------------------
WALK_ROW = 2

MEDIA_ROOT = Path(__file__).resolve().parent.parent / "media"
MEDIA_DIR = MEDIA_ROOT / "gen5"  # kept for backward compatibility
PMD_BASE = "https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/sprite"

# Dex ranges per generation → media folder
DEX_TO_GEN = [
    (range(1, 152), "gen1"),
    (range(152, 252), "gen2"),
    (range(252, 387), "gen3"),
    (range(387, 494), "gen4"),
    (range(494, 650), "gen5"),
    (range(650, 722), "gen6"),
]


def _gen_dir_for(dex: int) -> Path:
    for r, g in DEX_TO_GEN:
        if dex in r:
            return MEDIA_ROOT / g
    return MEDIA_DIR

# Gen 5 dex ID -> folder name (must match keys registered in
# src/common/pokemon-data.ts). If a Pokémon has no PMD entry (rare
# legendary etc.) it will just be skipped and the existing sliding
# GIF stays in place — the extension still works, just less polished.
GEN5: dict[int, str] = {
    495: "snivy", 496: "servine", 497: "serperior",
    498: "tepig", 499: "pignite", 500: "emboar",
    501: "oshawott", 502: "dewott", 503: "samurott",
    504: "patrat", 505: "watchog",
    506: "lillipup", 507: "herdier", 508: "stoutland",
    509: "purrloin", 510: "liepard",
    511: "pansage", 512: "simisage", 513: "pansear", 514: "simisear",
    515: "panpour", 516: "simipour",
    517: "munna", 518: "musharna",
    519: "pidove", 520: "tranquill", 521: "unfezant",
    522: "blitzle", 523: "zebstrika",
    524: "roggenrola", 525: "boldore", 526: "gigalith",
    527: "woobat", 528: "swoobat",
    529: "drilbur", 530: "excadrill",
    531: "audino",
    532: "timburr", 533: "gurdurr", 534: "conkeldurr",
    535: "tympole", 536: "palpitoad", 537: "seismitoad",
    538: "throh", 539: "sawk",
    540: "sewaddle", 541: "swadloon", 542: "leavanny",
    543: "venipede", 544: "whirlipede", 545: "scolipede",
    546: "cottonee", 547: "whimsicott", 548: "petilil", 549: "lilligant",
    550: "basculin",
    551: "sandile", 552: "krokorok", 553: "krookodile",
    554: "darumaka", 555: "darmanitan",
    556: "maractus", 557: "dwebble", 558: "crustle",
    559: "scraggy", 560: "scrafty",
    561: "sigilyph", 562: "yamask", 563: "cofagrigus",
    564: "tirtouga", 565: "carracosta", 566: "archen", 567: "archeops",
    568: "trubbish", 569: "garbodor",
    570: "zorua", 571: "zoroark",
    572: "minccino", 573: "cinccino",
    574: "gothita", 575: "gothorita", 576: "gothitelle",
    577: "solosis", 578: "duosion", 579: "reuniclus",
    580: "ducklett", 581: "swanna",
    582: "vanillite", 583: "vanillish", 584: "vanilluxe",
    585: "deerling", 586: "sawsbuck",
    587: "emolga",
    588: "karrablast", 589: "escavalier",
    590: "foongus", 591: "amoonguss",
    592: "frillish", 593: "jellicent",
    594: "alomomola",
    595: "joltik", 596: "galvantula",
    597: "ferroseed", 598: "ferrothorn",
    599: "klink", 600: "klang", 601: "klinklang",
    602: "tynamo", 603: "eelektrik", 604: "eelektross",
    605: "elgyem", 606: "beheeyem",
    607: "litwick", 608: "lampent", 609: "chandelure",
    610: "axew", 611: "fraxure", 612: "haxorus",
    613: "cubchoo", 614: "beartic",
    615: "cryogonal",
    616: "shelmet", 617: "accelgor",
    618: "stunfisk",
    619: "mienfoo", 620: "mienshao",
    621: "druddigon",
    622: "golett", 623: "golurk",
    624: "pawniard", 625: "bisharp",
    626: "bouffalant",
    627: "rufflet", 628: "braviary",
    629: "vullaby", 630: "mandibuzz",
    631: "heatmor", 632: "durant",
    633: "deino", 634: "zweilous", 635: "hydreigon",
    636: "larvesta", 637: "volcarona",
    638: "cobalion", 639: "terrakion", 640: "virizion",
    641: "tornadus", 642: "thundurus",
    643: "reshiram", 644: "zekrom",
    645: "landorus", 646: "kyurem",
    647: "keldeo", 648: "meloetta", 649: "genesect",
}

GEN6: dict[int, str] = {
    650: "chespin", 651: "quilladin", 652: "chesnaught",
    653: "fennekin", 654: "braixen", 655: "delphox",
    656: "froakie", 657: "frogadier", 658: "greninja",
    659: "bunnelby", 660: "diggersby",
    661: "fletchling", 662: "fletchinder", 663: "talonflame",
    664: "scatterbug", 665: "spewpa", 666: "vivillon",
    667: "litleo", 668: "pyroar",
    669: "flabebe", 670: "floette", 671: "florges",
    672: "skiddo", 673: "gogoat",
    674: "pancham", 675: "pangoro",
    676: "furfrou",
    677: "espurr", 678: "meowstic",
    679: "honedge", 680: "doublade", 681: "aegislash",
    682: "spritzee", 683: "aromatisse",
    684: "swirlix", 685: "slurpuff",
    686: "inkay", 687: "malamar",
    688: "binacle", 689: "barbaracle",
    690: "skrelp", 691: "dragalge",
    692: "clauncher", 693: "clawitzer",
    694: "helioptile", 695: "heliolisk",
    696: "tyrunt", 697: "tyrantrum",
    698: "amaura", 699: "aurorus",
    700: "sylveon",
    701: "hawlucha",
    702: "dedenne", 703: "carbink",
    704: "goomy", 705: "sliggoo", 706: "goodra",
    707: "klefki",
    708: "phantump", 709: "trevenant",
    710: "pumpkaboo", 711: "gourgeist",
    712: "bergmite", 713: "avalugg",
    714: "noibat", 715: "noivern",
    716: "xerneas", 717: "yveltal", 718: "zygarde",
    719: "diancie", 720: "hoopa", 721: "volcanion",
}

ALL: dict[int, str] = {**GEN5, **GEN6}


def fetch(url: str, retries: int = 3) -> bytes:
    last_err = None
    for i in range(retries):
        try:
            with urllib.request.urlopen(url, timeout=20) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            last_err = e
        except Exception as e:  # pragma: no cover - transient net errors
            last_err = e
        time.sleep(1 + i)
    raise last_err  # type: ignore[misc]


def _find_anim(root: ET.Element, wanted: str) -> ET.Element | None:
    for anim in root.find("Anims").findall("Anim"):
        if anim.find("Name").text == wanted:
            return anim
    return None


def _fetch_frames(dex: int, anim_name: str) -> tuple[list[Image.Image], list[int]] | str:
    """Return (frames, durations_ms) or an error status string."""
    dex_str = f"{dex:04d}"
    try:
        xml_bytes = fetch(f"{PMD_BASE}/{dex_str}/AnimData.xml")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "no-anim-data"
        raise

    root = ET.fromstring(xml_bytes)
    anim = _find_anim(root, anim_name)
    if anim is None:
        return "no-walk"

    fw = int(anim.find("FrameWidth").text)
    fh = int(anim.find("FrameHeight").text)
    durations = [int(d.text) for d in anim.find("Durations").findall("Duration")]

    try:
        png_bytes = fetch(f"{PMD_BASE}/{dex_str}/{anim_name}-Anim.png")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return "no-png"
        raise

    sheet = Image.open(io.BytesIO(png_bytes))
    sheet_w, sheet_h = sheet.size
    n_frames = sheet_w // fw
    n_rows = sheet_h // fh
    row = WALK_ROW if WALK_ROW < n_rows else 0

    row_y = row * fh
    frames = []
    for i in range(n_frames):
        crop = sheet.crop((i * fw, row_y, (i + 1) * fw, row_y + fh))
        frames.append(crop.convert("RGBA"))

    frame_ms: list[int] = []
    for i in range(n_frames):
        d = durations[i % len(durations)] if durations else 4
        frame_ms.append(max(60, min(int(d * 33), 220)))
    return frames, frame_ms


def _pad_frame(img: Image.Image, target_w: int, target_h: int) -> Image.Image:
    """Pad an RGBA frame to (target_w, target_h) with the sprite bottom-center anchored.
    This is what keeps the character's feet at a consistent Y so the extension's
    bottom-based positioning doesn't make the sprite appear to float or jump when
    the animation switches between different-sized source frames."""
    if img.size == (target_w, target_h):
        return img
    canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
    x = (target_w - img.width) // 2
    y = target_h - img.height  # bottom-align
    canvas.paste(img, (x, y), img)
    return canvas


def _save_gif(frames: list[Image.Image], frame_ms: list[int], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=frame_ms,
        loop=0,
        disposal=2,
        transparency=0,
    )


def _per_frame_align(frames: list[Image.Image], target_w: int, target_h: int) -> list[Image.Image]:
    """For each frame, tight-crop to its own non-transparent content, then paste
    into a (target_w, target_h) canvas horizontally centered and bottom-aligned.
    Character's lowest visible pixel lands at the frame bottom so a
    bottom-anchored CSS position puts the feet on the floor line, and the
    surrounding transparent padding keeps proportions natural when the browser
    stretches the sprite to a fixed square (matching Gen 1-4 convention)."""
    out = []
    for f in frames:
        bbox = f.getbbox()
        if bbox is None:
            out.append(Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0)))
            continue
        content = f.crop(bbox)
        # If content exceeds target, scale down proportionally (rare — only for
        # very large mons whose PMD sprite happens to be bigger than target).
        if content.width > target_w or content.height > target_h:
            scale = min(target_w / content.width, target_h / content.height)
            new_w = max(1, int(content.width * scale))
            new_h = max(1, int(content.height * scale))
            content = content.resize((new_w, new_h), Image.NEAREST)
        canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        x = (target_w - content.width) // 2
        y = target_h - content.height  # bottom-align
        canvas.paste(content, (x, y), content)
        out.append(canvas)
    return out


def _choose_target_size(max_w: int, max_h: int) -> int:
    """Pick a square canvas size matching Gen 1-4 conventions.
    Gen 1-4 uses 32x32 for most pokemon, 64x64 only for large ones (Dialga etc).
    We mirror that so all Gen 5 sprites render at natural in-frame proportions
    against the extension's fixed square CSS box."""
    if max(max_w, max_h) <= 32:
        return 32
    return 64


def build_pokemon(dex: int, name: str, *, dry_run: bool) -> tuple[str, str, int]:
    """Build both idle and walk with the character bottom-center anchored inside
    a Gen 1-4-style square canvas (32x32 or 64x64). Returns
    (walk_status, idle_status, target_size)."""
    idle_result = _fetch_frames(dex, "Idle")
    walk_result = _fetch_frames(dex, "Walk")

    idle_ok = isinstance(idle_result, tuple)
    walk_ok = isinstance(walk_result, tuple)
    idle_status = "ok" if idle_ok else idle_result
    walk_status = "ok" if walk_ok else walk_result

    if not (idle_ok or walk_ok):
        return walk_status, idle_status, 32

    all_frames: list[Image.Image] = []
    if idle_ok:
        all_frames.extend(idle_result[0])
    if walk_ok:
        all_frames.extend(walk_result[0])

    max_w = 0
    max_h = 0
    for f in all_frames:
        bbox = f.getbbox()
        if bbox is None:
            continue
        max_w = max(max_w, bbox[2] - bbox[0])
        max_h = max(max_h, bbox[3] - bbox[1])
    if max_w == 0 or max_h == 0:
        return walk_status, idle_status, 32

    target = _choose_target_size(max_w, max_h)

    if dry_run:
        return walk_status, idle_status, target

    out_dir = _gen_dir_for(dex) / name
    if idle_ok:
        idle_frames, idle_ms = idle_result
        _save_gif(
            _per_frame_align(idle_frames, target, target),
            idle_ms,
            out_dir / "default_idle_8fps.gif",
        )
    if walk_ok:
        walk_frames, walk_ms = walk_result
        _save_gif(
            _per_frame_align(walk_frames, target, target),
            walk_ms,
            out_dir / "default_walk_8fps.gif",
        )

    # Ensure shiny_*.gif exist so the extension doesn't 404 on shiny spawns.
    # PMD doesn't provide shiny palettes, so we fall back to the default GIFs.
    # (Gen 1-5 already have Showdown-style shinies from the original setup;
    # for Gen 6 species this is a fresh copy so shiny spawns render *something*.)
    for kind in ("idle", "walk"):
        default_path = out_dir / f"default_{kind}_8fps.gif"
        shiny_path = out_dir / f"shiny_{kind}_8fps.gif"
        if default_path.exists() and not shiny_path.exists():
            shiny_path.write_bytes(default_path.read_bytes())

    return walk_status, idle_status, target


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="don't write files, just probe PMDCollab")
    parser.add_argument("--only", type=str, default=None, help="comma-separated dex ids to run (e.g. 495,527,635)")
    args = parser.parse_args()

    targets = ALL
    if args.only:
        wanted = {int(x) for x in args.only.split(",")}
        targets = {k: v for k, v in ALL.items() if k in wanted}

    walk_counts = {"ok": 0, "no-anim-data": 0, "no-walk": 0, "no-png": 0, "error": 0}
    idle_counts = {"ok": 0, "no-anim-data": 0, "no-walk": 0, "no-png": 0, "error": 0}
    large_pokemon: list[str] = []  # need originalSpriteSize: 64 in pokemon-data.ts

    for dex, name in sorted(targets.items()):
        try:
            walk_status, idle_status, target = build_pokemon(dex, name, dry_run=args.dry_run)
        except Exception as e:  # pragma: no cover
            walk_status = idle_status = "error"
            target = 32
            print(f"  FAIL {name:16s} #{dex}  {e}", file=sys.stderr)
        walk_counts[walk_status] += 1
        idle_counts[idle_status] += 1
        if target == 64 and (walk_status == "ok" or idle_status == "ok"):
            large_pokemon.append(name)
        marker_map = {
            "ok": "OK  ",
            "no-anim-data": "MISS",
            "no-walk": "SKIP",
            "no-png": "SKIP",
            "error": "FAIL",
        }
        print(
            f"  walk={marker_map[walk_status]} idle={marker_map[idle_status]} "
            f"target={target:2d}  {name:16s} #{dex}"
        )

    print()
    print(f"walk: {walk_counts}")
    print(f"idle: {idle_counts}")
    if large_pokemon:
        print(f"\nlarge (target=64, need originalSpriteSize: 64 in pokemon-data.ts):")
        for n in large_pokemon:
            print(f"  {n}")
    return 0 if walk_counts["error"] == 0 and idle_counts["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
