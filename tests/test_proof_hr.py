import re

import rsm
from conftest import compare_have_want_handrails


def test_two_steps():
    compare_have_want_handrails(
        have="""
        # Some Title

        :proof:

          :step: Foo.::

          :step: Bar.::

        ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Some Title</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="proof hr hr-labeled" data-steps="2" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="paragraph hr-label" data-fold-label="2 steps hidden">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="step hr hr-offset" tabindex=0 data-nodeid="2">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="statement" data-nodeid="3">

        <div class="paragraph hr hr-hidden hr-offset" tabindex=0 data-nodeid="4">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Foo.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="step-number"><p>⟨1⟩</p></div></div>
        </div>

        </div>

        <div class="step last hr hr-offset" tabindex=0 data-nodeid="6">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="statement" data-nodeid="7">

        <div class="paragraph hr hr-hidden hr-offset" tabindex=0 data-nodeid="8">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Bar.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="step-number"><p>⟨2⟩</p></div></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_sub_step():
    compare_have_want_handrails(
        have="""
        # Some Title

        :proof:

          :step: Top level step.

            :step: Sub-step.

              :p: Sub-Proof.::

            ::
          ::

        ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Some Title</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="proof hr hr-labeled" data-steps="1" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="paragraph hr-label" data-fold-label="1 step hidden">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="step last hr hr-offset" tabindex=0 data-nodeid="2">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone" data-fold-label="1 step hidden">

        <div class="statement" data-nodeid="3">

        <div class="paragraph hr hr-hidden hr-offset" tabindex=0 data-nodeid="4">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Top level step.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="subproof hr hr-offset hr-shift-1" data-nodeid="6">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        </div>

        <div class="hr-border-zone">
        <div class="hr-border-rect"></div>
        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="step hr hr-hidden hr-offset" tabindex=0 data-nodeid="7">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone" data-fold-label="justification hidden">

        <div class="statement" data-nodeid="8">

        <div class="paragraph hr hr-offset hr-hidden" tabindex=0 data-nodeid="9">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Sub-step.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="subproof hr hr-offset hr-shift-1" data-nodeid="11">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        </div>

        <div class="hr-border-zone">
        <div class="hr-border-rect"></div>
        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="paragraph hr hr-offset hr-hidden" tabindex=0 data-nodeid="12">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Sub-Proof.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="step-number"><p>⟨1.1⟩</p></div></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="step-number"><p>⟨1⟩</p></div></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_theorem():
    compare_have_want_handrails(
        have="""
        :theorem:

        Hello.

        ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="theorem hr hr-labeled" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="paragraph hr-label" data-fold-label="theorem hidden">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        <div class="paragraph hr hr-offset hr-hidden" tabindex=0 data-nodeid="2">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Hello.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_proof():
    compare_have_want_handrails(
        have="""
        # Some Title

        :proof:

          :step: Bar.::

        ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Some Title</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="proof hr hr-labeled" data-steps="1" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="paragraph hr-label" data-fold-label="1 step hidden">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="step last hr hr-offset" tabindex=0 data-nodeid="2">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="statement" data-nodeid="3">

        <div class="paragraph hr hr-hidden hr-offset" tabindex=0 data-nodeid="4">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Bar.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="step-number"><p>⟨1⟩</p></div></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_proof_with_sketch():
    compare_have_want_handrails(
        have="""
        # Some Title

        :sketch: Foo.::

        :proof:

          :step: Bar.::

        ::
        """,
        want="""
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="heading hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <h1>Some Title</h1>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="sketch hr hr-labeled" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="paragraph hr-label" data-fold-label="sketch hidden">

        <p><span class="span label">Proof sketch.</span></p>

        </div>

        <div class="paragraph hr hr-offset hr-hidden" tabindex=0 data-nodeid="2">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Foo.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="proof hr hr-labeled" data-steps="1" tabindex=0 data-nodeid="4">

        <div class="hr-collapse-zone">

                    <button type="button" class="hr-collapse" aria-expanded="true" aria-label="Show or hide this block">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </button>

        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="paragraph hr-label" data-fold-label="1 step hidden">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="step last hr hr-offset" tabindex=0 data-nodeid="5">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <div class="statement" data-nodeid="6">

        <div class="paragraph hr hr-hidden hr-offset" tabindex=0 data-nodeid="7">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">
</div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg overflow="visible"><use href="#hr-icon-dots" width="100%" height="100%"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Bar.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="step-number"><p>⟨1⟩</p></div></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


# A folded block names what it hides at the foot of its handrail: "N steps
# hidden" when it holds steps, "justification hidden" for a step whose only
# hidden body is its :p:, else "<kind> hidden". The words ride a data-fold-label
# attribute that CSS renders, so the stylesheet holds no hard-coded text. Steps
# carry it on their content zone, labelled blocks (proof, sketch, theorem) on
# their .hr-label, so a proof's label never shares a pseudo-element with its
# tombstone. See beads rsm-2df and rsm-85x.


def _render_proof(body):
    return rsm.render("# T\n\n" + body, handrails=True, source_offsets=False)


def _labels(body):
    """Every (class, fold label) pair in the rendered body, in document order."""
    html = _render_proof(body)
    tags = re.findall(r'<div class="([^"]*)"[^>]*\bdata-fold-label="([^"]*)"', html)
    return [(cls, label) for cls, label in tags]


def test_fold_label_proof_counts_top_level_steps():
    body = """
        :proof:
          :step: First.::
          :step: Second.::
          :step: Third.::
        ::
        """
    assert 'data-steps="3"' in _render_proof(body)
    # The proof's label lives on its .hr-label, not on the content zone whose
    # ::after draws the tombstone.
    assert _labels(body) == [("paragraph hr-label", "3 steps hidden")]


def test_fold_label_proof_one_step():
    body = """
        :proof:
          :step: Only one.::
        ::
        """
    assert _labels(body) == [("paragraph hr-label", "1 step hidden")]


def test_fold_label_counts_only_direct_steps():
    # One top-level step holding two sub-steps: the proof hides one step, the
    # step hides two.
    body = """
        :proof:
          :step: Outer.
            :step: Inner a.::
            :step: Inner b.::
          ::
        ::
        """
    assert _labels(body) == [
        ("paragraph hr-label", "1 step hidden"),
        ("hr-content-zone", "2 steps hidden"),
    ]


def test_fold_label_step_with_one_substep():
    body = """
        :proof:
          :step: Outer.
            :step: Inner.::
          ::
        ::
        """
    assert _labels(body)[1] == ("hr-content-zone", "1 step hidden")


def test_fold_label_prose_proof():
    body = """
        :proof:
          Just prose, no steps at all.
        ::
        """
    assert "data-steps=" not in _render_proof(body)
    assert _labels(body) == [("paragraph hr-label", "proof hidden")]


def test_fold_label_step_with_only_justification():
    body = """
        :proof:
          :step: A claim.

            :p: The reason. ::

          ::
        ::
        """
    assert _labels(body) == [
        ("paragraph hr-label", "1 step hidden"),
        ("hr-content-zone", "justification hidden"),
    ]


def test_fold_label_step_with_nothing_to_hide():
    body = """
        :proof:
          :step: A bare claim.::
        ::
        """
    assert _labels(body) == [("paragraph hr-label", "1 step hidden")]


def test_no_fold_label_on_calc_step():
    # Calc rows start folded, so they show no label. The proof around the calc
    # has no steps of its own, so it reads "proof hidden".
    body = """
        :proof:
          :calc:

            :step: $f(x) = a$

              :p: Because the first reason. ::

            ::

          ::
        ::
        """
    assert _labels(body) == [("paragraph hr-label", "proof hidden")]


def test_fold_label_sketch():
    body = """
        :sketch: The idea in brief.::
        """
    assert _labels(body) == [("paragraph hr-label", "sketch hidden")]


def test_fold_label_theorem_uses_its_kind():
    body = """
        :lemma: A statement.::
        """
    assert _labels(body) == [("paragraph hr-label", "lemma hidden")]


def test_fold_label_only_with_handrails():
    html = rsm.render(
        "# T\n\n:proof:\n  :step: One.::\n::\n", handrails=False, source_offsets=False
    )
    assert "data-fold-label" not in html


def test_no_step_count_in_proof_header():
    html = _render_proof(
        """
        :proof:
          :step: First.::
          :step: Second.::
        ::
        """
    )
    assert "proof-step-count" not in html
