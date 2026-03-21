"""Pandoc bridge for RSM: export and import.

Export direction: :class:`PandocTranslator` converts an RSM AST
(``nodes.Manuscript``) to a pandoc JSON AST dict, which pandoc then renders to
any supported output format (LaTeX, PDF, EPUB, DOCX, …).

Import direction: :class:`PandocImporter` converts a pandoc JSON AST dict
(produced by ``pandoc --to=json``) back to RSM source text.

Neither class calls pandoc directly; the subprocess invocations live in
:mod:`rsm.app`.  These classes only handle the RSM ↔ pandoc-JSON boundary.

Analogy with the rest of the codebase:

- ``Translator``: RSM AST → HTML string  (HTML is the final output, we own it)
- ``PandocTranslator``: RSM AST → pandoc JSON dict  (pandoc owns the final output)
- ``PandocImporter``: pandoc JSON dict → RSM source text  (we own the RSM text)
"""

import logging

from rsm import nodes

logger = logging.getLogger("RSM").getChild("pandoc")

PANDOC_API_VERSION = [1, 23, 1]


# ─── Export: RSM AST → pandoc JSON ───────────────────────────────────────────


class PandocTranslator:
    """Convert a ``nodes.Manuscript`` tree to a pandoc JSON AST dict.

    Usage::

        from rsm.pandoc import PandocTranslator
        ast = PandocTranslator().translate(manuscript)
        # ast is a dict ready to be json.dumps'd and piped to pandoc

    Note on :static:: when a :class:`~rsm.nodes.Figure` has a ``static``
    path set, that path is used as the image source instead of ``path``.
    This allows authors to provide a vector/high-res version for non-web
    export (e.g. PDF via LaTeX).
    """

    def translate(self, tree: nodes.Manuscript) -> dict:
        meta = self._build_meta(tree)
        blocks = self._walk_children_as_blocks(tree)
        return {"pandoc-api-version": PANDOC_API_VERSION, "meta": meta, "blocks": blocks}

    # ── Meta ──────────────────────────────────────────────────────────────────

    def _build_meta(self, node: nodes.Manuscript) -> dict:
        meta: dict = {}
        if node.title:
            meta["title"] = {"t": "MetaInlines", "c": [{"t": "Str", "c": node.title}]}
        authors = [c for c in node.children if isinstance(c, nodes.Author)]
        if authors:
            meta["author"] = {
                "t": "MetaList",
                "c": [
                    {"t": "MetaInlines", "c": [{"t": "Str", "c": a.name}]}
                    for a in authors
                    if a.name
                ],
            }
        if node.date:
            date_str = (
                node.date.date().isoformat()
                if hasattr(node.date, "date")
                else str(node.date)
            )
            meta["date"] = {"t": "MetaInlines", "c": [{"t": "Str", "c": date_str}]}
        return meta

    # ── Block walker ──────────────────────────────────────────────────────────

    # Maps node type → method name.  Uses MRO: if a type is not listed,
    # the first ancestor that IS listed wins.  None means "skip silently".
    _BLOCK_DISPATCH: dict = {
        nodes.Section: "_block_section",       # Subsection, Subsubsection via MRO
        nodes.Paragraph: "_block_paragraph",   # Step via MRO; Note handled inline
        nodes.MathBlock: "_block_mathblock",
        nodes.CodeBlock: "_block_codeblock",
        nodes.Enumerate: "_block_enumerate",
        nodes.Itemize: "_block_itemize",
        nodes.Item: "_block_item",
        nodes.Theorem: "_block_theorem",       # all Theorem subclasses via MRO
        nodes.Proof: "_block_proof",
        nodes.Sketch: "_block_proof",          # Sketch is NOT a subclass of Proof
        nodes.Figure: "_block_figure",
        nodes.Table: "_block_table",
        nodes.Bibliography: "_block_bibliography",
        nodes.Abstract: "_block_abstract",
        nodes.Author: None,     # consumed by _build_meta
        nodes.AuthorBlock: None, # consumed by _build_meta
        nodes.AuthorNotes: None, # consumed by _build_meta
        nodes.Appendix: None,   # marker only, no output
        nodes.Caption: None,    # consumed inside _block_figure / _block_table
        nodes.Draft: None,
        nodes.Algorithm: None,
        nodes.Contents: "_block_toc",
        nodes.Html: "_block_asset_placeholder",
        nodes.Video: "_block_asset_placeholder",
        nodes.Subproof: "_block_proof",       # same as Proof — recurse into children
        nodes.ClaimBlock: "_block_construct",
        nodes.Construct: "_block_construct",
        nodes.Statement: "_block_construct",
    }

    def _walk_block(self, node: nodes.Node) -> list[dict]:
        for cls in type(node).__mro__:
            if cls in self._BLOCK_DISPATCH:
                method_name = self._BLOCK_DISPATCH[cls]
                if method_name is None:
                    return []
                return getattr(self, method_name)(node)
        return self._block_fallback(node)

    def _walk_children_as_blocks(self, node: nodes.Node) -> list[dict]:
        result: list[dict] = []
        for child in node.children:
            result.extend(self._walk_block(child))
        return result

    # ── Inline walker ─────────────────────────────────────────────────────────

    _INLINE_DISPATCH: dict = {
        nodes.Text: "_inline_text",
        nodes.SourceCode: "_inline_sourcecode",  # raw text inside Math nodes
        nodes.Span: "_inline_span",              # Keyword via MRO
        nodes.Math: "_inline_math",
        nodes.Code: "_inline_code",
        nodes.Reference: "_inline_reference",
        nodes.URL: "_inline_url",
        nodes.Cite: "_inline_cite",
        nodes.Note: "_inline_note",
        nodes.Error: "_inline_text",
    }

    def _walk_inline(self, node: nodes.Node) -> list[dict]:
        for cls in type(node).__mro__:
            if cls in self._INLINE_DISPATCH:
                method_name = self._INLINE_DISPATCH[cls]
                if method_name is None:
                    return []
                return getattr(self, method_name)(node)
        return self._inline_fallback(node)

    def _walk_children_as_inlines(self, node: nodes.Node) -> list[dict]:
        result: list[dict] = []
        for child in node.children:
            result.extend(self._walk_inline(child))
        return result

    # ── Block handlers ────────────────────────────────────────────────────────

    def _block_fallback(self, node: nodes.Node) -> list[dict]:
        logger.warning("PandocTranslator: no block handler for %s", type(node).__name__)
        return []

    def _block_section(self, node: nodes.Section) -> list[dict]:
        level = node.__class__.level
        anchor = node.label or ""
        num = node.full_number
        prefix = f"{num}. " if num and not node.nonum else ""
        title_inlines = [{"t": "Str", "c": f"{prefix}{node.title}"}] if node.title else []
        header = {"t": "Header", "c": [level, [anchor, [], []], title_inlines]}
        return [header] + self._walk_children_as_blocks(node)

    def _block_abstract(self, node: nodes.Abstract) -> list[dict]:
        header = {
            "t": "Header",
            "c": [3, ["abstract", [], []], [{"t": "Str", "c": "Abstract"}]],
        }
        inner = self._walk_children_as_blocks(node)
        result = [header] + inner
        if node.keywords:
            kw_text = "Keywords: " + ", ".join(node.keywords)
            result.append({"t": "Para", "c": [{"t": "Str", "c": kw_text}]})
        return result

    def _block_paragraph(self, node: nodes.Paragraph) -> list[dict]:
        # A Paragraph may contain block-level MathBlock / CodeBlock children.
        # Split at each such child: flush accumulated inlines as Para, emit the block.
        _BLOCK_IN_PARA = (nodes.MathBlock, nodes.CodeBlock)
        result: list[dict] = []
        current_inlines: list[dict] = []
        for child in node.children:
            if isinstance(child, _BLOCK_IN_PARA):
                if current_inlines:
                    result.append({"t": "Para", "c": current_inlines})
                    current_inlines = []
                result.extend(self._walk_block(child))
            else:
                current_inlines.extend(self._walk_inline(child))
        if current_inlines:
            result.append({"t": "Para", "c": current_inlines})
        return result

    def _block_mathblock(self, node: nodes.MathBlock) -> list[dict]:
        src = self._extract_math_source(node)
        return [{"t": "Para", "c": [{"t": "Math", "c": [{"t": "DisplayMath"}, src]}]}]

    def _block_codeblock(self, node: nodes.CodeBlock) -> list[dict]:
        src = self._extract_code_source(node)
        lang = [node.lang] if node.lang else []
        return [{"t": "CodeBlock", "c": [["", lang, []], src]}]

    def _block_enumerate(self, node: nodes.Enumerate) -> list[dict]:
        # _walk_block(item) dispatches to _block_item → [Para(inlines)]; each item
        # in pandoc OrderedList is a list of blocks, so the result is [[Para], ...].
        items = [
            self._walk_block(child)
            for child in node.children
            if isinstance(child, nodes.Item)
        ]
        list_attrs = [1, {"t": "Decimal"}, {"t": "Period"}]
        return [{"t": "OrderedList", "c": [list_attrs, items]}]

    def _block_itemize(self, node: nodes.Itemize) -> list[dict]:
        items = [
            self._walk_block(child)
            for child in node.children
            if isinstance(child, nodes.Item)
        ]
        return [{"t": "BulletList", "c": items}]

    def _block_item(self, node: nodes.Item) -> list[dict]:
        inlines = self._walk_children_as_inlines(node)
        return [{"t": "Para", "c": inlines}] if inlines else []

    def _block_theorem(self, node: nodes.Theorem) -> list[dict]:
        classname = type(node).__name__.lower()
        num = node.full_number
        num_str = f" {num}" if num else ""
        title_str = f": {node.title}" if node.title else "."
        label_text = f"{type(node).__name__}{num_str}{title_str}"
        label_para = {
            "t": "Para",
            "c": [{"t": "Strong", "c": [{"t": "Str", "c": label_text}]}],
        }
        anchor = node.label or ""
        inner = self._walk_children_as_blocks(node)
        # Wrap in raw Typst block with left border for PDF styling
        raw_open = {"t": "RawBlock", "c": ["typst", f'#block(stroke: (left: 1.5pt + rgb("#075487")), inset: (top: 6pt, bottom: 6pt), outset: (left: 14pt), width: 100%)[']}
        raw_close = {"t": "RawBlock", "c": ["typst", "]"]}
        label_block = [{"t": "RawBlock", "c": ["typst", f'<{anchor}>']}] if anchor and " " not in anchor else []
        return label_block + [raw_open, label_para] + inner + [raw_close]

    def _block_proof(self, node: nodes.Proof) -> list[dict]:
        label = "Proof sketch." if isinstance(node, nodes.Sketch) else "Proof."
        label_para = {
            "t": "Para",
            "c": [{"t": "Emph", "c": [{"t": "Strong", "c": [{"t": "Str", "c": label}]}]}],
        }
        inner = self._walk_children_as_blocks(node)
        # Proof: no border, just italic label + Halmos square at end
        halmos = {"t": "RawBlock", "c": ["typst", '#v(-0.8em)\n#align(right, box(width: 6pt, height: 6pt, fill: rgb("#027AC7")))']}
        return [label_para] + inner + [halmos]

    def _block_figure(self, node: nodes.Figure) -> list[dict]:
        # Use :static: path for non-web export when available
        path = str(node.static) if node.static else str(node.path)
        alt_text = node.alt or f"Figure {node.full_number or ''}".strip()
        image = {"t": "Image", "c": [["", [], []], [{"t": "Str", "c": alt_text}], [path, ""]]}

        caption_node = node.first_of_type(nodes.Caption)
        if caption_node:
            cap_inlines = self._walk_children_as_inlines(caption_node)
            caption = [None, [{"t": "Para", "c": cap_inlines}]]
        else:
            caption = [None, []]

        anchor = node.label or ""
        return [{
            "t": "Figure",
            "c": [[anchor, ["figure"], []], caption, [{"t": "Plain", "c": [image]}]],
        }]

    def _block_toc(self, node) -> list[dict]:
        # Emit raw Typst outline instead of a bullet list
        return [{"t": "RawBlock", "c": ["typst", "#outline(indent: auto)"]}]

    def _block_asset_placeholder(self, node: nodes.Node) -> list[dict]:
        kind = type(node).__name__
        path = getattr(node, "path", "")
        text = f"[{kind} asset: {path} — see online version]" if path else f"[{kind} — see online version]"
        return [{"t": "Para", "c": [{"t": "Emph", "c": [{"t": "Str", "c": text}]}]}]

    def _block_construct(self, node: nodes.Node) -> list[dict]:
        return self._walk_children_as_blocks(node)

    def _block_bibliography(self, node: nodes.Bibliography) -> list[dict]:
        header = {
            "t": "Header",
            "c": [2, ["references", [], []], [{"t": "Str", "c": "References"}]],
        }
        items = [
            [self._format_bibitem(child)]
            for child in node.children
            if isinstance(child, nodes.Bibitem)
        ]
        if not items:
            return [header]
        bib_list = {
            "t": "OrderedList",
            "c": [[1, {"t": "Decimal"}, {"t": "Period"}], items],
        }
        return [header, bib_list]

    def _format_bibitem(self, node: nodes.Bibitem) -> dict:
        parts = []
        if node.author:
            parts.append(node.author)
        if node.title:
            parts.append(f'"{node.title}"')
        if node.journal:
            parts.append(node.journal)
        if node.year and node.year != -1:
            parts.append(str(node.year))
        text = ". ".join(p.strip(".") for p in parts) + "." if parts else "?"
        anchor = f"ref-{node.label}" if node.label else ""
        inlines: list[dict] = [{"t": "Str", "c": text}]
        # Add DOI or URL as a clickable link
        link_url = None
        if getattr(node, "doi", None):
            link_url = f"https://doi.org/{node.doi}" if not node.doi.startswith("http") else node.doi
        elif getattr(node, "url", None):
            link_url = str(node.url)
        if link_url:
            inlines.append({"t": "Space"})
            inlines.append({"t": "Link", "c": [["", [], []], [{"t": "Str", "c": link_url}], [link_url, ""]]})
        return {"t": "Div", "c": [[anchor, [], []], [{"t": "Para", "c": inlines}]]}

    def _block_table(self, node: nodes.Table) -> list[dict]:
        head = node.first_of_type(nodes.TableHead)
        body = node.first_of_type(nodes.TableBody)
        head_rows = self._table_rows(head) if head else []
        body_rows = self._table_rows(body) if body else []

        all_rows = head_rows + body_rows
        col_count = max(
            (len(r["c"][1]) for r in all_rows),
            default=1,
        ) if all_rows else 1
        col_specs = [["AlignDefault", {"t": "ColWidthDefault"}] for _ in range(col_count)]

        caption_node = node.first_of_type(nodes.Caption)
        if caption_node:
            cap_inlines = self._walk_children_as_inlines(caption_node)
            caption = [None, [{"t": "Para", "c": cap_inlines}]]
        else:
            caption = [None, []]

        return [{"t": "Table", "c": [
            ["", [], []],
            caption,
            col_specs,
            {"t": "TableHead", "c": [["", [], []], head_rows]},
            [{"t": "TableBody", "c": [["", [], []], 0, [], body_rows]}],
            {"t": "TableFoot", "c": [["", [], []], []]},
        ]}]

    def _table_rows(self, node: nodes.NodeWithChildren) -> list[dict]:
        rows = []
        for row in node.children:
            if not isinstance(row, nodes.TableRow):
                continue
            cells = []
            for cell in row.children:
                if isinstance(cell, nodes.TableDatum):
                    inlines = self._walk_children_as_inlines(cell)
                    cells.append({
                        "t": "Cell",
                        "c": [
                            ["", [], []],
                            {"t": "AlignDefault"},
                            1, 1,
                            [{"t": "Plain", "c": inlines}],
                        ],
                    })
            rows.append({"t": "Row", "c": [["", [], []], cells]})
        return rows

    # ── Inline handlers ───────────────────────────────────────────────────────

    def _inline_fallback(self, node: nodes.Node) -> list[dict]:
        logger.warning("PandocTranslator: no inline handler for %s", type(node).__name__)
        return []

    def _inline_text(self, node: nodes.Text) -> list[dict]:
        if not node.text:
            return []
        result: list[dict] = []
        parts = node.text.split(" ")
        for i, word in enumerate(parts):
            if word:
                result.append({"t": "Str", "c": word})
            if i < len(parts) - 1:
                result.append({"t": "Space"})
        return result

    def _inline_sourcecode(self, node: nodes.SourceCode) -> list[dict]:
        # SourceCode children appear inside Math nodes; emit their raw text.
        return [{"t": "Str", "c": node.text}] if node.text else []

    def _inline_span(self, node: nodes.Span) -> list[dict]:
        inlines = self._walk_children_as_inlines(node)
        if node.strong:
            inlines = [{"t": "Strong", "c": inlines}]
        if node.emphas:
            inlines = [{"t": "Emph", "c": inlines}]
        if node.delete:
            inlines = [{"t": "Strikeout", "c": inlines}]
        if node.little:
            inlines = [{"t": "SmallCaps", "c": inlines}]
        if node.insert:
            inlines = [{"t": "Span", "c": [["", ["inserted"], []], inlines]}]
        return inlines

    def _inline_math(self, node: nodes.Math) -> list[dict]:
        src = self._extract_math_source(node)
        return [{"t": "Math", "c": [{"t": "InlineMath"}, src]}]

    def _inline_code(self, node: nodes.Code) -> list[dict]:
        src = self._extract_code_source(node)
        lang = [node.lang] if node.lang else []
        return [{"t": "Code", "c": [["", lang, []], src]}]

    def _inline_reference(self, node: nodes.Reference) -> list[dict]:
        if node.target is None:
            return []
        text = node.overwrite_reftext or (
            node.target.reftext if hasattr(node.target, "reftext") else str(node.target)
        )
        anchor = (
            f"#{node.target.label}"
            if hasattr(node.target, "label") and node.target.label
            else "#"
        )
        return [{"t": "Link", "c": [["", [], []], [{"t": "Str", "c": text}], [anchor, ""]]}]

    def _inline_url(self, node: nodes.URL) -> list[dict]:
        target = str(node.target)
        display = node.overwrite_reftext or target
        return [{"t": "Link", "c": [["", [], []], [{"t": "Str", "c": display}], [target, ""]]}]

    def _inline_cite(self, node: nodes.Cite) -> list[dict]:
        if not node.targets:
            return []
        # Render as clickable links [N] pointing to bibliography entries.
        result: list[dict] = [{"t": "Str", "c": "["}]
        for i, tgt in enumerate(node.targets):
            if i > 0:
                result.append({"t": "Str", "c": ", "})
            num = getattr(tgt, "number", None)
            label = tgt.label if hasattr(tgt, "label") and tgt.label else ""
            if num is not None and not isinstance(num, str):
                display = str(num)
            elif label:
                display = label
            else:
                display = "?"
            if label:
                anchor = f"#ref-{label}"
                result.append({"t": "Link", "c": [["", [], []], [{"t": "Str", "c": display}], [anchor, ""]]})
            else:
                result.append({"t": "Str", "c": display})
        result.append({"t": "Str", "c": "]"})
        return result

    def _inline_note(self, node: nodes.Note) -> list[dict]:
        inlines = self._walk_children_as_inlines(node)
        return [{"t": "Note", "c": [{"t": "Para", "c": inlines}]}]

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _extract_math_source(self, node: nodes.Node) -> str:
        return "".join(
            c.text
            for c in node.children
            if isinstance(c, (nodes.Text, nodes.SourceCode))
        ).strip()

    def _extract_code_source(self, node: nodes.Node) -> str:
        # In a parsed RSM document, the SourceCode is a child of Code/CodeBlock.
        # When nodes are created programmatically, the text is in node.source.text.
        src_child = node.first_of_type(nodes.SourceCode)
        if src_child is not None:
            return src_child.text
        if hasattr(node, "source") and node.source:
            return node.source.text
        return ""


