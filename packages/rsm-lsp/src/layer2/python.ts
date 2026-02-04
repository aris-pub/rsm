/**
 * Python subprocess integration for RSM AST parsing
 * Spawns `rsm parse --json` to get semantic AST from Python
 */

import { spawn } from 'child_process';
import { writeFile, unlink } from 'fs/promises';
import { tmpdir } from 'os';
import { join } from 'path';
import { ASTNode } from './ast';
import { logger } from '../utils/logger';

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
  let tempFile: string | null = null;

  try {
    // Write text to temporary file
    tempFile = join(tmpdir(), `rsm-lsp-${Date.now()}-${Math.random().toString(36).slice(2)}.rsm`);
    await writeFile(tempFile, text, 'utf-8');

    logger.debug(`Calling Python with temp file: ${tempFile}`);

    // Use spawn instead of exec to avoid shell injection
    const args = [
      'run',
      'rsm',
      'parse',
      tempFile,
      '--log-format',
      'json',
      '--log-no-timestamps',
      '--log-no-lineno',
    ];

    const stdout = await spawnProcess('uv', args, timeout);

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

      // Otherwise, it's a subprocess error
      const stderr = (error as any).stderr || '';
      throw {
        message: error.message,
        stderr,
      } as ParseError;
    }

    throw error;
  } finally {
    // Clean up temp file
    if (tempFile) {
      try {
        await unlink(tempFile);
        logger.debug(`Cleaned up temp file: ${tempFile}`);
      } catch {
        // Ignore cleanup errors
      }
    }
  }
}

/**
 * Helper function to spawn a process and return stdout
 */
function spawnProcess(
  command: string,
  args: string[],
  timeout: number
): Promise<string> {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      cwd: process.cwd(),
    });

    let stdout = '';
    let stderr = '';

    child.stdout.on('data', (data) => {
      stdout += data.toString();
    });

    child.stderr.on('data', (data) => {
      stderr += data.toString();
    });

    const timeoutId = setTimeout(() => {
      child.kill();
      reject(new Error(`Process timed out after ${timeout}ms`));
    }, timeout);

    child.on('error', (error) => {
      clearTimeout(timeoutId);
      reject(error);
    });

    child.on('close', (code) => {
      clearTimeout(timeoutId);
      if (code === 0) {
        resolve(stdout);
      } else {
        const error: any = new Error(`Process exited with code ${code}`);
        error.stderr = stderr;
        reject(error);
      }
    });
  });
}

/**
 * Test if Python CLI is available
 */
export async function testPythonCLI(): Promise<boolean> {
  try {
    await spawnProcess('uv', ['run', 'rsm', '--version'], 2000);
    return true;
  } catch {
    return false;
  }
}
