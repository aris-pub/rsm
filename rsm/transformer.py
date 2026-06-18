"""Input: abstract syntax tree -- Output: (transformed) abstract syntax tree.

The transform step is essential for the processing of the manuscript.  For exmaple,
references and citations are resolved during this time.

The transform step is also responsible for 'fixing up' some syntactic sugar afforded by
RSM markup to yield a sound manuscript.  For exmaple, for mathematical proofs, it is
possible to have a sequence of ``:step:`` tags inside a parent ``:step:``.  However, in
the final manuscript, those sub-steps will be wrapped by a :class:`rsm.nodes.SubProof`
node, without the user having to manually create a ``:p:`` tag.  This wrapper node is
created during the transform step.

After the transform step, static analysis tools such as the linter may run over the
manuscript.

The convention is that the manuscript will not be modified for any reason after the
transform step is done.  **This is currently not enforced**, but merely a convention,
though it must at all times be followed.

The transform step is carried out by :class:`Transformer`, which simply executes in
sequence a number of routines that are all independent from each other.  Since the task
of each such routine is to modify the manuscript tree, the order in which they take
place is of utmost importance.

"""

import logging
import re
from collections import defaultdict
from collections.abc import Generator
from itertools import count
from pathlib import Path
from string import ascii_uppercase

from . import nodes

logger = logging.getLogger("RSM").getChild("tform")


class RSMTransformerError(Exception):
    pass


