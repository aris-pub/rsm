/**
 * AST caching to avoid redundant Python subprocess calls
 */

import { ASTNode } from './ast';
import { logger } from '../utils/logger';

export interface CachedAST {
  ast: ASTNode;
  version: number;
  timestamp: number;
}

export class ASTCache {
  private cache = new Map<string, CachedAST>();

  /**
   * Get cached AST for a document
   */
  get(uri: string): CachedAST | undefined {
    return this.cache.get(uri);
  }

  /**
   * Set cached AST for a document
   */
  set(uri: string, ast: ASTNode, version: number): void {
    this.cache.set(uri, {
      ast,
      version,
      timestamp: Date.now(),
    });
    logger.debug(`Cached AST for ${uri} (version ${version})`);
  }

  /**
   * Check if cache is valid for given version
   */
  isValid(uri: string, version: number): boolean {
    const cached = this.cache.get(uri);
    if (!cached) return false;
    return cached.version === version;
  }

  /**
   * Delete cached AST for a document
   */
  delete(uri: string): void {
    this.cache.delete(uri);
    logger.debug(`Deleted cached AST for ${uri}`);
  }

  /**
   * Clear all cached ASTs
   */
  clear(): void {
    this.cache.clear();
    logger.debug('Cleared all cached ASTs');
  }

  /**
   * Get cache statistics
   */
  stats(): { size: number; uris: string[] } {
    return {
      size: this.cache.size,
      uris: Array.from(this.cache.keys()),
    };
  }
}
