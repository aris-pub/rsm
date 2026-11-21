import { CompletionItem, CompletionItemKind, TextEdit, Range, Position } from 'vscode-languageserver';

/**
 * RSM tag definitions for completion.
 * The tag names must match the tags and meta keys in tree-sitter-rsm/grammar.js;
 * test/unit/layer1/completion.test.ts compares the two. Most descriptions come
 * from docs/rsm-agent-skill.md.
 */
const RSM_TAGS = [
  // Document structure
  { tag: ':section:', description: 'Section (closes when the next section begins)' },
  { tag: ':subsection:', description: 'Subsection' },
  { tag: ':subsubsection:', description: 'Subsubsection' },
  { tag: ':appendix:', description: 'Marks where appendix sections begin (stamp)' },
  { tag: ':paragraph:', description: 'Paragraph with inline meta' },
  { tag: ':config:', description: 'Document configuration' },
  { tag: ':toc:', description: 'Table of contents' },
  { tag: ':tabs:', description: 'Group of tabs, one shown at a time' },
  { tag: ':tab:', description: 'One tab of a :tabs:, with a :title:' },

  // Front matter
  { tag: ':author:', description: 'Author information block' },
  { tag: ':abstract:', description: 'Manuscript abstract' },

  // Theorem-like blocks
  { tag: ':theorem:', description: 'Theorem' },
  { tag: ':lemma:', description: 'Lemma' },
  { tag: ':corollary:', description: 'Corollary' },
  { tag: ':proposition:', description: 'Proposition' },
  { tag: ':porism:', description: 'Porism (corollary of a proof)' },
  { tag: ':definition:', description: 'Definition' },
  { tag: ':example:', description: 'Example' },
  { tag: ':exercise:', description: 'Exercise' },
  { tag: ':problem:', description: 'Problem' },
  { tag: ':remark:', description: 'Remark' },

  // Notes and asides
  { tag: ':note:', description: 'Footnote: call with :note:label::, define with :note: {:label: label} ... ::' },
  { tag: ':aside:', description: 'Aside: call with :aside:label,phrase::, define with :aside: {:label: label} ... ::' },

  // Proofs
  { tag: ':proof:', description: 'Proof' },
  { tag: ':sketch:', description: 'Proof sketch' },
  { tag: ':step:', description: 'Proof step (inside proofs)' },
  { tag: ':p:', description: 'Subproof (used inside steps)' },
  { tag: ':calc:', description: 'Calculation: a chain of relations, each a :step: with its reason' },

  // Proof constructs
  { tag: ':assume:', description: 'Introduce an assumption' },
  { tag: ':case:', description: 'Prove a special case of the goal' },
  { tag: ':claim:', description: 'State a mathematical claim' },
  { tag: ':define:', description: 'Introduce a variable and assumption' },
  { tag: ':let:', description: 'Introduce a variable and assumption' },
  { tag: ':new:', description: 'Introduce a variable and assumption' },
  { tag: ':pick:', description: 'Introduce a variable with a property (pair with :st:)' },
  { tag: ':prove:', description: 'Set the goal' },
  { tag: ':st:', description: 'Such that (follows :pick:)' },
  { tag: ':suffices:', description: 'Change the goal' },
  { tag: ':suppose:', description: 'Introduce an assumption' },
  { tag: ':then:', description: 'State a claim under an assumption' },
  { tag: ':wlog:', description: 'Without loss of generality' },
  { tag: ':write:', description: 'Introduce notation / a symbol' },
  { tag: ':qed:', description: 'State that the goal is proven (stamp)' },

  // References
  { tag: ':ref:', description: 'Internal cross-reference' },
  { tag: ':cite:', description: 'Bibliography citation' },
  { tag: ':url:', description: 'External hyperlink' },
  { tag: ':previous:', description: 'Reference a step by number' },
  { tag: ':prev:', description: 'Reference the previous step (stamp)' },
  { tag: ':prev2:', description: 'Reference the step before last (stamp)' },
  { tag: ':prev3:', description: 'Reference two steps before (stamp)' },

  // Math, code and other as-is content
  { tag: ':math:', description: 'Inline math (as-is content)' },
  { tag: ':mathblock:', description: 'Display math (as-is content)' },
  { tag: ':code:', description: 'Inline code (as-is content)' },
  { tag: ':codeblock:', description: 'Code listing (as-is content)' },
  { tag: ':algorithm:', description: 'Algorithm listing (as-is content)' },
  { tag: ':notation:', description: 'Notation macros that the reader can change, one per line' },
  { tag: ':html:', description: 'Inline raw HTML (as-is content)' },
  { tag: ':htmlblock:', description: 'A block of raw HTML (as-is content)' },

  // Figures and tables
  { tag: ':figure:', description: 'Figure float' },
  { tag: ':video:', description: 'Video asset' },
  { tag: ':table:', description: 'Table' },
  { tag: ':thead:', description: 'Table header rows' },
  { tag: ':tbody:', description: 'Table body rows' },
  { tag: ':tr:', description: 'Table row (short form: cells separated by :)' },
  { tag: ':td:', description: 'Table cell' },
  { tag: ':caption:', description: 'Figure/table caption (paragraph-level)' },

  // Lists
  { tag: ':itemize:', description: 'Unnumbered list' },
  { tag: ':enumerate:', description: 'Numbered list' },

  // Inline
  { tag: ':span:', description: 'Text span, for styling via meta or attaching a :label:' },
  { tag: ':draft:', description: 'Visible comment / draft note' },

  // Bibliography
  { tag: ':references:', description: 'Bibliography section' },

  // Meta keys with text values
  { tag: ':affiliation:', description: 'Author institutional affiliation' },
  { tag: ':alt:', description: 'Alt text for figure images; the fallback of :html: and :htmlblock:' },
  { tag: ':author-note:', description: 'Author note (e.g. "Equal contribution")' },
  { tag: ':blockname:', description: "Name a block is called by, in place of its type's name" },
  { tag: ':email:', description: 'Author email' },
  { tag: ':eyebrow:', description: 'Short label above the manuscript title' },
  { tag: ':goal:', description: 'Theorem goal' },
  { tag: ':icon:', description: 'Icon assigned to the block' },
  { tag: ':label:', description: 'Cross-reference label' },
  { tag: ':lang:', description: 'Language code (e.g. en, es)' },
  { tag: ':name:', description: 'Author name' },
  { tag: ':of:', description: 'Label of the result proved by a proof placed away from it' },
  { tag: ':orcid:', description: 'Author ORCID identifier' },
  { tag: ':reftext:', description: 'Label display text for references' },
  { tag: ':title:', description: 'Block or manuscript title' },

  // Boolean meta keys
  { tag: ':as-paragraph:', description: 'A figure, widget or video sits at the level of a paragraph: no number, no caption' },
  { tag: ':collapsed:', description: 'Handrail starts collapsed' },
  { tag: ':emphas:', description: 'Emphasized span' },
  { tag: ':isclaim:', description: 'Math block is a claim' },
  { tag: ':no-minimap:', description: 'Turn the minimap off' },
  { tag: ':nonum:', description: 'Suppress numbering' },
  { tag: ':preamble:', description: 'Math block holds macro definitions' },
  { tag: ':strong:', description: 'Bold span' },

  // List meta keys
  { tag: ':class:', description: 'CSS classes' },
  { tag: ':keywords:', description: 'Abstract keywords' },
  { tag: ':msc:', description: 'Mathematics Subject Classification' },

  // Meta keys with a path, number, word or date value
  { tag: ':accent:', description: 'Accent color (blue, red, green, orange, yellow, purple, pink, gray)' },
  { tag: ':author-display-first:', description: 'Authors shown at start when >5' },
  { tag: ':author-display-last:', description: 'Authors shown at end when >5' },
  { tag: ':citation-style:', description: 'Citation style (numeric or author-year)' },
  { tag: ':dark:', description: 'Dark-mode figure path' },
  { tag: ':numbering:', description: 'Numbering mode (document, section, none)' },
  { tag: ':orientation:', description: 'Table of contents tree orientation (horizontal, vertical)' },
  { tag: ':override-date:', description: 'Override manuscript date' },
  { tag: ':path:', description: 'Figure path' },
  { tag: ':scale:', description: 'Figure scale' },
  { tag: ':static:', description: 'Static/PDF export figure path' },
  { tag: ':toc-depth:', description: 'Table of contents depth' },
  { tag: ':typography:', description: 'Typography style (sans-serif, serif)' },
  { tag: ':view:', description: 'Default view of the table of contents (e.g. tree)' },
];

