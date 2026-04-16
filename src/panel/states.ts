import { PokemonColor, PokemonType } from '../common/types';

export interface IPokemonType {
  nextFrame(): void;

  // Special methods for actions
  canSwipe: boolean;
  canChase: boolean;
  swipe(): void;
  chase(ballState: BallState, canvas: HTMLCanvasElement): void;
  speed: number;
  isMoving: boolean;
  hello: string;

  // State API
  getState(): PokemonInstanceState;
  recoverState(state: PokemonInstanceState): void;
  recoverFriend(friend: IPokemonType): void;

  // Positioning
  bottom: number;
  left: number;
  positionBottom(bottom: number): void;
  positionLeft(left: number): void;
  width: number;
  floor: number;

  // Flying
  flyingSpriteLabel: string;

  // Friends API
  name: string;
  emoji: string;
  hasFriend: boolean;
  friend: IPokemonType | undefined;
  makeFriendsWith(friend: IPokemonType): boolean;
  isPlaying: boolean;

  showSpeechBubble(duration: number, friend: boolean): void;
}

export class PokemonInstanceState {
  currentStateEnum: States | undefined;
}

export class PokemonElementState {
  pokemonState: PokemonInstanceState | undefined;
  pokemonGeneration: string | undefined;
  originalSpriteSize: number | undefined;
  pokemonType: PokemonType | undefined;
  pokemonColor: PokemonColor | undefined;
  elLeft: string | undefined;
  elBottom: string | undefined;
  pokemonName: string | undefined;
  pokemonFriend: string | undefined;
}

export class PokemonPanelState {
  pokemonStates: Array<PokemonElementState> | undefined;
  pokemonCounter: number | undefined;
}

export enum HorizontalDirection {
  left,
  right,
  natural, // No change to current direction
}

export const enum States {
  sitIdle = 'sit-idle',
  walkRight = 'walk-right',
  walkLeft = 'walk-left',
  runRight = 'run-right',
  runLeft = 'run-left',
  lie = 'lie',
  wallHangLeft = 'wall-hang-left',
  climbWallLeft = 'climb-wall-left',
  jumpDownLeft = 'jump-down-left',
  land = 'land',
  swipe = 'swipe',
  idleWithBall = 'idle-with-ball',
  chase = 'chase',
  chaseFriend = 'chase-friend',
  standRight = 'stand-right',
  standLeft = 'stand-left',
  flyRight = 'fly-right',
  flyLeft = 'fly-left',
  flyUpRight = 'fly-up-right',
  flyUpLeft = 'fly-up-left',
  flyDownRight = 'fly-down-right',
  flyDownLeft = 'fly-down-left',
  hover = 'hover',
  glideDown = 'glide-down',
}

export enum FrameResult {
  stateContinue,
  stateComplete,
  // Special states
  stateCancel,
}

export class BallState {
  cx: number;
  cy: number;
  vx: number;
  vy: number;
  paused: boolean;

  constructor(cx: number, cy: number, vx: number, vy: number) {
    this.cx = cx;
    this.cy = cy;
    this.vx = vx;
    this.vy = vy;
    this.paused = false;
  }
}

export function isStateAboveGround(state: States): boolean {
  return (
    state === States.climbWallLeft ||
    state === States.jumpDownLeft ||
    state === States.land ||
    state === States.wallHangLeft ||
    state === States.flyRight ||
    state === States.flyLeft ||
    state === States.flyUpRight ||
    state === States.flyUpLeft ||
    state === States.flyDownRight ||
    state === States.flyDownLeft ||
    state === States.hover ||
    state === States.glideDown
  );
}

