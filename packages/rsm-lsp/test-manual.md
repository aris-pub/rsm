# Testing RSM LSP Server via Terminal

The RSM LSP server communicates using JSON-RPC 2.0 over stdin/stdout.

## Quick Test

Run the server:
```bash
node dist/server.js --stdio
```

Then paste these messages one by one (each message needs a Content-Length header):

### 1. Initialize
```
Content-Length: 233

{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"processId":null,"rootUri":"file:///tmp","capabilities":{"textDocument":{"completion":{"completionItem":{"snippetSupport":true}}}}}}
```

Expected response: Server capabilities with `completionProvider`

### 2. Initialized notification
```
Content-Length: 52

{"jsonrpc":"2.0","method":"initialized","params":{}}
```

### 3. Open document
```
Content-Length: 312

{"jsonrpc":"2.0","method":"textDocument/didOpen","params":{"textDocument":{"uri":"file:///tmp/test.rsm","languageId":"rsm","version":1,"text":"# Test Document\n\nThis is a test.\n\n:the"}}}
```

### 4. Request completion at `:the`
```
Content-Length: 182

{"jsonrpc":"2.0","id":2,"method":"textDocument/completion","params":{"textDocument":{"uri":"file:///tmp/test.rsm"},"position":{"line":4,"character":4}}}
```

Expected response: Completion items including `:theorem:`, `:the:`, etc.

### 5. Test syntax error detection

Open a document with invalid syntax:
```
Content-Length: 289

{"jsonrpc":"2.0","method":"textDocument/didOpen","params":{"textDocument":{"uri":"file:///tmp/error.rsm","languageId":"rsm","version":1,"text":":theorem:\n\nUnclosed theorem tag"}}}
```

Expected: `textDocument/publishDiagnostics` with ERROR nodes

### 6. Shutdown
```
Content-Length: 45

{"jsonrpc":"2.0","id":3,"method":"shutdown"}
```

### 7. Exit
```
Content-Length: 36

{"jsonrpc":"2.0","method":"exit"}
```

## JSON-RPC Message Format

Each message must have:
1. `Content-Length: <bytes>\r\n\r\n` header
2. JSON payload (exact byte length as specified)

The byte length includes only the JSON payload, not the header.

## What Success Looks Like

1. **Initialize response**: Shows server capabilities (completion, diagnostics)
2. **Completion response**: Returns array of completion items with RSM tags
3. **Diagnostics**: Publishes syntax errors for invalid documents
4. **Clean shutdown**: Server exits with code 0

## Automated Test

Use the provided `test-lsp.sh` script:
```bash
./test-lsp.sh 2>&1 | grep -E '(jsonrpc|result|params)'
```

Look for:
- Initialize result with `completionProvider`
- Completion result with array of items
- Diagnostic notifications for errors
