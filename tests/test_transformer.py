import pytest
from conftest import compare_have_want

import rsm


def test_duplicate_label_warning(caplog):
    compare_have_want(
        have="""\
        :rsm:
          :title: Title

        There are :span: {:label: mylbl} two :: spans with the :span: {:label: mylbl}
        same :: label in this paragraph.

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>There are <span id="mylbl" class="span" data-nodeid="3">two</span> spans with the <span class="span" data-nodeid="6">same</span> label in this paragraph.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
    assert "Duplicate label mylbl" in caplog.text


def test_duplicate_bibtex_item_warning(caplog):
    compare_have_want(
        have="""\
        :rsm:

        :bibliography: ::

        ::


        :bibtex:

        @article{torres2020,
          title={Nonbacktracking eigenvalues under node removal: X-centrality and targeted immunization},
          author={Torres, Leo and Chan, Kevin S and Tong, Hanghang and Eliassi-Rad, Tina},
          journal={SIAM Journal on Mathematics of Data Science},
          year={2021},
        }

        @book{torres2020,
          title={Foo},
          author={Bar},
          journal={Baz},
          year={Bug},
        }

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="1">

        <li id="torres2020" class="bibitem" data-nodeid="2">
        1. Torres, Leo and Chan, Kevin S and Tong, Hanghang and Eliassi-Rad, Tina. "Nonbacktracking eigenvalues under node removal: X-centrality and targeted immunization". SIAM Journal on Mathematics of Data Science. 2021.
        </li>

        <li class="bibitem" data-nodeid="3">
        2. Bar. "Foo". Bug.
        </li>

        </ol>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )
    assert "Duplicate label torres2020" in caplog.text


