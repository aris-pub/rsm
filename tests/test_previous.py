import re

import pytest

import rsm
from conftest import compare_have_want


def test_works_with_no_reftext_and_label():
    compare_have_want(
        have="""\
        :proof:

          :step:
            {:label: lbl}
          Foo.
          ::

          :step: Bar :previous:1::.::

        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="proof" data-steps="2" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div id="lbl" class="step" data-nodeid="2">

        <div class="statement" data-nodeid="3">

        <div class="paragraph" data-nodeid="4">

        <p>Foo.</p>

        </div>

        </div>

        </div>

        <div class="step last" data-nodeid="6">

        <div class="statement" data-nodeid="7">

        <div class="paragraph" data-nodeid="8">

        <p>Bar <span class="inline-wrapper"><a class="reference" href="#lbl">Step ⟨1⟩</a><span>.</span></span></p>

        </div>

        </div>

        </div>

        <div class="halmos"></div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_works_with_no_reftext_and_no_label():
    compare_have_want(
        have="""\
        :proof:

          :step: Foo.::

          :step: Bar :previous:1::.::

        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="proof" data-steps="2" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div id="n2" class="step" data-nodeid="2">

        <div class="statement" data-nodeid="3">

        <div class="paragraph" data-nodeid="4">

        <p>Foo.</p>

        </div>

        </div>

        </div>

        <div class="step last" data-nodeid="6">

        <div class="statement" data-nodeid="7">

        <div class="paragraph" data-nodeid="8">

        <p>Bar <span class="inline-wrapper"><a class="reference" href="#n2">Step ⟨1⟩</a><span>.</span></span></p>

        </div>

        </div>

        </div>

        <div class="halmos"></div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_works_with_reftext_and_label():
    compare_have_want(
        have="""\
        :proof:

          :step:
            {:label: lbl}
          Foo.::

          :step: Bar :previous:1,bar::.::

        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="proof" data-steps="2" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div id="lbl" class="step" data-nodeid="2">

        <div class="statement" data-nodeid="3">

        <div class="paragraph" data-nodeid="4">

        <p>Foo.</p>

        </div>

        </div>

        </div>

        <div class="step last" data-nodeid="6">

        <div class="statement" data-nodeid="7">

        <div class="paragraph" data-nodeid="8">

        <p>Bar <span class="inline-wrapper"><a class="reference" href="#lbl">bar</a><span>.</span></span></p>

        </div>

        </div>

        </div>

        <div class="halmos"></div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_works_with_reftext_and_no_label():
    compare_have_want(
        have="""\
        :proof:

          :step: Foo.::

          :step: Bar :previous:1,bar::.::

        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="proof" data-steps="2" data-nodeid="1">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div id="n2" class="step" data-nodeid="2">

        <div class="statement" data-nodeid="3">

        <div class="paragraph" data-nodeid="4">

        <p>Foo.</p>

        </div>

        </div>

        </div>

        <div class="step last" data-nodeid="6">

        <div class="statement" data-nodeid="7">

        <div class="paragraph" data-nodeid="8">

        <p>Bar <span class="inline-wrapper"><a class="reference" href="#n2">bar</a><span>.</span></span></p>

        </div>

        </div>

        </div>

        <div class="halmos"></div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_previous_outside_step():
    with pytest.raises(rsm.transformer.RSMTransformerError):
        compare_have_want(
            have="""\
            Foo :previous:1,bar::.
            """,
            want="X",
        )


UNLABELLED_STEPS = """\
:proof:

  :step: :claim: $x$ ::.
  ::

  :step: :claim: $y$ ::.
  ::

  :step: By :prev: and :prev2:. :claim: $z$ ::.
  ::

::
"""

LABELLED_STEPS = """\
:proof:

  :step: {:label: first} :claim: $x$ ::.
  ::

  :step: By :prev:. :claim: $y$ ::.
  ::

::
"""


def _step_ids(html):
    return re.findall(r'<div id="([^"]*)" class="step', html)


def _ref_hrefs(html):
    return re.findall(r'<a class="reference" href="([^"]*)"', html)


@pytest.mark.parametrize("handrails", [False, True])
def test_prev_to_unlabelled_step_links_to_step_id(handrails, caplog):
    html = rsm.render(UNLABELLED_STEPS, handrails=handrails)
    ids = _step_ids(html)
    assert len(ids) == 3
    assert _ref_hrefs(html) == [f"#{ids[1]}", f"#{ids[0]}"]
    assert "un-labeled step" not in caplog.text


@pytest.mark.parametrize("handrails", [False, True])
def test_prev_to_labelled_step_links_to_label(handrails):
    html = rsm.render(LABELLED_STEPS, handrails=handrails)
    assert _step_ids(html)[0] == "first"
    assert _ref_hrefs(html) == ["#first"]
