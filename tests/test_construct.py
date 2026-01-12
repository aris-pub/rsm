from conftest import compare_have_want


def test_real_life_example():
    compare_have_want(
        have=r"""
        # A simple proof

        :let: $G$ be a simple graph::.  We will prove a fundamental fact about its structure.
        :define: $L(G) := |E(G)|$, where $E(G)$ is the set of edges of $G$:: and :write:
        $\deg(u)$ for the degree of a node $u \in V(G)$::.

        :theorem: {
          :label: thm-main
          :goal: eqn-thm
          :types: {important, main}
        }

          We have
          $${:label: eqn-thm}
            \sum_{u \in V(G)} \deg(u) = 2L(G).
          $$

        ::

        :proof:

          :step: :define: $n = |V(G)|$.:: ::

          :step: :case: $n = 1$.::

            :step: :claim: $L(G) = 0$ ::.

              :p: $G$ has no self-loops by assumption.::

            ::

            :step: :let: $u \in V(G)$::, :then: $\deg(u) = 0$::.

              :p: Since $G$ has only one node, and it has no self-loops.::

            ::

            :step: :qed:
            ::

          ::

          :step: :let: $v \notin V(G)$::.  :write: $H$ for the graph resulting from adding $v$
            to $G$::. SUFFICES :assume: :span: :span:{:label: asm} the theorem is true for $G$
            ::::::, :prove: the theorem is true for $H$::.

            :p: By induction. ::

          ::

          :step: :define: $\deg_G(u), \deg_H(u)$ as the degree of node $u$ in
            $G$ and $H$ respectively.:: Note $\deg_G(v) = 0$. ::

          :step:{:label: stp-edges}

            :claim: $L(H) = L(G) + \deg_H(v)$::.

            :p: Because the only added edges are those incident to $v$.::

          ::

          :step:{:label: stp-sum}
            :claim: $\sum_{u \in V(H)} \deg_H(u) = 2\deg_H(v) + \sum_{u \in V(G)} \deg_G(u)$::.

            :step: :write: $W \subset V(G)$ for the set of neighbors of $v$.::::

            :step: We have
              $$
                \begin{align}
                \sum_{u \in V(H)} \deg_H(u) &= \phantom{2} \deg_H(v) + \sum_{u \in V(H)\setminus\{v\}} \deg_H(u) \\
                \sum_{u \in V(H)} \deg_H(u) &= \phantom{2} \deg_H(v) + \sum_{u \in W} \deg_H(u) + \sum_{u \in V(H) \setminus W \setminus \{v\}} \deg_H(u) \\
                \sum_{u \in V(H)} \deg_H(u) &= \phantom{2} \deg_H(v) + \sum_{u \in W} (\deg_G(u) + 1) + \sum_{u \in V(H) \setminus W \setminus \{v\}} \deg_G(u) \\
                \sum_{u \in V(H)} \deg_H(u) &= 2\deg_H(v) + \sum_{u \in W} \deg_G(u) + \sum_{u \in V(H) \setminus W \setminus \{v\}} \deg_G(u) \\
                \sum_{u \in V(H)} \deg_H(u) &= 2\deg_H(v) + \sum_{u \in V(G)} \deg_G(u),
                \end{align}
              $$

              where in the right-most term in third equation we have used the fact that for
              every node $u$ in $V(G) \setminus W \setminus v$ we have $\deg_H(u) = \deg_G(u)$.

            ::

          ::

          :step: :qed:

            :p: We have
              $$
                \begin{align}
                2 L(G) &= \sum_{u \in V(G)} \deg_G(u) \\
                2 L(G) + 2 \deg_H(v) &=  2 \deg_H(v) + \sum_{u \in V(G)} \deg_G(u) \\
                2 L(H) &=  \sum_{u \in V(H)} \deg_H(u),
                \end{align}
              $$

              where the first equation is true by :ref:asm,induction hypothesis::, and the last
              equation is due to :prev2: and :prev:.

            ::

          ::
        ::
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <h1>A simple proof</h1>

        <div class="paragraph" data-nodeid="1">

        <p><span class="construct let assumption" data-nodeid="2"><span class="keyword" data-nodeid="3">LET</span> <span class="math" data-nodeid="6">\(G\)</span> be a simple graph</span>.  We will prove a fundamental fact about its structure. <span class="construct define assumption" data-nodeid="10"><span class="keyword" data-nodeid="11">DEFINE</span> <span class="math" data-nodeid="14">\(L(G) := |E(G)|\)</span>, where <span class="math" data-nodeid="17">\(E(G)\)</span> is the set of edges of <span class="math" data-nodeid="20">\(G\)</span></span> and <span class="construct write assumption" data-nodeid="23"><span class="keyword" data-nodeid="24">WRITE</span> <span class="math" data-nodeid="27">\(\deg(u)\)</span> for the degree of a node <span class="math" data-nodeid="30">\(u \in V(G)\)</span></span>.</p>

        </div>

        <div id="thm-main" class="theorem important main" data-nodeid="33">

        <div class="paragraph hr-label">

        <p><span class="span label">Theorem 1.</span></p>

        </div>

        <div class="paragraph" data-nodeid="34">

        <p>We have </p>
        <div id="eqn-thm" class="mathblock" data-nodeid="36">
        $$
        \sum_{u \in V(G)} \deg(u) = 2L(G).
        $$
        </div>

        </div>

        </div>

        <div class="proof" data-nodeid="38">

        <div class="paragraph hr-label">

        <p><span class="span label">Proof.</span></p>

        </div>

        <div class="step" data-nodeid="39">

        <div class="statement" data-nodeid="40">

        <div class="paragraph" data-nodeid="41">

        <p><span class="construct define assumption" data-nodeid="42"><span class="keyword" data-nodeid="43">DEFINE</span> <span class="math" data-nodeid="46">\(n = |V(G)|\)</span>.</span></p>

        </div>

        </div>

        </div>

        <div class="step" data-nodeid="49">

        <div class="statement" data-nodeid="50">

        <div class="paragraph" data-nodeid="51">

        <p><span class="construct case assumption" data-nodeid="52"><span class="keyword" data-nodeid="53">CASE</span> <span class="math" data-nodeid="56">\(n = 1\)</span>.</span></p>

        </div>

        </div>

        <div class="subproof" data-nodeid="59">

        <div class="step" data-nodeid="60">

        <div class="statement" data-nodeid="61">

        <div class="paragraph" data-nodeid="62">

        <p><span class="construct claim" data-nodeid="63"><span class="keyword" data-nodeid="64">⊢</span> <span class="math" data-nodeid="67">\(L(G) = 0\)</span></span>.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="70">

        <div class="paragraph" data-nodeid="71">

        <p><span class="math" data-nodeid="72">\(G\)</span> has no self-loops by assumption.</p>

        </div>

        </div>

        </div>

        <div class="step" data-nodeid="75">

        <div class="statement" data-nodeid="76">

        <div class="paragraph" data-nodeid="77">

        <p><span class="construct let assumption" data-nodeid="78"><span class="keyword" data-nodeid="79">LET</span> <span class="math" data-nodeid="82">\(u \in V(G)\)</span></span>, <span class="construct then" data-nodeid="85"><span class="keyword" data-nodeid="86">THEN</span> <span class="math" data-nodeid="89">\(\deg(u) = 0\)</span></span>.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="92">

        <div class="paragraph" data-nodeid="93">

        <p>Since <span class="math" data-nodeid="95">\(G\)</span> has only one node, and it has no self-loops.</p>

        </div>

        </div>

        </div>

        <div class="step" data-nodeid="98">

        <div class="statement" data-nodeid="99">

        <div class="paragraph" data-nodeid="100">

        <p><span class="construct qed" data-nodeid="101"><span class="keyword" data-nodeid="102">QED</span></span></p>

        </div>

        </div>

        </div>

        </div>

        </div>

        <div class="step" data-nodeid="104">

        <div class="statement" data-nodeid="105">

        <div class="paragraph" data-nodeid="106">

        <p><span class="construct let assumption" data-nodeid="107"><span class="keyword" data-nodeid="108">LET</span> <span class="math" data-nodeid="111">\(v \notin V(G)\)</span></span>. <span class="construct write assumption" data-nodeid="114"><span class="keyword" data-nodeid="115">WRITE</span> <span class="math" data-nodeid="118">\(H\)</span> for the graph resulting from adding <span class="math" data-nodeid="121">\(v\)</span> to <span class="math" data-nodeid="124">\(G\)</span></span>. SUFFICES <span class="construct assume assumption" data-nodeid="127"><span class="keyword" data-nodeid="128">ASSUME</span><span class="span" data-nodeid="130"><span id="asm" class="span" data-nodeid="131">the theorem is true for <span class="math" data-nodeid="133">\(G\)</span></span></span></span>, <span class="construct prove" data-nodeid="136"><span class="keyword" data-nodeid="137">PROVE</span> the theorem is true for <span class="math" data-nodeid="140">\(H\)</span></span>.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="143">

        <div class="paragraph" data-nodeid="144">

        <p>By induction.</p>

        </div>

        </div>

        </div>

        <div class="step" data-nodeid="146">

        <div class="statement" data-nodeid="147">

        <div class="paragraph" data-nodeid="148">

        <p><span class="construct define assumption" data-nodeid="149"><span class="keyword" data-nodeid="150">DEFINE</span> <span class="math" data-nodeid="153">\(\deg_G(u), \deg_H(u)\)</span> as the degree of node <span class="math" data-nodeid="156">\(u\)</span> in <span class="math" data-nodeid="159">\(G\)</span> and <span class="math" data-nodeid="162">\(H\)</span> respectively.</span> Note <span class="math" data-nodeid="166">\(\deg_G(v) = 0\)</span>.</p>

        </div>

        </div>

        </div>

        <div id="stp-edges" class="step" data-nodeid="169">

        <div class="statement" data-nodeid="170">

        <div class="paragraph" data-nodeid="171">

        <p><span class="construct claim" data-nodeid="172"><span class="keyword" data-nodeid="173">⊢</span> <span class="math" data-nodeid="176">\(L(H) = L(G) + \deg_H(v)\)</span></span>.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="179">

        <div class="paragraph" data-nodeid="180">

        <p>Because the only added edges are those incident to <span class="math" data-nodeid="182">\(v\)</span>.</p>

        </div>

        </div>

        </div>

        <div id="stp-sum" class="step" data-nodeid="185">

        <div class="statement" data-nodeid="186">

        <div class="paragraph" data-nodeid="187">

        <p><span class="construct claim" data-nodeid="188"><span class="keyword" data-nodeid="189">⊢</span> <span class="math" data-nodeid="192">\(\sum_{u \in V(H)} \deg_H(u) = 2\deg_H(v) + \sum_{u \in V(G)} \deg_G(u)\)</span></span>.</p>

        </div>

        </div>

        <div class="subproof" data-nodeid="195">

        <div class="step" data-nodeid="196">

        <div class="statement" data-nodeid="197">

        <div class="paragraph" data-nodeid="198">

        <p><span class="construct write assumption" data-nodeid="199"><span class="keyword" data-nodeid="200">WRITE</span> <span class="math" data-nodeid="203">\(W \subset V(G)\)</span> for the set of neighbors of <span class="math" data-nodeid="206">\(v\)</span>.</span></p>

        </div>

        </div>

        </div>

        <div class="step" data-nodeid="209">

        <div class="statement" data-nodeid="210">

        <div class="paragraph" data-nodeid="211">

        <p>We have </p>
        <div class="mathblock" data-nodeid="213">
        $$
        \begin{align}
                \sum_{u \in V(H)} \deg_H(u) &= \phantom{2} \deg_H(v) + \sum_{u \in V(H)\setminus\{v\}} \deg_H(u) \\
                \sum_{u \in V(H)} \deg_H(u) &= \phantom{2} \deg_H(v) + \sum_{u \in W} \deg_H(u) + \sum_{u \in V(H) \setminus W \setminus \{v\}} \deg_H(u) \\
                \sum_{u \in V(H)} \deg_H(u) &= \phantom{2} \deg_H(v) + \sum_{u \in W} (\deg_G(u) + 1) + \sum_{u \in V(H) \setminus W \setminus \{v\}} \deg_G(u) \\
                \sum_{u \in V(H)} \deg_H(u) &= 2\deg_H(v) + \sum_{u \in W} \deg_G(u) + \sum_{u \in V(H) \setminus W \setminus \{v\}} \deg_G(u) \\
                \sum_{u \in V(H)} \deg_H(u) &= 2\deg_H(v) + \sum_{u \in V(G)} \deg_G(u),
                \end{align}
        $$
        </div>

        </div>

        <div class="paragraph" data-nodeid="215">

        <p>where in the right-most term in third equation we have used the fact that for every node <span class="math" data-nodeid="217">\(u\)</span> in <span class="math" data-nodeid="220">\(V(G) \setminus W \setminus v\)</span> we have <span class="math" data-nodeid="223">\(\deg_H(u) = \deg_G(u)\)</span>.</p>

        </div>

        </div>

        </div>

        </div>

        </div>

        <div class="step last" data-nodeid="226">

        <div class="statement" data-nodeid="227">

        <div class="paragraph" data-nodeid="228">

        <p><span class="construct qed" data-nodeid="229"><span class="keyword" data-nodeid="230">QED</span></span></p>

        </div>

        </div>

        <div class="subproof" data-nodeid="232">

        <div class="paragraph" data-nodeid="233">

        <p>We have </p>
        <div class="mathblock" data-nodeid="235">
        $$
        \begin{align}
                2 L(G) &= \sum_{u \in V(G)} \deg_G(u) \\
                2 L(G) + 2 \deg_H(v) &=  2 \deg_H(v) + \sum_{u \in V(G)} \deg_G(u) \\
                2 L(H) &=  \sum_{u \in V(H)} \deg_H(u),
                \end{align}
        $$
        </div>

        </div>

        <div class="paragraph" data-nodeid="237">

        <p>where the first equation is true by <a class="reference" href="#asm">induction hypothesis</a>, and the last equation is due to <a class="reference" href="#stp-edges">Step ⟨5⟩</a> and <a class="reference" href="#stp-sum">Step ⟨6⟩</a>.</p>

        </div>

        </div>

        </div>

        <div class="halmos"></div>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )


def test_construct_at_line_start():
    """Regression test: construct tags at start of line should start new construct, not be consumed as TEXT."""
    compare_have_want(
        have=r"""
        :let: $G$ be a simple graph::.  We will prove a fact.
        :define: $L(G) := |E(G)|$, where $E(G)$ is the set of edges::.

        More text here.
        """,
        want=r"""
        <body>

        <div class="manuscriptwrapper">

        <div class="manuscript" data-nodeid="0">

        <section class="level-1">

        <div class="paragraph" data-nodeid="1">

        <p><span class="construct let assumption" data-nodeid="2"><span class="keyword" data-nodeid="3">LET</span> <span class="math" data-nodeid="6">\(G\)</span> be a simple graph</span>.  We will prove a fact. <span class="construct define assumption" data-nodeid="10"><span class="keyword" data-nodeid="11">DEFINE</span> <span class="math" data-nodeid="14">\(L(G) := |E(G)|\)</span>, where <span class="math" data-nodeid="17">\(E(G)\)</span> is the set of edges</span>.</p>

        </div>

        <div class="paragraph" data-nodeid="21">

        <p>More text here.</p>

        </div>

        </section>

        </div>

        </div>

        </body>
        """,
    )
