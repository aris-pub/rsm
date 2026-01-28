#!/bin/bash
# Test RSM LSP server via JSON-RPC over stdio
# Usage: ./test-lsp.sh

cat <<'EOF' | node dist/server.js --stdio
Content-Length: 233

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"processId":null,"rootUri":"file:///tmp","capabilities":{"textDocument":{"completion":{"completionItem":{"snippetSupport":true}}}}}}
Content-Length: 52

{"jsonrpc":"2.0","method":"initialized","params":{}}
Content-Length: 312

{"jsonrpc":"2.0","method":"textDocument/didOpen","params":{"textDocument":{"uri":"file:///tmp/test.rsm","languageId":"rsm","version":1,"text":"# Test Document\n\nThis is a test.\n\n:the"}}}
Content-Length: 182

{"jsonrpc":"2.0","id":2,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///tmp/test.rsm"},"position":{"line":4,"character":4}}}
Content-Length: 45

{"jsonrpc":"2.0","id":3,"method":"shutdown"}
Content-Length: 36

{"jsonrpc":"2.0","method":"exit"}
EOF
