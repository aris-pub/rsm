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

        <p class="author-names"><span class="author-name"><span class="author-name-text" data-affiliation="1">Alice</span></span></p>
        <button type="button" class="author-summary" aria-expanded="false" hidden>1 affiliation</button>
        <div class="author-details">
        <ol class="author-affiliations">
        <li data-affiliation="1">MIT</li>
        </ol>
        </div>

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

        <p class="author-names"><span class="author-name"><span class="author-name-text" data-affiliation="1">Author 1</span><sup data-affiliation="1">1</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="2">Author 2</span><sup data-affiliation="2">2</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="3">Author 3</span><sup data-affiliation="3">3</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="4">Author 4</span><sup data-affiliation="4">4</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="5">Author 5</span><sup data-affiliation="5">5</sup></span>, <span class="author-name"><span class="author-name-text" data-affiliation="6">Author 6</span><sup data-affiliation="6">6</sup></span></p>
        <button type="button" class="author-summary" aria-expanded="false" hidden>6 affiliations</button>
        <div class="author-details">
        <ol class="author-affiliations">
        <li value="1" data-affiliation="1"><sup>1</sup>MIT</li>
        <li value="2" data-affiliation="2"><sup>2</sup>Harvard</li>
        <li value="3" data-affiliation="3"><sup>3</sup>Stanford</li>
        <li value="4" data-affiliation="4"><sup>4</sup>Berkeley</li>
        <li value="5" data-affiliation="5"><sup>5</sup>Yale</li>
        <li value="6" data-affiliation="6"><sup>6</sup>Princeton</li>
        </ol>
        </div>

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
