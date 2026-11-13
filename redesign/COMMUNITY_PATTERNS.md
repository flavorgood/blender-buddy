# Blender Buddy — Community Workflow Patterns

**Purpose:** The workflow-methods layer for the job-based redesign.
**Companion document:** `~/workspace/research_notes/blender-user-wishes-research-20261112-2058/report.md` covers *what users wish the interface did* (find it, see it, understand it in plain words, do the job not the steps, don't get punished for exploring — Right-Click Select's 17,379 ideas, quit points, confusing terms, P1–P10 roadmap). This document does **not** repeat that. It covers the layer that report lacks: *how experienced users actually sequence real jobs*, step by step, so Buddy's flows follow the order the community already teaches and uses — instead of Blender's editor layout.

**How to use this document (for the developer building the flows):**

- Each job (§1–§6) is a flow. Steps are in the order sources teach them. Do not reorder steps to match Blender's menus; the order below *is* the product.
- "Tools that matter" is deliberately 3–6 per step. That is the candidate set for the context deck at that step — everything else is hidden until the step changes (owner rule, 2026-11-12: no tools that are not needed or not usable at the moment).
- "Scene state" is the detection contract: mode, selection, and scene facts a context-aware UI can read to infer which step the user is on, and which tools are therefore usable.
- **Conventions** marked "everyone does it this way" are the checks Buddy should offer *at the step where they matter* (e.g. apply scale *before* bevel), not as a separate lecture.
- Anything labelled **unsourced** could not be backed by the gathered sources. It is included only where a flow needs a placeholder; do not present it to users as community consensus, and verify it before shipping copy that claims it.

**Evidence basis and limits:**

- Sources are Blender Manual pages, community guides and tutorial-series write-ups gathered by web search on 2026-11-12/13, plus the prior research report. Most were read as search-result extracts, not full pages; exact wording beyond the extracts was not verified.
- Blender Artists / Stack Exchange workflow-specific threads were poorly surfaced by search (the prior report records the same gap for Stack Exchange question-level data). Where forum consensus is claimed below, it is via secondary guides summarising common practice, not a counted forum vote.
- A few sources are recent third-party "skill" files and blogs (e.g. GitHub skill documents). They describe one author's practiced workflow in unusual detail and agree with the mainstream guides on order, but they are **not** canonical community sources. Where a detail rests only on such a source, it is flagged inline.
- Version note: sources span Blender 2.80 manual pages through 4.x/5.x guides. Operator names below were checked against the add-on's own live index work in the parent project (e.g. `view3d.walk`, not `view3d.walk_navigation`); when in doubt, the running Blender's registry — not this document — governs.

---

## 0. Conventions that apply to almost every job

These recur across jobs and sources. Buddy can treat them as global pre-flight checks rather than repeating them per flow.

