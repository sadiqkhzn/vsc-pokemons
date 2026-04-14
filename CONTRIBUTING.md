# Contributing

How to build, test, and contribute to Flying Pokémon.

---

## Prerequisites

- [Node.js](https://nodejs.org/) v18+
- [VS Code](https://code.visualstudio.com/)
- npm (comes with Node.js)

---

## Setup

```bash
git clone <repo-url>
cd pokemon-extension
npm install
```

---

## Build

```bash
npm run compile
```

This runs 4 build steps:
1. `compile:panel` — Webpack bundles the webview code (`src/panel/`)
2. `compile:extension` — TypeScript compiles the extension host (`src/extension/`)
3. `compile:test` — TypeScript compiles tests
4. `compile:web` — Webpack bundles for web extension support

---

## Test Locally

1. Open the `pokemon-extension` folder in VS Code
2. Press `F5` → launches Extension Development Host
3. In the new window, open Command Palette (`Ctrl+Shift+P`)
4. Run "Start pokemon coding session"
5. Try "Spawn flying pokemon" (`Alt+Shift+F`)

---

## Watch Mode (auto-rebuild on changes)

```bash
npm run watch
```

This watches TypeScript files and recompiles on save. You still need to reload the Extension Development Host (`Ctrl+R` in the dev window) to see changes.

---

## Package as VSIX

```bash
npm install -g @vscode/vsce
vsce package
```

This creates `vsc-pokemons-1.0.0.vsix`. Share it or install via VS Code.

---

## Code Style

- **Linting**: `npm run lint` (ESLint)
- **Formatting**: `npm run format` (Prettier)
- **Fix all**: `npm run lint:fix`

Pre-commit hooks via Husky run lint + format automatically.

---

## Project Structure Quick Reference

| Path | What | When to Edit |
|------|------|-------------|
| `src/common/pokemon-data.ts` | All Pokémon data entries | Adding new Pokémon |
| `src/common/types.ts` | Interfaces and enums | Adding new config fields |
| `src/panel/states.ts` | State machine classes | Changing movement behavior |
| `src/panel/flying-pokemon.ts` | Flying sequence tree | Changing flying state transitions |
| `src/panel/pokemon-collection.ts` | Factory + collection | Changing how Pokémon are created |
| `src/panel/main.ts` | Webview rendering | Changing spawn animation/UI |
| `src/extension/extension.ts` | Commands + VS Code integration | Adding new commands |
| `media/pokemon.css` | All visual styling | Changing appearance |
| `package.json` | Extension manifest | Adding commands/settings/keybindings |

---

## Adding a New Pokémon (Checklist)

1. [ ] Get `default_idle_8fps.gif` and `default_walk_8fps.gif` sprites
2. [ ] Place them in `media/{gen}/{pokemonKey}/`
3. [ ] Add entry to `POKEMON_DATA` in `src/common/pokemon-data.ts`
4. [ ] If flying: add `isFlying: true`
5. [ ] If it has a fly GIF: add `hasFlySprite: true` and place `default_fly_8fps.gif`
6. [ ] Run `npm run compile` to verify
7. [ ] Test with `F5` → spawn the Pokémon

---

## Adding a New State/Behavior

1. Add to `States` enum in `src/panel/states.ts`
2. Create a new class implementing `IState`
3. Add to `resolveState()` switch
4. If above-ground: add to `isStateAboveGround()`
5. Add to relevant sequence trees in `pokemon.ts` or `flying-pokemon.ts`
6. Rebuild and test

---

## Known Limitations

- Only Gen 1-4 Pokémon included (Gen 5+ sprites need to be added manually)
- Only 11 of 69 flying Pokémon have actual fly sprites (rest use walk animation while airborne)
- Shiny sprites not available for all Gen 4 Pokémon
- No fly sprites for shiny variants (only default color flies)
- Friend-chasing between flying Pokémon doesn't account for altitude differences
