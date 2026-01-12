from conftest import compare_have_want


def test_empty_table():
    compare_have_want(
        have="""\
        :table:

        ::
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table class="table" data-nodeid="1">

        </table>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_one_row_no_header():
    compare_have_want(
        have="""
        :table:

        :tbody:

        :tr: :td:foo:: :td:bar:: ::

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

        <td class="tabledatum" data-nodeid="4">foo</td>

        <td class="tabledatum" data-nodeid="6">bar</td>

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


def test_two_rows_no_header():
    compare_have_want(
        have="""
        :table:

        :tbody:

        :tr: :td:one:: :td:two:: ::

        :tr: :td:three:: :td:four:: ::

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

        <td class="tabledatum" data-nodeid="4">one</td>

        <td class="tabledatum" data-nodeid="6">two</td>

        </tr>

        <tr class="tablerow" data-nodeid="8">

        <td class="tabledatum" data-nodeid="9">three</td>

        <td class="tabledatum" data-nodeid="11">four</td>

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


def test_with_header():
    compare_have_want(
        have="""
        :table:

        :thead:

        :tr: :td: head1 :: :td: head2 :: ::

        ::

        :tbody:

        :tr: :td:one:: :td:two:: ::

        :tr: :td:three:: :td:four:: ::

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

        <thead class="tablehead" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4">head1</td>

        <td class="tabledatum" data-nodeid="6">head2</td>

        </tr>

        </thead>

        <tbody class="tablebody" data-nodeid="8">

        <tr class="tablerow" data-nodeid="9">

        <td class="tabledatum" data-nodeid="10">one</td>

        <td class="tabledatum" data-nodeid="12">two</td>

        </tr>

        <tr class="tablerow" data-nodeid="14">

        <td class="tabledatum" data-nodeid="15">three</td>

        <td class="tabledatum" data-nodeid="17">four</td>

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


def test_math_in_header():
    compare_have_want(
        have=r"""
        :table:

        :thead:

        :tr: :td: $H^{\eta}$ :: :td: $H^{*}$ :: :td: $H^{c}$ :: ::

        ::

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table class="table" data-nodeid="1">

        <thead class="tablehead" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4"><span class="math" data-nodeid="5">\(H^{\eta}\)</span></td>

        <td class="tabledatum" data-nodeid="7"><span class="math" data-nodeid="8">\(H^{*}\)</span></td>

        <td class="tabledatum" data-nodeid="10"><span class="math" data-nodeid="11">\(H^{c}\)</span></td>

        </tr>

        </thead>

        </table>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_shortcuts_in_header():
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


def test_simple_caption():
    compare_have_want(
        have="""
        :table:

        :tbody:

        :tr: :td:foo:: :td:bar:: ::

        ::

        :caption:
        This is a caption.

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

        <td class="tabledatum" data-nodeid="4">foo</td>

        <td class="tabledatum" data-nodeid="6">bar</td>

        </tr>

        </tbody>

        <caption>
        <span class="label">Table 1. </span>This is a caption.
        </caption>

        </table>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_simple_caption_with_shortcuts():
    compare_have_want(
        have="""
        :table:

        :tbody:

        :tr: :td:foo:: :td:bar:: ::

        ::

        :caption:
        This is a *caption* with shortcuts $2+2$.

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table class="table" data-nodeid="1">

        <tbody class="tablebody" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4">foo</td>

        <td class="tabledatum" data-nodeid="6">bar</td>

        </tr>

        </tbody>

        <caption>
        <span class="label">Table 1. </span>This is a <span class="span" data-nodeid="10"><em>caption</em></span> with shortcuts <span class="math" data-nodeid="13">\(2+2\)</span>.
        </caption>

        </table>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_reference_to_table():
    compare_have_want(
        have="""
        :table:{:label: lbl}

        :tbody:

        :tr: :td:foo:: :td:bar:: ::

        ::

        ::

        This :ref:lbl:: refers to the table.
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table id="lbl" class="table" data-nodeid="1">

        <tbody class="tablebody" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4">foo</td>

        <td class="tabledatum" data-nodeid="6">bar</td>

        </tr>

        </tbody>

        </table>

        </div>

        <div class="paragraph" data-nodeid="8">

        <p>This <a class="reference" href="#lbl">Table 1</a> refers to the table.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_reference_to_table_with_reftext():
    compare_have_want(
        have="""
        :table: {:label: lbl}

        :tbody:

        :tr: :td:foo:: :td:bar:: ::

        ::

        ::

        This :ref:lbl,refers:: to the table.
        """,
        want="""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table id="lbl" class="table" data-nodeid="1">

        <tbody class="tablebody" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4">foo</td>

        <td class="tabledatum" data-nodeid="6">bar</td>

        </tr>

        </tbody>

        </table>

        </div>

        <div class="paragraph" data-nodeid="8">

        <p>This <a class="reference" href="#lbl">refers</a> to the table.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_extra_space_within_tr():
    compare_have_want(
        have="""
        :table:

        :tbody:

        :tr:
          :td:foo::
          :td:bar::
        ::

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

        <td class="tabledatum" data-nodeid="4">foo</td>

        <td class="tabledatum" data-nodeid="6">bar</td>

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


def test_real_life_example():
    compare_have_want(
        have=r"""
        :table: {:label: lbl}

          :thead:
            :tr: :td: $H^{\tau}$ :: :td: $H^{*}$ :: :td: $H^{c}$ :: ::
          ::
          :tbody:
            :tr: :td: $0.0001$ :: :td: $0.0146$ :: :td: $0.0549$ :: ::
            :tr: :td: $0.1222$ :: :td: $0.0139$ :: :td: $0.0106$ :: ::

          ::

          :caption:
          Values of $\epsilon$ and $\delta$ for select subgraphs of Gr-Qc.

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table id="lbl" class="table" data-nodeid="1">

        <thead class="tablehead" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4"><span class="math" data-nodeid="5">\(H^{\tau}\)</span></td>

        <td class="tabledatum" data-nodeid="7"><span class="math" data-nodeid="8">\(H^{*}\)</span></td>

        <td class="tabledatum" data-nodeid="10"><span class="math" data-nodeid="11">\(H^{c}\)</span></td>

        </tr>

        </thead>

        <tbody class="tablebody" data-nodeid="13">

        <tr class="tablerow" data-nodeid="14">

        <td class="tabledatum" data-nodeid="15"><span class="math" data-nodeid="16">\(0.0001\)</span></td>

        <td class="tabledatum" data-nodeid="18"><span class="math" data-nodeid="19">\(0.0146\)</span></td>

        <td class="tabledatum" data-nodeid="21"><span class="math" data-nodeid="22">\(0.0549\)</span></td>

        </tr>

        <tr class="tablerow" data-nodeid="24">

        <td class="tabledatum" data-nodeid="25"><span class="math" data-nodeid="26">\(0.1222\)</span></td>

        <td class="tabledatum" data-nodeid="28"><span class="math" data-nodeid="29">\(0.0139\)</span></td>

        <td class="tabledatum" data-nodeid="31"><span class="math" data-nodeid="32">\(0.0106\)</span></td>

        </tr>

        </tbody>

        <caption>
        <span class="label">Table 1. </span>Values of <span class="math" data-nodeid="36">\(\epsilon\)</span> and <span class="math" data-nodeid="39">\(\delta\)</span> for select subgraphs of Gr-Qc.
        </caption>

        </table>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_real_life_example_different_spacing():
    compare_have_want(
        have=r"""
        :table:
        {  :label: lbl}

          :thead:
          :tr:
            :td: $H^{\tau}$ ::
            :td: $H^{*}$ ::
            :td: $H^{c}$ :: ::
          ::
          :tbody:
          :tr:
            :td: $0.0001$ ::
            :td: $0.0146$ ::
            :td: $0.0549$ :: ::
          :tr:
            :td: $0.1222$ ::
            :td: $0.0139$ ::
            :td: $0.0106$ ::
          ::
          ::

          :caption:
          Values of $\epsilon$ and $\delta$ for select subgraphs of Gr-Qc.

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table id="lbl" class="table" data-nodeid="1">

        <thead class="tablehead" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4"><span class="math" data-nodeid="5">\(H^{\tau}\)</span></td>

        <td class="tabledatum" data-nodeid="7"><span class="math" data-nodeid="8">\(H^{*}\)</span></td>

        <td class="tabledatum" data-nodeid="10"><span class="math" data-nodeid="11">\(H^{c}\)</span></td>

        </tr>

        </thead>

        <tbody class="tablebody" data-nodeid="13">

        <tr class="tablerow" data-nodeid="14">

        <td class="tabledatum" data-nodeid="15"><span class="math" data-nodeid="16">\(0.0001\)</span></td>

        <td class="tabledatum" data-nodeid="18"><span class="math" data-nodeid="19">\(0.0146\)</span></td>

        <td class="tabledatum" data-nodeid="21"><span class="math" data-nodeid="22">\(0.0549\)</span></td>

        </tr>

        <tr class="tablerow" data-nodeid="24">

        <td class="tabledatum" data-nodeid="25"><span class="math" data-nodeid="26">\(0.1222\)</span></td>

        <td class="tabledatum" data-nodeid="28"><span class="math" data-nodeid="29">\(0.0139\)</span></td>

        <td class="tabledatum" data-nodeid="31"><span class="math" data-nodeid="32">\(0.0106\)</span></td>

        </tr>

        </tbody>

        <caption>
        <span class="label">Table 1. </span>Values of <span class="math" data-nodeid="36">\(\epsilon\)</span> and <span class="math" data-nodeid="39">\(\delta\)</span> for select subgraphs of Gr-Qc.
        </caption>

        </table>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_tr_shortcut():
    compare_have_want(
        have="""
        :table:

        :thead:
        :tr: foo : bar : baz ::
        ::
        :tbody:
        :tr: a1 : a2 : a3 ::
        :tr: b1 : b2 : b3 ::
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

        <thead class="tablehead" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4">foo</td>

        <td class="tabledatum" data-nodeid="6">bar</td>

        <td class="tabledatum" data-nodeid="8">baz</td>

        </tr>

        </thead>

        <tbody class="tablebody" data-nodeid="10">

        <tr class="tablerow" data-nodeid="11">

        <td class="tabledatum" data-nodeid="12">a1</td>

        <td class="tabledatum" data-nodeid="14">a2</td>

        <td class="tabledatum" data-nodeid="16">a3</td>

        </tr>

        <tr class="tablerow" data-nodeid="18">

        <td class="tabledatum" data-nodeid="19">b1</td>

        <td class="tabledatum" data-nodeid="21">b2</td>

        <td class="tabledatum" data-nodeid="23">b3</td>

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


def test_tr_shortcut_with_math():
    compare_have_want(
        have=r"""
        :table:

        :thead:
        :tr: $H^{\tau}$ : $H^{\top}$ : $H^{c}$ ::
        ::
        :tbody:
        :tr: $0.0001$ : $0.0146$ : $0.0549$ ::
        :tr: $0.1222$ : $0.0139$ : $0.0106$ ::
        ::

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table class="table" data-nodeid="1">

        <thead class="tablehead" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4"><span class="math" data-nodeid="5">\(H^{\tau}\)</span></td>

        <td class="tabledatum" data-nodeid="7"><span class="math" data-nodeid="8">\(H^{\top}\)</span></td>

        <td class="tabledatum" data-nodeid="10"><span class="math" data-nodeid="11">\(H^{c}\)</span></td>

        </tr>

        </thead>

        <tbody class="tablebody" data-nodeid="13">

        <tr class="tablerow" data-nodeid="14">

        <td class="tabledatum" data-nodeid="15"><span class="math" data-nodeid="16">\(0.0001\)</span></td>

        <td class="tabledatum" data-nodeid="18"><span class="math" data-nodeid="19">\(0.0146\)</span></td>

        <td class="tabledatum" data-nodeid="21"><span class="math" data-nodeid="22">\(0.0549\)</span></td>

        </tr>

        <tr class="tablerow" data-nodeid="24">

        <td class="tabledatum" data-nodeid="25"><span class="math" data-nodeid="26">\(0.1222\)</span></td>

        <td class="tabledatum" data-nodeid="28"><span class="math" data-nodeid="29">\(0.0139\)</span></td>

        <td class="tabledatum" data-nodeid="31"><span class="math" data-nodeid="32">\(0.0106\)</span></td>

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


def test_tr_shortcut_with_newlines():
    compare_have_want(
        have="""
        :table:

        :thead:
        :tr:
        foo : bar : baz
        ::
        ::
        :tbody:
        :tr:
        a1 : a2 : a3
        ::
        :tr:
        b1 : b2 : b3
        ::
        ::

        ::
        """,
        want="""        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="table-wrapper">

        <table class="table" data-nodeid="1">

        <thead class="tablehead" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4">foo</td>

        <td class="tabledatum" data-nodeid="6">bar</td>

        <td class="tabledatum" data-nodeid="8">baz</td>

        </tr>

        </thead>

        <tbody class="tablebody" data-nodeid="10">

        <tr class="tablerow" data-nodeid="11">

        <td class="tabledatum" data-nodeid="12">a1</td>

        <td class="tabledatum" data-nodeid="14">a2</td>

        <td class="tabledatum" data-nodeid="16">a3</td>

        </tr>

        <tr class="tablerow" data-nodeid="18">

        <td class="tabledatum" data-nodeid="19">b1</td>

        <td class="tabledatum" data-nodeid="21">b2</td>

        <td class="tabledatum" data-nodeid="23">b3</td>

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


def test_tr_shortcut_with_escaped_colon():
    compare_have_want(
        have=r"""
        :table:

        :thead:
        :tr: foo : bar : baz ::
        ::
        :tbody:
        :tr: a\: : a2 : a3 ::
        :tr: b1  : b2 : b3 ::
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

        <thead class="tablehead" data-nodeid="2">

        <tr class="tablerow" data-nodeid="3">

        <td class="tabledatum" data-nodeid="4">foo</td>

        <td class="tabledatum" data-nodeid="6">bar</td>

        <td class="tabledatum" data-nodeid="8">baz</td>

        </tr>

        </thead>

        <tbody class="tablebody" data-nodeid="10">

        <tr class="tablerow" data-nodeid="11">

        <td class="tabledatum" data-nodeid="12">a:</td>

        <td class="tabledatum" data-nodeid="14">a2</td>

        <td class="tabledatum" data-nodeid="16">a3</td>

        </tr>

        <tr class="tablerow" data-nodeid="18">

        <td class="tabledatum" data-nodeid="19">b1</td>

        <td class="tabledatum" data-nodeid="21">b2</td>

        <td class="tabledatum" data-nodeid="23">b3</td>

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