/**
 * Get completion items for RSM tags
 * Filters based on partial input if provided
 */
export function getTagCompletions(
  partialTag?: string,
  line?: number,
  startChar?: number,
  endChar?: number
): CompletionItem[] {
  let tags = RSM_TAGS;

  if (partialTag) {
    const lower = partialTag.toLowerCase();
    tags = tags.filter((t) => t.tag.toLowerCase().startsWith(lower));
  }

  return tags.map((t) => {
    const item: CompletionItem = {
      label: t.tag,
      kind: CompletionItemKind.Keyword,
      detail: t.description,
      sortText: t.tag,
    };

    // If position info provided, use textEdit to replace the partial tag
    if (line !== undefined && startChar !== undefined && endChar !== undefined) {
      item.textEdit = TextEdit.replace(
        Range.create(Position.create(line, startChar), Position.create(line, endChar)),
        t.tag
      );
    } else {
      item.insertText = t.tag;
    }

    return item;
  });
}

/**
 * Check if cursor is in a position where tag completion is appropriate
 * Returns the partial tag if applicable, null otherwise
 */
export function getPartialTag(line: string, character: number): string | null {
  // Check if we're after a colon
  const beforeCursor = line.substring(0, character);
  // Names in the grammar start with a letter and then use letters, digits and
  // hyphens. Requiring the letter first keeps ':-' (an item marker being typed)
  // and '::2' from counting as a partial tag.
  const match = beforeCursor.match(/:((?:[a-z][a-z0-9-]*)?)$/);
  return match ? `:${match[1]}` : null;
}
