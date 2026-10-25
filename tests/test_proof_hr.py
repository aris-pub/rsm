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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span><span class="span proof-step-count">2 steps</span></p>

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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span><span class="span proof-step-count">1 step</span></p>

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

        <div class="hr-content-zone">

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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

        <div class="paragraph hr-label">

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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span><span class="span proof-step-count">1 step</span></p>

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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

        <div class="paragraph hr-label">

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

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg overflow="visible"><use href="#hr-icon-collapse" width="100%" height="100%"/></svg></div>
                    </div>

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

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span><span class="span proof-step-count">1 step</span></p>

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


# A collapsed structured proof shows how many top-level steps are folded away,
# so the reader knows how much is hidden before expanding it. The count rides a
# data attribute and a muted suffix span, kept out of the label text so a
# document can hide or restyle it. See bead rsm-2df.


def _render_proof(body):
    return rsm.render("# T\n\n" + body, handrails=True, source_offsets=False)


def test_proof_step_count_multiple():
    html = _render_proof(
        """
        :proof:
          :step: First.::
          :step: Second.::
          :step: Third.::
        ::
        """
    )
    assert 'data-steps="3"' in html
    assert re.search(r'proof-step-count">\s*3 steps\s*<', html)


def test_proof_step_count_singular():
    html = _render_proof(
        """
        :proof:
          :step: Only one.::
        ::
        """
    )
    assert 'data-steps="1"' in html
    assert re.search(r'proof-step-count">\s*1 step\s*<', html)


def test_proof_step_count_only_top_level():
    # A single top-level step whose body holds two sub-steps still counts as one.
    html = _render_proof(
        """
        :proof:
          :step: Outer.
            :step: Inner a.::
            :step: Inner b.::
          ::
        ::
        """
    )
    assert 'data-steps="1"' in html
    assert re.search(r'proof-step-count">\s*1 step\s*<', html)


def test_proof_step_count_none():
    html = _render_proof(
        """
        :proof:
          Just prose, no steps at all.
        ::
        """
    )
    assert "data-steps=" not in html
    assert "proof-step-count" not in html
