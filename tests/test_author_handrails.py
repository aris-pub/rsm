"""Tests for author handrails mode."""

from conftest import compare_have_want_handrails


def test_single_author_with_handrails():
    """Single author should have handrails wrapper."""
    compare_have_want_handrails(
        have="""\
        :author:{
          :name: Alice
          :affiliation: MIT
        }
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="author hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Author</span>
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

        <p>Alice</p>

        <p>MIT</p>

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


def test_six_authors_collapsed_with_handrails():
    """With 6 authors and handrails, should have collapsed mode with handrails wrapper."""
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
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="authors-container">

        <div class="author hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Author</span>
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

        <p>Author 1<sup>1</sup></p>

        <p><sup>1</sup>MIT</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="author hr hr-hidden" tabindex=0 data-nodeid="2">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Author</span>
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

        <p>Author 2<sup>2</sup></p>

        <p><sup>2</sup>Harvard</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="author hr hr-hidden" tabindex=0 data-nodeid="3">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Author</span>
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

        <p>Author 3<sup>3</sup></p>

        <p><sup>3</sup>Stanford</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="author hr hr-hidden author-hidden author-toggleable" tabindex=0 data-nodeid="4">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Author</span>
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

        <p>Author 4<sup>4</sup></p>

        <p><sup>4</sup>Berkeley</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <button class="toggle-authors">Show/hide full author information</button>

        <div class="author hr hr-hidden" tabindex=0 data-nodeid="5">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Author</span>
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

        <p>Author 5<sup>5</sup></p>

        <p><sup>5</sup>Yale</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        <div class="author hr hr-hidden" tabindex=0 data-nodeid="6">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Author</span>
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

        <p>Author 6<sup>6</sup></p>

        <p><sup>6</sup>Princeton</p>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
