# Architecture

Technical reference for how the Flying Pokémon extension works. Read this if you want to modify behavior, add features, or understand the codebase.

---

## Tech Stack

- **Language**: TypeScript
- **Build**: Webpack (panel/webview) + tsc (extension host)
- **Runtime**: VS Code Extension API (Node.js side) + Webview (browser side)
- **Styling**: Plain CSS with keyframe animations
- **Sprites**: Pre-rendered GIF files (pixel art, 8fps)

---

## File Structure

```
pokemon-extension/
├── package.json              # Extension manifest, commands, settings, keybindings
├── webpack.config.js         # Bundles panel code for webview
├── tsconfig.extension.json   # TypeScript config for Node.js extension host
├── tsconfig.panel.json       # TypeScript config for browser webview
│
├── src/
│   ├── common/               # Shared between extension host and webview
│   │   ├── types.ts          # All enums, interfaces (PokemonConfig, PokemonSize, etc.)
│   │   ├── pokemon-data.ts   # POKEMON_DATA object (500+ entries), helper functions
│   │   ├── names.ts          # Random name generator (Bella, Charlie, Luna, etc.)
│   │   └── localize.ts       # i18n support (en-US, fr-FR, de-DE, ja-JP)
│   │
│   ├── extension/            # Runs in Node.js (VS Code host process)
│   │   └── extension.ts      # Entry point: commands, webview creation, state persistence
│   │
│   └── panel/                # Runs in browser (webview)
│       ├── main.ts           # Webview init, animation loop (100ms tick), spawn/despawn
│       ├── base-pokemon-type.ts  # Abstract base class: movement, sprite loading, state machine
│       ├── pokemon.ts        # Standard Pokemon class (walk + idle only)
│       ├── flying-pokemon.ts # FlyingPokemon class (hover, fly, glide + walk/idle)
│       ├── pokemon-collection.ts # Collection manager, friend detection, factory function
│       ├── states.ts         # All 20 state classes (IState interface, state machine)
│       └── sequences.ts      # Type definitions for state transition trees
│
├── media/
│   ├── pokemon.css           # All sprite styling, animations, flying effects
│   ├── backgrounds/          # Theme backgrounds (forest, castle, beach)
│   ├── gen1/                 # Gen 1 sprite GIFs (151 Pokémon)
│   ├── gen2/                 # Gen 2 sprite GIFs
│   ├── gen3/                 # Gen 3 sprite GIFs
│   ├── gen4/                 # Gen 4 sprite GIFs
│   └── icon/                 # Toolbar icons (add, remove, random)
│
├── scripts/
│   └── download-pmd-sprites.ps1  # Script to download PMD SpriteCollab sprites
│
└── l10n/                     # Localization bundles
```

---

## How the Extension Works (Overview)

```
┌─────────────────────────┐      messages      ┌──────────────────────┐
│   Extension Host        │ ◄──────────────► │   Webview (Browser)    │
│   (Node.js)             │                    │                      │
│                         │   spawn-pokemon    │   Canvas + DIVs      │
│   - Register commands   │ ──────────────►  │   - Sprite <img>      │
│   - Manage state        │                    │   - Collision <div>   │
│   - QuickPick UI        │   list-pokemon     │   - Speech bubble     │
│   - globalState persist │ ◄──────────────  │   - 100ms anim loop   │
└─────────────────────────┘                    └──────────────────────┘
```

The extension host registers commands and creates a webview. The webview renders Pokémon as absolutely-positioned `<img>` elements with GIF sprites. Every 100ms, each Pokémon's `nextFrame()` is called, which:

1. Checks the current state
2. Updates position (left/bottom)
3. Checks if state is complete → transitions to next state
4. Saves state to webview storage

---

## The State Machine

Every Pokémon has a **sequence tree** that defines which states can follow which:

### Standard Pokémon (Pokemon class)
```
sitIdle → walkLeft | walkRight
walkLeft → sitIdle | walkRight
walkRight → sitIdle | walkLeft
```

### Flying Pokémon (FlyingPokemon class)
```
hover → flyLeft | flyRight | glideDown
flyRight → hover | flyLeft | glideDown
flyLeft → hover | flyRight | glideDown
glideDown → walkLeft | walkRight | sitIdle
walkLeft → sitIdle | walkRight | flyRight | flyLeft
walkRight → sitIdle | walkLeft | flyLeft | flyRight
sitIdle → flyLeft | flyRight | walkLeft | walkRight
```

This means flying Pokémon naturally alternate between air and ground.

### State Classes (all in `states.ts`)

