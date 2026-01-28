/**
 * Debouncing mechanism for Python AST parsing
 * Waits for a pause in edits before triggering expensive operations
 */

import { logger } from '../utils/logger';

export type DebouncedCallback = () => void | Promise<void>;

export class Debouncer {
  private timers = new Map<string, NodeJS.Timeout>();
  private defaultDelay: number;

  constructor(defaultDelay = 500) {
    this.defaultDelay = defaultDelay;
  }

  /**
   * Debounce a callback for a specific key
   * @param key - Unique identifier for this debounced operation
   * @param callback - Function to call after delay
   * @param delay - Delay in milliseconds (uses default if not provided)
   */
  debounce(key: string, callback: DebouncedCallback, delay?: number): void {
    const actualDelay = delay ?? this.defaultDelay;

    // Cancel existing timer for this key
    const existingTimer = this.timers.get(key);
    if (existingTimer) {
      clearTimeout(existingTimer);
      logger.debug(`Cancelled pending operation for ${key}`);
    }

    // Set new timer
    const timer = setTimeout(async () => {
      logger.debug(`Executing debounced operation for ${key} after ${actualDelay}ms`);
      this.timers.delete(key);
      await callback();
    }, actualDelay);

    this.timers.set(key, timer);
    logger.debug(`Scheduled operation for ${key} in ${actualDelay}ms`);
  }

  /**
   * Cancel a pending debounced operation
   */
  cancel(key: string): void {
    const timer = this.timers.get(key);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(key);
      logger.debug(`Cancelled operation for ${key}`);
    }
  }

  /**
   * Cancel all pending operations
   */
  cancelAll(): void {
    for (const [key, timer] of this.timers.entries()) {
      clearTimeout(timer);
      logger.debug(`Cancelled operation for ${key}`);
    }
    this.timers.clear();
  }

  /**
   * Check if an operation is pending
   */
  isPending(key: string): boolean {
    return this.timers.has(key);
  }

  /**
   * Get all pending operation keys
   */
  getPending(): string[] {
    return Array.from(this.timers.keys());
  }
}
