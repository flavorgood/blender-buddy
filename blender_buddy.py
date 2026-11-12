"""
Blender Buddy - Blender in plain words (prototype 0.7)

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

import json
import math
import os
import random
import re
import shutil
import subprocess
import tempfile
import textwrap
import urllib.error
import urllib.request
from difflib import SequenceMatcher

import bpy
from bpy.props import (BoolProperty, EnumProperty, IntProperty,
                       StringProperty)
from bpy.types import AddonPreferences, Operator, Panel

bl_info = {
    "name": "Blender Buddy - Blender in Plain Words",
    "author": "Blender Buddy prototype",
    "version": (0, 7, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar (N key) > Blender Buddy tab",
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
         kind="custom", target="boolean_cut", needs="two", words="boolean hole cut out remove drill doorway slot subtract make a hole punch"),

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
         does="Makes the final image, seen through the camera, with real light and shadow. If no place to save was ever chosen, the picture lands in your home folder as blender_buddy_picture.png.",
         real="Render Image", key="F12", icon="",
         kind="custom", target="render_picture", words="render picture image photo final camera f12"),
    dict(id="save_work", section="12. Finish: picture, save, send it out",
         plain="Save your work",
         does="Saves everything so you can close Blender and come back. A first save lands in your home folder as blender_buddy_my_model.blend.",
         real="Save File", key="Ctrl+S", icon="",
         kind="custom", target="save_work", words="save file keep store blend"),
    dict(id="send_web", section="12. Finish: picture, save, send it out",
         plain="Send it out for web & games (.glb)",
         does="Writes the whole scene as one .glb file in your home folder (blender_buddy_model.glb) - the format websites, AR and most game tools accept.",
         real="Export glTF/GLB", key="-", icon="",
         kind="custom", target="export_glb", words="export glb gltf web games ar send out share"),
    dict(id="send_print", section="12. Finish: picture, save, send it out",
         plain="Send it out for 3D printing (.stl)",
         does="Writes the shapes as an .stl file in your home folder (blender_buddy_model.stl) - the format 3D printers and printing services take.",
         real="Export STL", key="-", icon="",
         kind="custom", target="export_stl", words="export stl 3d printing printer send out"),
    dict(id="send_obj", section="12. Finish: picture, save, send it out",
         plain="Send it out the classic way (.obj)",
         does="Writes an .obj file in your home folder (blender_buddy_model.obj) - the oldest, most widely accepted model format of all.",
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


_STOPWORDS = {"the", "a", "an", "it", "my", "this", "that", "of", "to",
              "me", "i", "want", "how", "do", "can", "please", "something",
              "not", "no", "on", "in", "is", "are", "was", "with", "for"}

# Loose words people actually type, mapped to the words the catalogue
# uses. A beginner describes the job their way; search meets them there.
_SYNONYMS = {
    "color": ["colour"], "colors": ["colour"], "gray": ["grey"],
    "center": ["centre", "middle"], "squish": ["scale", "squash"],
    "squash": ["scale", "cast"], "spin": ["rotate", "turn"],
    "spinning": ["rotate", "turn"], "twirl": ["rotate", "turn"],
    "glow": ["light"], "glowing": ["light"], "shine": ["light", "smooth"],
    "shiny": ["smooth", "material", "light"], "bright": ["light", "sun"],
    "dark": ["light", "shading"], "rough": ["displace", "bumps"],
    "bumpy": ["displace", "bumps", "smooth"], "lumpy": ["smooth", "bumps"],
    "clone": ["duplicate", "copy"], "glue": ["join", "weld"],
    "stick": ["join", "glue"], "drill": ["cut", "hole"],
    "stairs": ["array", "steps"], "steps": ["array"],
    "fence": ["array"], "hair": ["particles"], "fur": ["particles"],
    "grass": ["particles"], "sparks": ["particles"], "rain": ["particles"],
    "photo": ["render", "camera", "picture"], "snapshot": ["render", "picture"],
    "movie": ["animation", "play"], "film": ["animation", "play"],
    "video": ["animation", "play"], "softer": ["smooth", "soften"],
    "harder": ["crisp", "flat"], "sharpen": ["crisp", "edge"],
    "pointy": ["cone", "spike"], "donut": ["ring", "torus"],
    "doughnut": ["ring", "torus"], "ball": ["sphere"],
    "box": ["cube"], "tube": ["cylinder", "pipe"], "pipe": ["cylinder", "tube"],
    "jelly": ["soft", "body"], "bounce": ["collision", "soft"],
    "flag": ["cloth"], "curtain": ["cloth"], "fabric": ["cloth"],
    "wrinkle": ["cloth", "displace"], "tile": ["grid", "array"],
    "tiles": ["grid", "array"], "floor": ["plane", "grid", "sheet"],
    "wall": ["plane", "sheet", "collision"], "ground": ["plane", "sheet"],
    "erase": ["delete", "dissolve"], "remove": ["delete"],
    "trash": ["delete"], "bigger": ["scale", "grow"],
    "smaller": ["scale", "shrink"], "stretch": ["scale"],
    "bend": ["curve", "deform", "twist"], "bent": ["curve", "deform"],
    "twist": ["deform", "rotate"], "wave": ["ripple"],
    "water": ["wave", "ripple"], "wind": ["wave", "cloth"],
    "paint": ["colour"], "draw": ["knife", "curve", "line"],
    "write": ["text", "words"], "letters": ["text", "words"],
    "sign": ["text", "words"], "hollow": ["solidify", "shell", "thickness"],
    "thick": ["solidify", "thickness"], "thin": ["solidify", "scale"],
}


def _words_of(text):
    return re.findall(r"[a-z0-9]+", (text or "").lower())


def _expand(token):
    """All the forms one typed word might mean: itself, singular/plural,
    spelling variants, and its loose-word synonyms."""
    out = {token}
    if token.endswith("s") and len(token) > 3:
        out.add(token[:-1])        # edges -> edge
    if token.endswith("ing") and len(token) > 5:
        out.add(token[:-3])        # cutting -> cut
        out.add(token[:-3] + "e")  # shaping -> shape
    if token.endswith("ed") and len(token) > 4:
        out.add(token[:-2])        # picked -> pick
    for loose, targets in _SYNONYMS.items():
        if token == loose:
            out.update(targets)
        elif loose in targets and token in targets:
            out.add(loose)
    return out


def _fuzzy_ratio(a, b):
    return SequenceMatcher(None, a, b).ratio()


def _token_best(token, hay_words):
    """Score one typed word against a set of catalogue words:
    3 = the word (or its meaning) is right there, 2 = a half-word or a
    clear typo of it, 1 = a near miss, 0 = nothing alike."""
    best = 0
    for cand in _expand(token):
        if cand in hay_words:
            return 3
        if len(cand) >= 3:
            for hw in hay_words:
                if len(hw) >= 3 and (hw.startswith(cand) or cand.startswith(hw)):
                    best = max(best, 2)
                    break
    if best < 2 and len(token) >= 4:
        for hw in hay_words:
            if len(hw) >= 4 and _fuzzy_ratio(token, hw) >= 0.82:
                return 2           # clear typo: bevell -> bevel
            if len(hw) >= 4 and _fuzzy_ratio(token, hw) >= 0.72:
                best = max(best, 1)
    return best


def _query_tokens(query):
    q = (query or "").strip().lower()
    tokens = [t for t in _words_of(q)
              if t not in _STOPWORDS and len(t) >= 3]
    return q, tokens


def search_actions(query):
    """Loose search over the plain-words buttons. People describe the job
    their own way - synonyms, half-words, typos and all - and get ranked
    best matches instead of an all-or-nothing gate. Gibberish still
    returns nothing."""
    q, tokens = _query_tokens(query)
    if not tokens:
        return []
    scored = []
    for pos, a in enumerate(ACTIONS):
        hay_text = " ".join([a["plain"], a["does"], a["real"],
                             a.get("words", "")]).lower()
        hay_words = set(_words_of(hay_text))
        score = sum(_token_best(t, hay_words) for t in tokens)
        if q and q in hay_text:
            score += 6
        if score >= 2:
            scored.append((-score, pos, a))
    scored.sort()
    return [a for _s, _p, a in scored]


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
    mat = bpy.data.materials.get("Buddy Red")
    if mat is None:
        mat = bpy.data.materials.new("Buddy Red")
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
    mod = target.modifiers.new(name="Buddy Cut", type="BOOLEAN")
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
        scene.render.filepath = _home("blender_buddy_picture.png")
    return bpy.ops.render.render(write_still=True)


def _custom_save_work(context):
    if bpy.data.filepath:
        return bpy.ops.wm.save_mainfile()
    return bpy.ops.wm.save_as_mainfile(filepath=_home("blender_buddy_my_model.blend"))


def _custom_export_glb(context):
    return bpy.ops.export_scene.gltf(
        filepath=_home("blender_buddy_model.glb"), export_format="GLB")


def _custom_export_stl(context):
    if hasattr(bpy.ops.wm, "stl_export"):
        return bpy.ops.wm.stl_export(filepath=_home("blender_buddy_model.stl"))
    return bpy.ops.export_mesh.stl(filepath=_home("blender_buddy_model.stl"))


def _custom_export_obj(context):
    return bpy.ops.wm.obj_export(filepath=_home("blender_buddy_model.obj"))


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
            label = rna.name or name
            desc = rna.description or ""
            head_words = set(_words_of(label)) | set(
                _words_of(f"{cat} {name}"))
            entries.append({
                "idname": f"{cat}.{name}",
                "cat": cat,
                "label": label,
                "desc": desc,
                "head_words": head_words,
                "hay_words": head_words | set(_words_of(desc)),
            })
    _INDEX = entries
    return _INDEX


def search_index(query, limit=15):
    """Loose search over ALL of Blender's tools, same engine as the
    plain-words search: synonyms, half-words and typos all count, best
    matches first. A word in a tool's name counts most, a word in its
    explanation counts too."""
    q, tokens = _query_tokens(query)
    if not tokens:
        return []
    scored = []
    for pos, e in enumerate(build_index()):
        score = 0
        id_parts = e["idname"].replace(".", "_").split("_")
        for t in tokens:
            head = _token_best(t, e["head_words"])
            body = _token_best(t, e["hay_words"])
            score += head * 2 + body
            if e["label"].lower() == t:
                score += 4   # the tool whose whole name is this word
            if t in id_parts:
                score += 2   # the word is a piece of the tool's own name
        if q and q in e["label"].lower():
            score += 6
        if score >= 3:
            scored.append((-score, pos, e))
    scored.sort(key=lambda item: (item[0], item[1]))
    return [e for _s, _p, e in scored[:limit]]


# ----------------------------------------------------------------------------
# Day 1: the Donut Tour. The donut is the famous first Blender project -
# the Blender Guru's tutorial made it the rite of passage. This is the
# same donut in plain words: 8 steps, one press each, and a step only
# ticks off when the SCENE proves it happened (the object, the colour,
# the camera are really there) - never just because a button was pressed.
# ----------------------------------------------------------------------------

def _scene_obj(context, name):
    return context.scene.objects.get(name)


def _dough(context):
    skip = {"Icing", "Sprinkles", "Plate"}
    cands = [o for o in context.scene.objects
             if o.type == "MESH" and o.name not in skip
             and len(o.data.vertices) >= 300]
    if not cands:
        return None
    cands.sort(key=lambda o: len(o.data.vertices), reverse=True)
    return cands[0]


def _first_colour(obj):
    if obj is None or not obj.data.materials:
        return None
    mat = obj.data.materials[0]
    return mat.diffuse_color if mat else None


def _principled(mat, rgba, roughness, subsurface=0.0):
    """Set a material up the way the tutorial does: a real Principled
    material with a base colour, a roughness, and a touch of
    subsurface glow for food."""
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = roughness
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = subsurface


def _paint(obj, mat_name, rgba, roughness=0.55, subsurface=0.0):
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)
    _principled(mat, rgba, roughness, subsurface)
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def _tour_step_dough(context):
    # The famous tutorial's first move: get rid of the starter cube.
    # Only when the scene is EXACTLY Blender's untouched starter set
    # (Cube, Camera, Light and nothing else) - a lived-in scene is
    # never touched.
    objs = list(context.scene.objects)
    if {o.name for o in objs} <= {"Cube", "Camera", "Light"}:
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
    # His dough is PLUMP: a fat tube, squashed a little, smoothed and
    # subdivided - not the thin default ring.
    bpy.ops.mesh.primitive_torus_add(
        major_radius=1.0, minor_radius=0.42,
        major_segments=64, minor_segments=24)
    obj = context.object
    obj.name = "Dough"
    obj.scale = (1.0, 1.0, 0.82)
    for poly in obj.data.polygons:
        poly.use_smooth = True
    mod = obj.modifiers.new("Smoother", "SUBSURF")
    mod.levels = 2


def _tour_step_icing(context):
    import bmesh
    dough = _dough(context)
    if dough is None:
        raise RuntimeError("The dough ring is not there yet - do step 1 first.")
    # The tutorial's real method: the icing is the TOP of the dough
    # itself, separated off and given thickness - never a second ring.
    icing = dough.copy()
    icing.data = dough.data.copy()
    context.scene.collection.objects.link(icing)
    icing.name = "Icing"
    icing.data.name = "Icing"
    bm = bmesh.new()
    bm.from_mesh(icing.data)
    bm.faces.ensure_lookup_table()
    under = [f for f in bm.faces if f.calc_center_median().z < -0.02]
    bmesh.ops.delete(bm, geom=under, context="FACES")
    # Drips: the rim verts are pulled down the dough's side by an
    # uneven amount - long drips in places, short in others - the
    # wavy edge that makes it read as icing and not a shell.
    rng = random.Random(4)
    p1, p2, p3 = (rng.uniform(0, 6.28), rng.uniform(0, 6.28),
                  rng.uniform(0, 6.28))
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        if abs(v.co.z) < 0.09:
            a = math.atan2(v.co.y, v.co.x)
            wave = (math.sin(a * 3 + p1) * 0.5
                    + math.sin(a * 7 + p2) * 0.3
                    + math.sin(a * 13 + p3) * 0.2)
            drip = (max(0.0, wave) ** 1.5) * 0.34
            v.co.z -= drip
    bm.to_mesh(icing.data)
    bm.free()
    for poly in icing.data.polygons:
        poly.use_smooth = True
    # Stack order matters (learned from a bad render): thickness
    # FIRST, smoothing second - and a breath of outward lift - so the
    # icing sits ON the dough. Smoothing an open shell first shrinks
    # it under the dough's surface and the dough swallows it.
    for mod in list(icing.modifiers):
        icing.modifiers.remove(mod)
    thick = icing.modifiers.new("Icing Thickness", "SOLIDIFY")
    thick.thickness = 0.05
    sub = icing.modifiers.new("Smoother", "SUBSURF")
    sub.levels = 2
    icing.scale = (1.015, 1.015, 0.835)
    bpy.ops.object.select_all(action="DESELECT")
    icing.select_set(True)
    context.view_layer.objects.active = icing


def _tour_step_icing_pink(context):
    icing = _scene_obj(context, "Icing")
    if icing is None:
        raise RuntimeError("There is no icing yet - do the icing step first.")
    # Glossy, like his: low roughness, a whisper of subsurface.
    _paint(icing, "Buddy Pink", (0.80, 0.30, 0.47, 1.0),
           roughness=0.18, subsurface=0.05)


def _tour_step_dough_colour(context):
    dough = _dough(context)
    if dough is None:
        raise RuntimeError("The dough ring is not there yet - do step 1 first.")
    # Golden baked dough WITH the pale fry line around its middle -
    # the band where the donut floated in the oil. Faces around the
    # outside equator get the paler material.
    golden = bpy.data.materials.get("Buddy Dough") or \
        bpy.data.materials.new("Buddy Dough")
    _principled(golden, (0.52, 0.28, 0.09, 1.0),
                roughness=0.5, subsurface=0.3)
    pale = bpy.data.materials.get("Buddy Fry Line") or \
        bpy.data.materials.new("Buddy Fry Line")
    _principled(pale, (0.78, 0.55, 0.28, 1.0),
                roughness=0.55, subsurface=0.3)
    dough.data.materials.clear()
    dough.data.materials.append(golden)
    dough.data.materials.append(pale)
    for poly in dough.data.polygons:
        c = poly.center
        radial = math.hypot(c.x, c.y)
        if radial > 1.0 and abs(c.z) < 0.055:
            poly.material_index = 1


_SPRINKLE_COLOURS = [
    (0.35, 0.75, 0.70, 1.0),   # teal
    (0.62, 0.52, 0.85, 1.0),   # lavender
    (0.95, 0.90, 0.70, 1.0),   # cream
    (0.95, 0.62, 0.72, 1.0),   # pale pink
    (0.96, 0.96, 0.96, 1.0),   # white
    (0.55, 0.75, 0.95, 1.0),   # sky
]


def _tour_step_sprinkles(context):
    from mathutils import Matrix, Quaternion
    icing = _scene_obj(context, "Icing")
    if icing is None:
        raise RuntimeError("Sprinkles need the icing first - it is step 5.")
    rng = random.Random(11)
    mats = []
    for i, rgba in enumerate(_SPRINKLE_COLOURS):
        name = f"Sprinkle Colour {i + 1}"
        mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
        _principled(mat, rgba, roughness=0.35)
        mats.append(mat)
    if context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    # One long thin sprinkle shape, reused for every instance.
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8,
                                         radius=1.0)
    template = context.object
    template.data.transform(
        Matrix.Diagonal((0.083, 0.016, 0.016, 1.0)))
    template_mesh = template.data
    # Sample the icing's REAL surface (evaluated, drips and all) and
    # lay each sprinkle flat on it, spun a random way - the way his
    # sprinkles actually sit.
    dg = context.evaluated_depsgraph_get()
    eval_obj = icing.evaluated_get(dg)
    eval_mesh = eval_obj.to_mesh()
    mw = icing.matrix_world
    faces = []
    for poly in eval_mesh.polygons:
        cw = mw @ poly.center
        nw = (mw.to_3x3() @ poly.normal).normalized()
        if cw.z > 0.08 and nw.z > 0.2:
            faces.append((cw, nw))
    eval_obj.to_mesh_clear()
    if not faces:
        raise RuntimeError("Could not find the top of the icing.")
    made = []
    count = 130
    for i in range(count):
        cw, nw = faces[rng.randrange(len(faces))]
        spin = Quaternion(nw, rng.uniform(0, 2 * math.pi))
        align = nw.to_track_quat("Z", "Y")
        mat4 = (Matrix.Translation(cw + nw * 0.012)
                @ (spin @ align).to_matrix().to_4x4())
        mesh = template_mesh.copy()
        mesh.transform(mat4)
        mesh.materials.append(mats[i % len(mats)])
        obj = bpy.data.objects.new("Sprinkle", mesh)
        context.scene.collection.objects.link(obj)
        made.append(obj)
    # A few that fell on the plate, like his final shot.
    for i in range(6):
        a = rng.uniform(0, 2 * math.pi)
        r = rng.uniform(1.2, 1.45)
        pos = (r * math.cos(a), r * math.sin(a), -0.335)
        yaw = Quaternion((0, 0, 1), rng.uniform(0, 2 * math.pi))
        mesh = template_mesh.copy()
        mesh.transform(Matrix.Translation(pos)
                       @ yaw.to_matrix().to_4x4())
        mesh.materials.append(mats[(count + i) % len(mats)])
        obj = bpy.data.objects.new("Sprinkle", mesh)
        context.scene.collection.objects.link(obj)
        made.append(obj)
    bpy.data.objects.remove(template, do_unlink=True)
    bpy.ops.object.select_all(action="DESELECT")
    for s in made:
        s.select_set(True)
    context.view_layer.objects.active = made[0]
    bpy.ops.object.join()
    context.object.name = "Sprinkles"


def _tour_step_plate(context):
    # His final shot, staged: white plate, dark table, mug of coffee.
    bpy.ops.mesh.primitive_cylinder_add(
        radius=1.55, depth=0.06, location=(0, 0, -0.38))
    plate = context.object
    plate.name = "Plate"
    _paint(plate, "Buddy Plate", (0.93, 0.93, 0.95, 1.0), roughness=0.35)
    bpy.ops.mesh.primitive_circle_add(
        vertices=48, radius=7.0, fill_type="NGON", location=(0, 0, -0.415))
    table = context.object
    table.name = "Table"
    _paint(table, "Buddy Table", (0.16, 0.14, 0.13, 1.0), roughness=0.9)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.34, depth=0.5, location=(1.95, 0.6, -0.165))
    mug = context.object
    mug.name = "Mug"
    _paint(mug, "Buddy Mug", (0.36, 0.21, 0.13, 1.0), roughness=0.4)
    bpy.ops.mesh.primitive_circle_add(
        vertices=32, radius=0.29, fill_type="NGON", location=(1.95, 0.6, 0.07))
    coffee = context.object
    coffee.name = "Mug Coffee"
    _paint(coffee, "Buddy Coffee", (0.05, 0.03, 0.02, 1.0), roughness=0.25)
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.15, minor_radius=0.032,
        major_segments=32, minor_segments=10,
        location=(2.30, 0.6, -0.15), rotation=(0, math.pi / 2, 0))
    handle = context.object
    handle.name = "Mug Handle"
    mug_mat = bpy.data.materials.get("Buddy Mug")
    if mug_mat:
        handle.data.materials.append(mug_mat)


def _tour_step_picture(context):
    from mathutils import Vector
    scene = context.scene
    # The mood of his final shot: a near-black room and warm light
    # raking in from the side.
    if scene.world is None:
        scene.world = bpy.data.worlds.new("World")
    scene.world.use_nodes = True
    bg = scene.world.node_tree.nodes.get("Background")
    if bg is not None:
        bg.inputs[0].default_value = (0.012, 0.012, 0.016, 1.0)
        bg.inputs[1].default_value = 0.6
    if scene.camera is None:
        bpy.ops.object.camera_add(location=(3.3, -4.4, 1.9))
        cam = context.object
        cam.data.lens = 42
        # Aimed a touch right of centre so the mug is in the shot,
        # like his final frame.
        direction = Vector((0.35, 0.1, -0.05)) - cam.location
        cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        scene.camera = cam
    if not any(o.type == "LIGHT" for o in scene.objects):
        bpy.ops.object.light_add(type="SUN", location=(-3.0, -2.0, 3.0),
                                 rotation=(0.9, 0.25, -0.65))
        sun = context.object
        sun.data.energy = 2.4
        sun.data.color = (1.0, 0.80, 0.62)
        bpy.ops.object.light_add(type="POINT", location=(2.5, 2.0, 1.2))
        fill = context.object
        fill.data.energy = 12.0
        fill.data.color = (0.7, 0.8, 1.0)
    bpy.ops.buddy.action(action_id="take_picture")


def _tour_step_save(context):
    bpy.ops.buddy.action(action_id="save_work")


def _check_dough(context):
    return _dough(context) is not None


def _check_icing(context):
    icing = _scene_obj(context, "Icing")
    return icing is not None and any(
        m.type == "SOLIDIFY" for m in icing.modifiers)


def _check_icing_pink(context):
    c = _first_colour(_scene_obj(context, "Icing"))
    return bool(c) and c[0] > 0.75 and c[1] < 0.65 and 0.25 < c[2] < 0.85


def _check_dough_colour(context):
    c = _first_colour(_dough(context))
    return bool(c) and 0.3 < c[0] < 0.75 and c[1] < 0.45 and c[2] < 0.3


def _check_sprinkles(context):
    return _scene_obj(context, "Sprinkles") is not None


def _check_plate(context):
    return _scene_obj(context, "Plate") is not None


def _check_picture(context):
    # A fresh Blender scene already HAS a camera and a light, so their
    # existence proves nothing. The proof is the picture file itself,
    # written after this tour started.
    epoch = getattr(context.scene, "buddy_tour_epoch", 0)
    if epoch <= 0:
        return False
    target = os.path.join(os.path.expanduser("~"), "blender_buddy_picture.png")
    fp = context.scene.render.filepath
    if fp and fp.endswith(".png"):
        target = bpy.path.abspath(fp)
    return os.path.exists(target) and os.path.getmtime(target) >= epoch - 2


def _check_saved(context):
    return bool(bpy.data.filepath)


TOUR_STEPS = [
    {"title": "Add the dough ring",
     "how": "Every donut starts as a plain ring of dough. One press "
            "adds it - and clears Blender's starter cube out of the "
            "way first, exactly like the famous tutorial does.",
     "run": _tour_step_dough, "check": _check_dough},
    {"title": "Make the icing",
     "how": "His real method: the icing is the top of the dough itself, "
            "lifted off and given thickness, with its edge pulled down "
            "the sides into uneven drips. One press does all of it.",
     "run": _tour_step_icing, "check": _check_icing},
    {"title": "Colour the icing pink",
     "how": "Pink and glossy, like his. One press paints the icing.",
     "run": _tour_step_icing_pink, "check": _check_icing_pink},
    {"title": "Colour the dough golden",
     "how": "Baked golden, with the pale fry line around its middle - "
            "the band where the donut floated in the oil.",
     "run": _tour_step_dough_colour, "check": _check_dough_colour},
    {"title": "Add the sprinkles",
     "how": "Long thin sprinkles lying flat on the icing - about 130, "
            "in his pastel colours, plus a few that fell on the plate.",
     "run": _tour_step_sprinkles, "check": _check_sprinkles},
    {"title": "Set the scene",
     "how": "His final shot, staged: the donut on a white plate, on a "
            "dark table, with a mug of coffee beside it.",
     "run": _tour_step_plate, "check": _check_plate},
    {"title": "Take the picture",
     "how": "A dark room and warm light raking in from the side - the "
            "mood of his final shot - then the picture itself.",
     "run": _tour_step_picture, "check": _check_picture},
    {"title": "Save your work",
     "how": "Saves the whole scene so you can close Blender and come "
            "back to your donut any time.",
     "run": _tour_step_save, "check": _check_saved},
]


def tour_state(context):
    """(checks, current step index). A step counts as done only when
    the scene itself proves it."""
    checks = []
    for step in TOUR_STEPS:
        try:
            checks.append(bool(step["check"](context)))
        except Exception:
            checks.append(False)
    current = checks.index(False) if False in checks else len(checks)
    return checks, current


# ----------------------------------------------------------------------------
# The one operator behind every button
# ----------------------------------------------------------------------------

class BUDDY_OT_action(Operator):
    bl_idname = "buddy.action"
    bl_label = "Blender Buddy Action"
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


class BUDDY_OT_run_any(Operator):
    bl_idname = "buddy.run_any"
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


class BUDDY_OT_tour_start(Operator):
    bl_idname = "buddy.tour_start"
    bl_label = "Start the Donut"
    bl_options = {"REGISTER"}

    def execute(self, context):
        import time
        global _EXPERT_TIP
        context.scene.buddy_tour_started = True
        context.scene.buddy_tour_epoch = int(time.time())
        _EXPERT_TIP = "Donut tour, step 1: Add the dough ring."
        self.report({"INFO"}, "Donut tour started - step 1 is at the top "
                              "of the Blender Buddy panel.")
        return {"FINISHED"}


class BUDDY_OT_tour_hide(Operator):
    bl_idname = "buddy.tour_hide"
    bl_label = "Hide the Donut Tour"
    bl_options = {"REGISTER"}

    def execute(self, context):
        context.scene.buddy_tour_started = False
        return {"FINISHED"}


class BUDDY_OT_tour_do(Operator):
    bl_idname = "buddy.tour_do"
    bl_label = "Do This Step"
    bl_description = ("Do this donut step now. The step only ticks off "
                      "when the scene itself proves it happened")
    bl_options = {"REGISTER", "UNDO"}

    step: IntProperty(options={"HIDDEN"})

    def execute(self, context):
        global _EXPERT_TIP
        if not (0 <= self.step < len(TOUR_STEPS)):
            return {"CANCELLED"}
        step = TOUR_STEPS[self.step]
        try:
            step["run"](context)
        except Exception as exc:
            self.report({"WARNING"}, f"That step didn't finish: {exc}")
            return {"CANCELLED"}
        if step["check"](context):
            nxt = self.step + 1
            if nxt < len(TOUR_STEPS):
                _EXPERT_TIP = (f"Donut tour, step {nxt + 1}: "
                               f"{TOUR_STEPS[nxt]['title']}.")
                self.report({"INFO"}, f"Done - {step['title']}. "
                                      f"Next: {TOUR_STEPS[nxt]['title']}.")
            else:
                _EXPERT_TIP = "You made the donut. Ask me anything."
                self.report({"INFO"}, "Done - you made the donut.")
        else:
            self.report({"INFO"}, f"{step['title']} - take a look at the "
                                  "scene; the step ticks off when it's "
                                  "really there.")
        return {"FINISHED"}


# ----------------------------------------------------------------------------
# The Buddy Expert: plug in your own AI key and a small expert lives in
# the panel - and floats over the 3D window - answering in plain words
# about YOUR scene. It can also point at the exact Buddy button for
# the job, with a Do-it button right there. The key is the user's own,
# stored in Blender's preferences on their own computer; Buddy brings
# no key and charges nothing.
# ----------------------------------------------------------------------------

_EXPERT_DEFAULT_URL = "https://api.openai.com/v1/chat/completions"
_EXPERT_DEFAULT_MODEL = "gpt-4o-mini"
_EXPERT_LOCAL_URL = "http://localhost:11434/v1/chat/completions"
_EXPERT_LOCAL_MODEL = "llama3.1"
_EXPERT_TIP = ""
_EXPERT_HANDLE = None


def _expert_service_update(self, context):
    """Picking a way to reach the expert pre-fills the address and
    model fields for that way; the user can still edit them after."""
    if self.expert_service == "LOCAL":
        self.expert_url = _EXPERT_LOCAL_URL
        self.expert_model = _EXPERT_LOCAL_MODEL
    elif self.expert_service == "KEY":
        if (self.expert_url or "").startswith(("http://localhost",
                                                "http://127.0.0.1")):
            self.expert_url = _EXPERT_DEFAULT_URL
            self.expert_model = _EXPERT_DEFAULT_MODEL


class BUDDY_Preferences(AddonPreferences):
    bl_idname = __name__

    expert_service: EnumProperty(
        name="How the expert reaches your AI",
        description="Key: an AI service key you paste below. ChatGPT "
                    "login: through OpenAI's own Codex program on "
                    "this computer, signed in with your ChatGPT "
                    "account - Buddy never sees your login. Local AI: "
                    "a free AI running on this computer (like Ollama) "
                    "- no key, no login, nothing leaves the machine",
        items=[
            ("KEY", "AI key (OpenAI-style service)",
             "Paste a key from an AI service below"),
            ("CODEX", "ChatGPT login (through the Codex program)",
             "Uses OpenAI's Codex program on this computer, signed "
             "in with your ChatGPT account"),
            ("LOCAL", "Local AI on this computer (no key, no login)",
             "Talks to a free local AI such as Ollama"),
        ],
        default="KEY", update=_expert_service_update)
    expert_key: StringProperty(
        name="AI key",
        description="Your own AI service key (for example an OpenAI key). "
                    "It stays in Blender's preferences on your computer",
        default="", subtype="PASSWORD")
    expert_url: StringProperty(
        name="AI service address",
        description="The chat address of your AI service. The default "
                    "is OpenAI's; any service with the same chat shape "
                    "works",
        default=_EXPERT_DEFAULT_URL)
    expert_model: StringProperty(
        name="AI model",
        description="Which model answers you",
        default=_EXPERT_DEFAULT_MODEL)
    expert_float: BoolProperty(
        name="Float the expert over the 3D window",
        description="Show the expert's latest tip as a small floating "
                    "card over the big 3D window",
        default=True)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "expert_service")
        layout.prop(self, "expert_key")
        layout.prop(self, "expert_url")
        layout.prop(self, "expert_model")
        layout.prop(self, "expert_float")
        _wrap(layout, "Why no plain 'log in with ChatGPT or Muse' "
                      "button? Those companies don't offer one to "
                      "other apps: a ChatGPT or Claude subscription "
                      "login only works inside their own apps. The "
                      "honest ways around it are above. ChatGPT "
                      "login: OpenAI's own Codex program on your "
                      "computer IS signed in with your account, so "
                      "Buddy asks through it - your login never "
                      "touches Buddy. Claude logins can't be used "
                      "this way at all (Anthropic's rule, enforced "
                      "since 2026 - accounts were blocked for it), so "
                      "Buddy doesn't offer it rather than put your "
                      "Claude account at risk. Local AI needs "
                      "nothing: install a free local AI (for example "
                      "Ollama), pick Local, and everything stays on "
                      "your computer.")
        _wrap(layout, "Whatever way you pick: when you ask, Buddy "
                      "sends your question plus a short description "
                      "of your scene (what's in it, what you have "
                      "picked, which mode you're in). Nothing else "
                      "is sent. A key stays on your computer, in "
                      "Blender's own preferences.")


def _expert_settings():
    try:
        prefs = bpy.context.preferences.addons[__name__].preferences
        return {"key": prefs.expert_key, "url": prefs.expert_url,
                "model": prefs.expert_model, "float": prefs.expert_float,
                "service": prefs.expert_service}
    except Exception:
        return {"key": "", "url": _EXPERT_DEFAULT_URL,
                "model": _EXPERT_DEFAULT_MODEL, "float": True,
                "service": "KEY"}


def _is_local_url(url):
    return (url or "").startswith(("http://localhost", "http://127.0.0.1"))


def _expert_ready(settings):
    """Can the expert actually be asked right now? A key for key
    services, the Codex program for ChatGPT login, nothing at all
    for a local AI."""
    service = settings.get("service", "KEY")
    if service == "CODEX":
        return shutil.which("codex") is not None
    if service == "LOCAL":
        return True
    return bool(settings.get("key")) or _is_local_url(settings.get("url"))


def _expert_setup_message(settings):
    service = settings.get("service", "KEY")
    if service == "CODEX":
        return ("The expert is set to use your ChatGPT login, but "
                "OpenAI's Codex program isn't on this computer yet. "
                "Install Codex (it's OpenAI's own program), sign in "
                "with your ChatGPT account once, then ask again - "
                "Buddy asks through it, so your login never touches "
                "Buddy.")
    if service == "LOCAL":
        return ("The expert is set to a local AI, but it didn't "
                "answer. Make sure your local AI (for example "
                "Ollama) is running, then ask again.")
    return ("The expert isn't set up yet. Press 'Set up the expert' "
            "and either paste your own AI key, choose ChatGPT login "
            "(through OpenAI's Codex program), or choose a local AI "
            "- the key stays on your computer.")


def _run_cli(argv, timeout=120):
    """Run one of the AI companies' own programs and return what it
    prints. This is the ONLY way Buddy talks to a subscription
    login: through the company's own program, never through a
    copied login."""
    proc = subprocess.run(argv, capture_output=True, text=True,
                          timeout=timeout, cwd=tempfile.gettempdir())
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-200:]
        raise RuntimeError(tail or "the AI program didn't answer")
    return proc.stdout


def _ask_via_codex(system, user):
    out = _run_cli(["codex", "exec", "-s", "read-only",
                    "--skip-git-repo-check", f"{system}\n\n{user}"])
    text = (out or "").strip()
    if not text:
        raise RuntimeError("the Codex program answered with nothing")
    return text


def _scene_summary(context):
    counts = {}
    for o in context.scene.objects:
        counts[o.type] = counts.get(o.type, 0) + 1
    parts = [f"{n} {t.lower()}{'s' if n > 1 else ''}"
             for t, n in sorted(counts.items())]
    obj = context.object
    picked = (f"Picked: {obj.name} ({obj.type.lower()})."
              if obj else "Nothing picked.")
    checks, current = (tour_state(context)
                       if getattr(context.scene, "buddy_tour_started", False)
                       else (None, None))
    tour = ""
    if checks is not None:
        tour = (f" Donut tour: {sum(checks)} of {len(checks)} steps done"
                + (f", current step: {TOUR_STEPS[current]['title']}."
                   if current < len(checks) else " - finished."))
    return (f"Scene has: {', '.join(parts) or 'nothing'}. {picked} "
            f"Mode: {context.mode}.{tour} "
            f"Saved file: {'yes' if bpy.data.filepath else 'not yet'}.")


def _expert_system_prompt():
    buttons = "; ".join(f"{a['id']} = {a['plain']}" for a in ACTIONS)
    return (
        "You are the Buddy Expert, a patient Blender teacher inside a "
        "beginner add-on called Blender Buddy. Rules: answer in plain "
        "everyday words, no jargon without explaining it, at most 60 "
        "words. Teach for the user's actual scene, which is described "
        "in their message. If one of the add-on's buttons below does "
        "the job, end your answer with one extra line exactly like "
        "this: BUTTON: <id> (only when a button truly fits).\n"
        f"Buttons: {buttons}")


_AGENT_OPS_CACHE = None


def _agent_ops_list():
    """The Blender tools the expert may use in a plan: the everyday
    categories, as 'idname = name' lines. Cached."""
    global _AGENT_OPS_CACHE
    if _AGENT_OPS_CACHE is not None:
        return _AGENT_OPS_CACHE
    cats = {"mesh", "object", "view3d", "render", "scene", "wm",
            "transform", "curve", "surface", "armature", "material"}
    lines = [f"{e['idname']} = {e['label']}"
             for e in build_index() if e["cat"] in cats]
    _AGENT_OPS_CACHE = "\n".join(lines)
    return _AGENT_OPS_CACHE


def _expert_agent_prompt():
    buttons = "; ".join(f"{a['id']} = {a['plain']}" for a in ACTIONS)
    settings = "\n".join(f"STEP: set:{s['desc']}"
                         for s in SETTINGS.values())
    styles = "; ".join(f"{k} = {v[0]}" for k, v in STYLES.items())
    return (
        "You are the Buddy Expert, the user's own agent inside a "
        "beginner Blender add-on. The user asks for a result in "
        "plain words; you reply with a plan the add-on will run, "
        "step by step, in their Blender. You can press buttons, run "
        "Blender tools, adjust exact settings (like giving them the "
        "precise sculpt brush they describe), apply node-tree "
        "styles, and look up add-ons for them. Format EXACTLY:\n"
        "SUMMARY: <one plain sentence saying what the plan achieves>\n"
        "STEP: button:<id>   (an add-on button, preferred)\n"
        "STEP: tool:<idname>   (a raw Blender tool, when no button fits)\n"
        "STEP: set:<setting from the settings list>\n"
        "STEP: style:<style name>   (a node-tree style for the "
        "picked thing)\n"
        "STEP: find:<words>   (open an add-on search for these "
        "words, when a plugin would serve them better)\n"
        "One STEP per line, in the order they must run. Prefer "
        "buttons - they are safe and beginner-shaped. Use at most 8 "
        "steps. Only use ids from the lists below; anything else is "
        "dropped. No other text.\n"
        f"Buttons: {buttons}\n"
        f"Settings you may adjust:\n{settings}\n"
        f"Styles: {styles}\n"
        f"Tools:\n{_agent_ops_list()}")


def _first_modifier(context, mtype):
    obj = context.object
    if obj is None:
        return None
    for mod in obj.modifiers:
        if mod.type == mtype:
            return mod
    return None


def _sculpt_brush(context):
    ts = context.tool_settings
    brush = ts.sculpt.brush if ts.sculpt else None
    if brush is None:
        brush = bpy.data.brushes.new("Buddy Brush", mode="SCULPT")
        if ts.sculpt:
            ts.sculpt.brush = brush
    return brush


def _need_modifier(context, mtype, plain):
    mod = _first_modifier(context, mtype)
    if mod is None:
        raise RuntimeError(f"the picked thing has no {plain} yet - "
                           "add one first, then set it")
    return mod


# Settings the agent may adjust directly - the "give me the exact
# brush" layer. Each has a plain description (which is also what the
# AI sees), a setter, and a reader so a run step can verify its own
# work landed.
SETTINGS = {
    "brush.size": {
        "label": "Sculpt brush size",
        "desc": "brush.size:<pixels 1-500> - the sculpt brush's size",
        "set": lambda c, v: setattr(_sculpt_brush(c), "size", int(v)),
        "get": lambda c: _sculpt_brush(c).size,
    },
    "brush.strength": {
        "label": "Sculpt brush strength",
        "desc": "brush.strength:<0-1> - how hard the sculpt brush pushes",
        "set": lambda c, v: setattr(_sculpt_brush(c), "strength", float(v)),
        "get": lambda c: _sculpt_brush(c).strength,
    },
    "brush.falloff": {
        "label": "Sculpt brush falloff",
        "desc": "brush.falloff:<SMOOTH|SPHERE|SHARP|LIN|CONSTANT> - "
                "the shape of the sculpt brush's edge",
        "set": lambda c, v: setattr(_sculpt_brush(c), "curve_preset", str(v)),
        "get": lambda c: _sculpt_brush(c).curve_preset,
    },
    "bevel.width": {
        "label": "Edge rounding width",
        "desc": "bevel.width:<0-1> - width of the picked thing's bevel "
                "(needs a bevel on it first, e.g. from 'Round off a "
                "sharp edge')",
        "set": lambda c, v: setattr(
            _need_modifier(c, "BEVEL", "bevel"), "width", float(v)),
        "get": lambda c: _need_modifier(c, "BEVEL", "bevel").width,
    },
    "bevel.segments": {
        "label": "Edge rounding smoothness",
        "desc": "bevel.segments:<1-10> - segments of the bevel",
        "set": lambda c, v: setattr(
            _need_modifier(c, "BEVEL", "bevel"), "segments", int(v)),
        "get": lambda c: _need_modifier(c, "BEVEL", "bevel").segments,
    },
    "subdivision.levels": {
        "label": "Smoothness levels",
        "desc": "subdivision.levels:<0-6> - the picked thing's "
                "subdivision (needs one first, e.g. 'Make it smoother "
                "& rounder')",
        "set": lambda c, v: setattr(
            _need_modifier(c, "SUBSURF", "subdivision"), "levels", int(v)),
        "get": lambda c: _need_modifier(c, "SUBSURF", "subdivision").levels,
    },
    "solidify.thickness": {
        "label": "Shell thickness",
        "desc": "solidify.thickness:<0-1> - the picked thing's "
                "solidify thickness (needs one first)",
        "set": lambda c, v: setattr(
            _need_modifier(c, "SOLIDIFY", "solidify"), "thickness", float(v)),
        "get": lambda c: _need_modifier(c, "SOLIDIFY", "solidify").thickness,
    },
    "array.count": {
        "label": "Copies in a row",
        "desc": "array.count:<1-50> - copies in the picked thing's "
                "array (needs one first, e.g. 'Make a row of copies')",
        "set": lambda c, v: setattr(
            _need_modifier(c, "ARRAY", "array"), "count", int(v)),
        "get": lambda c: _need_modifier(c, "ARRAY", "array").count,
    },
    "render.samples": {
        "label": "Picture quality (Cycles samples)",
        "desc": "render.samples:<1-4096> - more samples = a cleaner "
                "picture that takes longer",
        "set": lambda c, v: setattr(c.scene.cycles, "samples", int(v)),
        "get": lambda c: c.scene.cycles.samples,
    },
    "light.energy": {
        "label": "Picked light brightness",
        "desc": "light.energy:<number> - the picked light's strength "
                "(the picked thing must be a light)",
        "set": lambda c, v: setattr(c.object.data, "energy", float(v)),
        "get": lambda c: c.object.data.energy,
    },
    "camera.focal": {
        "label": "Camera zoom (lens mm)",
        "desc": "camera.focal:<10-200> - the scene camera's lens",
        "set": lambda c, v: setattr(c.scene.camera.data, "lens", float(v)),
        "get": lambda c: c.scene.camera.data.lens,
    },
}


def _style_material(obj):
    if obj is None or obj.type not in {"MESH", "CURVE", "FONT"}:
        raise RuntimeError("pick a shape first - a style needs "
                           "something to land on")
    if not obj.data.materials:
        obj.data.materials.append(bpy.data.materials.new("Buddy Style"))
    mat = obj.data.materials[0]
    mat.use_nodes = True
    return mat


def _bsdf(mat):
    node = mat.node_tree.nodes.get("Principled BSDF")
    if node is None:
        raise RuntimeError("the material has no Principled node to style")
    return node


def _style_chrome(obj):
    bsdf = _bsdf(_style_material(obj))
    bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.92, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.08


def _style_brushed_metal(obj):
    mat = _style_material(obj)
    bsdf = _bsdf(mat)
    bsdf.inputs["Base Color"].default_value = (0.75, 0.75, 0.78, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.35
    tree = mat.node_tree
    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 150.0
    bump = tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.15
    tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])


def _style_matte_ceramic(obj):
    bsdf = _bsdf(_style_material(obj))
    bsdf.inputs["Metallic"].default_value = 0.0
    bsdf.inputs["Roughness"].default_value = 0.6
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 0.05


def _style_glowing(obj):
    bsdf = _bsdf(_style_material(obj))
    base = bsdf.inputs["Base Color"].default_value
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = base
    if "Emission Strength" in bsdf.inputs:
        bsdf.inputs["Emission Strength"].default_value = 3.0
    bsdf.inputs["Roughness"].default_value = 0.4


def _style_glass(obj):
    bsdf = _bsdf(_style_material(obj))
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.05
    if "IOR" in bsdf.inputs:
        bsdf.inputs["IOR"].default_value = 1.45


def _style_wood(obj):
    mat = _style_material(obj)
    bsdf = _bsdf(mat)
    tree = mat.node_tree
    noise = tree.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 3.0
    noise.inputs["Detail"].default_value = 6.0
    ramp = tree.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.25, 0.12, 0.04, 1.0)
    ramp.color_ramp.elements[1].color = (0.55, 0.33, 0.14, 1.0)
    bump = tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.3
    tree.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.55


def _style_marble(obj):
    mat = _style_material(obj)
    bsdf = _bsdf(mat)
    tree = mat.node_tree
    vor = tree.nodes.new("ShaderNodeTexVoronoi")
    vor.inputs["Scale"].default_value = 4.0
    ramp = tree.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.85, 0.85, 0.87, 1.0)
    ramp.color_ramp.elements[1].color = (0.35, 0.35, 0.40, 1.0)
    tree.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    tree.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.15


# Named node-tree styles the agent can apply - "style the tree for
# me", one press deep. Each builds a REAL node tree on the material.
STYLES = {
    "chrome": ("mirror chrome metal", _style_chrome),
    "brushed_metal": ("brushed metal with a fine grain", _style_brushed_metal),
    "matte_ceramic": ("soft matte ceramic", _style_matte_ceramic),
    "glowing": ("glowing, lit from inside", _style_glowing),
    "glass": ("clear glass", _style_glass),
    "wood": ("procedural wood grain (a real node tree)", _style_wood),
    "marble": ("procedural marble veins (a real node tree)", _style_marble),
}


def _open_url(url):
    return bpy.ops.wm.url_open(url=url)


_SETTING_INT_KEYS = {
    "brush.size", "bevel.segments", "subdivision.levels", "array.count",
    "render.samples",
}
_SETTING_ENUMS = {
    "brush.falloff": {"SMOOTH", "SPHERE", "SHARP", "LIN", "CONSTANT"},
}


def _coerce_setting(key, raw):
    """Turn an agent's text value into the setting's real type, or
    raise ValueError. A plan step is only kept when this succeeds."""
    if key in _SETTING_ENUMS:
        value = str(raw).upper()
        if value not in _SETTING_ENUMS[key]:
            raise ValueError(f"{value} is not one of the falloff shapes")
        return value
    if key in _SETTING_INT_KEYS:
        return int(raw)
    return float(raw)


def _parse_plan(text):
    """(summary, steps, dropped) from an agent reply. Steps are only
    kept when everything they name is verifiably real: the button
    exists, the tool exists, the setting is in the registry, the
    style is in the library."""
    summary = ""
    steps = []
    dropped = 0
    valid_tools = None
    for line in (text or "").splitlines():
        m = re.match(r"\s*SUMMARY:\s*(.+)$", line)
        if m:
            summary = m.group(1).strip()
            continue
        m = re.match(r"\s*STEP:\s*(button|tool|style|find):\s*(\S.*?)\s*$",
                     line)
        if m:
            kind, ident = m.group(1), m.group(2)
            if kind == "button" and any(a["id"] == ident for a in ACTIONS):
                steps.append({"kind": "button", "id": ident})
            elif kind == "tool":
                if valid_tools is None:
                    valid_tools = {e["idname"] for e in build_index()}
                if ident in valid_tools:
                    steps.append({"kind": "tool", "id": ident})
                else:
                    dropped += 1
            elif kind == "style" and ident in STYLES:
                steps.append({"kind": "style", "id": ident})
            elif kind == "find" and 0 < len(ident) <= 60:
                steps.append({"kind": "find", "id": ident})
            else:
                dropped += 1
            continue
        m = re.match(r"\s*STEP:\s*set:\s*([a-z_.]+):\s*(\S+)\s*$", line)
        if m:
            key, raw = m.group(1), m.group(2)
            if key in SETTINGS:
                try:
                    value = _coerce_setting(key, raw)
                except (TypeError, ValueError):
                    dropped += 1
                else:
                    steps.append({"kind": "set", "id": key, "value": value})
            else:
                dropped += 1
    return summary, steps, dropped


def _ask_ai(settings, system, user):
    if settings.get("service") == "CODEX":
        return _ask_via_codex(system, user)
    payload = {"model": settings["model"],
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}]}
    data = _expert_http(settings["url"], settings["key"], payload)
    return data["choices"][0]["message"]["content"].strip()


def _step_label(step):
    if step["kind"] == "button":
        act = next((a for a in ACTIONS if a["id"] == step["id"]), None)
        return act["plain"] if act else step["id"]
    if step["kind"] == "set":
        return f"Set {SETTINGS[step['id']]['label'].lower()} to {step['value']}"
    if step["kind"] == "style":
        return f"Style it: {STYLES[step['id']][0]}"
    if step["kind"] == "find":
        return f"Find add-ons for: {step['id']}"
    for e in build_index():
        if e["idname"] == step["id"]:
            return f"{e['label']} (Blender tool)"
    return step["id"]


def _expert_http(url, key, payload):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


class BUDDY_OT_open_prefs(Operator):
    bl_idname = "buddy.open_prefs"
    bl_label = "Set Up the Expert"
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.preferences.addon_show(module=__name__)
        return {"FINISHED"}


class BUDDY_OT_ask_expert(Operator):
    bl_idname = "buddy.ask_expert"
    bl_label = "Ask the Expert"
    bl_description = ("Ask the AI expert about your scene, in your own "
                      "words. It answers in plain words and points at "
                      "the right button when Buddy has one")
    bl_options = {"REGISTER"}

    def execute(self, context):
        global _EXPERT_TIP
        wm = context.window_manager
        settings = _expert_settings()
        question = (wm.buddy_ask or "").strip()
        if not _expert_ready(settings):
            wm.buddy_answer = _expert_setup_message(settings)
            wm.buddy_suggested = ""
            return {"CANCELLED"}
        if not question:
            wm.buddy_answer = "Type a question first - anything, in your own words."
            return {"CANCELLED"}
        if getattr(wm, "buddy_agent", False):
            try:
                text = _ask_ai(
                    settings, _expert_agent_prompt(),
                    f"{_scene_summary(context)}\n\nGoal: {question}")
            except Exception:
                text = ""
            if text:
                summary, steps, dropped = _parse_plan(text)
                if steps:
                    wm.buddy_plan = json.dumps(steps)
                    wm.buddy_plan_summary = summary or question
                    wm.buddy_plan_retried = ""
                    wm.buddy_answer = ""
                    wm.buddy_suggested = ""
                    note = (f" The expert also suggested {dropped} "
                            f"step{'s' if dropped > 1 else ''} that "
                            "couldn't be verified, so those were left out."
                            if dropped else "")
                    wm.buddy_plan_report = (
                        f"Plan ready: {len(steps)} steps.{note} "
                        "Check them below, then press Run.")
                    _EXPERT_TIP = f"Plan ready: {len(steps)} steps. Press Run these steps."
                    self.report({"INFO"}, "The expert made a plan - it's "
                                          "in the panel, ready to run.")
                    return {"FINISHED"}
            # No usable plan came back: fall through and answer as
            # plain advice instead of failing the user.
        try:
            text = _ask_ai(
                settings, _expert_system_prompt(),
                f"{_scene_summary(context)}\n\nQuestion: {question}")
        except Exception:
            wm.buddy_answer = ("The expert didn't answer. Check the "
                               "setup in the add-on's preferences, "
                               "and that you're online - then ask "
                               "again.")
            wm.buddy_suggested = ""
            return {"CANCELLED"}
        suggested = ""
        lines = text.splitlines()
        kept = []
        for line in lines:
            m = re.match(r"\s*BUTTON:\s*([a-z0-9_]+)\s*$", line)
            if m and any(a["id"] == m.group(1) for a in ACTIONS):
                suggested = m.group(1)
            elif not line.strip().upper().startswith("BUTTON:"):
                kept.append(line)
        wm.buddy_answer = "\n".join(kept).strip()
        wm.buddy_suggested = suggested
        first = wm.buddy_answer.split(". ")[0].strip()
        _EXPERT_TIP = (first[:110] + ("..." if len(first) > 110 else ""))
        self.report({"INFO"}, "The expert answered - it's in the panel.")
        return {"FINISHED"}


class BUDDY_OT_run_plan(Operator):
    bl_idname = "buddy.run_plan"
    bl_label = "Run These Steps"
    bl_description = ("Run the expert's plan, step by step, in your "
                      "Blender. It stops at the first step that can't "
                      "run and tells you plainly what happened")
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        global _EXPERT_TIP
        wm = context.window_manager
        try:
            steps = json.loads(wm.buddy_plan or "[]")
        except Exception:
            steps = []
        if not steps:
            wm.buddy_plan_report = "There's no plan to run."
            return {"CANCELLED"}
        done = 0
        notes = []
        fail_at, fail_why = None, ""
        for i, step in enumerate(steps):
            try:
                if step["kind"] == "button":
                    result = bpy.ops.buddy.action(action_id=step["id"])
                    ok = bool(result) and "FINISHED" in result
                elif step["kind"] == "tool":
                    result = _resolve_op(step["id"])()
                    ok = bool(result) and "FINISHED" in result
                elif step["kind"] == "set":
                    spec = SETTINGS[step["id"]]
                    spec["set"](context, step["value"])
                    got = spec["get"](context)
                    want = step["value"]
                    try:
                        ok = abs(float(got) - float(want)) < 1e-6
                    except (TypeError, ValueError):
                        ok = str(got) == str(want)
                    if not ok:
                        fail_why = (f"the setting reads back as {got}, "
                                    f"not {want}")
                elif step["kind"] == "style":
                    STYLES[step["id"]][1](context.object)
                    ok = True
                elif step["kind"] == "find":
                    import urllib.parse
                    _open_url("https://extensions.blender.org/search/"
                              "?q=" + urllib.parse.quote(step["id"]))
                    notes.append(f"Opened the add-on search for "
                                 f"'{step['id']}' in your browser - "
                                 "anything you install there shows up "
                                 "in Blender like Buddy did.")
                    ok = True
                else:
                    ok = False
            except Exception as exc:
                raw = str(exc)
                if "poll() failed" in raw or "context is incorrect" in raw:
                    fail_why = ("that step needs a different mode or "
                                "something different picked first")
                else:
                    fail_why = raw[:90]
                ok = False
            if not ok:
                fail_at = i
                if not fail_why:
                    fail_why = ("it couldn't run in the scene as it "
                                "is right now")
                break
            done += 1
        total = len(steps)
        if fail_at is None:
            wm.buddy_plan = ""
            wm.buddy_plan_report = (
                f"Done - all {total} steps ran. "
                f"{wm.buddy_plan_summary}"
                + ((" " + " ".join(notes)) if notes else ""))
            _EXPERT_TIP = f"Plan finished: {total} steps done."
            self.report({"INFO"}, wm.buddy_plan_report)
            return {"FINISHED"}
        label = _step_label(steps[fail_at])
        base = (f"Stopped at step {fail_at + 1} of {total} "
                f"('{label}'): {fail_why}. "
                f"{done} step{'s' if done != 1 else ''} before it "
                "did run, and they're kept - nothing was undone.")
        # One replan: send the failure back and let the expert route
        # around it. The new plan is SHOWN, never auto-run.
        settings = _expert_settings()
        if _expert_ready(settings) and not wm.buddy_plan_retried:
            try:
                text = _ask_ai(
                    settings, _expert_agent_prompt(),
                    f"{_scene_summary(context)}\n\n"
                    f"Goal: {wm.buddy_ask}\n"
                    f"Your previous plan stopped at step "
                    f"{fail_at + 1} ('{label}'): {fail_why}. "
                    f"Give a revised plan that still reaches the "
                    f"goal from the scene as it is now.")
                summary, new_steps, _d = _parse_plan(text)
                if new_steps:
                    wm.buddy_plan = json.dumps(new_steps)
                    wm.buddy_plan_summary = summary or wm.buddy_plan_summary
                    wm.buddy_plan_retried = "1"
                    wm.buddy_plan_report = (
                        base + " The expert replanned around it - "
                        "check the new plan below and press Run again.")
                    _EXPERT_TIP = "The plan hit a snag; the expert replanned."
                    self.report({"WARNING"}, wm.buddy_plan_report)
                    return {"CANCELLED"}
            except Exception:
                pass
        wm.buddy_plan_report = base
        _EXPERT_TIP = f"Plan stopped at step {fail_at + 1} of {total}."
        self.report({"WARNING"}, base)
        return {"CANCELLED"}


class BUDDY_OT_clear_plan(Operator):
    bl_idname = "buddy.clear_plan"
    bl_label = "Throw the Plan Away"
    bl_options = {"REGISTER"}

    def execute(self, context):
        wm = context.window_manager
        wm.buddy_plan = ""
        wm.buddy_plan_summary = ""
        wm.buddy_plan_report = ""
        wm.buddy_plan_retried = ""
        return {"FINISHED"}


def _draw_expert_overlay():
    """The floating expert: a small card over the 3D window with the
    latest tip. Drawn by Blender itself; must never raise."""
    try:
        if not _EXPERT_TIP or not _expert_settings()["float"]:
            return
        import blf
        import gpu
        from gpu_extras.batch import batch_for_shader
        region = bpy.context.region
        if region is None:
            return
        lines = ["Buddy Expert"] + textwrap.wrap(_EXPERT_TIP, width=46)[:3]
        width, height = 380, 26 + 16 * len(lines)
        x, y = 14, region.height - height - 14
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        batch = batch_for_shader(
            shader, "TRI_FAN",
            {"pos": [(x, y), (x + width, y), (x + width, y + height),
                     (x, y + height)]})
        gpu.state.blend_set("ALPHA")
        shader.bind()
        shader.uniform_float("color", (0.05, 0.05, 0.07, 0.85))
        batch.draw(shader)
        font = 0
        blf.size(font, 12)
        ty = y + height - 18
        for i, line in enumerate(lines):
            blf.color(font, 1.0, 0.85, 0.4, 1.0) if i == 0 else \
                blf.color(font, 0.95, 0.95, 0.95, 1.0)
            blf.position(font, x + 10, ty, 0)
            blf.draw(font, line)
            ty -= 16
        gpu.state.blend_set("NONE")
    except Exception:
        pass


# ----------------------------------------------------------------------------
# The panel
# ----------------------------------------------------------------------------

def _wrap(layout, text, width=44):
    for line in textwrap.wrap(text, width=width) or [""]:
        layout.label(text=line)


def _draw_action(layout, act, show_real):
    row = layout.row(align=True)
    if act.get("icon"):
        op = row.operator("buddy.action", text=act["plain"], icon=act["icon"])
    else:
        op = row.operator("buddy.action", text=act["plain"])
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


class VIEW3D_PT_blender_buddy(Panel):
    bl_idname = "VIEW3D_PT_blender_buddy"
    bl_label = "Blender Buddy - in plain words"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender Buddy"

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager
        show_real = getattr(wm, "buddy_show_real", True)

        scene = context.scene
        if not (wm.buddy_query or "").strip():
            box = layout.box()
            if not getattr(scene, "buddy_tour_started", False):
                box.label(text="Day 1: Make a Donut", icon="MESH_TORUS")
                _wrap(box, "The donut is how millions of people started "
                           "Blender - the Blender Guru's tutorial made it "
                           "the famous first project. This is the same "
                           "donut in plain words: 8 steps, one press each, "
                           "and a step only ticks off when your scene "
                           "proves it's done.")
                box.operator("buddy.tour_start", text="Start the donut")
            else:
                checks, current = tour_state(context)
                done = sum(checks)
                if current >= len(TOUR_STEPS):
                    box.label(text="You made the donut", icon="CHECKMARK")
                    _wrap(box, "Dough, icing, sprinkles, plate, picture, "
                               "saved - the same first project as the "
                               "famous tutorial, done in 8 presses. "
                               "Everything after this is just more tools "
                               "from the sections below.")
                    box.operator("buddy.tour_hide", text="Hide this")
                else:
                    step = TOUR_STEPS[current]
                    box.label(text=f"Make a Donut - step {current + 1} of "
                                   f"{len(TOUR_STEPS)}: {step['title']}",
                              icon="MESH_TORUS")
                    _wrap(box, step["how"])
                    op = box.operator("buddy.tour_do", text="Do this step")
                    op.step = current
                    _wrap(box, f"Done so far: {done} of {len(TOUR_STEPS)}. "
                               "Ticks are earned by the scene, not by "
                               "pressing.")
                    box.operator("buddy.tour_hide", text="Not now")

        if not (wm.buddy_query or "").strip():
            box = layout.box()
            box.label(text="Buddy Expert", icon="USER")
            settings = _expert_settings()
            if not _expert_ready(settings):
                _wrap(box, "Set up your expert and a small expert "
                           "lives here - and floats over the 3D "
                           "window. Three ways: your own AI key, your "
                           "ChatGPT login (through OpenAI's Codex "
                           "program), or a free local AI with no key "
                           "and no login at all. Ask in your own "
                           "words ('how do I make this look like "
                           "chrome?') and it answers for YOUR scene.")
                box.operator("buddy.open_prefs", text="Set up the expert")
            else:
                box.prop(wm, "buddy_agent", text="Let the expert do it")
                _wrap(box, "On: the expert makes a plan you can check "
                           "and run. It can press tools, set exact "
                           "values (like the exact sculpt brush you "
                           "ask for), style node trees, and find "
                           "add-ons. Off: it only gives advice.")
                box.prop(wm, "buddy_ask", text="")
                box.operator("buddy.ask_expert", text="Ask the expert")
                if (wm.buddy_answer or "").strip():
                    _wrap(box, wm.buddy_answer, width=48)
                if wm.buddy_suggested:
                    act = next((a for a in ACTIONS
                                if a["id"] == wm.buddy_suggested), None)
                    if act:
                        op = box.operator(
                            "buddy.action",
                            text=f"Do it: {act['plain']}")
                        op.action_id = act["id"]
                if (wm.buddy_plan_report or "").strip():
                    _wrap(box, wm.buddy_plan_report, width=48)
                plan = []
                try:
                    plan = json.loads(wm.buddy_plan or "[]")
                except Exception:
                    plan = []
                if plan:
                    if (wm.buddy_plan_summary or "").strip():
                        box.label(text="The plan", icon="SEQUENCE")
                        _wrap(box, wm.buddy_plan_summary, width=48)
                    for number, step in enumerate(plan, start=1):
                        try:
                            label = _step_label(step)
                        except Exception:
                            label = str(step.get("id", "Step"))
                        box.label(text=f"{number}. {label}")
                    box.operator("buddy.run_plan", text="Run these steps")
                    box.operator("buddy.clear_plan",
                                 text="Throw the plan away")

        box = layout.box()
        box.label(text="Where you are", icon="INFO")
        _wrap(box, _hint(context))

        box = layout.box()
        box.label(text="What do you want to do?", icon="VIEWZOOM")
        box.prop(wm, "buddy_query", text="")
        query = getattr(wm, "buddy_query", "")
        if query.strip():
            hits = search_actions(query)
            if hits:
                for act in hits[:10]:
                    _draw_action(box, act, show_real)
            else:
                _wrap(box, "No match. Try everyday words: round, copy, hole, "
                           "smooth, move, thicker, colour, delete.")
        box.prop(wm, "buddy_show_real",
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
                    op = row.operator("buddy.run_any",
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


CLASSES = (BUDDY_Preferences, BUDDY_OT_action, BUDDY_OT_run_any,
           BUDDY_OT_tour_start, BUDDY_OT_tour_hide, BUDDY_OT_tour_do,
           BUDDY_OT_open_prefs, BUDDY_OT_ask_expert, BUDDY_OT_run_plan,
           BUDDY_OT_clear_plan, VIEW3D_PT_blender_buddy)


def register():
    for cls in CLASSES:
        bpy.utils.register_class(cls)
    bpy.types.WindowManager.buddy_query = StringProperty(
        name="What do you want to do?",
        description="Type it in your own words - 'round the edges', "
                    "'make a copy', 'cut a hole' - and the matching "
                    "tools appear here",
        default="",
    )
    bpy.types.WindowManager.buddy_show_real = BoolProperty(
        name="Show real names",
        description="Show Blender's own name and shortcut under each "
                    "plain-words button, so you learn them as you go",
        default=True,
    )
    bpy.types.Scene.buddy_tour_started = BoolProperty(
        name="Donut tour started",
        description="Whether the Day 1 Donut Tour is showing in the panel",
        default=False,
    )
    bpy.types.Scene.buddy_tour_epoch = IntProperty(
        name="Donut tour start time",
        description="When the donut tour was started (whole seconds - "
                    "a float property cannot hold a time this big "
                    "exactly), so the picture step can prove the "
                    "picture was taken during it",
        default=0,
    )
    bpy.types.WindowManager.buddy_ask = StringProperty(
        name="Ask the expert",
        description="Ask the AI expert anything about your scene, in "
                    "your own words",
        default="",
    )
    bpy.types.WindowManager.buddy_answer = StringProperty(
        name="Expert answer", default="")
    bpy.types.WindowManager.buddy_suggested = StringProperty(
        name="Expert suggested button", default="")
    bpy.types.WindowManager.buddy_agent = BoolProperty(
        name="Let the expert do it",
        description="On: the expert answers with a plan of steps you "
                    "can run, so it does the work in Blender for you. "
                    "Off: it only advises",
        default=True)
    bpy.types.WindowManager.buddy_plan = StringProperty(
        name="Expert plan", default="")
    bpy.types.WindowManager.buddy_plan_summary = StringProperty(
        name="Expert plan summary", default="")
    bpy.types.WindowManager.buddy_plan_report = StringProperty(
        name="Expert plan report", default="")
    bpy.types.WindowManager.buddy_plan_retried = StringProperty(
        name="Expert plan replanned", default="")
    global _EXPERT_HANDLE
    try:
        _EXPERT_HANDLE = bpy.types.SpaceView3D.draw_handler_add(
            _draw_expert_overlay, (), "WINDOW", "POST_PIXEL")
    except Exception:
        _EXPERT_HANDLE = None


def unregister():
    global _EXPERT_HANDLE
    if _EXPERT_HANDLE is not None:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(
                _EXPERT_HANDLE, "WINDOW")
        except Exception:
            pass
        _EXPERT_HANDLE = None
    for attr in ("buddy_query", "buddy_show_real", "buddy_ask",
                 "buddy_answer", "buddy_suggested", "buddy_agent",
                 "buddy_plan", "buddy_plan_summary", "buddy_plan_report",
                 "buddy_plan_retried"):
        if hasattr(bpy.types.WindowManager, attr):
            delattr(bpy.types.WindowManager, attr)
    for attr in ("buddy_tour_started", "buddy_tour_epoch"):
        if hasattr(bpy.types.Scene, attr):
            delattr(bpy.types.Scene, attr)
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
