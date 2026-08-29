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

-- The frame is 16:9 and only about 77mm of it is body, so the height cap is
-- what decides the width of a wide chart, not \linewidth. \figmaxht is set in
-- the preamble (scripts/build_slides_pdf.py); tune the deck there, once.
local function graphic(src, alt, width, height)
  local opts = {}
  if width  then opts[#opts+1] = 'width='  .. to_length(width)  end
  if height then opts[#opts+1] = 'height=' .. to_length(height) end
  if not width and not height then
    -- No size given: fill the column, but never past the frame.
    opts[#opts+1] = 'width=\\linewidth'
  end
  -- A width alone lets a tall image run off the bottom, so cap every figure
  -- that was not given an explicit height of its own.
  if not height then opts[#opts+1] = 'height=\\figmaxht' end
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

-- Attribution under a quotation ([Name]{.who}) goes on its own line, and
-- upright, since the quotation around it is italic.
function Span(el)
  -- [Title]{.book}: italic in the text colour, as on the web deck. A switch,
  -- not \textit, so the tagging code sees no argument-taking command.
  if el.classes:includes('book') then
    local inner = pandoc.List({pandoc.RawInline('latex', '{\\itshape ')})
    inner:extend(el.content)
    inner:insert(pandoc.RawInline('latex', '}'))
    return inner
  end
  if el.classes:includes('who') then
    local inner = pandoc.List({pandoc.RawInline('latex', '\\\\{\\small\\upshape ')})
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
        b.content[1]:insert(1, pandoc.RawBlock('latex', '\\global\\itemsep=\\listsep'))
      end
    elseif b.t == 'Div' or b.t == 'BlockQuote' then
      space_lists(b.content, depth)
    end
  end
end
-- How much of the frame a figure may take depends on what else is on the
-- slide. A figure on its own can have nearly the whole body; one with a
-- caption or a line of instructions under it has to leave room, or the text
-- below runs off the bottom edge. \figmaxht is set per frame, so the
-- \setlength is local to that frame group and the preamble default stands
-- everywhere else.
local function slide_fig_height(blocks)
  local out, slide = pandoc.List(), pandoc.List()
  local function emit(g)
    local fig, other = false, false
    for _, b in ipairs(g) do
      if b.t == 'RawBlock' and b.text:match('\\includegraphics') then fig = true
      elseif b.t ~= 'Header' and b.t ~= 'RawBlock' then other = true end
    end
    if fig then
      local at = (#g > 0 and g[1].t == 'Header') and 2 or 1
      g:insert(at, pandoc.RawBlock('latex', '\\setlength{\\figmaxht}{'
        .. (other and '0.74' or '0.88') .. '\\textheight}'))
    end
    out:extend(g)
  end
  for _, b in ipairs(blocks) do
    if b.t == 'Header' and b.level == 2 then
      if #slide > 0 then emit(slide) end
      slide = pandoc.List({b})
    else
      slide:insert(b)
    end
  end
  if #slide > 0 then emit(slide) end
  return out
end

function Pandoc(doc)
  space_lists(doc.blocks, 0)
  doc.blocks = slide_fig_height(doc.blocks)
  return doc
end

-- Photo rows like the "About me" slide: `::: {.journey}` holding raw
-- <figure><img ...><figcaption>...</figcaption></figure> blocks, which pandoc
-- reads as paragraphs of inline HTML. Rebuilt as a row of images with the
-- captions on one line beneath, each image keeping its alt text.
local function journey(div)
  local pics, caps, in_cap, cap = {}, {}, false, {}
  -- <img> arrives as a RawInline and <figcaption> as a RawBlock, and walk()
  -- visits every inline before any block, so which caption a word belongs to
  -- is only knowable by reading the blocks in order.
  local function tag(text)
    local src, alt = text:match('<img%s+src="([^"]+)"%s+alt="([^"]*)"')
    -- Three photos side by side: each needs a width cap as well as a height
    -- one, or a landscape shot pushes the row past \linewidth and it wraps.
    if src then pics[#pics+1] = graphic(src, alt, '30%', '0.72\\textheight') end
    if text:match('<figcaption') then in_cap, cap = true, {} end
    if text:match('</figcaption') then
      in_cap = false; caps[#caps+1] = tex_escape(table.concat(cap, ''))
    end
  end
  for _, b in ipairs(div.content) do
    if b.t == 'RawBlock' and b.format:match('html') then
      tag(b.text)
    elseif b.t == 'Plain' or b.t == 'Para' then
      local words = {}
      for _, i in ipairs(b.content) do
        if i.t == 'RawInline' and i.format:match('html') then tag(i.text)
        else words[#words+1] = pandoc.utils.stringify(i) end
      end
      if in_cap and #words > 0 then cap[#cap+1] = table.concat(words, '') end
    end
  end
  if #pics == 0 then return nil end
  local out = '\\begin{center}' .. table.concat(pics, '\\hspace{1em}')
  if #caps > 0 then
    out = out .. '\\\\[0.4em]{\\footnotesize\\color{muted}'
      .. table.concat(caps, ' \\quad {\\color{accent}$\\rightarrow$} \\quad ') .. '}'
  end
  return pandoc.RawBlock('latex', out .. '\\end{center}')
end

-- ltx-talk's column environment runs \@parboxrestore, which sets \parskip to
-- zero, so paragraphs inside a column would otherwise run together with no
-- separation at all. The type size is left alone: it should match the slides
-- either side of it.
local function column(div)
  div.content:insert(1, pandoc.RawBlock('latex', '\\parskip=\\bodyparskip'))
  return div
end

-- The boxed takeaway on the web deck: set off with air above and below.
-- Kept as a plain paragraph on purpose; a box here is a paragraph inside a
-- paragraph, which the tagging code cannot represent.
function Div(el)
  if el.classes:includes('journey') then return journey(el) end
  -- Muted text keeps its size and position; only the source line under a
  -- figure is also small and centred, as on the web deck.
  if el.classes:includes('dim') then
    local out = pandoc.List({pandoc.RawBlock('latex', '\\begingroup\\color{muted}')})
    out:extend(el.content)
    out:insert(pandoc.RawBlock('latex', '\\par\\endgroup'))
    return out
  end
  if el.classes:includes('figcap') then
    local out = pandoc.List({pandoc.RawBlock('latex',
      '\\vspace{0.3em}\\begingroup\\footnotesize\\color{muted}\\centering')})
    out:extend(el.content)
    out:insert(pandoc.RawBlock('latex', '\\par\\endgroup'))
    return out
  end
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
