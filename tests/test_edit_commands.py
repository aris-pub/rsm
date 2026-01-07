from rsm import translator as tr


def test_edit_after_creation():
    cmd = tr.AppendOpenCloseTag(
        content="some content",
        classes=["foo"],
        newline_inner=False,
        newline_outer=False,
    )
    assert cmd.make_text() == '<div class="foo">some content</div>'

    cmd.classes.append("bar")
    assert cmd.make_text() == '<div class="foo bar">some content</div>'
