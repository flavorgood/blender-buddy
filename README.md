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
- **Sculpting has its first guided pieces** (v3.3.0, v3.4.0, v3.5.0, v3.6.0, v3.7.0):
  "Sculpt it like clay", a guided way of working under Learn by
  doing — a ball of clay blocked into its big forms, remeshed
  for a finer even surface, worked with finer detail, and
  finished smooth and saved, each step ticking only when the
  surface itself proves it — and "Sculpt both sides at once",
  which teaches the mirror: block both sides working one, then
  break the mirror on purpose for the finishing touches — and
  "Detail where you brush", which teaches DynTopo: detail that
  grows only where you work, on clay that stays coarse
  everywhere else — and "Keep one part safe", which teaches
  masks and face sets: protect the part that is already
  right, divide the clay into regions, and work the rest —
  and "Work it at every level", which teaches Multires: one
  sculpt at several levels of detail, big forms worked low
  and fine detail high, on a tidy net that is never thrown
  away. They
  are first pieces of the craft, not the whole of it, and
  nothing here should be read as more.
- **Animation has its first guided pieces** (v3.8.0,
  v3.9.0, v3.10.0, v3.11.0, v3.12.0, v3.13.0, v3.14.0, v3.15.0, v3.16.0, v3.17.0, v3.18.0): "Make it move", under Learn by doing — the one
  idea all animation is built from: remember where a
  thing is at one moment (a keyframe), move it, remember
  again at a later moment, and Blender fills in the
  movement between. One thing, moved and turned across
  two seconds, each step ticking only when the memories
  themselves and the real travel between them prove it —
  and "Make it glide", which teaches easing and curves:
  the pace of the journey is a choice (slow the ends,
  keep the middle), and a middle memory steers both the
  path and the timing — and "Move the camera", which
  teaches cameras: the camera itself travels and turns
  on memories of its own, aimed at the subject at both
  ends of the move so the subject stays in frame the
  whole way — and "Make a character move", which
  teaches characters: a skeleton of bones inside the
  character, poses remembered at two moments, and
  parts that move together instead of sliding as one
  thing — and "Make it loop", which teaches loops: a
  move with a repeat rule on its curves, joined end
  to start — the last memory is the first place,
  reached by a journey out and back — so it can run
  for ever without jumping — and "Follow a path",
  which teaches paths: the journey drawn first as a
  curve, the traveller tied to it with a Follow Path
  rule, and the travel remembered on the rule itself
  as a share of the way, so the thing rides the drawn
  route corner and all — and "Bring a second thing
  along", which teaches following: one leader carries
  the memories, a second thing is tied to it with
  Blender's parent tie, keeping its place, and the
  pair travels together with the gap between them
  held, the follower needing no memories of its own.
  They are first pieces of
  the craft, not the whole of it.
- **The other crafts are not covered yet.** Buddy does
  not teach them, and nothing here should be read as if
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

### v3.18.0: animation's eleventh piece — "Make it change colour"

