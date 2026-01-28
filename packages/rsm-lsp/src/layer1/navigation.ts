import { SyntaxNode, Tree } from 'tree-sitter';
import { Range } from 'vscode-languageserver';
import { pointsToRange } from '../utils/location';

/**
 * Represents a label found in the document
 */
export interface Label {
  name: string;
  range: Range;
  nodeType: string;
}

/**
 * Extract all labels from parse tree
 * Labels are defined as {:label: name} in metadata
 */
export function extractLabels(tree: Tree, text: string): Label[] {
  const labels: Label[] = [];

  function visit(node: SyntaxNode) {
    // Look for metadata nodes that contain labels
    if (node.type === 'metadata') {
      const labelNode = findLabelInMetadata(node, text);
      if (labelNode) {
        labels.push({
          name: labelNode.name,
          range: pointsToRange(node.parent!.startPosition, node.parent!.endPosition),
          nodeType: node.parent!.type,
        });
      }
    }

    for (let i = 0; i < node.childCount; i++) {
      const child = node.child(i);
      if (child) {
        visit(child);
      }
    }
  }

  visit(tree.rootNode);
  return labels;
}

/**
 * Find label definition in metadata node
 * Looks for pattern: {:label: name}
 */
function findLabelInMetadata(metadataNode: SyntaxNode, text: string): { name: string } | null {
  for (let i = 0; i < metadataNode.childCount; i++) {
    const child = metadataNode.child(i);
    if (!child) continue;

    // Look for metadata_pair with key 'label'
    if (child.type === 'metadata_pair') {
      const key = child.childForFieldName('key');
      const value = child.childForFieldName('value');

      if (key && value) {
        const keyText = text.substring(key.startIndex, key.endIndex);
        if (keyText === 'label') {
          const labelName = text.substring(value.startIndex, value.endIndex).trim();
          return { name: labelName };
        }
      }
    }
  }

  return null;
}

/**
 * Extract reference targets from parse tree
 * References are :ref:target:: or :cite:target::
 */
export function extractReferences(tree: Tree, text: string): Array<{ target: string; range: Range }> {
  const references: Array<{ target: string; range: Range }> = [];

  function visit(node: SyntaxNode) {
    // Look for reference nodes
    if (node.type === 'reference' || node.type === 'citation') {
      const targetNode = node.childForFieldName('target');
      if (targetNode) {
        const target = text.substring(targetNode.startIndex, targetNode.endIndex);
        references.push({
          target,
          range: pointsToRange(node.startPosition, node.endPosition),
        });
      }
    }

    for (let i = 0; i < node.childCount; i++) {
      const child = node.child(i);
      if (child) {
        visit(child);
      }
    }
  }

  visit(tree.rootNode);
  return references;
}
