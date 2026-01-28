#!/usr/bin/env node
/**
 * Simple LSP client to test the RSM Language Server
 * Sends JSON-RPC messages and displays responses
 */

const { spawn } = require('child_process');

class LSPClient {
  constructor() {
    this.server = null;
    this.buffer = '';
    this.messageId = 1;
  }

  start() {
    return new Promise((resolve) => {
      this.server = spawn('node', ['dist/server.js', '--stdio']);

      this.server.stdout.on('data', (data) => {
        this.buffer += data.toString();
        this.processMessages();
      });

      this.server.stderr.on('data', (data) => {
        console.error('Server stderr:', data.toString());
      });

      this.server.on('close', (code) => {
        console.log(`Server exited with code ${code}`);
      });

      // Give server time to start
      setTimeout(resolve, 100);
    });
  }

  processMessages() {
    while (true) {
      const match = this.buffer.match(/Content-Length: (\d+)\r?\n\r?\n/);
      if (!match) break;

      const headerLength = match[0].length;
      const contentLength = parseInt(match[1]);
      const messageStart = match.index + headerLength;
      const messageEnd = messageStart + contentLength;

      if (this.buffer.length < messageEnd) break;

      const content = this.buffer.substring(messageStart, messageEnd);
      this.buffer = this.buffer.substring(messageEnd);

      try {
        const message = JSON.parse(content);
        this.handleMessage(message);
      } catch (error) {
        console.error('Failed to parse message:', error);
      }
    }
  }

  handleMessage(message) {
    if (message.method === 'window/logMessage') {
      console.log(`[LOG] ${message.params.message}`);
    } else if (message.method === 'textDocument/publishDiagnostics') {
      console.log('\n[DIAGNOSTICS]', JSON.stringify(message.params, null, 2));
    } else if (message.result !== undefined) {
      console.log('\n[RESPONSE] id=' + message.id, JSON.stringify(message.result, null, 2));
    } else if (message.error) {
      console.error('\n[ERROR]', JSON.stringify(message.error, null, 2));
    }
  }

  sendMessage(message) {
    const content = JSON.stringify(message);
    const header = `Content-Length: ${Buffer.byteLength(content)}\r\n\r\n`;
    this.server.stdin.write(header + content);
  }

  async initialize() {
    console.log('\n=== INITIALIZE ===');
    this.sendMessage({
      jsonrpc: '2.0',
      id: this.messageId++,
      method: 'initialize',
      params: {
        processId: process.pid,
        rootUri: 'file:///tmp',
        capabilities: {
          textDocument: {
            completion: {
              completionItem: {
                snippetSupport: true,
              },
            },
          },
        },
      },
    });

    await this.wait(200);

    this.sendMessage({
      jsonrpc: '2.0',
      method: 'initialized',
      params: {},
    });
  }

  async testCompletion() {
    console.log('\n=== TEST COMPLETION ===');

    // Open document with partial tag
    this.sendMessage({
      jsonrpc: '2.0',
      method: 'textDocument/didOpen',
      params: {
        textDocument: {
          uri: 'file:///tmp/test.rsm',
          languageId: 'rsm',
          version: 1,
          text: '# Test Document\n\nThis is a test.\n\n:the',
        },
      },
    });

    await this.wait(100);

    // Request completion
    this.sendMessage({
      jsonrpc: '2.0',
      id: this.messageId++,
      method: 'textDocument/completion',
      params: {
        textDocument: { uri: 'file:///tmp/test.rsm' },
        position: { line: 4, character: 4 },
      },
    });

    await this.wait(200);
  }

  async testSyntaxError() {
    console.log('\n=== TEST SYNTAX ERROR ===');

    this.sendMessage({
      jsonrpc: '2.0',
      method: 'textDocument/didOpen',
      params: {
        textDocument: {
          uri: 'file:///tmp/error.rsm',
          languageId: 'rsm',
          version: 1,
          text: ':theorem:\n\nUnclosed theorem tag',
        },
      },
    });

    await this.wait(200);
  }

  async shutdown() {
    console.log('\n=== SHUTDOWN ===');

    this.sendMessage({
      jsonrpc: '2.0',
      id: this.messageId++,
      method: 'shutdown',
    });

    await this.wait(100);

    this.sendMessage({
      jsonrpc: '2.0',
      method: 'exit',
    });
  }

  wait(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }
}

async function main() {
  console.log('RSM LSP Server Test Client\n');

  const client = new LSPClient();

  await client.start();
  await client.initialize();
  await client.testCompletion();
  await client.testSyntaxError();
  await client.shutdown();

  await client.wait(500);
  process.exit(0);
}

main().catch(console.error);
