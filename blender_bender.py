"""
Blender Bender - Blender in plain words (prototype 0.2)

Design rule (the whole point of this add-on):
    A day-1 beginner must be able to use every button without already
    knowing Blender. So:
      * The big label on every button is the JOB, in plain words
        ("Round off a sharp edge"), never the jargon ("Bevel").
      * Under every button, one plain sentence says what it does and
        when you would want it.
      * Blender's real name and its keyboard shortcut are shown in
        small text under that, so a beginner learns the real words
        while working - the jargon is taught, never required.
      * The panel always says where you are and what to do next.
      * Buttons that need a first step do that step for you and tell
        you (e.g. a shaping button pressed too early switches you
        into shaping mode and picks everything, then asks you to
        press it again).

Nothing is removed or replaced: every button simply runs Blender's
own tool underneath, and Blender's normal interface stays untouched.
"""

import os
import textwrap

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import Operator, Panel

bl_info = {
    "name": "Blender Bender - Blender in Plain Words",
    "author": "Blender Bender prototype",
    "version": (0, 2, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar (N key) > Blender Bender tab",
    "description": "Every common Blender tool, labelled by the job it does, "
                   "explained in plain words, searchable in your own words.",
    "category": "3D View",
}


# ----------------------------------------------------------------------------
# The action catalogue.
# plain  = the button label. The job, in words a beginner already knows.
# does   = one plain sentence: what happens, and when you'd want it.
# real   = Blender's own name for it (taught, never required).
# key    = Blender's shortcut for it.
# kind   = how to run it: op | tool | modifier | mode | custom
# target = the Blender operator / tool id / modifier type underneath.
# needs  = None | "object" (something must be picked) | "edit" (shaping mode)
#          | "two" (two things picked, for the cut-a-hole action)
# words  = extra everyday words people might search for.
# ----------------------------------------------------------------------------

ACTIONS = [
    # -- 1. Add something ----------------------------------------------------
    dict(id="add_cube", section="1. Add something",
         plain="Add a box",
         does="The starting shape for most models. Add it, then move it, size it and shape it.",
         real="Cube", key="Shift+A", icon="MESH_CUBE",
         kind="op", target="mesh.primitive_cube_add", words="cube square block start"),
    dict(id="add_ball", section="1. Add something",
         plain="Add a ball",
         does="A round ball. Wheels, heads, planets, knobs - anything round starts here.",
         real="UV Sphere", key="Shift+A", icon="MESH_UVSPHERE",
         kind="op", target="mesh.primitive_uv_sphere_add", words="sphere round circle"),
    dict(id="add_tube", section="1. Add something",
         plain="Add a tube",
         does="A cylinder: legs, pipes, cups, tree trunks, poles.",
         real="Cylinder", key="Shift+A", icon="MESH_CYLINDER",
         kind="op", target="mesh.primitive_cylinder_add", words="cylinder pipe pole leg cup"),
    dict(id="add_cone", section="1. Add something",
         plain="Add a cone",
         does="Pointy on top, round at the bottom: roofs, spikes, ice-cream cones.",
         real="Cone", key="Shift+A", icon="MESH_CONE",
         kind="op", target="mesh.primitive_cone_add", words="point spike roof"),
    dict(id="add_ring", section="1. Add something",
         plain="Add a donut ring",
         does="A ring with a hole in the middle: tyres, rings, donuts, handles.",
         real="Torus", key="Shift+A", icon="MESH_TORUS",
         kind="op", target="mesh.primitive_torus_add", words="torus tyre tire hole ring"),
    dict(id="add_sheet", section="1. Add something",
         plain="Add a flat sheet",
         does="One flat surface with no thickness: the ground, a wall, a table top, a piece of paper.",
         real="Plane", key="Shift+A", icon="MESH_PLANE",
         kind="op", target="mesh.primitive_plane_add", words="plane ground floor flat wall table"),
    dict(id="add_monkey", section="1. Add something",
         plain="Add the test monkey",
         does="Blender's practice head. Safe to experiment on - mangle it, undo, learn. Nothing is lost.",
         real="Monkey (Suzanne)", key="Shift+A", icon="MESH_MONKEY",
         kind="op", target="mesh.primitive_monkey_add", words="suzanne practice test head"),
    dict(id="add_words", section="1. Add something",
         plain="Add words / letters",
         does="Type real text as a 3D shape - signs, logos, labels, names.",
         real="Text", key="Shift+A", icon="FONT_DATA",
         kind="op", target="object.text_add", words="text letters sign logo label name type"),

    # -- 2. Move & size it ----------------------------------------------------
    dict(id="tool_pick", section="2. Move it & size it",
         plain="Pick things with the mouse",
         does="The normal mouse. Click a thing to pick it; everything else works on the thing you picked.",
         real="Select Box tool", key="W", icon="",
         kind="tool", target="builtin.select_box", words="select choose click cursor"),
    dict(id="tool_move", section="2. Move it & size it",
         plain="Move it around",
         does="Drag the picked thing to a new place. The coloured arrows move it one way at a time.",
         real="Move tool", key="G", icon="",
         kind="tool", target="builtin.move", needs="object", words="drag place position shift"),
    dict(id="tool_turn", section="2. Move it & size it",
         plain="Turn it",
         does="Spin the picked thing around, like turning a chair to face another way.",
         real="Rotate tool", key="R", icon="",
         kind="tool", target="builtin.rotate", needs="object", words="rotate spin angle face"),
    dict(id="tool_size", section="2. Move it & size it",
         plain="Make it bigger or smaller",
         does="Stretch or shrink the picked thing. Drag outwards for bigger, inwards for smaller.",
         real="Scale tool", key="S", icon="",
         kind="tool", target="builtin.scale", needs="object", words="scale resize stretch shrink grow"),
    dict(id="copy_it", section="2. Move it & size it",
         plain="Make a copy of it",
         does="A second one, exactly the same. The copy is picked, so move it where you want it.",
         real="Duplicate", key="Shift+D", icon="",
         kind="custom", target="duplicate", needs="object", words="duplicate clone another second"),
    dict(id="throw_away", section="2. Move it & size it",
         plain="Throw it away",
         does="Deletes the picked thing completely. Ctrl+Z brings it back if you change your mind.",
         real="Delete", key="Delete", icon="TRASH",
         kind="custom", target="delete_object", needs="object", words="delete remove bin trash undo"),

    # -- 3. Shape it ----------------------------------------------------------
    dict(id="start_shaping", section="3. Shape it",
         plain="Start shaping it",
         does="Switches from moving whole things to changing one thing's shape - its corners, edges and faces. Press again (or the same key) to go back.",
         real="Edit Mode", key="Tab", icon="MESH_DATA",
         kind="mode", target="EDIT", needs="object", words="edit mode change shape points faces mesh"),
    dict(id="pull_face", section="3. Shape it",
         plain="Pull a face out (or push it in)",
         does="The main building move in Blender. Pick a flat face, then drag: the shape grows out there. Houses, boxes, handles - all built this way.",
         real="Extrude Region", key="E", icon="",
         kind="op", target="mesh.extrude_region_move", needs="edit", words="extrude grow lengthen extend taller push"),
    dict(id="inset_face", section="3. Shape it",
         plain="Make a smaller face inside a face",
         does="Draws a new, smaller face inside the one you picked - like outlining a window or a panel before you push it in or pull it out.",
         real="Inset Faces", key="I", icon="",
         kind="op", target="mesh.inset", needs="edit", words="panel window inset border frame"),
    dict(id="round_edge", section="3. Shape it",
         plain="Round off a sharp edge",
         does="Real things are almost never razor sharp. This softens a picked edge or corner so it catches the light like a real object.",
         real="Bevel", key="Ctrl+B", icon="",
         kind="op", target="mesh.bevel", needs="edit", words="bevel round soften edge corner smooth sharp"),
    dict(id="loop_cut", section="3. Shape it",
         plain="Add a ring of edges around it",
         does="Slices a new ring all the way around the shape, so you can shape one part of it - like adding a crease line.",
         real="Loop Cut", key="Ctrl+R", icon="",
         kind="tool", target="builtin.loop_cut", needs="edit", words="slice ring crease cut around"),
    dict(id="knife", section="3. Shape it",
         plain="Draw a cut with the mouse",
         does="Click point to point to draw your own cut lines on the surface, exactly where you want them. Enter finishes the cut.",
         real="Knife tool", key="K", icon="",
         kind="tool", target="builtin.knife", needs="edit", words="cut draw line slice freehand"),
    dict(id="split_faces", section="3. Shape it",
         plain="Split faces into smaller faces",
         does="Chops each picked face into four smaller ones, giving you more points to shape with. Use it where you need more detail.",
         real="Subdivide", key="right-click menu", icon="",
         kind="op", target="mesh.subdivide", needs="edit", words="subdivide more detail split grid"),
    dict(id="fill_face", section="3. Shape it",
         plain="Fill in a missing face",
         does="Pick the edges around a hole and this covers it with a new face, like patching a gap.",
         real="Make Face", key="F", icon="",
         kind="op", target="mesh.edge_face_add", needs="edit", words="face fill hole patch cover gap"),

    # -- 4. Copy & combine ----------------------------------------------------
    dict(id="mirror_it", section="4. Copy it & combine it",
         plain="Copy it, flipped, to the other side",
         does="Build one side and this keeps an identical flipped copy on the other side - faces, cars, tables. Change one side, the other follows.",
         real="Mirror modifier", key="-", icon="MODIFIER",
         kind="modifier", target="MIRROR", needs="object", words="mirror flip symmetry other side both sides"),
    dict(id="row_of_them", section="4. Copy it & combine it",
         plain="Repeat it in a row",
         does="Makes evenly spaced copies in a line: fence posts, stairs, windows, teeth on a gear.",
         real="Array modifier", key="-", icon="MODIFIER",
         kind="modifier", target="ARRAY", needs="object", words="array repeat row pattern fence steps copies"),
    dict(id="glue_together", section="4. Copy it & combine it",
         plain="Glue picked things into one thing",
         does="Turns everything you picked into a single object, so it moves and saves as one piece.",
         real="Join", key="Ctrl+J", icon="",
         kind="op", target="object.join", needs="object", words="join merge combine together one"),
    dict(id="cut_hole", section="4. Copy it & combine it",
         plain="Cut one shape out of another",
         does="Pick TWO things: first the thing to cut into, then the thing doing the cutting (pick the cutter LAST). The cutter's shape is removed - holes, slots, doorways.",
         real="Boolean Difference", key="-", icon="",
         kind="custom", target="boolean_cut", needs="two", words="boolean hole cut out remove drill doorway slot subtract"),

    # -- 5. Make it look right -------------------------------------------------
    dict(id="make_smoother", section="5. Make it look right",
         plain="Make it smoother & rounder",
         does="Softens and rounds the whole shape by itself. Blocky things start to look carved or moulded. Safe: removing it brings the blocky shape back.",
         real="Subdivision Surface modifier", key="Ctrl+1", icon="MODIFIER",
         kind="modifier", target="SUBSURF", needs="object", words="subdivision smooth round soften catmull"),
    dict(id="give_thickness", section="5. Make it look right",
         plain="Give a flat sheet some thickness",
         does="A flat sheet becomes a real slab with sides - paper becomes card, a surface becomes a wall or a lid.",
         real="Solidify modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SOLIDIFY", needs="object", words="solidify thick wall slab hollow shell"),
    dict(id="round_all_edges", section="5. Make it look right",
         plain="Round ALL its edges a little",
         does="Like 'round off a sharp edge', but for the whole thing at once, without picking edges one by one.",
         real="Bevel modifier", key="-", icon="MODIFIER",
         kind="modifier", target="BEVEL", needs="object", words="bevel round edges all soften"),
    dict(id="look_smooth", section="5. Make it look right",
         plain="Make it LOOK smooth (not blocky)",
         does="Only changes how light falls on it - the shape stays the same, but faces stop looking like flat panels. Balls and curves want this.",
         real="Shade Smooth", key="right-click menu", icon="",
         kind="op", target="object.shade_smooth", needs="object", words="shade smooth shading faceted blocky light"),
    dict(id="look_flat", section="5. Make it look right",
         plain="Make it look flat & crisp",
         does="The opposite: every face looks flat and distinct, like cut metal or a gemstone.",
         real="Shade Flat", key="right-click menu", icon="",
         kind="op", target="object.shade_flat", needs="object", words="shade flat faceted crisp panels"),
    dict(id="give_colour", section="5. Make it look right",
         plain="Give it a colour",
         does="Paints the picked thing red, so you can see colours are just a coating you can change any time. Change the colour later in the Material tab.",
         real="Material", key="-", icon="MATERIAL",
         kind="custom", target="colour", needs="object", words="color colour paint material red coating"),

    # -- 6. Fix common problems -------------------------------------------------
    dict(id="fix_faces", section="6. Fix common problems",
         plain="Fix dark or inside-out faces",
         does="If parts of your model look strangely dark, the faces there are probably pointing the wrong way. This turns them all to face outwards.",
         real="Recalculate Normals", key="Shift+N", icon="",
         kind="op", target="mesh.normals_make_consistent", needs="edit", words="normals dark inside out wrong way shading black"),
    dict(id="join_close_points", section="6. Fix common problems",
         plain="Join points that sit on top of each other",
         does="Models often end up with doubled points in the same spot, which causes cracks and weird shading. This welds them into one.",
         real="Merge by Distance", key="M > By Distance", icon="",
         kind="op", target="mesh.remove_doubles", needs="edit", words="merge distance doubles weld duplicate points cracks"),
    dict(id="lock_size", section="6. Fix common problems",
         plain="Lock in its size & turn (fixes odd behaviour)",
         does="If you stretched something and other tools start behaving strangely, this tells Blender 'this size is normal now'. The shape does not change.",
         real="Apply Scale & Rotation", key="Ctrl+A", icon="",
         kind="custom", target="apply_transforms", needs="object", words="apply transform scale rotation weird behaves wrong"),
    dict(id="handle_middle", section="6. Fix common problems",
         plain="Put its grab-point in the middle",
         does="Every thing has a handle point it turns and mirrors around. If yours is off to one side, this puts it back in the middle of the shape.",
         real="Set Origin to Geometry", key="right-click menu", icon="",
         kind="custom", target="origin_middle", needs="object", words="origin pivot handle center middle turns around"),

    # -- 7. More shapes -------------------------------------------------------
    dict(id="add_faceted_ball", section="7. More shapes",
         plain="Add a faceted ball",
         does="A ball made of flat triangles - like a gem or a low-poly planet. Games and stylised models use this one.",
         real="Ico Sphere", key="Shift+A", icon="MESH_ICOSPHERE",
         kind="op", target="mesh.primitive_ico_sphere_add", words="icosphere gem dice low poly ball"),
    dict(id="add_circle", section="7. More shapes",
         plain="Add a flat circle",
         does="A flat disc or ring outline: plates, lids, wheels seen from the side.",
         real="Circle", key="Shift+A", icon="MESH_CIRCLE",
         kind="op", target="mesh.primitive_circle_add", words="disc plate lid round flat"),
    dict(id="add_grid", section="7. More shapes",
         plain="Add a sheet of squares",
         does="A flat sheet already divided into a grid - good for tiled floors, cloth, and land you want to sculpt into hills.",
         real="Grid", key="Shift+A", icon="",
         kind="op", target="mesh.primitive_grid_add", words="grid tiles floor ground landscape squares"),
    dict(id="add_bendy_line", section="7. More shapes",
         plain="Add a bendy line",
         does="A line with handles you pull to bend it. The start of ropes, wires, hoses - and of outlines you spin or grow tubes from.",
         real="Bezier Curve", key="Shift+A", icon="",
         kind="op", target="curve.primitive_bezier_curve_add", words="curve line rope wire hose bend path"),
    dict(id="add_sun", section="7. More shapes",
         plain="Add sunlight",
         does="Light that comes from one direction, like the sun: bright, even, with shadows. Every outdoor scene needs light or the picture is black.",
         real="Sun Light", key="Shift+A", icon="",
         kind="op", target="object.light_add", args={"type": "SUN"}, words="sun light bright day outside shadow"),
    dict(id="add_lamp", section="7. More shapes",
         plain="Add a lamp",
         does="A single point of light, like a bulb: glows in all directions and fades with distance.",
         real="Point Light", key="Shift+A", icon="",
         kind="op", target="object.light_add", args={"type": "POINT"}, words="point light bulb lamp glow indoor"),
    dict(id="add_camera", section="7. More shapes",
         plain="Add a camera",
         does="The picture Blender takes is seen through a camera. No camera, no picture. You move it like any other thing.",
         real="Camera", key="Shift+A", icon="",
         kind="op", target="object.camera_add", words="camera photo picture render view shot"),
    dict(id="add_handle", section="7. More shapes",
         plain="Add an invisible handle",
         does="An empty marker that shows in your workspace but never in the picture. Other things can be attached to it, aim at it, or mirror around it.",
         real="Empty (Plain Axes)", key="Shift+A", icon="",
         kind="op", target="object.empty_add", args={"type": "PLAIN_AXES"}, words="empty marker anchor target attach"),

    # -- 8. More ways to shape it ---------------------------------------------
    dict(id="smooth_points", section="8. More ways to shape it",
         plain="Smooth out lumps",
         does="Nudges the picked points toward even, so a bumpy surface calms down without changing what the thing is.",
         real="Smooth Vertices", key="right-click menu", icon="",
         kind="op", target="mesh.vertices_smooth", needs="edit", words="smooth lumps bumps even vertices relax"),
    dict(id="poke_face", section="8. More ways to shape it",
         plain="Poke a face into slices",
         does="Puts a new point in the middle of a face and joins it to every corner - pizza slices. The middle point is easy to pull up into a bump or spike.",
         real="Poke Faces", key="Alt+P", icon="",
         kind="op", target="mesh.poke", needs="edit", words="poke fan triangles centre center spike bump"),
    dict(id="make_triangles", section="8. More ways to shape it",
         plain="Turn faces into triangles",
         does="Splits every picked four-sided face into two triangles. Games and some 3D printing paths want everything in triangles.",
         real="Triangulate Faces", key="Ctrl+T", icon="",
         kind="op", target="mesh.quads_convert_to_tris", needs="edit", words="triangulate triangles tris games export"),
    dict(id="make_quads", section="8. More ways to shape it",
         plain="Turn triangles back into four-sided faces",
         does="The tidy-up opposite: joins pairs of triangles into four-sided faces where it can, which are easier to shape.",
         real="Tris to Quads", key="Alt+J", icon="",
         kind="op", target="mesh.tris_convert_to_quads", needs="edit", words="quads triangles tidy convert faces"),
    dict(id="erase_edges", section="8. More ways to shape it",
         plain="Erase edges without making a hole",
         does="Removes the picked edges and joins the faces around them into one bigger face. The surface stays whole.",
         real="Dissolve Edges", key="X > Dissolve", icon="",
         kind="op", target="mesh.dissolve_edges", needs="edit", words="dissolve remove edges merge faces hole"),
    dict(id="make_same_both_sides", section="8. More ways to shape it",
         plain="Make both sides the same",
         does="Copies one half of the shape over the other half, exactly. Fixes a face or a car body that drifted lopsided while you worked.",
         real="Symmetrize", key="Mesh menu", icon="",
         kind="op", target="mesh.symmetrize", needs="edit", words="symmetry symmetrize same both sides mirror lopsided"),
    dict(id="split_off", section="8. More ways to shape it",
         plain="Split the picked part off as its own thing",
         does="The part you've picked becomes a separate object you can move, colour or delete on its own - like cutting a piece off to work on it.",
         real="Separate by Selection", key="P", icon="",
         kind="custom", target="separate_piece", needs="edit", words="separate split part own object detach"),

    # -- 9. The rest of the modifiers -----------------------------------------
    dict(id="simplify_faces", section="9. Every other modifier",
         plain="Use fewer faces (make it lighter)",
         does="Simplifies the shape so it has fewer faces: faster to work with and what games want. Half strength to start - push it too far and detail melts.",
         real="Decimate modifier", key="-", icon="MODIFIER",
         kind="modifier", target="DECIMATE", needs="object", words="decimate simplify fewer faces lighter games low poly"),
    dict(id="crisp_edges_mod", section="9. Every other modifier",
         plain="Keep edges crisp where smoothing went mushy",
         does="Tells Blender 'this edge is a real edge' - smoothed shapes keep their sharp corners instead of looking melted.",
         real="Edge Split modifier", key="-", icon="MODIFIER",
         kind="modifier", target="EDGE_SPLIT", needs="object", words="edge split crisp sharp corners hard"),
    dict(id="wireframe_it", section="9. Every other modifier",
         plain="Turn it into its wire skeleton",
         does="The solid becomes just its frame of edges, like a birdcage or a wire model. Great for cages, grilles and sci-fi panels.",
         real="Wireframe modifier", key="-", icon="MODIFIER",
         kind="modifier", target="WIREFRAME", needs="object", words="wireframe cage skeleton grille frame edges"),
    dict(id="build_up", section="9. Every other modifier",
         plain="Build it up piece by piece (for animation)",
         does="Faces appear one after another as time passes - press Play in the animation section and watch it grow.",
         real="Build modifier", key="-", icon="MODIFIER",
         kind="modifier", target="BUILD", needs="object", words="build appear grow animation faces time"),
    dict(id="rebuild_blocks", section="9. Every other modifier",
         plain="Rebuild it from fresh, even blocks",
         does="Throws away a messy inside and rebuilds the shape from clean even blocks. The standard rescue for models that came from scans or other programs.",
         real="Remesh modifier", key="-", icon="MODIFIER",
         kind="modifier", target="REMESH", needs="object", words="remesh rebuild clean even blocks scan fix messy"),
    dict(id="spin_shape", section="9. Every other modifier",
         plain="Spin a flat outline into a round thing",
         does="Draw half the outline of a vase, bottle or bowl as a flat shape, and this spins it around into the full round object.",
         real="Screw modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SCREW", needs="object", words="screw spin lathe vase bottle bowl round outline"),
    dict(id="grow_skin", section="9. Every other modifier",
         plain="Grow skin over a skeleton",
         does="Join points into a stick figure or a branching line, and this grows a smooth skin over it - branches, roots, fingers, tubes.",
         real="Skin modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SKIN", needs="object", words="skin branch root tube skeleton grow"),
    dict(id="all_triangles_mod", section="9. Every other modifier",
         plain="Turn every face into a triangle, for good",
         does="Same as the shaping version, but as a standing rule on the whole thing, including parts you add later.",
         real="Triangulate modifier", key="-", icon="MODIFIER",
         kind="modifier", target="TRIANGULATE", needs="object", words="triangulate triangles export games all faces"),
    dict(id="weld_points", section="9. Every other modifier",
         plain="Weld points that almost touch",
         does="Points that nearly sit on top of each other become one point, as a standing rule - seams and splits close up.",
         real="Weld modifier", key="-", icon="MODIFIER",
         kind="modifier", target="WELD", needs="object", words="weld merge points close seam distance"),
    dict(id="squash_shape", section="9. Every other modifier",
         plain="Squash it toward a ball, tube or box",
         does="Pulls the whole shape part-way toward a simple form. Half-squash a box toward a ball and you get a cushion.",
         real="Cast modifier", key="-", icon="MODIFIER",
         kind="modifier", target="CAST", needs="object", words="cast squash sphere ball cylinder box cushion shape"),
    dict(id="soften_a_bit", section="9. Every other modifier",
         plain="Soften bumps a little",
         does="A gentle smoothing over the whole thing that keeps its size and shape. The mildest of the three smoothers here.",
         real="Smooth modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SMOOTH", needs="object", words="smooth soften bumps gentle modifier"),
    dict(id="soften_keep_size", section="9. Every other modifier",
         plain="Soften it but keep its size",
         does="Smooths like the others, then puffs the shape back to the size it was, so it doesn't shrink while it softens.",
         real="Corrective Smooth modifier", key="-", icon="MODIFIER",
         kind="modifier", target="CORRECTIVE_SMOOTH", needs="object", words="corrective smooth keep size shrink soften"),
    dict(id="soften_even", section="9. Every other modifier",
         plain="Smooth it very evenly",
         does="The strongest, most even smoother of the three. It can shrink the shape a little - that's normal for this one.",
         real="Laplacian Smooth modifier", key="-", icon="MODIFIER",
         kind="modifier", target="LAPLACIANSMOOTH", needs="object", words="laplacian smooth even shrink strong"),
    dict(id="bend_twist", section="9. Every other modifier",
         plain="Twist it, bend it, taper it or stretch it",
         does="Four big shape tricks in one: it starts as a twist. Open the Modifier list (wrench tab) and the same entry can bend, taper or stretch instead.",
         real="Simple Deform modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SIMPLE_DEFORM", needs="object", words="simple deform twist bend taper stretch"),
    dict(id="ripples", section="9. Every other modifier",
         plain="Add ripples, like water",
         does="A wave passes through the shape and can move over time - cloth in wind, water surfaces, wobbly signs.",
         real="Wave modifier", key="-", icon="MODIFIER",
         kind="modifier", target="WAVE", needs="object", words="wave ripple water wind move"),
    dict(id="push_with_picture", section="9. Every other modifier",
         plain="Push the surface around with a picture",
         does="The light and dark of a picture pushes the surface out and in - how you get hammered metal, bark, or a face from a height photo. It needs a picture texture set up first.",
         real="Displace modifier", key="-", icon="MODIFIER",
         kind="modifier", target="DISPLACE", needs="object", words="displace picture texture height bumps push surface"),
    dict(id="wrap_onto", section="9. Every other modifier",
         plain="Wrap it tight onto another thing",
         does="Drapes this shape onto the surface of another one, like a sticker pulled tight over a bottle. The other thing is chosen in the Modifier list.",
         real="Shrinkwrap modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SHRINKWRAP", needs="object", words="shrinkwrap wrap drape sticker surface onto"),
    dict(id="bend_along_line", section="9. Every other modifier",
         plain="Bend it along a bendy line",
         does="The shape follows a bendy line you drew (section 7 adds one). Pick the line in the Modifier list and the shape curves along it - roads, hoses, roller-coasters.",
         real="Curve modifier", key="-", icon="MODIFIER",
         kind="modifier", target="CURVE", needs="object", words="curve bend along line path follow road hose"),
    dict(id="fix_hard_shading", section="9. Every other modifier",
         plain="Fix shading on hard, man-made shapes",
         does="Cars, guns, machines: this keeps flat faces flat and edges crisp while curved parts shade smoothly - the standard fix for weird dark smudges on hard models.",
         real="Weighted Normal modifier", key="-", icon="MODIFIER",
         kind="modifier", target="WEIGHTED_NORMAL", needs="object", words="weighted normal shading hard surface crisp smudge fix"),
    dict(id="make_cloth", section="9. Every other modifier",
         plain="Make it behave like cloth",
         does="Flags, curtains, tablecloths: the shape falls, folds and flaps when you press Play. Works best on the grid sheet from section 7, held at one edge.",
         real="Cloth (physics)", key="-", icon="MODIFIER",
         kind="modifier", target="CLOTH", needs="object", words="cloth fabric flag curtain physics fall"),
    dict(id="make_jelly", section="9. Every other modifier",
         plain="Make it soft & wobbly, like jelly",
         does="The shape squashes and bounces like something soft when you press Play and it lands or is hit.",
         real="Soft Body (physics)", key="-", icon="MODIFIER",
         kind="modifier", target="SOFT_BODY", needs="object", words="soft body jelly wobble squash bounce physics"),
    dict(id="make_bounce_wall", section="9. Every other modifier",
         plain="Make physics things bounce off it",
         does="By itself it does nothing you can see - it turns this thing into a solid wall/floor for cloth and other physics things to land on.",
         real="Collision (physics)", key="-", icon="MODIFIER",
         kind="modifier", target="COLLISION", needs="object", words="collision bounce physics wall floor solid"),
    dict(id="add_particles", section="9. Every other modifier",
         plain="Cover it with particles",
         does="Sprouts lots of small copies or hairs from the surface: grass, fur, sparks, dust, rain. What each particle looks like is set in the Particle tab.",
         real="Particle System", key="-", icon="MODIFIER",
         kind="modifier", target="PARTICLE_SYSTEM", needs="object", words="particles hair fur grass sparks rain dust"),

    # -- 10. Sculpt & paint -----------------------------------------------------
    dict(id="start_sculpting", section="10. Sculpt it & paint it",
         plain="Start sculpting (shape it like clay)",
         does="Instead of moving corners one by one, you push and pull the surface with brushes, like clay. Needs a shape picked. Press it again to stop.",
         real="Sculpt Mode", key="Ctrl+Tab", icon="",
         kind="mode", target="SCULPT", needs="object", words="sculpt clay brush push pull smooth draw mode"),
    dict(id="paint_it", section="10. Sculpt it & paint it",
         plain="Paint colour straight onto it",
         does="Paint with the mouse directly on the surface - each point of the shape holds its own colour, like painting a figure by hand.",
         real="Vertex Paint Mode", key="Ctrl+Tab", icon="",
         kind="mode", target="VERTEX_PAINT", needs="object", words="vertex paint colour color brush direct surface"),
    dict(id="paint_picture", section="10. Sculpt it & paint it",
         plain="Paint a picture onto its skin",
         does="Paints onto a picture that is wrapped around the shape - how game characters get their detailed skins. The shape needs a picture set up first.",
         real="Texture Paint Mode", key="Ctrl+Tab", icon="",
         kind="mode", target="TEXTURE_PAINT", needs="object", words="texture paint image skin picture wrap"),

    # -- 11. Animate it ---------------------------------------------------------
    dict(id="remember_pose", section="11. Animate it",
         plain="Remember where it is right now",
         does="This is how all animation works: you remember a thing's place at one moment, move it, remember again at a later moment - and Blender fills in the movement between. One memory is called a keyframe.",
         real="Insert Keyframe (place, turn, size)", key="I", icon="",
         kind="custom", target="keyframe", needs="object", words="keyframe remember animation moment move position record"),
    dict(id="go_to_start", section="11. Animate it",
         plain="Go back to the start",
         does="Jumps the play line back to frame 1, the beginning of the animation.",
         real="Jump to Start", key="Shift+Down", icon="",
         kind="op", target="screen.frame_jump", args={"end": False}, words="start beginning frame jump rewind"),
    dict(id="play_it", section="11. Animate it",
         plain="Play / stop what moves",
         does="Plays the animation so you can watch it. Press again (or the space bar) to stop.",
         real="Play Animation", key="Space", icon="",
         kind="op", target="screen.animation_play", words="play stop animation watch run space"),

    # -- 12. Finish it ----------------------------------------------------------
    dict(id="take_picture", section="12. Finish: picture, save, send it out",
         plain="Take the picture",
         does="Makes the final image, seen through the camera, with real light and shadow. If no place to save was ever chosen, the picture lands in your home folder as blender_bender_picture.png.",
         real="Render Image", key="F12", icon="",
         kind="custom", target="render_picture", words="render picture image photo final camera f12"),
    dict(id="save_work", section="12. Finish: picture, save, send it out",
         plain="Save your work",
         does="Saves everything so you can close Blender and come back. A first save lands in your home folder as blender_bender_my_model.blend.",
         real="Save File", key="Ctrl+S", icon="",
         kind="custom", target="save_work", words="save file keep store blend"),
    dict(id="send_web", section="12. Finish: picture, save, send it out",
         plain="Send it out for web & games (.glb)",
         does="Writes the whole scene as one .glb file in your home folder (blender_bender_model.glb) - the format websites, AR and most game tools accept.",
         real="Export glTF/GLB", key="-", icon="",
         kind="custom", target="export_glb", words="export glb gltf web games ar send out share"),
    dict(id="send_print", section="12. Finish: picture, save, send it out",
         plain="Send it out for 3D printing (.stl)",
         does="Writes the shapes as an .stl file in your home folder (blender_bender_model.stl) - the format 3D printers and printing services take.",
         real="Export STL", key="-", icon="",
         kind="custom", target="export_stl", words="export stl 3d printing printer send out"),
    dict(id="send_obj", section="12. Finish: picture, save, send it out",
         plain="Send it out the classic way (.obj)",
         does="Writes an .obj file in your home folder (blender_bender_model.obj) - the oldest, most widely accepted model format of all.",
         real="Export OBJ", key="-", icon="",
         kind="custom", target="export_obj", words="export obj classic old format send out"),
    dict(id="centre_world", section="12. Finish: picture, save, send it out",
         plain="Put it back in the middle of the world",
         does="Moves the picked thing to position zero - the centre crossroads where new things appear. Handy when something got lost far away.",
         real="Set Location to 0,0,0", key="Alt+G", icon="",
         kind="custom", target="centre_world", needs="object", words="centre center middle world zero lost move back origin"),
    dict(id="make_permanent", section="12. Finish: picture, save, send it out",
         plain="Make its add-on changes permanent",
         does="Bakes every modifier (sections 5 and 9) into the real shape, so what you see is exactly what exports. After this they can't be tweaked as modifiers - Ctrl+Z still undoes it.",
         real="Apply All Modifiers", key="-", icon="",
         kind="custom", target="apply_modifiers", needs="object", words="apply modifiers permanent bake final real"),

    # -- 13. Find your way around ----------------------------------------------
    dict(id="see_everything", section="13. Find your way around",
         plain="See everything at once",
         does="Zooms the big window so every thing in the scene fits in view. The first thing to press when you feel lost.",
         real="Frame All", key="Home", icon="",
         kind="op", target="view3d.view_all", words="view all frame zoom everything lost find"),
    dict(id="look_at_picked", section="13. Find your way around",
         plain="Jump to what I picked",
         does="Centres the view on the thing you picked and zooms in on it.",
         real="Frame Selected", key="Numpad .", icon="",
         kind="op", target="view3d.view_selected", words="view selected frame jump zoom centre picked"),
    dict(id="look_front", section="13. Find your way around",
         plain="Look at it from the front",
         does="Puts your eye square in front of the scene, like looking at a photo of it.",
         real="Front View", key="Numpad 1", icon="",
         kind="op", target="view3d.view_axis", args={"type": "FRONT"}, words="front view look direction"),
    dict(id="look_top", section="13. Find your way around",
         plain="Look at it from above",
         does="Puts your eye directly overhead, like looking down at a map or a floor plan.",
         real="Top View", key="Numpad 7", icon="",
         kind="op", target="view3d.view_axis", args={"type": "TOP"}, words="top view above overhead map plan"),
    dict(id="look_side", section="13. Find your way around",
         plain="Look at it from the side",
         does="Puts your eye square on the right-hand side of the scene.",
         real="Right View", key="Numpad 3", icon="",
         kind="op", target="view3d.view_axis", args={"type": "RIGHT"}, words="side right view look direction"),
    dict(id="look_camera", section="13. Find your way around",
         plain="Look through the camera",
         does="Shows exactly what the camera sees - which is exactly what your picture will be. The framed edge is the edge of the picture.",
         real="Camera View", key="Numpad 0", icon="",
         kind="op", target="view3d.view_camera", words="camera view through picture frame shot"),
]

SECTIONS = []
for _a in ACTIONS:
    if _a["section"] not in SECTIONS:
        SECTIONS.append(_a["section"])

ACTIONS_BY_ID = {a["id"]: a for a in ACTIONS}

_DONE = {
    "op": "Done - {plain}.",
    "tool": "That tool is on now - use it in the big window. Pick another tool any time.",
    "modifier": "Done - {plain}. It sits in the Modifier list (wrench tab) if you want to change or remove it.",
    "mode": "Done - {plain}.",
    "custom": "Done - {plain}.",
}


_STOPWORDS = {"the", "a", "an", "it", "my", "this", "that", "of", "to"}


def _token_matches(token, hay):
    variants = {token}
    if token.endswith("s") and len(token) > 3:
        variants.add(token[:-1])   # edges -> edge, faces -> face
    if token.endswith("ing") and len(token) > 5:
        variants.add(token[:-3])   # cutting -> cut
    return any(v in hay for v in variants)


def search_actions(query):
    """Match a beginner's own words against plain labels, explanations,
    everyday search words, and Blender's real names."""
    q = (query or "").strip().lower()
    if not q:
        return []
    tokens = [t for t in q.split() if t not in _STOPWORDS]
    hits = []
    for a in ACTIONS:
        hay = " ".join([a["plain"], a["does"], a["real"], a.get("words", "")]).lower()
        if q in hay or (tokens and all(_token_matches(t, hay) for t in tokens)):
            hits.append(a)
    return hits


# ----------------------------------------------------------------------------
# Custom actions (things Blender spreads across several steps, done in one)
# ----------------------------------------------------------------------------

def _custom_duplicate(context):
    return bpy.ops.object.duplicate()


def _custom_delete_object(context):
    if context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    return bpy.ops.object.delete()


def _custom_colour(context):
    obj = context.object
    if obj is None or obj.type not in {"MESH", "CURVE", "FONT"}:
        raise RuntimeError("Pick a shape first - colour needs something to land on.")
    mat = bpy.data.materials.get("Bender Red")
    if mat is None:
        mat = bpy.data.materials.new("Bender Red")
        mat.diffuse_color = (0.8, 0.12, 0.08, 1.0)
        mat.use_nodes = True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf:
            bsdf.inputs["Base Color"].default_value = (0.8, 0.12, 0.08, 1.0)
    if obj.data and hasattr(obj.data, "materials"):
        if obj.data.materials:
            obj.data.materials[0] = mat
        else:
            obj.data.materials.append(mat)
    return {"FINISHED"}


def _custom_apply_transforms(context):
    return bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)


