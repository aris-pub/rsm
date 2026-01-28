import { Position, Range } from 'vscode-languageserver';
import { Point } from 'tree-sitter';

/**
 * Convert tree-sitter Point to LSP Position
 */
export function pointToPosition(point: Point): Position {
  return Position.create(point.row, point.column);
}

/**
 * Convert tree-sitter start/end points to LSP Range
 */
export function pointsToRange(start: Point, end: Point): Range {
  return Range.create(pointToPosition(start), pointToPosition(end));
}

/**
 * Check if a position is within a range
 */
export function isPositionInRange(position: Position, range: Range): boolean {
  if (position.line < range.start.line || position.line > range.end.line) {
    return false;
  }
  if (position.line === range.start.line && position.character < range.start.character) {
    return false;
  }
  if (position.line === range.end.line && position.character > range.end.character) {
    return false;
  }
  return true;
}

/**
 * Check if two ranges overlap
 */
export function rangesOverlap(a: Range, b: Range): boolean {
  return !(
    a.end.line < b.start.line ||
    (a.end.line === b.start.line && a.end.character < b.start.character) ||
    b.end.line < a.start.line ||
    (b.end.line === a.start.line && b.end.character < a.start.character)
  );
}

/**
 * Convert Python AST position tuple [row, column] to tree-sitter Point
 */
export function tupleToPoint(tuple: [number, number]): Point {
  return { row: tuple[0], column: tuple[1] };
}

/**
 * Convert Python AST position tuples to LSP Range
 */
export function tuplesToRange(start: [number, number], end: [number, number]): Range {
  return pointsToRange(tupleToPoint(start), tupleToPoint(end));
}