export function resolveState(state: string, pokemon: IPokemonType): IState {
  switch (state) {
    case States.sitIdle:
      return new SitIdleState(pokemon);
    case States.walkRight:
      return new WalkRightState(pokemon);
    case States.walkLeft:
      return new WalkLeftState(pokemon);
    case States.runRight:
      return new RunRightState(pokemon);
    case States.runLeft:
      return new RunLeftState(pokemon);
    case States.lie:
      return new LieState(pokemon);
    case States.wallHangLeft:
      return new WallHangLeftState(pokemon);
    case States.climbWallLeft:
      return new ClimbWallLeftState(pokemon);
    case States.jumpDownLeft:
      return new JumpDownLeftState(pokemon);
    case States.land:
      return new LandState(pokemon);
    case States.swipe:
      return new SwipeState(pokemon);
    case States.idleWithBall:
      return new IdleWithBallState(pokemon);
    case States.chaseFriend:
      return new ChaseFriendState(pokemon);
    case States.standRight:
      return new StandRightState(pokemon);
    case States.standLeft:
      return new StandLeftState(pokemon);
    case States.flyRight:
      return new FlyRightState(pokemon);
    case States.flyLeft:
      return new FlyLeftState(pokemon);
    case States.flyUpRight:
      return new FlyUpRightState(pokemon);
    case States.flyUpLeft:
      return new FlyUpLeftState(pokemon);
    case States.flyDownRight:
      return new FlyDownRightState(pokemon);
    case States.flyDownLeft:
      return new FlyDownLeftState(pokemon);
    case States.hover:
      return new HoverState(pokemon);
    case States.glideDown:
      return new GlideDownState(pokemon);
  }
  return new SitIdleState(pokemon);
}

export interface IState {
  label: string;
  spriteLabel: string;
  horizontalDirection: HorizontalDirection;
  pokemon: IPokemonType;
  nextFrame(): FrameResult;
}

class AbstractStaticState implements IState {
  label = States.sitIdle;
  idleCounter: number;
  spriteLabel = 'idle';
  holdTime = 50;
  pokemon: IPokemonType;

  horizontalDirection = HorizontalDirection.left;

  constructor(pokemon: IPokemonType) {
    this.idleCounter = 0;
    this.pokemon = pokemon;
  }

  nextFrame(): FrameResult {
    this.idleCounter++;
    if (this.idleCounter > this.holdTime) {
      return FrameResult.stateComplete;
    }
    return FrameResult.stateContinue;
  }
}

export class SitIdleState extends AbstractStaticState {
  label = States.sitIdle;
  spriteLabel = 'idle';
  horizontalDirection = HorizontalDirection.right;
  holdTime = 50;
}

export class LieState extends AbstractStaticState {
  label = States.lie;
  spriteLabel = 'lie';
  horizontalDirection = HorizontalDirection.right;
  holdTime = 50;
}

export class WallHangLeftState extends AbstractStaticState {
  label = States.wallHangLeft;
  spriteLabel = 'wallgrab';
  horizontalDirection = HorizontalDirection.left;
  holdTime = 50;
}

export class LandState extends AbstractStaticState {
  label = States.land;
  spriteLabel = 'land';
  horizontalDirection = HorizontalDirection.left;
  holdTime = 10;
}

export class SwipeState extends AbstractStaticState {
  label = States.swipe;
  spriteLabel = 'idle'; // use base idle sprite
  horizontalDirection = HorizontalDirection.natural;
  holdTime = 15;
}

export class IdleWithBallState extends AbstractStaticState {
  label = States.idleWithBall;
  spriteLabel = 'with_ball';
  horizontalDirection = HorizontalDirection.left;
  holdTime = 30;
}

export class WalkRightState implements IState {
  label = States.walkRight;
  pokemon: IPokemonType;
  spriteLabel = 'walk';
  horizontalDirection = HorizontalDirection.right;
  leftBoundary: number;
  speedMultiplier = 1;
  idleCounter: number;
  holdTime = 60;

  constructor(pokemon: IPokemonType) {
    this.leftBoundary = Math.floor(window.innerWidth * 0.95);
    this.pokemon = pokemon;
    this.idleCounter = 0;
  }

