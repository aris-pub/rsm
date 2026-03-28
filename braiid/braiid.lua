-- braiid.lua — Pandoc Lua filter for theorem environments.
--
-- Maps Div nodes with semantic classes (theorem, definition, proof, etc.)
-- to format-specific environments. For LaTeX: \begin{...}\end{...}.
-- For Typst: styled blocks with blue left border and Halmos squares.

local theorem_envs = {
  theorem = true,
  definition = true,
  proposition = true,
  lemma = true,
  corollary = true,
  remark = true,
  example = true,
  exercise = true,
  problem = true,
  porism = true,
}

local fmt = FORMAT

function Div(el)
  for _, cls in ipairs(el.classes) do
    if cls == "proof" then
      if fmt:match("latex") then
        return {pandoc.RawBlock("latex", "\\begin{proof}")}
          .. el.content
          .. {pandoc.RawBlock("latex", "\\end{proof}")}
      elseif fmt:match("typst") then
        return {pandoc.RawBlock("typst",
          '#block(spacing: 1.2em)[')}
          .. el.content
          .. {pandoc.RawBlock("typst",
          '#v(-0.8em)\n#align(right, box(width: 6pt, height: 6pt, fill: rgb("#0361A1")))\n]')}
      end
    end
    if theorem_envs[cls] then
      if fmt:match("latex") then
        local label = ""
        if el.identifier and el.identifier ~= "" then
          label = "\\label{" .. el.identifier .. "}"
        end
        return {pandoc.RawBlock("latex", "\\begin{" .. cls .. "}" .. label)}
          .. el.content
          .. {pandoc.RawBlock("latex", "\\end{" .. cls .. "}")}
      elseif fmt:match("typst") then
        local anchor = ""
        if el.identifier and el.identifier ~= "" then
          anchor = " <" .. el.identifier .. ">"
        end
        return {pandoc.RawBlock("typst",
          '#block(stroke: (left: 1.5pt + rgb("#D1D5DB")), inset: (top: 6pt, bottom: 6pt), outset: (left: 14pt), width: 100%)[')}
          .. el.content
          .. {pandoc.RawBlock("typst", "]" .. anchor)}
      end
    end
  end
end