def _custom_origin_middle(context):
    return bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY", center="MEDIAN")


def _custom_boolean_cut(context):
    picked = list(context.selected_objects)
    cutter = context.object  # the thing picked LAST does the cutting
    if len(picked) < 2 or cutter is None or cutter not in picked:
        raise RuntimeError(
            "Pick two things: the thing to cut into first, then the cutter last.")
    target = next(o for o in picked if o is not cutter)
    if target.type != "MESH" or cutter.type != "MESH":
        raise RuntimeError("Cutting works on solid shapes - pick two shapes.")
    context.view_layer.objects.active = target
    for o in picked:
        o.select_set(o is target)
    mod = target.modifiers.new(name="Bender Cut", type="BOOLEAN")
    mod.operation = "DIFFERENCE"
    if hasattr(mod, "solver"):
        mod.solver = "EXACT"
    mod.object = cutter
    try:
        bpy.ops.object.modifier_apply(modifier=mod.name)
    except Exception:
        pass  # the live modifier still cuts; it just stays editable
    cutter.hide_set(True)
    cutter.hide_render = True
    cutter.select_set(False)
    target.select_set(True)
    context.view_layer.objects.active = target
    return {"FINISHED"}


def _custom_separate_piece(context):
    return bpy.ops.mesh.separate(type="SELECTED")