  nextFrame(): FrameResult {
    this.idleCounter++;
    this.pokemon.positionLeft(
      this.pokemon.left + this.pokemon.speed * this.speedMultiplier,
    );

    // Random chance to stop in the middle
    if (this.pokemon.isMoving && Math.random() < 0.01) {
      return FrameResult.stateComplete;
    }

    if (
      this.pokemon.isMoving &&
      this.pokemon.left >= this.leftBoundary - this.pokemon.width
    ) {
      return FrameResult.stateComplete;
    } else if (!this.pokemon.isMoving && this.idleCounter > this.holdTime) {
      return FrameResult.stateComplete;
    }
    return FrameResult.stateContinue;
  }
}

export class WalkLeftState implements IState {
  label = States.walkLeft;
  spriteLabel = 'walk_left';
  horizontalDirection = HorizontalDirection.left;
  pokemon: IPokemonType;
  speedMultiplier = 1;
  idleCounter: number;
  holdTime = 60;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
    this.idleCounter = 0;
  }

  nextFrame(): FrameResult {
    this.idleCounter++;
    this.pokemon.positionLeft(
      this.pokemon.left - this.pokemon.speed * this.speedMultiplier,
    );

    // Random chance to stop in the middle
    if (this.pokemon.isMoving && Math.random() < 0.01) {
      return FrameResult.stateComplete;
    }

    if (this.pokemon.isMoving && this.pokemon.left <= 0) {
      return FrameResult.stateComplete;
    } else if (!this.pokemon.isMoving && this.idleCounter > this.holdTime) {
      return FrameResult.stateComplete;
    }
    return FrameResult.stateContinue;
  }
}

export class RunRightState extends WalkRightState {
  label = States.runRight;
  spriteLabel = 'walk_fast';
  speedMultiplier = 1.6;
  holdTime = 130;
}

export class RunLeftState extends WalkLeftState {
  label = States.runLeft;
  spriteLabel = 'walk_fast';
  speedMultiplier = 1.6;
  holdTime = 130;
}

export class ChaseState implements IState {
  label = States.chase;
  spriteLabel = 'run';
  horizontalDirection = HorizontalDirection.left;
  ballState: BallState;
  canvas: HTMLCanvasElement;
  pokemon: IPokemonType;

  constructor(
    pokemon: IPokemonType,
    ballState: BallState,
    canvas: HTMLCanvasElement,
  ) {
    this.pokemon = pokemon;
    this.ballState = ballState;
    this.canvas = canvas;
  }

  nextFrame(): FrameResult {
    if (this.ballState.paused) {
      return FrameResult.stateCancel; // Ball is already caught
    }
    if (this.pokemon.left > this.ballState.cx) {
      this.horizontalDirection = HorizontalDirection.left;
      this.pokemon.positionLeft(this.pokemon.left - this.pokemon.speed);
    } else {
      this.horizontalDirection = HorizontalDirection.right;
      this.pokemon.positionLeft(this.pokemon.left + this.pokemon.speed);
    }

    if (
      this.canvas.height - this.ballState.cy <
        this.pokemon.width + this.pokemon.floor &&
      this.ballState.cx < this.pokemon.left &&
      this.pokemon.left < this.ballState.cx + 15
    ) {
      // hide ball
      this.canvas.style.display = 'none';
      this.ballState.paused = true;
      return FrameResult.stateComplete;
    }
    return FrameResult.stateContinue;
  }
}

export class ChaseFriendState implements IState {
  label = States.chaseFriend;
  spriteLabel = 'run';
  horizontalDirection = HorizontalDirection.left;
  pokemon: IPokemonType;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
  }

  nextFrame(): FrameResult {
    if (!this.pokemon.hasFriend || !this.pokemon.friend?.isPlaying) {
      return FrameResult.stateCancel; // Friend is no longer playing.
    }
    // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
    if (this.pokemon.left > this.pokemon.friend!.left) {
      this.horizontalDirection = HorizontalDirection.left;
      this.pokemon.positionLeft(this.pokemon.left - this.pokemon.speed);
    } else {
      this.horizontalDirection = HorizontalDirection.right;
      this.pokemon.positionLeft(this.pokemon.left + this.pokemon.speed);
    }

    return FrameResult.stateContinue;
  }
}