Animation's eleventh piece teaches changing colour — a thing's paint travelling from one colour to a clearly different one — in four steps: pick the thing that will change colour, remember its starting colour (a colour memory at frame 1 on the paint's Base Color slot, the reference build wearing red), change the colour and remember again (blue remembered at frame 48), then watch it change and save. The teaching point is that the memories can hold a thing's PAINT as a journey of its own: one colour, a different colour, and Blender blending between them — red to blue passes through purple. The checks read the colour memories themselves (they live on the material's node tree, read through the same cross-version helper as every other memory) and the real evaluated colour at the first and last memories — the span must run at least 20 frames and the colour must really travel, a distance of at least 0.6 through colour space where red to blue measures about 1.1, so a nudge of the same colour cannot pass for a change. A probe on Blender 5.3.0 and 4.2.5 before building showed a red memory at frame 1 and a blue one at frame 48 read back and blend identically on both versions (frame 24 reading purple, 0.451 / 0.183 / 0.477). The battery's negative cases prove a plain scene ticks only step 1, a starting colour alone does not prove the change, and a nudge of the same colour does not prove it either. The coverage box now names all eleven animation pieces and still calls them first pieces, not the whole craft. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all nineteen flows, plus the anim_color, anim_swing, anim_bounce, anim_scale, anim_follow, anim_path, anim_loop, anim_character, anim_camera, anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_color_final.png — the reference build's thing at frame 48, fully blue at the end of its change from red, on the ground with its shadow below.

### v3.17.0: animation's tenth piece — "Make it swing"

Animation's tenth piece teaches swinging — a thing's facing leaning one way, then the other, and back — in four steps: pick the thing that will swing, remember its facing leaned one way (a facing memory at frame 1, the reference build leaning it 0.7 radians to one side), lean it the other way and back (the other lean remembered at frame 24 and the first lean remembered again at frame 48), then watch it swing and save. The teaching point is that the memories can hold a thing's FACING as a journey of its own: leaned, leaned the other way, and back, and Blender fills in the sweep between. The checks read the facing memories themselves and the real evaluated facing across the whole span — the span must run at least 20 frames, the lean must sweep at least one radian end to end, it must reach clearly to both sides of upright on the same axis (at least 0.35 radians each way; the reference build reaches 0.7 each way), and the two ends must sit at about the same lean, so a one-way turn cannot pass for a swing. A probe on Blender 5.3.0 and 4.2.5 before building showed a lean-lean-back set of facing memories reads back and interpolates identically on both versions (−0.7 at frame 1, +0.7 at frame 24, −0.7 again at frame 48). One defect was caught by the proof picture during the build: the first design leaned on the Z axis, which is Blender's up axis, so the reference thing spun like a turntable and the render read upright — the shipped piece leans on the Y axis, and the lean reads plainly in the picture. The battery's negative cases prove a plain scene ticks only step 1, a starting lean alone does not prove the swing, a one-way turn does not prove it, a tip that never crosses the middle does not prove it, and a small sway does not prove it either. The coverage box now names all ten animation pieces and still calls them first pieces, not the whole craft. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all eighteen flows, plus the anim_swing, anim_bounce, anim_scale, anim_follow, anim_path, anim_loop, anim_character, anim_camera, anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_swing_final.png — the reference build's red thing at frame 24, leaned fully the other way, tipped on the ground with its shadow below.

### v3.16.0: animation's ninth piece — "Make it bounce"

Animation's ninth piece teaches bouncing — a thing leaving the ground and coming back to it — in four steps: pick the thing that will bounce, remember where it starts, down low (a place memory at frame 1), send it up and bring it back down (a high place memory at frame 24 — the reference build raises it two and a half units — and the low place remembered again at frame 48), then watch it bounce and save. The teaching point is that a bounce is three memories, not two: low, high, and low again, and Blender fills in the rise and the fall between. The checks read the place memories themselves and the real evaluated height across the whole span — the span must run at least 20 frames, the peak must really clear the ground (at least one and a half units above the lower end; the reference peak is 2.5), and the two ends must sit at about the same height, so a rise that never comes back down cannot pass for a bounce. A probe on Blender 5.3.0 and 4.2.5 before building showed a low-high-low set of memories reads back and interpolates identically on both versions (0 at frame 1, 2.5 at frame 24, 0 again at frame 48). The battery's negative cases prove a plain scene ticks only step 1, a starting place alone does not prove the bounce, a straight rise that never comes back does not prove it, and a small hop (half a unit) does not prove it either. The coverage box now names all nine animation pieces and still calls them first pieces, not the whole craft. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all seventeen flows, plus the anim_bounce, anim_scale, anim_follow, anim_path, anim_loop, anim_character, anim_camera, anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_bounce_final.png — the reference build's red thing at frame 24, at the top of its bounce, in the air above the ground with its shadow below.

### v3.15.0: animation's eighth piece — "Make it grow"

Animation's eighth piece teaches growing — a thing's size changing over time — in four steps: pick the thing that will grow, remember its starting size (a scale memory at frame 1), grow it a clear amount and remember again (the reference build multiplies its size by two and a half at frame 48), then watch it grow and save. The teaching point is that the memories can hold a thing's SIZE, not only its place: two size memories, and Blender fills in every size between, so the thing grows smoothly across the span. The checks read the size memories themselves and the real evaluated size at their frames — the span must run at least 20 frames and the size must really multiply (at least 1.8 times; the reference ratio is 2.5, reading 1.73 halfway at frame 24). A probe on Blender 5.3.0 and 4.2.5 before building showed size memories read back and interpolate identically on both versions. The battery's negative cases prove a plain scene ticks only step 1, a starting size alone does not prove the grow, and a small nudge of size (1.2 times) does not prove it either. The coverage box now names all eight animation pieces and still calls them first pieces, not the whole craft. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all sixteen flows, plus the anim_scale, anim_follow, anim_path, anim_loop, anim_character, anim_camera, anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_scale_final.png — the reference build's red thing at frame 48, full-grown at two and a half times its starting size.

### v3.14.0: animation's seventh piece — "Bring a second thing along"

Animation's seventh piece teaches following — two things moving together, one set of memories — in five steps: pick the leader (one thing that will carry the move), give the leader a move that travels (its place remembered at frame 1, moved a clear distance and remembered again at frame 48, the first piece's own way), bring in a second thing (a plain shape sitting a clear step away from the leader — the reference build sets it a step and a half above, riding on top — with no memories of its own), tie it to the leader (Blender's parent tie, made keeping its place, so the follower stays exactly where it sits and is carried from there), then watch them travel together and save. The teaching point is how groups, riders, loads and props actually move in animation: not by remembering every thing's journey separately, but by tying the followers to one leader whose journey is remembered once. The checks read the leader's memories themselves (a span of at least 20 frames, a clear distance travelled), the tie itself (the follower's parent must BE the leader), and the pair's real world places read across the span — the follower must really travel (the reference build's follower travels 3.16 units) and the gap between the pair must hold (the reference gap change is 0.0). A probe on Blender 5.3.0 and 4.2.5 before building showed a tied follower rides its leader's remembered move identically on both versions, its gap unchanged at every frame. One render was rejected on sight during the build: with the follower set a step behind the leader, the proof camera saw only a sliver of it behind the leader's bulk — the reference follower now rides on top, and the pair reads clearly in the proof picture. The battery's negative cases prove a plain scene ticks only step 1, a travelling leader alone does not prove the second thing, a second thing sitting untied does not prove the tie, and a pair tied to a leader that never travels does not prove the finish. The coverage box now names all seven animation pieces and still calls them first pieces, not the whole craft. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all fifteen flows, plus the anim_follow, anim_path, anim_loop, anim_character, anim_camera, anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_follow_final.png — the reference build's pair at frame 24, halfway through the leader's move: the red leader mid-travel with the orange follower riding on top, the gap held.