| State | Class | Sprite | Movement |
|-------|-------|--------|----------|
| sitIdle | SitIdleState | `idle` | None, holds for ~50 frames |
| walkRight | WalkRightState | `walk` | +speed horizontally per frame |
| walkLeft | WalkLeftState | `walk_left` or `walk` | -speed horizontally |
| runRight | RunRightState | `walk_fast` | 1.6x walk speed |
| runLeft | RunLeftState | `walk_fast` | 1.6x walk speed |
| **flyRight** | FlyRightState | `fly` or `walk` | +1.2x speed horiz + sin() vertical bob |
| **flyLeft** | FlyLeftState | `fly` or `walk` | -1.2x speed horiz + sin() vertical bob |
| **hover** | HoverState | `idle` | Gentle 5px bob at altitude |
| **glideDown** | GlideDownState | `walk` | -1.5px/frame descent + horizontal drift |
| swipe | SwipeState | `idle` | Mouse-over reaction |
| chase | ChaseState | `run` | Follows pokéball position |
| chaseFriend | ChaseFriendState | `run` | Follows friend Pokémon |
| climbWallLeft | ClimbWallLeftState | `wallclimb` | +1px vertical |
| wallHangLeft | WallHangLeftState | `wallgrab` | Static on wall |
| jumpDownLeft | JumpDownLeftState | `fall_from_grab` | -5px vertical |
| land | LandState | `land` | Brief pause after landing |

### Flying Sprite Selection

The `flyingSpriteLabel` property on `IPokemonType` determines what GIF is used during flight:
- `FlyingPokemon` with `hasFlySprite: true` → returns `'fly'` → loads `default_fly_8fps.gif`
- `FlyingPokemon` without fly sprite → returns `'walk'` → loads `default_walk_8fps.gif`
- Standard `Pokemon` → always returns `'walk'`

---

## Data Model

### PokemonConfig (`src/common/types.ts`)

```typescript
interface PokemonConfig {
  id: number;              // National Pokédex number
  name: string;            // Display name
  generation: PokemonGeneration;  // Gen1-Gen4
  cry: string;             // Speech bubble text
  possibleColors: PokemonColor[]; // [default] or [default, shiny]
  originalSpriteSize?: number;    // 32 (default) or 64 (for large Pokémon)
  extraSprites?: PokemonExtraSprite[];  // ['left_facing'] for some
  isFlying?: boolean;      // true for 69 flying-type Pokémon
  hasFlySprite?: boolean;  // true for 11 with FlapAround GIFs
}
```

### POKEMON_DATA (`src/common/pokemon-data.ts`)

A flat object with ~500 entries. Keys are lowercase snake_case: `bulbasaur`, `charizard`, `pikachu_female`, `shaymin_sky`, etc.

Helper functions:
- `getAllPokemon()` → all keys
- `getPokemonByGeneration(gen)` → keys for one generation
- `getFlyingPokemon()` → all 69 flying-type keys
- `isPokemonFlying(type)` → boolean check
- `hasPokemonFlySprite(type)` → boolean check
- `getRandomPokemonConfig()` → random [key, config] pair

---

## Sprite System

### File Naming Convention
```
media/{gen}/{pokemonKey}/{color}_{animation}_8fps.gif
```

Examples:
```
media/gen1/pikachu/default_idle_8fps.gif
media/gen1/pikachu/default_walk_8fps.gif
media/gen1/pikachu/shiny_idle_8fps.gif
media/gen1/pikachu/shiny_walk_8fps.gif
media/gen1/pidgey/default_fly_8fps.gif     ← PMD FlapAround sprite
```

### Sprite Loading (in `base-pokemon-type.ts`)
```typescript
setAnimation(face: string) {
  this.el.src = `${this.pokemonRoot}_${face}_8fps.gif`;
}
```

Where `pokemonRoot` = `{basePokemonUri}/{gen}/{pokemonKey}/{color}`.

So `spriteLabel = 'walk'` loads `default_walk_8fps.gif`, `spriteLabel = 'fly'` loads `default_fly_8fps.gif`.

---

## Spawn Factory

In `pokemon-collection.ts`, the `createPokemon()` function checks `isPokemonFlying(type)`:
- If true → creates `FlyingPokemon` instance
- If false → creates standard `Pokemon` instance

Both extend `BasePokemonType`, so the rest of the system (collection, state persistence, friend detection) works identically.

---

## CSS Additions for Flying

In `media/pokemon.css`:

```css
img.pokemon.flying {
  filter: drop-shadow(0px 20px 4px rgba(0, 0, 0, 0.15));
  transition: bottom 0.1s ease-out;
}
```

The `flying` class is added to the sprite `<img>` element in `main.ts` when `isPokemonFlying(type)` is true.

---

## Extension Commands

| Command ID | Description | Added by us? |
|------------|-------------|:---:|
| `vscode-pokemon.start` | Open/create panel | No |
| `vscode-pokemon.spawn-pokemon` | Pick & spawn | No |
| `vscode-pokemon.spawn-random-pokemon` | Random spawn | No |
| `vscode-pokemon.spawn-flying-pokemon` | Pick from flying types | **Yes** |
| `vscode-pokemon.delete-pokemon` | Remove selected | No |
| `vscode-pokemon.remove-all-pokemon` | Clear all | No |
| `vscode-pokemon.roll-call` | List all active | No |
| `vscode-pokemon.export-pokemon-list` | Export to JSON | No |
| `vscode-pokemon.import-pokemon-list` | Import from JSON | No |

---

## Session Persistence

Pokémon survive VS Code restarts via two mechanisms:

1. **Extension globalState**: Stores arrays of types, colors, and names (by index)
2. **Webview setState/getState**: Stores positions, current states, friend links

On restart, Pokémon are re-created from globalState and their positions/states recovered from webview state.
