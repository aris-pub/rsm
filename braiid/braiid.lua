-- braiid.lua: Pandoc Lua filter for theorem headings, proof titles, equation
-- numbers and section numbers.
--
-- For LaTeX, maps Div nodes with semantic classes (theorem, definition, proof,
-- etc.) to LaTeX environments: \begin{...}\end{...}. The environments are defined
-- in theorems.tex. RSM numbers the blocks and equations itself, and this filter
-- prints RSM's numbers, so that they agree with the text of references to them.
--
-- Other formats (Word, EPUB, HTML, Markdown and the rest) have no theorem
-- environments and do not number headings. For them the filter writes the same
-- headings into the text: "Theorem 1.1 (Title)." in bold before the statement,
-- "Proof." or "Proof of Theorem 1.1." in italics before the proof, the number
-- before each section title, and the number after each numbered equation.

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

local function block_name(cls, attrs)
  local name = attrs["blockname"] or (cls:gsub("^%l", string.upper))
  if attrs["number"] then
    name = name .. " " .. attrs["number"]
  end
  return name
end

local function prepend_run_in(el, heading)
  local first = el.content[1]
  if first and (first.t == "Para" or first.t == "Plain") then
    first.content = {heading, pandoc.Space()} .. first.content
  else
    el.content:insert(1, pandoc.Para({heading}))
  end
  return el
end

local function text_div(el)
  for _, cls in ipairs(el.classes) do
    if cls == "proof" or cls == "sketch" then
      local title = {pandoc.Str(cls == "sketch" and "Proof sketch." or "Proof.")}
      local of = el.attributes["of"]
      if of then
        local link = pandoc.Link(pandoc.Inlines(el.attributes["of-text"]), "#" .. of)
        title = {pandoc.Str("Proof of "), link, pandoc.Str(".")}
      end
      return prepend_run_in(el, pandoc.Emph(title))
    end
    if theorem_envs[cls] then
      local text = block_name(cls, el.attributes)
      if el.attributes["title"] then
        text = text .. " (" .. el.attributes["title"] .. ")"
      end
      return prepend_run_in(el, pandoc.Strong(pandoc.Inlines(text .. ".")))
    end
  end
end

function Div(el)
  if el.classes:includes("math-env") then
    -- The translator gives an amsmath block as raw LaTeX first, then as display
    -- math for the formats that drop raw LaTeX.
    return fmt:match("latex") and el.content[1] or el.content[2]
  end
  if not fmt:match("latex") then
    return text_div(el)
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
      local name = block_name(cls, attrs)
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
  if not el.attributes["number"] then
    return nil
  end
  if not fmt:match("latex") then
    el.content = {pandoc.Str(el.attributes["number"]), pandoc.Space()} .. el.content
    return el
  end
  local number = "\\renewcommand{\\rsmsecnum}{" .. latex_text(el.attributes["number"]) .. "}"
  return {pandoc.RawBlock("latex", number), el}
end

function Span(el)
  if not el.classes:includes("equation") then
    return nil
  end
  local math = el.content[1]
  if #el.content ~= 1 or math.t ~= "Math" or math.mathtype ~= "DisplayMath" then
    return nil
  end
  if not fmt:match("latex") then
    -- pandoc drops \tag when it converts math for Word, EPUB and HTML, so the
    -- number is written into the math itself.
    math.text = math.text .. " \\qquad (" .. el.attributes["number"] .. ")"
    return el
  end
  local tag = "\\tag{" .. el.attributes["number"] .. "}"
  local label = el.identifier ~= "" and ("\\label{" .. el.identifier .. "}") or ""
  return pandoc.RawInline(
    "latex",
    "\\begin{equation}\n" .. math.text .. "\n" .. tag .. label .. "\n\\end{equation}"
  )
end
