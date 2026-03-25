from conftest import compare_have_want, compare_have_want_handrails


def test_real_life_example():
    compare_have_want(
        have=r"""
        :algorithm:
        \begin{algorithm}
        \caption{Quicksort}
        \begin{algorithmic}
            \PROCEDURE{Quicksort}{$A, p, r$}
                \IF{$p < r$}
                    \STATE $q = $ \CALL{Partition}{$A, p, r$}
                    \STATE \CALL{Quicksort}{$A, p, q - 1$}
                    \STATE \CALL{Quicksort}{$A, q + 1, r$}
                \ENDIF
            \ENDPROCEDURE
            \PROCEDURE{Partition}{$A, p, r$}
                \STATE $x = A[r]$
                \STATE $i = p - 1$
                \FOR{$j = p$ \TO $r - 1$}
                    \IF{$A[j] < x$}
                        \STATE $i = i + 1$
                        \STATE exchange
                        $A[i]$ with $A[j]$
                    \ENDIF
                    \STATE exchange $A[i]$ with $A[r]$
                \ENDFOR
            \ENDPROCEDURE
        \end{algorithmic}
        \end{algorithm}
        ::
        """,
        want=r"""        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="algorithm">

        <pre class="pseudocode">
        \begin{algorithm}
        \caption{Quicksort}
        \begin{algorithmic}
            \PROCEDURE{Quicksort}{$A, p, r$}
                \IF{$p < r$}
                    \STATE $q = $ \CALL{Partition}{$A, p, r$}
                    \STATE \CALL{Quicksort}{$A, p, q - 1$}
                    \STATE \CALL{Quicksort}{$A, q + 1, r$}
                \ENDIF
            \ENDPROCEDURE
            \PROCEDURE{Partition}{$A, p, r$}
                \STATE $x = A[r]$
                \STATE $i = p - 1$
                \FOR{$j = p$ \TO $r - 1$}
                    \IF{$A[j] < x$}
                        \STATE $i = i + 1$
                        \STATE exchange
                        $A[i]$ with $A[j]$
                    \ENDIF
                    \STATE exchange $A[i]$ with $A[r]$
                \ENDFOR
            \ENDPROCEDURE
        \end{algorithmic}
        \end{algorithm}
        </pre>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_label():
    compare_have_want(
        have=r"""
        :algorithm: {:label: alg}

        \begin{algorithm}
        \caption{Quicksort}
        \begin{algorithmic}
        k=v
        \end{algorithmic}
        \end{algorithm}
        ::
        """,
        want=r"""        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div id="alg" class="algorithm">

        <pre class="pseudocode">
        \begin{algorithm}
        \caption{Quicksort}
        \begin{algorithmic}
        k=v
        \end{algorithmic}
        \end{algorithm}
        </pre>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_handrails():
    compare_have_want_handrails(
        have=r"""
        :algorithm:
        \begin{algorithm}
        \begin{algorithmic}
        \STATE $x = 1$
        \end{algorithmic}
        \end{algorithm}
        ::
        """,
        want=r"""        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="algorithm hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Algorithm 1</span>
          </div>

          <div class="hr-menu-separator"></div>

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

        <pre class="pseudocode">
        \begin{algorithm}
        \begin{algorithmic}
        \STATE $x = 1$
        \end{algorithmic}
        \end{algorithm}
        </pre>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )


def test_handrails_with_label():
    compare_have_want_handrails(
        have=r"""
        :algorithm: {:label: alg-test}
        \begin{algorithm}
        \begin{algorithmic}
        \STATE $x = 1$
        \end{algorithmic}
        \end{algorithm}
        ::
        """,
        want=r"""        <body data-accent="blue" data-lang="en" data-typography="sans-serif">

        <main class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div id="alg-test" class="algorithm hr hr-hidden" tabindex=0 data-nodeid="1">

        <div class="hr-collapse-zone">
        <div class="hr-spacer"></div>
        </div>

        <div class="hr-menu-zone">

        <div class="hr-menu">

          <div class="hr-menu-label">
            <span class="hr-menu-item-text">Algorithm 1</span>
          </div>

          <div class="hr-menu-separator"></div>

          <div class="hr-menu-item link">
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

        <pre class="pseudocode">
        \begin{algorithm}
        \begin{algorithmic}
        \STATE $x = 1$
        \end{algorithmic}
        \end{algorithm}
        </pre>

        </div>

        <div class="hr-info-zone">
        <div class="hr-info"></div>
        </div>

        </div>

        </section>

        </div>

        </main>

        </body>
        """,
    )
