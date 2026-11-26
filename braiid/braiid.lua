-- braiid.lua: Pandoc Lua filter for theorem environments, equation numbers and
-- section numbers.
--
-- Maps Div nodes with semantic classes (theorem, definition, proof, etc.)
-- to LaTeX environments: \begin{...}\end{...}. The environments are defined in
-- theorems.tex. RSM numbers the blocks and equations itself, and this filter prints
-- RSM's numbers, so that they agree with the text of references to them.

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

local function latex_text(text)
  return pandoc.write(pandoc.Pandoc({pandoc.Plain({pandoc.Str(text)})}), "latex")
end

local function anchor(identifier)
  if identifier and identifier ~= "" then
    return "\\phantomsection\\label{" .. identifier .. "}"
  end
  return ""
end

function Div(el)
  if not fmt:match("latex") then
    return nil
  end
  for _, cls in ipairs(el.classes) do
    if cls == "proof" or cls == "sketch" then
      local opt = cls == "sketch" and "[Proof sketch]" or ""
      local of = el.attributes["of"]
      if of then
        local link = pandoc.Link({pandoc.Str(el.attributes["of-text"])}, "#" .. of)
        local text = pandoc.write(
          pandoc.Pandoc({pandoc.Plain({pandoc.Str("Proof of "), link})}), "latex"
        )
        -- The ] of \hyperref[...] would end the optional argument of proof, and
        -- then of the \item that amsthm passes it to, so it sits in two groups.
        opt = "[{{" .. text .. "}}]"
      end
      return {pandoc.RawBlock("latex", "\\begin{proof}" .. opt)}
        .. el.content
        .. {pandoc.RawBlock("latex", "\\end{proof}")}
    end
    if theorem_envs[cls] then
      local attrs = el.attributes
      local name = attrs["blockname"] or (cls:gsub("^%l", string.upper))
      if attrs["number"] then
        name = name .. " " .. attrs["number"]
      end
      local opt = attrs["title"] and ("[{" .. latex_text(attrs["title"]) .. "}]") or ""
      local begin = "\\renewcommand{\\rsmblockname}{" .. latex_text(name) .. "}\n"
        .. "\\begin{" .. cls .. "}" .. opt .. anchor(el.identifier)
      return {pandoc.RawBlock("latex", begin)}
        .. el.content
        .. {pandoc.RawBlock("latex", "\\end{" .. cls .. "}")}
    end
  end
end

function Header(el)
  if not fmt:match("latex") or not el.attributes["number"] then
    return nil
  end
  local number = "\\renewcommand{\\rsmsecnum}{" .. latex_text(el.attributes["number"]) .. "}"
  return {pandoc.RawBlock("latex", number), el}
end

function Span(el)
  if not fmt:match("latex") or not el.classes:includes("equation") then
    return nil
  end
  local math = el.content[1]
  if #el.content ~= 1 or math.t ~= "Math" or math.mathtype ~= "DisplayMath" then
    return nil
  end
  local tag = "\\tag{" .. el.attributes["number"] .. "}"
  local label = el.identifier ~= "" and ("\\label{" .. el.identifier .. "}") or ""
  return pandoc.RawInline(
    "latex",
    "\\begin{equation}\n" .. math.text .. "\n" .. tag .. label .. "\n\\end{equation}"
  )
end
