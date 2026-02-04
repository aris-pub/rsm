import { describe, it, expect } from 'vitest';
import {
  ASTNode,
  isNodeOfType,
  findNodesByType,
  findNodeByLabel,
  extractLabels,
  extractReferences,
} from '../../../src/layer2/ast';

// Mock AST structure
const mockAST: ASTNode = {
  nodeclass: 'Manuscript',
  start_point: [0, 0],
  end_point: [10, 0],
  title: 'Test',
  children: [
    {
      nodeclass: 'Section',
      start_point: [1, 0],
      end_point: [5, 0],
      label: 'sec1',
      title: 'Introduction',
      children: [
        {
          nodeclass: 'Paragraph',
          start_point: [2, 0],
          end_point: [3, 0],
          children: [
            {
              nodeclass: 'Text',
              start_point: [2, 0],
              end_point: [2, 10],
              text: 'Hello',
            },
          ],
        },
      ],
    },
    {
      nodeclass: 'Theorem',
      start_point: [6, 0],
      end_point: [8, 0],
      label: 'thm1',
      children: [],
    },
    {
      nodeclass: 'Reference',
      start_point: [9, 0],
      end_point: [9, 10],
      target: 'thm1',
    },
  ],
};

describe('AST helper functions', () => {
  describe('isNodeOfType', () => {
    it('should check node type correctly', () => {
      expect(isNodeOfType(mockAST, 'Manuscript')).toBe(true);
      expect(isNodeOfType(mockAST, 'Section')).toBe(false);
    });
  });

  describe('findNodesByType', () => {
    it('should find all nodes of given type', () => {
      const sections = findNodesByType(mockAST, 'Section');
      expect(sections).toHaveLength(1);
      expect(sections[0].nodeclass).toBe('Section');
    });

    it('should find nested nodes', () => {
      const paragraphs = findNodesByType(mockAST, 'Paragraph');
      expect(paragraphs).toHaveLength(1);
    });

    it('should return empty array if no matches', () => {
      const lemmas = findNodesByType(mockAST, 'Lemma');
      expect(lemmas).toHaveLength(0);
    });

    it('should find all Text nodes', () => {
      const texts = findNodesByType(mockAST, 'Text');
      expect(texts).toHaveLength(1);
      expect(texts[0].text).toBe('Hello');
    });
  });

  describe('findNodeByLabel', () => {
    it('should find node by label', () => {
      const node = findNodeByLabel(mockAST, 'thm1');
      expect(node).toBeDefined();
      expect(node?.nodeclass).toBe('Theorem');
    });

    it('should find nested labeled nodes', () => {
      const node = findNodeByLabel(mockAST, 'sec1');
      expect(node).toBeDefined();
      expect(node?.nodeclass).toBe('Section');
    });

    it('should return null for nonexistent label', () => {
      const node = findNodeByLabel(mockAST, 'nonexistent');
      expect(node).toBeNull();
    });
  });

  describe('extractLabels', () => {
    it('should extract all labels', () => {
      const labels = extractLabels(mockAST);
      expect(labels.size).toBe(2);
      expect(labels.has('sec1')).toBe(true);
      expect(labels.has('thm1')).toBe(true);
    });

    it('should map labels to nodes', () => {
      const labels = extractLabels(mockAST);
      const thm = labels.get('thm1');
      expect(thm?.nodeclass).toBe('Theorem');
    });
  });

  describe('extractReferences', () => {
    it('should extract all references', () => {
      const refs = extractReferences(mockAST);
      expect(refs).toHaveLength(1);
      expect(refs[0].target).toBe('thm1');
      expect(refs[0].node.nodeclass).toBe('Reference');
    });
  });
});
