from conftest import compare_have_want


def test_simple():
    compare_have_want(
        have="""\
        # The Perron non-backtracking eigenvalue after node addition {
          :label: mylbl
        }

        :config: {
          :override-date: 2022-03-29
        }
        ::

        :author: {
          :name: Leo Torres
          :affiliation: Max Planck Institute for Mathematics in the Sciences
          :email: leo@leotrs.com
        }
        ::

        :abstract: {
            :keywords: spectral graph theory, non-backtracking, interlacing
            :msc: 05C50, 05C82, 15A18, 15B99
          }
          first
          second
          third

          fourth
          fifth

        ::

        ## Introduction {
          :title:
          :label: sec-introduction
          :class: t1, t2
        }

        Lorem ipsum.
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div id="mylbl" class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>The Perron <span class="hyphenated">non-backtracking</span> eigenvalue after node addition</h1>

        <p class="manuscript-date">March 29, 2022</p>

        <div class="author-block">
        <p class="author-names"><span class="author-name"><span class="author-name-text" data-affiliation="Max Planck Institute for Mathematics in the Sciences">Leo Torres</span><a class="author-contact" href="mailto:leo@leotrs.com" aria-label="Email Leo Torres" data-tip="Email Leo Torres"><span class="icon mail" aria-hidden="true"><svg overflow="visible"><use href="#hr-icon-mail" width="100%" height="100%"/></svg></span></a></span></p>
        <button type="button" class="author-summary" aria-expanded="false" hidden>1 affiliation<span aria-hidden="true"> · </span>1 email</button>
        <div class="author-details">
        <ol class="author-affiliations">
        <li>Max Planck Institute for Mathematics in the Sciences</li>
        </ol>
        <p class="author-correspondence">Correspondence: <a href="mailto:leo@leotrs.com">leo@leotrs.com</a></p>
        </div>
        </div>

        <div class="abstract" data-nodeid="2">

        <h2>Abstract</h2>

        <div class="paragraph" data-nodeid="3">

        <p>first second third</p>

        </div>

        <div class="paragraph" data-nodeid="5">

        <p>fourth fifth</p>

        </div>

        <p class="keywords">Keywords: spectral graph theory, <span class="hyphenated">non-backtracking,</span> interlacing</p>

        <p class="msc">MSC: 05C50, 05C82, 15A18, 15B99</p>

        </div>

        <section id="sec-introduction" class="section level-2 t1 t2" data-nodeid="7">

        <h2>1. Introduction</h2>

        <div class="paragraph" data-nodeid="8">

        <p>Lorem ipsum.</p>

        </div>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )
