-- braiid.lua — Pandoc Lua filter for theorem environments.
--
-- Maps Div nodes with semantic classes (theorem, definition, proof, etc.)
-- to LaTeX environments: \begin{...}\end{...}.

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
    if cls == "proof" or cls == "sketch" then
      local proof_name = cls == "sketch" and "Proof sketch" or nil
      if fmt:match("latex") then
        local opt = proof_name and ("[" .. proof_name .. "]") or ""
        return {pandoc.RawBlock("latex", "\\begin{proof}" .. opt)}
          .. el.content
          .. {pandoc.RawBlock("latex", "\\end{proof}")}
      end
    end
    if theorem_envs[cls] then
      local title = el.attributes and el.attributes["title"] or nil
      if fmt:match("latex") then
        local label = ""
        if el.identifier and el.identifier ~= "" then
          label = "\\label{" .. el.identifier .. "}"
        end
        local opt = title and ("[" .. title .. "]") or ""
        return {pandoc.RawBlock("latex", "\\begin{" .. cls .. "}" .. opt .. label)}
          .. el.content
          .. {pandoc.RawBlock("latex", "\\end{" .. cls .. "}")}
      end
    end
  end
end
