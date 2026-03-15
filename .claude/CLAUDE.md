# CLAUDE.md — RSM

## Testing

**NEVER EVER EVER EVER run the entire test suite.** It will take HOURS.

Use the justfile recipes:

- `just test-fast` — fast tests only (skips slow, visual, accessibility, interactive)
- `just test-slow` — only slow tests
- `just test-visual` — visual regression tests (parallel)
- `just test-a11y` — accessibility tests (parallel)
- `just test-interactive` — interactive browser tests
- `just test-docs` — doctests

When working on a specific feature, run only the relevant test files directly:
```bash
uv run pytest tests/test_author.py tests/test_author_advanced.py -x -q
```

**Do NOT run `uv run pytest tests/` or `just test` — those run everything.**