export class ClimbWallLeftState implements IState {
  label = States.climbWallLeft;
  spriteLabel = 'wallclimb';
  horizontalDirection = HorizontalDirection.left;
  pokemon: IPokemonType;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
  }

  nextFrame(): FrameResult {
    this.pokemon.positionBottom(this.pokemon.bottom + 1);
    if (this.pokemon.bottom >= 100) {
      return FrameResult.stateComplete;
    }
    return FrameResult.stateContinue;
  }
}

export class JumpDownLeftState implements IState {
  label = States.jumpDownLeft;
  spriteLabel = 'fall_from_grab';
  horizontalDirection = HorizontalDirection.right;
  pokemon: IPokemonType;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
  }

  nextFrame(): FrameResult {
    this.pokemon.positionBottom(this.pokemon.bottom - 5);
    if (this.pokemon.bottom <= this.pokemon.floor) {
      this.pokemon.positionBottom(this.pokemon.floor);
      return FrameResult.stateComplete;
    }
    return FrameResult.stateContinue;
  }
}

export class StandRightState extends AbstractStaticState {
  label = States.standRight;
  spriteLabel = 'stand';
  horizontalDirection = HorizontalDirection.right;
  holdTime = 60;
}

export class StandLeftState extends AbstractStaticState {
  label = States.standRight;
  spriteLabel = 'stand';
  horizontalDirection = HorizontalDirection.left;
  holdTime = 60;
}

export class FlyRightState implements IState {
  label = States.flyRight;
  spriteLabel: string;
  horizontalDirection = HorizontalDirection.right;
  pokemon: IPokemonType;
  private frameCount = 0;
  private flyHeight: number;
  private amplitude = 15;
  private frequency = 0.08;
  private minHeight: number;
  private maxHeight: number;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
    this.spriteLabel = pokemon.flyingSpriteLabel;
    // Enhanced height management for viewport bounds
    this.minHeight = pokemon.floor + 50;
    this.maxHeight = window.innerHeight * 0.8;
    this.flyHeight =
      pokemon.bottom > pokemon.floor + 20
        ? Math.min(Math.max(pokemon.bottom, this.minHeight), this.maxHeight)
        : this.minHeight + Math.random() * (this.maxHeight - this.minHeight) * 0.6;
    this.pokemon.positionBottom(this.flyHeight);
  }

  nextFrame(): FrameResult {
    this.frameCount++;

    // Calculate next horizontal position
    const nextLeft = this.pokemon.left + this.pokemon.speed * 1.1;
    
    // Enhanced vertical movement with bounds checking
    const bob = Math.sin(this.frameCount * this.frequency) * this.amplitude;
    const targetHeight = this.flyHeight + (this.frameCount * 0.1) + bob;
    const clampedHeight = Math.min(Math.max(targetHeight, this.minHeight), this.maxHeight);

    // Clamp horizontal movement within viewport
    const maxLeft = window.innerWidth - this.pokemon.width - 10;
    const clampedLeft = Math.min(Math.max(nextLeft, 10), maxLeft);

    // Apply clamped movement
    this.pokemon.positionLeft(clampedLeft);
    this.pokemon.positionBottom(clampedHeight);

    // Random chance to change state after minimum flight time
    if (this.frameCount > 35 && Math.random() < 0.013) {
      return FrameResult.stateComplete;
    }

    // Complete if hit boundary
    if (clampedLeft !== nextLeft) {
      return FrameResult.stateComplete;
    }

    return FrameResult.stateContinue;
  }
}

