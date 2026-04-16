import { POKEMON_DATA } from '../common/pokemon-data';
import { PokemonSize } from '../common/types';
import { BasePokemonType } from './base-pokemon-type';
import { States } from './states';

export class FlyingPokemon extends BasePokemonType {
  constructor(
    pokemonType: string,
    spriteElement: HTMLImageElement,
    collisionElement: HTMLDivElement,
    speechElement: HTMLImageElement,
    size: PokemonSize,
    left: number,
    bottom: number,
    pokemonRoot: string,
    floor: number,
    name: string,
    speed: number,
    generation: string,
    originalSpriteSize: number,
  ) {
    super(
      spriteElement,
      collisionElement,
      speechElement,
      size,
      left,
      bottom,
      pokemonRoot,
      floor,
      name,
      speed,
      generation,
      originalSpriteSize,
    );

    this.label = pokemonType;
  }

  sequence = {
    startingState: States.hover,
    sequenceStates: [
      {
        state: States.hover,
        possibleNextStates: [
          States.flyLeft, 
          States.flyRight, 
          States.flyUpLeft, 
          States.flyUpRight,
          States.flyDownLeft,
          States.flyDownRight,
          States.glideDown
        ],
      },
      {
        state: States.flyRight,
        possibleNextStates: [
          States.hover, 
          States.flyLeft, 
          States.flyUpRight,
          States.flyDownRight,
          States.glideDown
        ],
      },
      {
        state: States.flyLeft,
        possibleNextStates: [
          States.hover, 
          States.flyRight, 
          States.flyUpLeft,
          States.flyDownLeft,
          States.glideDown
        ],
      },
      {
        state: States.flyUpRight,
        possibleNextStates: [
          States.hover,
          States.flyRight,
          States.flyUpLeft,
          States.flyDownRight,
          States.glideDown
        ],
      },
      {
        state: States.flyUpLeft,
        possibleNextStates: [
          States.hover,
          States.flyLeft,
          States.flyUpRight,
          States.flyDownLeft,
          States.glideDown
        ],
      },
      {
        state: States.flyDownRight,
        possibleNextStates: [
          States.hover,
          States.flyRight,
          States.flyUpRight,
          States.flyDownLeft,
          States.glideDown
        ],
      },
      {
        state: States.flyDownLeft,
        possibleNextStates: [
          States.hover,
          States.flyLeft,
          States.flyUpLeft,
          States.flyDownRight,
          States.glideDown
        ],
      },
      {
        state: States.glideDown,
        possibleNextStates: [States.walkLeft, States.walkRight, States.sitIdle],
      },
      {
        state: States.walkLeft,
        possibleNextStates: [
          States.sitIdle,
          States.walkRight,
          States.flyRight,
          States.flyLeft,
          States.hover,
        ],
      },
      {
        state: States.walkRight,
        possibleNextStates: [
          States.sitIdle,
          States.walkLeft,
          States.flyLeft,
          States.flyRight,
          States.hover,
        ],
      },
      {
        state: States.sitIdle,
        possibleNextStates: [
          States.flyLeft,
          States.flyRight,
          States.walkLeft,
          States.walkRight,
          States.hover,
        ],
      },
      {
        state: States.swipe,
        possibleNextStates: [States.hover],
      },
      {
        state: States.idleWithBall,
        possibleNextStates: [
          States.hover, 
          States.flyLeft, 
          States.flyRight,
          States.flyUpLeft,
          States.flyUpRight,
        ],
      },
    ],
  };

  get generation() {
    return (
      POKEMON_DATA[this.label]?.generation ?? POKEMON_DATA.bulbasaur.generation
    );
  }

  get pokedexNumber(): number {
    return POKEMON_DATA[this.label]?.id ?? 0;
  }

  get flyingSpriteLabel(): string {
    return 'walk';
  }
}