### v3.13.0: animation's sixth piece — "Follow a path"

Animation's sixth piece teaches paths — the journey drawn first, then ridden — in five steps: pick the traveller (one thing that will ride the route), draw the path it will follow (a curve whose drawn line runs a real distance across the scene — the reference route runs 9 units, out, round a corner, and on), put it on the path (a Follow Path rule on the traveller, aimed at the drawn curve, measuring the journey as a share of the whole route with Fixed Location), remember the journey along it (the rule's Offset remembered at 0 at frame 1 and at the whole way, 1, at frame 48 — the memories live on the rule, not on the thing), then watch it travel and save. The teaching point is the other way animators move things: instead of remembering places and letting Blender fill in a straight-ish journey between them, the route itself is drawn and the filling-in follows it. The checks read the curve itself (its drawn length, summed along its own points), the rule itself (on the traveller, aimed at that curve, measuring by share), its Offset memories (a span of at least 20 frames, at least half the way travelled), and the traveller's real world place read across the span (the reference build's real excursion is 4.21 units — the corner makes the farthest point farther than the ends suggest). A probe on Blender 5.3.0 and 4.2.5 before building showed the rule and its Offset memories read and ride identically on both versions. One defect was found and fixed during the build: a curve created through Blender's data API is not tagged for evaluation until something tags it — in the window, operators do that invisibly — so a headless reference build's Follow Path rule read a path that was never built and the traveller never moved; the build now tags the curve plainly when it draws it, and the evaluated-place read tags the rule's target curve before reading. The battery's negative cases prove a plain scene ticks only step 1, a drawn path alone does not prove the tie, and a traveller tied to the path with no travel remembered does not prove the journey. The coverage box now names all six animation pieces and still calls them first pieces, not the whole craft. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all fourteen flows, plus the anim_path, anim_loop, anim_character, anim_camera, anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_path_final.png — the reference build's red traveller at frame 24, halfway along its drawn route, on the corner leg of the journey.