class Transformer:
    """Apply transformations to the abstract syntax tree.

    A transformation is any operation on the manuscript tree that modifies its
    structure.  This class keeps a register of transformations and applies them in
    sequence.  Order of application is of the utmost importance since each transform
    modifies the tree in some way.

    Notes
    -----
    If an operation is being carried out not to transform the tree, but merely to check
    it in some way, consider implementing it as a linter operation instead.

    Examples
    --------
    Consider the following manuscript.

    >>> src = \"\"\"
    ... Here comes a :span:{:label:lbl} word :: with a label,
    ... and a reference to the :ref:lbl,word::.
    ... \"\"\"

    The transform step comes after the parsing step.  After parsing, the manuscript
    looks as follows.

    >>> parser = rsm.tsparser.TSParser()
    >>> sans_transform = parser.parse(src)
    >>> print(sans_transform.sexp())
    (Manuscript
      (Paragraph
        (Text)
        (Span
          (Text))
        (Text)
        (PendingReference)
        (Text)))

    The :class:`rsm.nodes.PendingReference` node is created as a placeholder.  One can
    inspect its desired target.

    >>> sans_transform.children[0].children[3].target
    'lbl'

    The target is the string ``'lbl'``.  Note this is the label of the target node.

    After the transform step, the tree is modified and the reference is resolved.

    >>> tform = rsm.transformer.Transformer()
    >>> with_transform = tform.transform(sans_transform)
    >>> print(with_transform.sexp())
    (Manuscript
      (Paragraph
        (Text)
        (Span
          (Text))
        (Text)
        (Reference)
        (Text)))

    Accordingly, its target is now no longer a string, but the actual node.

    >>> with_transform.children[0].children[3].target
    Span(label=lbl, parent=Paragraph, [Text])

    """

    def __init__(
        self,
        root_dir: Path | None = None,
        src_file: Path | None = None,
        strict: bool = False,
        parser=None,
    ) -> None:
        self.tree: nodes.Manuscript | None = None
        self.labels_to_nodes: dict[str, nodes.Node] = {}
        self.root_dir = root_dir
        self.src_file = src_file
        self.external_manuscripts: dict[str, tuple[nodes.Manuscript, dict]] = {}
        self.strict = strict
        self.parser = parser

    def transform(self, tree: nodes.Manuscript) -> nodes.Manuscript:
        """Transform a manuscript tree.

        For examples see class docstring.

        Parameters
        ----------
        tree
            Manuscript tree to be transformed.

        Returns
        -------
        tree
            The transformed tree.  All transformations occur in place.

        Notes
        -----
        *tree* is stored as ``self.tree``.

        """
        logger.info("Transforming...")
        self.tree = tree

        self.collect_labels()
        self.parse_notation()
        self.resolve_pending_references()
        self.assign_author_affiliations()
        self.assign_author_note_symbols()
        self.build_author_block()
        self.add_necessary_subproofs()
        self.autonumber_nodes()
        self.make_toc()
        self.make_proof_trees()
        self.add_keywords_to_constructs()
        self.add_handrail_depth()
        self.assign_node_ids()
        self.make_proof_state()
        self.check_for_cst_errors()
        return tree

    def _load_external_manuscript(
        self, filepath: str
    ) -> tuple[nodes.Manuscript, dict[str, nodes.Node]]:
        """Load and parse an external RSM file.

        Parameters
        ----------
        filepath
            Path to external RSM file, relative to root_dir

        Returns
        -------
        tuple
            (manuscript, labels_to_nodes dict)

        Raises
        ------
        ValueError
            If root_dir is not set
        FileNotFoundError
            If the file doesn't exist
        """
        # Check cache first
        if filepath in self.external_manuscripts:
            return self.external_manuscripts[filepath]

        # Validate root_dir is set
        if self.root_dir is None:
            raise ValueError("root_dir must be set to load external manuscripts")

        # Resolve filepath relative to root_dir
        full_path = self.root_dir / filepath

        # Check file exists
        if not full_path.exists():
            raise FileNotFoundError(f"External manuscript not found: {full_path}")

        # Parse external file using ParserApp
        from .app import ParserApp

        app = ParserApp(srcpath=full_path)
        app.run()

        # Extract manuscript and labels
        manuscript = app.transformer.tree
        labels_map = app.transformer.labels_to_nodes.copy()

        # Cache the result
        result = (manuscript, labels_map)
        self.external_manuscripts[filepath] = result

        return result

    def check_for_cst_errors(self) -> None:
        """Check the concrete syntax tree for parse errors.

        Walks the CST (not the AST) because some ERROR nodes may not survive
        the abstractify step if they are nested inside node types not in
        PUSH_THESE_TYPES.

        Raises
        ------
        RSMTransformerError
            If strict mode is enabled and ERROR nodes are present in the CST.
        """
        if not self.strict:
            return
        if not self.parser or not self.parser.cst:
            return

        error_nodes = []

        def _find_errors(node):
            if node.type == "ERROR":
                error_nodes.append(node)
            for child in node.children:
                _find_errors(child)

        _find_errors(self.parser.cst.root_node)

        if error_nodes:
            error_messages = []
            for node in error_nodes:
                start = node.start_point
                end = node.end_point
                error_messages.append(
                    f"  - ({start[0]}, {start[1]}) - ({end[0]}, {end[1]}): {node.text.decode('utf-8', errors='replace') if node.text else 'unknown error'}"
                )

            error_summary = "\n".join(error_messages)
            raise RSMTransformerError(
                f"Strict mode enabled: CST errors detected in manuscript:\n{error_summary}"
            )

    def collect_labels(self) -> None:
        """Find all nodes with labels.

        Find all nodes with a non-empty *label* attribute and build a label-to-node
        mapping.  This mapping is later used by other transforms.

        Warnings
        --------
        If two nodes with the same label are found, only the first node is assigned the
        label and the second (and later, if any) nodes' labels are erased and ignored.

        Notes
        -----
        This transform does not actually modify the tree, but is necessary for the
        execution of other transforms that may modify it.  Therefore, this must be
        executed before all other ones.

        """
        for node in self.tree.traverse(condition=lambda n: n.label):
            if node.label in self.labels_to_nodes:
                logger.warning(f"Duplicate label {node.label}, using first encountered")
                node.label = ""
                continue
            self.labels_to_nodes[node.label] = node

    def _label_to_node(
        self, label: str, external_file: str | None = None, default=nodes.Error
    ) -> nodes.Node:
        # Handle external file references
        if external_file:
            try:
                manuscript, labels_map = self._load_external_manuscript(external_file)
                if not label:
                    return manuscript
                try:
                    return labels_map[label]
                except KeyError:
                    logger.warning(
                        f'Label "{label}" not found in external file "{external_file}"'
                    )
                    return default(f'[unknown label "{label}" in "{external_file}"]')
            except (ValueError, FileNotFoundError) as e:
                logger.warning(f'Failed to load external file "{external_file}": {e}')
                return default(f'[error loading "{external_file}": {e}]')

        # Handle internal references (existing behavior)
        try:
            return self.labels_to_nodes[label]
        except KeyError:
            logger.warning(f'Reference to nonexistent label "{label}"')
            return default(f'[unknown label "{label}"]')

    def resolve_pending_references(self) -> None:
        classes = [
            nodes.PendingReference,
            nodes.PendingCite,
            nodes.PendingPrev,
        ]

        counter = count()
        for pending in self.tree.traverse(condition=lambda n: type(n) in classes):
            if isinstance(pending, nodes.PendingReference):
                target = self._label_to_node(
                    pending.target_label, external_file=pending.external_file
                )
                if isinstance(target, nodes.Error):
                    pending.replace_self(target)
                else:
                    ext_ms = None
                    if pending.external_file and pending.target_label:
                        try:
                            ext_ms, _ = self._load_external_manuscript(
                                pending.external_file
                            )
                        except Exception:
                            pass
                    pending.replace_self(
                        nodes.Reference(
                            target=target,
                            external_file=pending.external_file,
                            external_manuscript=ext_ms,
                            overwrite_reftext=pending.overwrite_reftext,
                        )
                    )
            elif isinstance(pending, nodes.PendingCite):
                targets = [
                    self._label_to_node(label, default=nodes.UnknownBibitem)
                    for label in pending.targetlabels
                ]
                cite = nodes.Cite(targets=targets, targetlabels=list(pending.targetlabels))
                cite.label = f"cite-{next(counter)}"
                pending.replace_self(cite)
                for tgt in targets:
                    tgt.backlinks.append(cite.label)
            elif isinstance(pending, nodes.PendingPrev):
                try:
                    step = pending.first_ancestor_of_type(nodes.Step)
                except AttributeError:
                    step = None
                if step is None:
                    raise RSMTransformerError("Found :prev: tag outside proof step")

                target = step
                for _ in range(int(str(pending.target))):
                    target = target.prev_sibling(nodes.Step)
                    if target is None:
                        raise RSMTransformerError(
                            f"Did not find previous {pending.target} step(s)"
                        )

                if target.label is None or not target.label.strip():
                    logger.warning(
                        ":prev: references un-labeled step, link will not work"
                    )
                pending.replace_self(
                    nodes.Reference(
                        target=target, overwrite_reftext=pending.overwrite_reftext
                    )
                )

        for _pending in self.tree.traverse(condition=lambda n: type(n) in classes):
            raise RSMTransformerError("Found unresolved pending reference")

    def assign_author_affiliations(self) -> None:
        """Deduplicate affiliations and assign superscript numbers to authors.

        This transform iterates through all Author nodes and:
        1. Collects unique affiliations in order of first appearance
        2. Assigns a number (1, 2, 3, ...) to each unique affiliation
        3. Sets the affiliation_number attribute on each Author node
        4. Stores the total count of unique affiliations on the Manuscript node

        Authors with the same affiliation text get the same number.
        Authors without an affiliation get affiliation_number = None.

        Examples
        --------
        Two authors with the same affiliation get the same number:

        >>> from rsm import nodes
        >>> from rsm.transformer import Transformer
        >>> tree = nodes.Manuscript()
        >>> a1 = nodes.Author(name="Alice", affiliation="MIT")
        >>> a2 = nodes.Author(name="Bob", affiliation="MIT")
        >>> _ = tree.append(a1).append(a2)
        >>> tform = Transformer()
        >>> tform.tree = tree
        >>> tform.assign_author_affiliations()
        >>> a1.affiliation_number
        1
        >>> a2.affiliation_number
        1

        """
        affiliation_map: dict[str, int] = {}
        next_num = 1

        for author in self.tree.traverse(
            condition=lambda n: isinstance(n, nodes.Author)
        ):
            if author.affiliation:
                if author.affiliation not in affiliation_map:
                    affiliation_map[author.affiliation] = next_num
                    next_num += 1
                author.affiliation_number = affiliation_map[author.affiliation]

        self.tree.total_unique_affiliations = len(affiliation_map)

    def assign_author_note_symbols(self) -> None:
        r"""Assign symbols (\*, †, ‡, §, ¶, ‖, \*\*, ††, ...) to author notes.

        This transform iterates through all Author nodes and:
        1. Collects unique note texts in order of first appearance
        2. Assigns a symbol to each unique note
        3. Sets the note_symbol attribute on each Author node
        4. Stores the total count of unique notes on the Manuscript node

        Symbol progression: \*, †, ‡, §, ¶, ‖, \*\*, ††, ‡‡, §§, ¶¶, ‖‖, \*\*\*, †††, ...

        Authors with the same note text get the same symbol.
        Authors without a note get note_symbol = "".

        Examples
        --------
        Two authors with the same note get the same symbol:

        >>> from rsm import nodes
        >>> from rsm.transformer import Transformer
        >>> tree = nodes.Manuscript()
        >>> a1 = nodes.Author(name="Alice", author_note="Equal contribution")
        >>> a2 = nodes.Author(name="Bob", author_note="Equal contribution")
        >>> _ = tree.append(a1).append(a2)
        >>> tform = Transformer()
        >>> tform.tree = tree
        >>> tform.assign_author_note_symbols()
        >>> a1.note_symbol
        '*'
        >>> a2.note_symbol
        '*'

        """
        SYMBOLS = ["*", "†", "‡", "§", "¶", "‖"]

        # Collect unique notes in order of appearance
        note_map: dict[str, str] = {}
        symbol_idx = 0

        for author in self.tree.traverse(
            condition=lambda n: isinstance(n, nodes.Author)
        ):
            if author.author_note and author.author_note not in note_map:
                # Assign next symbol
                if symbol_idx < len(SYMBOLS):
                    symbol = SYMBOLS[symbol_idx]
                else:
                    # Generate repeated symbols: **, ††, ‡‡, etc.
                    base_idx = (symbol_idx - len(SYMBOLS)) % len(SYMBOLS)
                    repeat_count = ((symbol_idx - len(SYMBOLS)) // len(SYMBOLS)) + 2
                    symbol = SYMBOLS[base_idx] * repeat_count

                note_map[author.author_note] = symbol
                symbol_idx += 1

        # Assign symbols to all authors
        for author in self.tree.traverse(
            condition=lambda n: isinstance(n, nodes.Author)
        ):
            if author.author_note:
                author.note_symbol = note_map[author.author_note]

        self.tree.total_unique_notes = len(note_map)

    def build_author_block(self) -> None:
        """Create an AuthorBlock node containing all Authors and an AuthorNotes child."""
        all_authors = list(
            self.tree.traverse(condition=lambda n: isinstance(n, nodes.Author))
        )
        authors = [
            a for a in all_authors
            if a.name or a.affiliation or a.email or a.orcid or a.author_note
        ]
        if not authors:
            return

        affiliation_map: dict[str, int] = {}
        for author in authors:
            if author.affiliation and author.affiliation_number is not None:
                affiliation_map[author.affiliation] = author.affiliation_number

        note_map: dict[str, str] = {}
        for author in authors:
            if author.author_note and author.note_symbol:
                note_map[author.author_note] = author.note_symbol

        emails = [(a.name, a.email) for a in authors if a.email]
        orcids = [(a.name, a.orcid) for a in authors if a.orcid]

        block = nodes.AuthorBlock()

        for author in authors:
            author.parent.remove(author)
            block.append(author)

        notes = nodes.AuthorNotes(
            affiliation_map=affiliation_map,
            note_map=note_map,
            emails=emails,
            orcids=orcids,
        )
        block.append(notes)

        self.tree.prepend(block)

    def add_necessary_subproofs(self) -> None:
        for step in self.tree.traverse(nodeclass=nodes.Step):
            if not step.children:
                continue

            _, split_at_idx = step.first_of_type(
                (nodes.Step, nodes.Subproof), return_idx=True
            )
            if split_at_idx is None:
                split_at_idx = len(step.children)

            children = step.children[::]
            step.clear()

            statement = nodes.Statement()
            statement.append(children[:split_at_idx])
            statement.handrail_depth += 1

            if split_at_idx == len(children):
                step.append(statement)
                continue

            if isinstance(children[split_at_idx], nodes.Step):
                subproof = nodes.Subproof()
                subproof.append(children[split_at_idx:])
            elif isinstance(children[split_at_idx], nodes.Subproof):
                assert split_at_idx == len(children) - 1
                subproof = children[split_at_idx]
            else:
                raise RSMTransformerError("How did we get here?")
            step.append([statement, subproof])

    def autonumber_nodes(self) -> None:
        counts: dict[type[nodes.Node], dict[type[nodes.Node], Generator]] = defaultdict(
            lambda: defaultdict(lambda: count(start=1))
        )
        within_appendix = False

        # Check manuscript numbering config
        numbering_mode = getattr(self.tree, 'numbering', 'section')  # default to 'section'

        for node in self.tree.traverse():
            if isinstance(node, nodes.Appendix):
                counts[nodes.Manuscript][nodes.Section] = iter(ascii_uppercase)
                within_appendix = True
                continue
            if isinstance(node, nodes.Proof | nodes.Subproof):
                self._autonumber_steps(node)
                continue
            if isinstance(node, nodes.Step):
                continue

            if node.autonumber and not node.nonum:
                # Apply numbering mode from config
                if numbering_mode == 'none':
                    # Don't assign numbers when numbering is none
                    node.nonum = True
                    continue
                elif numbering_mode == 'document':
                    # Number within manuscript (1, 2, 3...)
                    number_within = nodes.Manuscript
                else:
                    # Default to section numbering (1.1, 1.2, 2.1...)
                    number_within = node.number_within

                # Override node's number_within for full_number property
                if numbering_mode == 'document':
                    node._number_within_override = nodes.Manuscript

                counts[type(node)] = defaultdict(lambda: count(start=1))
                num = next(counts[number_within][node.number_as])
                node.number = num
                if within_appendix and isinstance(node, nodes.Section):
                    node.reftext_template = node.reftext_template.replace(
                        "{nodeclass}", "Appendix"
                    )

    def _autonumber_steps(self, proof: nodes.Proof) -> None:
        step_gen = (s for s in proof.children if isinstance(s, nodes.Step))
        for idx, step in enumerate(step_gen, start=1):
            step.number = idx

    def make_toc(self) -> None:
        toc = None
        for node in self.tree.traverse(nodeclass=nodes.Contents):
            if toc is None:
                toc = node
            else:
                logger.warning("Multiple Tables of Content found, using only first one")
                node.remove_self()
        if toc is None:
            return

        # :toc: is a standard block grammatically, but its contents are
        # auto-generated here; author-written content is not allowed.
        if toc.children:
            logger.warning("The :toc: tag takes no content; discarding it")
            for child in list(toc.children):
                child.remove_self()

        # Compute cross-section reference edges before creating the TOC's own
        # Reference nodes, so they are not counted as edges themselves.
        self._compute_toc_edges(toc)

        current_parent = toc
        for sec in self.tree.traverse(nodeclass=nodes.Section):
            item = nodes.Item()
            reftext = f"{sec.title}" if sec.nonum else f"{sec.full_number}. {sec.title}"
            item.append(nodes.Reference(target=sec, overwrite_reftext=reftext))

            # The order of the `if isinstance(...)` statements here matters because all
            # Subsections are also Sections so isinstance(sec, nodes.Section) evaluates
            # to True even when sec is a Subsection.  Thus, we have to go from smallest
            # (Subsubsection) to largest (Section).
            if isinstance(sec, nodes.Subsubsection):
                current_parent.append(item)
                if sec.parent.last_of_type(nodes.Subsubsection) is sec:
                    current_parent = current_parent.parent.parent
            elif isinstance(sec, nodes.Subsection):
                current_parent.append(item)
                if sec.first_of_type(nodes.Subsubsection):
                    itemize = nodes.Itemize()
                    item.append(itemize)
                    current_parent = itemize
                elif sec.parent.last_of_type(nodes.Subsection) is sec:
                    current_parent = current_parent.parent.parent
            elif isinstance(sec, nodes.Section):
                toc.append(item)
                if sec.first_of_type(nodes.Subsection):
                    itemize = nodes.Itemize()
                    item.append(itemize)
                    current_parent = itemize
            else:
                raise RSMTransformerError("How did we get here?")

    def _compute_toc_edges(self, toc: nodes.Contents) -> None:
        """Derive cross-section reference edges for the TOC tree view.

        Each resolved Reference contributes an edge between the nearest
        enclosing Section of its location and that of its target (the target
        itself when it is a Section). Intra-section references are dropped,
        parallel references collapse into a count, and references to an
        earlier section are dependencies ("dep") while references to a later
        section are forward pointers ("fwd").
        """
        # Unnumbered sections (a colophon, say) are back-matter and stay out
        # of the table of contents.
        sections = [
            sec
            for sec in self.tree.traverse(nodeclass=nodes.Section)
            if not sec.nonum
        ]
        row_of = {id(sec): row for row, sec in enumerate(sections)}

        def depth_of(sec: nodes.Section) -> int:
            if isinstance(sec, nodes.Subsubsection):
                return 3
            if isinstance(sec, nodes.Subsection):
                return 2
            return 1

        toc.tree_nodes = [
            {
                "num": "" if sec.nonum else str(sec.full_number),
                "title": sec.title,
                "label": sec.label or "",
                "depth": depth_of(sec),
            }
            for sec in sections
        ]
        toc.tree_root_title = self.tree.title or "Document"

        def nearest_section(node: nodes.Node) -> nodes.Section | None:
            # first_ancestor_of_type matches exact types by design; here the
            # nearest enclosing TOC entry of ANY section level is wanted.
            ancestor = node.parent
            while ancestor is not None and not isinstance(ancestor, nodes.Section):
                ancestor = ancestor.parent
            return ancestor

        counts: dict[tuple[int, int], int] = {}
        for ref in self.tree.traverse(nodeclass=nodes.Reference):
            src = nearest_section(ref)
            target = ref.target
            if isinstance(target, nodes.Section):
                dst = target
            elif isinstance(target, nodes.Node):
                dst = nearest_section(target)
            else:
                dst = None
            if src is None or dst is None or src is dst:
                continue
            # A reference touching an unnumbered (out-of-TOC) section has no row.
            if id(src) not in row_of or id(dst) not in row_of:
                continue
            key = (row_of[id(src)], row_of[id(dst)])
            counts[key] = counts.get(key, 0) + 1

        toc.toc_edges = [
            {
                "src": s,
                "dst": d,
                "count": c,
                "kind": "dep" if d < s else "fwd",
            }
            for (s, d), c in sorted(counts.items())
        ]

    def make_proof_trees(self) -> None:
        for proof in self.tree.traverse(nodeclass=nodes.Proof):
            self._compute_proof_tree(proof)

    def _compute_proof_tree(self, proof: nodes.Proof) -> None:
        """Per-proof step DAG for the floating proof-tree, mirroring the TOC.

        Nodes are the proof's steps in document order; edges are references
        from one step to another step OF THE SAME PROOF (containment edges and
        the root are added by the renderer, as for the TOC). Cross-proof and
        external references are dropped: the tree is scoped to one proof.
        """
        steps = list(proof.traverse(nodeclass=nodes.Step))
        if not steps:
            return
        row_of = {id(s): i for i, s in enumerate(steps)}

        def step_depth(step: nodes.Step) -> int:
            d = 1
            anc = step.parent
            while anc is not None and anc is not proof:
                if isinstance(anc, nodes.Step):
                    d += 1
                anc = anc.parent
            return d

        def nearest_step(node: nodes.Node) -> nodes.Step | None:
            anc = node.parent
            while anc is not None and anc is not proof:
                if isinstance(anc, nodes.Step):
                    return anc
                anc = anc.parent
            return None

        proof.tree_nodes = [
            {
                "num": str(s.full_number),
                "title": self._step_title(s),
                "label": s.label or "",
                "depth": step_depth(s),
            }
            for s in steps
        ]
        proof.tree_root_title = self._proof_root_title(proof)

        counts: dict[tuple[int, int], int] = {}
        for ref in proof.traverse(nodeclass=nodes.Reference):
            target = ref.target
            if not isinstance(target, nodes.Step) or id(target) not in row_of:
                continue
            src = nearest_step(ref)
            if src is None or src is target:
                continue
            key = (row_of[id(src)], row_of[id(target)])
            counts[key] = counts.get(key, 0) + 1

        proof.tree_edges = [
            {"src": s, "dst": d, "count": c, "kind": "dep" if d < s else "fwd"}
            for (s, d), c in sorted(counts.items())
        ]

    @staticmethod
    def _step_title(step: nodes.Step) -> str:
        """Short text of a step's own claim, excluding nested sub-steps."""
        parts: list[str] = []

        def walk(node: nodes.Node) -> None:
            for child in node.children:
                if isinstance(child, nodes.Step):
                    continue
                if isinstance(child, nodes.Text):
                    parts.append(child.text)
                elif isinstance(child, nodes.NodeWithChildren):
                    walk(child)

        walk(step)
        text = " ".join(" ".join(parts).split())
        return text[:90]

    @staticmethod
    def _proof_root_title(proof: nodes.Proof) -> str:
        """The result a proof establishes, used as its tree's root label."""
        sib = proof.prev_sibling()
        theorem_types = (
            nodes.Theorem,
            nodes.Lemma,
            nodes.Corollary,
            nodes.Proposition,
            nodes.Definition,
            nodes.Remark,
            nodes.Statement,
        )
        while sib is not None:
            if isinstance(sib, theorem_types):
                return sib.reftext or "Statement"
            sib = sib.prev_sibling()
        # No theorem precedes this proof (e.g. several proofs of one result, each
        # under its own subsection): fall back to the enclosing heading's title.
        anc = proof.parent
        while anc is not None and not isinstance(anc, nodes.Section):
            anc = anc.parent
        if anc is not None and getattr(anc, "title", ""):
            return anc.title
        return "Statement"

    _NOTATION_LINE = re.compile(r"^\s*(\\[A-Za-z]+)\s*\$(.+?)\$\s*(.*?)\s*$")

    def parse_notation(self) -> None:
        """Parse each :notation: block's raw lines into entries:
        `\\macro $default$ label` -> {macro, default, label}."""
        for notn in self.tree.traverse(nodeclass=nodes.Notation):
            text_node = next(iter(notn.traverse(nodeclass=nodes.Text)), None)
            if text_node is None:
                continue
            entries = []
            for line in text_node.text.splitlines():
                if not line.strip():
                    continue
                m = self._NOTATION_LINE.match(line)
                if not m:
                    logger.warning(f"Unparseable :notation: line: {line!r}")
                    continue
                entries.append(
                    {"macro": m.group(1), "default": m.group(2).strip(),
                     "label": m.group(3).strip()}
                )
            notn.entries = entries
            # the raw lines are now captured in `entries`; drop them so they
            # don't render as literal text.
            notn.clear()

    def make_proof_state(self) -> None:
        """Per-step `hypotheses |- goal` for the rail's State view (runs after
        node ids are assigned, since it records construct node ids to clone)."""
        for proof in self.tree.traverse(nodeclass=nodes.Proof):
            self._compute_proof_state(proof)

    HYP_KINDS = ("let", "assume")
    GOAL_KINDS = ("claim", "claimblock")

    def _compute_proof_state(self, proof: nodes.Proof) -> None:
        steps = list(proof.traverse(nodeclass=nodes.Step))
        if not steps:
            return

        def nearest_step(node: nodes.Node) -> nodes.Step | None:
            anc = node.parent
            while anc is not None and anc is not proof:
                if isinstance(anc, nodes.Step):
                    return anc
                anc = anc.parent
            return None

        def own_constructs(container: nodes.Node, kinds: tuple) -> list:
            # constructs of the given kinds belonging directly to `container`
            # (not to a nested step); for the theorem container, all of them.
            out = []
            is_step = isinstance(container, nodes.Step)
            for c in container.traverse(nodeclass=nodes.Construct):
                if c.kind not in kinds:
                    continue
                if not is_step or nearest_step(c) is container:
                    out.append(c)
            return out

        def ancestors(step: nodes.Step) -> list:  # outermost first
            chain = [step]
            anc = step.parent
            while anc is not None and anc is not proof:
                if isinstance(anc, nodes.Step):
                    chain.append(anc)
                anc = anc.parent
            chain.reverse()
            return chain

        def preceding_step_siblings(step: nodes.Step) -> list:  # document order
            # A let/assume introduced by a step stays in scope for every later
            # step at the same level (Lamport), so a later step's hypotheses
            # include those of all its preceding step siblings.
            out = []
            sib = step.prev_sibling(nodes.Step)
            while sib is not None:
                out.append(sib)
                sib = sib.prev_sibling(nodes.Step)
            out.reverse()
            return out

        theorem = proof.prev_sibling()
        thm_types = (
            nodes.Theorem, nodes.Lemma, nodes.Corollary,
            nodes.Proposition, nodes.Statement,
        )
        while theorem is not None and not isinstance(theorem, thm_types):
            theorem = theorem.prev_sibling()
        # Theorem hypotheses have no step number (they precede the proof).
        base_hyps = (
            [{"id": c.nodeid, "num": None} for c in own_constructs(theorem, self.HYP_KINDS)]
            if theorem is not None else []
        )

        state = []
        for s in steps:
            chain = ancestors(s)
            hyps = list(base_hyps)
            for anc in chain:
                # Preceding siblings at this level are in scope, then the
                # ancestor's own let/assume.
                for sib in preceding_step_siblings(anc):
                    snum = str(sib.full_number)
                    hyps += [
                        {"id": c.nodeid, "num": snum}
                        for c in own_constructs(sib, self.HYP_KINDS)
                    ]
                num = str(anc.full_number)
                hyps += [
                    {"id": c.nodeid, "num": num}
                    for c in own_constructs(anc, self.HYP_KINDS)
                ]
            goal = None
            for anc in reversed(chain):  # innermost first
                claims = own_constructs(anc, self.GOAL_KINDS)
                if claims:
                    goal = {"id": claims[0].nodeid, "num": str(anc.full_number)}
                    break
            # A setup step with no claim of its own is working toward the
            # theorem; show its conclusion as the goal.
            if goal is None and theorem is not None:
                goal = {"id": theorem.nodeid, "num": theorem.reftext or None, "thm": True}
            state.append({"goal": goal, "hyps": hyps})
        proof.step_state = state

    def add_keywords_to_constructs(self) -> None:
        for construct in self.tree.traverse(nodeclass=nodes.Construct):
            kind = construct.kind
            assert kind
            construct.classes.append(kind)
            if kind not in {"then", "suffices", "claim", "claimblock", "qed", "prove"}:
                construct.classes.append("assumption")

    def add_handrail_depth(self) -> None:
        for nc in nodes.all_node_subtypes():
            if nc.has_handrail:
                self._add_handrail_depth_for_class(nc)

    def _add_handrail_depth_for_class(self, nodeclass) -> None:
        for node in self.tree.traverse(nodeclass=nodeclass):
            for desc in node.traverse():
                if desc == node:
                    continue
                desc.handrail_depth += 1

    def assign_node_ids(self) -> None:
        nodeid = 0
        for node in self.tree.traverse():
            if isinstance(node, (nodes.AuthorBlock, nodes.AuthorNotes)):
                continue
            node.nodeid = nodeid
            nodeid += 1
