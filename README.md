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

## What it covers today

Honest scope, in plain words:

- **Modeling is covered.** The Donut follow-along takes you from
  an empty scene to a finished picture, checking your work as you
  go, and the panel's plain-words tools cover the everyday
  modeling jobs. The other guided projects — hard-surface,
  look-real, print-ready — are modeling work too.
- **Sculpting has its first guided pieces** (v3.3.0, v3.4.0):
  "Sculpt it like clay", a guided way of working under Learn by
  doing — a ball of clay blocked into its big forms, remeshed
  for a finer even surface, worked with finer detail, and
  finished smooth and saved, each step ticking only when the
  surface itself proves it — and "Sculpt both sides at once",
  which teaches the mirror: block both sides working one, then
  break the mirror on purpose for the finishing touches. They
  are first pieces of the craft, not the whole of it, and
  nothing here should be read as more.
- **Animation and the other crafts are not covered yet.** Buddy
  does not teach them, and nothing here should be read as if
  it does.
- The Donut also includes a little sculpting near the end —
  smoothing the icing — as a finishing touch inside a modeling
  project. The sculpting flow above is the actual first
  sculpting piece; the Donut passage remains a taste inside
  someone else's project.
- Each craft is being added one at a time, in its own shape,
  taught the way that craft actually works. Whatever made the
  Donut work does not transfer to sculpting or animation on its
  own, so each craft is built and proven separately.

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
  the machine. Ask in plain words for advice, explanations, or
  exact values for your scene. **Expert help with tasks** starts
  on and remembers your choice. With it on, the Expert can draft
  a plan for you to review. Press **Run these steps** to apply
  it. Switch task help off for advice only. A plan can press
  Buddy buttons, run Blender's
  own everyday tools, set exact values — for example the size,
  strength and falloff of the sculpt brush you describe, a bevel's
  width, or the picture's sample count — wire your material's node
  tree (add a node, set its value, join two sockets), set a colour
  ramp from a description, apply node-tree styles such as
  procedural wood or marble (read before they're written, so a
  texture you already have is never silently overwritten), look up
  real add-ons, models and textures — every link checked before
  it's shown — and grow simple ingredients like a low tree or a
  flat picture of a thing for the background. You stay the author
  throughout: the expert assists with the task in front of you, it
  doesn't do your project. Every named button, tool, setting and
  style is checked against what really exists in your Blender
  before a plan is shown; invented steps are dropped. If a step
  cannot run, the expert stops, says what happened in plain words,
  and may offer one revised plan — it never runs that revision
  until you press Run again. With task help off, the expert still
  suggests one Buddy button when a single button fits the answer,
  as one press you make yourself. (Its tips can also float as
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
your scene proves you caught up** — the finished icing is a
real shell with its modifiers applied away, exactly as his
part ends; the scatter step
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

### v3.4.0: sculpting's second piece — "Sculpt both sides at once"

Sculpting's second piece teaches the mirror, in four steps: fresh clay (a finer ball, so paired features have the points to read in), block the big paired forms working one side only with X symmetry on, then turn the mirror off on purpose and add the small one-sided life real faces have, then finish smooth and save. The checks read the clay against its own mirror image: mirrored work leaves every worked point with a twin the same distance out on the other side, so the mirrored step ticks only when both sides of the surface itself match — and the battery's negative cases prove a plain ball ticks only step 1 and one-sided work without the mirror does not tick step 2. The coverage box now names both sculpting pieces and still calls them a first piece, not the whole craft; DynTopo, masks/face sets and Multires remain untaught later pieces. Verified on Blender 5.3.0: the flows battery (all five flows, plus the symmetry negatives), the interface battery, and the plain-layer and search batteries. test_context fails at its Codex-availability assertion in this environment — confirmed identical on the untouched v3.3.0 baseline, an environment gap, not this version. The 4.2.5 pass is still owed (no 4.2.5 binary on the build machine this run), as is the full parallel battery on an unloaded machine.

### v3.3.0: sculpting's first piece — "Sculpt it like clay"

Sculpting arrives the way every craft arrives in Buddy: as its own guided way of working, taught the way the craft actually works, proven separately. **Sculpt it like clay** sits under "Learn by doing" beside the other flows, in six steps: start with a ball of clay (or the monkey), pick up the brushes (Sculpt Mode, brush size with F, strength with Shift+F, Draw / Grab / Smooth), block the big forms with a big brush, remesh (Ctrl+R) for a finer even surface only once the forms read, work the finer detail small and light, then shade smooth and save. Each step ticks only when the surface itself proves it: a perfect ball has every point the same distance from its centre, so blocked forms are read from the spread of those distances; the remesh step reads the finer surface; fine detail is read by how much of the surface a smoothed copy of it has to erase. A plain untouched ball ticks only step 1 — that negative case is in the test battery alongside the full walk. The Start screen's coverage box now says sculpting has a first piece (and that it is not the whole craft); animation and the other crafts remain plainly untaught. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all four flows walked end to end, sculpt included), the interface battery (including the coverage box), and on 5.3.0 also the plain-layer, context and search batteries. The full parallel battery's longest suite (test_tour, the Donut walk) timed out on the build machine at this version and at the v3.2.7 baseline alike — a machine limit, recorded in the lane queue, not a pass claimed.

### v3.2.7: the step-7 trap, named in the lesson

One lesson made safer. In the Donut's sprinkles step, the card's Set Origin instruction now names the trap beside it: "Origin to 3D Cursor" sits right next to "Origin to Geometry" in the same menu, is the wrong row, and can drop the tour back if picked - and if it is picked by mistake, Ctrl+Z or running Origin to Geometry again puts it right. The warning comes from a real walk: slipping onto that row once dropped the tour from step 7 to step 2 with no explanation. Nothing else changes.

### v3.2.6: the first-session walk fixes

Blender Buddy was walked cold, exactly as a new learner meets it - fresh install of the v3.2.5 download, first open, first job. Three things the walk found are fixed. Starting a job now lands you on the Blender Buddy panel itself: before, the workspace opened on Blender's Item tab while the status bar pointed at the Buddy panel, so the card it named was not on screen (on Blender 5.3 the workspaces now open on the Buddy tab; Blender 4.2's template loading ignores the saved tab, so there it opens as it did before). The step counter can no longer be clipped away: step labels lead with "Step 1 of 8:" and let the package name take the clipping instead. And the "What do you want to do?" search box now says what it is for - type what you want to do in your own words, with examples. Everything else the walk read - the coverage box, the Donut's first lesson, the Expert's plain answer with no AI connected, the pie, the loose search - read clean and is unchanged.

