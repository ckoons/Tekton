# Tekton Clean Launcher

A clean C launcher for Tekton that handles environment setup before Python starts.

## Why C?

Similar to Git, Docker, and other tools, using a compiled launcher solves the Python module import timing issues by setting up the environment cleanly before Python even starts.

## Building

```bash
make
```

## Installing

```bash
# Symlink to your utils directory
ln -s $(pwd)/tekton-clean-launch ~/utils/tekton

# Or copy it
cp tekton-clean-launch ~/utils/tekton
```

## How it works

1. Parses command line arguments (including `--coder`)
2. Loads environment files in order:
   - `~/.env`
   - `$TEKTON_ROOT/.env.tekton`
   - `$TEKTON_ROOT/.env.local`
3. Sets `_TEKTON_ENV_FROZEN=1` to indicate environment is ready
4. Executes the appropriate Python script with the full environment

## Benefits

- No Python import timing issues
- Clean environment setup before Python starts
- Supports `--coder` flag for alternate environments
- Fast startup
- Simple and predictable