def _custom_keyframe(context):
    obj = context.object
    frame = context.scene.frame_current
    for path in ("location", "rotation_euler", "scale"):
        obj.keyframe_insert(data_path=path, frame=frame)
    return {"FINISHED"}


def _home(filename):
    return os.path.join(os.path.expanduser("~"), filename)


def _custom_render_picture(context):
    scene = context.scene
    # A first picture must just work: if the scene has no camera or no
    # light yet (the two classic day-1 dead ends), add them - from a
    # sensible spot - instead of failing.
    if scene.camera is None:
        bpy.ops.object.camera_add(location=(6.0, -7.0, 5.0),
                                  rotation=(1.05, 0.0, 0.72))
        scene.camera = context.object
    if not any(o.type == "LIGHT" for o in scene.objects):
        bpy.ops.object.light_add(type="SUN", location=(4.0, -4.0, 8.0))
    path = (scene.render.filepath or "").strip()
    if path in {"", "/tmp", "/tmp/"}:
        scene.render.filepath = _home("blender_bender_picture.png")
    return bpy.ops.render.render(write_still=True)


def _custom_save_work(context):
    if bpy.data.filepath:
        return bpy.ops.wm.save_mainfile()
    return bpy.ops.wm.save_as_mainfile(filepath=_home("blender_bender_my_model.blend"))


