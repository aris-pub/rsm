/**
 * TypeScript type definitions for RSM AST (deserialized from Python JSON)
 */

export interface ASTNode {
  nodeclass: string;
  start_point: [number, number];
  end_point: [number, number];
  reftext?: string;
  nodeid?: number;
  label?: string;
  number?: number;
  children?: ASTNode[];

  // Node-specific properties
  text?: string; // Text nodes
  title?: string; // Heading nodes (Manuscript, Section, etc.)
  name?: string; // Author nodes
  email?: string; // Author nodes
  affiliation?: string; // Author nodes
  target?: string; // Reference nodes
  targetlabels?: string[]; // Cite nodes: all bibtex keys
  unknownTargetlabels?: string[]; // Cite nodes: keys that failed to resolve
  [key: string]: unknown; // Allow other properties
}

export interface Manuscript extends ASTNode {
  nodeclass: 'Manuscript';
  title: string;
  children: ASTNode[];
}

/**
 * Check if a node is of a specific type
 */
export function isNodeOfType(node: ASTNode, type: string): boolean {
  return node.nodeclass === type;
}

/**
 * Find all nodes of a given type in the AST
 */
export function findNodesByType(root: ASTNode, type: string): ASTNode[] {
  const results: ASTNode[] = [];

  function traverse(node: ASTNode) {
    if (node.nodeclass === type) {
      results.push(node);
    }
    if (node.children) {
      for (const child of node.children) {
        traverse(child);
      }
    }
  }

  traverse(root);
  return results;
}

/**
 * Find a node by label
 */
export function findNodeByLabel(root: ASTNode, label: string): ASTNode | null {
  function traverse(node: ASTNode): ASTNode | null {
    if (node.label === label) {
      return node;
    }
    if (node.children) {
      for (const child of node.children) {
        const result = traverse(child);
        if (result) return result;
      }
    }
    return null;
  }

  return traverse(root);
}

/**
 * Extract all labels from the AST
 */
export function extractLabels(root: ASTNode): Map<string, ASTNode> {
  const labels = new Map<string, ASTNode>();

  function traverse(node: ASTNode) {
    if (node.label) {
      labels.set(node.label, node);
    }
    if (node.children) {
      for (const child of node.children) {
        traverse(child);
      }
    }
  }

  traverse(root);
  return labels;
}

/**
 * Find a node by its nodeid
 */
export function findNodeById(root: ASTNode, nodeid: number): ASTNode | null {
  function traverse(node: ASTNode): ASTNode | null {
    if (node.nodeid === nodeid) {
      return node;
    }
    if (node.children) {
      for (const child of node.children) {
        const result = traverse(child);
        if (result) return result;
      }
    }
    return null;
  }

  return traverse(root);
}

/**
 * Find the deepest node containing a given source position
 */
export function findNodeAtPosition(root: ASTNode, line: number, col: number): ASTNode | null {
  let best: ASTNode | null = null;

  function traverse(node: ASTNode) {
    if (node.nodeid == null) {
      // Skip nodes without nodeids (Text, etc.)
      if (node.children) {
        for (const child of node.children) traverse(child);
      }
      return;
    }
    const [startLine, startCol] = node.start_point;
    const [endLine, endCol] = node.end_point;
    const afterStart = line > startLine || (line === startLine && col >= startCol);
    const beforeEnd = line < endLine || (line === endLine && col <= endCol);
    if (afterStart && beforeEnd) {
      best = node;
      if (node.children) {
        for (const child of node.children) traverse(child);
      }
    }
  }

  traverse(root);
  return best;
}

/**
 * Extract all reference targets from the AST
 */
export function extractReferences(root: ASTNode): Array<{ node: ASTNode; target: string }> {
  const references: Array<{ node: ASTNode; target: string }> = [];

  function traverse(node: ASTNode) {
    // Check for Reference nodes or nodes with target property
    if (node.nodeclass === 'Reference' || node.nodeclass === 'Cite') {
      if (node.target && typeof node.target === 'string') {
        references.push({ node, target: node.target });
      }
    }
    if (node.children) {
      for (const child of node.children) {
        traverse(child);
      }
    }
  }

  traverse(root);
  return references;
}
