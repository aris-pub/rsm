from conftest import compare_have_want


def test_single():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This has a citation at the end. :cite:knuth::

        :bibliography: ::

        ::


        :bibtex:

        @book{knuth,
          title={Art of computer programming, volume 2, Seminumerical algorithms},
          author={Knuth, Donald E},
          year={2014},
          publisher={Addison-Wesley Professional}
        }

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This has a citation at the end. [<a id="cite-0" class="reference cite" href="#knuth">1</a>]</p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="4">

        <li id="knuth" class="bibitem" data-nodeid="5">
        1. Knuth, Donald E. "Art of computer programming, volume 2, Seminumerical algorithms". Addison-Wesley Professional. 2014.<br />[<a class="reference backlink" href="#cite-0">↖1</a>]
        </li>

        </ol>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_with_shortcuts():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This has a *citation* at the end. :cite:knuth::

        :bibliography: ::

        ::


        :bibtex:

        @book{knuth,
          title={Art of computer programming, volume 2: Seminumerical algorithms},
          author={Knuth, Donald E},
          year={2014},
          publisher={Addison-Wesley Professional}
        }

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This has a <span class="span" data-nodeid="3"><strong>citation</strong></span> at the end. [<a id="cite-0" class="reference cite" href="#knuth">1</a>]</p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="7">

        <li id="knuth" class="bibitem" data-nodeid="8">
        1. Knuth, Donald E. "Art of computer programming, volume 2: Seminumerical algorithms". Addison-Wesley Professional. 2014.<br />[<a class="reference backlink" href="#cite-0">↖1</a>]
        </li>

        </ol>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_many():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This has a citation at the end. :cite:torres2020,knuth::

        :bibliography: ::

        ::


        :bibtex:

        @article{torres2020,
          title={Nonbacktracking eigenvalues under node removal: X-centrality and targeted immunization},
          author={Torres, Leo and Chan, Kevin S and Tong, Hanghang and Eliassi-Rad, Tina},
          journal={SIAM Journal on Mathematics of Data Science},
          volume={3},
          number={2},
          year={2021},
        }

        @book{knuth,
          title={Art of computer programming, volume 2: Seminumerical algorithms},
          author={Knuth, Donald E},
          year={2014},
          publisher={Addison-Wesley Professional}
        }

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This has a citation at the end. [<span id="cite-0"><a id="cite-0-0" class="reference cite" href="#torres2020">1</a>, <a id="cite-0-1" class="reference cite" href="#knuth">2</a></span>]</p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="4">

        <li id="torres2020" class="bibitem" data-nodeid="5">
        1. Torres, Leo and Chan, Kevin S and Tong, Hanghang and Eliassi-Rad, Tina. "Nonbacktracking eigenvalues under node removal: X-centrality and targeted immunization". SIAM Journal on Mathematics of Data Science. 2021.<br />[<a class="reference backlink" href="#cite-0">↖1</a>]
        </li>

        <li id="knuth" class="bibitem" data-nodeid="6">
        2. Knuth, Donald E. "Art of computer programming, volume 2: Seminumerical algorithms". Addison-Wesley Professional. 2014.<br />[<a class="reference backlink" href="#cite-0">↖1</a>]
        </li>

        </ol>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_order():
    compare_have_want(
        have="""\
        :rsm:
          :title: My Title

        This has a citation at the end. :cite:knuth,torres2020::

        :bibliography: ::

        ::


        :bibtex:

        @article{torres2020,
          title={Nonbacktracking eigenvalues under node removal: X-centrality and targeted immunization},
          author={Torres, Leo and Chan, Kevin S and Tong, Hanghang and Eliassi-Rad, Tina},
          journal={SIAM Journal on Mathematics of Data Science},
          volume={3},
          number={2},
          year={2021},
        }

        @book{knuth,
          title={Art of computer programming, volume 2: Seminumerical algorithms},
          author={Knuth, Donald E},
          year={2014},
          publisher={Addison-Wesley Professional}
        }

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This has a citation at the end. [<span id="cite-0"><a id="cite-0-0" class="reference cite" href="#knuth">2</a>, <a id="cite-0-1" class="reference cite" href="#torres2020">1</a></span>]</p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="4">

        <li id="torres2020" class="bibitem" data-nodeid="5">
        1. Torres, Leo and Chan, Kevin S and Tong, Hanghang and Eliassi-Rad, Tina. "Nonbacktracking eigenvalues under node removal: X-centrality and targeted immunization". SIAM Journal on Mathematics of Data Science. 2021.<br />[<a class="reference backlink" href="#cite-0">↖1</a>]
        </li>

        <li id="knuth" class="bibitem" data-nodeid="6">
        2. Knuth, Donald E. "Art of computer programming, volume 2: Seminumerical algorithms". Addison-Wesley Professional. 2014.<br />[<a class="reference backlink" href="#cite-0">↖1</a>]
        </li>

        </ol>

        </section>

        </section>

        </div>

        </div>

        </body>
        """,
    )
