import re
from pathlib import Path

import rsm.tags

ROOT_DIR = Path(__file__).parent.parent
GRAMMAR_FILE = ROOT_DIR / "tree-sitter-rsm/grammar.js"
TAGS_FILE = ROOT_DIR / "rsm/tags.py"


def extract_grammar_tags():
    with open(GRAMMAR_FILE) as f:
        contents = f.read()
    tags = set(re.findall(r":(\w+):", contents))
    return tags


def extract_documented_tags():
    tags = {
        t
        for t in dir(rsm.tags)
        if isinstance(
            getattr(rsm.tags, t),
            (
                rsm.tags.BlockTagInfo,
                rsm.tags.InlineTagInfo,
                rsm.tags.MathTagInfo,
                rsm.tags.MetaTagInfo,
                rsm.tags.ParagraphTagInfo,
                rsm.tags.TableTagInfo,
            ),
        )
    }
    return tags


def test_all_tags_are_documented():
    grammar_tags = extract_grammar_tags()
    documented_tags = extract_documented_tags()
    assert grammar_tags == documented_tags