### v3.2.5: what Buddy covers, said plainly

The Start screen now opens with a "What Buddy covers today" box, and the same note sits near the top of this README. Buddy teaches modeling today. Sculpting, animation, and the other crafts are not covered yet - the Donut's little sculpting step is a finishing touch, not sculpting lessons - and each craft is being added one at a time, taught the way that craft actually works. This release carries forward everything in v3.2.4 (the floating Expert repairs) unchanged; the only addition is that Buddy says its limits out loud, where a learner sees them first.

### v3.2.4 brings reliable input and reopening to the floating Expert

Choose **Open Buddy Expert** in the Blender Buddy sidebar to open or reopen
the conversation. Type in the floating card and press **Enter** or click **Ask**.
You can use the Expert in a new, unsaved project. Task help remembers your
choice across Blender launches. For example, select a mesh and ask to turn it
into a flat circle. Review the plan and press **Run these steps** to add a
removable modifier that keeps the original mesh.

Windows ChatGPT-login requests now find supported Codex desktop installations
and can send long scene descriptions. The card reports when waiting times out
and lets you stop waiting with **Esc** in the 3D Viewport.

### v3.2.3: the Expert moves out of the panel

The Buddy Expert now lives in a floating card over the 3D
view instead of a panel section. Drag it anywhere by its
title bar, resize it by its corner, and minimise it to a
small chip in the corner of the view when you want it out
of the way — click the chip and it comes back at the size
and place you left it. Everything the Expert does happens
in the card: ask in your own words, read the answer, and
run a plan it drafts only when you press Run. The panel
keeps the setup (your key, ChatGPT login, or a local AI);
the card starts on its own when Blender opens and is on
by default.