### v3.12.0: animation's fifth piece — "Make it loop"

Animation's fifth piece teaches loops — a move built to repeat — in four steps: start with a move that travels (one thing, remembered at frame 1, moved a clear distance and remembered at frame 48), make it repeat for ever (the Cycles rule on every one of the mover's place curves, so the curve plays again when it runs out), join the ends so it flows (the last memory is the starting place again, reached by a journey out to a middle memory and back, so the repeat flows instead of jumping), then watch it loop and save. The teaching point is that a loop is two halves and both are checked: repetition — the Cycles rule must be on ALL of the mover's place curves, or one axis drifts while the others repeat — and the join — the ends the same place with a real journey in between, read by putting the play line across the span (reference build: 3.16 units out and home, ends exactly together; at frame 72, a full round past the last memory, the mover is back out at its far place, mid-journey in its second round). A probe on Blender 5.3.0 and 4.2.5 before building showed the Cycles rule repeats the curve exactly as drawn on both versions. One defect was found and fixed during the build: the first travelling-move check read the distance between the first and last memories, which a finished loop reads as zero — the step unticked itself when the loop was joined; the check now reads the real excursion in between. The battery's negative cases prove a plain scene ticks no steps, a travelling move alone does not prove the repeat, a repeating straight move does not prove the joined ends, and joined ends without the rule do not prove the repeat. The coverage box now names all five animation pieces and still calls them first pieces, not the whole craft. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all thirteen flows, plus the anim_loop, anim_character, anim_camera, anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_loop_final.png — the reference build's red mover at frame 24, out at its far place on the ground, halfway through its round.

### v3.11.0: animation's fourth piece — "Make a character move"

Animation's fourth piece teaches characters — moving in parts, on a skeleton — in five steps: build a simple character (an armature of three bones — a body, an arm, a head — with a plain part tied to each), remember its first pose at frame 1 (the bones' facings, remembered the way a place is), change the pose and remember again at frame 48 (one bone turned, and Blender fills in the swing), make a second part move too (a different bone, posed and remembered the same way), then watch it move and save. The teaching point is the first piece's idea split into parts: a character does not move as one thing — each bone carries its own two memories, and the performance is the parts together. The checks read the skeleton itself: a real armature with at least three bones, a starting pose remembered, and each moved part's real turn read from the pose at its first and last remembered moments (at least 0.3 radians across at least 20 frames; reference build: the arm turns 0.9, the head 0.55). A probe on Blender 5.3.0 and 4.2.5 before building showed the factory scene has no armature at all, so nothing ticks for free, and that pose bones arrive set to quaternion turns — the reference build sets each bone to plain turns before remembering it. The battery's negative cases prove a plain scene ticks no steps, one pose alone does not prove a moved part, and one part moving alone does not prove the second part. The coverage box now names all four animation pieces and still calls them first pieces, not the whole craft; with characters taught, animation's four named pieces are complete. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all twelve flows, plus the anim_character, anim_camera, anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_character_final.png — the reference build's character at frame 24, halfway through its move, the arm mid-swing and the head mid-tilt.

### v3.10.0: animation's third piece — "Move the camera"