export class FlyLeftState implements IState {
  label = States.flyLeft;
  spriteLabel: string;
  horizontalDirection = HorizontalDirection.left;
  pokemon: IPokemonType;
  private frameCount = 0;
  private flyHeight: number;
  private amplitude = 15;
  private frequency = 0.08;
  private minHeight: number;
  private maxHeight: number;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
    this.spriteLabel = pokemon.flyingSpriteLabel;
    // Enhanced height management for viewport bounds
    this.minHeight = pokemon.floor + 50;
    this.maxHeight = window.innerHeight * 0.8;
    this.flyHeight =
      pokemon.bottom > pokemon.floor + 20
        ? Math.min(Math.max(pokemon.bottom, this.minHeight), this.maxHeight)
        : this.minHeight + Math.random() * (this.maxHeight - this.minHeight) * 0.6;
    this.pokemon.positionBottom(this.flyHeight);
  }

  nextFrame(): FrameResult {
    this.frameCount++;

    // Calculate next horizontal position
    const nextLeft = this.pokemon.left - this.pokemon.speed * 1.1;
    
    // Enhanced vertical movement with bounds checking
    const bob = Math.sin(this.frameCount * this.frequency) * this.amplitude;
    const targetHeight = this.flyHeight + (this.frameCount * 0.1) + bob;
    const clampedHeight = Math.min(Math.max(targetHeight, this.minHeight), this.maxHeight);

    // Clamp horizontal movement within viewport
    const maxLeft = window.innerWidth - this.pokemon.width - 10;
    const clampedLeft = Math.min(Math.max(nextLeft, 10), maxLeft);

    // Apply clamped movement
    this.pokemon.positionLeft(clampedLeft);
    this.pokemon.positionBottom(clampedHeight);

    // Random chance to change state after minimum flight time
    if (this.frameCount > 35 && Math.random() < 0.013) {
      return FrameResult.stateComplete;
    }

    // Complete if hit boundary
    if (clampedLeft !== nextLeft) {
      return FrameResult.stateComplete;
    }

    return FrameResult.stateContinue;
  }
}

export class HoverState implements IState {
  label = States.hover;
  spriteLabel = 'idle';
  horizontalDirection = HorizontalDirection.right;
  pokemon: IPokemonType;
  private frameCount = 0;
  private holdTime: number;
  private flyHeight: number;
  private amplitude = 5;
  private frequency = 0.06;
  private minHeight: number;
  private maxHeight: number;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
    this.holdTime = 40 + Math.floor(Math.random() * 40);
    // Enhanced height management for viewport bounds
    this.minHeight = pokemon.floor + 50;
    this.maxHeight = window.innerHeight * 0.8;
    this.flyHeight =
      pokemon.bottom > pokemon.floor + 20
        ? Math.min(Math.max(pokemon.bottom, this.minHeight), this.maxHeight)
        : this.minHeight + Math.random() * (this.maxHeight - this.minHeight) * 0.6;
    this.pokemon.positionBottom(this.flyHeight);
  }

  nextFrame(): FrameResult {
    this.frameCount++;

    // Enhanced hovering with viewport bounds checking
    const bob = Math.sin(this.frameCount * this.frequency) * this.amplitude;
    const targetHeight = this.flyHeight + bob;
    const clampedHeight = Math.min(Math.max(targetHeight, this.minHeight), this.maxHeight);
    
    // Also ensure horizontal position stays within bounds (in case Pokemon drifted)
    const maxLeft = window.innerWidth - this.pokemon.width - 10;
    const clampedLeft = Math.min(Math.max(this.pokemon.left, 10), maxLeft);
    
    this.pokemon.positionLeft(clampedLeft);
    this.pokemon.positionBottom(clampedHeight);

    if (this.frameCount > this.holdTime) {
      return FrameResult.stateComplete;
    }
    return FrameResult.stateContinue;
  }
}