### v3.2.2: the second half of the donut, walked and fixed

v3.2.1's notes said the steps 4–8 cold walk was under way.
It finished — and it found real faults. Step 4 could never
tick from its own instructions: a finished render left
nothing the check could see, so the tour sat on step 4
forever. Steps 5 and 6 dead-ended anyone without the
Poliigon add-on — the cards named no other route to the
textures. Step 8 pointed at a camera setting and a bake
button that are not where the card said, and its final
tick could be satisfied by an old render left over from
an earlier step.

v3.2.2 fixes all of it. A completed render now records
itself in the file, and step 4 ticks on the render the
card tells you to make. Steps 5 and 6 teach a complete
by-hand route with your own picture files, alongside his
Poliigon route. Step 8's card names the settings' real
homes, and the finale now counts only a render made with
the finished scene standing — an earlier step's picture
no longer finishes the tutorial. Every fix was verified
the same way the faults were found: the walked scenes
themselves, re-graded, plus the full test battery on
Blender 5.3.0 and 4.2.5.

### v3.2.1: the tutorial, transcribed and proven

Two honest admissions first. The v3.2.0 finale picture was
near-black and should never have shipped; it has been removed
from that release. And the v3.2.0 donut steps, checked against
Blender Guru's actual videos line by line, diverged from his
procedure in 61 places — steps he takes that Buddy skipped,
values Buddy invented, checks written against Buddy's own
reference scene instead of the scene his procedure produces.

v3.2.1 is the correction. Every step of the companion is now
a transcription of his series — his actions in his order, his
stated values exact, and the values he leaves to the eye
flagged as by-eye instead of filled in. The Expert was rebuilt
the same way: its audit found the question box could vanish
entirely on the ChatGPT-login route, and whole classes of
connection failure collapsed into one shrug of a message; both
are fixed, and the panel is now collapsible sections instead
of one long scroll.

Then the whole thing was proven the hard way: independent
examiners walked the tutorial using only the on-screen cards —
no video, no outside help — in fresh Blender installs. Steps
1–3 passed every check: a step ticks exactly when the scene
proves the work is done (a handle merely touching the mug
never ticks; a hand-sewn handle does), cutting the work back
out revokes the tick, and progress reads back from the saved
file alone after a full restart. Steps 4–8 carry the same
transcription and pass the same test suites; their own cold
walk is under way. The release picture is the current build's
own render of the finished scene.

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

Blender Buddy supports Blender 4.2 or newer. Download the package for your
installation from [GitHub Releases](https://github.com/flavorgood/blender-buddy/releases/latest).

- **Extension** (recommended). For 3.3.0, download
  [blender_buddy_v3.3.0_extension.zip](https://github.com/flavorgood/blender-buddy/releases/download/v3.3.0/blender_buddy_v3.3.0_extension.zip). Open **Edit → Preferences → Get
  Extensions**, use the upper-right menu, and choose **Install from Disk**.
  Select the downloaded ZIP and confirm. To update an existing extension,
  select the same local repository you used before. Check that Blender Buddy
  shows version 3.3.0 in Preferences.
- **Classic add-on**. Download [blender_buddy_v3.3.0.zip](https://github.com/flavorgood/blender-buddy/releases/download/v3.3.0/blender_buddy_v3.3.0.zip). In **Edit →
  Preferences → Add-ons**, use the install-from-disk control to select the ZIP.
  Enable **Blender Buddy**. Use the same installation format for future updates.
- **Single-file add-on**. Download the tagged
  [blender_buddy.py](https://raw.githubusercontent.com/flavorgood/blender-buddy/v3.3.0/blender_buddy.py)
  and use the classic add-on installation steps with the Python file.

The GitHub ZIP is a manual update. If you have work open or the Expert is
waiting on a request, leave that Blender process open and launch a second
Blender process to install the update. The first process keeps the code it
already loaded. You can try the updated Expert in the second process without
saving a project.

In the 3D Viewport, press **N**, open the **Blender Buddy** tab, and choose
**Open Buddy Expert**.

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