# ─── Import: pandoc JSON → RSM source text ───────────────────────────────────


class PandocImporter:
    """Convert a pandoc JSON AST dict to RSM source text.

    The input is the JSON produced by ``pandoc --to=json``.  The output is
    valid RSM markup that can be parsed by the RSM toolchain.

    Usage::

        import json, subprocess
        proc = subprocess.run(
            ["pandoc", "--from=markdown", "--to=json"],
            input=markdown_text, capture_output=True, text=True,
        )
        rsm_text = PandocImporter().from_json(json.loads(proc.stdout))
    """

    def from_json(self, pandoc_ast: dict) -> str:
        meta = pandoc_ast.get("meta", {})
        blocks = pandoc_ast.get("blocks", [])
        parts = [self._render_meta(meta)]
        parts += [self._render_block(b) for b in blocks]
        return "".join(p for p in parts if p)

    # ── Meta ──────────────────────────────────────────────────────────────────

    def _render_meta(self, meta: dict) -> str:
        parts: list[str] = []
        if "title" in meta:
            title = self._meta_to_text(meta["title"])
            if title:
                parts.append(f"# {title}\n\n")
        if "author" in meta:
            for item in meta["author"].get("c", []):
                name = self._meta_to_text(item)
                if name:
                    parts.append(f":author: {{\n  :name: {name}\n}} ::\n\n")
        return "".join(parts)

    def _meta_to_text(self, val: dict) -> str:
        t = val.get("t", "")
        c = val.get("c", [])
        if t == "MetaInlines":
            return self._render_inlines(c)
        if t == "MetaList":
            return " ".join(self._meta_to_text(item) for item in c)
        if t == "MetaString":
            return str(c)
        return ""

    # ── Block rendering ───────────────────────────────────────────────────────

    def _render_block(self, block: dict) -> str:
        t = block.get("t", "")
        c = block.get("c", [])
        method = getattr(self, f"_block_{t.lower()}", None)
        if method is not None:
            return method(c)
        logger.warning("PandocImporter: no handler for block type '%s'", t)
        return ""

    def _block_header(self, c: list) -> str:
        level, _attrs, inlines = c
        text = self._render_inlines(inlines)
        prefix = "#" * level
        return f"{prefix} {text}\n\n"

    def _block_para(self, c: list) -> str:
        # DisplayMath inside Para inlines must be flushed as a block construct.
        result: list[str] = []
        pending: list[dict] = []
        for inline in c:
            if (
                inline.get("t") == "Math"
                and isinstance(inline.get("c"), list)
                and len(inline["c"]) >= 1
                and inline["c"][0].get("t") == "DisplayMath"
            ):
                if pending:
                    text = self._render_inlines(pending)
                    if text:
                        result.append(f"{text}\n\n")
                    pending = []
                src = inline["c"][1] if len(inline["c"]) >= 2 else ""
                result.append(f":mathblock:\n  {src}\n::\n\n")
            else:
                pending.append(inline)
        if pending:
            text = self._render_inlines(pending)
            if text:
                result.append(f"{text}\n\n")
        return "".join(result)

    def _block_plain(self, c: list) -> str:
        # Pandoc uses Plain (no trailing newline) in list items and table cells.
        text = self._render_inlines(c)
        return text if text else ""

    def _block_bulletlist(self, c: list) -> str:
        items: list[str] = []
        for item_blocks in c:
            text = "".join(self._render_block(b).strip() for b in item_blocks)
            items.append(f"  :-: {text}")
        return ":itemize:\n\n" + "\n\n".join(items) + "\n\n::\n\n"

    def _block_orderedlist(self, c: list) -> str:
        _list_attrs, item_list = c
        items: list[str] = []
        for item_blocks in item_list:
            text = "".join(self._render_block(b).strip() for b in item_blocks)
            items.append(f"  :-: {text}")
        return ":enumerate:\n\n" + "\n\n".join(items) + "\n\n::\n\n"

    def _block_codeblock(self, c: list) -> str:
        attrs, code = c
        _id, classes, _kv = attrs
        lang = classes[0] if classes else ""
        meta = f" {{:lang: {lang}}}" if lang else ""
        indented = "\n".join("  " + line for line in code.splitlines())
        return f":codeblock:{meta}\n{indented}\n::\n\n"

    def _block_rawblock(self, c: list) -> str:
        fmt, raw = c
        if fmt == "latex":
            indented = "\n".join("  " + line for line in raw.strip().splitlines())
            return f":mathblock:\n{indented}\n::\n\n"
        logger.warning("PandocImporter: skipping RawBlock with format '%s'", fmt)
        return ""

    def _block_horizontalrule(self, c: list) -> str:
        return ""  # No RSM equivalent; silently skip

    def _block_blockquote(self, c: list) -> str:
        inner = "".join(self._render_block(b) for b in c)
        indented = "\n".join("  " + line for line in inner.splitlines() if line)
        return f"{indented}\n\n"

    def _block_div(self, c: list) -> str:
        attrs, blocks = c
        _id, classes, _kv = attrs
        inner = "".join(self._render_block(b) for b in blocks).strip()
        # Map well-known classes to RSM constructs
        for cls in classes:
            if cls == "proof":
                return f":proof:\n\n{inner}\n\n::\n\n"
            if cls in ("theorem", "lemma", "corollary", "example", "exercise",
                       "proposition", "problem"):
                return f":{cls}:\n\n{inner}\n\n::\n\n"
        # Unknown Div: emit inner content directly
        return f"{inner}\n\n" if inner else ""

    def _block_figure(self, c: list) -> str:
        _attrs, caption_obj, content_blocks = c
        path = ""
        for block in content_blocks:
            if block.get("t") == "Plain":
                for inline in block.get("c", []):
                    if inline.get("t") == "Image":
                        path = inline["c"][2][0]
        caption_text = ""
        if caption_obj and isinstance(caption_obj.get("c"), list):
            cap_blocks = caption_obj["c"][1] if len(caption_obj["c"]) >= 2 else []
            if cap_blocks:
                caption_text = "".join(
                    self._render_block(b).strip() for b in cap_blocks
                )
        caption_line = f"\n  :caption: {caption_text}" if caption_text else ""
        return f":figure: {{:path: {path}}}{caption_line}\n::\n\n"

    def _block_table(self, _c: list) -> str:
        logger.warning("PandocImporter: table import not yet implemented")
        return ""

    def _block_lineblock(self, c: list) -> str:
        lines = [self._render_inlines(line) for line in c]
        return "\n".join(lines) + "\n\n"

    # ── Inline rendering ──────────────────────────────────────────────────────

    def _render_inlines(self, inlines: list) -> str:
        return "".join(self._render_inline(i) for i in inlines)

    def _render_inline(self, inline: dict) -> str:
        t = inline.get("t", "")
        c = inline.get("c", [])
        method = getattr(self, f"_inline_{t.lower()}", None)
        if method is not None:
            return method(c)
        logger.warning("PandocImporter: no handler for inline type '%s'", t)
        return ""

    def _inline_str(self, c) -> str:
        return c

    def _inline_space(self, c) -> str:
        return " "

    def _inline_softbreak(self, c) -> str:
        return " "

    def _inline_linebreak(self, c) -> str:
        return "\n\n"

    def _inline_emph(self, c: list) -> str:
        return f"*{self._render_inlines(c)}*"

    def _inline_strong(self, c: list) -> str:
        return f"**{self._render_inlines(c)}**"

    def _inline_strikeout(self, c: list) -> str:
        return f":span: {{:delete:}} {self._render_inlines(c)} ::"

    def _inline_smallcaps(self, c: list) -> str:
        return f":span: {{:little:}} {self._render_inlines(c)} ::"

    def _inline_code(self, c: list) -> str:
        attrs, code = c
        _id, classes, _kv = attrs
        lang = classes[0] if classes else ""
        meta = f" {{:lang: {lang}}}" if lang else ""
        return f":code:{meta} {code} ::"

    def _inline_math(self, c: list) -> str:
        math_type, src = c
        # DisplayMath inside inlines is handled by _block_para; this is a fallback.
        return f":math: {src} ::"

    def _inline_link(self, c: list) -> str:
        _attrs, _inlines, target = c
        url = target[0]
        return f":url: {url} ::"

    def _inline_image(self, c: list) -> str:
        _attrs, _alt, target = c
        path = target[0]
        return f":figure: {{:path: {path}}}\n::"

    def _inline_cite(self, c: list) -> str:
        citations, _fallback = c
        return "".join(f":cite:{cite['citationId']}::" for cite in citations)

    def _inline_note(self, c: list) -> str:
        inner = "".join(self._render_block(b).strip() for b in c)
        return f":note: {inner} ::"

    def _inline_rawinline(self, c: list) -> str:
        fmt, raw = c
        if fmt == "latex":
            return f":math: {raw} ::"
        logger.warning("PandocImporter: skipping RawInline with format '%s'", fmt)
        return ""

    def _inline_span(self, c: list) -> str:
        _attrs, inlines = c
        return self._render_inlines(inlines)

    def _inline_quoted(self, c: list) -> str:
        quote_type, inlines = c
        text = self._render_inlines(inlines)
        return f"'{text}'" if quote_type.get("t") == "SingleQuote" else f'"{text}"'

    def _inline_superscript(self, c: list) -> str:
        return self._render_inlines(c)

    def _inline_subscript(self, c: list) -> str:
        return self._render_inlines(c)
