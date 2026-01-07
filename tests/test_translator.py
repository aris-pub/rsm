import rsm


def test_translator_starts_anew_each_time():
    text = rsm.nodes.Text("foo")
    tr = rsm.translator.Translator()
    assert tr.translate(text) == "foo"
    assert tr.translate(text) == "foo"
