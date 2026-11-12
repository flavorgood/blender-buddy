# Blender Buddy — Blender in plain words

A free add-on that puts a plain-words layer over Blender 4.2, built on
one rule:

> **If a day-1 beginner can't use it, we aren't done.**

Blender's problem isn't missing power — it's that the power is hidden
behind shortcuts and names you have to already know. Blender Buddy
changes none of Blender's functions. It makes them visible:

- **Every button is labelled by the job, not the jargon.**
  "Round off a sharp edge", "Cut one shape out of another",
  "Give a flat sheet some thickness" — never just *Bevel*, *Boolean*,
  *Solidify*.
- **Every button explains itself.** One plain sentence under each
  button says what it does and when you'd want it, *before* you press it.
- **The real name is taught, not required.** Small text under each
  explanation shows Blender's own name and shortcut, so you learn the
  real words while you work — and can follow any tutorial later.
- **The panel tells you where you are.** A "Where you are" box reads
  what you've picked and what mode you're in, and says what to do next.
- **Buttons help instead of failing.** Press a shaping button before
  you're shaping and it doesn't error — it switches you into shaping,
  picks everything, and tells you to press the same button again. Press
  "Take the picture" in a scene with no camera or light and it adds
  them for you instead of failing.
- **Search in your own words — loosely.** Type "round the edges",
  "make a copy", "cut a hole" and the matching tools appear. Loose
  words work too: everyday synonyms ("squish", "clone", "glow"),
  half-words ("extrud"), US spellings ("color") and plain typos
  ("bevell") all find their tool, ranked best-first. Gibberish still
  finds nothing.
- **One press for multi-step jobs.** "Cut one shape out of another"
  does the whole Boolean setup and applies it. "Give it a colour"
  builds and assigns the material.

## Nothing is lost

Blender 4.2.5 exposes **2,410 tools**. Blender Buddy puts **93** of
the everyday ones on plain-words buttons in 13 job-ordered sections —
and **all 2,410** are in the searchable "Everything else Blender can
do" index at the bottom of the same panel, each with Blender's own
one-line explanation and a Run button. The index is built live from
your Blender, so it always matches your version. Blender's own
interface, shortcuts and menus are untouched — turn the add-on off
and nothing is different.

Sections: Add something · Move it & size it · Shape it · Copy it &
combine it · Make it look right · Fix common problems · More shapes ·
More ways to shape it · Every other modifier · Sculpt it & paint it ·
Animate it · Finish: picture, save, send it out · Find your way around.

## Get it (2 minutes)

You need Blender 4.2 or newer (free at blender.org).

1. Download **[blender_buddy.py](https://raw.githubusercontent.com/flavorgood/blender-buddy/main/blender_buddy.py)**
   (right-click → Save link as… if it opens in the browser instead of downloading).
2. In Blender: **Edit → Preferences → Add-ons → Install…** and pick
   the downloaded `blender_buddy.py`.
3. Tick the checkbox next to **"Blender Buddy - Blender in Plain Words"**.
4. In the 3D Viewport press **N** and open the **Blender Buddy** tab.

Developers: the `blender_buddy/` folder in this repo is the same
add-on in package form (zip it and install the zip), and
`tests/` holds the headless proof suites.

## Try this first (day-1 path)

1. **Add a box** (section 1).
2. **Make a copy of it** (section 2) and move the copy aside.
3. Pick the first box, press **Start shaping it** (section 3), then
   **Round off a sharp edge**.
4. **Add a ball** (section 1), then **Make it smoother & rounder** and
   **Give it a colour** (section 5).
5. Type `cut a hole` in the search box and read what it asks you to pick.
6. Press **Take the picture** (section 12).

If any step needs a word you don't already know, that's a bug in this
add-on — that's the standard it is built to. Open an issue and say
which word stopped you.

## What was verified

Headless test suites (`tests/`, Blender 4.2.5 LTS): all checks pass —
the add-on registers; plain-words search matches everyday phrasing;
all 28 modifier buttons genuinely add their modifier to a real object;
the index holds 2,410 tools and its Run button executes real tools;
sculpt mode, keyframes, GLB/STL/OBJ exports, render and save all
produce real results; both install paths (zip package and the single
`.py` file) install and enable through Blender's own Install button.
The demo scene in `demo/` (box with rounded edges + smooth red ball
on a ground sheet) was built using only the add-on's buttons.

Not yet verified: the panel's on-screen layout in the live GUI
(headless test machines can't draw the viewport sidebar). First thing
to check on a real machine — reports welcome.

## License

MIT — see `LICENSE`. Free to use, copy and share.