export class GlideDownState implements IState {
  label = States.glideDown;
  spriteLabel = 'walk';
  horizontalDirection = HorizontalDirection.right;
  pokemon: IPokemonType;
  private frameCount = 0;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
    // Randomly pick horizontal direction
    if (Math.random() > 0.5) {
      this.horizontalDirection = HorizontalDirection.left;
    }
  }

  nextFrame(): FrameResult {
    this.frameCount++;

    // Gradual descent
    this.pokemon.positionBottom(this.pokemon.bottom - 1.5);

    // Slight horizontal drift
    const drift =
      this.horizontalDirection === HorizontalDirection.right
        ? this.pokemon.speed * 0.5
        : -this.pokemon.speed * 0.5;
    this.pokemon.positionLeft(this.pokemon.left + drift);

    // Landed
    if (this.pokemon.bottom <= this.pokemon.floor) {
      this.pokemon.positionBottom(this.pokemon.floor);
      return FrameResult.stateComplete;
    }

    return FrameResult.stateContinue;
  }
}

export class FlyUpRightState implements IState {
  label = States.flyUpRight;
  spriteLabel: string;
  horizontalDirection = HorizontalDirection.right;
  pokemon: IPokemonType;
  private frameCount = 0;
  private maxHeight: number;
  private amplitude = 10;
  private frequency = 0.06;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
    this.spriteLabel = pokemon.flyingSpriteLabel;
    // Set maximum height to 80% of viewport to keep within bounds
    this.maxHeight = window.innerHeight * 0.8;
  }

  nextFrame(): FrameResult {
    this.frameCount++;

    // Calculate next position but don't move yet
    const nextLeft = this.pokemon.left + this.pokemon.speed * 0.8;
    const nextBottom = this.pokemon.bottom + this.pokemon.speed * 0.6;
    
    // Add flight wobble
    const wobble = Math.sin(this.frameCount * this.frequency) * this.amplitude;
    const wobbledBottom = nextBottom + wobble * 0.1;

    // Check boundaries before moving
    const maxLeft = window.innerWidth - this.pokemon.width - 10; // 10px margin
    const clampedLeft = Math.min(Math.max(nextLeft, 10), maxLeft);
    const clampedBottom = Math.min(Math.max(wobbledBottom, this.pokemon.floor + 50), this.maxHeight);

    // Apply clamped movement
    this.pokemon.positionLeft(clampedLeft);
    this.pokemon.positionBottom(clampedBottom);

    // Random chance to change direction after minimum flight time
    if (this.frameCount > 40 && Math.random() < 0.012) {
      return FrameResult.stateComplete;
    }

    // Complete state if we hit boundaries
    if (clampedLeft !== nextLeft || clampedBottom !== wobbledBottom) {
      return FrameResult.stateComplete;
    }

    return FrameResult.stateContinue;
  }
}

export class FlyUpLeftState implements IState {
  label = States.flyUpLeft;
  spriteLabel: string;
  horizontalDirection = HorizontalDirection.left;
  pokemon: IPokemonType;
  private frameCount = 0;
  private maxHeight: number;
  private amplitude = 10;
  private frequency = 0.06;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
    this.spriteLabel = pokemon.flyingSpriteLabel;
    this.maxHeight = window.innerHeight * 0.8;
  }

  nextFrame(): FrameResult {
    this.frameCount++;

    // Calculate next position but don't move yet
    const nextLeft = this.pokemon.left - this.pokemon.speed * 0.8;
    const nextBottom = this.pokemon.bottom + this.pokemon.speed * 0.6;
    
    // Add flight wobble
    const wobble = Math.sin(this.frameCount * this.frequency) * this.amplitude;
    const wobbledBottom = nextBottom + wobble * 0.1;

    // Check boundaries before moving
    const maxLeft = window.innerWidth - this.pokemon.width - 10;
    const clampedLeft = Math.min(Math.max(nextLeft, 10), maxLeft);
    const clampedBottom = Math.min(Math.max(wobbledBottom, this.pokemon.floor + 50), this.maxHeight);

    // Apply clamped movement
    this.pokemon.positionLeft(clampedLeft);
    this.pokemon.positionBottom(clampedBottom);

    // Random chance to change direction
    if (this.frameCount > 40 && Math.random() < 0.012) {
      return FrameResult.stateComplete;
    }

    // Complete state if we hit boundaries
    if (clampedLeft !== nextLeft || clampedBottom !== wobbledBottom) {
      return FrameResult.stateComplete;
    }

    return FrameResult.stateContinue;
  }
}

