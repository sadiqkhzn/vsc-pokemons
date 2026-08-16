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
    """For each frame, tight-crop to its own non-transparent content and paste
    into a (target_w, target_h) canvas horizontally centered and bottom-aligned.
    This matches Gen 1-4 convention where the character's lowest visible pixel
    sits at the frame bottom (so bottom-anchored CSS positioning puts feet at
    the floor line, not hovering above it)."""
    out = []
    for f in frames:
        bbox = f.getbbox()
        if bbox is None:
            # empty frame — just make a transparent canvas
            out.append(Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0)))
            continue
        content = f.crop(bbox)
        canvas = Image.new("RGBA", (target_w, target_h), (0, 0, 0, 0))
        x = (target_w - content.width) // 2
        y = target_h - content.height  # bottom-align
        canvas.paste(content, (x, y), content)
        out.append(canvas)
    return out


def build_pokemon(dex: int, name: str, *, dry_run: bool) -> tuple[str, str]:
    """Build both idle and walk. For each pokemon, compute a shared canvas size
    from the max content width and height across all idle+walk frames, then
    place every frame's content bottom-center anchored. This gives:
      - identical dims across idle and walk (no floating jump between states)
      - character's feet at frame bottom (matches Gen 1-4 convention)
      - horizontal center consistent (no sliding-sideways)"""
    idle_result = _fetch_frames(dex, "Idle")
    walk_result = _fetch_frames(dex, "Walk")

    idle_ok = isinstance(idle_result, tuple)
    walk_ok = isinstance(walk_result, tuple)
    idle_status = "ok" if idle_ok else idle_result
    walk_status = "ok" if walk_ok else walk_result

    if not (idle_ok or walk_ok):
        return walk_status, idle_status

    all_frames: list[Image.Image] = []
    if idle_ok:
        all_frames.extend(idle_result[0])
    if walk_ok:
        all_frames.extend(walk_result[0])

    # Compute max content dims across all per-frame bounding boxes.
    max_w = 0
    max_h = 0
    for f in all_frames:
        bbox = f.getbbox()
        if bbox is None:
            continue
        max_w = max(max_w, bbox[2] - bbox[0])
        max_h = max(max_h, bbox[3] - bbox[1])
    if max_w == 0 or max_h == 0:
        return walk_status, idle_status

    if dry_run:
        return walk_status, idle_status

    if idle_ok:
        idle_frames, idle_ms = idle_result
        _save_gif(
            _per_frame_align(idle_frames, max_w, max_h),
            idle_ms,
            MEDIA_DIR / name / "default_idle_8fps.gif",
        )
    if walk_ok:
        walk_frames, walk_ms = walk_result
        _save_gif(
            _per_frame_align(walk_frames, max_w, max_h),
            walk_ms,
            MEDIA_DIR / name / "default_walk_8fps.gif",
        )

    return walk_status, idle_status


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
        try:
            walk_status, idle_status = build_pokemon(dex, name, dry_run=args.dry_run)
        except Exception as e:  # pragma: no cover
            walk_status = idle_status = "error"
            print(f"  FAIL {name:16s} #{dex}  {e}", file=sys.stderr)
        walk_counts[walk_status] += 1
        idle_counts[idle_status] += 1
        marker_map = {
            "ok": "OK  ",
            "no-anim-data": "MISS",
            "no-walk": "SKIP",
            "no-png": "SKIP",
            "error": "FAIL",
        }
        print(
            f"  walk={marker_map[walk_status]} idle={marker_map[idle_status]} "
            f"{name:16s} #{dex}"
        )

    print()
    print(f"walk: {walk_counts}")
    print(f"idle: {idle_counts}")
    return 0 if walk_counts["error"] == 0 and idle_counts["error"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
