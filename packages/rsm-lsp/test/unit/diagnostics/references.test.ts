import { describe, it, expect } from 'vitest';
import { DiagnosticSeverity } from 'vscode-languageserver';
import { checkUndefinedReferences, checkReferences } from '../../../src/diagnostics/rules/references';
import { ASTNode } from '../../../src/layer2/ast';

describe('Reference diagnostics', () => {
  describe('checkUndefinedReferences', () => {
    it('should detect undefined references via Error nodes', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Error',
            start_point: [5, 0],
            end_point: [5, 20],
            text: '[unknown label "nonexistent"]',
          },
        ],
      };

      const diagnostics = checkUndefinedReferences(ast);
      expect(diagnostics).toHaveLength(1);
      expect(diagnostics[0].severity).toBe(DiagnosticSeverity.Error);
      expect(diagnostics[0].message).toContain('nonexistent');
    });

    it('should skip Error nodes with invalid positions', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Error',
            start_point: [-1, -1], // Invalid position
            end_point: [-1, -1],
            text: '[unknown label "foo"]',
          },
        ],
      };

      const diagnostics = checkUndefinedReferences(ast);
      expect(diagnostics).toHaveLength(0); // Skipped due to invalid position
    });

    it('should ignore non-reference Error nodes', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Error',
            start_point: [5, 0],
            end_point: [5, 10],
            text: '[CST error at (0, 0) - (0, 1)]',
          },
        ],
      };

      const diagnostics = checkUndefinedReferences(ast);
      expect(diagnostics).toHaveLength(0);
    });

    it('should extract label name from error message', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Error',
            start_point: [5, 0],
            end_point: [5, 20],
            text: '[unknown label "my-label"]',
          },
        ],
      };

      const diagnostics = checkUndefinedReferences(ast);
      expect(diagnostics).toHaveLength(1);
      expect(diagnostics[0].message).toContain('my-label');
    });
  });

  describe('checkReferences', () => {
    it('should run all reference checks', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Error',
            start_point: [5, 0],
            end_point: [5, 20],
            text: '[unknown label "undefined"]',
          },
        ],
      };

      const diagnostics = checkReferences(ast);
      expect(diagnostics.length).toBeGreaterThan(0);
    });
  });
});
