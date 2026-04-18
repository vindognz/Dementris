# Dementris Refactor Notes

## Goal

Rebuild `Dementris` from the ground up on a new branch.

The target is:
- as close to the original game as possible
- same visual feel
- same goofiness
- same cursed `Dementris` identity
- much better code structure

This is not an in-place cleanup of `main.py`.
The current game stays as the reference implementation.

## Why Rewrite Instead Of Refactor

The current codebase works, but it comes from:
- old `PyTetris` code
- lots of direct modification
- systems being added on top of each other
- pre-OOP survival coding

Trying to untangle that file directly is likely to be slower, less fun, and more error-prone than rebuilding the game cleanly.

## Core Rule

Preserve the soul, replace the guts.

If the rewrite becomes technically cleaner but loses the original game's personality, visual jank, timing feel, or weirdness, that is a failure.

## Recommended Approach

1. Keep the existing `Dementris` as the playable reference.
2. Make a new branch for the rewrite.
3. Rebuild the normal Tetris foundation first.
4. Add `Dementris`-specific mechanics after the base game feels correct.
5. Port extra visuals, particles, and nonsense last.

## Rewrite Priorities

### First
- board/grid representation
- piece data and spawning
- movement and collision
- rotation system
- lock behavior
- line clear logic
- hold
- ghost piece
- input handling

### Second
- scoring / level / speed behavior
- menus / pause / reset
- control rebinding or config loading
- rendering cleanup

### Last
- dementia mechanics
- particles
- visual flourishes
- unusual animations
- all cursed extras

## Suggested Structure

Keep the architecture simple. Do not overengineer it just because this is a rewrite.

Possible layout:

- `Game`
  Runs the main loop and owns the high-level game state.

- `Board`
  Owns the playfield, collision checks, line clears, and lock behavior.

- `Piece`
  Represents the active tetromino, rotation state, and movement.

- `Bag` or `Randomizer`
  Handles piece generation.

- `Renderer`
  Draws the board, current piece, ghost, UI, overlays, and later effects.

- `InputMapper`
  Handles controls and config-backed key bindings.

- `DementiaSystem` or similar
  Contains the special `Dementris` mechanics so they do not infect the entire base game.

## Important Constraint

Keep normal Tetris logic separate from `Dementris` logic.

The original version likely mixes them together. The rewrite should not.

Base game systems should be understandable on their own.
The weird mechanics should plug into that clean base instead of replacing it with chaos.

## Practical Dev Strategy

- get an ugly playable build working first
- verify it feels close to the original before polishing architecture too much
- compare behavior against the original often
- only optimize once the remake is correct
- prefer several small files over one giant god file
- but do not split things so aggressively that the code becomes annoying to navigate

## What Success Looks Like

The rewrite should:
- feel like the same game
- be easier to extend
- be easier to debug
- make future features less painful
- let the code quality catch up to the idea

## Reminder

Do not let the rewrite become "generic clean Tetris clone #4000".

It should still feel like `Dementris`.

## Codex Session Resume

If this Codex CLI session gets closed and I want to restore this chat, use:

```bash
codex resume 019d9dd2-0958-7963-bc05-4938901fdb4c
```