def _custom_export_glb(context):
    return bpy.ops.export_scene.gltf(
        filepath=_home("blender_bender_model.glb"), export_format="GLB")


def _custom_export_stl(context):
    if hasattr(bpy.ops.wm, "stl_export"):
        return bpy.ops.wm.stl_export(filepath=_home("blender_bender_model.stl"))
    return bpy.ops.export_mesh.stl(filepath=_home("blender_bender_model.stl"))


def _custom_export_obj(context):
    return bpy.ops.wm.obj_export(filepath=_home("blender_bender_model.obj"))


def _custom_centre_world(context):
    context.object.location = (0.0, 0.0, 0.0)
    return {"FINISHED"}


def _custom_apply_modifiers(context):
    obj = context.object
    if context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for mod in list(obj.modifiers):
        try:
            bpy.ops.object.modifier_apply(modifier=mod.name)
        except Exception:
            pass  # a modifier missing its partner object stays; the rest apply
    return {"FINISHED"}


_CUSTOM = {
    "duplicate": _custom_duplicate,
    "delete_object": _custom_delete_object,
    "colour": _custom_colour,
    "apply_transforms": _custom_apply_transforms,
    "origin_middle": _custom_origin_middle,
    "boolean_cut": _custom_boolean_cut,
    "separate_piece": _custom_separate_piece,
    "keyframe": _custom_keyframe,
    "render_picture": _custom_render_picture,
    "save_work": _custom_save_work,
    "export_glb": _custom_export_glb,
    "export_stl": _custom_export_stl,
    "export_obj": _custom_export_obj,
    "centre_world": _custom_centre_world,
    "apply_modifiers": _custom_apply_modifiers,
}

