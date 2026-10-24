import re
from pathlib import Path

import rsm.tags

ROOT_DIR = Path(__file__).parent.parent
GRAMMAR_FILE = ROOT_DIR / "tree-sitter-rsm/grammar.js"
TAGS_FILE = ROOT_DIR / "rsm/tags.py"


def extract_grammar_tags():
    with open(GRAMMAR_FILE) as f:
        contents = f.read()
    tags = set(re.findall(r":([\w-]+):", contents))
    tags = {tag.replace("-", "_") for tag in tags}
    # :-:, :--:, :---: are the list item depth markers, not traditional tags;
    # they all share the node type 'item'. (:----: appears in a grammar comment
    # as the unsupported 4th level.) Drop every all-underscore marker.
    tags = {tag for tag in tags if set(tag) != {"_"}}
    tags.add("item")
    return tags


def extract_documented_tags():
    tags = {
        t
        for t in dir(rsm.tags)
        if isinstance(
            getattr(rsm.tags, t),
            rsm.tags.BlockTagInfo
            | rsm.tags.InlineTagInfo
            | rsm.tags.MathTagInfo
            | rsm.tags.MetaTagInfo
            | rsm.tags.ParagraphTagInfo
            | rsm.tags.TableTagInfo,
        )
    }
    # Special case: class_ in Python -> class in grammar
    if "class_" in tags:
        tags.remove("class_")
        tags.add("class")
    return tags


def test_all_tags_are_documented():
    grammar_tags = extract_grammar_tags()
    documented_tags = extract_documented_tags()
    assert grammar_tags == documented_tags


def test_theorem_like_tags_render_their_own_name():
    import rsm

    for tag, name in [("problem", "Problem"), ("exercise", "Exercise"),
                      ("porism", "Porism")]:
        src = f"# T\n\n:{tag}:\n  Some content.\n::\n"
        h = rsm.render(src, handrails=False, source_offsets=False)
        assert name in h, (tag, h)
        assert "Theorem" not in h, (tag, h)
