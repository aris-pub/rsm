import rsm
from rsm.nodes import (
    Paragraph,
    PendingReference,
    Proof,
    Reference,
    Span,
    Step,
    Subproof,
    Text,
)


def test_equality():
    s1, s2 = Step(), Step()
    assert s1 is not s2
    assert s1 == s2


def test_equality_different_number_ofchildren():
    s1, s2 = Step(), Step()
    s1.append(Paragraph())
    assert s1 is not s2
    assert s1 != s2


def test_equality_different_children():
    s1, s2 = Step(), Step()
    s1.append(Paragraph())
    s2.append(Subproof())
    assert s1 is not s2
    assert s1 != s2

    s2.prepend(Paragraph())
    assert s1 is not s2
    assert s1 != s2


def test_equality_different_parent():
    p = Proof()
    s1, s2 = Step(), Step()
    p.append(s1)
    assert s1 is not s2
    assert s1 != s2


def test_equal_to_self():
    pending = PendingReference(target="lbl")
    assert pending == pending


def test_replace_self():
    target = Paragraph(label="lbl")
    para = Paragraph()
    pending = PendingReference(target="lbl")
    para.append(Text("foo"))
    para.append(pending)
    para.append(Text("bar"))

    assert pending is para.children[1]
    assert pending == para.children[1]
    assert pending != para.children[0]
    assert pending != para.children[2]

    ref = Reference(target=target)
    assert pending.parent is para
    assert ref.parent is None
    pending.replace_self(ref)
    assert pending.parent is None
    assert ref.parent is para
    assert pending not in para.children
    assert ref is para.children[1]
    assert ref == para.children[1]


def test_append_order():
    parent = rsm.nodes.NodeWithChildren()
    parent.append([rsm.nodes.Text("1"), rsm.nodes.Text("2"), rsm.nodes.Text("3")])
    assert str(parent.children) == '(Text("1"), Text("2"), Text("3"))'


def test_prepend_order():
    parent = rsm.nodes.NodeWithChildren()
    parent.prepend([rsm.nodes.Text("1"), rsm.nodes.Text("2"), rsm.nodes.Text("3")])
    assert str(parent.children) == '(Text("1"), Text("2"), Text("3"))'


def test_set_parent_to_none():
    node = rsm.nodes.Step()
    node.parent = None


def test_first_of_type():
    p = Paragraph()
    t1, t2 = Text("one"), Text("two")
    p.append([t1, t2])
    assert t1 == p.first_of_type(Text)
    assert (t1, 0) == p.first_of_type(Text, return_idx=True)
    p.prepend(Span())
    assert t1 == p.first_of_type(Text)
    assert (t1, 1) == p.first_of_type(Text, return_idx=True)


def test_last_of_type():
    p = Paragraph()
    t1, t2 = Text("one"), Text("two")
    p.append([t1, t2])
    assert t2 == p.last_of_type(Text)
    assert (t2, 1) == p.last_of_type(Text, return_idx=True)
    p.prepend(Span())
    assert t2 == p.last_of_type(Text)
    assert (t1, 2) == p.last_of_type(Text, return_idx=True)


def test_prev_sibling():
    p, s, t1, t2 = Paragraph(), Span(), Text("one"), Text("two")
    p.append([t1, s, t2])
    assert t2.prev_sibling() is s
    assert t2.prev_sibling(Text) is t1
    assert t1.prev_sibling() is None


def test_pending_reference_internal():
    """Internal reference should have no external_file."""
    pending = PendingReference(target="my-label")
    assert pending.target_label == "my-label"
    assert pending.external_file is None


def test_pending_reference_external():
    """External reference should parse file path and label."""
    pending = PendingReference(target="definitions/def.rsm#my-label")
    assert pending.external_file == "definitions/def.rsm"
    assert pending.target_label == "my-label"


def test_pending_reference_external_relative_path():
    """External reference with relative path."""
    pending = PendingReference(target="../theorems/thm.rsm#theorem-label")
    assert pending.external_file == "../theorems/thm.rsm"
    assert pending.target_label == "theorem-label"


def test_pending_reference_external_nested_path():
    """External reference with nested directory path."""
    pending = PendingReference(target="math/algebra/groups.rsm#group-def")
    assert pending.external_file == "math/algebra/groups.rsm"
    assert pending.target_label == "group-def"


def test_pending_reference_backward_compat():
    """Ensure existing .target attribute still works for internal refs."""
    pending = PendingReference(target="simple-label")
    assert pending.target == "simple-label"


def test_reference_internal():
    """Internal reference should have no external_file."""
    target_node = Paragraph(label="target-label")
    ref = Reference(target=target_node, external_file=None)
    assert ref.target == target_node
    assert ref.external_file is None


def test_reference_external():
    """External reference should store external_file path."""
    target_node = Paragraph(label="target-label")
    ref = Reference(target=target_node, external_file="definitions/def.rsm")
    assert ref.target == target_node
    assert ref.external_file == "definitions/def.rsm"


def test_reference_external_with_path():
    """External reference with full path."""
    target_node = Paragraph(label="my-theorem")
    ref = Reference(target=target_node, external_file="../theorems/thm.rsm")
    assert ref.target == target_node
    assert ref.external_file == "../theorems/thm.rsm"