_MOD_DEFAULTS = {
    "SUBSURF": {"levels": 2, "render_levels": 2},
    "BEVEL": {"width": 0.03, "segments": 3},
    "SOLIDIFY": {"thickness": 0.04},
    "ARRAY": {"count": 3, "relative_offset_displace": (1.15, 0.0, 0.0)},
    "DECIMATE": {"ratio": 0.5},
    "REMESH": {"mode": "SMOOTH"},
    "SIMPLE_DEFORM": {"deform_method": "TWIST", "angle": 0.6},
    "WIREFRAME": {"thickness": 0.03},
}


_CONTEXT_MODE = {
    "EDIT": "EDIT_MESH",
    "SCULPT": "SCULPT",
    "VERTEX_PAINT": "PAINT_VERTEX",
    "WEIGHT_PAINT": "PAINT_WEIGHT",
    "TEXTURE_PAINT": "PAINT_TEXTURE",
}


def _resolve_op(path):
    node = bpy.ops
    for part in path.split("."):
        node = getattr(node, part)
    return node


# ----------------------------------------------------------------------------
# The complete index: EVERY operator this Blender exposes, with Blender's
# own name and one-line description. This is the guarantee that the plain
# words layer loses nothing - the curated buttons above are the everyday
# set, and the whole of the rest of Blender is searchable right below them.
# (Blender 4.2.5 exposes ~2,400 operators; the index is built once, live,
# from the running Blender, so it can never drift out of date.)
# ----------------------------------------------------------------------------

