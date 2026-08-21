-- Removes speaker notes from the rendered deck when `strip-notes: true`.
--
-- The project sets that flag in _quarto.yml, so every deck published to the
-- website ships without notes. To build a copy for yourself, with notes, pass
-- the flag back off on the command line:
--
--   quarto render slides/lecture1.qmd -M strip-notes:false -o lecture1-presenter.html
--
-- Presenter copies are gitignored, so they stay off the public site.

local strip = false

function Meta(meta)
  local flag = meta["strip-notes"]
  if flag ~= nil then
    -- metadata arrives as a boolean, or as inlines when set on the CLI
    if type(flag) == "boolean" then
      strip = flag
    else
      strip = pandoc.utils.stringify(flag) == "true"
    end
  end
  return meta
end

function Div(el)
  if strip and el.classes:includes("notes") then
    return {}
  end
  return el
end

return { { Meta = Meta }, { Div = Div } }