Animation's third piece teaches cameras — the travelling shot — in five steps: set up the shot (a subject, and the scene's camera placed and aimed at it), remember the camera's place and facing at frame 1, move the camera a clear distance and remember again at frame 48, aim it at the subject again at both ends of the move, then watch the move through the camera and save. The teaching point is the first piece's idea moved to the camera: a camera is a thing — it has a place, a facing, and it carries keyframes exactly the way a mover does. The travel checks read the camera's own memories the way "Make it move" reads a thing's; the aim step is checked from the camera's real facing, read by putting the play line on the first and last memories — the angle between where the camera is looking and the subject must be within 0.30 radians at both ends (reference build: 0.0 at both ends, 0.116 at the halfway frame; a camera moved carrying its old facing misses by 1.36 radians, probed on 4.2.5 before building). The battery's negative cases prove a plain scene ticks only step 1, one memory alone does not prove the move, and a moved camera whose facing was never remembered at the new place does not prove the aim. The coverage box now names all three animation pieces and still calls them first pieces, not the whole craft; characters remain a later piece. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all eleven flows, plus the anim_camera, anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_camera_final.png — the view through the reference build's camera at frame 24, halfway through its move, the red subject held in frame while the camera travels.

### v3.9.0: animation's second piece — "Make it glide"

Animation's second piece teaches easing and curves — the pace of a journey, and how a middle memory steers it — in four steps: start with a move that already travels (the first piece's two memories and a real journey between them), slow the ends and keep the middle (the smooth Bezier curve with an easing chosen on the memories, not inherited), bend the journey with a middle memory placed off the straight line (the path and the timing both bend around it), then watch it glide and save. The eased step is checked two ways, because Blender's own default curve is already gentle at the ends and a pace-only check would tick for free: every location memory must carry the smooth curve with a real easing picked for it, and the real pace — read by putting the play line at the span's edges, fifths and middle — must show the ends at no more than three quarters of the middle's pace (reference build: leaving at 0.56 of middle pace, arriving at 0.67, after the bend). The bend step reads the middle memory's place against the straight line between the journey's ends and demands a clear departure (at least a quarter pace). The battery's negative cases prove a plain scene ticks no steps, a travelling move on the default curve does not prove the eased step, and an eased straight journey does not prove the bend. The coverage box now names both animation pieces and still calls them first pieces, not the whole craft; cameras and characters remain later pieces. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all ten flows, plus the anim_ease, anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_ease_final.png — the reference build's red mover at frame 24, sitting on its middle memory, off the straight line between its start and end.

### v3.8.0: animation's first piece — "Make it move"

Animation arrives the way every craft arrives in Buddy: as its own guided way of working, taught the way the craft actually works. **Make it move** teaches keyframes in five steps: pick one thing, remember where it starts at frame 1, jump later, move it a clear distance and remember again — Blender fills in every frame between the two memories — then give it a turn remembered the same way, watch it play, and save. The checks read the keys themselves (on Blender 4.2 they sit on the action; on 5.x they sit in the keyframe strip's channel bag, reached through the action's slot — one helper reads both, probed on 5.3.0 and 4.2.5 before building) and the real travel and turn, read by putting the play line on the key frames. The battery's negative cases prove a plain thing ticks only step 1, one memory alone proves neither movement nor turn, and a second memory at nearly the same place does not prove travel. The coverage box now names animation's first piece and still calls it a first piece, not the whole craft; the other crafts remain plainly untaught. Verified on Blender 5.3.0 and 4.2.5: the flows battery (all nine flows, plus the anim_move and sculpting negatives), the interface battery, and the plain-layer and search batteries. The 4.2.5 passes owed for v3.4.0–v3.7.0 were also run this cycle at the v3.8.0 source, which contains those flows unchanged. The full parallel battery on an unloaded machine is still owed. Proof picture: demo/anim_move_final.png — the reference build's mover at frame 24, mid-travel and mid-turn between its two memories.

### v3.7.0: sculpting's fifth piece — "Work it at every level"

