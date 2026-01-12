from conftest import compare_have_want


def test_code():
    compare_have_want(
        have="""\
        :code: comp = [abs(x) for x in range(10)] ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="code" data-nodeid="2"><code>comp = [abs(x) for x in range(10)]</code></span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_code_with_shorthand():
    compare_have_want(
        have="""\
        `comp = [abs(x) for x in range(10)]`
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="code" data-nodeid="2"><code>comp = [abs(x) for x in range(10)]</code></span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_code_with_lang():
    compare_have_want(
        have="""\
        :code: {:lang: python}
          comp = [abs(x) for x in range(10)]
        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="code" data-nodeid="2"><code class="highlight python"><span class="n">comp</span> <span class="o">=</span> <span class="p">[</span><span class="nb">abs</span><span class="p">(</span><span class="n">x</span><span class="p">)</span> <span class="k">for</span> <span class="n">x</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="mi">10</span><span class="p">)]</span>
        </code></span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_code_with_shorthand_and_lang():
    compare_have_want(
        have="""\
        `{:lang: python} comp = [abs(x) for x in range(10)]`
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="code" data-nodeid="2"><code class="highlight python"><span class="n">comp</span> <span class="o">=</span> <span class="p">[</span><span class="nb">abs</span><span class="p">(</span><span class="n">x</span><span class="p">)</span> <span class="k">for</span> <span class="n">x</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="mi">10</span><span class="p">)]</span>
        </code></span></p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_codeblock():
    compare_have_want(
        have="""\
        :codeblock:

          comp = [abs(x) for x in range(10)]

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code>comp = [abs(x) for x in range(10)]</code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_codeblock_with_lang():
    compare_have_want(
        have="""\
        :codeblock: {:lang: python}

          comp = [abs(x) for x in range(10)]

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code class="highlight python"><span class="n">comp</span> <span class="o">=</span> <span class="p">[</span><span class="nb">abs</span><span class="p">(</span><span class="n">x</span><span class="p">)</span> <span class="k">for</span> <span class="n">x</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="mi">10</span><span class="p">)]</span>
        </code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_codeblock_with_shorthand():
    compare_have_want(
        have="""\
        ```
        comp = [abs(x) for x in range(10)]
        ```
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code>comp = [abs(x) for x in range(10)]</code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_codeblock_with_shorthand_and_lang():
    compare_have_want(
        have="""\
        ```{:lang: python}

        comp = [abs(x) for x in range(10)]

        ```
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code class="highlight python"><span class="n">comp</span> <span class="o">=</span> <span class="p">[</span><span class="nb">abs</span><span class="p">(</span><span class="n">x</span><span class="p">)</span> <span class="k">for</span> <span class="n">x</span> <span class="ow">in</span> <span class="nb">range</span><span class="p">(</span><span class="mi">10</span><span class="p">)]</span>
        </code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_meta():
    compare_have_want(
        have="""\
        `{:label: 1}k=v`

        :code:{:label: 2}k=v::

        :codeblock: {
          :label: 3
        }
          k = v
        ::

        ```
          {:label: 4}
          k = v
        ```
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span id="1" class="code" data-nodeid="2"><code>k=v</code></span></p>

        </div>

        <div class="paragraph" data-nodeid="4">

        <p><span id="2" class="code" data-nodeid="5"><code>k=v</code></span></p>

        </div>

        <div id="3" class="codeblock" data-nodeid="7">

        <pre>
        <code>k = v</code>
        </pre>

        </div>

        <div id="4" class="codeblock" data-nodeid="9">

        <pre>
        <code>k = v</code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_meta_and_lang():
    compare_have_want(
        have="""\
        `{:label: 1, :lang: js}k=v`

        :code:{:label: 2, :lang: js}k=v::

        :codeblock: {
          :label: 3
          :lang: js
        }
          k = v
        ::

        ``` {
          :label: 4
          :lang: js
        }
          k = v
        ```
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span id="1" class="code" data-nodeid="2"><code class="highlight js"><span class="nx">k</span><span class="o">=</span><span class="nx">v</span>
        </code></span></p>

        </div>

        <div class="paragraph" data-nodeid="4">

        <p><span id="2" class="code" data-nodeid="5"><code class="highlight js"><span class="nx">k</span><span class="o">=</span><span class="nx">v</span>
        </code></span></p>

        </div>

        <div id="3" class="codeblock" data-nodeid="7">

        <pre>
        <code class="highlight js"><span class="nx">k</span><span class="w"> </span><span class="o">=</span><span class="w"> </span><span class="nx">v</span>
        </code>
        </pre>

        </div>

        <div id="4" class="codeblock" data-nodeid="9">

        <pre>
        <code class="highlight js"><span class="nx">k</span><span class="w"> </span><span class="o">=</span><span class="w"> </span><span class="nx">v</span>
        </code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_multiline_codeblock():
    compare_have_want(
        have="""\
        :codeblock:

        import sys
        print(sys.argv)

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code>import sys
        print(sys.argv)</code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_multiline_codeblock_with_lang():
    compare_have_want(
        have="""\
        :codeblock:{:lang: python}

        import sys
        print(sys.argv)

        ::
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code class="highlight python"><span class="kn">import</span><span class="w"> </span><span class="nn">sys</span>
        <span class="nb">print</span><span class="p">(</span><span class="n">sys</span><span class="o">.</span><span class="n">argv</span><span class="p">)</span>
        </code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_multiline_codeblock_with_shorthand():
    compare_have_want(
        have="""\
        ```
        import sys
        print(sys.argv)
        ```
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code>import sys
        print(sys.argv)</code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_multiline_codeblock_with_shorthand_and_lang():
    compare_have_want(
        have="""\
        ```
        {:lang: python}

        import sys
        print(sys.argv)

        ```
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="codeblock" data-nodeid="1">

        <pre>
        <code class="highlight python"><span class="kn">import</span><span class="w"> </span><span class="nn">sys</span>
        <span class="nb">print</span><span class="p">(</span><span class="n">sys</span><span class="o">.</span><span class="n">argv</span><span class="p">)</span>
        </code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_multiline_meta():
    compare_have_want(
        have="""\
        :codeblock:{:label: 3}
        k = v
        key = val
        ::

        ```
        {:label: 4}
        k = v
        key = val
        ```
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div id="3" class="codeblock" data-nodeid="1">

        <pre>
        <code>k = v
        key = val</code>
        </pre>

        </div>

        <div id="4" class="codeblock" data-nodeid="3">

        <pre>
        <code>k = v
        key = val</code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_multiline_meta_and_lang():
    compare_have_want(
        have="""\
        :codeblock: {
          :label: 3
          :lang: lisp
        }
        (defun forall (list func)
         (if (null list)
           t
           (and (funcall func (car list))
           (forall (cdr list) func))))
        ::

        ``` {
          :label: 4
          :lang: lisp
        }
        (defun forall (list func)
         (if (null list)
           t
           (and (funcall func (car list))
           (forall (cdr list) func))))
        ```
        """,
        want="""\
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div id="3" class="codeblock" data-nodeid="1">

        <pre>
        <code class="highlight lisp"><span class="p">(</span><span class="nb">defun</span><span class="w"> </span><span class="nv">forall</span><span class="w"> </span><span class="p">(</span><span class="nb">list</span><span class="w"> </span><span class="nv">func</span><span class="p">)</span>
        <span class="w"> </span><span class="p">(</span><span class="k">if</span><span class="w"> </span><span class="p">(</span><span class="nb">null</span><span class="w"> </span><span class="nb">list</span><span class="p">)</span>
        <span class="w">   </span><span class="no">t</span>
        <span class="w">   </span><span class="p">(</span><span class="nb">and</span><span class="w"> </span><span class="p">(</span><span class="nb">funcall</span><span class="w"> </span><span class="nv">func</span><span class="w"> </span><span class="p">(</span><span class="nb">car</span><span class="w"> </span><span class="nb">list</span><span class="p">))</span>
        <span class="w">   </span><span class="p">(</span><span class="nv">forall</span><span class="w"> </span><span class="p">(</span><span class="nb">cdr</span><span class="w"> </span><span class="nb">list</span><span class="p">)</span><span class="w"> </span><span class="nv">func</span><span class="p">))))</span>
        </code>
        </pre>

        </div>

        <div id="4" class="codeblock" data-nodeid="3">

        <pre>
        <code class="highlight lisp"><span class="p">(</span><span class="nb">defun</span><span class="w"> </span><span class="nv">forall</span><span class="w"> </span><span class="p">(</span><span class="nb">list</span><span class="w"> </span><span class="nv">func</span><span class="p">)</span>
        <span class="w"> </span><span class="p">(</span><span class="k">if</span><span class="w"> </span><span class="p">(</span><span class="nb">null</span><span class="w"> </span><span class="nb">list</span><span class="p">)</span>
        <span class="w">   </span><span class="no">t</span>
        <span class="w">   </span><span class="p">(</span><span class="nb">and</span><span class="w"> </span><span class="p">(</span><span class="nb">funcall</span><span class="w"> </span><span class="nv">func</span><span class="w"> </span><span class="p">(</span><span class="nb">car</span><span class="w"> </span><span class="nb">list</span><span class="p">))</span>
        <span class="w">   </span><span class="p">(</span><span class="nv">forall</span><span class="w"> </span><span class="p">(</span><span class="nb">cdr</span><span class="w"> </span><span class="nb">list</span><span class="p">)</span><span class="w"> </span><span class="nv">func</span><span class="p">))))</span>
        </code>
        </pre>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