_INDEX = None


def build_index():
    global _INDEX
    if _INDEX is not None:
        return _INDEX
    entries = []
    for cat in dir(bpy.ops):
        if cat.startswith("_"):
            continue
        try:
            module = getattr(bpy.ops, cat)
            names = dir(module)
        except Exception:
            continue
        for name in names:
            if name.startswith("_"):
                continue
            try:
                rna = getattr(module, name).get_rna_type()
            except Exception:
                continue
            if rna is None:
                continue
            entries.append({
                "idname": f"{cat}.{name}",
                "cat": cat,
                "label": rna.name or name,
                "desc": rna.description or "",
            })
    _INDEX = entries
    return _INDEX


def search_index(query, limit=15):
    q = (query or "").strip().lower()
    if not q:
        return []
    tokens = [t for t in q.split() if t not in _STOPWORDS]
    scored = []
    for e in build_index():
        hay = f"{e['label']} {e['idname']} {e['desc']}".lower()
        if q in hay or (tokens and all(_token_matches(t, hay) for t in tokens)):
            label = e["label"].lower()
            if label == q or label.startswith(q):
                score = 0
            elif q in label:
                score = 1
            elif q in e["idname"]:
                score = 2
            else:
                score = 3
            scored.append((score, e["label"], e))
    scored.sort(key=lambda item: (item[0], item[1]))
    return [e for _s, _l, e in scored[:limit]]


