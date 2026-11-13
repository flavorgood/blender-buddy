# Blender Buddy — Put the power in the hands of average people who can't spend 10k hours learning a skill

Blender is the free professional studio behind films, video games,
product designs, architecture and 3D printing — the same class of
tool the big studios pay thousands per seat for, except Blender
costs nothing. It has exactly one flaw, and it's fatal: it is
famously unusable by normal people. Its thousands of tools are
hidden behind keyboard shortcuts and insider jargon, so most
people who open it — people with real ideas — quit within the
first hour. The power was never the problem. The door is locked.

Blender Buddy doesn't translate Blender. **It redesigns how
Blender is used.** Tools are organised by the job you're trying
to do, everything is visible instead of hidden behind shortcuts,
you can search in your own everyday words — typos and all — and
learn by doing real projects (starting with the famous Donut)
while Buddy checks your work as you go. Your own AI expert lives
in the panel: it knows your scene, answers in plain language,
and can operate the tools with you. Nothing is removed and
nothing is dumbed down — every professional tool stays, and
Buddy re-checks itself against each new Blender version so it
never goes stale.

Blender made world-class creation free for everyone. **Blender
Buddy makes it usable by anyone.**

Built on one rule:

> **If a day-1 beginner can't use it, we aren't done.**

![Blender Buddy running in Blender: the guided-projects panel and the floating expert card](https://github.com/flavorgood/blender-buddy/releases/download/v1.0.0/bb_v10_full.png)

The panel's sections are drawers — one open at a time:

![Section drawers with plain-words buttons](https://github.com/flavorgood/blender-buddy/releases/download/v1.0.0/bb_v10_drawers.png)

And Day 1 is the Donut, taught step by step — you do it, it checks:

![A Donut project step card in the panel](https://github.com/flavorgood/blender-buddy/releases/download/v1.0.0/bb_v10_teachcard.png)

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
- **Guided projects — Day 1 is the Donut.** At the top of the
  panel sits a shelf of guided projects. The first is the donut:
  the follow-along companion to Blender Guru's new Blender 5.0
  series (see "New in v3.2"). Each of its 8 steps pairs with one
  video part, opens that part from the card, and tells you what
  to do with your own hands in real Blender (menus and keys
  named, in plain words) — the cup and the mug from a photo,
  Edit Mode, the icing as the *top of the dough itself*
  (thickened, dripped, shrink-wrapped onto the dough),
  materials with subsurface, photo textures wired as a real
  PBR recipe, seams and UV unwrapping, Blender 5.0's Scatter
  on Surface sprinkles, and lighting a final picture. There is
  no "do this step" button; a step ticks off only when your
  scene *proves* you did it, and the card tells you in plain
  words what it's still waiting for. More projects can be
  added to the shelf the same way.
- **Your own Buddy agent — key, ChatGPT login, or local AI.** There
  is no "log in with ChatGPT/Claude" button an add-on is allowed to
  offer: subscription logins only work inside those companies' own
  apps. So the preferences offer the three honest routes instead.
  **AI key:** paste your own key for an OpenAI-shaped chat service
  (it never leaves your computer except to that service), or pick
  **Claude key** and paste an Anthropic key — Claude's service
  speaks a different shape, and Buddy translates.
  **ChatGPT login:** if OpenAI's own Codex program is installed and
  signed in with your ChatGPT account, Buddy asks *through it* —
  your login never touches Buddy, and the asking runs read-only.
  (Claude logins can't be used this way: Anthropic's rule, enforced
  since 2026 with accounts blocked for it — Buddy won't put your
  Claude account at risk.) **Local AI:** run a free AI on your own
  computer (for example Ollama) — no key, no login, nothing leaves
  the machine. With "Let the expert do it" on, asking in plain words
  produces a short plan you can read before pressing **Run these
  steps**. A plan can press Buddy buttons, run Blender's own tools,
  set exact values — for example the size, strength and falloff of
  the sculpt brush you describe, a bevel's width, or the picture's
  sample count — apply real node-tree styles such as procedural
  wood or marble, and open an add-on search when another plugin is
  the better tool. Every named button, tool, setting and style is
  checked against what really exists before a plan is shown;
  invented steps are dropped. If a step cannot run, the agent stops,
  says what happened in plain words, and may offer one revised plan
  — it never runs that revision until you press Run again. Turn
  agent mode off and it goes back to advice only, with a "Do it"
  button when one Buddy button fits. (Its tips can also float as
  a small card over the 3D window - off by default, because it got
  in the way; turn it on in preferences if you like it.)
- **One press for multi-step jobs.** "Cut one shape out of another"
  does the whole Boolean setup and applies it. "Give it a colour"
  builds and assigns the material.

## New in v3.2: the Donut, rebuilt as a follow-along companion

The guided Donut project is rebuilt around Blender Guru's
**new donut series for Blender 5.0** ("Blender Donut Tutorial
(2025)"). It is no longer a course of its own — it is a
**follow-along companion** to his: the video teaches, Buddy
sits beside you. Each of the 8 steps pairs with the exact part
it follows (Part 1's cup, Part 2's mug from the photo, Part 3's
dripping icing, Part 4's materials and first render, Part 5's
photo textures, Part 6's UV unwrapping, Part 7's Scatter on
Surface sprinkles, Part 8's lighting finale), carries a
**"Watch Part N" link that opens that video**, tells you what
he is about to do before he does it, and ticks **only when
your scene proves you caught up** — the icing really carries
Solidify and a Shrinkwrap aimed at the dough; the scatter step
really finds Blender 5.0's Scatter on Surface modifier, your
sprinkle collection and your painted vertex group. Where a
part's finish is a judgment (a handle that looks right, a
pattern that sits straight, a render that looks like food),
the card says so plainly instead of pretending a tick can see
it. Progress is never stored: close Blender mid-project,
reopen the file, and the card reads its place back from the
scene alone — proven by a test that builds two steps, saves,
reloads, and checks the tour resumes at step 3. Part 7's
modifier exists only in Blender 5.0+, so on older Blender
that one step honestly waits (its check answers "not yet",
never an error) while the other seven work as always.

## New in v3.1: the plain-words layer - where am I, and what's about to bite me

Furniture was never the deepest problem. The deepest
problem is that Blender never explains its own invisible
ideas - modes, the origin, the 3D cursor, which thing is
"active" - and a beginner hits those walls in the first
hour and concludes Blender is broken. v3.1 teaches the
concepts at the moment they bite:

- **"Where you are", always on screen.** The top of the
  panel now states, in plain words, what half of Blender
  you're in: *"You're moving whole things"* - or, in Edit
  Mode, *"You're reshaping 'Cube' itself - you're moving
  its corners, edges and faces, that's why your tools
  changed"*, with a **Back to moving whole things** button
  underneath. Sculpting, posing and painting get the same
  treatment. Pick several things and it says which one is
  *in charge* - and what that even means.
- **Heads-ups for the invisible traps, with the fix
  attached.** Buddy watches the scene and speaks up in
  plain words when: a thing's **spin point** (the little
  orange dot Blender calls the origin) is sitting away
  from the thing itself - *"that's why it swings in a
  wide circle when you turn it"* - with **Put the spin
  point in the middle** / **at the bottom** buttons; the
  **target** (the 3D cursor) has drifted far away, so new
  things would appear in the wrong place; a thing's size
  is stretched but **not locked in**, so shaping tools
  come out uneven (and the minus-size flip that turns a
  thing inside-out gets its own warning); or **everything
  is hidden** and the window only *looks* empty. Every
  heads-up can be dismissed per thing with **Got it** -
  it won't nag about the same thing twice.

## New in v3.0: Buddy lives inside Blender itself

v2 was still, in the end, a smarter panel - and a panel is an
extra window, not a redesign. v3 moves into Blender's own
furniture:

- **Blender can open AS Buddy.** Installing Buddy also
  installs a **Blender Buddy app template**: from the splash
  screen's New File list (or by launching with it), Blender
  opens on Buddy's own screens - **Start, Model, Look,
  Finish** - and Blender's default workspace sprawl simply
  isn't there. The Start screen asks the only first question
  that matters: *What are you making?*
- **The whole screen follows the job.** Start a guided job
  and each step re-forms the entire program around it: the
  workspace switches (modelling steps on the Model screen,
  colour steps on the Look screen with the shader editor
  already open, the picture step on the Finish screen
  through the camera), and the viewport shading follows.
  Buddy conducts the application, not just its own corner
  of it. In a plain file, "Set up Buddy's screens" (in the
  add-on preferences) builds the same screens into the file
  you're in - your own workspaces are never touched.
- **The tools are where your mouse already is.** Press the
  **`** key (top-left of the keyboard) and the moment's
  tools appear in a circle around your cursor, in the 3D
  view itself. The 3D view's own header bar carries a
  **Buddy tools** button and your job's progress. And in
  Edit Mode, Blender's own toolbar gains three of Buddy's
  plain-words tools next to Blender's own: **Pull a face
  out**, **Add a ring of edges**, **Draw a cut** - the same
  operators as Extrude, Loop Cut and Knife, under names a
  beginner already understands.
- **Compact by default.** The step card now leads with where
  you are and the step's tools; the full written lesson is
  one tap away ("Show the full lesson") instead of a wall of
  text. The "where you are" line was rewritten per kind of
  thing picked - a camera is for framing and taking the
  picture now, never for "shaping".

Everything from v1/v2 is still underneath, unchanged -
Blender itself is never modified, and disabling Buddy
changes nothing.

## New in v2.0: the panel follows the moment

v1 translated Blender. v2 redesigns how you move through it -
in two ways:

- **Only what you can use, only when you can use it.** The panel
  now opens on a **"For right now"** deck: the few tools this
  exact moment calls for, in the order a person reaches for
  them. Pick a thing and it's Move, Size, Turn, Start shaping.
  Enter Edit Mode and the deck becomes the shaping bench. The
  section drawers follow the same rule - a tool that can't run
  yet (wrong mode, nothing picked, no modifier to apply) isn't
  greyed out, it simply isn't there, and it appears the moment
  it becomes usable. A drawer with nothing usable in it doesn't
  appear at all. Search works the same way. Nothing is lost:
  the complete index at the bottom still holds every tool this
  Blender has.
- **Ways of working: the community's job patterns, as guided
  flows.** Under "Learn by doing" you'll now find flows that
  follow the order experienced Blender users actually work in -
  gathered from the community's own guides (the full research
  lives in `redesign/COMMUNITY_PATTERNS.md` in this repo):
  **Make a hard-surface thing** (blockout, lock the size,
  forms, live detail, edges, shading), **Make it look real**
  (frame the shot, light, surfaces, light again, picture,
  save) and **Get it ready for 3D printing** (millimetres,
  locked size, one solid, export, verify). Each step names the
  method, teaches it in plain words, shows only the tools that
  step needs, and ticks off only when your scene proves it.
  The Donut is still there too - in its own drawer now, not
  squatting at the top of the panel.

Also fixed: setting up the ChatGPT (Codex) expert route on
Windows - Buddy now finds the Codex program where it actually
installs, and the expert settings have a **Test this
connection** button that tells you plainly whether it answered.

## Nothing is lost

Blender 4.2.5 exposes **2,410 tools**. Blender Buddy puts **96** of
the everyday ones on plain-words buttons in 13 job-ordered
section drawers (one open at a time, the rest a single line each) —
and **all 2,410** are in the searchable "Everything else Blender can
do" index at the bottom of the same panel, each with Blender's own
one-line explanation and a Run button. The index is built live from
your Blender, so it always matches your version. Blender's own
interface, shortcuts and menus are untouched — turn the add-on off
and nothing is different.

Sections: Add something · Move around & find things · Move it &
size it · Shape it · Copy it & combine it · Make it look right ·
Fix common problems · More shapes · More ways to shape it · Every
other modifier · Sculpt it & paint it · Animate it · Finish:
picture, save, send it out.

## Get it (2 minutes)

You need Blender 4.2 or newer (free at blender.org). Verified on
Blender 4.2.5 and on Blender 5.2.0.

**First, the trap that catches everyone:** do NOT search for
Blender Buddy inside Blender's **Get Extensions** window. That
search only covers Blender's official online store, and Buddy
isn't published there yet — the search comes back empty even
though nothing is wrong. You install Buddy **from a file**, one
of these three ways (same plugin in all three):

**Way 1 — the extension zip (Blender 4.2+):** grab
`blender_buddy_v1.2.1_extension.zip` from the
[latest release](https://github.com/flavorgood/blender-buddy/releases/latest).
In Blender: **Edit → Preferences → Get Extensions**, click the
small dropdown arrow at the top right of that window →
**Install from Disk…** → pick the zip. It switches on by itself.

**Way 2 — the add-on zip:** grab `blender_buddy_v1.2.1.zip` from
the same release. **Edit → Preferences → Add-ons → Install…** →
pick the zip → then **tick the checkbox** next to "Blender
Buddy" in the list. Until you tick it, nothing appears — Blender
never tells you this step exists.

**Way 3 — no zip at all, one single file:** download
**[blender_buddy.py](https://raw.githubusercontent.com/flavorgood/blender-buddy/main/blender_buddy.py)**
(right-click → Save link as… if it opens in the browser instead
of downloading), then Way 2's steps, picking the `.py` file.

Don't feed one door the other door's file: the **extension** zip
only goes through **Get Extensions**, the plain zip and the
`.py` only through **Add-ons**. The wrong pairing fails quietly.

Whichever way you used: in the 3D Viewport press **N** and open
the **Blender Buddy** tab on the right edge.

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
the add-on registers; plain-words search matches everyday phrasing,
and the loose-search suite proves synonyms, half-words, US spellings
and typos find their tools while gibberish finds nothing; all 28
modifier buttons genuinely add their modifier to a real object;
the index holds 2,410 tools and its Run button executes real tools;
sculpt mode, keyframes, GLB/STL/OBJ exports, render and save all
produce real results; both install paths (zip package and the single
`.py` file) install and enable through Blender's own Install button.
The anti-stale self-check suite proves the v1.2 promise on two
Blender generations at once (4.2.5 and 5.2.0): every one of the
96 curated actions is verified against the running Blender's real
registries - the live operator index, the modifier and mode
lists, and the toolbar's own tool table - and flags nothing on
either version, while planted fakes of every kind are caught.
Its first catch was real: v1.1's Walk button pointed at an
operator name that does not exist (Blender's lazy operator
lookup had let a hollow existence test pass it); the check found
it, the button now calls the real operator, and the survival
suite's existence test was rewritten against the registry so it
can never be fooled that way again.
The guided-project suite proves the teaching contract — every
step carries by-hand instructions, a named skill and a
what's-still-missing line, and no "do this step" button exists in
the panel — proves every donut step carries its own verified
video link, and proves each step's scene check against the step's
reference build (the icing's Solidify + Shrinkwrap onto the
dough, the mug's seams, and on Blender 5.x the Scatter on
Surface modifier with its sprinkle collection and painted
vertex group; on 4.2.5 it proves the scatter check simply
answers "not yet"). It also proves interrupt-and-resume: two
steps built, the file saved and reloaded fresh, and the tour
reads its place back from the scene alone. The donut in `demo/`
was built by that reference machinery and rendered through the
project's own camera. The
expert suite proves the advice plumbing with a stubbed service — no
key, no call; answers and suggested buttons land in the panel; an
invented button name is dropped; a dead service becomes a plain
explanation. The agent suite uses the same stub to prove the full
loop without a real service: a goal becomes a checked plan; buttons
and a raw Blender tool run; brush, bevel and render settings land
and read back; a procedural-wood node tree is built; an add-on
search opens; malformed and invented steps are dropped; a failed
step produces one revised plan that waits for a second Run press.
The login suite proves the routing with the program and network
stubbed: readiness differs per route, a missing Codex program
becomes a plain setup message, a present one carries a full agent
plan without touching the key/network path, a local AI answers
with an empty key, and the Claude-key route sends Anthropic's own
request shape (key header, system as its own field) and reads the
text blocks back into a runnable plan. An official Extensions
package (`extension_src/` + Blender's own build tool) validates
and installs through Blender's extension system — see
`LISTING.md` for the submission draft (the license question it
waited on is settled: GPL, the stay-free license, ruled by the
owner on 2026-11-12). The demo scene in `demo/` (box
with rounded edges + smooth red ball on a ground sheet) was built
using only the add-on's buttons.

Seen with our own eyes (v0.9): the panel, the floating expert
card and the preferences were photographed inside a real running
Blender window (a virtual display on the test machine, real GUI,
real mouse clicks; the before-and-after screenshots are kept in
the project's `demo/checks/` folder). The first
photos caught real flaws: text lines Blender cut off with '...'
wherever the add-on guessed the panel width instead of measuring
it, a tour heading too long for its line, four buttons whose
hover help said '(undocumented operator)', and the floating card
sitting half under the window's header strip, struck through by
the view's own corner text. v0.9 fixes all of them — text now
wraps to the width that actually fits, every button explains
itself, and the card sits clear in its corner. Seen again for
v1.0: the section drawers, the guided-projects shelf, a live step
card advancing on scene proof, and the card redrawn with rounded
corners — the first v1.0 photo caught those corners folded into a
wedge, so the card is now built from explicit triangles with its
geometry pinned by a test, and the re-shot card is clean. v1.1
adds the "Move around & find things" survival drawer at position
2 — bring what I picked into view, see everything at once, find
everything in my scene, look through the camera, move the camera
to what I'm looking at, walk navigation, and the front/top/side
views with their no-number-pad menu paths — photographed in the
GUI as a drawer stack (its own contents verified by the survival
test suite). Still
not verified: a
live conversation with a real AI service, a real signed-in Codex
program, or a real local model (each needs the real thing on a
real machine), and how the panel looks on a physical monitor at
other window sizes and UI scales.

## License

GNU General Public License v3.0 or later — see `LICENSE`. Free to
use, copy, change and share; anyone who passes it on has to keep
it free and open the same way, so it can never be taken, locked
up and sold as someone else's closed product. (Switched from MIT
on the owner's ruling, 2026-11-12 — the stay-free license is also
the one Blender's official Extensions platform expects.)
