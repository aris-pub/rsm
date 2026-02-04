import { describe, it, expect } from 'vitest';
import { DiagnosticSeverity } from 'vscode-languageserver';
import {
  checkMissingTitle,
  checkSectionsWithoutLabels,
  checkTheoremsWithoutLabels,
  checkEmptySections,
  checkStructure,
} from '../../../src/diagnostics/rules/structure';
import { ASTNode } from '../../../src/layer2/ast';

describe('Structure diagnostics', () => {
  describe('checkMissingTitle', () => {
    it('should warn if manuscript has no title', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [5, 0],
        title: '',
      };

      const diagnostics = checkMissingTitle(ast);
      expect(diagnostics).toHaveLength(1);
      expect(diagnostics[0].severity).toBe(DiagnosticSeverity.Warning);
      expect(diagnostics[0].message).toContain('missing a title');
    });

    it('should not warn if manuscript has title', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [5, 0],
        title: 'Test Document',
      };

      const diagnostics = checkMissingTitle(ast);
      expect(diagnostics).toHaveLength(0);
    });
  });

  describe('checkSectionsWithoutLabels', () => {
    it('should report sections without labels', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Section',
            start_point: [1, 0],
            end_point: [5, 0],
            title: 'Introduction',
            // No label
          },
        ],
      };

      const diagnostics = checkSectionsWithoutLabels(ast);
      expect(diagnostics).toHaveLength(1);
      expect(diagnostics[0].severity).toBe(DiagnosticSeverity.Information);
      expect(diagnostics[0].message).toContain('Introduction');
      expect(diagnostics[0].message).toContain('no label');
    });

    it('should not report sections with labels', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Section',
            start_point: [1, 0],
            end_point: [5, 0],
            title: 'Introduction',
            label: 'intro',
          },
        ],
      };

      const diagnostics = checkSectionsWithoutLabels(ast);
      expect(diagnostics).toHaveLength(0);
    });
  });

  describe('checkTheoremsWithoutLabels', () => {
    it('should report theorems without labels', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Theorem',
            start_point: [1, 0],
            end_point: [3, 0],
            // No label
          },
        ],
      };

      const diagnostics = checkTheoremsWithoutLabels(ast);
      expect(diagnostics).toHaveLength(1);
      expect(diagnostics[0].severity).toBe(DiagnosticSeverity.Information);
      expect(diagnostics[0].message).toContain('Theorem');
      expect(diagnostics[0].message).toContain('no label');
    });

    it('should check lemmas, propositions, definitions', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [20, 0],
        children: [
          { nodeclass: 'Lemma', start_point: [1, 0], end_point: [3, 0] },
          { nodeclass: 'Proposition', start_point: [4, 0], end_point: [6, 0] },
          { nodeclass: 'Definition', start_point: [7, 0], end_point: [9, 0] },
        ],
      };

      const diagnostics = checkTheoremsWithoutLabels(ast);
      expect(diagnostics).toHaveLength(3);
    });

    it('should not report labeled theorems', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Theorem',
            start_point: [1, 0],
            end_point: [3, 0],
            label: 'thm1',
          },
        ],
      };

      const diagnostics = checkTheoremsWithoutLabels(ast);
      expect(diagnostics).toHaveLength(0);
    });
  });

  describe('checkEmptySections', () => {
    it('should warn about empty sections', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Section',
            start_point: [1, 0],
            end_point: [2, 0],
            title: 'Empty Section',
            children: [],
          },
        ],
      };

      const diagnostics = checkEmptySections(ast);
      expect(diagnostics).toHaveLength(1);
      expect(diagnostics[0].severity).toBe(DiagnosticSeverity.Warning);
      expect(diagnostics[0].message).toContain('empty');
    });

    it('should not warn about sections with content', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        children: [
          {
            nodeclass: 'Section',
            start_point: [1, 0],
            end_point: [5, 0],
            title: 'Filled Section',
            children: [{ nodeclass: 'Paragraph', start_point: [2, 0], end_point: [3, 0] }],
          },
        ],
      };

      const diagnostics = checkEmptySections(ast);
      expect(diagnostics).toHaveLength(0);
    });
  });

  describe('checkStructure', () => {
    it('should run all structure checks', () => {
      const ast: ASTNode = {
        nodeclass: 'Manuscript',
        start_point: [0, 0],
        end_point: [10, 0],
        title: '', // Missing title
        children: [
          {
            nodeclass: 'Section',
            start_point: [1, 0],
            end_point: [2, 0],
            title: 'Empty',
            children: [], // Empty section
          },
          {
            nodeclass: 'Theorem',
            start_point: [3, 0],
            end_point: [5, 0],
            // No label
          },
        ],
      };

      const diagnostics = checkStructure(ast);
      expect(diagnostics.length).toBeGreaterThan(0);
    });
  });
});
