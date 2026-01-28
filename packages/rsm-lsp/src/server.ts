#!/usr/bin/env node

import {
  createConnection,
  TextDocuments,
  ProposedFeatures,
  InitializeParams,
  TextDocumentSyncKind,
  InitializeResult,
  CompletionParams,
  CompletionItem,
} from 'vscode-languageserver/node';

import { TextDocument } from 'vscode-languageserver-textdocument';
import { RsmParser, ParseTreeCache } from './layer1/parser';
import { getTagCompletions, getPartialTag } from './layer1/completion';
import { logger } from './utils/logger';

// Create LSP connection
const connection = createConnection(ProposedFeatures.all);

// Create document manager
const documents = new TextDocuments(TextDocument);

// Parser and cache
const parser = new RsmParser();
const parseCache = new ParseTreeCache();

// Initialize server
connection.onInitialize((_params: InitializeParams) => {
  logger.info('Initializing RSM Language Server');

  const result: InitializeResult = {
    capabilities: {
      textDocumentSync: TextDocumentSyncKind.Incremental,
      completionProvider: {
        triggerCharacters: [':'],
      },
    },
  };

  return result;
});

connection.onInitialized(() => {
  logger.info('RSM Language Server initialized');
});

// Document lifecycle handlers
documents.onDidOpen((event) => {
  logger.debug(`Document opened: ${event.document.uri}`);
  validateDocument(event.document);
});

documents.onDidChangeContent((event) => {
  logger.debug(`Document changed: ${event.document.uri}`);
  validateDocument(event.document);
});

documents.onDidClose((event) => {
  logger.debug(`Document closed: ${event.document.uri}`);
  parseCache.delete(event.document.uri);
  connection.sendDiagnostics({ uri: event.document.uri, diagnostics: [] });
});

/**
 * Validate document (Layer 1: syntax checking)
 */
function validateDocument(document: TextDocument) {
  const text = document.getText();
  const uri = document.uri;
  const version = document.version;

  // Get old tree for incremental parsing
  const cached = parseCache.get(uri);
  const oldTree = cached?.tree;

  // Parse with tree-sitter
  const tree = parser.parse(text, oldTree);
  parseCache.set(uri, tree, version);

  // Extract syntax errors
  const diagnostics = parser.getSyntaxErrors(tree);

  // Send diagnostics to client
  connection.sendDiagnostics({ uri, diagnostics });

  logger.debug(`Found ${diagnostics.length} syntax errors in ${uri}`);
}

/**
 * Completion handler
 */
connection.onCompletion((params: CompletionParams): CompletionItem[] => {
  const document = documents.get(params.textDocument.uri);
  if (!document) {
    return [];
  }

  const position = params.position;
  const line = document.getText({
    start: { line: position.line, character: 0 },
    end: position,
  });

  // Check if we're in a position for tag completion
  const partialTag = getPartialTag(line, position.character);
  if (partialTag) {
    logger.debug(`Tag completion triggered: ${partialTag}`);
    return getTagCompletions(partialTag);
  }

  return [];
});

// Make the text document manager listen on the connection
documents.listen(connection);

// Start listening
connection.listen();

logger.info('RSM Language Server started');
