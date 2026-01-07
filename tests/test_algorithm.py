from conftest import compare_have_want


def test_real_life_example():
    compare_have_want(
        have=r"""        :rsm:

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

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

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

        </div>

        </body>
        """,
    )


def test_label():
    compare_have_want(
        have=r"""        :rsm:

        :algorithm:
        :label: alg

        \begin{algorithm}
        \caption{Quicksort}
        \begin{algorithmic}
        k=v
        \end{algorithmic}
        \end{algorithm}
        ::

        ::
        """,
        want=r"""        <body>

        <div class="manuscriptwrapper">

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

        </div>

        </body>
        """,
    )
