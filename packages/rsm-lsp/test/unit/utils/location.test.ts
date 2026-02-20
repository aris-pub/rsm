import { describe, it, expect } from 'vitest';
import {
  pointToPosition,
  pointsToRange,
  isPositionInRange,
  rangesOverlap,
  tupleToPoint,
  tuplesToRange,
} from '../../../src/utils/location';
import { Position, Range } from 'vscode-languageserver';
import { Point } from 'tree-sitter';

describe('location utilities', () => {
  describe('pointToPosition', () => {
    it('should convert tree-sitter Point to LSP Position', () => {
      const point: Point = { row: 5, column: 10 };
      const position = pointToPosition(point);

      expect(position.line).toBe(5);
      expect(position.character).toBe(10);
    });

    it('should handle zero position', () => {
      const point: Point = { row: 0, column: 0 };
      const position = pointToPosition(point);

      expect(position.line).toBe(0);
      expect(position.character).toBe(0);
    });
  });

  describe('pointsToRange', () => {
    it('should convert start and end points to LSP Range', () => {
      const start: Point = { row: 1, column: 5 };
      const end: Point = { row: 3, column: 10 };
      const range = pointsToRange(start, end);

      expect(range.start.line).toBe(1);
      expect(range.start.character).toBe(5);
      expect(range.end.line).toBe(3);
      expect(range.end.character).toBe(10);
    });

    it('should handle single-point range', () => {
      const point: Point = { row: 2, column: 7 };
      const range = pointsToRange(point, point);

      expect(range.start).toEqual(range.end);
    });
  });

  describe('isPositionInRange', () => {
    const range = Range.create(
      Position.create(5, 10),
      Position.create(8, 20)
    );

    it('should return true for position inside range', () => {
      const position = Position.create(6, 15);
      expect(isPositionInRange(position, range)).toBe(true);
    });

    it('should return true for position at start of range', () => {
      const position = Position.create(5, 10);
      expect(isPositionInRange(position, range)).toBe(true);
    });

    it('should return true for position at end of range', () => {
      const position = Position.create(8, 20);
      expect(isPositionInRange(position, range)).toBe(true);
    });

    it('should return false for position before range (line)', () => {
      const position = Position.create(4, 15);
      expect(isPositionInRange(position, range)).toBe(false);
    });

    it('should return false for position after range (line)', () => {
      const position = Position.create(9, 15);
      expect(isPositionInRange(position, range)).toBe(false);
    });

    it('should return false for position before range (same start line)', () => {
      const position = Position.create(5, 9);
      expect(isPositionInRange(position, range)).toBe(false);
    });

    it('should return false for position after range (same end line)', () => {
      const position = Position.create(8, 21);
      expect(isPositionInRange(position, range)).toBe(false);
    });

    it('should handle single-line range', () => {
      const singleLineRange = Range.create(
        Position.create(5, 10),
        Position.create(5, 20)
      );

      expect(isPositionInRange(Position.create(5, 15), singleLineRange)).toBe(true);
      expect(isPositionInRange(Position.create(5, 9), singleLineRange)).toBe(false);
      expect(isPositionInRange(Position.create(5, 21), singleLineRange)).toBe(false);
      expect(isPositionInRange(Position.create(4, 15), singleLineRange)).toBe(false);
      expect(isPositionInRange(Position.create(6, 15), singleLineRange)).toBe(false);
    });
  });

  describe('rangesOverlap', () => {
    it('should return true for completely overlapping ranges', () => {
      const a = Range.create(Position.create(5, 0), Position.create(10, 0));
      const b = Range.create(Position.create(6, 0), Position.create(9, 0));
      expect(rangesOverlap(a, b)).toBe(true);
      expect(rangesOverlap(b, a)).toBe(true);
    });

    it('should return true for partially overlapping ranges', () => {
      const a = Range.create(Position.create(5, 0), Position.create(10, 0));
      const b = Range.create(Position.create(8, 0), Position.create(12, 0));
      expect(rangesOverlap(a, b)).toBe(true);
      expect(rangesOverlap(b, a)).toBe(true);
    });

    it('should return true for ranges that touch at boundary', () => {
      const a = Range.create(Position.create(5, 0), Position.create(10, 20));
      const b = Range.create(Position.create(10, 20), Position.create(15, 0));
      expect(rangesOverlap(a, b)).toBe(true);
    });

    it('should return false for non-overlapping ranges (different lines)', () => {
      const a = Range.create(Position.create(5, 0), Position.create(7, 0));
      const b = Range.create(Position.create(8, 0), Position.create(10, 0));
      expect(rangesOverlap(a, b)).toBe(false);
      expect(rangesOverlap(b, a)).toBe(false);
    });

    it('should return false for non-overlapping ranges (same line)', () => {
      const a = Range.create(Position.create(5, 0), Position.create(5, 10));
      const b = Range.create(Position.create(5, 15), Position.create(5, 20));
      expect(rangesOverlap(a, b)).toBe(false);
    });

    it('should return false for adjacent ranges on same line', () => {
      const a = Range.create(Position.create(5, 0), Position.create(5, 10));
      const b = Range.create(Position.create(5, 11), Position.create(5, 20));
      expect(rangesOverlap(a, b)).toBe(false);
    });

    it('should handle identical ranges', () => {
      const a = Range.create(Position.create(5, 0), Position.create(10, 0));
      const b = Range.create(Position.create(5, 0), Position.create(10, 0));
      expect(rangesOverlap(a, b)).toBe(true);
    });

    it('should handle single-character ranges', () => {
      const a = Range.create(Position.create(5, 10), Position.create(5, 10));
      const b = Range.create(Position.create(5, 10), Position.create(5, 10));
      expect(rangesOverlap(a, b)).toBe(true);
    });

    it('should handle multi-line overlap with character precision', () => {
      const a = Range.create(Position.create(5, 10), Position.create(7, 5));
      const b = Range.create(Position.create(7, 3), Position.create(9, 0));
      expect(rangesOverlap(a, b)).toBe(true);
    });

    it('should return false when ranges end exactly where other starts (same line)', () => {
      const a = Range.create(Position.create(5, 0), Position.create(5, 10));
      const b = Range.create(Position.create(5, 10), Position.create(5, 20));
      expect(rangesOverlap(a, b)).toBe(true); // They touch at character 10
    });
  });

  describe('tupleToPoint', () => {
    it('should convert Python AST tuple to tree-sitter Point', () => {
      const tuple: [number, number] = [3, 7];
      const point = tupleToPoint(tuple);

      expect(point.row).toBe(3);
      expect(point.column).toBe(7);
    });

    it('should handle zero tuple', () => {
      const tuple: [number, number] = [0, 0];
      const point = tupleToPoint(tuple);

      expect(point.row).toBe(0);
      expect(point.column).toBe(0);
    });
  });

  describe('tuplesToRange', () => {
    it('should convert Python AST tuples to LSP Range', () => {
      const start: [number, number] = [2, 5];
      const end: [number, number] = [4, 10];
      const range = tuplesToRange(start, end);

      expect(range.start.line).toBe(2);
      expect(range.start.character).toBe(5);
      expect(range.end.line).toBe(4);
      expect(range.end.character).toBe(10);
    });

    it('should handle single-point tuple range', () => {
      const tuple: [number, number] = [1, 8];
      const range = tuplesToRange(tuple, tuple);

      expect(range.start.line).toBe(1);
      expect(range.start.character).toBe(8);
      expect(range.end.line).toBe(1);
      expect(range.end.character).toBe(8);
    });
  });
});
