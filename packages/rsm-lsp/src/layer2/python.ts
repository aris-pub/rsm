/**
 * Python subprocess integration for RSM AST parsing
 * Spawns `rsm parse --json` to get semantic AST from Python
 */

import { exec } from 'child_process';
import { promisify } from 'util';
import { ASTNode } from './ast';
import { logger } from '../utils/logger';

const execAsync = promisify(exec);

export interface ParseResult {
  ast: ASTNode;
  elapsed: number;
}

export interface ParseError {
  message: string;
  stderr: string;
}

/**
 * Parse RSM document using Python CLI
 * @param text - Document text
 * @param timeout - Timeout in milliseconds (default: 5000)
 * @returns Promise resolving to AST or rejecting with error
 */
export async function parseWithPython(
  text: string,
  timeout = 5000
): Promise<ParseResult> {
  const startTime = Date.now();

  try {
    // Escape text for shell
    const escapedText = text.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\$/g, '\\$');

    // Call rsm parse -c with the document text
    const command = `uv run rsm parse -c "${escapedText}" --log-format json --log-no-timestamps --log-no-lineno`;

    logger.debug(`Calling Python: ${command.substring(0, 100)}...`);

    const { stdout, stderr } = await execAsync(command, {
      timeout,
      maxBuffer: 10 * 1024 * 1024, // 10MB buffer
      cwd: process.cwd(),
    });

    // Parse JSON output
    const ast = JSON.parse(stdout) as ASTNode;

    const elapsed = Date.now() - startTime;
    logger.debug(`Python parse completed in ${elapsed}ms`);

    return { ast, elapsed };
  } catch (error) {
    const elapsed = Date.now() - startTime;

    if (error instanceof Error) {
      logger.error(`Python parse failed after ${elapsed}ms:`, error.message);

      // Check if it's a timeout
      if (error.message.includes('timeout')) {
        throw new Error(`Python parsing timed out after ${timeout}ms`);
      }

      // Check if it's a JSON parse error
      if (error.message.includes('JSON')) {
        throw new Error(`Failed to parse Python output: ${error.message}`);
      }

      // Otherwise, it's likely a subprocess error
      const stderr = (error as any).stderr || '';
      throw {
        message: error.message,
        stderr,
      } as ParseError;
    }

    throw error;
  }
}

/**
 * Test if Python CLI is available
 */
export async function testPythonCLI(): Promise<boolean> {
  try {
    await execAsync('uv run rsm --version', { timeout: 2000 });
    return true;
  } catch {
    return false;
  }
}