def test_theorem_within_section():
    compare_have_want(
        have="""\
        :rsm:

        ## Section

        :theorem:

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section</h2>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.1.</span></p>

        </div>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_theorems_same_section():
    compare_have_want(
        have="""\
        :rsm:

        ## Section

        :theorem:

        ::

        :theorem:

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section</h2>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.1.</span></p>

        </div>

        </div>

        <div class="theorem" data-nodeid="3">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.2.</span></p>

        </div>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_theorems_different_sections():
    compare_have_want(
        have="""\
        :rsm:

        ## Section 1

        :theorem:

        ::

        ## Section 2

        :theorem:

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section 1</h2>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.1.</span></p>

        </div>

        </div>

        </section>

        <section class="section level-2" data-nodeid="3">

        <h2>2. Section 2</h2>

        <div class="theorem" data-nodeid="4">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 2.1.</span></p>

        </div>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_theorems_same_section_nonum():
    compare_have_want(
        have="""\
        :rsm:

        ## Section

        :theorem:
        :nonum:

        ::

        :theorem:

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section</h2>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem.</span></p>

        </div>

        </div>

        <div class="theorem" data-nodeid="3">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.1.</span></p>

        </div>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_theorem_inside_section_with_nonum():
    compare_have_want(
        have="""\
        :rsm:

        ## Section
        :nonum:

        :theorem:

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>Section</h2>

        <div class="theorem" data-nodeid="2">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        </div>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_theorem_inside_subsection():
    compare_have_want(
        have="""\
        :rsm:

        ## Section

        ### Subsection

        :theorem:

        ::

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <section class="section level-2" data-nodeid="1">

        <h2>1. Section</h2>

        <section class="subsection level-3" data-nodeid="2">

        <h3>1.1. Subsection</h3>

        <div class="theorem" data-nodeid="3">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.1.</span></p>

        </div>

        </div>

        </section>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_transformer_init_default():
    """Transformer can be initialized without root_dir or src_file."""
    from rsm.transformer import Transformer

    t = Transformer()
    assert t.root_dir is None
    assert t.src_file is None
    assert t.external_manuscripts == {}


def test_transformer_init_with_root_dir():
    """Transformer can be initialized with root_dir."""
    from pathlib import Path

    from rsm.transformer import Transformer

    root_dir = Path("/some/root/directory")
    t = Transformer(root_dir=root_dir)
    assert t.root_dir == root_dir
    assert t.src_file is None
    assert t.external_manuscripts == {}


def test_transformer_init_with_src_file():
    """Transformer can be initialized with src_file."""
    from pathlib import Path

    from rsm.transformer import Transformer

    src_file = Path("/some/file.rsm")
    t = Transformer(src_file=src_file)
    assert t.root_dir is None
    assert t.src_file == src_file
    assert t.external_manuscripts == {}


def test_transformer_init_with_both():
    """Transformer can be initialized with both root_dir and src_file."""
    from pathlib import Path

    from rsm.transformer import Transformer

    root_dir = Path("/root/dir")
    src_file = Path("/root/dir/my_file.rsm")
    t = Transformer(root_dir=root_dir, src_file=src_file)
    assert t.root_dir == root_dir
    assert t.src_file == src_file
    assert t.external_manuscripts == {}


def test_load_external_manuscript_no_root_dir():
    """_load_external_manuscript should raise error if root_dir not set."""
    from rsm.transformer import Transformer

    t = Transformer()
    with pytest.raises(ValueError, match="root_dir must be set"):
        t._load_external_manuscript("definitions/def.rsm")


def test_load_external_manuscript_file_not_found():
    """_load_external_manuscript should raise FileNotFoundError if file doesn't exist."""
    from pathlib import Path

    from rsm.transformer import Transformer

    root_dir = Path(__file__).parent / "fixtures/crossref"
    t = Transformer(root_dir=root_dir)

    with pytest.raises(FileNotFoundError, match="nonexistent.rsm"):
        t._load_external_manuscript("definitions/nonexistent.rsm")


def test_load_external_manuscript_success():
    """_load_external_manuscript should successfully load and parse external file."""
    from pathlib import Path

    from rsm.transformer import Transformer

    root_dir = Path(__file__).parent / "fixtures/crossref"
    t = Transformer(root_dir=root_dir)

    manuscript, labels_map = t._load_external_manuscript("definitions/def.rsm")

    assert manuscript is not None
    assert "test-def" in labels_map
    assert labels_map["test-def"].label == "test-def"


def test_load_external_manuscript_caching():
    """_load_external_manuscript should cache results."""
    from pathlib import Path

    from rsm.transformer import Transformer

    root_dir = Path(__file__).parent / "fixtures/crossref"
    t = Transformer(root_dir=root_dir)

    # Load first time
    manuscript1, labels1 = t._load_external_manuscript("definitions/def.rsm")

    # Verify it's cached
    assert "definitions/def.rsm" in t.external_manuscripts

    # Load second time
    manuscript2, labels2 = t._load_external_manuscript("definitions/def.rsm")

    # Should be the same objects (from cache)
    assert manuscript1 is manuscript2
    assert labels1 is labels2


def test_label_to_node_internal():
    """_label_to_node should work for internal labels (existing behavior)."""
    from rsm.transformer import Transformer

    src = """:rsm:
## Section
  :label: my-label

Content here.
::"""

    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)

    t = Transformer()
    t.transform(tree)

    # Internal label lookup
    node = t._label_to_node("my-label")
    assert node.label == "my-label"
    assert node.__class__.__name__ == "Section"


def test_label_to_node_external():
    """_label_to_node should load external file and find label."""
    from pathlib import Path

    from rsm.transformer import Transformer

    root_dir = Path(__file__).parent / "fixtures/crossref"
    t = Transformer(root_dir=root_dir)

    # Need to initialize the transformer by transforming an empty tree
    src = ":rsm:\n::"
    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)
    t.transform(tree)

    # External label lookup
    node = t._label_to_node("test-def", external_file="definitions/def.rsm")
    assert node.label == "test-def"
    assert node.__class__.__name__ == "Section"


def test_label_to_node_external_not_found():
    """_label_to_node should return Error node if external label not found."""
    from pathlib import Path

    from rsm.transformer import Transformer

    root_dir = Path(__file__).parent / "fixtures/crossref"
    t = Transformer(root_dir=root_dir)

    # Need to initialize the transformer
    src = ":rsm:\n::"
    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)
    t.transform(tree)

    # External label that doesn't exist
    node = t._label_to_node("nonexistent-label", external_file="definitions/def.rsm")
    assert node.__class__.__name__ == "Error"


def test_label_to_node_external_file_not_found():
    """_label_to_node should return Error node if external file not found."""
    from pathlib import Path

    from rsm.transformer import Transformer

    root_dir = Path(__file__).parent / "fixtures/crossref"
    t = Transformer(root_dir=root_dir)

    # Need to initialize the transformer
    src = ":rsm:\n::"
    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)
    t.transform(tree)

    # External file that doesn't exist
    node = t._label_to_node("any-label", external_file="nonexistent/file.rsm")
    assert node.__class__.__name__ == "Error"


def test_resolve_pending_references_external():
    """resolve_pending_references should resolve external references."""
    from pathlib import Path

    from rsm.transformer import Transformer

    root_dir = Path(__file__).parent / "fixtures/crossref"

    # Parse the main.rsm file which contains an external reference
    src = """:rsm:
  :title: Main Document

This document references :ref:definitions/def.rsm#test-def::.

::"""

    parser = rsm.tsparser.TSParser()
    tree = parser.parse(src)

    # Transform with root_dir set
    t = Transformer(root_dir=root_dir)
    transformed = t.transform(tree)

    # Find the reference node
    refs = [
        node
        for node in transformed.traverse()
        if node.__class__.__name__ == "Reference"
    ]
    assert len(refs) == 1

    ref = refs[0]
    assert ref.external_file == "definitions/def.rsm"
    assert ref.target.label == "test-def"
    assert ref.target.__class__.__name__ == "Section"
