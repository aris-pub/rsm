"""All tags available in RSM markup."""

from collections import namedtuple
from datetime import datetime
from pathlib import Path

############
# Block tags
############
BlockTagInfo = namedtuple("BlockTagInfo", ["shorthand"])

abstract = BlockTagInfo(None)
"""Manuscript abstract."""
algorithm = BlockTagInfo(None)
"""Algorithm listing."""
appendix = BlockTagInfo(None)
"""Mark where the appendix sections begin."""
author = BlockTagInfo(None)
"""Author information."""
bibliography = BlockTagInfo(None)
"""Automatically generate the list of references."""
bibtex = BlockTagInfo(None)
"""List of bibliography items."""
codeblock = BlockTagInfo(None)
"""Code listing."""
corollary = BlockTagInfo(None)
"""Corollary."""
definition = BlockTagInfo(None)
"""Definition."""
enumerate = BlockTagInfo(None)  # pylint: disable=redefined-builtin
"""Numbered list."""
example = BlockTagInfo(None)
"""Example."""
figure = BlockTagInfo(None)
"""Figure float."""
html = BlockTagInfo(None)
"""HTML asset."""
itemize = BlockTagInfo(None)
"""Unnumbered list."""
lemma = BlockTagInfo(None)
"""Lemma."""
mathblock = BlockTagInfo(None)
"""Math block (a.k.a. display math)."""
proof = BlockTagInfo(None)
"""Proof of Theorem."""
proposition = BlockTagInfo(None)
"""Proposition."""
remark = BlockTagInfo(None)
"""Remark."""
rsm = BlockTagInfo(None)
"""Top-level RSM tag."""
section = BlockTagInfo(None)
"""Section."""
sketch = BlockTagInfo(None)
"""Proof sketch."""
subsection = BlockTagInfo(None)
"""Subsection."""
subsubsection = BlockTagInfo(None)
"""Sub-subsection."""
theorem = BlockTagInfo(None)
"""Theorem."""
toc = BlockTagInfo(None)
"""Table of Contents"""
video = BlockTagInfo(None)
"""Video asset."""


################
# Paragraph tags
################
ParagraphTagInfo = namedtuple("ParagraphTagInfo", ["x"])

item = ParagraphTagInfo(None)
"""Item in enumerate or itemize."""
caption = ParagraphTagInfo(None)
"""Figure or table caption."""
paragraph = ParagraphTagInfo(None)
"""Generic paragraph.  Use when adding meta tags to a paragraph."""


#############
# Inline tags
#############
InlineTagInfo = namedtuple("InlineTagInfo", ["shorthand"])

code = InlineTagInfo(None)
"""Inline code."""
cite = InlineTagInfo(None)
"""Citation."""
claim = InlineTagInfo(None)
"""Mathematical claim."""
draft = InlineTagInfo(None)
"""A visible comment."""
math = InlineTagInfo(None)
"""Inline math."""
note = InlineTagInfo(None)
"""Footnote."""
ref = InlineTagInfo(None)
"""Link to internal label."""
span = InlineTagInfo(None)
"""Text span."""
url = InlineTagInfo(None)
"""Link to external URL."""


###########
# Meta tags
###########


MetaTagInfo = namedtuple("MetaTagInfo", ["parent", "type"])

affiliation = MetaTagInfo(None, datetime)
"""Author institutional affiliation."""
date = MetaTagInfo(None, datetime)
"""Manuscript date."""
email = MetaTagInfo(None, str)
"""Author email."""
emphas = MetaTagInfo(None, bool)
"""Whether span is emphasized."""
goal = MetaTagInfo(None, "?")
"""Theorem goal."""
icon = MetaTagInfo(None, list)
"""Icon assigned to the block."""
isclaim = MetaTagInfo(None, bool)
"""Whether a math block is a claim."""
keywords = MetaTagInfo(None, list)
"""Abstract keywords."""
label = MetaTagInfo(None, str)
"""Tag label."""
lang = MetaTagInfo(None, str)
"""Specify language in code and code blocks."""
msc = MetaTagInfo(None, list)
"""Mathematics Subject Classification."""
name = MetaTagInfo(None, str)
"""Author name."""
nonum = MetaTagInfo(None, bool)
"""Whether to number the tag."""
path = MetaTagInfo(None, Path)
"""Figure path."""
reftext = MetaTagInfo(None, str)
"""Label reftext."""
scale = MetaTagInfo(None, str)
"""Figure scale."""
strong = MetaTagInfo(None, bool)
"""Whether span is strong."""
title = MetaTagInfo(None, str)
"""Manuscript or section title."""
types = MetaTagInfo(None, list)
"""Tag types."""


###########
# Math tags
###########
MathTagInfo = namedtuple("MathTagInfo", ["shorthand"])

assume = MathTagInfo(None)
"""Introduce an assumption."""
case = MathTagInfo(None)
"""Prove special case of the goal."""
define = MathTagInfo(None)
"""Introduce a variable and assumption."""
exercise = MathTagInfo(None)
"""Introduce an exercise."""
let = MathTagInfo(None)
"""Introduce a variable and assumption."""
new = MathTagInfo(None)
"""Introduce a variable and assumption."""
p = MathTagInfo(None)
"""Sub-proof."""
pick = MathTagInfo(None)
"""Introduce a variable with a specific property (see 'st')."""
porism = MathTagInfo(None)
"""Corollary of a proof."""
prev = MathTagInfo(None)
"""Reference the previous step."""
prev2 = MathTagInfo(None)
"""Reference the step before last."""
prev3 = MathTagInfo(None)
"""Reference the step two steps before."""
previous = MathTagInfo(None)
"""Reference the previous step."""
problem = MathTagInfo(None)
"""Introduce a problem."""
prove = MathTagInfo(None)
"""Set goal."""
qed = MathTagInfo(None)
"""State the goal is proven."""
st = MathTagInfo(None)
"""'Such that', part of 'pick'."""
step = MathTagInfo(None)
"""Proof step."""
suffices = MathTagInfo(None)
"""Change goal."""
suppose = MathTagInfo(None)
"""Introduce an assumption."""
then = MathTagInfo(None)
"""State a claim under an assumption."""
wlog = MathTagInfo(None)
"""Without loss of generality (introduce an assupmtion)."""
write = MathTagInfo(None)
"""Introduce a symbol."""


############
# Table tags
############
TableTagInfo = namedtuple("TableTagInfo", ["shorthand"])

table = TableTagInfo(None)
"""Table."""
tbody = TableTagInfo(None)
"""Table body."""
td = TableTagInfo(None)
"""Table datum."""
thead = TableTagInfo(None)
"""Table head."""
tr = TableTagInfo(None)
"""Table row."""
