-- ::: {.sumrow} around a table: the last row is a total, so it moves into the
-- table foot. Pandoc's LaTeX writer then sets a \midrule above it and the HTML
-- writer wraps it in <tfoot>, which assets/slides.scss rules off. Shared by
-- the web decks (front matter filters) and the PDF decks (build_slides_pdf.py).
function Div(el)
  if not el.classes:includes('sumrow') then return nil end
  return el:walk({ Table = function(t)
    local body = t.bodies[1]
    if not body or #body.body < 2 then return nil end
    local last = table.remove(body.body)
    t.foot = pandoc.TableFoot({last})
    return t
  end })
end
