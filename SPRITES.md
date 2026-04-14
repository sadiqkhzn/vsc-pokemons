# Sprites Guide

Everything about where sprites come from, how they work, and how to add more.

---

## Current Sprite Sources

### 1. Walk & Idle Sprites (All Gen 1-4 Pokémon)

Every Pokémon has at minimum two animations:
- `default_idle_8fps.gif` — standing still
- `default_walk_8fps.gif` — walking animation

Some also have:
- `shiny_idle_8fps.gif` — shiny variant idle
- `shiny_walk_8fps.gif` — shiny variant walk
- `default_walk_left_8fps.gif` — dedicated left-facing walk (only ~40 Pokémon)

These are pixel art GIFs at 8 frames per second. Original sprite size is 32x32 for most, 64x64 for large Pokémon (Wailord, Lugia, Rayquaza, etc.).

**Source**: Pokémon game sprites. © The Pokémon Company / Nintendo / Game Freak. Used under fan project fair use.

### 2. Flying Sprites (FlapAround Animations)

11 flying-type Pokémon have a dedicated `default_fly_8fps.gif` with actual wing-flapping animation:

| Pokémon | Dex # | Frames | Source Animation |
|---------|-------|--------|-----------------|
| Butterfree | 12 | 24 | FlapAround |
| Pidgey | 16 | 18 | FlapAround |
| Pidgeotto | 17 | 18 | FlapAround |
| Pidgeot | 18 | 18 | FlapAround |
| Venomoth | 49 | 18 | FlapAround |
| Murkrow | 198 | 18 | FlapAround |
| Beautifly | 267 | 18 | FlapAround |
| Dustox | 269 | 18 | FlapAround |
| Flygon | 330 | 19 | FlapAround |
| Swellow | 277 | 18 | FlapAround |
| Taillow | 276 | 18 | FlapAround |

**Source**: [PMD SpriteCollab](https://sprites.pmdcollab.org/) ([GitHub repo](https://github.com/PMDCollab/SpriteCollab))
**License**: [CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) — free for non-commercial use, **must credit artists**
**Credits**: Full list at [PMD SpriteCollab Contributors](https://sprites.pmdcollab.org/#/Contributors)

---

## How PMD Sprites Were Converted

PMD SpriteCollab provides sprite sheets (PNG), not GIFs. The conversion process:

1. **Download**: `https://spriteserver.pmdcollab.org/assets/{dex_padded_4}/sprites.zip`
   - Example: Pidgey (#16) → `assets/0016/sprites.zip`

2. **Parse `AnimData.xml`**: Each zip contains an XML file defining:
   - Frame dimensions (FrameWidth, FrameHeight)
   - Number of frames (Durations array)
   - Animation types available (Walk, Idle, FlapAround, Sleep, Attack, etc.)

3. **Extract sprite sheet row**: The PNG sprite sheet has 8 rows (one per direction):
   - Row 0: Down
   - Row 1: Down-Right
   - **Row 2: Right** ← this is what we extract
   - Row 3: Up-Right
   - Row 4: Up
   - Row 5: Up-Left
   - Row 6: Left
   - Row 7: Down-Left

4. **Create animated GIF**: Individual frames from Row 2 are assembled into a looping GIF with Netscape extension for infinite loop.

The script `scripts/download-pmd-sprites.ps1` automates this entire process.

---

## How to Add More Pokémon (Gen 5+)

### Step 1: Get Sprites

**Option A — PMD SpriteCollab** (recommended for flying types):
```
https://spriteserver.pmdcollab.org/assets/{dex_padded_4}/sprites.zip
```
- Gen 5: #494-#649 → `0494` to `0649`
- Gen 6: #650-#721
- Gen 7: #722-#809
- Gen 8: #810-#905
- Gen 9: #906-#1025

Run the download script after adding new entries to the `$flyingPokemon` hashtable.

**Option B — Pokémon Showdown** (quick single-animation GIFs):
```
https://play.pokemonshowdown.com/sprites/gen5ani/{name}.gif
https://play.pokemonshowdown.com/sprites/gen5ani-shiny/{name}.gif
```
- Names are lowercase, no spaces: `pidgeot.gif`, `mr-mime.gif`
- These are single-pose animated GIFs (idle only)
- Good for quick additions but no walk/fly distinction

### Step 2: Add Sprite Files

Place GIFs in the correct folder:
```
media/gen5/{pokemonKey}/default_idle_8fps.gif
media/gen5/{pokemonKey}/default_walk_8fps.gif
media/gen5/{pokemonKey}/default_fly_8fps.gif    ← optional, for flyers
media/gen5/{pokemonKey}/shiny_idle_8fps.gif     ← optional
media/gen5/{pokemonKey}/shiny_walk_8fps.gif     ← optional
```

### Step 3: Add to POKEMON_DATA

In `src/common/pokemon-data.ts`, add a new entry:

```typescript
// Add PokemonGeneration.Gen5 to the enum in types.ts first
unfezant: {
  id: 521,
  name: 'Unfezant',
  generation: PokemonGeneration.Gen5,
  cry: 'Unfezant!',
  possibleColors: [PokemonColor.default, PokemonColor.shiny],
  isFlying: true,       // ← if it's a flying type
  hasFlySprite: true,   // ← only if you created a fly GIF
},
```

### Step 4: Add Generation Enum (if needed)

In `src/common/types.ts`:
```typescript
export enum PokemonGeneration {
  Gen1 = 1,
  Gen2 = 2,
  Gen3 = 3,
  Gen4 = 4,
  Gen5 = 5,  // ← add this
}
```

### Step 5: Rebuild

```bash
npm run compile
```

---

## PMD SpriteCollab — Available Animations

Not all Pokémon have all animations. Here's what PMD offers per Pokémon:

| Animation | Description | Commonly Available? |
|-----------|-------------|:---:|
| Walk | Walking movement | ✅ Almost all |
| Idle | Standing still | ✅ Almost all |
| Sleep | Sleeping pose | ✅ Most |
| Hurt | Taking damage | ✅ Most |
| Attack | Melee attack | ✅ Most |
| FlapAround | **Wing flapping** | ⚠️ Only flying types |
| Charge | Charging up | Some |
| Shoot | Projectile attack | Some |
| Strike | Quick hit | Some |
| Swing | Wide attack | Some |
| Hop | Jumping | Some |
| Rotate | Spinning | Some |
| Faint | Falling over | Some |

For this extension, we use: **Walk**, **Idle**, and **FlapAround**.

---

## Flying-Type Pokémon by Generation (for future reference)

When adding Gen 5+, these are the flying-type Pokémon to tag with `isFlying: true`:

### Gen 5 (#494-649)
Unfezant (#521), Swoobat (#528), Sigilyph (#561), Archeops (#567), Swanna (#581), Emolga (#587), Braviary (#628), Mandibuzz (#630), Tornadus (#641)

### Gen 6 (#650-721)
Talonflame (#663), Vivillon (#666), Hawlucha (#701), Noivern (#715), Yveltal (#717)

### Gen 7 (#722-809)
Toucannon (#733), Oricorio (#741), Minior (#774), Celesteela (#797), Naganadel (#804)

### Gen 8 (#810-905)
Corviknight (#823), Cramorant (#845), Frosmoth (#873)

### Gen 9 (#906-1025)
Kilowattrel (#940), Bombirdier (#962), Flamigo (#973), Iron Jugulis (#993), Flutter Mane (#987)

*(Not exhaustive — check Bulbapedia for the complete list per generation)*
