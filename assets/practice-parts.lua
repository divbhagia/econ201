-- practice-parts.lua: hanging labels on practice pages.
--
-- A paragraph that opens with a bold part label, "**(a)**" or "**Q3.**",
-- is wrapped in div.part with the label in span.part-label, so the CSS in
-- assets/styles.css can hang the label in the margin and indent the
-- question text, its option list, and its Solution under it. The label
-- stays inside the paragraph, so the reading order is unchanged.
-- Wired in by practice/_metadata.yml.

local function label_of(para)
  local first = para.content[1]
  if not first or first.t ~= "Strong" then return nil end
  local txt = pandoc.utils.stringify(first)
  if txt:match("^%(%a%)$") or txt:match("^Q%d+%.$") then return txt end
  return nil
end

function Para(el)
  local lab = label_of(el)
  if not lab then return nil end
  local rest = pandoc.List(el.content)
  rest:remove(1)
  if rest[1] and rest[1].t == "Space" then rest:remove(1) end
  local out = pandoc.List({pandoc.Span(pandoc.Str(lab), {class = "part-label"}),
                           pandoc.Space()})
  out:extend(rest)
  return pandoc.Div({pandoc.Para(out)}, {class = "part"})
end