export class FlyDownRightState implements IState {
  label = States.flyDownRight;
  spriteLabel: string;
  horizontalDirection = HorizontalDirection.right;
  pokemon: IPokemonType;
  private frameCount = 0;
  private minHeight: number;
  private amplitude = 8;
  private frequency = 0.05;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
    this.spriteLabel = pokemon.flyingSpriteLabel;
    // Set minimum flying height above ground Pokemon
    this.minHeight = pokemon.floor + 50;
  }

  nextFrame(): FrameResult {
    this.frameCount++;

    // Calculate next position but don't move yet
    const wobble = Math.sin(this.frameCount * this.frequency) * this.amplitude;
    const nextLeft = this.pokemon.left + this.pokemon.speed * 0.8 + wobble * 0.1;
    const nextBottom = this.pokemon.bottom - this.pokemon.speed * 0.4;

    // Check boundaries before moving
    const maxLeft = window.innerWidth - this.pokemon.width - 10;
    const clampedLeft = Math.min(Math.max(nextLeft, 10), maxLeft);
    const clampedBottom = Math.min(Math.max(nextBottom, this.minHeight), window.innerHeight * 0.8);

    // Apply clamped movement
    this.pokemon.positionLeft(clampedLeft);
    this.pokemon.positionBottom(clampedBottom);

    // Random chance to change direction
    if (this.frameCount > 40 && Math.random() < 0.012) {
      return FrameResult.stateComplete;
    }

    // Complete state if we hit boundaries
    if (clampedLeft !== nextLeft || clampedBottom !== nextBottom) {
      return FrameResult.stateComplete;
    }

    return FrameResult.stateContinue;
  }
}

export class FlyDownLeftState implements IState {
  label = States.flyDownLeft;
  spriteLabel: string;
  horizontalDirection = HorizontalDirection.left;
  pokemon: IPokemonType;
  private frameCount = 0;
  private minHeight: number;
  private amplitude = 8;
  private frequency = 0.05;

  constructor(pokemon: IPokemonType) {
    this.pokemon = pokemon;
    this.spriteLabel = pokemon.flyingSpriteLabel;
    this.minHeight = pokemon.floor + 50;
  }

  nextFrame(): FrameResult {
    this.frameCount++;

    // Calculate next position but don't move yet
    const wobble = Math.sin(this.frameCount * this.frequency) * this.amplitude;
    const nextLeft = this.pokemon.left - this.pokemon.speed * 0.8 + wobble * 0.1;
    const nextBottom = this.pokemon.bottom - this.pokemon.speed * 0.4;

    // Check boundaries before moving
    const maxLeft = window.innerWidth - this.pokemon.width - 10;
    const clampedLeft = Math.min(Math.max(nextLeft, 10), maxLeft);
    const clampedBottom = Math.min(Math.max(nextBottom, this.minHeight), window.innerHeight * 0.8);

    // Apply clamped movement
    this.pokemon.positionLeft(clampedLeft);
    this.pokemon.positionBottom(clampedBottom);

    // Random chance to change direction
    if (this.frameCount > 40 && Math.random() < 0.012) {
      return FrameResult.stateComplete;
    }

    // Complete state if we hit boundaries
    if (clampedLeft !== nextLeft || clampedBottom !== nextBottom) {
      return FrameResult.stateComplete;
    }

    return FrameResult.stateContinue;
  }
}
