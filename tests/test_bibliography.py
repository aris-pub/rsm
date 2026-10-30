import logging
import re
from textwrap import dedent

import rsm
from conftest import compare_have_want


def test_single():
    compare_have_want(
        have="""\
        # My Title

        This has a citation at the end. :cite:knuth::

        :references:
          @book{knuth,
            title={Art of computer programming, volume 2, Seminumerical algorithms},
            author={Knuth, Donald E},
            year={2014},
            publisher={Addison-Wesley Professional}
          }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This has a citation at the end. <span class="nowrap">[<a id="cite-0" class="reference cite" href="#knuth">1</a>]</span></p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="4">

        <li id="knuth" class="bibitem" data-nodeid="5">
        <div class="bib-card"><span class="bib-num">1</span><div class="bib-body"><div class="bib-line"><div class="bib-who">Knuth, Donald E (2014)</div></div><div class="bib-title">Art of computer programming, volume 2, Seminumerical algorithms</div><div class="bib-line"><div class="bib-venue">Addison-Wesley Professional</div><span class="bib-cited">cited <a class="reference backlink" href="#cite-0" aria-label="Back to the citation">↖</a></span></div></div></div>
        </li>

        </ol>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_with_shortcuts():
    compare_have_want(
        have="""\
        # My Title

        This has a **citation** at the end. :cite:knuth::

        :references:
        @book{knuth,
          title={Art of computer programming, volume 2: Seminumerical algorithms},
          author={Knuth, Donald E},
          year={2014},
          publisher={Addison-Wesley Professional}
        }
        ::
        """,
        want="""\
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This has a <span class="span" data-nodeid="3"><strong>citation</strong></span> at the end. <span class="nowrap">[<a id="cite-0" class="reference cite" href="#knuth">1</a>]</span></p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="7">

        <li id="knuth" class="bibitem" data-nodeid="8">
        <div class="bib-card"><span class="bib-num">1</span><div class="bib-body"><div class="bib-line"><div class="bib-who">Knuth, Donald E (2014)</div></div><div class="bib-title">Art of computer programming, volume 2: Seminumerical algorithms</div><div class="bib-line"><div class="bib-venue">Addison-Wesley Professional</div><span class="bib-cited">cited <a class="reference backlink" href="#cite-0" aria-label="Back to the citation">↖</a></span></div></div></div>
        </li>

        </ol>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_many():
    compare_have_want(
        have="""\
        # My Title

        This has a citation at the end. :cite:torres2020,knuth::

        :references:
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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This has a citation at the end. <span id="cite-0"><span class="nowrap">[<a id="cite-0-0" class="reference cite" href="#torres2020">1</a>,</span> <span class="nowrap"><a id="cite-0-1" class="reference cite" href="#knuth">2</a>]</span></span></p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="4">

        <li id="torres2020" class="bibitem" data-nodeid="5">
        <div class="bib-card"><span class="bib-num">1</span><div class="bib-body"><div class="bib-line"><div class="bib-who">Torres, Leo and Chan, Kevin S and Tong, Hanghang and Eliassi-Rad, Tina (2021)</div></div><div class="bib-title">Nonbacktracking eigenvalues under node removal: X-centrality and targeted immunization</div><div class="bib-line"><div class="bib-venue">SIAM Journal on Mathematics of Data Science 3(2)</div><span class="bib-cited">cited <a class="reference backlink" href="#cite-0" aria-label="Back to the citation">↖</a></span></div></div></div>
        </li>

        <li id="knuth" class="bibitem" data-nodeid="6">
        <div class="bib-card"><span class="bib-num">2</span><div class="bib-body"><div class="bib-line"><div class="bib-who">Knuth, Donald E (2014)</div></div><div class="bib-title">Art of computer programming, volume 2: Seminumerical algorithms</div><div class="bib-line"><div class="bib-venue">Addison-Wesley Professional</div><span class="bib-cited">cited <a class="reference backlink" href="#cite-0" aria-label="Back to the citation">↖</a></span></div></div></div>
        </li>

        </ol>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_order():
    compare_have_want(
        have="""\
        # My Title

        This has a citation at the end. :cite:knuth,torres2020::

        :references:
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
        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>My Title</h1>

        <div class="paragraph" data-nodeid="1">

        <p>This has a citation at the end. <span id="cite-0"><span class="nowrap">[<a id="cite-0-0" class="reference cite" href="#knuth">2</a>,</span> <span class="nowrap"><a id="cite-0-1" class="reference cite" href="#torres2020">1</a>]</span></span></p>

        </div>

        <section class="level-2">

        <h2>References</h2>

        <ol class="bibliography" data-nodeid="4">

        <li id="torres2020" class="bibitem" data-nodeid="5">
        <div class="bib-card"><span class="bib-num">1</span><div class="bib-body"><div class="bib-line"><div class="bib-who">Torres, Leo and Chan, Kevin S and Tong, Hanghang and Eliassi-Rad, Tina (2021)</div></div><div class="bib-title">Nonbacktracking eigenvalues under node removal: X-centrality and targeted immunization</div><div class="bib-line"><div class="bib-venue">SIAM Journal on Mathematics of Data Science 3(2)</div><span class="bib-cited">cited <a class="reference backlink" href="#cite-0" aria-label="Back to the citation">↖</a></span></div></div></div>
        </li>

        <li id="knuth" class="bibitem" data-nodeid="6">
        <div class="bib-card"><span class="bib-num">2</span><div class="bib-body"><div class="bib-line"><div class="bib-who">Knuth, Donald E (2014)</div></div><div class="bib-title">Art of computer programming, volume 2: Seminumerical algorithms</div><div class="bib-line"><div class="bib-venue">Addison-Wesley Professional</div><span class="bib-cited">cited <a class="reference backlink" href="#cite-0" aria-label="Back to the citation">↖</a></span></div></div></div>
        </li>

        </ol>

        </section>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_bibitem_without_year_renders():
    # Regression: year defaulted to the int -1, which is truthy, so a bibitem
    # with no year appended -1 to the rendered parts and then .strip()'d it as
    # an int, raising AttributeError. A missing year must simply be omitted.
    html = rsm.render(
        dedent(
            """
            # T

            :references:
            @article{a1,
              author={Smith, J},
              title={A paper with no year},
              journal={J. Testing}
            }
            ::
            """
        ).strip(),
        handrails=False,
        source_offsets=False,
    )
    item = re.search(r'<li[^>]*class="bibitem"[^>]*>(.*?)</li>', html, re.S)
    assert item, "bibitem did not render"
    assert "A paper with no year" in item.group(1)
    # no sentinel leaking in as a bogus year or entry number
    assert "-1" not in item.group(1)


def _bibitem_html(src: str) -> str:
    html = rsm.render(dedent(src).strip(), handrails=False, source_offsets=False)
    match = re.search(r'<li[^>]*class="bibitem"[^>]*>(.*?)</li>', html, re.S)
    assert match, "bibitem did not render"
    return match.group(1)


def test_verbatim_bibitem_renders_raw_text():
    # An unparsed reference carries its text in `verbatim` and is rendered as-is,
    # not formatted through empty author and title fields.
    item = _bibitem_html(
        """
        # T

        :references:
        @misc{raw1,
          verbatim={Doe, J. An unparsed reference. Journal of Stuff, 2021.}
        }
        ::
        """
    )
    assert "Doe, J. An unparsed reference. Journal of Stuff, 2021." in item
    assert '""' not in item


def test_webpage_kind_renders():
    item = _bibitem_html(
        """
        # T

        :references:
        @webpage{site1,
          author={Doe, J},
          title={A web resource},
          url={https://example.com/x}
        }
        ::
        """
    )
    assert "A web resource" in item
    assert "https://example.com/x" in item


def test_article_volume_only():
    # Volume prints right after the journal, with the year in parentheses.
    item = _bibitem_html(
        """
        # T

        :references:
        @article{a1,
          author={Torres, Leo},
          title={A paper},
          journal={Israel J. Math.},
          volume={52},
          year={1985}
        }
        ::
        """
    )
    assert '<div class="bib-venue">Israel J. Math. 52</div>' in item
    assert "(1985)</div>" in item


def test_article_volume_and_number():
    # Issue number prints in parentheses attached to the volume.
    item = _bibitem_html(
        """
        # T

        :references:
        @article{a1,
          author={Torres, Leo},
          title={A paper},
          journal={Israel J. Math.},
          volume={52},
          number={3},
          year={1985}
        }
        ::
        """
    )
    assert '<div class="bib-venue">Israel J. Math. 52(3)</div>' in item
    assert "(1985)</div>" in item


def test_article_no_volume_no_number():
    # With neither volume nor issue the journal is followed by the year alone.
    item = _bibitem_html(
        """
        # T

        :references:
        @article{a1,
          author={Torres, Leo},
          title={A paper},
          journal={Israel J. Math.},
          year={1985}
        }
        ::
        """
    )
    assert '<div class="bib-venue">Israel J. Math.</div>' in item
    assert "(1985)</div>" in item
    # no volume digits leak in when volume is absent
    assert "52" not in item


def test_article_pages_not_rendered():
    # A pages field is parsed but must never appear in the reference.
    item = _bibitem_html(
        """
        # T

        :references:
        @article{a1,
          author={Torres, Leo},
          title={A paper},
          journal={Israel J. Math.},
          volume={52},
          number={3},
          year={1985},
          pages={123--145}
        }
        ::
        """
    )
    assert "123" not in item
    assert "145" not in item


def test_doi_given_bare_yields_one_link():
    item = _bibitem_html(
        """
        # T

        :references:
        @article{a1,
          author={Torres, Leo},
          title={A paper},
          journal={Israel J. Math.},
          year={1985},
          doi={10.1234/abc}
        }
        ::
        """
    )
    assert 'href="https://doi.org/10.1234/abc"' in item
    assert item.count("https://doi.org/") == 1


def test_doi_given_as_url_yields_one_link():
    # A DOI already written as a resolver URL must not be prefixed again.
    item = _bibitem_html(
        """
        # T

        :references:
        @article{a1,
          author={Torres, Leo},
          title={A paper},
          journal={Israel J. Math.},
          year={1985},
          doi={https://doi.org/10.1234/abc}
        }
        ::
        """
    )
    assert 'href="https://doi.org/10.1234/abc"' in item
    assert "https://doi.org/https://doi.org/" not in item
    assert item.count("https://doi.org/") == 1


def test_doi_given_as_dx_url_is_normalized():
    item = _bibitem_html(
        """
        # T

        :references:
        @article{a1,
          author={Torres, Leo},
          title={A paper},
          journal={Israel J. Math.},
          year={1985},
          doi={http://dx.doi.org/10.1234/abc}
        }
        ::
        """
    )
    assert 'href="https://doi.org/10.1234/abc"' in item
    assert "dx.doi.org" not in item
    assert item.count("https://doi.org/") == 1


def test_verbatim_bibitem_warns_once(caplog):
    # A verbatim entry is unstructured, so it gets a single warning saying it is
    # verbatim, not the per-field warnings (no DOI, no year) nor the handrails
    # "unable to extract link" warning.
    caplog.set_level(logging.WARNING, logger="RSM")
    rsm.render(
        dedent(
            """
            # T

            :references:
            @misc{raw1,
              verbatim={Doe, J. An unparsed reference. Journal of Stuff, 2021.}
            }
            ::
            """
        ).strip(),
        handrails=True,
        source_offsets=False,
    )
    msgs = [r.getMessage() for r in caplog.records]
    verbatim = [m for m in msgs if "verbatim" in m.lower() and "raw1" in m]
    assert len(verbatim) == 1, msgs
    assert not any("has no DOI" in m for m in msgs)
    assert not any("has no year" in m for m in msgs)
    assert not any("Unable to extract link" in m for m in msgs)