Sculpting's fifth piece teaches Multires — working one sculpt at several levels of detail at once — in five steps: start with tidy, finer clay (the net you start with is the net you keep), give it levels (a Multires modifier subdivided three times; the eye, camera and sculpt level numbers are met where they live), block the big forms at a low sculpt level where the coarse net is forgiving, work the fine detail at the top level where only a fine net can hold it, then finish smooth and save with the levels kept on the clay — never applied away. The checks read the modifier itself (a real Multires stack, at least two levels) and the surface: the big forms displaced, and the fine grain read the clay flow's honest way — smoothing the surface's distance field until only big forms survive and measuring what had to be erased — with the bar probed and set where big smooth forms alone cannot reach it (reference clay: big forms read 0.0037, big forms plus worked detail 0.0069, bar at 0.0055). The battery's negative cases prove a plain ball ticks only step 1, levels with no work tick neither worked step, big forms alone do not tick the detail step, and detail worked without Multires does not tick it either. The coverage box now names all five sculpting pieces and still calls them first pieces, not the whole craft; with Multires taught, every way a sculpt's surface is organised now has a guided piece. Verified on Blender 5.3.0: the flows battery (all eight flows, plus the Multires, masks, DynTopo and symmetry negatives), the interface battery, and the plain-layer and search batteries. The 4.2.5 pass is still owed (no 4.2.5 binary on the build machine), as is the full parallel battery on an unloaded machine. Proof picture: demo/sculpt_multires_final.png — the reference build's finished clay at its top level: the big forms blocked low, reading through the Multires smoothing, with the modifier's three levels still on the file.

### v3.6.0: sculpting's fourth piece — "Keep one part safe"

Sculpting's fourth piece teaches masks and face sets — working selectively — in five steps: fresh clay, give one area its own face set (a region with its own colour that can be hidden, shown and worked alone), mask the part you will protect (painted protection: where the mask sits, the brushes stop moving the clay), work the rest with the mask on — big work straight across the masked patch included — then finish smooth and save with the divisions kept in the file. The checks read the stores Blender keeps on the surface itself: the per-face set numbers (a real second set covering a real area, 3–70% of faces outside the biggest set), the per-point mask values (a real patch covered, 3–90% — masking everything protects nothing and does not tick), and, for the worked step, the protection itself: the masked points still sit tight together on the original ball's surface while the clay around them is displaced. The battery's negative cases prove a plain ball ticks only step 1, a face set alone does not tick the mask step, a mask over everything does not tick it either, and work that drags the masked patch along does not tick the protected-work step. The coverage box now names all four sculpting pieces and still calls them first pieces, not the whole craft; Multires remains the one untaught sculpting piece. Verified on Blender 5.3.0: the flows battery (all seven flows, plus the masks, DynTopo and symmetry negatives), the interface battery, and the plain-layer and search batteries. The 4.2.5 pass is still owed (no 4.2.5 binary on the build machine), as is the full parallel battery on an unloaded machine. Proof picture: demo/sculpt_masks_final.png — the reference build's finished clay: the pale region is the second face set, divided on the surface itself, and the smooth patch on top is the masked area the big work never moved.

### v3.5.0: sculpting's third piece — "Detail where you brush"

Sculpting's third piece teaches DynTopo (Dynamic Topology), in four steps: start with coarse clay on purpose (the detail is not there yet, and that is the point), turn DynTopo on with Constant detail — taught with its price stated plainly: the tidy net and its UVs are gone, so this is exploring and detailing clay, not a finished net — then work one small area while the rest of the clay stays coarse, then turn it off, finish smooth, and save. The checks read the surface's own spacing: DynTopo work leaves the worked area packed with close points while the rest keeps its wide coarse spacing (nearest-neighbour spacing contrast, 90th percentile over median), a contrast an even remesh never produces however fine it is. The battery's negative cases prove a plain coarse ball ticks only step 1, DynTopo on with no work does not tick the worked step, and an even fine subdivided surface does not tick it either. The coverage box now names all three sculpting pieces and still calls them first pieces, not the whole craft; masks/face sets and Multires remain untaught later pieces. Verified on Blender 5.3.0: the flows battery (all six flows, plus the DynTopo and symmetry negatives), the interface battery, and the plain-layer and search batteries. The 4.2.5 pass is still owed (no 4.2.5 binary on the build machine), as is the full parallel battery on an unloaded machine. Proof picture: demo/sculpt_dyntopo_final.png — the reference build's finished clay, one worked creased patch on an otherwise coarse ball.

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
