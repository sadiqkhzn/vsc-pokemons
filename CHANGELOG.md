# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-09

### Added
- **Gen 5 (Unova)** — all 156 Pokémon (#495-#649) with animated PMD walk + idle sprites (Snivy line through Genesect). Flying-type Pokémon flagged with `isFlying` for aerial behavior. Sprites sourced from PMDCollab/SpriteCollab (14 stragglers without PMD data fall back to PokeAPI Showdown mirror).
- **Gen 6 Kalos species** — all 72 Pokémon (#650-#721) from Chespin through Volcanion.
- **Real-height-based sprite sizing** — every Pokémon's `originalSpriteSize` derived from its actual Pokédex height (Bulbasaur 0.7m = 32px anchor, cube-root scaling, clamped [22, 58]). Wailord truly dwarfs Diglett, Snorlax visibly smaller than Dialga, etc.
- **Canvas normalization** — pokemon with 64x64 sprite canvases (Dialga, Lugia, etc.) automatically get 2x `originalSpriteSize` so their character-within-frame renders at the intended proportional size.

### Changed
- README, ARCHITECTURE, SPRITES, and CONTRIBUTING docs updated to reflect Gen 1-6 coverage.
- `package.json` description bumped to mention 790+ Pokémon.
- `package.json` keywords expanded (`gen5`, `gen6`, `kanto`, `unova`) and alphabetized.
- CHANGELOG.md added following Keep a Changelog format.
- Pull request template added under `.github/pull_request_template.md`.

### Fixed
- Extension no longer crashes on `pokemonView` load if workspace state references a removed Pokémon type (defensive fallback to Bulbasaur in `PokemonSpecification` constructor + skip-unknown filtering in `collectionFromMemento`).

### Removed
- Mega Evolutions and Primal Reversions — added in development, then removed prior to release because PMD SpriteCollab has no mega walk animations, forcing megas to appear as "sliding" idle sprites. Preserved on branch `wip/mega-evolutions` for future revisit if a proper sprite source is found.

## [1.1.0] - Earlier

- Enhanced flying Pokémon behavior with diagonal movement and viewport boundaries.
- 4 new diagonal flying states: `flyUpRight`, `flyUpLeft`, `flyDownRight`, `flyDownLeft`.

## [1.0.0]

Initial release. 565+ animated Pokémon from Gen 1-4.