| Convention | Why / when | Sources |
|---|---|---|
| **Reference first, never a blank viewport.** Load front/side (or photo) reference before modelling; check silhouette against it constantly. | Taught for both hard-surface and character work; "never start from a blank viewport" for characters. | https://cada-edu.com/guides/box-modelling ; https://cada-edu.com/guides/3d-character-modelling-for-games-how-to-model-in-blender ; https://www.strayspark.studio/blog/how-to-make-a-3d-character-in-blender-2026 |
| **Blockout first, detail last.** Big masses / silhouette / proportions are settled while everything is still primitives. Primary → secondary → tertiary forms, in that order. | "If the silhouette does not read at this stage, no amount of detail will save it"; sculpting sources use the identical primary/secondary/tertiary discipline. | https://www.blendertutoring.com/blog/hard-surface-modeling-blender ; https://www.strayspark.studio/blog/how-to-make-a-3d-character-in-blender-2026 ; https://3dstudio.co/blog/3d-sculpting-software/ |
| **Work at real-world scale, then Apply Scale (and usually Rotation) before** bevels, booleans, physics, baking or export. | Unapplied scale makes bevel widths and modifier results uneven. Named as a pre-step in hard-surface, printing and game-export sources alike. | https://cada-edu.com/guides/box-modelling ; https://3d-agent.com/blender-ai/3d-printing ; https://www.pixelpand.com/posts/exporting-a-blender-model-to-fbx-without-losing-your-texture-maps/ |
| **Modifiers evaluate top → bottom; order is meaning, not tidiness.** New modifiers land at the bottom (evaluated last). The Manual's own example: Mirror *then* Subdivision gives one merged surface; the reverse gives two surfaces. | Stack order changes the result, so a flow that adds modifiers must add them in the job's order and say why. | Blender Manual, Modifiers introduction (search result via https://docs.blender.org/manual/sl/4.3/modeling/modifiers/introduction.html — localised mirror; the English introduction states the same top-to-bottom rule) |
| **Keep it non-destructive until the design is locked.** Cutters, bevels, mirrors and arrays stay live modifiers; apply the stack only on an *export copy*, never on the working file. | Hard-surface guides keep boolean cutters live in their own collection until lock; game/print flows apply on a copy. | https://garagefarm.net/blog/hard-surface-modeling-in-blender ; https://www.skills.sh/el4cteo/blender-skills/blender-hardsurface-modeling (single-author skill file — practice example, not consensus) |
| **Symmetry is a modifier, not hand work.** Mirror (with Clipping on the centre axis) for anything symmetrical; model one half only. | First modifier added on most hard-surface and character blockouts. | https://cada-edu.com/guides/box-modelling ; https://www.strayspark.studio/blog/how-to-make-a-3d-character-in-blender-2026 |
| **Name things as you go, in a scheme the next step can match.** `_high` / `_low` / `_cage` suffixes for bake pairs (suffix must be **last** — Blender's auto `.001` breaks auto-matching in Substance and similar tools); boolean cutters clearly named / collected (one source uses a `CUT_*` prefix — single-author scheme, not universal). | Baking tools auto-match by name; unnamed defaults make the bake/print/export steps fail silently. | http://blender.tekriss.com/blender-and-substance-painter-tutorial-how-to-make-a-barrel-for-games-part-4-finishing-up-model/ ; https://devtalk.blender.org/t/layered-textures-design-feedback/23092/78 |
| **Origin placement is a decision, not an accident.** Origin at the object's logical pivot / ground contact / joint before mirroring, rigging, or export; "Origin to Geometry" before transform work in the game-export flow. | A misplaced origin mirrors "off into the void" (prior report §3) and breaks rigs and engine placement. | https://www.pixelpand.com/posts/exporting-a-blender-model-to-fbx-without-losing-your-texture-maps/ ; prior report §3 (Origin vs 3D Cursor confusion) |
| **Organise with Collections by role/stage**, not one flat Outliner list (e.g. model / cutters / high / low / reference). | Tripo3D's pipeline guide organises Collections by production stage; hard-surface practice keeps cutters in a separate collection. | https://www.tripo3d.ai/blog/explore/blender-3d-artwork ; https://cada-edu.com/guides/box-modelling |

---

## 1. Model a hard-surface object (mug, crate, game prop)

Canonical shape of the job, merged from the box-modelling guide, the four-stage hard-surface overview, and the GarageFarm workflow guide: **reference + scale → blockout → major forms → detail (booleans / panels) → edge control (bevel) → shading check**. A subdivision variant inserts support loops + Subdivision Surface at the forms/detail boundary; a game-prop variant continues into §5.

Sources: https://cada-edu.com/guides/box-modelling ; https://www.blendertutoring.com/blog/hard-surface-modeling-blender ; https://garagefarm.net/blog/hard-surface-modeling-in-blender

| # | Step | Tools that matter (3–6) | Scene state — what Buddy can detect |
|---|---|---|---|
| 1.1 | **Set scale + load reference.** Set/confirm real-world dimensions; add reference image(s); place them behind/around the work area. | Add Image Reference / Empty Image, Scene Units, object Dimensions, Move, Scale | Object Mode; no or one selected object; an Image Empty exists (or not — its absence at flow start is the prompt). Units/dimensions readable from scene. |
| 1.2 | **Block out the silhouette from primitives.** One cube/cylinder per big mass; no detail; check the outline from front/side/top. | Add Cube / Cylinder, Move, Scale, Rotate, Mirror modifier | Object Mode, then Edit Mode for rough shaping; several low-vertex mesh objects selected/active in turn; Mirror present on symmetric parts. Signal: low vertex counts + no bevel/boolean yet = still blockout. |
| 1.3 | **Apply transforms before real editing.** Apply Scale (and Rotation) on each blocked part (Ctrl+A). | Apply Scale, Apply Rotation, Apply All Transforms | Object Mode; object selected; `scale != (1,1,1)` or non-zero rotation is directly detectable — this is a checkable gate before 1.4. |
| 1.4 | **Build the major forms (box modelling core).** Loop cuts to place structure, inset faces for panels, extrude to raise/recess them. One guide calls inset + extrude "the heart of hard-surface box modelling". | Loop Cut (Ctrl+R), Inset (I), Extrude (E), Knife, Edge Slide | Edit Mode; face/edge selection mode; active mesh vertex count growing. Mode = Edit + face select is the strongest "forms" signal. |
| 1.5 | **Cut openings and add repeated detail — non-destructively.** Boolean cutters for holes/ports; Array for bolts, vents, ridges. Cutters stay live and hidden, in their own collection, until the design locks. | Boolean modifier (Difference/Union), Array modifier, Move (cutter placement), collection visibility toggles | Object Mode for cutter placement (two objects: target + cutter); target's modifier stack contains Boolean; cutter objects exist in a separate collection. |
| 1.6 | **(Subdivision variant) Hold the shape.** Add support loops/creases near edges that must stay crisp, then Subdivision Surface. | Loop Cut, Edge Crease, Bevel (as edge holder), Subdivision Surface modifier | Edit Mode for support loops; stack contains Subdivision Surface. If Subsurf is present with no nearby support loops, edges will "melt" — a known, warnable state (source: blendertutoring guide). |
| 1.7 | **Control the edges.** Real manufactured edges are never perfectly sharp: a small bevel (commonly 1–2 segments on a low-poly game mesh) catches the light. Prefer a live, angle-limited Bevel modifier; hand bevel (Ctrl+B) for local edges. | Bevel modifier, Bevel tool (Ctrl+B), Mean Bevel Weight / Limit Method (Angle), Shade Smooth / Smooth by Angle | Object Mode (modifier) or Edit Mode with edges selected (tool). Stack position matters: see conventions. |
| 1.8 | **Fix the shading.** Smooth shading + Weighted Normal last in the stack; check for gradients across flat faces and black/smeared patches (the classic boolean+bevel artifact). | Shade Smooth, Weighted Normal modifier, Recalculate Normals (Shift+N), Face Orientation overlay (check) | Object Mode; stack's last modifier is Weighted Normal; normals state checkable via overlay. No selection requirement. |

**"Everyone does it this way" — hard-surface:**

- **Modifier order (working stack): Mirror → Boolean(s) → Array → Solidify (if thickness needed) → Bevel → Subdivision (if used) → Weighted Normal last.** Two independently gathered practice sources agree on this order almost exactly; the Manual guarantees only the top→bottom evaluation rule, not this specific recipe — treat the recipe as *strong common practice*, not a Blender rule. Sources: https://github.com/1337VIPER/skillblend (single-author learned-workflow repo) ; https://www.skills.sh/el4cteo/blender-skills/blender-hardsurface-modeling (single-author skill file).
- Note the apparent conflict a flow must explain plainly: in a **subdivision** workflow the bevel/support work comes *before* Subsurf in the stack so the smoothing respects it; in a **mid-poly game** workflow there is no Subsurf and Bevel → Weighted Normal ends the stack. "Bevel before subdivision" is therefore a stack-order statement, not a step-order slogan.
- **Keep quads where Subsurf or deformation will touch the mesh**; booleans leave n-gons/triangle fans that shade acceptably flat but pinch under subdivision or baking — so boolean-heavy parts are either cleaned up or kept out of the Subsurf path. Source: https://www.blendertutoring.com/blog/hard-surface-modeling-blender
- **UV the base mesh before relying on bevel/boolean UV propagation** in the mid-poly game variant (after bevels, no edge is sharp enough to auto-seam reliably). Single-author skill source — flag as practice, not consensus: https://www.skills.sh/el4cteo/blender-skills/blender-hardsurface-modeling
- Cutters named and collected separately (one scheme: `CUT_*` prefix). Single-author scheme: https://github.com/dr3ladwyn/3d-agent-skills/blob/HEAD/skills/blender/blender-hard-surface/SKILL.md — cite as an example scheme only.

---

## 2. Model a simple organic / character-like thing

Canonical pipeline, agreed by all three character/sculpt sources: **reference & blockout → sculpt (primary → secondary → tertiary) → retopology → UV unwrap → bake/texturing → rig (if it will move) → pose/render**. For a *simple* organic thing (a creature, a blob character, a stylised prop), the same order applies with retopology/UV/bake shortened — but not skipped if it will be textured, rigged, or exported (see §5 for the full game version).

Sources: https://cada-edu.com/guides/3d-character-modelling-for-games-how-to-model-in-blender ; https://www.strayspark.studio/blog/how-to-make-a-3d-character-in-blender-2026 ; https://3dstudio.co/blog/3d-character-modeling/ ; sculpt-stage detail: https://3dstudio.co/blog/3d-sculpting-software/

| # | Step | Tools that matter (3–6) | Scene state — what Buddy can detect |
|---|---|---|---|
| 2.1 | **Turnaround reference + blockout.** Front/side reference planes; block the body from primitives (or a simple base mesh) against them; Mirror on X with Clipping; check silhouette and proportions constantly. | Add Image Reference, Add Cube/Sphere/Cylinder, Move/Scale/Rotate, Mirror modifier (Clipping) | Object Mode; image empties present; several primitive meshes; Mirror on the active object. Mode = Object + references present + primitives = blockout. |
| 2.2 | **Make it sculptable — pick ONE density strategy.** Dyntopo for free-form exploration; Multiresolution for predictable levels on a clean base; Voxel Remesh to merge the blockout primitives into one closed volume. Choosing is the step beginners don't know exists. | Dyntopo toggle, Multiresolution modifier, Voxel Remesh, Join (Ctrl+J) | Object Mode to join/remesh, then Sculpt Mode. Detectable: Dyntopo state, Multires level, single vs many meshes. Many un-joined primitives + user entering Sculpt Mode = "join/remesh first" moment. |
| 2.3 | **Sculpt primary forms.** Largest masses only, big brushes, low resolution: skull/torso/limb masses, overall gesture. | Grab, Clay Strips, Draw, Smooth (Shift), Inflate | **Sculpt Mode**; one active mesh; symmetry on (X). Brush identity + low mesh density is a reliable primary-forms signal. |
| 2.4 | **Sculpt secondary, then tertiary — in that order.** Secondary: muscle groups, fat pads, nose bridge, lips. Tertiary last, and only once anatomy reads: wrinkles, pores, folds. "Never sculpt a pore before the skull is right" (single-author phrasing of a universally taught rule). | Clay Strips, Crease, Pinch, Scrape/Flatten, Smooth, Mask / Face Sets | Sculpt Mode; resolution has stepped up (higher Multires level / smaller Dyntopo detail / post-remesh density jump). Density + brush size shrinking across the session tracks form-stage. |
| 2.5 | **Retopology — build the clean, animatable mesh over the sculpt.** New low-poly mesh drawn on the sculpt's surface; extra loops reserved around eyes, mouth, shoulders, elbows, knees (deformation zones). **If the sculpt changes after this, retopo, UVs and bake must all be redone** — the pipeline's most expensive surprise, so Buddy should warn *before* sculpt edits on a retopo'd asset. | Poly Build tool, Shrinkwrap modifier, Snap to Face (Face Project), Retopology overlay, Move/Extrude on the new mesh | Edit Mode on a *new, low-vertex* mesh while a high-vertex sculpt object exists and is visible as reference; snapping enabled; Shrinkwrap in the new mesh's stack. Two meshes (very high + very low) is the signature scene state. |
| 2.6 | **UV unwrap the low poly.** (Full method in §5.3 — seams → unwrap → adjust → pack.) | Mark Seam, Unwrap, UV Editor, Pack Islands | Edit Mode (all faces selected for unwrap); active object is the low poly; a UV layer now exists where none did. |
| 2.7 | **Bake + texture the detail down.** (Full method in §5.4.) Then paint/assign materials (§3). | Bake (Normal/AO), Image Texture node, Principled BSDF, Texture Paint brushes | Object Mode; both high and low exist; render engine = Cycles (baking requires it); an active Image Texture node as bake target. |
| 2.8 | **Rig if it will move** — otherwise skip straight to §3/§6. Basic version lives in §6.2. | Armature, With Automatic Weights, Weight Paint, Pose Mode | An Armature object exists; mesh has an Armature modifier / vertex groups named after bones. |

**"Everyone does it this way" — organic:**

- Primary → secondary → tertiary, resolution following form: only subdivide/remesh when current density stops you expressing the shape. Sources above (§2 header).
- Rotate the view constantly and use Smooth generously during sculpting; lumps invisible head-on are the normal failure. Source: https://www.strayspark.studio/blog/how-to-make-a-3d-character-in-blender-2026
- Dyntopo meshes are **not** final meshes: triangulated/uneven topology makes them unsuitable for animation or engines without retopology. Multiresolution wants a clean quad base and corrupts if the base is edited after subdividing. Source: https://3dstudio.co/blog/3d-sculpting-software/
- Stylised/low-poly characters may skip sculpting entirely (box modelling + Mirror) — the pipeline is a menu by goal, not a law. Source: https://www.strayspark.studio/blog/how-to-make-a-3d-character-in-blender-2026

---

## 3. Make a model look real (materials + lighting + render)

Canonical order from the two full workflow guides — note the discipline both teach: **composition and lighting are decided before material detail**, because materials are judged under the light they'll live in. One gathered pro-workflow summary puts it as maxims: "Don't add detail before the silhouette works" and "Don't tweak materials before lighting is decided." (Single secondary source for the maxims; the step order itself is corroborated by both guides below.)

Sources: https://blog.3sfarm.com/the-ultimate-blender-3d-rendering-workflow-from-scene-to-final-image ; https://www.tripo3d.ai/blog/explore/blender-3d-artwork

| # | Step | Tools that matter (3–6) | Scene state — what Buddy can detect |
|---|---|---|---|
| 3.1 | **Start from a sound model at real scale.** (§1/§2 output; real-world units — light falloff and camera behaviour depend on it.) | Dimensions check, Apply Scale, Move/Rotate | Object Mode; model objects present; scene camera may not exist yet — its absence defines the next steps. |
| 3.2 | **Compose the shot.** Add/place the camera; frame with rule-of-thirds guides; Lock Camera to View while framing. | Add Camera, Camera to View, Lock Camera to View, Composition Guides, Move/Rotate (camera) | Object Mode; a Camera object exists and is the scene camera; viewport is (or isn't) looking through it — detectable via view state. No camera = user is not yet at lighting/materials in this flow, however much they tweak nodes. |
| 3.3 | **Light v1 — three-point + environment.** Key, fill and back/rim lights for shaping; add an HDRI/world for realistic reflections and shadows. Judge shapes, ignore fine colour. | Add Light (Area/Spot/Sun), World HDRI, Light energy/colour, Move/Rotate lights, Rendered viewport shading | Object Mode; light objects count 0 → 1 → 3+ is a direct progress signal; World has an environment texture (or not). Viewport shading = Rendered is the working state for this and all following steps. |
| 3.4 | **Materials — Principled BSDF + real maps.** One Principled BSDF per surface; layer image textures: base colour, roughness map, normal map; values/scale of maps matter more than node spaghetti. | Principled BSDF, Image Texture nodes, Mapping/Texture Coordinate, Roughness/Normal inputs, Material slots + Assign | Object Mode with target object active, **or** Shader Editor context; objects with zero materials vs materials without texture nodes are distinguishable states. Selection: the object being shaded must be active. |
| 3.5 | **Light v2 + camera settings.** Colour and ratios of lights against the now-real materials; focal length, depth of field. | Light colour/energy, Camera Focal Length, Depth of Field, Exposure (AgX/Filmic — named version-dependently; verify against running Blender) | Object Mode; camera active/selected; Rendered shading on. |
| 3.6 | **Render settings + render.** Cycles for realism (Eevee for speed); samples + denoiser (OptiX / OpenImageDenoise); output resolution and path set *before* pressing render. | Render Engine (Cycles), Samples, Denoise toggle, Output resolution, Render (F12) | Any mode (usually Object); scene render settings readable in full — missing output path / Workbench engine with a "look real" goal are warnable mismatches. |
| 3.7 | **Composite.** Render passes → denoise → colour correction → glare/bloom → composite output; save the image deliberately (a render left only in the viewer is a classic lost-work moment). | Compositor nodes: Render Layers, Denoise, Color Correction, Glare, Composite/Viewer, Save As (Alt+S in the viewer) | Compositing workspace/nodes exist (or not); a Render Result image exists. Render Result present + no saved file path = "save it now" state. |

**"Everyone does it this way" — look-real:**

- Three-point first, HDRI for reflections/realism second; don't judge materials under a single default light. Both sources.
- Principled BSDF is the default material brain; realism comes from texture maps (especially roughness variation and normals), not from stacking exotic shaders. Both sources.
- Cycles = realism, Eevee = speed/preview. Both sources.
- Full pipeline order (Tripo3D): Pre-production → Modelling → UV → Texturing & Materials → Rigging & Animation (if needed) → Lighting → Rendering → Post. Note UV sits *before* materials in production order even though this flow's local order is light-then-materials: textured materials are impossible without UVs (§5.3), so Buddy should route a no-UV model to unwrap before offering texture-map tools.

---

## 4. Prepare a model for 3D printing

The most checklist-like job in Blender — and the one with an official checker. Order below follows the printing-workflow guide end to end; it is effectively a gate sequence: **units → transforms → check → fix → re-check → export → verify in slicer**. No step is optional in the sources.

Source: https://3d-agent.com/blender-ai/3d-printing (single comprehensive guide; the individual operations — Merge by Distance, Recalculate Outside, Make Manifold — are standard Blender/3D Print Toolbox operations, but the *sequence as a whole* rests on this source plus the Toolbox's own Check All design. Flagged honestly: no second full printing pipeline was gathered.)

| # | Step | Tools that matter (3–6) | Scene state — what Buddy can detect |
|---|---|---|---|
| 4.1 | **Set millimetres.** Scene Unit Scale 0.001, Length = Millimeters. STL carries unitless numbers that slicers read as mm — model in mm or the print comes out at the wrong size. | Scene Units (Unit Scale, Length), object Dimensions | Any mode; scene unit settings directly readable. Wrong units at flow start = first warning, before any mesh work. |
| 4.2 | **Finish the model + apply Rotation & Scale (Ctrl+A).** Transforms must be baked before checks mean anything. | Apply Rotation, Apply Scale, Move/Scale (final sizing) | Object Mode; object selected; non-identity scale/rotation detectable as in 1.3. |
| 4.3 | **Run the official checker: 3D Print Toolbox → Check All.** Checks: Solid (non-manifold), Intersections, Degenerate, Distorted, Thickness, Edge Sharp, Overhang. The Toolbox is an official extension — the flow's first action may be "enable it", not a mesh tool. | 3D Print Toolbox (enable extension), Check All, report panel | Object Mode (checks evaluate the object); active object is a mesh. Checker results are numeric — Buddy can read pass/fail per category if exposed; at minimum it can sequence the fixes by category. **[Unsourced detail:** whether the add-on can read Toolbox results programmatically was not verified — treat as a manual report-back step until proven.] |
| 4.4 | **Fix what the check found, by category.** Merge by Distance (doubles), Recalculate Outside (Shift+N, flipped normals), Fill Holes / Make Manifold (open shells), Solidify (zero-thickness walls), Boolean Exact → Union (overlapping shells into one solid). | Merge by Distance, Recalculate Normals, Fill Holes, Make Manifold (Toolbox), Solidify modifier, Boolean (Union, Exact solver) | Edit Mode for merge/normals/holes (vertex/edge/face selection as needed); Object Mode for Solidify/Boolean. Mode flipping in this pattern is expected — the flow, not the user, should announce which mode each fix needs. |
| 4.5 | **Re-check until clean.** Loop 4.3–4.4 until Solid and Intersections read clean; thickness/overhang reviewed (overhang is a slicer-support question, not always a mesh error). | Check All, Overhang/Thickness readouts | Same as 4.3. The loop count is state: "fixed but not re-checked" must never read as "ready". |
| 4.6 | **Export STL (or OBJ) + verify in the slicer.** Blender has no built-in 3MF exporter in this source's account — export STL, confirm size and orientation in the slicer, save 3MF from there if wanted. | Export STL, slicer (external), Dimensions (final sanity read) | Object Mode; export is the terminal action. Buddy's job ends at a verified export — size/orientation confirmation happens outside Blender (**unsourced** whether any in-Blender check can substitute; do not claim one). |

**"Everyone does it this way" — printing:**

- **Watertight/manifold or it doesn't print** — one closed solid, outward normals, real wall thickness. Every fix in 4.4 serves that single definition of "ready".
- Check → fix → **re-check** is the loop; a single pass is not the workflow.
- Units are set at the *start*, not corrected at export.

---

## 5. Prepare / export a game-ready asset (UVs, bake, export)

Canonical chain, corroborated across the baking, seams, and export sources: **high poly → low poly → name the pair → UV the low → bake high→low → sanity-check → export low + maps**. The Donut/character flows (§2) join this chain at the retopology step.

Sources: Blender Manual, Render Baking — https://docs.blender.org/manual/en/2.80/render/cycles/baking.html ; Blender Manual, Seams — https://docs.blender.org/manual/en/2.80/_sources/modeling/meshes/editing/uv/unwrapping/seams.rst.txt ; https://dev.triverse.ai/blog/low-poly-vs-high-poly ; https://www.pixelpand.com/posts/exporting-a-blender-model-to-fbx-without-losing-your-texture-maps/ ; barrel tutorial (naming) — http://blender.tekriss.com/blender-and-substance-painter-tutorial-how-to-make-a-barrel-for-games-part-4-finishing-up-model/

| # | Step | Tools that matter (3–6) | Scene state — what Buddy can detect |
|---|---|---|---|
| 5.1 | **Have both meshes: detailed high poly + clean low poly.** High from sculpt/Subsurf (§1.6/§2.4); low from retopology (§2.5) or the mid-poly base. Organise into named collections first. | Collections, Move to Collection, Rename, Hide/Show | Object Mode; two mesh objects with hugely different vertex counts is the signature state. Only one mesh exists → flow branches: mid-poly route (no bake) vs build-a-low route. |
| 5.2 | **Name the pair so tools can match them.** Same base name, differing only by suffix: `name_low` / `name_high` (plus `name_cage` if a cage is used). **Suffix must be last** — rename any `.001` endings away. | Rename (Outliner / F2), Collections | Object Mode; names are strings Buddy can literally check — one of the most automatable gates in this whole document. |
| 5.3 | **UV unwrap the LOW poly.** Manual's own loop: **mark seams → unwrap → adjust seams and repeat → adjust UVs by hand**. Seams hidden where they won't be seen; pack islands; match texel density to the target texture size across parts. | Mark Seam (Edge menu / Ctrl+E), Unwrap, UV Editor (island select/move/scale), Pack Islands, Texel-density check **[unsourced:** no built-in texel-density tool was sourced; Blender's stock UV tools do not surface a numeric texel-density readout — do not promise one] | Edit Mode on the low poly; seam edges exist (edge attribute) or don't; a UV map exists after unwrap. High poly needs no UVs for a normal bake — offering unwrap tools with the *high* selected is a wrong-context moment Buddy can catch. |
| 5.4 | **Bake high → low.** Low poly must have a UV map **and an active Image Texture node** as the bake target (Manual requirement — the bake goes nowhere without it). Use **Selected to Active**: rays cast from the low toward the high; tune Extrusion / Max Ray Distance (or a cage) when the high isn't fully enclosed by the low. Bake passes **individually** (Normal — tangent space, which Unity/Unreal expect — plus AO/roughness/metalness or Combined as the target pipeline wants), not one Combined bake for everything. Engine must be Cycles. | Render Bake panel, Selected to Active, Extrusion / Max Ray Distance / Cage, Image Texture node (target), Render Engine = Cycles, Save Image (baked maps must be saved explicitly) | Object Mode; **both** objects exist, low = active, high = selected (selection order is the bake's meaning — active-vs-selected is detectable and is the #1 bake setup error); Cycles set or not; target image node active or not. This step has the richest checkable preconditions of any in the document — build the gate here first. |
| 5.5 | **Sanitation pass before export.** Apply Scale and Rotation; check Face Orientation overlay — red/inward faces recalculated (Shift+N); origin at the placement point the engine expects. (PixelPand's order puts this before UV/bake; in practice it must simply be true before 5.6 — Buddy should check it at 5.4's gate too, since unapplied scale distorts bakes.) | Apply Scale/Rotation, Face Orientation overlay, Recalculate Normals, Set Origin | Object Mode; all directly readable (transform values, origin location, overlay state). |
| 5.6 | **Export the LOW poly + maps.** FBX (or OBJ) for the mesh; maps as PNG (EXR for 16-bit data where the pipeline wants it). Export selection = low only; high stays in the .blend as the source of truth. | Export FBX, Export OBJ, image Save As (PNG/EXR), export "Selected Objects" | Object Mode; low selected, high deselected/hidden. Wrong-selection export (shipping the high poly to the engine) is detectable at the moment of export by vertex count vs selection. |

**"Everyone does it this way" — game assets:**

- Texture-file suffixes exist but **schemes vary by studio**: one gathered scheme uses `_N` for normal maps and channel-packed `_ARM` (AO/Roughness/Metalness in separate channels — and even that poster's channel assignment is their own). Teach "pick a scheme and be consistent"; do **not** hard-code one channel packing as universal. Source: https://devtalk.blender.org/t/layered-textures-design-feedback/23092/78
- Tangent-space normals are what Unity/Unreal expect from a bake. Source: https://dev.triverse.ai/blog/low-poly-vs-high-poly
- The high poly is never the deliverable; it exists to be baked from and kept as source. Sources: all §5 sources agree implicitly; stated explicitly in the Triverse pipeline summary.

---

## 6. A short animation (object or simple rig)

Two nested workflows. **6A** is the beginner-complete job (move a thing). **6B** adds the simple rig. **6C** is the professional pass structure (blocking → spline → polish) that governs *both* once more than two keys exist — the community's single most-repeated animation method, and the one beginners have usually never heard of (they keyframe start-to-finish in smooth interpolation and fight the resulting floatiness).

Sources: https://arwall.co/blogs/arwall-blogs/how-to-animate-in-blender ; https://cada-edu.com/guides/animation ; https://cgiacademyhub.com/blog/animacion-3d-blocking-spline-polish ; SlideToDoc, "Basic Rigging and Animation" (older book chapter — mechanics only; treat UI specifics as dated).

### 6A. Animate an object

| # | Step | Tools that matter (3–6) | Scene state — what Buddy can detect |
|---|---|---|---|
| 6A.1 | **Set the shot up first.** Animation workspace; frame range decided before keying (e.g. 1–120 for 5 s at 24 fps); animations conventionally **start at frame 1**. | Animation workspace, Frame Range (Start/End), Frame Rate, Timeline | Animation workspace active; scene frame range readable. Range still at default while user starts keying = set-up not done. |
| 6A.2 | **Pose at frame 1 + key it.** Move/rotate/scale the object to its start state; Insert Keyframe (I) → Location / Rotation / LocRot / LocRotScale as the move needs. | Move/Rotate/Scale, Insert Keyframe (I), Auto Keying (optional at this level) | Object Mode; object selected; playhead at frame 1 (or Start); an Action now exists on the object with keys at the start frame. |
| 6A.3 | **Move in time, change, key again.** Jump to a later frame, change the transform, key again. Repeat per story beat. | Current Frame field / Timeline scrub, Move/Rotate, Insert Keyframe, Dope Sheet (see all keys) | Object Mode; playhead ≠ keyed frames between keys; Action's key count growing. The Dope Sheet — not the plain Timeline — is where keys can be selected, moved (G) and deleted (X); route users there the moment they ask "move my keys". |
| 6A.4 | **Shape the motion.** Timing in the Dope Sheet (slide keys, add holds); speed/ease in the Graph Editor (steep = fast, flat = slow/hold); interpolation per key (Constant = stepped, Linear = constant speed, Bezier = eased). | Dope Sheet, Graph Editor, Interpolation (T), keyframe Handles, Preview Range (loop the shot) | Animation editors open; F-Curves exist to edit — Graph Editor tools are meaningless before the first two keys, and Buddy should not offer them earlier. |

### 6B. Simple rig (the minimum that moves a character/thing with joints)

| # | Step | Tools that matter (3–6) | Scene state — what Buddy can detect |
|---|---|---|---|
| 6B.1 | **Model in a rig-friendly pose** (T-pose/A-pose for humanoids; neutral pose generally) with origin placed deliberately. | (From §1/§2) Mirror, Apply Transforms, Set Origin | Object Mode; mesh exists, no armature yet. |
| 6B.2 | **Build the armature inside the mesh.** Add Armature; in Edit Mode place bones joint-to-joint; for mechanical rigs, snap bone heads to joints via the 3D Cursor (Shift+S). One bone per moving part for hard parts. | Add Armature, Extrude bone (E), 3D Cursor snap (Shift+S), bone Rename | **Armature Edit Mode** — a distinct mode Buddy must recognise; armature is active object; mesh not selectable for editing in this state (a classic "why can't I click my model" moment). |
| 6B.3 | **Bind mesh to rig.** Select mesh, **Shift-select the armature second** (armature = active), Ctrl+P → **With Automatic Weights**. Adds the Armature modifier + bone-named vertex groups. Mechanical parts: full weight to one bone, no soft blending. | Parent (Ctrl+P) → With Automatic Weights, Armature modifier, Weight Paint (fixes), vertex groups | Object Mode; selection = exactly {mesh, armature} with armature active — selection *order/active* is the precondition and is detectable before the user presses Ctrl+P. After: mesh has Armature modifier (checkable). |
| 6B.4 | **Animate in Pose Mode.** Frame 1: LocRotScale key on the bones. Pose the key moments; then 6C's passes. | Pose Mode, Move/Rotate bones, Insert Keyframe (LocRotScale), Auto Keying, Dope Sheet | **Pose Mode** (not Object, not Edit — the third mode this job needs); armature active; keys land on bone channels in the Action. A user keying the *mesh object* while a rig exists is a wrong-target state Buddy can name. |

### 6C. The pass structure (applies to 6A and 6B)

| Pass | What happens | Tools | Detectable state |
|---|---|---|---|
| **1. Blocking** | Only the storytelling poses / extremes, on Constant (stepped) interpolation so each pose holds until the next pops. Timing and silhouette are judged with *no* smoothing. If blocking doesn't read, no polish saves it. | Insert Keyframe, Constant interpolation (T), Dope Sheet (spacing), keyframe types (Keyframe / Extreme) | All keys' interpolation = CONSTANT is a readable, exact state — Buddy can *know* a shot is in blocking, and can offer "switch to spline" only when keys exist and are all still constant. |
| **2. Breakdowns** | Poses *between* keys that explain the path (not mathematical midpoints — biased toward the extreme they belong to); arcs and anticipations appear. | Breakdown pose tools / Breakdown keyframe type, Dope Sheet, Graph Editor (checking arcs) | Keyframe types include BREAKDOWN; key count grows between existing extremes while interpolation may still be Constant ("blocking plus"). |
| **3. Spline** | Convert keys to Bezier; the computer's even easing makes everything floaty at first — expected, not a failure. Shape curves: sharpen contacts, allow overshoot only where wanted (Auto Clamped handles are the Manual-recommended default per the CGI Academy summary). | Set Interpolation → Bezier (T), Graph Editor handles, handle types | Interpolation flips CONSTANT → BEZIER across keys: the spline transition is a single detectable event and the right moment to surface Graph Editor tools. |
| **4. Polish** | Fix sliding contacts/feet, clean arcs, offset keys so parts don't move in unison (overlap/follow-through), add settles and moving holds; retime accents in the Dope Sheet; loop with Preview Range. | Graph Editor, Dope Sheet (retime/offset), Motion Paths (arc check) **[partially unsourced:** motion-path use in polish is asserted by the DayZ knowledge-pack research file, a single secondary source], Preview Range | Bezier keys + keys being nudged/offset; playhead looping a preview range. Polish tools offered during blocking are noise — pass detection is what keeps the deck honest. |

Sources for 6C: https://cada-edu.com/guides/animation ; https://cgiacademyhub.com/blog/animacion-3d-blocking-spline-polish ; https://animost.com/ideas-inspirations/how-do-i-make-my-animation-smoother-in-blender/ (passes named identically: Blocking → Splining → Polishing).

---

## 7. (a) Methods experienced users rely on that beginners don't know exist

Ranked by how many of the six jobs they unlock. Each row: the method, why beginners miss it, and where Buddy should surface it. All are evidenced in §§0–6 sources unless marked.

| # | Method | Why beginners miss it | Surface it… |
|---|---|---|---|
| M1 | **Apply Transforms (Ctrl+A) before modifiers/bakes/export** | Nothing in the UI says object scale is "unapplied"; bevels just come out uneven and the cause is invisible. | As a gate check at §1.3, §4.2, §5.5 — detectable exactly (scale/rotation values). |
| M2 | **Non-destructive modifier stacks with deliberate order** | Beginners apply modifiers immediately (or model destructively) because "Apply" looks like "confirm". They don't know the stack is editable, reorderable, and evaluated top→bottom. | Whenever a flow adds a second modifier; show the stack as the job's recipe (§1 conventions), not as a property panel. |
| M3 | **Blockout-first / primary→secondary→tertiary discipline** | Beginners start with the detail they can picture (an eye, a bolt) and strand the proportions. Every tutorial tradition teaches the opposite order. | At flow start for §1, §2, §6C — and as a gentle state read: high detail + unsettled silhouette = warn. |
| M4 | **Reference images as scene objects** | Beginners alt-tab to a browser photo; the idea of pinning front/side references *inside* the scene is a workflow, not a tool they go looking for. | Step 1 of §1 and §2; absence of references at blockout is detectable. |
| M5 | **Mirror + Clipping instead of modelling both sides** | Symmetry by hand looks "simpler" until the halves disagree. | First modifier offered for any symmetric blockout (§0). |
| M6 | **Live boolean cutters in their own collection** | Beginners apply booleans instantly, inherit n-gon topology they can't edit, and lose the ability to move the hole. | §1.5; cutter collection + live Boolean in stack is the teachable pattern. |
| M7 | **Collections as roles (model / cutters / high / low / reference)** | The Outliner reads as a flat list; colour-coded collections were themselves a top community request (prior report §1a). | Flow setup for §1, §5; collection names become flow state (§5.1–5.2). |
| M8 | **Selection order is meaning: active vs selected** | Bake (Selected to Active), parenting (mesh then armature), and booleans all silently depend on *which* object is active. Nothing visual explains the distinction; the prior report flags the general mode/selection confusion (§3). | At §5.4 and §6B.3 gates — both are checkable before the operation runs. |
| M9 | **A step isn't done until it's checked in the right view**: Face Orientation overlay for normals, Rendered shading for materials, Check All for printing, silhouette views for blockout. | Beginners check in the default Solid view, where normals, shading errors and scale problems are literally invisible. | Pair every "fix" step above with its check step (§1.8, §3.3, §4.3/4.5, §5.5). |
| M10 | **Save/keep the source, export a copy.** Working .blend keeps live stacks, high polys and cutters; applied/baked/exported artefacts are derived. | Beginners overwrite the only copy by applying everything "to finish it". | §5.6 and §4.6 exits; the flow's last step is always an export, never an apply, on the working file. **[Design recommendation, synthesis — not a quoted community rule, though it follows from M2 + the hard-surface sources' "apply only on an export copy".]** |
| M11 | **Animation is done in passes (block → spline → polish), not start-to-finish** | The default (Bezier) interpolation invites keying pose 1, then pose 2, then wondering why everything floats. Stepped blocking is a *method*, invisible in the UI. | §6C; interpolation state makes the current pass detectable, so the deck can change per pass. |
| M12 | **Retopology is a separate, planned step** — sculpt output is not the final mesh. | Beginners try to rig/UV/export the sculpt directly and hit topology walls with no name for the missing step. | §2.5, including the redo warning: sculpt edits after retopo invalidate retopo + UV + bake. |
| M13 | **The Adjust Last Operation panel (F9) and Quick Favorites (Q) / F3 search as recovery tools** | Prior report §2: the adjust panel vanishes after the next action and its F9 recall is something even the Donut tutorial's author says he never remembers; F3/Q are experienced as "secrets". | Not a job step — a *rescue* layer under every flow: when state diverges from the flow's expectation, these are the community's own way back. (Evidence: prior report, not re-sourced here.) |
| M14 | **Naming for machine matching (`_low`/`_high`, suffix last)** | Beginners name for humans only, then bake/paint tools fail to pair assets with no error message. | §5.2 as an automatic rename offer — strings are checkable. |

---

## 8. (b) Flow-design cheat sheet — reading the scene to know the step

Consolidated detection signals from §§1–6, ordered by reliability. "Hard" signals are exact reads of Blender state; "soft" signals are heuristics to confirm with the user, never to silently advance a flow on.

**Hard signals (exact state reads):**

- **Mode**: Object / Edit (mesh) / Sculpt / Pose / Armature-Edit / Weight Paint / UV Editor focus. Mode alone partitions most steps: Sculpt ⇒ §2.3–2.4; Pose ⇒ §6B.4; Edit ⇒ forming, fixing, retopo, or UV work (disambiguate by active object, below).
- **Active object's data**: vertex count (primitive-low vs sculpt-high vs retopo-low), modifier stack contents *and order* (Mirror? Boolean? Bevel? Subsurf? Weighted Normal last? Armature?), material count and whether materials have texture nodes, existence of a UV layer, seam edges, vertex groups named after bones.
- **Transform values**: scale ≠ 1 or rotation ≠ 0 ⇒ Apply-Transforms gate is open (M1) in any flow.
- **Scene facts**: camera exists / is scene camera; light count and types; World has an HDRI; render engine (Cycles required for bake; Cycles-vs-Eevee is a §3 choice); unit scale/length (§4.1); frame range and current frame (§6).
- **Animation data**: an Action exists; key count; keyframe types present (EXTREME/KEYFRAME vs BREAKDOWN); interpolation across keys (all CONSTANT ⇒ blocking; mixed/Bezier ⇒ splining or polish).
- **Selection composition**: exactly {mesh, armature} with armature active ⇒ ready to bind (§6B.3); {low active + high selected} ⇒ bake-ready *if* Cycles + target image node also hold (§5.4); low-only selected with high hidden ⇒ export pose (§5.6).
- **Names**: `_low`/`_high` pairing, `.001` suffixes, a cutter collection — string checks (§5.2, M14).

**Soft signals (probable step — confirm, don't assume):**

- Brush identity + mesh density trend in Sculpt Mode ⇒ primary vs tertiary stage (§2.3–2.4).
- Several low-vertex objects + references present + no modifiers beyond Mirror ⇒ still in blockout (§1.2/§2.1).
- Render Result exists + no output path/file saved ⇒ end of §3, "save it" moment.
- Repeated Edit↔Object mode flipping with merge/normals operators used ⇒ inside the §4 fix loop; completion is defined *only* by a clean re-check (§4.5), not by fixes attempted.

**Design consequences (synthesis — the developer's takeaways, not community claims):**

1. **Precondition gates beat instructions.** The highest-value checks in this document are all hard signals at known failure points: apply-scale before bevel/boolean/bake/export; active-image-node + Cycles + selection order before bake; armature-active before parenting; units before printing checks; Mirror-before-Subsurf stack order. Buddy should *read and announce* these, in plain words, at the step — that is M1/M8 turned into UI.
2. **The deck per step is small because the method is narrow.** Each step above genuinely uses 3–6 tools in community practice. If a step's deck needs more, the step is probably two steps.
3. **Mode is the cheapest context.** Half the "wrong tools shown" problem is mode: sculpt brushes in Object Mode, Graph Editor before keys exist, unwrap tools on the high poly. Mode + active-object checks retire most of it before any job logic runs.
4. **Progress = state change, not clicks.** Every flow here has a state-defined done-condition (clean Check All; UV layer exists; keys exist at both beats; Weighted Normal is last in stack). Advance the flow when the *scene* proves the step — the same teach-first principle the Donut package already uses.
5. **Name the expensive surprises early.** Retopo-invalidation (§2.5), bake-without-target-image (§5.4), print-at-wrong-units (§4.1) and floaty-first-spline (§6C.3) are all places where community practice exists *because* the failure is costly or confusing. A one-line warning at the step before is worth more than a fix-up flow after.

---

## Sources index

Prior research (companion): `~/workspace/research_notes/blender-user-wishes-research-20261112-2058/report.md` — UX wishes, Right-Click Select archive (17,379 ideas, verified live 2026-11-12), quit points, confusing terms, P1–P10 roadmap.

Workflow sources gathered for this document (URLs verbatim from search results):

- Hard-surface: https://cada-edu.com/guides/box-modelling · https://www.blendertutoring.com/blog/hard-surface-modeling-blender · https://garagefarm.net/blog/hard-surface-modeling-in-blender · https://www.skills.sh/el4cteo/blender-skills/blender-hardsurface-modeling (single-author) · https://github.com/1337VIPER/skillblend (single-author) · https://github.com/dr3ladwyn/3d-agent-skills/blob/HEAD/skills/blender/blender-hard-surface/SKILL.md (single-author; a second copy of this URL was returned as `/.claude/skills/hard-surface/SKILL.md` under another repo — not cited in the body)
- Organic/character/sculpt: https://cada-edu.com/guides/3d-character-modelling-for-games-how-to-model-in-blender · https://www.strayspark.studio/blog/how-to-make-a-3d-character-in-blender-2026 · https://3dstudio.co/blog/3d-character-modeling/ · https://3dstudio.co/blog/3d-sculpting-software/ · https://github.com/prokstudio/skills/blob/HEAD/skills/blender/blender-sculpting/SKILL.md (single-author)
- Look real: https://blog.3sfarm.com/the-ultimate-blender-3d-rendering-workflow-from-scene-to-final-image · https://www.tripo3d.ai/blog/explore/blender-3d-artwork
- 3D printing: https://3d-agent.com/blender-ai/3d-printing
- Game-ready: https://docs.blender.org/manual/en/2.80/render/cycles/baking.html · https://docs.blender.org/manual/en/2.80/_sources/modeling/meshes/editing/uv/unwrapping/seams.rst.txt · https://dev.triverse.ai/blog/low-poly-vs-high-poly · https://www.pixelpand.com/posts/exporting-a-blender-model-to-fbx-without-losing-your-texture-maps/ · http://blender.tekriss.com/blender-and-substance-painter-tutorial-how-to-make-a-barrel-for-games-part-4-finishing-up-model/ · https://devtalk.blender.org/t/layered-textures-design-feedback/23092/78
- Animation: https://arwall.co/blogs/arwall-blogs/how-to-animate-in-blender · https://cada-edu.com/guides/animation · https://cgiacademyhub.com/blog/animacion-3d-blocking-spline-polish · https://animost.com/ideas-inspirations/how-do-i-make-my-animation-smoother-in-blender/ · https://blenderzen.com/2023/07/09/blender-robot-arm-rigging-and-animation/ (mechanical rig pattern, §6B.2–6B.3 supporting detail)
- Modifiers: Blender Manual, Modifiers introduction (top→bottom evaluation; localised result URL https://docs.blender.org/manual/sl/4.3/modeling/modifiers/introduction.html)

**Explicitly unsourced / not verified in this pass** (do not upgrade without new evidence):

- Whether Buddy can programmatically read 3D Print Toolbox check results (§4.3).
- A built-in numeric texel-density readout in stock Blender (§5.3).
- Motion Paths as a standard polish-pass tool (§6C.4) — single secondary source.
- Any Reddit, YouTube-comment, or Blender Stack Exchange question-level workflow data — not retrievable in this or the prior pass; no figures are quoted for them.
- Exact version behaviour of colour-management/view-transform names in §3.5 — verify against the running Blender at build time.