# ----------------------------------------------------------------------------
# The one operator behind every button
# ----------------------------------------------------------------------------

class BENDER_OT_action(Operator):
    bl_idname = "bender.action"
    bl_label = "Blender Bender Action"
    bl_description = ("Run this tool. The panel beside the button explains, "
                      "in plain words, what it does before you press it")
    bl_options = {"REGISTER", "UNDO"}

    action_id: StringProperty(options={"HIDDEN"})

    def execute(self, context):
        act = ACTIONS_BY_ID.get(self.action_id)
        if act is None:
            return {"CANCELLED"}

        needs = act.get("needs")
        if needs in {"object", "edit", "two"} and context.object is None:
            self.report({"ERROR"}, "Nothing is picked yet. Click a thing in the "
                                   "big window first - or add a box in section 1.")
            return {"CANCELLED"}

        # A shaping button pressed too early: do the first step FOR the
        # beginner, explain it, and let the same button finish the job.
        if needs == "edit" and context.mode != "EDIT_MESH":
            try:
                bpy.ops.object.mode_set(mode="EDIT")
                if context.object and context.object.type == "MESH":
                    bpy.ops.mesh.select_all(action="SELECT")
            except Exception as exc:
                self.report({"WARNING"}, f"Could not start shaping: {exc}")
                return {"CANCELLED"}
            self.report({"INFO"}, "You are shaping it now, and every part of it "
                                  "is picked. Press the same button again to do it.")
            return {"FINISHED"}

        try:
            kind = act["kind"]
            if kind == "op":
                result = _resolve_op(act["target"])(**act.get("args", {}))
            elif kind == "tool":
                result = bpy.ops.wm.tool_set_by_id(name=act["target"])
            elif kind == "mode":
                mode = act["target"]
                mapped = _CONTEXT_MODE.get(mode, mode)
                if context.mode == mapped:
                    mode = "OBJECT"
                result = bpy.ops.object.mode_set(mode=mode)
            elif kind == "modifier":
                result = bpy.ops.object.modifier_add(type=act["target"])
                mod = context.object.modifiers[-1] if context.object.modifiers else None
                if mod is not None:
                    for prop, value in _MOD_DEFAULTS.get(act["target"], {}).items():
                        if hasattr(mod, prop):
                            setattr(mod, prop, value)
            elif kind == "custom":
                result = _CUSTOM[act["target"]](context)
            else:
                result = {"CANCELLED"}
        except Exception as exc:
            self.report({"WARNING"}, f"That didn't work here: {exc}  "
                                     "Check the sentence under the button - it "
                                     "says what has to be picked first.")
            return {"CANCELLED"}

        if result and "CANCELLED" in result:
            self.report({"WARNING"}, "Blender said no to that one here. The "
                                     "sentence under the button says what it needs.")
            return {"CANCELLED"}
        self.report({"INFO"}, _DONE[act["kind"]].format(plain=act["plain"]))
        return {"FINISHED"}


