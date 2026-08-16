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

MEDIA_DIR = Path(__file__).resolve().parent.parent / "media" / "gen5"
PMD_BASE = "https://raw.githubusercontent.com/PMDCollab/SpriteCollab/master/sprite"

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


def _build_one(dex: int, name: str, anim_name: str, out_filename: str, *, dry_run: bool) -> str:
    """Extract one animation ("Walk" or "Idle") and save as a GIF.
    Returns "ok" / "no-anim-data" / "no-walk" / "no-png" / "error"."""
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

    if dry_run:
        return "ok"

    # PMD durations are game ticks (~30fps). Convert to ms, clamp so nothing
    # lingers absurdly and nothing plays too fast to see.
    frame_ms: list[int] = []
    for i in range(n_frames):
        d = durations[i % len(durations)] if durations else 4
        frame_ms.append(max(60, min(int(d * 33), 220)))

    out_path = MEDIA_DIR / name / out_filename
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
    return "ok"


def build_walk_gif(dex: int, name: str, *, dry_run: bool) -> str:
    return _build_one(dex, name, "Walk", "default_walk_8fps.gif", dry_run=dry_run)


def build_idle_gif(dex: int, name: str, *, dry_run: bool) -> str:
    return _build_one(dex, name, "Idle", "default_idle_8fps.gif", dry_run=dry_run)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="don't write files, just probe PMDCollab")
    parser.add_argument("--only", type=str, default=None, help="comma-separated dex ids to run (e.g. 495,527,635)")
    args = parser.parse_args()

    targets = GEN5
    if args.only:
        wanted = {int(x) for x in args.only.split(",")}
        targets = {k: v for k, v in GEN5.items() if k in wanted}

    walk_counts = {"ok": 0, "no-anim-data": 0, "no-walk": 0, "no-png": 0, "error": 0}
    idle_counts = {"ok": 0, "no-anim-data": 0, "no-walk": 0, "no-png": 0, "error": 0}
    for dex, name in sorted(targets.items()):
        for label, builder, counts in (
            ("walk", build_walk_gif, walk_counts),
            ("idle", build_idle_gif, idle_counts),
        ):
            try:
                status = builder(dex, name, dry_run=args.dry_run)
            except Exception as e:  # pragma: no cover
                status = "error"
                print(f"  FAIL {name:16s} #{dex} {label}  {e}", file=sys.stderr)
            counts[status] += 1
            marker = {
                "ok": "OK  ",
                "no-anim-data": "MISS",
                "no-walk": "SKIP",
                "no-png": "SKIP",
                "error": "FAIL",
            }[status]
            print(f"  {marker} {name:16s} #{dex}  {label}  ({status})")

    print()
    print(f"walk: {walk_counts}")
    print(f"idle: {idle_counts}")
    return 0 if walk_counts["error"] == 0 and idle_counts["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
