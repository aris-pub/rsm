from conftest import compare_have_want


def test_period_after():
    compare_have_want(
        have="""
        Period after math :math:2+2=4::.

        Period after code :code:k=v::.

        Period after claim :claim:foo::.
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Period after math <span class="math" data-nodeid="3">\(2+2=4\)</span>.</p>

        </div>

        <div class="paragraph" data-nodeid="6">

        <p>Period after code <span class="code" data-nodeid="8"><code>k=v</code></span>.</p>

        </div>

        <div class="paragraph" data-nodeid="11">

        <p>Period after claim <span class="construct claim" data-nodeid="13"><span class="keyword" data-nodeid="14">⊢</span> foo</span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_period_after_with_shortcut():
    compare_have_want(
        have="""
        Period after math $2+2=4$.

        Period after code `k=v`.

        Period after claim :|-:foo::.
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Period after math <span class="math" data-nodeid="3">\(2+2=4\)</span>.</p>

        </div>

        <div class="paragraph" data-nodeid="6">

        <p>Period after code <span class="code" data-nodeid="8"><code>k=v</code></span>.</p>

        </div>

        <div class="paragraph" data-nodeid="11">

        <p>Period after claim <span class="construct claim" data-nodeid="13"><span class="keyword" data-nodeid="14">⊢</span> foo</span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_separate_words():
    compare_have_want(
        have="""
        :span:{:strong:}Separate:: words.

        Separate :span:{:strong:}words::.
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="span" data-nodeid="2"><strong>Separate</strong></span> words.</p>

        </div>

        <div class="paragraph" data-nodeid="5">

        <p>Separate <span class="span" data-nodeid="7"><strong>words</strong></span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_separate_words_with_shortcut():
    compare_have_want(
        have="""
        **Separate** words.

        Separate **words**.
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="span" data-nodeid="2"><strong>Separate</strong></span> words.</p>

        </div>

        <div class="paragraph" data-nodeid="5">

        <p>Separate <span class="span" data-nodeid="7"><strong>words</strong></span>.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_multiline_content_middle_of_line():
    compare_have_want(
        have="""
        This is a paragraph
        with :span: {:strong:} a
        span :: that takes multiple lines
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph with <span class="span" data-nodeid="3"><strong>a span</strong></span> that takes multiple lines</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_multiline_content_beginning_of_line():
    compare_have_want(
        have="""
        This is a paragraph with
        :span: {:strong:} a
        span :: that takes multiple lines
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph with <span class="span" data-nodeid="3"><strong>a span</strong></span> that takes multiple lines</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_multiline_content_beginning_of_line_with_shortcut():
    compare_have_want(
        have="""
        This is a paragraph with
        ** a
        span ** that takes multiple lines
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph with <span class="span" data-nodeid="3"><strong>a span</strong></span> that takes multiple lines</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_multiline_content_middle_of_line_with_shortcut():
    compare_have_want(
        have="""
        This is a paragraph
        with ** a
        span ** that takes multiple lines
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph with <span class="span" data-nodeid="3"><strong>a span</strong></span> that takes multiple lines</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_math_start_of_line():
    compare_have_want(
        have="""
        This is a paragraph with
        :math:2+2=4:: at the start of a line.
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph with <span class="math" data-nodeid="3">\(2+2=4\)</span> at the start of a line.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_math_start_of_line_with_shortcut():
    compare_have_want(
        have="""
        This is a paragraph with
        $2+2=4$ at the start of a line.
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>This is a paragraph with <span class="math" data-nodeid="3">\(2+2=4\)</span> at the start of a line.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_table_tr():
    compare_have_want(
        have="""
        :table:

        :tbody:

        :tr: :td: *foo* :: :td: **bar** :: ::

        ::

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table class="table" data-nodeid="1">

        <tbody class="tablebody" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4"><span class="span" data-nodeid="5"><em>foo</em></span></td>

        <td class="tabledatum" data-nodeid="7"><span class="span" data-nodeid="8"><strong>bar</strong></span></td>

        </tr>

        </tbody>

        </table>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_table_trshort():
    compare_have_want(
        have="""
        :table:

        :tbody:

        :tr: *foo* : **bar** ::

        ::

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table class="table" data-nodeid="1">

        <tbody class="tablebody" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4"><span class="span" data-nodeid="5"><em>foo</em></span></td>

        <td class="tabledatum" data-nodeid="7"><span class="span" data-nodeid="8"><strong>bar</strong></span></td>

        </tr>

        </tbody>

        </table>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_ignore_space_within_inline():
    compare_have_want(
        have="""
        Ignore space :span: {:strong:} within :: inline.

        Ignore space :span: {:strong:}   within   :: inline.

        Ignore space :claim: within :: inline.

        Ignore space :claim:   within   :: inline.
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Ignore space <span class="span" data-nodeid="3"><strong>within</strong></span> inline.</p>

        </div>

        <div class="paragraph" data-nodeid="6">

        <p>Ignore space <span class="span" data-nodeid="8"><strong>within</strong></span> inline.</p>

        </div>

        <div class="paragraph" data-nodeid="11">

        <p>Ignore space <span class="construct claim" data-nodeid="13"><span class="keyword" data-nodeid="14">⊢</span> within</span> inline.</p>

        </div>

        <div class="paragraph" data-nodeid="18">

        <p>Ignore space <span class="construct claim" data-nodeid="20"><span class="keyword" data-nodeid="21">⊢</span> within</span> inline.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_ignore_space_within_inline_with_shortcut():
    compare_have_want(
        have="""
        Ignore space ** within ** inline.

        Ignore space **   within   ** inline.

        Ignore space :|-: within ::. inline.

        Ignore space :|-:   within   ::. inline.
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Ignore space <span class="span" data-nodeid="3"><strong>within</strong></span> inline.</p>

        </div>

        <div class="paragraph" data-nodeid="6">

        <p>Ignore space <span class="span" data-nodeid="8"><strong>within</strong></span> inline.</p>

        </div>

        <div class="paragraph" data-nodeid="11">

        <p>Ignore space <span class="construct claim" data-nodeid="13"><span class="keyword" data-nodeid="14">⊢</span> within</span>. inline.</p>

        </div>

        <div class="paragraph" data-nodeid="18">

        <p>Ignore space <span class="construct claim" data-nodeid="20"><span class="keyword" data-nodeid="21">⊢</span> within</span>. inline.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_consecutive_lines_should_be_joined_by_spaces():
    compare_have_want(
        have="""
        Consecutive lines should be
        joined by spaces.

        Consecutive lines should :span:{:strong:}be
        joined:: by spaces.

        Consecutive lines should **be
        joined** by spaces.

        Consecutive lines should be
        :span:{:strong:}joined:: by spaces.

        Consecutive lines should be
        **joined** by spaces.

        Consecutive lines should **be**
        joined by spaces.
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p>Consecutive lines should be joined by spaces.</p>

        </div>

        <div class="paragraph" data-nodeid="3">

        <p>Consecutive lines should <span class="span" data-nodeid="5"><strong>be joined</strong></span> by spaces.</p>

        </div>

        <div class="paragraph" data-nodeid="8">

        <p>Consecutive lines should <span class="span" data-nodeid="10"><strong>be joined</strong></span> by spaces.</p>

        </div>

        <div class="paragraph" data-nodeid="13">

        <p>Consecutive lines should be <span class="span" data-nodeid="15"><strong>joined</strong></span> by spaces.</p>

        </div>

        <div class="paragraph" data-nodeid="18">

        <p>Consecutive lines should be <span class="span" data-nodeid="20"><strong>joined</strong></span> by spaces.</p>

        </div>

        <div class="paragraph" data-nodeid="23">

        <p>Consecutive lines should <span class="span" data-nodeid="25"><strong>be</strong></span> joined by spaces.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_span():
    compare_have_want(
        have="""
        :span: foo :: :span: bar ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="span" data-nodeid="2">foo</span> <span class="span" data-nodeid="5">bar</span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_span_construct():
    compare_have_want(
        have="""
        :span: foo :: :prove: bar ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="span" data-nodeid="2">foo</span> <span class="construct prove" data-nodeid="5"><span class="keyword" data-nodeid="6">PROVE</span> bar</span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_construct_construct():
    compare_have_want(
        have="""
        :pick:foo :: :st: bar ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="construct pick assumption" data-nodeid="2"><span class="keyword" data-nodeid="3">PICK</span> foo</span> <span class="construct st assumption" data-nodeid="7"><span class="keyword" data-nodeid="8">SUCH THAT</span> bar</span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_math_math():
    compare_have_want(
        have="""
        $2$ $2$
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="math" data-nodeid="2">\(2\)</span> <span class="math" data-nodeid="5">\(2\)</span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
