-- Fix-ups for the tagged-PDF slide deck build (Makefile target `slides-pdf`).
-- Runs on pandoc's *beamer* writer output; the .tex is then compiled under
-- ltx-talk (see scripts/build_slides_pdf.py).
--
-- Pandoc's LaTeX writer drops fig-alt, so \includegraphics goes out with no
-- alt= key and the tagging code falls back to the filename. Rebuilding the
-- command here keeps the same descriptions the HTML slides use.
--
-- Also rewrites image paths: sources are under slides/img/, and the build
-- converts .svg to .pdf in a copy of that folder next to the .tex.

if not (FORMAT:match('latex') or FORMAT:match('beamer')) then return {} end

local function tex_escape(s)
  return (s:gsub('\\', '\\textbackslash{}'):gsub('([{}%%&#_%$])', '\\%1'))
end

-- Quarto widths are bare pixel counts on reveal's 1280px canvas, or a
-- percentage of the container. Pixels map to the same fraction of
-- \paperwidth, the one unit ltx-talk keeps stable inside columns; a
-- percentage maps to \linewidth.
local function to_length(v)
  local pct = v:match('^(%d+%.?%d*)%%$')
  if pct then return string.format('%.3f\\linewidth', tonumber(pct) / 100) end
  local n = v:match('^(%d+%.?%d*)$')
  if n then return string.format('%.3f\\paperwidth', tonumber(n) / 1280) end
  -- Anything else goes through as a TeX length. A stray % would start a
  -- comment and swallow the rest of the \includegraphics line.
  return (v:gsub('%%', ''))
end

local function build_path(src)
  return (src:gsub('%.svg$', '.pdf'))
end

local function graphic(src, alt, width, height)
  local opts = {}
  if width  then opts[#opts+1] = 'width='  .. to_length(width)  end
  if height then opts[#opts+1] = 'height=' .. to_length(height) end
  if not width and not height then
    -- No size given: fill the column, but never past the frame.
    opts[#opts+1] = 'width=\\linewidth'
    opts[#opts+1] = 'height=0.62\\textheight'
  end
  opts[#opts+1] = 'keepaspectratio'
  opts[#opts+1] = 'alt={' .. tex_escape(alt) .. '}'
  return '\\includegraphics[' .. table.concat(opts, ',') .. ']{' .. build_path(src) .. '}'
end

function Image(el)
  local alt = el.attributes['fig-alt']
  if not alt or alt == '' then return nil end
  return pandoc.RawInline('latex',
    graphic(el.src, alt, el.attributes.width, el.attributes.height))
end

-- The decks put the course name above the lecture number with an HTML <br>,
-- which the LaTeX writer drops.
function RawInline(el)
  if el.format:match('html') and el.text:match('^<br%s*/?>$') then
    return pandoc.RawInline('latex', '\\\\')
  end
end

-- Attribution under a quotation ([Name]{.who}) goes on its own line.
function Span(el)
  if el.classes:includes('who') then
    local inner = pandoc.List({pandoc.RawInline('latex', '\\\\{\\small ')})
    inner:extend(el.content)
    inner:insert(pandoc.RawInline('latex', '}'))
    return inner
  end
end

-- A paragraph that is only an image is centred.
function Para(el)
  if #el.content == 1 then
    local x = el.content[1]
    local tex
    if x.t == 'RawInline' and x.text:match('^\\includegraphics') then tex = x.text
    elseif x.t == 'Image' then local i = Image(x); tex = i and i.text end
    if tex then
      return pandoc.RawBlock('latex', '\\begin{center}' .. tex .. '\\end{center}')
    end
  end
end

-- Air between top-level list items (sub-points stay tight), matching the web
-- deck. ltx-talk's own inter-item code overrides the class-level knobs, so it
-- is set from inside the first item, globally, where it survives.
local function space_lists(blocks, depth)
  for _, b in ipairs(blocks) do
    if b.t == 'BulletList' or b.t == 'OrderedList' then
      for i, item in ipairs(b.content) do
        space_lists(item, depth + 1)
      end
      if depth == 0 and #b.content > 0 then
        b.content[1]:insert(1, pandoc.RawBlock('latex', '\\global\\itemsep=0.6em'))
      end
    elseif b.t == 'Div' or b.t == 'BlockQuote' then
      space_lists(b.content, depth)
    end
  end
end
local function ends_in_list(b)
  if b.t == 'BulletList' or b.t == 'OrderedList' then return true end
  if b.t == 'Div' and #b.content > 0 then return ends_in_list(b.content[#b.content]) end
  return false
end
local function space_between_lists(blocks)
  local out = pandoc.List()
  for i, b in ipairs(blocks) do
    if b.t == 'Div' then b.content = space_between_lists(b.content) end
    out:insert(b)
    local nxt = blocks[i + 1]
    if nxt and ends_in_list(b) and nxt.t ~= 'Header' then
      out:insert(pandoc.RawBlock('latex', '\\vspace{0.6em}'))
    end
  end
  return out
end
function Pandoc(doc)
  space_lists(doc.blocks, 0)
  doc.blocks = space_between_lists(doc.blocks)
  return doc
end

-- Photo rows like the "About me" slide: `::: {.journey}` holding raw
-- <figure><img ...><figcaption>...</figcaption></figure> blocks, which pandoc
-- reads as paragraphs of inline HTML. Rebuilt as a row of images with the
-- captions on one line beneath, each image keeping its alt text.
local function journey(div)
  local pics, caps, in_cap, cap = {}, {}, false, {}
  div:walk({
    RawInline = function(r)
      if not r.format:match('html') then return nil end
      local src, alt = r.text:match('<img%s+src="([^"]+)"%s+alt="([^"]*)"')
      if src then pics[#pics+1] = graphic(src, alt, nil, '0.42\\textheight') end
      if r.text:match('^<figcaption') then in_cap, cap = true, {} end
      if r.text:match('^</figcaption') then
        in_cap = false; caps[#caps+1] = tex_escape(table.concat(cap, ' '))
      end
    end,
    Str = function(t) if in_cap then cap[#cap+1] = t.text end end,
  })
  if #pics == 0 then return nil end
  local out = '\\begin{center}' .. table.concat(pics, '\\hspace{1em}')
  if #caps > 0 then
    out = out .. '\\\\[0.3em]' .. table.concat(caps, ' \\quad $\\rightarrow$ \\quad ')
  end
  return pandoc.RawBlock('latex', out .. '\\end{center}')
end

-- Text beside a figure runs smaller on the web deck (0.9em); \small is the
-- nearest step, and it is what keeps a three-bullet column inside the frame.
local function column(div)
  div.content:insert(1, pandoc.RawBlock('latex', '\\small'))
  return div
end

-- The boxed takeaway on the web deck: set off with air above and below.
-- Kept as a plain paragraph on purpose; a box here is a paragraph inside a
-- paragraph, which the tagging code cannot represent.
function Div(el)
  if el.classes:includes('journey') then return journey(el) end
  if el.classes:includes('column') then return column(el) end
  if el.classes:includes('takeaway') then
    local out = pandoc.List({pandoc.RawBlock('latex', '\\vspace{0.6em}')})
    out:extend(el.content)
    out:insert(pandoc.RawBlock('latex', '\\vspace{0.3em}'))
    return out
  end
end

-- `## Title {.smaller}` shrinks the type on a dense slide, as on the web deck.
function Header(el)
  if el.level == 2 and el.classes:includes('smaller') then
    return { el, pandoc.RawBlock('latex', '\\small') }
  end
end