class BENDER_OT_run_any(Operator):
    bl_idname = "bender.run_any"
    bl_label = "Run Blender Tool"
    bl_description = ("Run this Blender tool directly. These keep Blender's "
                      "own names - the plain-words buttons above are the "
                      "same idea, translated")
    bl_options = {"REGISTER", "UNDO"}

    op_id: StringProperty(options={"HIDDEN"})

    def execute(self, context):
        valid = {e["idname"] for e in build_index()}
        if self.op_id not in valid:
            return {"CANCELLED"}
        try:
            result = _resolve_op(self.op_id)()
        except Exception as exc:
            self.report({"WARNING"}, f"That one didn't run here: {exc}")
            return {"CANCELLED"}
        if result and "CANCELLED" in result:
            self.report({"WARNING"}, "That one didn't run here - most of these "
                                     "need the right thing picked, the right "
                                     "window open, or a setting filled in first. "
                                     "Nothing was changed.")
            return {"CANCELLED"}
        self.report({"INFO"}, f"Ran Blender's own tool: {self.op_id}")
        return {"FINISHED"}


# ----------------------------------------------------------------------------
# The panel
# ----------------------------------------------------------------------------

def _wrap(layout, text, width=44):
    for line in textwrap.wrap(text, width=width) or [""]:
        layout.label(text=line)


def _draw_action(layout, act, show_real):
    row = layout.row(align=True)
    if act.get("icon"):
        op = row.operator("bender.action", text=act["plain"], icon=act["icon"])
    else:
        op = row.operator("bender.action", text=act["plain"])
    op.action_id = act["id"]
    col = layout.column()
    col.scale_y = 0.8
    _wrap(col, act["does"])
    if show_real:
        _wrap(col, f"Blender calls this: {act['real']}   Key: {act['key']}", width=52)
    layout.separator(factor=0.6)


def _hint(context):
    obj = context.object
    if obj is None:
        return ("You have not picked anything yet. Either click a thing in the "
                "big window, or add a box in section 1 below - a box is the "
                "easiest first thing to practise on.")
    if context.mode == "EDIT_MESH":
        return (f"You are SHAPING '{obj.name}' - changing its corners, edges "
                "and faces. Section 3 is your main toolbox right now. 'Start "
                "shaping it' (section 3) takes you back to moving whole things.")
    return (f"You have picked '{obj.name}'. Move it or size it in section 2, "
            "copy or combine it in section 4, or press 'Start shaping it' in "
            "section 3 to change its actual shape.")


class VIEW3D_PT_blender_bender(Panel):
    bl_idname = "VIEW3D_PT_blender_bender"
    bl_label = "Blender Bender - in plain words"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender Bender"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        show_real = getattr(wm, "bender_show_real", True)

        box = layout.box()
        box.label(text="Where you are", icon="INFO")
        _wrap(box, _hint(context))

        box = layout.box()
        box.label(text="What do you want to do?", icon="VIEWZOOM")
        box.prop(wm, "bender_query", text="")
        query = getattr(wm, "bender_query", "")
        if query.strip():
            hits = search_actions(query)
            if hits:
                for act in hits[:10]:
                    _draw_action(box, act, show_real)
            else:
                _wrap(box, "No match. Try everyday words: round, copy, hole, "
                           "smooth, move, thicker, colour, delete.")
        box.prop(wm, "bender_show_real",
                 text="Also show Blender's real names (learn them as you go)")

        for section in SECTIONS:
            box = layout.box()
            box.label(text=section)
            for act in ACTIONS:
                if act["section"] == section:
                    _draw_action(box, act, show_real)

        # The complete index: everything else Blender can do, searchable.
        box = layout.box()
        box.label(text="Everything else Blender can do", icon="QUESTION")
        index = build_index()
        _wrap(box, f"The plain-words buttons above are the everyday set. "
                   f"Blender has {len(index)} tools in total in this "
                   f"version - and every single one of them is reachable "
                   f"from here, so nothing is lost. Type any part of a "
                   f"name or job in the search box at the top and matches "
                   f"appear below, with Blender's own one-line explanation.")
        if query.strip():
            hits = search_index(query)
            if hits:
                for e in hits:
                    row = box.row(align=True)
                    op = row.operator("bender.run_any",
                                      text=e["label"] or e["idname"])
                    op.op_id = e["idname"]
                    col = box.column()
                    col.scale_y = 0.8
                    if e["desc"]:
                        _wrap(col, e["desc"])
                    _wrap(col, f"Blender's name for it: {e['idname']}", width=52)
                    box.separator(factor=0.6)
            else:
                _wrap(box, "No tool in the whole of Blender matches that. "
                           "Try fewer or different words.")
        else:
            _wrap(box, "These keep Blender's own names - they're the long "
                       "tail, there are thousands, and most people need "
                       "only a few. If you find yourself using one a lot, "
                       "it deserves a plain-words button above.")


CLASSES = (BENDER_OT_action, BENDER_OT_run_any, VIEW3D_PT_blender_bender)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.bender_query = StringProperty(
        name="What do you want to do?",
        description="Type it in your own words - 'round the edges', "
                    "'make a copy', 'cut a hole' - and the matching "
                    "tools appear here",
        default="",
    )
    bpy.types.WindowManager.bender_show_real = BoolProperty(
        name="Show real names",
        description="Show Blender's own name and shortcut under each "
                    "plain-words button, so you learn them as you go",
        default=True,
    )


def unregister():
    for attr in ("bender_query", "bender_show_real"):
        if hasattr(bpy.types.WindowManager, attr):
            delattr(bpy.types.WindowManager, attr)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
