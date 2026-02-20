# RSM-LSP Emacs Setup

Clean setup of rsm-lsp for Emacs with eglot.

## What's Configured

### 1. rsm-mode (`~/elisp/rsm-mode.el`)
- Clean major mode for `.rsm` files
- Basic syntax highlighting (regexp-based fallback)
- Optional tree-sitter support (if grammar installed)
- Comment support (`%` line comments)
- Basic indentation

### 2. Eglot Integration (`~/elisp/init.el`)
- Auto-starts LSP server when opening `.rsm` files
- Server path: `/Users/leo.torres/aris/rsm/packages/rsm-lsp/dist/server.js`
- Provides:
  - Real-time diagnostics (syntax errors, structure validation)
  - Tag completion (`:the` → `:theorem:`)
  - Semantic analysis via Python AST

## Testing

1. **Reload Emacs config:**
   ```elisp
   M-x eval-buffer RET  ; in init.el
   ```

2. **Open an RSM file:**
   ```
   C-x C-f /path/to/test.rsm
   ```

3. **Verify LSP is running:**
   ```elisp
   M-x eglot-events  ; Shows LSP protocol messages
   M-x eglot-stderr  ; Shows server logs
   ```

4. **Test completion:**
   - Type `:the` and wait for completion popup
   - Should suggest `:theorem:`

5. **Test diagnostics:**
   - Create a syntax error (e.g., `:theorem:` without `::`)
   - Should see error underline and message

## Commands

- `M-x reload-rsm-mode` - Reload rsm-mode from disk
- `C-c l r` - Rename symbol (eglot)
- `C-c l a` - Code actions (eglot)
- `M-.` - Go to definition (eglot)
- `M-;` - Find references (eglot)

## Troubleshooting

### LSP server won't start

Check server works manually:
```bash
cd /Users/leo.torres/aris/rsm/packages/rsm-lsp
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | node dist/server.js --stdio
```

### No syntax highlighting

Tree-sitter grammar not installed. Mode still works with basic regexp highlighting. To install tree-sitter grammar:

```bash
# Build and install grammar for Emacs
cd /Users/leo.torres/aris/rsm/tree-sitter-rsm
npx tree-sitter generate
# Then compile as dynamic library for Emacs (platform-specific)
```

### Completions don't work

1. Check eglot is connected: `M-x eglot`
2. Enable completion: `M-x company-mode` or ensure `corfu-mode` is active
3. Check completion trigger character is `:` in server capabilities

### Python errors in diagnostics

LSP uses `uv run rsm parse` for semantic analysis. Ensure:
```bash
cd /Users/leo.torres/aris/rsm
uv run rsm --version  # Should work
```

If not, run:
```bash
cd /Users/leo.torres/aris/rsm
just install
```

## Current Limitations

1. **Tree-sitter grammar not installed** - Using basic regexp highlighting
2. **No hover info yet** - Planned for Phase 4
3. **No go-to-definition yet** - Planned for Phase 4
4. **Limited reference tracking** - Python transformer pre-resolves refs

## Next Steps

To enable full tree-sitter syntax highlighting, install the RSM grammar for Emacs. This requires compiling the grammar as a dynamic library (`.dylib` on macOS) and placing it in `~/.emacs.d/tree-sitter/`.

For now, the LSP server provides all the important features (diagnostics, completion) without tree-sitter.
