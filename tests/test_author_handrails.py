"""Tests for author handrails mode."""

from conftest import compare_have_want_handrails


def test_single_author_with_handrails():
    """Single author should render author block with handrail wrapping all content."""
    compare_have_want_handrails(
        have="""\
        :author:{
          :name: Alice
          :affiliation: MIT
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="author-block">
        <div class="heading hr-hidden hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg width="16" height="16"><use href="#hr-icon-collapse" width="16" height="16"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-item link disabled">
            <div class="icon link"><svg width="16" height="16"><use href="#hr-icon-link" width="16" height="16"/></svg></div>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <div class="icon code"><svg width="16" height="16"><use href="#hr-icon-code" width="16" height="16"/></svg></div>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg width="16" height="16"><use href="#hr-icon-dots" width="16" height="16"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p class="author-names">Alice</p>
        <details class="author-details">
        <summary><div class="icon chevron-down"><svg width="16" height="16"><use href="#hr-icon-chevron-down" width="16" height="16"/></svg></div>Affiliations</summary>
        <ol class="author-affiliations">
        <li>MIT</li>
        </ol>
        </details>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_six_authors_with_handrails():
    """With 6 authors and handrails, all names shown inline with collapsible details."""
    compare_have_want_handrails(
        have="""\
        :author:{
          :name: Author 1
          :affiliation: MIT}
        ::

        :author:{
          :name: Author 2
          :affiliation: Harvard}
        ::

        :author:{
          :name: Author 3
          :affiliation: Stanford}
        ::

        :author:{
          :name: Author 4
          :affiliation: Berkeley}
        ::

        :author:{
          :name: Author 5
          :affiliation: Yale}
        ::

        :author:{
          :name: Author 6
          :affiliation: Princeton}
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="author-block">
        <div class="heading hr-hidden hr" tabindex=0>

        <div class="hr-collapse-zone">

                    <div class="hr-collapse">
                      <div class="icon collapse"><svg width="16" height="16"><use href="#hr-icon-collapse" width="16" height="16"/></svg></div>
                    </div>

        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-item link disabled">
            <div class="icon link"><svg width="16" height="16"><use href="#hr-icon-link" width="16" height="16"/></svg></div>
            <span class="hr-menu-item-text">Copy link</span>
          </div>

          <div class="hr-menu-item">
            <div class="icon code"><svg width="16" height="16"><use href="#hr-icon-code" width="16" height="16"/></svg></div>
            <span class="hr-menu-item-text">Source</span>
          </div>

        </div>

        </div>

        <div class="hr-border-zone">

                        <div class="hr-border-dots">
                          <div class="icon dots"><svg width="16" height="16"><use href="#hr-icon-dots" width="16" height="16"/></svg></div>
                        </div>
                        <div class="hr-border-rect">
                        </div>

        </div>

        <div class="hr-spacer-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-content-zone">

        <p class="author-names">Author 1<sup data-tooltip="MIT">1</sup>, Author 2<sup data-tooltip="Harvard">2</sup>, Author 3<sup data-tooltip="Stanford">3</sup>, Author 4<sup data-tooltip="Berkeley">4</sup>, Author 5<sup data-tooltip="Yale">5</sup>, Author 6<sup data-tooltip="Princeton">6</sup></p>
        <details class="author-details">
        <summary><div class="icon chevron-down"><svg width="16" height="16"><use href="#hr-icon-chevron-down" width="16" height="16"/></svg></div>Affiliations</summary>
        <ol class="author-affiliations">
        <li value="1"><sup>1</sup>MIT</li>
        <li value="2"><sup>2</sup>Harvard</li>
        <li value="3"><sup>3</sup>Stanford</li>
        <li value="4"><sup>4</sup>Berkeley</li>
        <li value="5"><sup>5</sup>Yale</li>
        <li value="6"><sup>6</sup>Princeton</li>
        </ol>
        </details>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>
        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
