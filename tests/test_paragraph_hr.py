from conftest import compare_have_want_handrails


def test_paragraph_with_mathblock_ending_with_text():
    compare_have_want_handrails(
        have="""
        This is a paragraph with math inside of it
        $$
        2+2=4,
        $$
        and it ends with text.
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>This is a paragraph with math inside of it </p>
        <div class="mathblock hr hr-hidden hr-offset" tabindex=0 data-nodeid="3">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Equation (1)</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">
        $$
        2+2=4,
        $$
        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="eqn-number"><p>(1)</p></div></div>
        </div>

        </div>
        <p> and it ends with text.</p>
        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_paragraph_ending_with_mathblock():
    compare_have_want_handrails(
        have="""
        This is a paragraph with math inside of it
        $$
        2+2=4.
        $$
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>This is a paragraph with math inside of it </p>
        <div class="mathblock hr hr-hidden hr-offset" tabindex=0 data-nodeid="3">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Equation (1)</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">
        $$
        2+2=4.
        $$
        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="eqn-number"><p>(1)</p></div></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_paragraph_with_icon_ending_with_mathblock():
    compare_have_want_handrails(
        have=r"""
        :paragraph: {:icon: heart} Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
        do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        $$
        \left( \mathbf{B} \mathbf{v} \right)_{i \to j} = \sum_{k \to i \in \vec{E}}
        \mathbf{v}_{k \to i} - \mathbf{v}_{j \to i}.
        $$
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. </p>
        <div class="mathblock hr hr-hidden hr-offset" tabindex=0 data-nodeid="3">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Equation (1)</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">
        $$
        \left( \mathbf{B} \mathbf{v} \right)_{i \to j} = \sum_{k \to i \in \vec{E}}
        \mathbf{v}_{k \to i} - \mathbf{v}_{j \to i}.
        $$
        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="eqn-number"><p>(1)</p></div></div>
        </div>

        </div>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info">
                        <div class="icon heart">
                        </div>
                        </div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_paragraph_with_icon_with_mathblock_ending_with_text():
    compare_have_want_handrails(
        have=r"""
        :paragraph: {:icon: heart} Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
        do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        $$
        \left( \mathbf{B} \mathbf{v} \right)_{i \to j} = \sum_{k \to i \in \vec{E}}
        \mathbf{v}_{k \to i} - \mathbf{v}_{j \to i}.
        $$
        Lorem ipsum.
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. </p>
        <div class="mathblock hr hr-hidden hr-offset" tabindex=0 data-nodeid="3">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Equation (1)</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">
        $$
        \left( \mathbf{B} \mathbf{v} \right)_{i \to j} = \sum_{k \to i \in \vec{E}}
        \mathbf{v}_{k \to i} - \mathbf{v}_{j \to i}.
        $$
        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="eqn-number"><p>(1)</p></div></div>
        </div>

        </div>
        <p> Lorem ipsum.</p>
        </div>

        <div class="hr-info-zone">
        <div class="hr-info">
                        <div class="icon heart">
                        </div>
                        </div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_paragraphs_with_icon():
    compare_have_want_handrails(
        have=r"""
        :paragraph: {:icon: heart} Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
        do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
        $$
        \left( \mathbf{B} \mathbf{v} \right)_{i \to j} = \sum_{k \to i \in \vec{E}}
        \mathbf{v}_{k \to i} - \mathbf{v}_{j \to i}.
        $$
        Lorem ipsum.

        :paragraph: {:icon: success} Lorem ipsum dolor sit amet, consectetur adipiscing elit,
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
        consequat.
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. </p>
        <div class="mathblock hr hr-hidden hr-offset" tabindex=0 data-nodeid="3">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Equation (1)</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">
        $$
        \left( \mathbf{B} \mathbf{v} \right)_{i \to j} = \sum_{k \to i \in \vec{E}}
        \mathbf{v}_{k \to i} - \mathbf{v}_{j \to i}.
        $$
        </div>

        <div class="hr-info-zone">
        <div class="hr-info"><div class="eqn-number"><p>(1)</p></div></div>
        </div>

        </div>
        <p> Lorem ipsum.</p>
        </div>

        <div class="hr-info-zone">
        <div class="hr-info">
                        <div class="icon heart">
                        </div>
                        </div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="6">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info">
                        <div class="icon success">
                        </div>
                        </div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_two_paragraphs_with_icon_no_mathblock():
    compare_have_want_handrails(
        have=r"""
        :paragraph: {:icon: heart} Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed
        do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
        quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.

        :paragraph: {:icon: success} Lorem ipsum dolor sit amet, consectetur adipiscing elit,
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim
        veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
        consequat.
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info">
                        <div class="icon heart">
                        </div>
                        </div>
        </div>

        </div>

        <div class="paragraph hr hr-hidden" tabindex=0 data-nodeid="3">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Paragraph</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link disabled">
            <span class="icon link">
            </span>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon tree">
            </span>
            <span class="hr-menu-item-text">Tree</span>
          </div>

          <div class="hr-menu-item">
            <span class="icon code">
            </span>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots">
                          </div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info">
                        <div class="icon success">
                        </div>
                        </div>
        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
