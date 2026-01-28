import { CompletionItem, CompletionItemKind } from 'vscode-languageserver';

/**
 * RSM tag definitions for completion
 * Extracted from rsm/tags.py
 */
const RSM_TAGS = [
  // Document structure
  { tag: ':manuscript:', description: 'Document root' },
  { tag: ':section:', description: 'Section' },
  { tag: ':subsection:', description: 'Subsection' },
  { tag: ':subsubsection:', description: 'Subsubsection' },

  // Mathematical constructs
  { tag: ':theorem:', description: 'Theorem statement' },
  { tag: ':lemma:', description: 'Lemma statement' },
  { tag: ':corollary:', description: 'Corollary statement' },
  { tag: ':proposition:', description: 'Proposition statement' },
  { tag: ':conjecture:', description: 'Conjecture statement' },
  { tag: ':definition:', description: 'Definition' },
  { tag: ':example:', description: 'Example' },
  { tag: ':remark:', description: 'Remark' },
  { tag: ':note:', description: 'Note' },

  // Proof constructs
  { tag: ':proof:', description: 'Proof block' },
  { tag: ':claim:', description: 'Claim within proof' },
  { tag: ':step:', description: 'Proof step' },
  { tag: ':p:', description: 'Justification for claim/step' },
  { tag: ':qed:', description: 'End of proof' },
  { tag: ':let:', description: 'Variable introduction' },
  { tag: ':assume:', description: 'Assumption' },
  { tag: ':st:', description: 'Such that (with :pick:)' },
  { tag: ':pick:', description: 'Choose element' },

  // References
  { tag: ':ref:', description: 'Reference to labeled element' },
  { tag: ':cite:', description: 'Citation reference' },
  { tag: ':eqref:', description: 'Equation reference' },

  // Figures and tables
  { tag: ':figure:', description: 'Figure' },
  { tag: ':table:', description: 'Table' },
  { tag: ':caption:', description: 'Caption for figure/table' },

  // Lists
  { tag: ':itemize:', description: 'Unordered list' },
  { tag: ':enumerate:', description: 'Ordered list' },
  { tag: ':item:', description: 'List item' },

  // Front matter
  { tag: ':title:', description: 'Document title' },
  { tag: ':author:', description: 'Author' },
  { tag: ':date:', description: 'Date' },
  { tag: ':abstract:', description: 'Abstract' },

  // Bibliography
  { tag: ':references:', description: 'Bibliography section' },
  { tag: ':bibitem:', description: 'Bibliography entry' },

  // Inline constructs
  { tag: ':emph:', description: 'Emphasis (italic)' },
  { tag: ':strong:', description: 'Strong emphasis (bold)' },
  { tag: ':code:', description: 'Inline code' },
  { tag: ':url:', description: 'URL link' },

  // Special
  { tag: ':draft:', description: 'Draft marker' },
  { tag: ':todo:', description: 'TODO marker' },
];

/**
 * Get completion items for RSM tags
 * Filters based on partial input if provided
 */
export function getTagCompletions(partialTag?: string): CompletionItem[] {
  let tags = RSM_TAGS;

  if (partialTag) {
    const lower = partialTag.toLowerCase();
    tags = tags.filter((t) => t.tag.toLowerCase().startsWith(lower));
  }

  return tags.map((t) => ({
    label: t.tag,
    kind: CompletionItemKind.Keyword,
    detail: t.description,
    insertText: t.tag,
    sortText: t.tag,
  }));
}

/**
 * Check if cursor is in a position where tag completion is appropriate
 * Returns the partial tag if applicable, null otherwise
 */
export function getPartialTag(line: string, character: number): string | null {
  // Check if we're after a colon
  const beforeCursor = line.substring(0, character);
  const match = beforeCursor.match(/:([a-z]*)$/);
  return match ? `:${match[1]}` : null;
}
