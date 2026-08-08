# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing yet.

## [1.1.1] - 2026-08

### Added
- **Gen 5 (Unova)** — all 156 Pokémon (#495-#649) with animated default and shiny sprites (Snivy line through Genesect). Flying-type Pokémon flagged with `isFlying` for aerial behavior.
- **Gen 6 introduced** — `PokemonGeneration.Gen6` enum value and `gen6` locale key.
- **50 Mega Evolutions & Primal Reversions** — 15 Kanto, 6 Johto, 20 Hoenn, 5 Sinnoh, 2 later-era (Audino, Diancie), 2 Primals (Kyogre, Groudon). Aerial megas flagged `isFlying`.
- **New command:** `Spawn a Random Mega Evolution` (`vscode-pokemon.spawn-random-mega`) that picks a random Gen 6 mega/primal.
- **`getRandomMegaConfig()` helper** in `pokemon-data.ts` for filtering to Gen 6 forms.

### Changed
- README, ARCHITECTURE, SPRITES, and CONTRIBUTING docs updated to reflect Gen 1-6 coverage.
- `package.json` description bumped to mention 770+ Pokémon.
- `package.json` keywords expanded (`gen5`, `gen6`, `mega evolution`, `kanto`, `unova`) and alphabetized.

## [1.1.0] - Earlier

- Enhanced flying Pokémon behavior with diagonal movement and viewport boundaries.
- 4 new diagonal flying states: `flyUpRight`, `flyUpLeft`, `flyDownRight`, `flyDownLeft`.

## [1.0.0]

Initial release. 565+ animated Pokémon from Gen 1-4.
