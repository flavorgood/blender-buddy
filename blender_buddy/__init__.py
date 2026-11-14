"""
Blender Buddy - Blender in plain words (prototype 0.8)

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
import filecmp
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
from bpy.types import AddonPreferences, Menu, Operator, Panel, WorkSpaceTool

bl_info = {
    "name": "Blender Buddy - Blender in Plain Words",
    "author": "Blender Buddy prototype",
    "version": (3, 2, 0),
    "blender": (4, 2, 0),
    "location": "3D Viewport > Sidebar (N key) > Blender Buddy tab",
    "description": "Put the power in the hands of average people who can't spend 10k hours learning a skill: Blender "
                   "redesigned around the job you're doing - every tool "
                   "visible, searchable in your own words, taught by "
                   "doing real projects, with your own AI expert.",
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

    # -- 2. Move around & find things -----------------------------------------
    dict(id="look_at_picked", section="2. Move around & find things",
         plain="Bring what I picked into view",
         does="Centres the view on the thing you picked and zooms in on it. The rescue button when something is lost off-screen. No number pad? This button is that key.",
         real="Frame Selected", key="Numpad .", icon="",
         kind="op", target="view3d.view_selected", words="view selected frame jump zoom centre picked lost find where"),
    dict(id="see_everything", section="2. Move around & find things",
         plain="See everything at once",
         does="Zooms the big window so every thing in the scene fits in view. The first thing to press when you feel lost.",
         real="Frame All", key="Home", icon="",
         kind="op", target="view3d.view_all", words="view all frame zoom everything lost find whole scene"),
    dict(id="find_everything", section="2. Move around & find things",
         plain="Find everything in my scene",
         does="Unhides anything that got hidden and brings the whole scene into view, so a lost thing shows up. The full list of your things is always the Outliner, at the top-right.",
         real="Unhide All + Frame All", key="", icon="",
         kind="custom", target="find_everything", words="lost hidden find where object outliner list missing gone"),
    dict(id="look_camera", section="2. Move around & find things",
         plain="Look through the camera",
         does="Shows exactly what the camera sees - which is exactly what your picture will be. The framed edge is the edge of the picture.",
         real="Camera View", key="Numpad 0", icon="",
         kind="op", target="view3d.view_camera", words="camera view through picture frame shot"),
    dict(id="camera_here", section="2. Move around & find things",
         plain="Move the camera to what I'm looking at",
         does="Puts the camera where your eye is right now, pointing the way you're looking - the easy way to line up a shot. Adds a camera first if the scene has none.",
         real="Align Camera to View", key="", icon="",
         kind="custom", target="camera_here", words="camera align view aim shot position picture frame"),
    dict(id="walk_mode", section="2. Move around & find things",
         plain="Walk through your scene",
         does="Walk about inside your scene like a game: mouse looks around, W A S D walk, E and Q go up and down. Click or press Enter when you're done, Esc to jump back.",
         real="Walk Navigation", key="", icon="",
         kind="op", target="view3d.walk", words="walk fly navigate game wasd first person inside look around"),
    dict(id="look_front", section="2. Move around & find things",
         plain="Look at it from the front",
         does="Puts your eye square in front of the scene, like looking at a photo of it. The plain way, without the number pad: View menu, Viewpoint, Front.",
         real="Front View", key="Numpad 1", icon="",
         kind="op", target="view3d.view_axis", args={"type": "FRONT"}, words="front view look direction"),
    dict(id="look_top", section="2. Move around & find things",
         plain="Look at it from above",
         does="Puts your eye directly overhead, like looking down at a map or a floor plan. Without the number pad: View menu, Viewpoint, Top.",
         real="Top View", key="Numpad 7", icon="",
         kind="op", target="view3d.view_axis", args={"type": "TOP"}, words="top view above overhead map plan"),
    dict(id="look_side", section="2. Move around & find things",
         plain="Look at it from the side",
         does="Puts your eye square on the right-hand side of the scene. Without the number pad: View menu, Viewpoint, Right.",
         real="Right View", key="Numpad 3", icon="",
         kind="op", target="view3d.view_axis", args={"type": "RIGHT"}, words="side right view look direction"),

    # -- 3. Move & size it ----------------------------------------------------
    dict(id="tool_pick", section="3. Move it & size it",
         plain="Pick things with the mouse",
         does="The normal mouse. Click a thing to pick it; everything else works on the thing you picked.",
         real="Select Box tool", key="W", icon="",
         kind="tool", target="builtin.select_box", words="select choose click cursor"),
    dict(id="tool_move", section="3. Move it & size it",
         plain="Move it around",
         does="Drag the picked thing to a new place. The coloured arrows move it one way at a time.",
         real="Move tool", key="G", icon="",
         kind="tool", target="builtin.move", needs="object", words="drag place position shift"),
    dict(id="tool_turn", section="3. Move it & size it",
         plain="Turn it",
         does="Spin the picked thing around, like turning a chair to face another way.",
         real="Rotate tool", key="R", icon="",
         kind="tool", target="builtin.rotate", needs="object", words="rotate spin angle face"),
    dict(id="tool_size", section="3. Move it & size it",
         plain="Make it bigger or smaller",
         does="Stretch or shrink the picked thing. Drag outwards for bigger, inwards for smaller.",
         real="Scale tool", key="S", icon="",
         kind="tool", target="builtin.scale", needs="object", words="scale resize stretch shrink grow"),
    dict(id="copy_it", section="3. Move it & size it",
         plain="Make a copy of it",
         does="A second one, exactly the same. The copy is picked, so move it where you want it.",
         real="Duplicate", key="Shift+D", icon="",
         kind="custom", target="duplicate", needs="object", words="duplicate clone another second"),
    dict(id="throw_away", section="3. Move it & size it",
         plain="Throw it away",
         does="Deletes the picked thing completely. Ctrl+Z brings it back if you change your mind.",
         real="Delete", key="Delete", icon="TRASH",
         kind="custom", target="delete_object", needs="object", words="delete remove bin trash undo"),

    # -- 4. Shape it ----------------------------------------------------------
    dict(id="start_shaping", section="4. Shape it",
         plain="Start shaping it",
         does="Switches from moving whole things to changing one thing's shape - its corners, edges and faces. Press again (or the same key) to go back.",
         real="Edit Mode", key="Tab", icon="MESH_DATA",
         kind="mode", target="EDIT", needs="object", words="edit mode change shape points faces mesh"),
    dict(id="pull_face", section="4. Shape it",
         plain="Pull a face out (or push it in)",
         does="The main building move in Blender. Pick a flat face, then drag: the shape grows out there. Houses, boxes, handles - all built this way.",
         real="Extrude Region", key="E", icon="",
         kind="op", target="mesh.extrude_region_move", needs="edit", words="extrude grow lengthen extend taller push"),
    dict(id="inset_face", section="4. Shape it",
         plain="Make a smaller face inside a face",
         does="Draws a new, smaller face inside the one you picked - like outlining a window or a panel before you push it in or pull it out.",
         real="Inset Faces", key="I", icon="",
         kind="op", target="mesh.inset", needs="edit", words="panel window inset border frame"),
    dict(id="round_edge", section="4. Shape it",
         plain="Round off a sharp edge",
         does="Real things are almost never razor sharp. This softens a picked edge or corner so it catches the light like a real object.",
         real="Bevel", key="Ctrl+B", icon="",
         kind="op", target="mesh.bevel", needs="edit", words="bevel round soften edge corner smooth sharp"),
    dict(id="loop_cut", section="4. Shape it",
         plain="Add a ring of edges around it",
         does="Slices a new ring all the way around the shape, so you can shape one part of it - like adding a crease line.",
         real="Loop Cut", key="Ctrl+R", icon="",
         kind="tool", target="builtin.loop_cut", needs="edit", words="slice ring crease cut around"),
    dict(id="knife", section="4. Shape it",
         plain="Draw a cut with the mouse",
         does="Click point to point to draw your own cut lines on the surface, exactly where you want them. Enter finishes the cut.",
         real="Knife tool", key="K", icon="",
         kind="tool", target="builtin.knife", needs="edit", words="cut draw line slice freehand"),
    dict(id="split_faces", section="4. Shape it",
         plain="Split faces into smaller faces",
         does="Chops each picked face into four smaller ones, giving you more points to shape with. Use it where you need more detail.",
         real="Subdivide", key="right-click menu", icon="",
         kind="op", target="mesh.subdivide", needs="edit", words="subdivide more detail split grid"),
    dict(id="fill_face", section="4. Shape it",
         plain="Fill in a missing face",
         does="Pick the edges around a hole and this covers it with a new face, like patching a gap.",
         real="Make Face", key="F", icon="",
         kind="op", target="mesh.edge_face_add", needs="edit", words="face fill hole patch cover gap"),

    # -- 5. Copy & combine ----------------------------------------------------
    dict(id="mirror_it", section="5. Copy it & combine it",
         plain="Copy it, flipped, to the other side",
         does="Build one side and this keeps an identical flipped copy on the other side - faces, cars, tables. Change one side, the other follows.",
         real="Mirror modifier", key="-", icon="MODIFIER",
         kind="modifier", target="MIRROR", needs="object", words="mirror flip symmetry other side both sides"),
    dict(id="row_of_them", section="5. Copy it & combine it",
         plain="Repeat it in a row",
         does="Makes evenly spaced copies in a line: fence posts, stairs, windows, teeth on a gear.",
         real="Array modifier", key="-", icon="MODIFIER",
         kind="modifier", target="ARRAY", needs="object", words="array repeat row pattern fence steps copies"),
    dict(id="glue_together", section="5. Copy it & combine it",
         plain="Glue picked things into one thing",
         does="Turns everything you picked into a single object, so it moves and saves as one piece.",
         real="Join", key="Ctrl+J", icon="",
         kind="op", target="object.join", needs="object", words="join merge combine together one"),
    dict(id="cut_hole", section="5. Copy it & combine it",
         plain="Cut one shape out of another",
         does="Pick TWO things: first the thing to cut into, then the thing doing the cutting (pick the cutter LAST). The cutter's shape is removed - holes, slots, doorways.",
         real="Boolean Difference", key="-", icon="",
         kind="custom", target="boolean_cut", needs="two", words="boolean hole cut out remove drill doorway slot subtract make a hole punch"),

    # -- 6. Make it look right -------------------------------------------------
    dict(id="make_smoother", section="6. Make it look right",
         plain="Make it smoother & rounder",
         does="Softens and rounds the whole shape by itself. Blocky things start to look carved or moulded. Safe: removing it brings the blocky shape back.",
         real="Subdivision Surface modifier", key="Ctrl+1", icon="MODIFIER",
         kind="modifier", target="SUBSURF", needs="object", words="subdivision smooth round soften catmull"),
    dict(id="give_thickness", section="6. Make it look right",
         plain="Give a flat sheet some thickness",
         does="A flat sheet becomes a real slab with sides - paper becomes card, a surface becomes a wall or a lid.",
         real="Solidify modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SOLIDIFY", needs="object", words="solidify thick wall slab hollow shell"),
    dict(id="round_all_edges", section="6. Make it look right",
         plain="Round ALL its edges a little",
         does="Like 'round off a sharp edge', but for the whole thing at once, without picking edges one by one.",
         real="Bevel modifier", key="-", icon="MODIFIER",
         kind="modifier", target="BEVEL", needs="object", words="bevel round edges all soften"),
    dict(id="look_smooth", section="6. Make it look right",
         plain="Make it LOOK smooth (not blocky)",
         does="Only changes how light falls on it - the shape stays the same, but faces stop looking like flat panels. Balls and curves want this.",
         real="Shade Smooth", key="right-click menu", icon="",
         kind="op", target="object.shade_smooth", needs="object", words="shade smooth shading faceted blocky light"),
    dict(id="look_flat", section="6. Make it look right",
         plain="Make it look flat & crisp",
         does="The opposite: every face looks flat and distinct, like cut metal or a gemstone.",
         real="Shade Flat", key="right-click menu", icon="",
         kind="op", target="object.shade_flat", needs="object", words="shade flat faceted crisp panels"),
    dict(id="give_colour", section="6. Make it look right",
         plain="Give it a colour",
         does="Paints the picked thing red, so you can see colours are just a coating you can change any time. Change the colour later in the Material tab.",
         real="Material", key="-", icon="MATERIAL",
         kind="custom", target="colour", needs="object", words="color colour paint material red coating"),

    # -- 7. Fix common problems -------------------------------------------------
    dict(id="fix_faces", section="7. Fix common problems",
         plain="Fix dark or inside-out faces",
         does="If parts of your model look strangely dark, the faces there are probably pointing the wrong way. This turns them all to face outwards.",
         real="Recalculate Normals", key="Shift+N", icon="",
         kind="op", target="mesh.normals_make_consistent", needs="edit", words="normals dark inside out wrong way shading black"),
    dict(id="join_close_points", section="7. Fix common problems",
         plain="Join points that sit on top of each other",
         does="Models often end up with doubled points in the same spot, which causes cracks and weird shading. This welds them into one.",
         real="Merge by Distance", key="M > By Distance", icon="",
         kind="op", target="mesh.remove_doubles", needs="edit", words="merge distance doubles weld duplicate points cracks"),
    dict(id="lock_size", section="7. Fix common problems",
         plain="Lock in its size & turn (fixes odd behaviour)",
         does="If you stretched something and other tools start behaving strangely, this tells Blender 'this size is normal now'. The shape does not change.",
         real="Apply Scale & Rotation", key="Ctrl+A", icon="",
         kind="custom", target="apply_transforms", needs="object", words="apply transform scale rotation weird behaves wrong"),
    dict(id="handle_middle", section="7. Fix common problems",
         plain="Put its grab-point in the middle",
         does="Every thing has a handle point it turns and mirrors around. If yours is off to one side, this puts it back in the middle of the shape.",
         real="Set Origin to Geometry", key="right-click menu", icon="",
         kind="custom", target="origin_middle", needs="object", words="origin pivot handle center middle turns around"),

    # -- 8. More shapes -------------------------------------------------------
    dict(id="add_faceted_ball", section="8. More shapes",
         plain="Add a faceted ball",
         does="A ball made of flat triangles - like a gem or a low-poly planet. Games and stylised models use this one.",
         real="Ico Sphere", key="Shift+A", icon="MESH_ICOSPHERE",
         kind="op", target="mesh.primitive_ico_sphere_add", words="icosphere gem dice low poly ball"),
    dict(id="add_circle", section="8. More shapes",
         plain="Add a flat circle",
         does="A flat disc or ring outline: plates, lids, wheels seen from the side.",
         real="Circle", key="Shift+A", icon="MESH_CIRCLE",
         kind="op", target="mesh.primitive_circle_add", words="disc plate lid round flat"),
    dict(id="add_grid", section="8. More shapes",
         plain="Add a sheet of squares",
         does="A flat sheet already divided into a grid - good for tiled floors, cloth, and land you want to sculpt into hills.",
         real="Grid", key="Shift+A", icon="",
         kind="op", target="mesh.primitive_grid_add", words="grid tiles floor ground landscape squares"),
    dict(id="add_bendy_line", section="8. More shapes",
         plain="Add a bendy line",
         does="A line with handles you pull to bend it. The start of ropes, wires, hoses - and of outlines you spin or grow tubes from.",
         real="Bezier Curve", key="Shift+A", icon="",
         kind="op", target="curve.primitive_bezier_curve_add", words="curve line rope wire hose bend path"),
    dict(id="add_sun", section="8. More shapes",
         plain="Add sunlight",
         does="Light that comes from one direction, like the sun: bright, even, with shadows. Every outdoor scene needs light or the picture is black.",
         real="Sun Light", key="Shift+A", icon="",
         kind="op", target="object.light_add", args={"type": "SUN"}, words="sun light bright day outside shadow"),
    dict(id="add_lamp", section="8. More shapes",
         plain="Add a lamp",
         does="A single point of light, like a bulb: glows in all directions and fades with distance.",
         real="Point Light", key="Shift+A", icon="",
         kind="op", target="object.light_add", args={"type": "POINT"}, words="point light bulb lamp glow indoor"),
    dict(id="add_camera", section="8. More shapes",
         plain="Add a camera",
         does="The picture Blender takes is seen through a camera. No camera, no picture. You move it like any other thing.",
         real="Camera", key="Shift+A", icon="",
         kind="op", target="object.camera_add", words="camera photo picture render view shot"),
    dict(id="add_handle", section="8. More shapes",
         plain="Add an invisible handle",
         does="An empty marker that shows in your workspace but never in the picture. Other things can be attached to it, aim at it, or mirror around it.",
         real="Empty (Plain Axes)", key="Shift+A", icon="",
         kind="op", target="object.empty_add", args={"type": "PLAIN_AXES"}, words="empty marker anchor target attach"),

    # -- 9. More ways to shape it ---------------------------------------------
    dict(id="smooth_points", section="9. More ways to shape it",
         plain="Smooth out lumps",
         does="Nudges the picked points toward even, so a bumpy surface calms down without changing what the thing is.",
         real="Smooth Vertices", key="right-click menu", icon="",
         kind="op", target="mesh.vertices_smooth", needs="edit", words="smooth lumps bumps even vertices relax"),
    dict(id="poke_face", section="9. More ways to shape it",
         plain="Poke a face into slices",
         does="Puts a new point in the middle of a face and joins it to every corner - pizza slices. The middle point is easy to pull up into a bump or spike.",
         real="Poke Faces", key="Alt+P", icon="",
         kind="op", target="mesh.poke", needs="edit", words="poke fan triangles centre center spike bump"),
    dict(id="make_triangles", section="9. More ways to shape it",
         plain="Turn faces into triangles",
         does="Splits every picked four-sided face into two triangles. Games and some 3D printing paths want everything in triangles.",
         real="Triangulate Faces", key="Ctrl+T", icon="",
         kind="op", target="mesh.quads_convert_to_tris", needs="edit", words="triangulate triangles tris games export"),
    dict(id="make_quads", section="9. More ways to shape it",
         plain="Turn triangles back into four-sided faces",
         does="The tidy-up opposite: joins pairs of triangles into four-sided faces where it can, which are easier to shape.",
         real="Tris to Quads", key="Alt+J", icon="",
         kind="op", target="mesh.tris_convert_to_quads", needs="edit", words="quads triangles tidy convert faces"),
    dict(id="erase_edges", section="9. More ways to shape it",
         plain="Erase edges without making a hole",
         does="Removes the picked edges and joins the faces around them into one bigger face. The surface stays whole.",
         real="Dissolve Edges", key="X > Dissolve", icon="",
         kind="op", target="mesh.dissolve_edges", needs="edit", words="dissolve remove edges merge faces hole"),
    dict(id="make_same_both_sides", section="9. More ways to shape it",
         plain="Make both sides the same",
         does="Copies one half of the shape over the other half, exactly. Fixes a face or a car body that drifted lopsided while you worked.",
         real="Symmetrize", key="Mesh menu", icon="",
         kind="op", target="mesh.symmetrize", needs="edit", words="symmetry symmetrize same both sides mirror lopsided"),
    dict(id="split_off", section="9. More ways to shape it",
         plain="Split the picked part off as its own thing",
         does="The part you've picked becomes a separate object you can move, colour or delete on its own - like cutting a piece off to work on it.",
         real="Separate by Selection", key="P", icon="",
         kind="custom", target="separate_piece", needs="edit", words="separate split part own object detach"),

    # -- 10. The rest of the modifiers -----------------------------------------
    dict(id="simplify_faces", section="10. Every other modifier",
         plain="Use fewer faces (make it lighter)",
         does="Simplifies the shape so it has fewer faces: faster to work with and what games want. Half strength to start - push it too far and detail melts.",
         real="Decimate modifier", key="-", icon="MODIFIER",
         kind="modifier", target="DECIMATE", needs="object", words="decimate simplify fewer faces lighter games low poly"),
    dict(id="crisp_edges_mod", section="10. Every other modifier",
         plain="Keep edges crisp where smoothing went mushy",
         does="Tells Blender 'this edge is a real edge' - smoothed shapes keep their sharp corners instead of looking melted.",
         real="Edge Split modifier", key="-", icon="MODIFIER",
         kind="modifier", target="EDGE_SPLIT", needs="object", words="edge split crisp sharp corners hard"),
    dict(id="wireframe_it", section="10. Every other modifier",
         plain="Turn it into its wire skeleton",
         does="The solid becomes just its frame of edges, like a birdcage or a wire model. Great for cages, grilles and sci-fi panels.",
         real="Wireframe modifier", key="-", icon="MODIFIER",
         kind="modifier", target="WIREFRAME", needs="object", words="wireframe cage skeleton grille frame edges"),
    dict(id="build_up", section="10. Every other modifier",
         plain="Build it up piece by piece (for animation)",
         does="Faces appear one after another as time passes - press Play in the animation section and watch it grow.",
         real="Build modifier", key="-", icon="MODIFIER",
         kind="modifier", target="BUILD", needs="object", words="build appear grow animation faces time"),
    dict(id="rebuild_blocks", section="10. Every other modifier",
         plain="Rebuild it from fresh, even blocks",
         does="Throws away a messy inside and rebuilds the shape from clean even blocks. The standard rescue for models that came from scans or other programs.",
         real="Remesh modifier", key="-", icon="MODIFIER",
         kind="modifier", target="REMESH", needs="object", words="remesh rebuild clean even blocks scan fix messy"),
    dict(id="spin_shape", section="10. Every other modifier",
         plain="Spin a flat outline into a round thing",
         does="Draw half the outline of a vase, bottle or bowl as a flat shape, and this spins it around into the full round object.",
         real="Screw modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SCREW", needs="object", words="screw spin lathe vase bottle bowl round outline"),
    dict(id="grow_skin", section="10. Every other modifier",
         plain="Grow skin over a skeleton",
         does="Join points into a stick figure or a branching line, and this grows a smooth skin over it - branches, roots, fingers, tubes.",
         real="Skin modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SKIN", needs="object", words="skin branch root tube skeleton grow"),
    dict(id="all_triangles_mod", section="10. Every other modifier",
         plain="Turn every face into a triangle, for good",
         does="Same as the shaping version, but as a standing rule on the whole thing, including parts you add later.",
         real="Triangulate modifier", key="-", icon="MODIFIER",
         kind="modifier", target="TRIANGULATE", needs="object", words="triangulate triangles export games all faces"),
    dict(id="weld_points", section="10. Every other modifier",
         plain="Weld points that almost touch",
         does="Points that nearly sit on top of each other become one point, as a standing rule - seams and splits close up.",
         real="Weld modifier", key="-", icon="MODIFIER",
         kind="modifier", target="WELD", needs="object", words="weld merge points close seam distance"),
    dict(id="squash_shape", section="10. Every other modifier",
         plain="Squash it toward a ball, tube or box",
         does="Pulls the whole shape part-way toward a simple form. Half-squash a box toward a ball and you get a cushion.",
         real="Cast modifier", key="-", icon="MODIFIER",
         kind="modifier", target="CAST", needs="object", words="cast squash sphere ball cylinder box cushion shape"),
    dict(id="soften_a_bit", section="10. Every other modifier",
         plain="Soften bumps a little",
         does="A gentle smoothing over the whole thing that keeps its size and shape. The mildest of the three smoothers here.",
         real="Smooth modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SMOOTH", needs="object", words="smooth soften bumps gentle modifier"),
    dict(id="soften_keep_size", section="10. Every other modifier",
         plain="Soften it but keep its size",
         does="Smooths like the others, then puffs the shape back to the size it was, so it doesn't shrink while it softens.",
         real="Corrective Smooth modifier", key="-", icon="MODIFIER",
         kind="modifier", target="CORRECTIVE_SMOOTH", needs="object", words="corrective smooth keep size shrink soften"),
    dict(id="soften_even", section="10. Every other modifier",
         plain="Smooth it very evenly",
         does="The strongest, most even smoother of the three. It can shrink the shape a little - that's normal for this one.",
         real="Laplacian Smooth modifier", key="-", icon="MODIFIER",
         kind="modifier", target="LAPLACIANSMOOTH", needs="object", words="laplacian smooth even shrink strong"),
    dict(id="bend_twist", section="10. Every other modifier",
         plain="Twist it, bend it, taper it or stretch it",
         does="Four big shape tricks in one: it starts as a twist. Open the Modifier list (wrench tab) and the same entry can bend, taper or stretch instead.",
         real="Simple Deform modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SIMPLE_DEFORM", needs="object", words="simple deform twist bend taper stretch"),
    dict(id="ripples", section="10. Every other modifier",
         plain="Add ripples, like water",
         does="A wave passes through the shape and can move over time - cloth in wind, water surfaces, wobbly signs.",
         real="Wave modifier", key="-", icon="MODIFIER",
         kind="modifier", target="WAVE", needs="object", words="wave ripple water wind move"),
    dict(id="push_with_picture", section="10. Every other modifier",
         plain="Push the surface around with a picture",
         does="The light and dark of a picture pushes the surface out and in - how you get hammered metal, bark, or a face from a height photo. It needs a picture texture set up first.",
         real="Displace modifier", key="-", icon="MODIFIER",
         kind="modifier", target="DISPLACE", needs="object", words="displace picture texture height bumps push surface"),
    dict(id="wrap_onto", section="10. Every other modifier",
         plain="Wrap it tight onto another thing",
         does="Drapes this shape onto the surface of another one, like a sticker pulled tight over a bottle. The other thing is chosen in the Modifier list.",
         real="Shrinkwrap modifier", key="-", icon="MODIFIER",
         kind="modifier", target="SHRINKWRAP", needs="object", words="shrinkwrap wrap drape sticker surface onto"),
    dict(id="bend_along_line", section="10. Every other modifier",
         plain="Bend it along a bendy line",
         does="The shape follows a bendy line you drew (section 7 adds one). Pick the line in the Modifier list and the shape curves along it - roads, hoses, roller-coasters.",
         real="Curve modifier", key="-", icon="MODIFIER",
         kind="modifier", target="CURVE", needs="object", words="curve bend along line path follow road hose"),
    dict(id="fix_hard_shading", section="10. Every other modifier",
         plain="Fix shading on hard, man-made shapes",
         does="Cars, guns, machines: this keeps flat faces flat and edges crisp while curved parts shade smoothly - the standard fix for weird dark smudges on hard models.",
         real="Weighted Normal modifier", key="-", icon="MODIFIER",
         kind="modifier", target="WEIGHTED_NORMAL", needs="object", words="weighted normal shading hard surface crisp smudge fix"),
    dict(id="make_cloth", section="10. Every other modifier",
         plain="Make it behave like cloth",
         does="Flags, curtains, tablecloths: the shape falls, folds and flaps when you press Play. Works best on the grid sheet from section 7, held at one edge.",
         real="Cloth (physics)", key="-", icon="MODIFIER",
         kind="modifier", target="CLOTH", needs="object", words="cloth fabric flag curtain physics fall"),
    dict(id="make_jelly", section="10. Every other modifier",
         plain="Make it soft & wobbly, like jelly",
         does="The shape squashes and bounces like something soft when you press Play and it lands or is hit.",
         real="Soft Body (physics)", key="-", icon="MODIFIER",
         kind="modifier", target="SOFT_BODY", needs="object", words="soft body jelly wobble squash bounce physics"),
    dict(id="make_bounce_wall", section="10. Every other modifier",
         plain="Make physics things bounce off it",
         does="By itself it does nothing you can see - it turns this thing into a solid wall/floor for cloth and other physics things to land on.",
         real="Collision (physics)", key="-", icon="MODIFIER",
         kind="modifier", target="COLLISION", needs="object", words="collision bounce physics wall floor solid"),
    dict(id="add_particles", section="10. Every other modifier",
         plain="Cover it with particles",
         does="Sprouts lots of small copies or hairs from the surface: grass, fur, sparks, dust, rain. What each particle looks like is set in the Particle tab.",
         real="Particle System", key="-", icon="MODIFIER",
         kind="modifier", target="PARTICLE_SYSTEM", needs="object", words="particles hair fur grass sparks rain dust"),

    # -- 11. Sculpt & paint -----------------------------------------------------
    dict(id="start_sculpting", section="11. Sculpt it & paint it",
         plain="Start sculpting (shape it like clay)",
         does="Instead of moving corners one by one, you push and pull the surface with brushes, like clay. Needs a shape picked. Press it again to stop.",
         real="Sculpt Mode", key="Ctrl+Tab", icon="",
         kind="mode", target="SCULPT", needs="object", words="sculpt clay brush push pull smooth draw mode"),
    dict(id="paint_it", section="11. Sculpt it & paint it",
         plain="Paint colour straight onto it",
         does="Paint with the mouse directly on the surface - each point of the shape holds its own colour, like painting a figure by hand.",
         real="Vertex Paint Mode", key="Ctrl+Tab", icon="",
         kind="mode", target="VERTEX_PAINT", needs="object", words="vertex paint colour color brush direct surface"),
    dict(id="paint_picture", section="11. Sculpt it & paint it",
         plain="Paint a picture onto its skin",
         does="Paints onto a picture that is wrapped around the shape - how game characters get their detailed skins. The shape needs a picture set up first.",
         real="Texture Paint Mode", key="Ctrl+Tab", icon="",
         kind="mode", target="TEXTURE_PAINT", needs="object", words="texture paint image skin picture wrap"),

    # -- 12. Animate it ---------------------------------------------------------
    dict(id="remember_pose", section="12. Animate it",
         plain="Remember where it is right now",
         does="This is how all animation works: you remember a thing's place at one moment, move it, remember again at a later moment - and Blender fills in the movement between. One memory is called a keyframe.",
         real="Insert Keyframe (place, turn, size)", key="I", icon="",
         kind="custom", target="keyframe", needs="object", words="keyframe remember animation moment move position record"),
    dict(id="go_to_start", section="12. Animate it",
         plain="Go back to the start",
         does="Jumps the play line back to frame 1, the beginning of the animation.",
         real="Jump to Start", key="Shift+Down", icon="",
         kind="op", target="screen.frame_jump", args={"end": False}, words="start beginning frame jump rewind"),
    dict(id="play_it", section="12. Animate it",
         plain="Play / stop what moves",
         does="Plays the animation so you can watch it. Press again (or the space bar) to stop.",
         real="Play Animation", key="Space", icon="",
         kind="op", target="screen.animation_play", words="play stop animation watch run space"),

    # -- 13. Finish it ----------------------------------------------------------
    dict(id="take_picture", section="13. Finish: picture, save, send it out",
         plain="Take the picture",
         does="Makes the final image, seen through the camera, with real light and shadow. If no place to save was ever chosen, the picture lands in your home folder as blender_buddy_picture.png.",
         real="Render Image", key="F12", icon="",
         kind="custom", target="render_picture", words="render picture image photo final camera f12"),
    dict(id="save_work", section="13. Finish: picture, save, send it out",
         plain="Save your work",
         does="Saves everything so you can close Blender and come back. A first save lands in your home folder as blender_buddy_my_model.blend.",
         real="Save File", key="Ctrl+S", icon="",
         kind="custom", target="save_work", words="save file keep store blend"),
    dict(id="send_web", section="13. Finish: picture, save, send it out",
         plain="Send it out for web & games (.glb)",
         does="Writes the whole scene as one .glb file in your home folder (blender_buddy_model.glb) - the format websites, AR and most game tools accept.",
         real="Export glTF/GLB", key="-", icon="",
         kind="custom", target="export_glb", words="export glb gltf web games ar send out share"),
    dict(id="send_print", section="13. Finish: picture, save, send it out",
         plain="Send it out for 3D printing (.stl)",
         does="Writes the shapes as an .stl file in your home folder (blender_buddy_model.stl) - the format 3D printers and printing services take.",
         real="Export STL", key="-", icon="",
         kind="custom", target="export_stl", words="export stl 3d printing printer send out"),
    dict(id="send_obj", section="13. Finish: picture, save, send it out",
         plain="Send it out the classic way (.obj)",
         does="Writes an .obj file in your home folder (blender_buddy_model.obj) - the oldest, most widely accepted model format of all.",
         real="Export OBJ", key="-", icon="",
         kind="custom", target="export_obj", words="export obj classic old format send out"),
    dict(id="centre_world", section="13. Finish: picture, save, send it out",
         plain="Put it back in the middle of the world",
         does="Moves the picked thing to position zero - the centre crossroads where new things appear. Handy when something got lost far away.",
         real="Set Location to 0,0,0", key="Alt+G", icon="",
         kind="custom", target="centre_world", needs="object", words="centre center middle world zero lost move back origin"),
    dict(id="make_permanent", section="13. Finish: picture, save, send it out",
         plain="Make its add-on changes permanent",
         does="Bakes every modifier (sections 5 and 9) into the real shape, so what you see is exactly what exports. After this they can't be tweaked as modifiers - Ctrl+Z still undoes it.",
         real="Apply All Modifiers", key="-", icon="",
         kind="custom", target="apply_modifiers", needs="object", words="apply modifiers permanent bake final real"),

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


# ----------------------------------------------------------------------------
# The anti-stale self-check. Buddy's law (owner, 2026-11-12): Buddy is a
# Blender expert that must not go stale across Blender updates. The big
# index already re-learns itself from the running Blender on every
# launch. The curated buttons are the part written against one era of
# Blender - so on first use in any session, every curated action is
# checked against THIS Blender: the operator, modifier type, mode or
# toolbar tool it points at must still exist here. Anything that
# changed is hidden from the drawers and the search, and named in
# plain words in the panel, instead of failing silently in a
# beginner's hands. A check that cannot be made (a Blender too
# restructured to ask) counts as fine - Buddy never hides a tool on
# a guess.
# ----------------------------------------------------------------------------

_STALE_CACHE = None


def _enum_items(idname, prop):
    """The valid values of an operator's enum property, or None when
    this Blender can't be asked that way."""
    try:
        rna = _resolve_op(idname).get_rna_type()
        return set(rna.properties[prop].enum_items.keys())
    except Exception:
        return None


def _known_tool_ids():
    """Every toolbar tool id in the 3D View on this Blender, read from
    the same tool table Blender's own toolbar draws - or None when it
    can't be read."""
    try:
        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper

        def _walk(cls):
            for sub in cls.__subclasses__():
                yield sub
                yield from _walk(sub)

        def _collect(node, out):
            if node is None:
                return
            if hasattr(node, "idname"):
                out.add(node.idname)
            elif isinstance(node, (list, tuple)):
                for child in node:
                    _collect(child, out)

        ids = set()
        for sub in _walk(ToolSelectPanelHelper):
            if sub.__name__ == "VIEW3D_PT_tools_active":
                for entry in sub.tools_all():
                    _collect(entry, ids)
        return ids or None
    except Exception:
        return None


def _check_action(act, op_idnames=None, modifier_types=None,
                  mode_names=None, tool_ids=None):
    """None when the tool behind this action still exists in the
    running Blender; otherwise a short plain reason it does not."""
    kind = act.get("kind")
    target = act.get("target", "")
    if kind == "op":
        # bpy.ops will happily invent a wrapper for an operator that
        # does not exist - it only fails when called. The live index
        # (built from this Blender's real registry) is the truth.
        if op_idnames is not None and target not in op_idnames:
            return "the tool behind it is not in this Blender"
    elif kind == "modifier":
        if modifier_types is not None and target not in modifier_types:
            return "this kind of modifier is not in this Blender"
    elif kind == "mode":
        if mode_names is not None and target not in mode_names:
            return "this mode is not in this Blender"
    elif kind == "tool":
        if tool_ids is not None and target not in tool_ids:
            return "this toolbar tool is not in this Blender"
    elif kind == "custom":
        if target not in _CUSTOM:
            return "Buddy's own helper for it is missing"
    else:
        return "Buddy doesn't know how to run it"
    return None


def _self_check(actions=None):
    """Check actions (default: the whole catalogue) against this
    Blender. Returns [{'id', 'plain', 'reason'}] for the ones that no
    longer match it."""
    acts = ACTIONS if actions is None else actions
    op_idnames = {e["idname"] for e in build_index()}
    modifier_types = _enum_items("object.modifier_add", "type")
    mode_names = _enum_items("object.mode_set", "mode")
    tool_ids = _known_tool_ids()
    stale = []
    for act in acts:
        reason = _check_action(act, op_idnames, modifier_types,
                               mode_names, tool_ids)
        if reason:
            stale.append({"id": act["id"], "plain": act["plain"],
                          "reason": reason})
    return stale


def _stale_map():
    """{action_id: reason} for every curated action that changed in
    this Blender. Computed once per session, then cached."""
    global _STALE_CACHE
    if _STALE_CACHE is None:
        _STALE_CACHE = {s["id"]: s["reason"] for s in _self_check()}
    return _STALE_CACHE


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


def search_actions(query, available_only=False, context=None):
    """Loose search over the plain-words buttons. People describe the job
    their own way - synonyms, half-words, typos and all - and get ranked
    best matches instead of an all-or-nothing gate. Gibberish still
    returns nothing."""
    q, tokens = _query_tokens(query)
    if not tokens:
        return []
    scored = []
    stale = _stale_map()
    for pos, a in enumerate(ACTIONS):
        if a["id"] in stale:
            continue
        if available_only and not _action_available(
                a, context or bpy.context):
            continue
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


def _custom_find_everything(context):
    # The substance: nothing in the scene stays hidden. Framing the
    # whole scene afterwards is a view convenience - in a window
    # with no 3D view to frame (or a headless run) it just doesn't
    # happen; the unhide already did the finding.
    for obj in context.scene.objects:
        obj.hide_viewport = False
        try:
            obj.hide_set(False)
        except Exception:
            pass
    try:
        bpy.ops.view3d.view_all()
    except Exception:
        pass
    return {"FINISHED"}


def _custom_camera_here(context):
    scene = context.scene
    if scene.camera is None:
        bpy.ops.object.camera_add()
        scene.camera = context.object
    try:
        bpy.ops.view3d.camera_to_view()
    except Exception:
        pass
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
    "find_everything": _custom_find_everything,
    "camera_here": _custom_camera_here,
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
# Guided projects. The donut is the famous first Blender project -
# the Blender Guru's tutorial made it the rite of passage, because
# one small project touches almost every core skill. These packages
# TEACH it: each step tells the learner what to do, in plain words
# and real Blender controls, and ticks off only when the SCENE
# proves they did it (the object, the colour, the render are really
# there). Nothing here does the steps for them - a tour that does
# the work teaches nothing. (Each step still carries a reference
# build, "run", which the test suites use to prove the checks, and
# which generated the demo donut.)
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


# ----------------------------------------------------------------------------
# The Donut package, rebuilt as the follow-along companion to
# Blender Guru's NEW donut series - "Blender Donut Tutorial
# (2025)", taught in Blender 5.0. One step per part:
#   Part 1 (2026) - the basics, taught on a coffee cup
#   Part 2 Basic Modelling - the real mug, from a reference photo
#   Part 3 Basic Organic Modelling - icing that drips and hugs
#   Part 4 Basic Materials - plate, lattice, SSS, first picture
#   Part 5 Basic Texturing - photo textures as a three-map recipe
#   Part 6 Basic UV Unwrapping - seams on the mug, coffee foam
#   Part 7 How to Scatter in Blender 5.0 - Scatter on Surface
#   Part 8 The Basics of Lighting and Rendering - the finale
# The video teaches; these steps orient (which part, what he is
# about to do), verify (the tick is the scene's proof, never a
# button press) and rescue (the missing text names what your
# screen is still missing). The run functions are the reference
# builds the tests prove the checks against - the panel never
# offers them.
# ----------------------------------------------------------------------------

def _find_dough(context):
    """The dough ring: his name for it first, then the shape of
    it - a fat ring (a hole in the middle) that is not any of
    the scene's other named pieces."""
    named = _scene_obj(context, "Dough")
    if named is not None and named.type == "MESH":
        return named
    skip = {"Icing", "Sprinkles", "Plate", "Table", "Mug", "Cup",
            "Coffee Foam", "Mug Coffee", "Mug Handle"}
    for obj in context.scene.objects:
        if obj.type != "MESH" or obj.name in skip:
            continue
        if obj.name.startswith("Sprinkle"):
            continue
        if len(obj.data.vertices) < 300:
            continue
        if min(math.hypot(v.co.x, v.co.y)
               for v in obj.data.vertices) > 0.25:
            return obj
    return None


def _render_proof(context):
    """A picture exists because someone rendered: the Render
    Result still holds it, or a render file was written to the
    scene's output path during this tour."""
    img = bpy.data.images.get("Render Result")
    try:
        if img is not None and img.size[0] > 0 and img.has_data:
            return True
    except Exception:
        pass
    fp = context.scene.render.filepath
    if fp and fp.lower().endswith(".png"):
        target = bpy.path.abspath(fp)
        if os.path.exists(target):
            epoch = getattr(context.scene, "buddy_tour_epoch", 0)
            if epoch <= 0 or os.path.getmtime(target) >= epoch - 2:
                return True
    return False


def _sss_weight(obj):
    """The strongest subsurface (light sinking into food) on any
    of the object's materials - 0 when there is none."""
    best = 0.0
    if obj is None or obj.type != "MESH":
        return best
    for mat in obj.data.materials:
        if mat is None or not mat.use_nodes or mat.node_tree is None:
            continue
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None and "Subsurface Weight" in bsdf.inputs:
            best = max(best, float(
                bsdf.inputs["Subsurface Weight"].default_value))
    return best


def _build_dough_ring(context):
    """His dough: a PLUMP ring - fat tube, squashed a little,
    smoothed and subdivided - not the thin default torus."""
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
    return obj


def _build_icing(context, dough):
    """His real method (Part 3): the icing is the TOP of the
    dough itself, separated off, pulled down into drips, given
    thickness (Solidify, his 0.025), and shrink-wrapped onto
    the dough so it hugs instead of floating."""
    import bmesh
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
    # uneven amount - long drips in places, short in others.
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
    for mod in list(icing.modifiers):
        icing.modifiers.remove(mod)
    hug = icing.modifiers.new("Hug the Dough", "SHRINKWRAP")
    hug.target = dough
    hug.wrap_method = "NEAREST_SURFACEPOINT"
    hug.offset = 0.012
    thick = icing.modifiers.new("Icing Thickness", "SOLIDIFY")
    thick.thickness = 0.025
    sub = icing.modifiers.new("Smoother", "SUBSURF")
    sub.levels = 2
    icing.scale = (1.015, 1.015, 0.835)
    bpy.ops.object.select_all(action="DESELECT")
    icing.select_set(True)
    context.view_layer.objects.active = icing
    return icing


def _colour_dough(context, dough):
    """Golden baked dough WITH the pale fry line around its
    middle - and subsurface up, so it reads as food."""
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


def _tour_step_first_cup(context):
    # The new series teaches the whole workshop on a cup first -
    # and only when the scene is EXACTLY Blender's untouched
    # starter set is the starter trio cleared.
    objs = list(context.scene.objects)
    if {o.name for o in objs} <= {"Cube", "Camera", "Light"}:
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()
    import bmesh
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.40, depth=0.95, vertices=32,
        location=(1.95, 0.60, 0.06))
    cup = context.object
    cup.name = "Cup"
    # The opening (his 17:57 move): the top face goes away.
    bm = bmesh.new()
    bm.from_mesh(cup.data)
    bm.faces.ensure_lookup_table()
    top = [f for f in bm.faces if f.calc_center_median().z > 0.40]
    bmesh.ops.delete(bm, geom=top, context="FACES")
    bm.to_mesh(cup.data)
    bm.free()
    for poly in cup.data.polygons:
        poly.use_smooth = True
    walls = cup.modifiers.new("Cup Walls", "SOLIDIFY")
    walls.thickness = 0.035
    sub = cup.modifiers.new("Smoother", "SUBSURF")
    sub.levels = 2
    # His last move of Part 1 (27:11): save the file.
    if not bpy.data.filepath:
        bpy.ops.wm.save_as_mainfile(
            filepath=_home("blender_buddy_my_donut.blend"))


def _reference_image(context):
    """A small stand-in for the cup reference photo he links
    from the series page - a plain mug silhouette, drawn in
    pixels here (no downloads)."""
    img = bpy.data.images.get("Cup Reference")
    if img is None:
        img = bpy.data.images.new("Cup Reference", 96, 96)
    w, h = 96, 96
    px = []
    for y in range(h):
        for x in range(w):
            inside = 28 <= x <= 62 and 18 <= y <= 80
            handle = (62 < x <= 74 and 34 <= y <= 62
                      and not (66 < x <= 70 and 40 <= y <= 56))
            if inside or handle:
                px.extend((0.45, 0.30, 0.20, 1.0))
            else:
                px.extend((0.92, 0.92, 0.94, 1.0))
    img.pixels.foreach_set(px)
    img.update()
    return img


def _tour_step_mug_reference(context):
    import bmesh
    # The reference photo, standing where he puts it - on show
    # in the scene, lined up behind the mug it teaches.
    img = _reference_image(context)
    bpy.ops.object.empty_add(type="IMAGE",
                             location=(1.95, 1.30, 0.35),
                             rotation=(math.pi / 2, 0, 0))
    ref = context.object
    ref.name = "Mug Reference"
    ref.data = img
    ref.empty_display_size = 1.1
    # The mug itself: a cylinder given rings, a profile, an
    # opening, walls - and a handle joined into it.
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.40, depth=0.95, vertices=48,
        location=(1.95, 0.60, 0.06))
    mug = context.object
    mug.name = "Mug"
    bm = bmesh.new()
    bm.from_mesh(mug.data)
    bm.edges.ensure_lookup_table()
    vertical = [e for e in bm.edges
                if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.5]
    bmesh.ops.subdivide_edges(bm, edges=vertical, cuts=5)
    bm.verts.ensure_lookup_table()
    for v in bm.verts:
        t = (v.co.z + 0.475) / 0.95
        f = 0.92 + 0.10 * math.sin(math.pi * max(0.0, min(1.0, t)))
        if t > 0.92:
            f *= 1.04          # a slight lip at the rim
        if t < 0.05:
            f *= 0.90          # the foot - his bottom lip
        v.co.x *= f
        v.co.y *= f
    bm.faces.ensure_lookup_table()
    top = [f for f in bm.faces if f.calc_center_median().z > 0.40]
    bmesh.ops.delete(bm, geom=top, context="FACES")
    bm.to_mesh(mug.data)
    bm.free()
    for poly in mug.data.polygons:
        poly.use_smooth = True
    walls = mug.modifiers.new("Mug Walls", "SOLIDIFY")
    walls.thickness = 0.03
    # The handle: a ring standing on edge, sunk into the wall.
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.17, minor_radius=0.035,
        major_segments=32, minor_segments=10,
        location=(2.42, 0.60, 0.12), rotation=(0, math.pi / 2, 0))
    handle = context.object
    bpy.ops.object.select_all(action="DESELECT")
    mug.select_set(True)
    handle.select_set(True)
    context.view_layer.objects.active = mug
    bpy.ops.object.join()
    mug = context.object
    mug.name = "Mug"
    _paint(mug, "Buddy Mug", (0.36, 0.21, 0.13, 1.0), roughness=0.4)


def _tour_step_icing_hug(context):
    # The folded-in mini-step: the plain ring itself. Part 3
    # assumes it (his series makes it on the way); if it is not
    # there yet, the reference builds it first.
    dough = _find_dough(context)
    if dough is None:
        dough = _build_dough_ring(context)
    _build_icing(context, dough)


def _tour_step_first_picture(context):
    from mathutils import Vector
    scene = context.scene
    dough = _find_dough(context)
    icing = _scene_obj(context, "Icing")
    if dough is None or icing is None:
        raise RuntimeError("The donut comes first - that is Part 3.")
    # The plate (Part 3's homework) and the table under it.
    if _scene_obj(context, "Plate") is None:
        bpy.ops.mesh.primitive_cylinder_add(
            radius=1.55, depth=0.06, location=(0, 0, -0.38))
        plate = context.object
        plate.name = "Plate"
        _paint(plate, "Buddy Plate", (0.93, 0.93, 0.95, 1.0),
               roughness=0.35)
    if _scene_obj(context, "Table") is None:
        bpy.ops.mesh.primitive_circle_add(
            vertices=48, radius=7.0, fill_type="NGON",
            location=(0, 0, -0.415))
        table = context.object
        table.name = "Table"
        _paint(table, "Buddy Table", (0.16, 0.14, 0.13, 1.0),
               roughness=0.9)
    # The Lattice: the whole donut bent gently out of round, so
    # it stops looking computer-perfect (his 8:29 move).
    if _scene_obj(context, "Lumpy") is None:
        lat_data = bpy.data.lattices.new("Lumpy")
        lat_data.points_u = 3
        lat_data.points_v = 3
        lat_data.points_w = 2
        lat = bpy.data.objects.new("Lumpy", lat_data)
        scene.collection.objects.link(lat)
        lat.location = (0, 0, 0)
        lat.scale = (3.1, 3.1, 1.15)
        rng = random.Random(7)
        for point in lat_data.points:
            point.co_deform.x += rng.uniform(-0.05, 0.05)
            point.co_deform.y += rng.uniform(-0.05, 0.05)
            point.co_deform.z += rng.uniform(-0.03, 0.03)
        for target in (dough, icing):
            mod = target.modifiers.new("Lumpy", "LATTICE")
            mod.object = lat
    # Materials with the food setting: subsurface above zero on
    # both dough and icing.
    _paint(icing, "Buddy Pink", (0.80, 0.30, 0.47, 1.0),
           roughness=0.18, subsurface=0.25)
    _colour_dough(context, dough)
    # The room, one light, the camera - then the first picture.
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
        direction = Vector((0.35, 0.1, -0.05)) - cam.location
        cam.rotation_euler = direction.to_track_quat(
            "-Z", "Y").to_euler()
        scene.camera = cam
    if not any(o.type == "LIGHT" for o in scene.objects):
        bpy.ops.object.light_add(type="SUN",
                                 location=(-3.0, -2.0, 3.0),
                                 rotation=(0.9, 0.25, -0.65))
        sun = context.object
        sun.data.energy = 2.2
    # The picture is written to a file as well as shown - the
    # same habit the picture button teaches, and the file is
    # the proof that survives everywhere.
    path = (scene.render.filepath or "").strip()
    if path in {"", "/tmp", "/tmp/"}:
        scene.render.filepath = _home("blender_buddy_picture.png")
    bpy.ops.render.render(write_still=True)


def _make_texture_set(name, rgb, seed, rough_mid):
    """Three small photo-like maps drawn in pixels here - a
    mottled colour map, a roughness map (data), and a normal
    map (data). No downloads; they stand in for his Poliigon
    textures. Saved as files and packed, so they travel with
    the scene."""
    folder = os.path.join(tempfile.gettempdir(),
                          "buddy_donut_textures")
    os.makedirs(folder, exist_ok=True)
    rng = random.Random(seed)
    size = 128
    cells = {}
    for gy in range(16):
        for gx in range(16):
            cells[(gx, gy)] = rng.uniform(-0.16, 0.16)

    def cell_noise(x, y):
        return cells[(x // 8, y // 8)]

    def build(kind):
        img = bpy.data.images.get(f"{name} {kind}")
        if img is None:
            img = bpy.data.images.new(f"{name} {kind}", size, size)
        px = []
        for y in range(size):
            for x in range(size):
                n = cell_noise(x, y) + rng.uniform(-0.03, 0.03)
                if kind == "Colour":
                    px.extend((max(0.0, rgb[0] * (1 + n)),
                               max(0.0, rgb[1] * (1 + n)),
                               max(0.0, rgb[2] * (1 + n)), 1.0))
                elif kind == "Roughness":
                    v = max(0.05, min(0.95, rough_mid + n))
                    px.extend((v, v, v, 1.0))
                else:  # Normal: mostly flat, gently bumpy
                    px.extend((0.5 + n * 0.6, 0.5 + n * 0.4, 1.0, 1.0))
        # Colours space FIRST: changing it afterwards throws the
        # pixels away (measured on 4.2.5 and 5.3 - the buffer
        # resets to black), which silently rendered every
        # textured surface black.
        want = "sRGB" if kind == "Colour" else "Non-Color"
        if img.colorspace_settings.name != want:
            img.colorspace_settings.name = want
        img.pixels.foreach_set(px)
        img.filepath_raw = os.path.join(
            folder, f"buddy_{name.lower().replace(' ', '_')}_"
                    f"{kind.lower()}.png")
        img.save()
        try:
            img.pack()
        except Exception:
            pass
        return img

    return {"colour": build("Colour"), "rough": build("Roughness"),
            "normal": build("Normal")}


def _apply_pbr(obj, tex, subsurface=0.0):
    """Wire a texture set into the object's material the way
    Part 5 teaches: colour into Base Color, roughness as data,
    a Normal Map node into the Normal socket."""
    mat = bpy.data.materials.get(f"Buddy {obj.name} Surface")
    if mat is None:
        mat = bpy.data.materials.new(f"Buddy {obj.name} Surface")
    mat.use_nodes = True
    nt = mat.node_tree
    for node in list(nt.nodes):
        nt.nodes.remove(node)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (300, 0)
    out.location = (560, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    if subsurface > 0 and "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = subsurface
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    nt.links.new(coord.outputs["UV"], mapping.inputs["Vector"])

    def tex_node(image, loc):
        node = nt.nodes.new("ShaderNodeTexImage")
        node.image = image
        node.location = loc
        nt.links.new(mapping.outputs["Vector"], node.inputs["Vector"])
        return node

    col = tex_node(tex["colour"], (0, 160))
    nt.links.new(col.outputs["Color"], bsdf.inputs["Base Color"])
    rgh = tex_node(tex["rough"], (0, -80))
    nt.links.new(rgh.outputs["Color"], bsdf.inputs["Roughness"])
    nrm = tex_node(tex["normal"], (0, -320))
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nmap.location = (240, -320)
    nt.links.new(nrm.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    obj.data.materials.clear()
    obj.data.materials.append(mat)


def _tour_step_real_surfaces(context):
    dough = _find_dough(context)
    icing = _scene_obj(context, "Icing")
    plate = _scene_obj(context, "Plate")
    table = _scene_obj(context, "Table")
    if None in (dough, icing, plate, table):
        raise RuntimeError("The scene comes first - that is Part 4.")
    _apply_pbr(table, _make_texture_set(
        "Table Wood", (0.30, 0.20, 0.13), 21, 0.8))
    _apply_pbr(plate, _make_texture_set(
        "Plate Ceramic", (0.90, 0.90, 0.92), 22, 0.3))
    _apply_pbr(dough, _make_texture_set(
        "Dough Crumb", (0.55, 0.32, 0.12), 23, 0.55),
        subsurface=0.3)
    _apply_pbr(icing, _make_texture_set(
        "Icing Glaze", (0.82, 0.32, 0.48), 24, 0.2),
        subsurface=0.25)


def _tour_step_unwrap_mug(context):
    import bmesh
    mug = _scene_obj(context, "Mug")
    if mug is None:
        raise RuntimeError("The mug comes first - that is Part 2.")
    # Seams: one line of edges down the back of the mug and the
    # ring of edges around its rim - the cuts his unwrap uses.
    bm = bmesh.new()
    bm.from_mesh(mug.data)
    bm.edges.ensure_lookup_table()
    for e in bm.edges:
        a, b = e.verts[0].co, e.verts[1].co
        mid = (a + b) / 2
        vertical = abs(a.z - b.z) > 0.05 and \
            math.hypot(a.x - b.x, a.y - b.y) < 0.05
        back = math.atan2(mid.y, mid.x) > 2.6 or \
            math.atan2(mid.y, mid.x) < -2.6
        rim = a.z > 0.40 and b.z > 0.40 and abs(a.z - b.z) < 0.05
        if (vertical and back) or rim:
            e.seam = True
    bm.to_mesh(mug.data)
    bm.free()
    if not mug.data.uv_layers:
        mug.data.uv_layers.new(name="UVMap")
    # The coffee itself: a foam disc just inside the rim, with
    # a material of its own.
    if _scene_obj(context, "Coffee Foam") is None:
        bpy.ops.mesh.primitive_circle_add(
            vertices=32, radius=0.34, fill_type="NGON",
            location=(1.95, 0.60, 0.49))
        foam = context.object
        foam.name = "Coffee Foam"
        _paint(foam, "Buddy Foam", (0.92, 0.85, 0.72, 1.0),
               roughness=0.5)


def _scatter_group():
    """Blender 5.0's own Scatter on Surface node group, from
    the essentials library every 5.x install ships. None on
    older Blender - the feature simply is not there."""
    existing = bpy.data.node_groups.get("Scatter on Surface")
    if existing is not None:
        return existing
    path = os.path.join(
        bpy.utils.system_resource("DATAFILES"), "assets", "nodes",
        "geometry_nodes_essentials.blend")
    if not os.path.exists(path):
        return None
    try:
        with bpy.data.libraries.load(path, link=False) as (src, dst):
            if "Scatter on Surface" not in src.node_groups:
                return None
            dst.node_groups = ["Scatter on Surface"]
    except Exception:
        return None
    return bpy.data.node_groups.get("Scatter on Surface")


def _tour_step_scatter(context):
    grp = _scatter_group()
    if grp is None:
        raise RuntimeError(
            "Scatter on Surface is one of Blender 5.0's new "
            "tools, and this copy of Blender does not have it. "
            "This step waits for Blender 5.0 or newer - every "
            "other step works on what you have.")
    icing = _scene_obj(context, "Icing")
    if icing is None:
        raise RuntimeError("Sprinkles need the icing first - "
                           "that is Part 3.")
    # Three sprinkle variants in their own collection - a rod,
    # a ball, a disc - each with its own bright colour.
    coll = bpy.data.collections.get("Sprinkle Types")
    if coll is None:
        coll = bpy.data.collections.new("Sprinkle Types")
        context.scene.collection.children.link(coll)

    def variant(name, build, rgba, spot):
        obj = _scene_obj(context, name)
        if obj is not None:
            return obj
        build(spot)
        obj = context.object
        obj.name = name
        for parent in list(obj.users_collection):
            parent.objects.unlink(obj)
        coll.objects.link(obj)
        _paint(obj, f"Buddy {name}", rgba, roughness=0.35)
        return obj

    def build_rod(spot):
        from mathutils import Matrix
        bpy.ops.mesh.primitive_uv_sphere_add(
            segments=12, ring_count=8, radius=1.0, location=spot)
        context.object.data.transform(
            Matrix.Diagonal((0.085, 0.017, 0.017, 1.0)))

    variant("Sprinkle Rod", build_rod,
            (0.35, 0.75, 0.70, 1.0), (4.5, 3.5, 0))
    variant("Sprinkle Ball",
            lambda s: bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions=2, radius=0.022, location=s),
            (0.95, 0.62, 0.72, 1.0), (4.8, 3.5, 0))
    variant("Sprinkle Disc",
            lambda s: bpy.ops.mesh.primitive_cylinder_add(
                radius=0.032, depth=0.012, vertices=16, location=s),
            (0.62, 0.52, 0.85, 1.0), (5.1, 3.5, 0))
    # The painted guide: a vertex group, weight on the icing's
    # top, nothing on its underside - painted the way he paints
    # it, here computed from the icing's own shape.
    vg = icing.vertex_groups.get("Sprinkles")
    if vg is None:
        vg = icing.vertex_groups.new(name="Sprinkles")
    top = [v.index for v in icing.data.vertices if v.co.z > 0.05]
    if top:
        vg.add(top, 1.0, "REPLACE")
    # The modifier itself - Blender 5.0's own scatter, pointed
    # at the collection, mixing variants, masked by the group.
    if not any(m.type == "NODES" and m.node_group is grp
               for m in icing.modifiers):
        mod = icing.modifiers.new("Scatter on Surface", "NODES")
        mod.node_group = grp
        try:
            inp = mod.properties.inputs
            inp.Socket_6.value = "Collection"   # Instance Type
            inp.Socket_7.value = coll           # Collection
            inp.Socket_17.value = True          # Pick Instance
            inp.Socket_30.value = "Amount"      # Density Method
            inp.Socket_31.value = 140           # Amount
            inp.Socket_39.value = True          # Randomize
            inp.Socket_35.value = (0.0, 0.0, 6.283)  # spin freely
            inp.Socket_29.value = True          # Masking on
            inp.Socket_2.attribute_name = "Sprinkles"  # the mask
        except Exception:
            pass  # the modifier + group are the proof; the
            # values are defaults a learner can match by hand


def _tour_step_final_picture(context):
    scene = context.scene
    # The finale's lighting build: the sun from Part 4 stays,
    # and two purpose-placed lights join it - a warm key and a
    # cool rim - so the picture is lit in layers.
    if _scene_obj(context, "Key Light") is None:
        bpy.ops.object.light_add(type="AREA",
                                 location=(2.5, -2.5, 3.0),
                                 rotation=(0.85, 0.0, 0.65))
        key = context.object
        key.name = "Key Light"
        key.data.energy = 250
        key.data.shape = "DISK"
        key.data.size = 2.0
        key.data.color = (1.0, 0.95, 0.88)
    if _scene_obj(context, "Rim Light") is None:
        bpy.ops.object.light_add(type="POINT",
                                 location=(-3.0, 2.5, 2.0))
        rim = context.object
        rim.name = "Rim Light"
        rim.data.energy = 15
    rim = _scene_obj(context, "Rim Light")
    rim.data.color = (0.75, 0.85, 1.0)
    if scene.camera is None:
        bpy.ops.object.camera_add(location=(3.3, -4.4, 1.9))
        scene.camera = context.object
    if scene.render.engine == "CYCLES":
        scene.cycles.samples = 64
    scene.render.filepath = _home("blender_buddy_donut_final.png")
    bpy.ops.render.render(write_still=True)


# --- the checks: the scene itself is the only proof -----------

def _check_saved(context):
    # Shared with the job flows: the work exists as a file.
    return bool(bpy.data.filepath)


def _check_picture(context):
    # Shared with the job flows: a picture was rendered.
    return _render_proof(context)


def _check_first_cup(context):
    # Part 1's tick is the save: the work exists as a file.
    return _check_saved(context)


def _check_mug_reference(context):
    has_ref = any(
        o.type == "EMPTY" and o.empty_display_type == "IMAGE"
        for o in context.scene.objects)
    if not has_ref:
        return False
    cup = _scene_obj(context, "Cup")
    base = len(cup.data.vertices) if (
        cup is not None and cup.type == "MESH") else 100
    for obj in context.scene.objects:
        if obj.type != "MESH" or obj is cup:
            continue
        if len(obj.data.vertices) > max(base * 2, base + 60):
            return True
    return False


def _check_icing_hug(context):
    dough = _find_dough(context)
    if dough is None:
        return False
    icing = _scene_obj(context, "Icing")
    if icing is None:
        return False
    if not any(m.type == "SOLIDIFY" for m in icing.modifiers):
        return False
    return any(m.type == "SHRINKWRAP" and m.target is dough
               for m in icing.modifiers)


def _check_first_picture(context):
    if _scene_obj(context, "Plate") is None:
        return False
    if _scene_obj(context, "Table") is None:
        return False
    dough = _find_dough(context)
    icing = _scene_obj(context, "Icing")
    if dough is None or icing is None:
        return False
    if _sss_weight(icing) <= 0 or _sss_weight(dough) <= 0:
        return False
    return _render_proof(context)


def _pbr_pattern(mat):
    """(photo wired into the material, a data map present, a
    Normal Map node present) for one material's node recipe."""
    if mat is None or not mat.use_nodes or mat.node_tree is None:
        return False, False, False
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    if bsdf is None:
        return False, False, False
    feeding = set()
    stack = [bsdf]
    while stack:
        node = stack.pop()
        if node in feeding:
            continue
        feeding.add(node)
        for sock in node.inputs:
            for link in sock.links:
                stack.append(link.from_node)
    wired = False
    noncolor = False
    for node in nt.nodes:
        if node.type != "TEX_IMAGE" or node.image is None:
            continue
        if node in feeding:
            wired = True
        if node.image.colorspace_settings.name != "sRGB":
            noncolor = True
    normal = any(n.type == "NORMAL_MAP" for n in nt.nodes)
    return wired, noncolor, normal


def _check_real_surfaces(context):
    targets = []
    for name in ("Table", "Plate", "Icing"):
        obj = _scene_obj(context, name)
        if obj is not None and obj.type == "MESH":
            targets.append(obj)
    dough = _find_dough(context)
    if dough is not None:
        targets.append(dough)
    if len(targets) < 4:
        return False
    wired_objects = 0
    any_noncolor = False
    any_normal = False
    for obj in targets:
        obj_wired = False
        for mat in obj.data.materials:
            wired, noncolor, normal = _pbr_pattern(mat)
            obj_wired = obj_wired or wired
            any_noncolor = any_noncolor or noncolor
            any_normal = any_normal or normal
        if obj_wired:
            wired_objects += 1
    return (wired_objects >= 3 and any_noncolor and any_normal)


def _check_unwrap_mug(context):
    mug = _scene_obj(context, "Mug")
    if mug is None or mug.type != "MESH":
        return False
    if not any(e.use_seam for e in mug.data.edges):
        return False
    foam = _scene_obj(context, "Coffee Foam")
    if foam is None or foam.type != "MESH":
        return False
    return len(foam.data.materials) > 0 and \
        foam.data.materials[0] is not None


def _check_scatter(context):
    icing = _scene_obj(context, "Icing")
    if icing is None:
        return False
    if not any(m.type == "NODES" and m.node_group is not None
               and "Scatter on Surface" in m.node_group.name
               for m in icing.modifiers):
        return False
    variants = False
    for coll in bpy.data.collections:
        if coll is context.scene.collection:
            continue
        small = [o for o in coll.objects
                 if o.type == "MESH" and len(o.data.vertices) < 2000]
        if len(small) >= 2:
            variants = True
    if not variants:
        return False
    for vg in icing.vertex_groups:
        for v in list(icing.data.vertices)[:600]:
            try:
                if vg.weight(v.index) > 0.0:
                    return True
            except RuntimeError:
                continue
    return False


def _check_final_picture(context):
    lights = [o for o in context.scene.objects if o.type == "LIGHT"]

    def deliberate(light):
        c = light.data.color
        return max(abs(c[0] - 1.0), abs(c[1] - 1.0),
                   abs(c[2] - 1.0)) > 0.02

    if not (len(lights) >= 2 or any(deliberate(l) for l in lights)):
        return False
    return _render_proof(context)


TOUR_STEPS = [
    {"title": "Your first cup, saved",
     "skill": "Moving around, adding a shape, Edit Mode, your "
              "first modifier - and saving",
     "how": "Part 1 of the new series ('Blender Donut Tutorial "
            "Part 1 (2026)'): before any donut exists, he "
            "teaches the whole workshop on a coffee cup - then "
            "saves the file.",
     "teach": [
         "1. Watch Part 1 first. He starts with moving around "
         "(from 1:30): hold the middle mouse button and drag to "
         "orbit; scroll to zoom. Everything else stands on this.",
         "2. Adding things is at 6:02, Shade Smooth at 9:32 - "
         "right-click the shape and pick Shade Smooth when your "
         "cup looks faceted.",
         "3. The cup itself starts at 10:27. At 15:42 he enters "
         "Edit Mode (Tab) - working on the skin, not the whole "
         "thing - and at 17:57 he deletes the top face in Edit "
         "Mode to open the cup's mouth.",
         "4. Modifiers arrive at 18:27: the wrench tab, Add "
         "Modifier, Subdivision Surface (20:40) makes the cup "
         "smooth; loop cuts (22:43) and the Inset tool (24:31) "
         "shape it, and at 26:47 he gives the cup's walls real "
         "thickness.",
         "5. At 27:11 he saves - Ctrl+S, a name, Save Blender "
         "File. Do the same now: this step ticks the moment "
         "your work exists as a saved file."],
     "missing": "Not saved yet: this step is done when your "
                "scene - cup and all - is saved as a .blend "
                "file (Ctrl+S).",
     "video": {"url": "https://www.youtube.com/watch?v=-tbSCMbJA6o",
               "label": "Watch Part 1 - Blender Donut Tutorial "
                        "Part 1"},
     "tools": ["make_smoother", "loop_cut", "inset_face",
               "save_work"],
     "run": _tour_step_first_cup, "check": _check_first_cup},
    {"title": "The mug with a handle, built from the photo",
     "skill": "Reference images: modelling a real thing by "
              "looking at it, not from memory",
     "how": "Part 2 ('Blender Basic Modelling Tutorial'): he "
            "models a realistic coffee mug from a reference "
            "photo - the photo he links from the series page.",
     "teach": [
         "1. Watch Part 2. At 0:00 he makes the case for "
         "reference; at 3:25 he adds the photo (Shift+A, Image, "
         "Reference) and works with it on show in the scene.",
         "2. At 7:31 he builds the mug's large forms against "
         "the photo; the bottom lip is at 10:18. Model what the "
         "photo shows, not what you remember a mug looks like.",
         "3. The handle is modelled at 13:25 and joined into "
         "itself at 20:54; at 23:36 he fixes the shading "
         "artifacts the join leaves behind - grey smudges are "
         "normal there, and fixable.",
         "4. Honest note: no measurement can judge your handle "
         "- it counts when it looks like the photo's handle to "
         "you. This step ticks on the photo being in your scene "
         "and your mug having grown well past the plain Part 1 "
         "cup."],
     "missing": "This step is done when the reference photo is "
                "in your scene as a visible image, and your mug "
                "has grown into a real modelled mug - well beyond "
                "the plain practice cup.",
     "video": {"url": "https://www.youtube.com/watch?v=K1UyEdmSttQ",
               "label": "Watch Part 2 - Basic Modelling"},
     "tools": ["start_shaping", "inset_face", "look_smooth"],
     "run": _tour_step_mug_reference, "check": _check_mug_reference},
    {"title": "Icing that drips and hugs the donut",
     "skill": "Edit Mode selection, Solidify, and the "
              "Shrinkwrap modifier",
     "how": "Part 3 ('Blender Basic Organic Modelling "
            "Tutorial'): the icing is the donut's own top - "
            "thickened, pulled into drips, and shrink-wrapped "
            "onto the dough so it hugs.",
     "teach": [
         "1. First the ring itself, if you don't have it yet: "
         "Shift+A, Mesh, Torus; right-click, Shade Smooth; the "
         "wrench tab, Add Modifier, Subdivision Surface at "
         "level 2. His Part 3 opens (0:00) by naming objects - "
         "rename yours Dough, and the copy below Icing.",
         "2. At 3:16 he duplicates the dough; at 4:08 he "
         "selects half of it - the top - in Edit Mode (Tab, "
         "then select by faces). The top is the icing; delete "
         "the rest of the copy.",
         "3. At 7:35, thickness: with Icing picked, the wrench "
         "tab, Add Modifier, Solidify - his thickness is about "
         "0.025. At 13:03 he pulls the rim down into runoff "
         "drips with proportional editing (the O key).",
         "4. At 14:26, the hug: Add Modifier, Deform, "
         "Shrinkwrap, and set its Target to the Dough. The "
         "icing now clings to the donut instead of floating "
         "above it.",
         "5. Stuck mid-part? His chapter at 5:46 is literally "
         "called the Unstuck Yourself Guide - it is the "
         "video's own rescue page."],
     "missing": "This step is done when a ring of dough exists "
                "and the piece named Icing has both a Solidify "
                "modifier and a Shrinkwrap modifier aimed at "
                "the dough.",
     "video": {"url": "https://www.youtube.com/watch?v=9OA2asQdi_U",
               "label": "Watch Part 3 - Basic Organic Modelling"},
     "tools": ["give_thickness", "wrap_onto", "start_shaping"],
     "run": _tour_step_icing_hug, "check": _check_icing_hug},
    {"title": "A lumpy donut, its first picture, and skin like food",
     "skill": "Staging a set, the Lattice, materials with "
              "subsurface - and the first render",
     "how": "Part 4 ('Blender Basic Materials Tutorial'): the "
            "plate arrives, a lattice makes the donut lumpy, "
            "real materials go on - and the setting that makes "
            "it read as food is turned on.",
     "teach": [
         "1. Watch Part 4. It opens (0:00) modelling the plate "
         "- that was Part 3's homework - and the donut rests "
         "on it.",
         "2. At 8:29 he bends the donut out of round with a "
         "Lattice: perfect circles read as computer-made, so "
         "the whole donut gets gently deformed before anyone "
         "looks closely.",
         "3. At 16:03 comes your first render - F12 - with "
         "camera control at 17:02. It will look grey and plain: "
         "that is correct at this point, the colour has not "
         "happened yet. If it comes out black, suspect the "
         "light first, not your donut.",
         "4. Basic materials arrive at 23:30 (the checker-ball "
         "tab): the icing gets its glossy pink, the dough its "
         "baked golden. Then SSS at 26:30 - Subsurface Weight "
         "above zero on both: light sinks into the surface and "
         "glows a little, like real icing and crumb, instead "
         "of bouncing off like plastic.",
         "5. The table is added last (29:35) - the big flat "
         "shape everything sits on. This step ticks when the "
         "plate, the table, the subsurface and a render are "
         "all in your scene, whichever order you did them."],
     "missing": "This step is done when the donut sits on a "
                "plate on a table, both dough and icing have "
                "Subsurface Weight above zero, and a render "
                "exists.",
     "video": {"url": "https://www.youtube.com/watch?v=5Xlu2zwbJd0",
               "label": "Watch Part 4 - Basic Materials"},
     "tools": ["give_colour", "take_picture", "camera_here"],
     "run": _tour_step_first_picture,
     "check": _check_first_picture},
    {"title": "Real surfaces from photo textures",
     "skill": "Image textures: colour, roughness and bump "
              "working together as one recipe",
     "how": "Part 5 ('Blender Basic Texturing Tutorial'): he "
            "textures the table, plate, donut and icing with "
            "photo textures - and a real surface turns out to "
            "be three pictures doing three different jobs.",
     "teach": [
         "1. Watch Part 5 - his chapter at 2:34 ('What are PBR "
         "Textures?') is the whole idea in four minutes. Open "
         "the Shader Editor - the screen of boxes and wires. "
         "Each surface is a recipe hanging off the Principled "
         "BSDF, the one big node everything feeds into.",
         "2. The colour photo (an Image Texture node) plugs "
         "into Base Color. It is the only picture that is "
         "actually colour, so its Colour Space stays sRGB.",
         "3. A second picture plugs into Roughness - where the "
         "surface is shiny, where it is dull. Set its Colour "
         "Space to Non-Color: it is data, not colour, and "
         "leaving it on sRGB is the classic 'looks wrong and "
         "nobody says why'.",
         "4. A third picture feeds a Normal Map node, and that "
         "plugs into the Principled's Normal socket - fine "
         "bumps faked from a photo. Also Non-Color. (He "
         "textures the icing at 21:37 and the donut at 27:42.)",
         "5. Buddy's tick looks for exactly this recipe - a "
         "photo wired into the material, at least one "
         "Non-Color data map, and a Normal Map node - across "
         "your table, plate, dough and icing."],
     "missing": "This step is done when your table, plate, "
                "dough and icing wear photo textures wired into "
                "their materials - with at least one Non-Color "
                "data map and a Normal Map node in the recipe.",
     "video": {"url": "https://www.youtube.com/watch?v=h30ZJQrb4s8",
               "label": "Watch Part 5 - Basic Texturing"},
     "tools": ["give_colour", "paint_picture"],
     "run": _tour_step_real_surfaces,
     "check": _check_real_surfaces},
    {"title": "Unwrap the mug so its pattern sits right",
     "skill": "Seams and UV unwrapping: choosing where a "
              "shape's wrapping paper is cut",
     "how": "Part 6 ('Blender Basic UV Unwrapping Tutorial'): "
            "the mug gets a pattern - and a pattern only lands "
            "straight if you first choose where the mug's skin "
            "is cut to lay it flat.",
     "teach": [
         "1. Watch Part 6. To wrap a flat picture around a "
         "mug, Blender needs a flat map of its skin - the UV "
         "map. You choose the cuts: pick the mug, Tab into "
         "Edit Mode, select edges, and Mark Seam (right-click "
         "menu, or Ctrl+E). Down the back and around the rim "
         "is where a real mug's glaze line runs.",
         "2. Then select everything (A) and press U, then "
         "Unwrap. The mug's skin flattens into the UV Editor. "
         "Seams in the wrong place make the pattern stretch - "
         "Buddy can see your seams, but only your eye can "
         "judge the flattening.",
         "3. At 25:02 he creates the coffee foam: a flat disc "
         "just inside the mug's rim, with a material of its "
         "own, so the mug reads as full instead of hollow. "
         "(The handle gets its own island in the unwrap at "
         "2:54 - that is why it was joined the way it was.)"],
     "missing": "This step is done when your mug has seams "
                "marked on its edges and a coffee-foam disc "
                "sits inside the mug's rim with a material of "
                "its own. Whether the pattern sits straight is "
                "your eye's call - no tick can see that.",
     "video": {"url": "https://www.youtube.com/watch?v=yxAqN8TzFbo",
               "label": "Watch Part 6 - Basic UV Unwrapping"},
     "tools": ["start_shaping", "paint_it"],
     "run": _tour_step_unwrap_mug, "check": _check_unwrap_mug},
    {"title": "Sprinkles by the hundred, none by hand",
     "skill": "The Scatter on Surface modifier: making "
              "Blender place the copies for you",
     "how": "Part 7 ('How to Scatter in Blender 5.0'): "
            "Blender 5.0's new Scatter on Surface modifier "
            "covers the icing in sprinkles - you model two or "
            "three, it places the hundred.",
     "teach": [
         "1. Watch Part 7. At 0:18 he explains the 3D cursor - "
         "the red-and-white target is where new things are "
         "born. At 0:51 he models one sprinkle; at 5:21 he "
         "makes the sprinkle variants - a few shapes, gathered "
         "into one Collection.",
         "2. At 7:23 he adds the Scatter on Surface modifier "
         "to the icing (wrench tab, Add Modifier) and points "
         "it at the sprinkle collection, with Pick Instance on "
         "so it mixes the variants instead of cloning one.",
         "3. At 12:44 he controls where it scatters: the "
         "icing's painted vertex group becomes the modifier's "
         "Distribution Mask, so sprinkles land where the "
         "icing shows and nowhere else. Paint it in Weight "
         "Paint mode - red is 'sprinkles here'.",
         "4. At 18:19 he fixes intersections (sprinkles sunk "
         "too deep - lift them with the Surface Offset), and "
         "at 24:04 the colours get randomized.",
         "5. This modifier is new in Blender 5.0. On an older "
         "Blender it simply is not there, and this one step "
         "waits until you are on 5.0 or newer."],
     "missing": "This step is done when the icing carries a "
                "Scatter on Surface modifier, a collection "
                "holds at least two sprinkle shapes, and the "
                "icing has a painted vertex group guiding them.",
     "video": {"url": "https://www.youtube.com/watch?v=_-QsGTL7pS0",
               "label": "Watch Part 7 - How to Scatter in "
                        "Blender 5.0"},
     "tools": [],
     "run": _tour_step_scatter, "check": _check_scatter},
    {"title": "Light it like a photo, render it twice",
     "skill": "Lighting for realism - and the two render "
              "engines, Eevee and Cycles",
     "how": "The finale ('The Basics of Lighting and "
            "Rendering in Blender'): he lights the donut for "
            "realism, then renders it in both of Blender's "
            "engines so you can see what each one does.",
     "teach": [
         "1. Watch the finale. His own summary of it: you "
         "learn to add lights for realism. The method is one "
         "light at a time, looking at what each one changes - "
         "a single flat light is exactly why a render looks "
         "like plastic.",
         "2. Build the light in layers: a strong main light "
         "from one side to shape the donut, a gentler light to "
         "lift the shadows, and the room's own light (the "
         "World) kept in check. This step ticks when your "
         "scene holds a real setup - more than one light, or "
         "one light you have deliberately aimed and coloured "
         "- and a fresh render exists.",
         "3. Then render it twice: Render Properties, Render "
         "Engine - once with Eevee (fast, a little less true), "
         "once with Cycles (slow, honest light), F12 each "
         "time, and compare the two pictures side by side.",
         "4. Which one looks like food is your eye's decision. "
         "That judgment is the whole craft of this part - no "
         "tick can grade it, and Buddy won't pretend to."],
     "missing": "This step is done when your scene is lit on "
                "purpose - more than one light, or one "
                "deliberately set - and a fresh render exists. "
                "The rest, whether it looks like a photo, is "
                "your eye: that is the real finish.",
     "video": {"url": "https://www.youtube.com/watch?v=WobATxh3i-g",
               "label": "Watch Part 8 - Lighting and Rendering "
                        "(the finale)"},
     "tools": ["add_sun", "add_lamp", "take_picture", "save_work"],
     "run": _tour_step_final_picture,
     "check": _check_final_picture},
]



# ----------------------------------------------------------------------------
# Job flows: the community's ways of working, as packages.
# The step ORDER and the methods come from the gathered
# community patterns (redesign/COMMUNITY_PATTERNS.md): blockout
# before detail, transforms locked before bevels and exports,
# modifiers live and in stack order, check in the view that
# reveals the problem, export a copy and keep the source.
# Like the projects, a flow TEACHES: the user does each step;
# the scene proves it. Checks are gates - a gate the scene
# already satisfies (size already locked, camera already
# there) simply reads as done, which is how a flow can meet
# you in the middle of a job.
# ----------------------------------------------------------------------------

def _flow_meshes(context):
    return [o for o in context.scene.objects if o.type == "MESH"]


def _flow_main(context):
    obj = context.object
    if obj is not None and obj.type == "MESH":
        return obj
    meshes = _flow_meshes(context)
    if not meshes:
        return None
    return max(meshes, key=lambda o: len(o.data.vertices))


def _flow_pick_main(context):
    main = _flow_main(context)
    if main is None:
        return None
    if context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    main.select_set(True)
    context.view_layer.objects.active = main
    return main


def _flow_locked(obj):
    if obj is None:
        return False
    return (all(abs(s - 1.0) < 0.001 for s in obj.scale)
            and all(abs(r) < 0.001 for r in obj.rotation_euler))


def _flow_run_lock(context):
    if _flow_pick_main(context) is not None:
        bpy.ops.buddy.action(action_id="lock_size")


def _flow_run_subdivide(context):
    main = _flow_pick_main(context)
    if main is None:
        bpy.ops.mesh.primitive_cube_add()
        main = context.object
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.subdivide(number_cuts=1)
    bpy.ops.object.mode_set(mode="OBJECT")


# -- hard-surface flow -------------------------------------------------

def _check_flow_reference(context):
    return any(o.type == "EMPTY"
               and getattr(o, "empty_display_type", "") == "IMAGE"
               for o in context.scene.objects)


def _flow_run_reference(context):
    bpy.ops.object.empty_add(type="IMAGE")


def _check_flow_blockout(context):
    return any(len(o.data.vertices) >= 4 for o in _flow_meshes(context))


def _flow_run_blockout(context):
    if not _flow_meshes(context):
        bpy.ops.mesh.primitive_cube_add()


def _check_flow_locked(context):
    return _flow_locked(_flow_main(context))


def _check_flow_forms(context):
    main = _flow_main(context)
    return main is not None and len(main.data.vertices) > 8


def _check_flow_detail(context):
    return any(m.type in ("BOOLEAN", "ARRAY")
               for o in _flow_meshes(context) for m in o.modifiers)


def _flow_run_detail(context):
    if _flow_pick_main(context) is not None:
        bpy.ops.buddy.action(action_id="row_of_them")


def _check_flow_thickness(context):
    return any(m.type in ("SOLIDIFY", "SUBSURF")
               for o in _flow_meshes(context) for m in o.modifiers)


def _flow_run_thickness(context):
    if _flow_pick_main(context) is not None:
        bpy.ops.buddy.action(action_id="give_thickness")


def _check_flow_edges(context):
    return any(m.type == "BEVEL"
               for o in _flow_meshes(context) for m in o.modifiers)


def _flow_run_edges(context):
    if _flow_pick_main(context) is not None:
        bpy.ops.buddy.action(action_id="round_all_edges")


def _check_flow_hard_finish(context):
    return (any(m.type == "WEIGHTED_NORMAL"
                for o in _flow_meshes(context) for m in o.modifiers)
            and _check_saved(context))


def _flow_run_hard_finish(context):
    if _flow_pick_main(context) is not None:
        bpy.ops.buddy.action(action_id="fix_hard_shading")
        bpy.ops.buddy.action(action_id="save_work")


HARD_SURFACE_STEPS = [
    {"title": "Set the size and bring in a reference",
     "skill": "Working from something real: size and a picture to "
              "check against",
     "how": "How the community starts every hard-surface job: "
            "never a blank window. Real size first - light, "
            "bevels and printing all depend on it - and a "
            "reference picture pinned where you can see it.",
     "teach": [
         "1. Decide how big the real thing is. In the sidebar "
         "(press N) under Item, your picked thing shows its "
         "Dimensions - size it with S until they read right.",
         "2. Bring the reference in: drag a photo of the thing "
         "straight into the big 3D window, or press Shift+A, "
         "choose Image, then Reference.",
         "3. Park the picture behind or beside your work area "
         "with G, and turn back to it whenever you check the "
         "outline."],
     "missing": "No reference picture in the scene yet - drag "
                "one into the 3D window.",
     "tools": ["tool_move", "tool_size"],
     "run": _flow_run_reference, "check": _check_flow_reference},
    {"title": "Block out the big shapes",
     "skill": "Blockout: silhouette and proportions before any "
              "detail",
     "how": "One plain shape per big part - a box for the body, "
            "a tube for the handle. No detail at all yet: if the "
            "outline doesn't read at this stage, no detail will "
            "save it.",
     "teach": [
         "1. Add the big masses with the Add buttons above - one "
         "shape per part of the real thing.",
         "2. Move, turn and size them until the outline matches "
         "your reference from the front, the side and the top "
         "(the Move around drawer has the one-press views).",
         "3. If it's the same on both sides, use Mirror on it "
         "instead of building the other half by hand."],
     "missing": "No blockout shape yet - add a box or a tube to "
                "start the silhouette.",
     "tools": ["add_cube", "add_tube", "tool_move", "tool_size",
               "tool_turn", "mirror_it"],
     "run": _flow_run_blockout, "check": _check_flow_blockout},
    {"title": "Lock the size before you shape",
     "skill": "Apply transforms: the invisible setting that "
              "breaks bevels when it's wrong",
     "how": "Every guide names this gate: once the blockout is "
            "sized, lock it in (Blender calls it Apply Scale and "
            "Rotation). Skip it and bevels come out uneven and "
            "nobody tells you why.",
     "teach": [
         "1. Click the blocked-out thing.",
         "2. Press the Lock the size in button below - it bakes "
         "the size and turn into the shape itself.",
         "3. Do it for every part you sized, before any real "
         "shaping starts."],
     "missing": "The main shape's size isn't locked in yet - "
                "click it and use Lock the size in.",
     "tools": ["lock_size", "handle_middle"],
     "run": _flow_run_lock, "check": _check_flow_locked},
    {"title": "Build the main forms",
     "skill": "Box modelling: loop cuts, insets and pulling "
              "faces - the heart of hard-surface work",
     "how": "Now the shaping, in Edit Mode: cuts to place the "
            "structure, insets for panels, pulling faces out or "
            "in for the raised and recessed parts.",
     "teach": [
         "1. Press Start shaping (or Tab) to work on the skin of "
         "the thing.",
         "2. Cut a line around it where a panel edge or a bend "
         "belongs (Cut a line around it), select the face inside "
         "it, and sink it a little (Sink a face inwards).",
         "3. Pull faces out for raised parts (Pull a face out). "
         "Work big forms first; small detail comes later."],
     "missing": "The main shape is still a plain block - it "
                "needs cuts and shaped faces (more points than "
                "the 8 it started with).",
     "tools": ["start_shaping", "pull_face", "inset_face",
               "loop_cut", "knife", "split_faces"],
     "run": _flow_run_subdivide, "check": _check_flow_forms},
    {"title": "Add openings and repeats - without wrecking "
              "the original",
     "skill": "Non-destructive detail: live cutters and arrays",
     "how": "Holes, ports, vents, bolts: the community way "
            "keeps them LIVE - a cutter you can still move, a "
            "row you can still recount - instead of carving the "
            "shape itself to pieces.",
     "teach": [
         "1. For a hole: add a shape where the hole belongs, "
         "pick the main thing first and the cutter last, then "
         "Cut a hole through it.",
         "2. For repeats - bolts, vents, ridges - use Make a "
         "row of copies and set the count in the wrench tab.",
         "3. Leave them live until the design is settled. "
         "Making them permanent is a finishing step, not a "
         "modelling step."],
     "missing": "No live detail yet: the shape needs a Boolean "
                "cut or an Array row on it.",
     "tools": ["cut_hole", "row_of_them", "mirror_it"],
     "run": _flow_run_detail, "check": _check_flow_detail},
    {"title": "Give it thickness or hold its shape",
     "skill": "Solidify and Subdivision: walls, and smoothing "
              "that keeps its edges",
     "how": "Thin shells become real walls with Solidify. If "
            "you smooth the shape instead (Subdivision), the "
            "order matters: edge control comes before the "
            "smoother in the stack, or the edges melt.",
     "teach": [
         "1. Pick the shape and give it thickness (Give it "
         "thickness) if it's a shell - a mug wall, a casing.",
         "2. Or smooth it (Make it smoother & rounder) and add "
         "extra cuts near edges that must stay crisp.",
         "3. Check the stack in the wrench tab: things apply "
         "top to bottom, so read it like a recipe."],
     "missing": "No thickness or smoothing on the shape yet.",
     "tools": ["give_thickness", "make_smoother"],
     "run": _flow_run_thickness, "check": _check_flow_thickness},
    {"title": "Control the edges",
     "skill": "Bevels: real edges catch the light",
     "how": "Nothing manufactured has a perfectly sharp edge. "
            "A small bevel is what makes a model read as a real "
            "object in the light - the community step that "
            "separates 'CG block' from 'thing'.",
     "teach": [
         "1. Pick the shape and press Round off all the edges.",
         "2. In the wrench tab, keep the width small - just "
         "enough to catch a highlight.",
         "3. For one local edge instead: shape it, select the "
         "edge, and use Round off a sharp edge."],
     "missing": "No bevel on the shape yet - its edges are "
                "still knife-sharp.",
     "tools": ["round_all_edges", "round_edge"],
     "run": _flow_run_edges, "check": _check_flow_edges},
    {"title": "Fix the shading, then save the source",
     "skill": "Weighted normals, and keeping the live source "
              "file",
     "how": "Last in the stack: Weighted Normal smooths out "
            "the shading smears that cuts and bevels leave "
            "behind. Then save - the file keeps everything "
            "live and editable; exports are copies of it, "
            "never replacements.",
     "teach": [
         "1. Press Keep hard shading crisp (the Weighted "
         "Normal) and turn the view around: flat faces should "
         "shade flat and clean, with no smears or black "
         "patches.",
         "2. If a face shades inside-out, shape it, select "
         "all, and use Point the faces the right way.",
         "3. Save the file (Ctrl+S). This is the source - "
         "everything else gets made from it."],
     "missing": "Not finished: the shape needs its shading "
                "fixed (Weighted Normal) and the file saved.",
     "tools": ["fix_hard_shading", "look_smooth", "save_work"],
     "run": _flow_run_hard_finish, "check": _check_flow_hard_finish},
]


# -- look-real flow ------------------------------------------------------

def _check_flow_model_ready(context):
    main = _flow_main(context)
    return main is not None and (len(main.data.vertices) > 8
                                 or len(main.modifiers) > 0)


def _check_flow_camera(context):
    return context.scene.camera is not None


def _flow_run_camera(context):
    if context.scene.camera is None:
        bpy.ops.buddy.action(action_id="add_camera")
        cam = context.object
        if cam is not None and cam.type == "CAMERA":
            context.scene.camera = cam


def _check_flow_lit(context):
    scene = context.scene
    if sum(1 for o in scene.objects if o.type == "LIGHT") >= 3:
        return True
    world = scene.world
    if world is not None and world.use_nodes and world.node_tree:
        return any(n.type == "TEX_ENVIRONMENT"
                   and getattr(n, "image", None)
                   for n in world.node_tree.nodes)
    return False


def _flow_run_light(context):
    while sum(1 for o in context.scene.objects
              if o.type == "LIGHT") < 3:
        bpy.ops.buddy.action(action_id="add_sun")
        if sum(1 for o in context.scene.objects
               if o.type == "LIGHT") < 3:
            bpy.ops.buddy.action(action_id="add_lamp")


def _check_flow_material(context):
    main = _flow_main(context)
    if main is None:
        return False
    for mat in main.data.materials:
        if mat is not None and mat.use_nodes and mat.node_tree:
            if any(n.type == "BSDF_PRINCIPLED"
                   for n in mat.node_tree.nodes):
                return True
    return False


def _flow_run_material(context):
    if _flow_pick_main(context) is not None:
        bpy.ops.buddy.action(action_id="give_colour")


def _flow_run_picture(context):
    bpy.ops.buddy.action(action_id="take_picture")


def _flow_run_save(context):
    bpy.ops.buddy.action(action_id="save_work")


LOOK_REAL_STEPS = [
    {"title": "Start from a sound model",
     "skill": "The model comes first - looks are judged on a "
              "finished shape",
     "how": "Both community guides are blunt about the order: "
            "a sound, finished model first. Detail and looks "
            "can't rescue a shape that isn't there yet.",
     "teach": [
         "1. Finish the modelling first - silhouette and main "
         "forms settled (the hard-surface way of working walks "
         "through exactly that).",
         "2. If the thing is still a plain block, this flow "
         "will wait here until it isn't."],
     "missing": "The model isn't shaped yet - it's still a "
                "plain block with nothing done to it.",
     "tools": ["start_shaping", "split_faces"],
     "run": _flow_run_subdivide, "check": _check_flow_model_ready},
    {"title": "Check its real size",
     "skill": "Real-world scale: light and cameras behave "
              "differently at the wrong size",
     "how": "Light falls off and camera lenses act like the "
            "real world - a model at the wrong scale will fight "
            "every later step. Lock its size in now.",
     "teach": [
         "1. Click the model and read its Dimensions in the "
         "sidebar (N key, Item tab) - do they match the real "
         "thing?",
         "2. Press Lock the size in so the size is baked into "
         "the shape."],
     "missing": "The model's size isn't locked in yet.",
     "tools": ["lock_size", "handle_middle", "centre_world"],
     "run": _flow_run_lock, "check": _check_flow_locked},
    {"title": "Frame the shot",
     "skill": "Composition before materials: decide what the "
              "picture is",
     "how": "The guides decide the shot BEFORE the materials, "
            "because materials are judged in the frame and "
            "light they'll actually live in.",
     "teach": [
         "1. If there's no camera, add one (Add a camera).",
         "2. Turn your view until the model sits well, then "
         "use Move the camera to what I'm looking at - the "
         "camera takes the shot you just composed.",
         "3. Look through it (Look through the camera) and "
         "nudge until the framing is the picture you want."],
     "missing": "No camera in the scene yet.",
     "tools": ["add_camera", "camera_here", "look_camera"],
     "run": _flow_run_camera, "check": _check_flow_camera},
    {"title": "Light it - first pass",
     "skill": "Three-point lighting and environment light",
     "how": "The studio pattern: a key light to shape it, a "
            "fill so the shadows aren't dead, a rim from "
            "behind to lift it off the background - or an "
            "environment (HDRI) doing the same job. Judge "
            "shapes now, colours later.",
     "teach": [
         "1. Add sunlight for the key and a lamp or two for "
         "fill and rim; move each one like any other thing.",
         "2. Switch the big window's shading to Rendered (the "
         "last of the four balls at its top-right) so you see "
         "the real light.",
         "3. Or: in the World tab, give the world an "
         "environment picture (HDRI) - instant believable "
         "reflections and light."],
     "missing": "The scene needs a lighting setup: three "
                "lights, or an environment picture in the World.",
     "tools": ["add_sun", "add_lamp"],
     "run": _flow_run_light, "check": _check_flow_lit},
    {"title": "Give it real surfaces",
     "skill": "Principled materials: one honest material per "
              "surface",
     "how": "Realism comes from the Principled material plus "
            "variation - roughness that isn't perfectly even, "
            "a normal map for surface detail - not from exotic "
            "shaders. One warning from production order: "
            "picture-based materials need UVs first; a model "
            "with no UV map routes to unwrapping before "
            "textures will sit right.",
     "teach": [
         "1. Click the model and give it a colour to start - "
         "that lays down a real Principled material.",
         "2. In the Material tab, set Roughness per surface: "
         "polished things low, rough things high. Nothing "
         "real is perfectly even.",
         "3. Add picture textures (Base Color, Roughness, "
         "Normal) in the Shader editor when you're ready - "
         "that's where real surfaces come from."],
     "missing": "The model has no real (Principled) material "
                "yet.",
     "tools": ["give_colour"],
     "run": _flow_run_material, "check": _check_flow_material},
    {"title": "Polish the light, then take the picture",
     "skill": "Second lighting pass, camera settings, and "
              "the render",
     "how": "With real surfaces on, judge the light again: "
            "colour, strength, ratios. Set the camera's lens, "
            "choose the engine (Cycles for realism, Eevee for "
            "speed), set the picture size - then render.",
     "teach": [
         "1. In Rendered view, tune each light's strength and "
         "colour against the real materials.",
         "2. Click the camera and set its Focal Length in the "
         "camera tab - 50 is neutral, wider feels dramatic.",
         "3. In the Render tab pick Cycles for the realistic "
         "engine and your picture size, then Take the "
         "picture."],
     "missing": "No picture taken yet in this flow - frame, "
                "light, and render it.",
     "tools": ["take_picture"],
     "run": _flow_run_picture, "check": _check_picture},
    {"title": "Save it before you lose it",
     "skill": "A render you didn't save is a picture you "
              "don't have",
     "how": "The classic lost-work moment: the render sits "
            "in the picture window, unsaved, and one click "
            "closes it forever. Save the picture AND the file.",
     "teach": [
         "1. In the picture window: Image, Save As - save "
         "the render somewhere you'll find it.",
         "2. Save the Blender file too (Save your work) - "
         "the scene is the source of the picture."],
     "missing": "The file isn't saved yet.",
     "tools": ["save_work", "send_web"],
     "run": _flow_run_save, "check": _check_saved},
]


# -- 3D printing flow ----------------------------------------------------

def _check_flow_mm(context):
    units = context.scene.unit_settings
    return (units.length_unit == "MILLIMETERS"
            and abs(units.scale_length - 0.001) < 1e-6)


def _flow_run_mm(context):
    units = context.scene.unit_settings
    units.system = "METRIC"
    units.length_unit = "MILLIMETERS"
    units.scale_length = 0.001


def _check_flow_solid(context):
    main = _flow_main(context)
    if main is None:
        return False
    counts = {}
    for poly in main.data.polygons:
        for key in poly.edge_keys:
            counts[key] = counts.get(key, 0) + 1
    if not counts or any(v != 2 for v in counts.values()):
        return False
    verts = [tuple(v.co) for v in main.data.vertices]
    return len(set(verts)) == len(verts)


def _flow_run_solid(context):
    main = _flow_pick_main(context)
    if main is None or _check_flow_solid(context):
        return
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    try:
        bpy.ops.mesh.remove_doubles(threshold=0.0001)
    except Exception:
        pass
    try:
        bpy.ops.mesh.normals_make_consistent(inside=False)
    except Exception:
        pass
    bpy.ops.object.mode_set(mode="OBJECT")


def _check_flow_stl(context):
    epoch = getattr(context.scene, "buddy_tour_epoch", 0)
    if epoch <= 0:
        return False
    path = _home("blender_buddy_model.stl")
    return (os.path.exists(path)
            and os.path.getmtime(path) >= epoch - 2)


def _flow_run_stl(context):
    if _flow_pick_main(context) is not None:
        bpy.ops.buddy.action(action_id="send_print")


PRINT_STEPS = [
    {"title": "Set millimetres first",
     "skill": "Print units: the slicer reads everything as "
              "millimetres",
     "how": "The printing guides set units at the START, not "
            "at export: print files carry bare numbers that "
            "slicers read as millimetres, so a model built at "
            "the wrong scale prints at the wrong size.",
     "teach": [
         "1. Open the Scene tab on the right (the one with "
         "the little scene icon).",
         "2. Under Units: Length = Millimeters, and Unit "
         "Scale = 0.001.",
         "3. Check your thing's Dimensions (sidebar, Item) "
         "read as the real millimetres you want to hold."],
     "missing": "The scene isn't set to millimetres yet.",
     "tools": [],
     "run": _flow_run_mm, "check": _check_flow_mm},
    {"title": "Finish it and lock the size",
     "skill": "Transforms locked before checks mean anything",
     "how": "Same gate as everywhere: rotation and scale "
            "baked in, or every check and the export itself "
            "measures a lie.",
     "teach": [
         "1. Finish the modelling - printing prep starts "
         "from a finished thing.",
         "2. Click it and press Lock the size in."],
     "missing": "The thing's size and rotation aren't locked "
                "in yet.",
     "tools": ["lock_size", "centre_world"],
     "run": _flow_run_lock, "check": _check_flow_locked},
    {"title": "Make it one solid thing - and prove it",
     "skill": "Watertight: one closed solid, outward faces, "
              "no doubled points",
     "how": "A printer needs ONE closed solid. The official "
            "checker (3D Print Toolbox, in Get Extensions) "
            "runs Check All for the full report - Buddy ticks "
            "this step when the core truth holds: every edge "
            "belongs to exactly two faces, and no two points "
            "sit in the same place. Thickness and overhang "
            "are reviewed in the slicer - they're support "
            "questions, not always mesh errors.",
     "teach": [
         "1. Shape the thing, select all of it, and merge "
         "points that sit on top of each other (Join points "
         "that are on top of each other).",
         "2. Point the faces outward (Point the faces the "
         "right way).",
         "3. Holes in the shell: select the open ring of "
         "edges and Fill in a missing face, until the shell "
         "closes."],
     "missing": "Not one solid yet: the shell has openings, "
                "or points doubled up on each other.",
     "tools": ["start_shaping", "join_close_points", "fix_faces",
               "fill_face"],
     "run": _flow_run_solid, "check": _check_flow_solid},
    {"title": "Send it to the slicer",
     "skill": "Export a copy; the slicer has the last word "
              "on size",
     "how": "Export the print file (STL) from the finished, "
            "checked thing - then confirm the size and "
            "direction in your slicer. Buddy's job ends at a "
            "verified export; the slicer check happens "
            "outside Blender and nothing in here replaces it.",
     "teach": [
         "1. Click the finished thing.",
         "2. Press Send it out for 3D printing - the file "
         "lands in your home folder as blender_buddy_model.stl.",
         "3. Open it in your slicer and confirm the size in "
         "millimetres is the size in your hand will be."],
     "missing": "No print file exported yet in this flow.",
     "tools": ["send_print"],
     "run": _flow_run_stl, "check": _check_flow_stl},
    {"title": "Keep the source",
     "skill": "The .blend is the master; the print file is "
              "a copy of it",
     "how": "Save the Blender file with everything live. "
            "Next change starts from the source, never from "
            "the exported print file.",
     "teach": [
         "1. Press Save your work (Ctrl+S).",
         "2. Exports are copies: the next change always starts "
         "from this file, never from the print file."],
     "missing": "The source file isn't saved yet.",
     "tools": ["save_work"],
     "run": _flow_run_save, "check": _check_saved},
]

PACKAGES = [
    {"id": "donut",
     "name": "Make a Donut",
     "byline": "The follow-along companion to Blender Guru's new "
               "donut series for Blender 5.0 - the famous first "
               "project, rebuilt for 5.0.",
     "intro": "Eight video parts, eight steps. He teaches on "
              "YouTube; this companion keeps your place in the "
              "series, tells you what he is about to do, and "
              "ticks each step off only when your scene proves "
              "you caught up. Cup, mug, icing, materials, photo "
              "textures, unwrapping, scattering, light - you do "
              "every step with your own hands, in real Blender.",
     "steps": TOUR_STEPS},
    {"id": "hard_surface",
     "kind": "flow",
     "name": "Make a hard-surface thing",
     "byline": "The community's order for mugs, crates, tools "
               "and props: blockout, locked size, forms, live "
               "detail, edges, shading.",
     "intro": "Not a lesson about a specific object - a way of "
              "working, in the order experienced modellers "
              "actually do it, gathered from the community's "
              "own guides. Start it beside your own project: "
              "each step names the method, shows the few tools "
              "that matter for it, and ticks off only when your "
              "scene proves the step is true.",
     "steps": HARD_SURFACE_STEPS},
    {"id": "look_real",
     "kind": "flow",
     "name": "Make it look real",
     "byline": "The rendering order from the community's "
               "workflow guides: shot first, light, surfaces, "
               "light again, picture, save.",
     "intro": "The discipline both full workflow guides "
              "teach: composition and lighting are decided "
              "before material detail, because materials are "
              "judged under the light they'll live in. Start "
              "it with a finished model and work the steps "
              "against your own scene.",
     "steps": LOOK_REAL_STEPS},
    {"id": "print_ready",
     "kind": "flow",
     "name": "Get it ready for 3D printing",
     "byline": "The print checklist as a gate sequence: "
               "millimetres, locked size, one solid, export, "
               "verify in the slicer.",
     "intro": "The most checklist-like job in Blender, run "
              "as gates in the community's order - no step is "
              "optional in the sources. Each gate ticks only "
              "when the scene proves it, and the last check "
              "still happens in your slicer, where it belongs.",
     "steps": PRINT_STEPS},
]

PACKAGES_BY_ID = {p["id"]: p for p in PACKAGES}


def _active_package(context):
    pid = getattr(context.scene, "buddy_tour_package", "donut")
    return PACKAGES_BY_ID.get(pid or "donut", PACKAGES[0])


def tour_state(context):
    """(checks, current step index) for the active guided project.
    A step counts as done only when the scene itself proves it."""
    checks = []
    for step in _active_package(context)["steps"]:
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

        stale_reason = _stale_map().get(act["id"])
        if stale_reason:
            self.report({"WARNING"},
                        "That one changed in this version of Blender, "
                        "so Buddy has hidden it rather than guess: "
                        f"{stale_reason}. Every current Blender tool "
                        "is still in the search below.")
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
    bl_label = "Start a Guided Project"
    bl_description = ("Start a guided project: it teaches you each "
                      "step and ticks it off when your scene proves "
                      "you did it - it never does the steps for you")
    bl_options = {"REGISTER"}

    package: StringProperty(options={"HIDDEN"}, default="donut")

    def execute(self, context):
        import time
        global _EXPERT_TIP, _TOUR_TIP_STEP
        pkg = PACKAGES_BY_ID.get(self.package or "donut", PACKAGES[0])
        context.scene.buddy_tour_package = pkg["id"]
        context.scene.buddy_tour_started = True
        _CONDUCT["key"] = None
        _conduct_check()
        context.scene.buddy_tour_epoch = int(time.time())
        _TOUR_TIP_STEP = 0
        _EXPERT_TIP = (f"{pkg['name']}, step 1: "
                       f"{pkg['steps'][0]['title']}.")
        self.report({"INFO"}, f"{pkg['name']} started - step 1 is at "
                              "the top of the Blender Buddy panel. "
                              "You do it; the card ticks it off.")
        return {"FINISHED"}


class BUDDY_OT_tour_hide(Operator):
    bl_idname = "buddy.tour_hide"
    bl_label = "Hide the Guided Project"
    bl_description = "Hide the guided project card for now"
    bl_options = {"REGISTER"}

    def execute(self, context):
        context.scene.buddy_tour_started = False
        return {"FINISHED"}


class BUDDY_OT_tour_do(Operator):
    """The reference build of a step - kept for the test suites and
    for generating the demo donut. The guided projects themselves
    never offer it: they teach, the learner does."""
    bl_idname = "buddy.tour_do"
    bl_label = "Build This Step (Reference)"
    bl_description = ("Build this step the reference way - the "
                      "machinery the tests use to prove each step's "
                      "scene check. The guided project in the panel "
                      "teaches you to do it yourself instead")
    bl_options = {"REGISTER", "UNDO"}

    step: IntProperty(options={"HIDDEN"})

    def execute(self, context):
        global _EXPERT_TIP
        steps = _active_package(context)["steps"]
        if not (0 <= self.step < len(steps)):
            return {"CANCELLED"}
        step = steps[self.step]
        global _BUILDING
        _BUILDING = True
        try:
            step["run"](context)
        except Exception as exc:
            self.report({"WARNING"}, f"That step didn't finish: {exc}")
            return {"CANCELLED"}
        finally:
            _BUILDING = False
        _conduct_check()
        if step["check"](context):
            nxt = self.step + 1
            if nxt < len(steps):
                _EXPERT_TIP = (f"Step {nxt + 1}: {steps[nxt]['title']}.")
                self.report({"INFO"}, f"Done - {step['title']}. "
                                      f"Next: {steps[nxt]['title']}.")
            else:
                _EXPERT_TIP = "Project finished. Ask me anything."
                self.report({"INFO"}, "Done - project finished.")
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
_CLAUDE_URL = "https://api.anthropic.com/v1/messages"
_CLAUDE_MODEL = "claude-sonnet-4-5"
_CLAUDE_VERSION = "2023-06-01"
_EXPERT_TIP = ""
# The tour step the floating card was last told about, so the panel
# only updates the card when the step actually changes.
_TOUR_TIP_STEP = -1
_EXPERT_HANDLE = None


def _expert_service_update(self, context):
    """Picking a way to reach the expert pre-fills the address and
    model fields for that way; the user can still edit them after."""
    if self.expert_service == "LOCAL":
        self.expert_url = _EXPERT_LOCAL_URL
        self.expert_model = _EXPERT_LOCAL_MODEL
    elif self.expert_service == "CLAUDE":
        self.expert_url = _CLAUDE_URL
        self.expert_model = _CLAUDE_MODEL
    elif self.expert_service == "KEY":
        url = self.expert_url or ""
        if url.startswith(("http://localhost", "http://127.0.0.1")) \
                or "anthropic.com" in url:
            self.expert_url = _EXPERT_DEFAULT_URL
            self.expert_model = _EXPERT_DEFAULT_MODEL


class BUDDY_Preferences(AddonPreferences):
    bl_idname = __name__

    expert_service: EnumProperty(
        name="Expert connects by",
        description="Key: an AI service key you paste below. Claude "
                    "key: an Anthropic key you paste below. ChatGPT "
                    "login: through OpenAI's own Codex program on "
                    "this computer, signed in with your ChatGPT "
                    "account - Buddy never sees your login. Local AI: "
                    "a free AI running on this computer (like Ollama) "
                    "- no key, no login, nothing leaves the machine",
        items=[
            ("KEY", "AI key (OpenAI-style service)",
             "Paste a key from an AI service below"),
            ("CLAUDE", "Claude key (Anthropic)",
             "Paste an Anthropic key below - Claude's service "
             "speaks a different shape, and Buddy translates"),
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
                    "card over the big 3D window. Off by default - "
                    "the card got in the way more than it helped",
        default=False)

    def draw(self, context):
        global _WRAP_CAP
        _WRAP_CAP = _fit_width(context)
        layout = self.layout
        layout.prop(self, "expert_service")
        layout.prop(self, "expert_key")
        layout.prop(self, "expert_url")
        layout.prop(self, "expert_model")
        layout.prop(self, "expert_float")
        layout.operator("buddy.test_expert",
                        text="Test this connection")
        try:
            status = context.window_manager.buddy_expert_status
        except Exception:
            status = ""
        if (status or "").strip():
            _wrap(layout, status)
        if self.expert_service == "CODEX":
            found = _find_codex()
            if found:
                _wrap(layout, f"Codex program: found ({found}).")
            else:
                _wrap(layout, "Codex command-line program: not located "
                              "from Blender. This does not prove the "
                              "desktop app is missing. If it is already "
                              "installed, restart Blender after Codex "
                              "finishes updating, then test again.")
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
                      "Buddy doesn't offer the login rather than put "
                      "your Claude account at risk. A Claude key is "
                      "different - that's Anthropic's own route for "
                      "other apps - so 'Claude key' above works. "
                      "Local AI needs "
                      "nothing: install a free local AI (for example "
                      "Ollama), pick Local, and everything stays on "
                      "your computer.")
        layout.separator()
        _wrap(layout, "Buddy's screens: Buddy can rearrange "
                      "Blender itself around your job - its own "
                      "Start, Model, Look and Finish screens in "
                      "the tabs at the very top, switching as "
                      "your job's steps change. Set them up in "
                      "this file now; from your next Blender "
                      "start, 'Blender Buddy' is also one of "
                      "the opening choices on the splash "
                      "screen.")
        layout.operator("buddy.build_screens",
                        text="Set up Buddy's screens in this file")
        layout.separator()
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
                "model": _EXPERT_DEFAULT_MODEL, "float": False,
                "service": "KEY"}


def _is_local_url(url):
    return (url or "").startswith(("http://localhost", "http://127.0.0.1"))


def _expert_ready(settings):
    """Can the expert actually be asked right now? A key for key
    services, the Codex program for ChatGPT login, nothing at all
    for a local AI."""
    service = settings.get("service", "KEY")
    if service == "CODEX":
        return _find_codex() is not None
    if service == "LOCAL":
        return True
    return bool(settings.get("key")) or _is_local_url(settings.get("url"))


def _expert_setup_message(settings):
    service = settings.get("service", "KEY")
    if service == "CODEX":
        return ("The expert is set to use your ChatGPT login, but "
                "Buddy couldn't locate OpenAI's Codex command-line program. "
                "This does not mean the desktop app is missing or "
                "that you need to sign in again. Buddy needs its "
                "command-line executable to ask through your login.")
    if service == "LOCAL":
        return ("The expert is set to a local AI, but it didn't "
                "answer. Make sure your local AI (for example "
                "Ollama) is running, then ask again.")
    if service == "CLAUDE":
        return ("The expert is set to Claude, but no Claude key is "
                "pasted yet. Press 'Set up the expert' and paste "
                "your Anthropic key - it stays on your computer. "
                "(A Claude login can't be used in other apps - the "
                "key is Anthropic's way for this.)")
    return ("The expert isn't set up yet. Press 'Set up the expert' "
            "and either paste your own AI key, choose ChatGPT login "
            "(through OpenAI's Codex program), or choose a local AI "
            "- the key stays on your computer.")


def _run_cli(argv, timeout=120):
    """Run one of the AI companies' own programs and return what it
    prints. This is the ONLY way Buddy talks to a subscription
    login: through the company's own program, never through a
    copied login."""
    if os.name == "nt" and str(argv[0]).lower().endswith((".cmd", ".bat")):
        # Windows cannot run a .cmd/.bat file directly - it has to
        # go through the command shell. The npm-installed Codex is
        # a .cmd, which is exactly why "setting up Codex doesn't
        # work" on Windows when a program is launched naively.
        argv = ["cmd", "/c"] + list(argv)
    proc = subprocess.run(argv, capture_output=True, text=True,
                          timeout=timeout, cwd=tempfile.gettempdir())
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-200:]
        raise RuntimeError(tail or "the AI program didn't answer")
    return proc.stdout


def _desktop_codex_candidates(local):
    """The desktop app installs its CLI under a version/hash directory.
    Check only that known location, never recursively scan user files or
    run programs while drawing preferences. Hash names are not versions.
    """
    candidates = []
    root = os.path.join(local, "OpenAI", "Codex", "bin")
    try:
        with os.scandir(root) as entries:
            for entry in entries:
                try:
                    if not entry.is_dir(follow_symlinks=False):
                        continue
                    executable = os.path.join(entry.path, "codex.exe")
                    if os.path.isfile(executable):
                        candidates.append((os.path.getmtime(executable), executable))
                except OSError:
                    continue  # An update may remove a version during discovery.
    except OSError:
        return []
    return [path for _, path in sorted(candidates, reverse=True)]


def _find_codex():
    """Find OpenAI's Codex program wherever it actually landed on
    this computer. The PATH lookup alone misses the normal Windows
    installs (the desktop app and the npm shim don't always
    register a plain 'codex' command), which made the ChatGPT
    route look broken. Returns the full path, or None."""
    for name in ("codex", "codex.cmd", "codex.exe", "codex.bat"):
        found = shutil.which(name)
        if found:
            return found
    if os.name == "nt":
        guesses = []
        appdata = os.environ.get("APPDATA")
        local = os.environ.get("LOCALAPPDATA")
        if appdata:
            guesses += [os.path.join(appdata, "npm", "codex.cmd"),
                        os.path.join(appdata, "npm", "codex.bat")]
        if local:
            guesses += _desktop_codex_candidates(local)
            guesses += [os.path.join(local, "Programs", "Codex",
                                     "codex.exe"),
                        os.path.join(local, "Programs", "OpenAI Codex",
                                     "codex.exe"),
                        os.path.join(local, "Microsoft", "WindowsApps",
                                     "codex.exe")]
        home = os.path.expanduser("~")
        guesses += [os.path.join(home, ".local", "bin", "codex.exe"),
                    os.path.join(home, ".codex", "bin", "codex.exe")]
        for guess in guesses:
            if os.path.isfile(guess):
                return guess
    return None


def _ask_via_codex(system, user):
    path = _find_codex()
    if not path:
        raise RuntimeError(
            "Buddy couldn't locate the Codex command-line program. "
            "An existing desktop installation may not be discoverable "
            "from Blender; this is not a login failure.")
    out = _run_cli([path, "exec", "-s", "read-only",
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
            if kind == "button" and any(a["id"] == ident for a in ACTIONS
                                        if a["id"] not in _stale_map()):
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


def _expert_http_claude(url, key, payload):
    """Anthropic's service speaks a different shape than the
    OpenAI-style one: the key rides in its own header, with the
    service's version header alongside."""
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json",
                 "x-api-key": key,
                 "anthropic-version": _CLAUDE_VERSION})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _ask_via_claude(settings, system, user):
    payload = {"model": settings["model"], "max_tokens": 1024,
               "system": system,
               "messages": [{"role": "user", "content": user}]}
    data = _expert_http_claude(settings["url"], settings["key"], payload)
    parts = [b.get("text", "") for b in data.get("content", [])
             if b.get("type") == "text"]
    text = "\n".join(p for p in parts if p).strip()
    if not text:
        raise RuntimeError("Claude answered with nothing readable")
    return text


def _ask_ai(settings, system, user):
    if settings.get("service") == "CODEX":
        return _ask_via_codex(system, user)
    if settings.get("service") == "CLAUDE":
        return _ask_via_claude(settings, system, user)
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
    bl_description = ("Open the Buddy Expert settings: pick how your "
                      "expert connects (your key, your ChatGPT login "
                      "through Codex, a Claude key, or a local AI)")
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
            if m and any(a["id"] == m.group(1) for a in ACTIONS
                         if a["id"] not in _stale_map()):
                suggested = m.group(1)
            elif not line.strip().upper().startswith("BUTTON:"):
                kept.append(line)
        wm.buddy_answer = "\n".join(kept).strip()
        wm.buddy_suggested = suggested
        first = wm.buddy_answer.split(". ")[0].strip()
        _EXPERT_TIP = (first[:110] + ("..." if len(first) > 110 else ""))
        self.report({"INFO"}, "The expert answered - it's in the panel.")
        return {"FINISHED"}


class BUDDY_OT_test_expert(Operator):
    """Send one tiny test question through the expert route the
    user picked, and say plainly whether it answered. The Codex
    setup failed silently before this existed (owner, 2026-11-12:
    "setting up codex doesnt work") - now there is proof either
    way, in words."""
    bl_idname = "buddy.test_expert"
    bl_label = "Test the Expert Connection"
    bl_description = ("Send one tiny test question through the "
                      "expert route you picked above and show, in "
                      "plain words, whether it answered")

    def execute(self, context):
        settings = _expert_settings()
        service = settings.get("service", "KEY")
        try:
            if service == "CODEX" and _find_codex() is None:
                raise RuntimeError(
                    "Buddy couldn't locate the Codex command-line program. "
                    "An existing desktop installation may not be "
                    "discoverable from Blender; this is not a login "
                    "failure.")
            reply = _ask_ai(settings, "You are a connection test.",
                            "Reply with exactly: BUDDY OK")
            if "BUDDY OK" in (reply or ""):
                msg = ("It works - your expert answered the test "
                       "question. Ask it anything in the panel.")
            else:
                msg = ("Something answered, but not cleanly: "
                       + (reply or "")[:90])
        except Exception as exc:
            msg = f"Not working yet: {exc}"
        try:
            context.window_manager.buddy_expert_status = msg
        except Exception:
            pass
        self.report({"INFO"} if msg.startswith("It works")
                    else {"WARNING"}, msg[:240])
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
    bl_description = "Throw away the expert's plan without running it"
    bl_options = {"REGISTER"}

    def execute(self, context):
        wm = context.window_manager
        wm.buddy_plan = ""
        wm.buddy_plan_summary = ""
        wm.buddy_plan_report = ""
        wm.buddy_plan_retried = ""
        return {"FINISHED"}


def _rounded_rect_points(x0, y0, x1, y1, r, seg=5):
    """The outline of a rounded rectangle, walked counter-clockwise
    corner arc by corner arc. Pure geometry - tested headless,
    because the first fan drawn from it folded into a wedge on
    screen (TRI_FAN is not honoured the way it is documented, so
    the overlay below builds explicit triangles from these)."""
    import math
    pts = []
    for cx, cy, a0 in ((x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90),
                       (x0 + r, y0 + r, 180), (x1 - r, y0 + r, 270)):
        for i in range(seg + 1):
            a = math.radians(a0 + 90 * i / seg)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _fan_tris(cx, cy, pts):
    """A fan around (cx, cy) through pts, as explicit triangles -
    the only primitive form that drew as drawn (v1.0 lesson)."""
    tris = []
    for i in range(len(pts)):
        tris.append((cx, cy))
        tris.append(pts[i])
        tris.append(pts[(i + 1) % len(pts)])
    return tris


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
        # Placement, from real screenshots (v0.9): x=72 clears the
        # editor's left toolbar (at x=14 the toolbar icons were
        # drawn over the card's left edge and its first words);
        # top margin 96 clears the editor's header strip (at 14
        # the title row sat half behind it) AND both lines of the
        # view's own corner text, which is drawn after this card
        # and struck through it at smaller margins.
        x, y = 72, region.height - height - 96

        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        gpu.state.blend_set("ALPHA")
        shader.bind()
        # The card itself: a rounded rectangle (v1.0 - the sharp
        # rectangle read as a debug overlay, not a designed card),
        # built as explicit triangles from the tested outline.
        # Nearly opaque on purpose: at 0.85 the view's own corner
        # text ghosted through the card (seen in screenshots, v0.9).
        batch = batch_for_shader(
            shader, "TRIS",
            {"pos": _fan_tris(x + width / 2, y + height / 2,
                              _rounded_rect_points(x, y, x + width,
                                                   y + height, 10))})
        shader.uniform_float("color", (0.05, 0.05, 0.07, 0.97))
        batch.draw(shader)
        # A gold stripe down its left edge, in the straight section.
        sx0, sy0, sx1, sy1 = x, y + 10, x + 5, y + height - 10
        stripe = batch_for_shader(
            shader, "TRIS",
            {"pos": [(sx0, sy0), (sx1, sy0), (sx1, sy1),
                     (sx0, sy0), (sx1, sy1), (sx0, sy1)]})
        shader.uniform_float("color", (1.0, 0.75, 0.25, 0.95))
        stripe.draw(shader)
        font = 0
        blf.size(font, 12)
        ty = y + height - 18
        for i, line in enumerate(lines):
            blf.color(font, 1.0, 0.85, 0.4, 1.0) if i == 0 else \
                blf.color(font, 0.95, 0.95, 0.95, 1.0)
            blf.position(font, x + 16, ty, 0)
            blf.draw(font, line)
            ty -= 16
        gpu.state.blend_set("NONE")
    except Exception:
        pass


# ----------------------------------------------------------------------------
# The panel
# ----------------------------------------------------------------------------

_WRAP_CAP = 64


def _fit_width(context):
    """How many characters actually fit across the panel right now.
    Blender cuts off (with '...') any label longer than the panel,
    so wrapping has to aim at the real width, not a guess. That was
    learned from actual screenshots of this panel (v0.9): at the
    default sidebar width the old fixed guesses clipped words."""
    try:
        w = context.region.width
    except Exception:
        return 44
    if not w:
        return 44
    return max(26, min(64, int((w - 48) / 6.2)))


def _wrap(layout, text, width=44):
    width = max(20, min(width, _WRAP_CAP))
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
    layout.separator(factor=0.35)


def _hint(context):
    """One true sentence about where you are. It used to point
    at numbered sections ("move it in section 3...") - the
    owner, looking at it on a camera, called it 'very lacking':
    the sections move and hide now, and a camera cannot be
    shaped at all. So: per-kind words, no section numbers,
    never an action the picked thing cannot do."""
    obj = context.object
    if obj is None:
        return ("You have not picked anything yet. Click a thing "
                "in the big window, or start with the tools "
                "above - adding a box is the easiest first "
                "thing to practise on.")
    if context.mode == "EDIT_MESH":
        return (f"You are SHAPING '{obj.name}' - changing its "
                "corners, edges and faces. The tools above are "
                "the shaping tools that fit right now. Press "
                "Tab to go back to moving the whole thing.")
    if obj.type == "CAMERA":
        return ("You have picked the camera. The tools above "
                "look through it and aim it - when the frame "
                "looks right, take the picture.")
    if obj.type == "LIGHT":
        return ("You have picked a light. Move it to change "
                "where it shines; how strong it is and its "
                "colour live in the light's own settings.")
    if obj.type in ("CURVE", "FONT"):
        return (f"You have picked '{obj.name}'. The tools above "
                "are what can be done with it right now - move "
                "it, size it, or turn it into a solid shape you "
                "can shape like anything else.")
    if obj.type != "MESH":
        return (f"You have picked '{obj.name}'. The tools above "
                "are what can be done with it right now.")
    return (f"You have picked '{obj.name}'. The tools above are "
            "its tools for right now - move it, size it, copy "
            "it, or start shaping it.")


class VIEW3D_PT_blender_buddy(Panel):
    bl_idname = "VIEW3D_PT_blender_buddy"
    bl_label = "Blender Buddy - in plain words"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender Buddy"

    def draw(self, context):
        global _WRAP_CAP
        _WRAP_CAP = _fit_width(context)
        layout = self.layout
        wm = context.window_manager
        show_real = getattr(wm, "buddy_show_real", True)

        scene = context.scene
        if not (wm.buddy_query or "").strip():
            ws = getattr(context, "workspace", None)
            if (ws is not None and ws.name == "Buddy Start"
                    and not getattr(scene, "buddy_tour_started",
                                    False)):
                _draw_start(layout, context)
                return
            if getattr(scene, "buddy_tour_started", False):
                _draw_strip(layout, context)
                box = layout.box()
                global _TOUR_TIP_STEP, _EXPERT_TIP
                pkg = _active_package(context)
                steps = pkg["steps"]
                checks, current = tour_state(context)
                done = sum(checks)
                if current != _TOUR_TIP_STEP:
                    _TOUR_TIP_STEP = current
                    if current >= len(steps):
                        _EXPERT_TIP = "You finished it. Ask me anything."
                    else:
                        _EXPERT_TIP = (f"{pkg['name']}, step "
                                       f"{current + 1}: "
                                       f"{steps[current]['title']}.")
                if current >= len(steps):
                    box.label(text=f"You finished: {pkg['name']}",
                              icon="CHECKMARK")
                    skills = "; ".join(s["skill"].split(":")[0]
                                       for s in steps)
                    _wrap(box, "You did every step yourself, in real "
                               "Blender. Skills this project touched: "
                               f"{skills}. Everything after this is "
                               "just more tools, in the drawers below.")
                    box.operator("buddy.tour_hide", text="Hide this")
                else:
                    step = steps[current]
                    box.label(text=f"{pkg['name']} - step "
                                   f"{current + 1} of {len(steps)}",
                              icon="MESH_TORUS")
                    _wrap(box, step["title"])
                    _wrap(box, step["how"])
                    video = step.get("video")
                    if video:
                        op = box.operator(
                            "wm.url_open", text=video["label"],
                            icon="URL")
                        op.url = video["url"]
                    box.prop(scene, "buddy_show_lesson",
                             text="Show the full lesson",
                             toggle=True)
                    if getattr(scene, "buddy_show_lesson",
                               False):
                        _wrap(box, f"The skill: {step['skill']}.")
                        for line in step["teach"]:
                            _wrap(box, line)
                    shown = []
                    for tid in step.get("tools") or []:
                        act = ACTIONS_BY_ID.get(tid)
                        if act and _action_available(act, context):
                            shown.append(act)
                    if shown:
                        box.label(text="Tools for this step",
                                  icon="TOOL_SETTINGS")
                        for act in shown:
                            _draw_action(box, act, show_real)
                    if not checks[current]:
                        _wrap(box, f"Not yet: {step['missing']}")
                    _wrap(box, f"Done so far: {done} of {len(steps)}. "
                               "Do the step up there in Blender - "
                               "this card watches your scene and "
                               "moves on by itself when it's done.")
                    box.operator("buddy.tour_hide", text="Hide for now")

        if not (wm.buddy_query or "").strip():
            _draw_where(layout, context)
            _draw_heads_up(layout, context)

        if not (wm.buddy_query or "").strip():
            box = layout.box()
            box.label(text="For right now", icon="INFO")
            _wrap(box, _hint(context))
            facts = _scene_facts(context)
            for act in _now_deck(context, facts=facts):
                _draw_action(box, act, show_real)
            _wrap(box, f"Buddy is showing the "
                       f"{len(_available_actions(context, facts))} "
                       f"tools (of {len(ACTIONS)}) that can be used "
                       f"right now. The rest appear the moment "
                       f"they're usable - pick something, switch "
                       f"mode, and this panel keeps up. Everything "
                       f"Blender has is always in the index at the "
                       f"bottom.")


        if not (wm.buddy_query or "").strip():
            box = layout.box()
            box.label(text="Buddy Expert", icon="USER")
            settings = _expert_settings()
            if not _expert_ready(settings):
                _wrap(box, "Your own AI expert lives here. Connect "
                           "it with your key, your ChatGPT login "
                           "(through Codex), a Claude key, or a free "
                           "local AI. Ask in your own words and it "
                           "answers for YOUR scene.")
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

        stale = _stale_map()
        if stale:
            box = layout.box()
            box.label(text="This Blender changed some tools",
                      icon="ERROR")
            names = "; ".join(ACTIONS_BY_ID[i]["plain"] for i in stale)
            _wrap(box, f"{len(stale)} of Buddy's buttons were made "
                       f"for an older Blender and don't match this "
                       f"one (Blender {bpy.app.version_string}), so "
                       f"they're hidden instead of failing on you: "
                       f"{names}. Everything else works as normal, "
                       f"and every tool this Blender actually has is "
                       f"in the search below.")

        box = layout.box()
        box.label(text="What do you want to do?", icon="VIEWZOOM")
        box.prop(wm, "buddy_query", text="")
        query = getattr(wm, "buddy_query", "")
        if query.strip():
            hits = search_actions(query, available_only=True,
                                  context=context)
            if hits:
                for act in hits[:10]:
                    _draw_action(box, act, show_real)
            else:
                _wrap(box, "Nothing you can use right now matches "
                           "that. It may need a picked thing or a "
                           "different mode first - or try everyday "
                           "words: round, copy, hole, smooth, move, "
                           "thicker, colour, delete.")
        box.prop(wm, "buddy_show_real",
                 text="Also show Blender's real names")

        # The tool sections live in their own collapsible panels
        # below this one (SECTION_PANELS) - a tidy list of drawers,
        # not one endless scrolling page.

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



# ------------------------------------------------------------
# What can be used RIGHT NOW. The redesign rule (owner,
# 2026-11-12): "no need for tools that are not needed or not
# usable at the moment". Every drawer, the search and the
# "For right now" deck filter through _action_available: a
# tool appears only when the current scene, mode and picked
# thing can actually use it. A tool that can't run yet is not
# shown greyed or dead - it is simply not there, and it
# appears the moment it becomes usable (pick a thing, enter
# the mode, add a modifier). Nothing is lost: the complete
# index still holds every operator this Blender has, and a
# plan the expert makes may still use steps that become
# usable as the plan runs.

_MODIFIER_TYPES = {"MESH", "CURVE", "SURFACE", "FONT", "LATTICE"}
_MATERIAL_TYPES = {"MESH", "CURVE", "SURFACE", "FONT", "META",
                   "VOLUME", "GPENCIL", "GREASE_PENCIL"}
_MODE_TARGETS = {
    "EDIT": {"MESH", "CURVE", "SURFACE", "FONT", "ARMATURE",
             "LATTICE", "META"},
    "SCULPT": {"MESH"},
    "VERTEX_PAINT": {"MESH"},
    "TEXTURE_PAINT": {"MESH"},
}
_ADD_OPS = {"object.text_add", "object.light_add",
            "object.camera_add", "object.empty_add"}


def _scene_facts(context):
    """A small, defensive snapshot of where the user is."""
    obj = getattr(context, "object", None)
    scene = getattr(context, "scene", None)
    facts = {"mode": getattr(context, "mode", "OBJECT") or "OBJECT",
             "obj": obj,
             "type": getattr(obj, "type", None),
             "selected": 0,
             "modifiers": 0,
             "has_camera": bool(
                 scene is not None
                 and getattr(scene, "camera", None))}
    try:
        facts["selected"] = len(context.selected_objects or [])
    except Exception:
        facts["selected"] = 1 if obj else 0
    if obj is not None:
        try:
            facts["modifiers"] = len(obj.modifiers)
        except Exception:
            facts["modifiers"] = 0
    return facts


def _action_available(act, context, facts=None):
    """True when this tool can actually be used in this moment."""
    if act["id"] in _stale_map():
        return False
    f = facts or _scene_facts(context)
    mode, obj, otype = f["mode"], f["obj"], f["type"]
    needs = act.get("needs")
    if needs == "object" and obj is None:
        return False
    if needs == "two" and f["selected"] < 2:
        return False
    if needs == "edit" and mode != "EDIT_MESH":
        return False
    kind, target = act["kind"], act["target"]
    if kind == "modifier":
        return (otype in _MODIFIER_TYPES
                and mode in ("OBJECT", "EDIT_MESH"))
    if kind == "mode":
        return otype in _MODE_TARGETS.get(target, set())
    if kind == "tool":
        if target in ("builtin.loop_cut", "builtin.knife"):
            return mode == "EDIT_MESH"
        if target == "builtin.select_box":
            return True
        return (obj is not None and "SCULPT" not in mode
                and "PAINT" not in mode)
    if kind == "op":
        if (target.startswith(("mesh.primitive_",
                               "curve.primitive_"))
                or target in _ADD_OPS):
            return mode == "OBJECT"
        if target == "object.join":
            return f["selected"] >= 2
        if target in ("object.shade_smooth", "object.shade_flat"):
            return otype in ("MESH", "CURVE", "SURFACE")
        if target == "view3d.view_camera":
            return f["has_camera"]
        return True
    if kind == "custom":
        if target == "apply_modifiers":
            return f["modifiers"] > 0 and mode == "OBJECT"
        if target == "colour":
            return otype in _MATERIAL_TYPES
        if target in ("apply_transforms", "origin_middle",
                      "centre_world"):
            return obj is not None and mode == "OBJECT"
        return True
    return True


def _available_actions(context, facts=None):
    f = facts or _scene_facts(context)
    return [a for a in ACTIONS if _action_available(a, context, f)]


def _section_actions(section, context, facts=None):
    f = facts or _scene_facts(context)
    return [a for a in ACTIONS
            if a["section"] == section
            and _action_available(a, context, f)]


_NOW_ORDER = {
    "empty": ["add_cube", "add_ball", "add_tube", "add_ring",
              "add_words", "see_everything", "find_everything",
              "add_camera", "add_sun"],
    "object": ["tool_move", "tool_size", "tool_turn",
               "start_shaping", "copy_it", "give_colour",
               "round_all_edges", "make_smoother",
               "give_thickness", "remember_pose", "take_picture"],
    "edit": ["pull_face", "inset_face", "round_edge", "loop_cut",
             "knife", "split_faces", "fill_face", "fix_faces",
             "start_shaping"],
    "sculpt": ["paint_it", "start_shaping", "take_picture"],
    "busy": ["tool_move", "start_shaping", "take_picture"],
}


def _now_deck(context, limit=8, facts=None):
    """The 'For right now' deck: the few tools this moment calls
    for, in the order a person reaches for them, filled out with
    whatever else is usable right now."""
    f = facts or _scene_facts(context)
    if f["obj"] is None:
        key = "empty"
    elif f["mode"] == "EDIT_MESH":
        key = "edit"
    elif f["mode"] == "SCULPT":
        key = "sculpt"
    elif f["mode"] == "OBJECT":
        key = "object"
    else:
        key = "busy"
    avail = {a["id"]: a for a in _available_actions(context, f)}
    deck = [avail[i] for i in _NOW_ORDER[key] if i in avail]
    have = {a["id"] for a in deck}
    for act in ACTIONS:
        if len(deck) >= limit:
            break
        if act["id"] in avail and act["id"] not in have:
            deck.append(act)
            have.add(act["id"])
    return deck[:limit]


def _make_section_panel(index, section):
    """One collapsible drawer per tool section, under the main
    panel. Until v1.0 every section was drawn as a box in one long
    panel - a scrolling document. Drawers make it an app: a short
    list of named sections, each opening only when wanted."""
    def draw(self, context):
        global _WRAP_CAP
        _WRAP_CAP = _fit_width(context)
        wm = context.window_manager
        show_real = getattr(wm, "buddy_show_real", True)
        for act in _section_actions(section, context):
            _draw_action(self.layout, act, show_real)

    def poll(cls, context):
        # A drawer with nothing usable in it right now does not
        # appear at all - it comes back when its tools do.
        try:
            return bool(_section_actions(section, context))
        except Exception:
            return True

    attrs = {
        "bl_idname": f"VIEW3D_PT_buddy_sec_{index}",
        "bl_label": section,
        "bl_space_type": "VIEW_3D",
        "bl_region_type": "UI",
        "bl_category": "Blender Buddy",
        "bl_parent_id": "VIEW3D_PT_blender_buddy",
        "bl_order": index,
        "draw": draw,
        "poll": classmethod(poll),
    }
    if index > 0:
        attrs["bl_options"] = {"DEFAULT_CLOSED"}
    return type(f"VIEW3D_PT_buddy_sec_{index}", (Panel,), attrs)


SECTION_PANELS = tuple(
    _make_section_panel(i, s) for i, s in enumerate(SECTIONS))


class VIEW3D_PT_buddy_projects(Panel):
    """Guided projects live in their own drawer, closed until
    wanted (owner, 2026-11-12: "the donut tutorial is
    permanent"). The panel opens on the tools of the moment; a
    project shows its step card at the top of the main panel
    only while it is actually running."""
    bl_label = "Learn by doing: projects & ways of working"
    bl_idname = "VIEW3D_PT_buddy_projects"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender Buddy"
    bl_parent_id = "VIEW3D_PT_blender_buddy"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = len(SECTIONS) + 1

    def draw(self, context):
        global _WRAP_CAP
        _WRAP_CAP = _fit_width(context)
        layout = self.layout
        if getattr(context.scene, "buddy_tour_started", False):
            pkg = _active_package(context)
            _wrap(layout, f"Running now: {pkg['name']} - its step "
                          "card is at the top of the main panel.")
            layout.operator("buddy.tour_hide",
                            text="Hide the project card")
            return
        groups = [
            ("Guided projects",
             [p for p in PACKAGES if p.get("kind") != "flow"]),
            ("Ways of working - how the community does the job",
             [p for p in PACKAGES if p.get("kind") == "flow"]),
        ]
        for title, pkgs in groups:
            if not pkgs:
                continue
            layout.label(text=title, icon="INFO")
            for pkg in pkgs:
                _wrap(layout, f"{pkg['name']} - {pkg['byline']}")
                _wrap(layout, pkg["intro"])
                op = layout.operator("buddy.tour_start",
                                     text=f"Start: {pkg['name']}",
                                     icon="MESH_TORUS")
                op.package = pkg["id"]

# ----------------------------------------------------------------------------
# The complete redesign: Buddy inside Blender itself (v3).
# Until v2 everything Buddy made lived in one sidebar panel -
# the owner, using it: "all the controls are still in their
# default place, this is just an extra window not a blender
# interface redesign". So v3 moves into Blender's own furniture:
#
# - An APP TEMPLATE ("Blender Buddy", installed into the user's
#   app-template folder): Blender can open AS Buddy - its own
#   Start / Model / Look / Finish workspaces and nothing else.
# - STEP-CONDUCTING: while a job runs, each step re-forms the
#   whole screen - the workspace switches, and the viewport
#   shading and camera view follow. (Mode is deliberately NOT
#   conducted: steps like the donut's icing begin in Object
#   Mode and enter Edit Mode mid-step, in their own words -
#   the step's tools switch mode when pressed, as they have
#   since v1.) Buddy conducts the application, not just its
#   own region.
# - An in-viewport PIE of the moment's tools on the ` key, and
#   a "Buddy tools" button + job progress in the 3D view's own
#   header bar.
# - Plain-words tools in Blender's OWN toolbar (T): the same
#   operators as the native Extrude / Loop Cut / Knife tools,
#   under names a beginner already understands.
# Everything still layers over Blender; disabling Buddy
# changes nothing, and none of it depends on the template -
# in a plain file the same screens can be built on request.
# ----------------------------------------------------------------------------

BUDDY_SCREENS = ("Buddy Start", "Buddy Model", "Buddy Look",
                 "Buddy Finish")

_SCREEN_AREA_SWAPS = {
    "Buddy Start": {},
    "Buddy Model": {},
    "Buddy Look": {"PROPERTIES": "NODE_EDITOR",
                   "DOPESHEET_EDITOR": "IMAGE_EDITOR"},
    "Buddy Finish": {"OUTLINER": "IMAGE_EDITOR"},
}

# (package, step) -> (workspace, viewport shading, view, mode)
_STEP_SCREENS = {
    ("donut", 0): ("Buddy Model", None, None, None),
    ("donut", 1): ("Buddy Model", None, None, None),
    ("donut", 2): ("Buddy Model", None, None, None),
    ("donut", 3): ("Buddy Finish", "RENDERED", None, None),
    ("donut", 4): ("Buddy Look", "RENDERED", None, None),
    ("donut", 5): ("Buddy Look", None, None, None),
    ("donut", 6): ("Buddy Model", None, None, None),
    ("donut", 7): ("Buddy Finish", "RENDERED", "CAMERA", None),
    ("hard_surface", 0): ("Buddy Model", None, None, None),
    ("hard_surface", 1): ("Buddy Model", None, None, None),
    ("hard_surface", 2): ("Buddy Model", None, None, None),
    ("hard_surface", 3): ("Buddy Model", None, None, None),
    ("hard_surface", 4): ("Buddy Model", None, None, None),
    ("hard_surface", 5): ("Buddy Model", None, None, None),
    ("hard_surface", 6): ("Buddy Model", None, None, None),
    ("hard_surface", 7): ("Buddy Look", "RENDERED", None, None),
    ("look_real", 0): ("Buddy Model", None, None, None),
    ("look_real", 1): ("Buddy Model", None, None, None),
    ("look_real", 2): ("Buddy Finish", None, "CAMERA", None),
    ("look_real", 3): ("Buddy Look", "RENDERED", None, None),
    ("look_real", 4): ("Buddy Look", None, None, None),
    ("look_real", 5): ("Buddy Finish", "RENDERED", "CAMERA", None),
    ("look_real", 6): ("Buddy Finish", None, None, None),
    ("print_ready", 0): ("Buddy Model", None, None, None),
    ("print_ready", 1): ("Buddy Model", None, None, None),
    ("print_ready", 2): ("Buddy Model", None, None, None),
    ("print_ready", 3): ("Buddy Model", None, None, None),
    ("print_ready", 4): ("Buddy Finish", None, None, None),
}

_CONDUCT = {"key": None, "scheduled": False}
_BUILDING = False
_BUDDY_KEYMAPS = []


def _conduct_spec(context):
    scene = getattr(context, "scene", None)
    if scene is None or not getattr(scene, "buddy_tour_started",
                                    False):
        return None, None
    pkg = _active_package(context)
    _checks, current = tour_state(context)
    if current >= len(pkg["steps"]):
        return (pkg["id"], "done"), ("Buddy Finish", None, None,
                                      None)
    return ((pkg["id"], current),
            _STEP_SCREENS.get((pkg["id"], current)))


def _conduct_check(*_args):
    """Watch for the job's step changing; when it does, the
    whole screen re-forms for the new step. Cheap when nothing
    changed, and never allowed to raise."""
    if _BUILDING:
        # A reference build is mid-flight: its half-made scene
        # must not conduct anything. The key stays unconsumed,
        # so the finished step conducts when the build ends.
        return
    try:
        key, spec = _conduct_spec(bpy.context)
        if key == _CONDUCT["key"]:
            return
        _CONDUCT["key"] = key
        if spec is None or _CONDUCT["scheduled"]:
            return
        _CONDUCT["scheduled"] = True
        bpy.app.timers.register(_conduct_apply,
                                first_interval=0.05)
    except Exception:
        pass


def _conduct_apply():
    _CONDUCT["scheduled"] = False
    if _BUILDING:
        _CONDUCT["key"] = None
        return None
    try:
        context = bpy.context
        _key, spec = _conduct_spec(context)
        if spec is None:
            return None
        ws_name, shading, view, mode = spec
        window = getattr(context, "window", None)
        if window is None:
            return None
        ws = bpy.data.workspaces.get(ws_name)
        if ws is not None and window.workspace != ws:
            window.workspace = ws
        if shading or view:
            for area in window.screen.areas:
                if area.type != "VIEW_3D":
                    continue
                for space in area.spaces:
                    if space.type != "VIEW_3D":
                        continue
                    if shading:
                        try:
                            space.shading.type = shading
                        except Exception:
                            pass
                    if view == "CAMERA" and space.region_3d:
                        try:
                            space.region_3d.view_perspective = \
                                "CAMERA"
                        except Exception:
                            pass
        if mode == "EDIT" and context.mode == "OBJECT":
            obj = context.object
            if obj is not None and obj.type == "MESH":
                bpy.ops.object.mode_set(mode="EDIT")
    except Exception:
        pass
    return None


_SCREENS_JOB = {"stage": "idle", "base": None, "current": None,
                "created": []}


def _screens_tick():
    """Build Buddy's screens one UI tick at a time. A
    workspace's screen only accepts edits that survive saving
    once the workspace has actually been shown, and switching
    to it settles a tick later - so: switch to the base screen,
    settle, copy it, settle, then edit the copy's screen."""
    job = _SCREENS_JOB
    try:
        context = bpy.context
        window = getattr(context, "window", None)
        if window is None:
            job["stage"] = "idle"
            return None
        if job["stage"] == "to_base":
            base = bpy.data.workspaces.get(job["base"] or "")
            if base is not None:
                window.workspace = base
            job["stage"] = "dup"
            return 0.35
        if job["stage"] == "dup":
            missing = [n for n in BUDDY_SCREENS
                       if n not in bpy.data.workspaces]
            if not missing:
                job["stage"] = "idle"
                return None
            name = missing[0]
            before = {w.name for w in bpy.data.workspaces}
            bpy.ops.workspace.duplicate()
            fresh = [w for w in bpy.data.workspaces
                     if w.name not in before]
            if not fresh:
                job["stage"] = "idle"
                return None
            fresh[0].name = name
            window.workspace = fresh[0]
            job["current"] = name
            job["stage"] = "edit"
            return 0.35
        if job["stage"] == "edit":
            swaps = _SCREEN_AREA_SWAPS[job["current"]]
            for area in window.screen.areas:
                if area.type in swaps:
                    try:
                        area.type = swaps[area.type]
                    except Exception:
                        pass
                if area.type == "VIEW_3D":
                    for space in area.spaces:
                        if space.type == "VIEW_3D":
                            space.show_region_ui = True
            job["created"].append(job["current"])
            if all(n in bpy.data.workspaces
                   for n in BUDDY_SCREENS):
                job["stage"] = "idle"
                return None
            job["stage"] = "to_base"
            return 0.1
    except Exception:
        job["stage"] = "idle"
    return None


def _build_screens(context):
    """Start building Buddy's screens in this file (they appear
    in the top tabs one by one over a couple of seconds - see
    _screens_tick for why it can't be instant). Existing
    workspaces, yours and Buddy's, are never touched. Returns
    the Buddy screens already present."""
    window = getattr(context, "window", None)
    if window is None:
        return []
    present = [n for n in BUDDY_SCREENS
               if n in bpy.data.workspaces]
    if len(present) == len(BUDDY_SCREENS):
        return present
    if _SCREENS_JOB["stage"] == "idle":
        _SCREENS_JOB["base"] = window.workspace.name
        _SCREENS_JOB["created"] = []
        _SCREENS_JOB["stage"] = "to_base"
        if not bpy.app.timers.is_registered(_screens_tick):
            bpy.app.timers.register(_screens_tick,
                                    first_interval=0.1)
    return present


class BUDDY_OT_build_screens(Operator):
    bl_idname = "buddy.build_screens"
    bl_label = "Set Up Buddy's Screens"
    bl_description = ("Give this file Buddy's own screens - "
                      "Start, Model, Look and Finish - in the "
                      "workspace tabs at the very top. Your own "
                      "screens are never touched")
    bl_options = {"REGISTER"}

    def execute(self, context):
        present = _build_screens(context)
        if len(present) == len(BUDDY_SCREENS):
            self.report({"INFO"}, "Buddy's screens are already "
                                  "set up in this file.")
            ws = bpy.data.workspaces.get("Buddy Start")
            if ws is not None and getattr(context, "window",
                                          None):
                context.window.workspace = ws
        else:
            self.report({"INFO"}, "Buddy is building its "
                                  "screens - watch the tabs at "
                                  "the very top: Start, Model, "
                                  "Look and Finish appear one "
                                  "by one.")
        return {"FINISHED"}


def _template_source():
    try:
        d = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "templates", "Blender_Buddy")
        return d if os.path.isdir(d) else None
    except Exception:
        return None


def _install_template():
    """Put the Buddy app template where Blender looks for it,
    so from the next start Blender offers 'Blender Buddy' as
    one of its opening choices. Only copies what changed."""
    src = _template_source()
    if not src:
        return
    try:
        dst = bpy.utils.user_resource(
            "SCRIPTS",
            path="startup/bl_app_templates_user/Blender_Buddy",
            create=True)
        for name in ("startup.blend", "__init__.py"):
            s = os.path.join(src, name)
            t = os.path.join(dst, name)
            if os.path.isfile(s) and (
                    not os.path.isfile(t)
                    or not filecmp.cmp(s, t, shallow=False)):
                shutil.copy2(s, t)
    except Exception:
        pass

# ----------------------------------------------------------------
# The plain-words layer (v3.1): where am I, and what is about
# to bite me. The owner's standard, 2026-11-13: the redesign
# is for the average person, and the gaps are the concepts
# Blender never explains - modes, the origin, the 3D cursor,
# picked vs in-charge. So Buddy says where you are in plain
# words at all times, and watches for the invisible traps,
# naming each in plain words at the moment it bites, with the
# fix attached. Trap text avoids Blender's jargon word when a
# plain word exists: the origin is "the spin point", the 3D
# cursor is "the target".


def _bbox_world(obj):
    """(centre, size, low, high) of the object's box, in the
    world's measurements."""
    from mathutils import Vector
    corners = [obj.matrix_world @ Vector(c)
               for c in obj.bound_box]
    lo = Vector((min(c.x for c in corners),
                 min(c.y for c in corners),
                 min(c.z for c in corners)))
    hi = Vector((max(c.x for c in corners),
                 max(c.y for c in corners),
                 max(c.z for c in corners)))
    return (lo + hi) * 0.5, hi - lo, lo, hi


def _where_am_i(context):
    """(headline, sub): where you are, in plain words. Never
    Blender's bare mode names - a mode is explained by what
    you can do in it and how to get back."""
    obj = context.object
    name = obj.name if obj else None
    mode = context.mode
    if mode == "EDIT_MESH" and obj:
        return (f"You're reshaping '{name}' itself",
                "You're moving its corners, edges and faces - "
                "that's why your tools changed. This is the "
                "shaping half of Blender; nothing is broken.")
    if mode.startswith("SCULPT") and obj:
        return (f"You're sculpting '{name}'",
                "Pushing its surface around like clay. The "
                "brush is sized in the bar above the big "
                "window.")
    if mode == "POSE" and obj:
        return (f"You're posing '{name}'",
                "You're moving its bones and the body "
                "follows. You're not changing the things "
                "themselves.")
    if mode == "PAINT_WEIGHT" and obj:
        return (f"You're painting bone strength on '{name}'",
                "Where it's red, the bone pulls hard. Where "
                "it's blue, the bone barely moves it.")
    if mode in ("PAINT_VERTEX", "PAINT_TEXTURE") and obj:
        return (f"You're painting on '{name}'",
                "Colour goes straight onto the thing itself.")
    if mode == "PARTICLE_EDIT" and obj:
        return (f"You're combing the hair on '{name}'",
                "Each stroke moves the strands under the "
                "brush.")
    if mode != "OBJECT" and obj:
        return (f"You're working on '{name}' up close",
                "A close-up mode is on - the button below "
                "takes you back to moving whole things.")
    picked = [o for o in context.selected_objects]
    if obj is None:
        return ("You're moving whole things",
                "Nothing is picked yet. Click a thing in the "
                "big window to pick it, then it can be moved, "
                "sized and turned as one piece.")
    if len(picked) > 1:
        return (f"You're moving whole things - '{name}' is "
                "in charge",
                f"{len(picked)} things are picked. The paler "
                "orange one is in charge: it's the one tools "
                "measure from, and the one whose settings "
                "you see. The others just come along.")
    return (f"You're moving whole things - '{name}' is picked",
            "It moves, sizes and turns as one piece. To "
            "change its actual shape, start shaping it - "
            "the button below - and you move its corners "
            "instead.")


def _is_shown(obj):
    if obj.hide_viewport:
        return False
    try:
        return not obj.hide_get()
    except Exception:
        return True


def _traps(context):
    """The invisible traps, in the order they bite. Each is a
    dict: key (its mute identity), text (plain words), fixes
    (a list of (operator, button text)). Computed live from
    the scene every draw - no state that can go stale."""
    out = []
    scene = context.scene
    if scene is None:
        return out
    objs = list(scene.objects)
    obj = context.object
    if objs and not any(_is_shown(o) for o in objs):
        out.append({
            "key": "all_hidden",
            "text": "Everything you've made is hidden right "
                    "now - that's why the big window looks "
                    "empty. Your work is still here.",
            "fixes": [("buddy.show_everything",
                       "Show everything")],
        })
    if obj is not None and obj.type == "MESH":
        try:
            centre, size, lo, hi = _bbox_world(obj)
            biggest = max(size.x, size.y, size.z)
            origin = obj.matrix_world.translation
            if biggest > 0.001 and \
                    (origin - centre).length > 0.6 * biggest:
                out.append({
                    "key": f"origin_far|{obj.name}",
                    "text": f"'{obj.name}' turns around its "
                            "spin point - the little orange "
                            "dot - and that dot is sitting "
                            "away from the thing itself. "
                            "That's why it swings in a wide "
                            "circle when you turn it.",
                    "fixes": [
                        ("buddy.origin_center",
                         "Put the spin point in the middle"),
                        ("buddy.origin_bottom",
                         "Put the spin point at the bottom")],
                })
        except Exception:
            pass
    if obj is not None:
        sx, sy, sz = obj.scale
        if min(sx, sy, sz) < 0:
            out.append({
                "key": f"mirrored|{obj.name}",
                "text": f"'{obj.name}' has a minus in its "
                        "size numbers, which flips it "
                        "inside-out. Some tools will treat "
                        "it wrong until the flip is locked "
                        "in.",
                "fixes": [("buddy.lock_in",
                           "Lock in the flip")],
            })
        elif max(abs(sx - 1), abs(sy - 1),
                 abs(sz - 1)) > 0.02:
            out.append({
                "key": f"scale_open|{obj.name}",
                "text": f"'{obj.name}' is stretched by its "
                        f"size numbers ({sx:g}, {sy:g}, "
                        f"{sz:g}) but the stretch isn't "
                        "locked in yet. Until it is, some "
                        "shaping tools - like rounding an "
                        "edge - come out uneven.",
                "fixes": [("buddy.lock_in",
                           "Lock in the size and turn")],
            })
    try:
        cur = scene.cursor.location
        far = cur.length > 4.0
        if far and obj is not None:
            far = (cur - obj.matrix_world.translation
                   ).length > 4.0
        if far:
            fixes = [("buddy.cursor_home",
                      "Bring the target back to the middle")]
            if obj is not None:
                fixes.append(
                    ("buddy.cursor_to_picked",
                     f"Put the target on '{obj.name}'"))
            out.append({
                "key": "cursor_far",
                "text": "The target - the red-and-white "
                        "ring - is a long way from the "
                        "middle of things. New things you "
                        "add appear at the target, so they'd "
                        "land way over there.",
                "fixes": fixes,
            })
    except Exception:
        pass
    return out


def _muted_keys(context):
    try:
        return set(json.loads(
            getattr(context.window_manager, "buddy_muted",
                    "[]") or "[]"))
    except Exception:
        return set()


def _visible_traps(context):
    muted = _muted_keys(context)
    return [t for t in _traps(context)
            if t["key"] not in muted][:2]


def _draw_where(layout, context):
    box = layout.box()
    box.label(text="Where you are", icon="INFO")
    headline, sub = _where_am_i(context)
    _wrap(box, headline)
    _wrap(box, sub)
    obj = context.object
    if context.mode != "OBJECT":
        box.operator("buddy.mode_back",
                     text="Back to moving whole things")
    elif obj is not None and obj.type == "MESH":
        op = box.operator("buddy.action",
                          text=f"Start shaping '{obj.name}'")
        op.action_id = "start_shaping"


def _draw_heads_up(layout, context):
    for trap in _visible_traps(context):
        box = layout.box()
        box.label(text="Heads up", icon="ERROR")
        _wrap(box, trap["text"])
        for idname, text in trap["fixes"]:
            box.operator(idname, text=text)
        op = box.operator("buddy.mute_trap", text="Got it")
        op.trap_key = trap["key"]


def _only_active(context, call):
    """Run call() with just the active thing selected and in
    the moving-whole-things mode, then put the selection and
    mode back. Several of Blender's fix-it operators only run
    that way, and a beginner should never have to know."""
    obj = context.object
    keep = [o for o in context.selected_objects]
    was = context.mode
    if was != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    context.view_layer.objects.active = obj
    try:
        call()
    finally:
        bpy.ops.object.select_all(action="DESELECT")
        for other in keep:
            try:
                other.select_set(True)
            except Exception:
                pass
        context.view_layer.objects.active = obj
        if was == "EDIT_MESH":
            try:
                bpy.ops.object.mode_set(mode="EDIT")
            except Exception:
                pass


class BUDDY_OT_mode_back(Operator):
    bl_idname = "buddy.mode_back"
    bl_label = "Back to moving whole things"
    bl_description = ("Leave the close-up mode you're in and "
                      "go back to moving whole things")

    @classmethod
    def poll(cls, context):
        return (context.object is not None
                and context.mode != "OBJECT")

    def execute(self, context):
        bpy.ops.object.mode_set(mode="OBJECT")
        self.report({"INFO"}, "Back to moving whole things.")
        return {"FINISHED"}


class BUDDY_OT_origin_center(Operator):
    bl_idname = "buddy.origin_center"
    bl_label = "Put the spin point in the middle"
    bl_description = ("Move this thing's spin point - the "
                      "point it turns and grows around, the "
                      "little orange dot (Blender calls it "
                      "the origin) - into the middle of the "
                      "thing")
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        obj = context.object
        _only_active(context, lambda: bpy.ops.object.origin_set(
            type="ORIGIN_GEOMETRY", center="BOUNDS"))
        self.report({"INFO"}, f"The spin point of "
                              f"'{obj.name}' is in its "
                              "middle now.")
        return {"FINISHED"}


class BUDDY_OT_origin_bottom(Operator):
    bl_idname = "buddy.origin_bottom"
    bl_label = "Put the spin point at the bottom"
    bl_description = ("Move this thing's spin point to the "
                      "bottom middle of the thing, so it "
                      "stands on the ground the way you'd "
                      "expect")
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        from mathutils import Vector
        obj = context.object
        centre, size, lo, hi = _bbox_world(obj)
        target = Vector((centre.x, centre.y, lo.z))
        cursor = context.scene.cursor
        saved = cursor.location.copy()

        def place():
            cursor.location = target
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")

        try:
            _only_active(context, place)
        finally:
            cursor.location = saved
        self.report({"INFO"}, f"The spin point of "
                              f"'{obj.name}' is at its "
                              "bottom now.")
        return {"FINISHED"}


class BUDDY_OT_cursor_home(Operator):
    bl_idname = "buddy.cursor_home"
    bl_label = "Bring the target back to the middle"
    bl_description = ("Put the target (the red-and-white "
                      "ring - Blender calls it the 3D cursor) "
                      "back at the middle of the world, where "
                      "new things appear sensibly")
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        context.scene.cursor.location = (0.0, 0.0, 0.0)
        self.report({"INFO"}, "The target is back in the "
                              "middle.")
        return {"FINISHED"}


class BUDDY_OT_cursor_to_picked(Operator):
    bl_idname = "buddy.cursor_to_picked"
    bl_label = "Put the target on the picked thing"
    bl_description = ("Put the target on the picked thing, "
                      "so the next thing you add appears "
                      "right there")
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        obj = context.object
        context.scene.cursor.location = \
            obj.matrix_world.translation
        self.report({"INFO"}, f"The target is on "
                              f"'{obj.name}' now.")
        return {"FINISHED"}


class BUDDY_OT_lock_in(Operator):
    bl_idname = "buddy.lock_in"
    bl_label = "Lock in the size and turn"
    bl_description = ("Make this thing's current size and "
                      "turn its real ones (Blender calls "
                      "this applying the transform), so "
                      "every tool treats it the way it "
                      "looks")
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.object is not None

    def execute(self, context):
        obj = context.object
        _only_active(context, lambda: bpy.ops.object
                     .transform_apply(location=False,
                                      rotation=True,
                                      scale=True))
        self.report({"INFO"}, f"'{obj.name}' is locked in "
                              "at the size and turn it "
                              "shows.")
        return {"FINISHED"}


class BUDDY_OT_show_everything(Operator):
    bl_idname = "buddy.show_everything"
    bl_label = "Show everything"
    bl_description = "Bring back everything you've hidden"

    def execute(self, context):
        shown = 0
        for obj in context.scene.objects:
            if not _is_shown(obj):
                shown += 1
            obj.hide_viewport = False
            try:
                obj.hide_set(False)
            except Exception:
                pass
        self.report({"INFO"}, f"Showing everything "
                              f"({shown} thing(s) were "
                              "hidden).")
        return {"FINISHED"}


class BUDDY_OT_mute_trap(Operator):
    bl_idname = "buddy.mute_trap"
    bl_label = "Got it"
    bl_description = "Stop showing this one heads-up"

    trap_key: StringProperty(default="")

    def execute(self, context):
        keys = _muted_keys(context)
        keys.add(self.trap_key)
        context.window_manager.buddy_muted = json.dumps(
            sorted(keys))
        return {"FINISHED"}


class VIEW3D_MT_buddy_pie(Menu):
    bl_idname = "VIEW3D_MT_buddy_pie"
    bl_label = "Buddy - for right now"

    def draw(self, context):
        pie = self.layout.menu_pie()
        for act in _now_deck(context, limit=8):
            if act.get("icon"):
                op = pie.operator("buddy.action",
                                  text=act["plain"],
                                  icon=act["icon"])
            else:
                op = pie.operator("buddy.action",
                                  text=act["plain"])
            op.action_id = act["id"]


class BUDDY_OT_pie(Operator):
    bl_idname = "buddy.pie"
    bl_label = "Buddy Tools for Right Now"
    bl_description = ("Open the tools for this moment in a "
                      "circle around your mouse - the same deck "
                      "as the panel, without leaving the big "
                      "window (key: the ` key, top-left)")
    bl_options = {"REGISTER"}

    def execute(self, context):
        bpy.ops.wm.call_menu_pie(name="VIEW3D_MT_buddy_pie")
        return {"FINISHED"}


def _buddy_header_draw(self, context):
    """Buddy in the 3D view's own header: the pie button, and
    the running job's progress where Blender's own bar is."""
    try:
        layout = self.layout
        row = layout.row(align=True)
        row.operator("buddy.pie", text="Buddy tools",
                     icon="TOOL_SETTINGS")
        scene = getattr(context, "scene", None)
        if scene is not None and getattr(
                scene, "buddy_tour_started", False):
            pkg = _active_package(context)
            _c, current = tour_state(context)
            if current < len(pkg["steps"]):
                row.label(text=f"{pkg['name']}: step "
                               f"{current + 1} of "
                               f"{len(pkg['steps'])}")
            else:
                row.label(text=f"{pkg['name']}: finished")
    except Exception:
        pass


def _draw_action_compact(layout, act):
    if act.get("icon"):
        op = layout.operator("buddy.action", text=act["plain"],
                             icon=act["icon"])
    else:
        op = layout.operator("buddy.action", text=act["plain"])
    op.action_id = act["id"]


def _draw_strip(layout, context):
    """The slim step strip, drawn at the top of Buddy's main
    panel while a job runs: where you are and the moment's
    first tools, in one glance. (It began as its own panel;
    Blender would not promise to draw a second top-level panel
    above the main one, so the strip lives at the top of the
    main panel instead - same sight, guaranteed place.)"""
    pkg = _active_package(context)
    checks, current = tour_state(context)
    box = layout.box()
    if current >= len(pkg["steps"]):
        box.label(text=f"Finished: {pkg['name']}",
                  icon="CHECKMARK")
        return
    step = pkg["steps"][current]
    box.label(text=f"{pkg['name']} - step {current + 1} of "
                   f"{len(pkg['steps'])}", icon="INFO")
    _wrap(box, step["title"])
    for act in _now_deck(context, limit=4):
        _draw_action_compact(box, act)


def _draw_start(layout, context):
    """The Start screen's whole content, drawn as the main
    panel when the Buddy Start screen is showing and no job
    is running: 'What are you making?' Picking a job starts
    it - and the conducting moves you to the screen that job
    starts on."""
    _wrap(layout, "Pick a job and Buddy arranges the whole "
                  "program around it, step by step. Or model "
                  "freely - the tools for the moment are "
                  "always on the ` key (top-left of the "
                  "keyboard) and in the Buddy tools button in "
                  "the bar above the big window.")
    for pkg in PACKAGES:
        box = layout.box()
        _wrap(box, pkg["name"])
        _wrap(box, pkg["byline"])
        op = box.operator("buddy.tour_start",
                          text=f"Start: {pkg['name']}",
                          icon="PLAY")
        op.package = pkg["id"]


class _BuddyExtrudeTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "EDIT_MESH"
    bl_idname = "buddy.extrude"
    bl_label = "Pull a face out"
    bl_description = ("Pull the picked faces out into new "
                      "shape - Blender calls this Extrude")
    bl_icon = "ops.mesh.extrude_region_move"
    bl_widget = None
    bl_keymap = (
        ("mesh.extrude_context_move",
         {"type": "LEFTMOUSE", "value": "PRESS"}, None),
    )


class _BuddyLoopCutTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "EDIT_MESH"
    bl_idname = "buddy.loop_cut"
    bl_label = "Add a ring of edges"
    bl_description = ("Slice a new ring of edges all the way "
                      "around the shape - Blender calls this "
                      "Loop Cut")
    bl_icon = "ops.mesh.loopcut_slide"
    bl_widget = None
    bl_keymap = (
        ("mesh.loopcut_slide",
         {"type": "LEFTMOUSE", "value": "PRESS"}, None),
    )


class _BuddyKnifeTool(WorkSpaceTool):
    bl_space_type = "VIEW_3D"
    bl_context_mode = "EDIT_MESH"
    bl_idname = "buddy.knife"
    bl_label = "Draw a cut"
    bl_description = ("Draw a cut across the shape with the "
                      "mouse - Blender calls this the Knife")
    bl_icon = "ops.mesh.knife_tool"
    bl_widget = None
    bl_keymap = (
        ("mesh.knife_tool",
         {"type": "LEFTMOUSE", "value": "PRESS"}, None),
    )


_BUDDY_TOOLS = ((_BuddyExtrudeTool, {"builtin.extrude_region"}),
                (_BuddyLoopCutTool, {"builtin.loop_cut"}),
                (_BuddyKnifeTool, {"builtin.knife"}))


def _register_tools():
    for cls, after in _BUDDY_TOOLS:
        try:
            bpy.utils.register_tool(cls, after=after)
        except Exception:
            pass


def _unregister_tools():
    for cls, _after in reversed(_BUDDY_TOOLS):
        try:
            bpy.utils.unregister_tool(cls)
        except Exception:
            pass



CLASSES = (BUDDY_Preferences, BUDDY_OT_action, BUDDY_OT_run_any,
           BUDDY_OT_tour_start, BUDDY_OT_tour_hide, BUDDY_OT_tour_do,
           BUDDY_OT_open_prefs, BUDDY_OT_ask_expert, BUDDY_OT_run_plan,
           BUDDY_OT_clear_plan, BUDDY_OT_test_expert,
           BUDDY_OT_pie, BUDDY_OT_build_screens,
           BUDDY_OT_mode_back, BUDDY_OT_origin_center,
           BUDDY_OT_origin_bottom, BUDDY_OT_cursor_home,
           BUDDY_OT_cursor_to_picked, BUDDY_OT_lock_in,
           BUDDY_OT_show_everything, BUDDY_OT_mute_trap,
           VIEW3D_MT_buddy_pie,
           VIEW3D_PT_blender_buddy,
           VIEW3D_PT_buddy_projects) + SECTION_PANELS


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
    bpy.types.Scene.buddy_tour_package = StringProperty(
        name="Guided project",
        description="Which guided project is active in the panel",
        default="donut",
    )
    bpy.types.Scene.buddy_show_lesson = BoolProperty(
        name="Show the full lesson", default=False)
    bpy.types.Scene.buddy_tour_started = BoolProperty(
        name="Guided project started",
        description="Whether a guided project is showing in the panel",
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
    bpy.types.WindowManager.buddy_expert_status = StringProperty(
        name="Expert connection test result", default="")
    bpy.types.WindowManager.buddy_muted = StringProperty(
        name="Heads-ups already got",
        description="Which plain-words heads-ups you've "
                    "already said 'got it' to (this session)",
        default="[]")
    global _EXPERT_HANDLE
    try:
        _EXPERT_HANDLE = bpy.types.SpaceView3D.draw_handler_add(
            _draw_expert_overlay, (), "WINDOW", "POST_PIXEL")
    except Exception:
        _EXPERT_HANDLE = None
    _install_template()
    try:
        bpy.types.VIEW3D_HT_header.append(_buddy_header_draw)
    except Exception:
        pass
    try:
        if _conduct_check not in \
                bpy.app.handlers.depsgraph_update_post:
            bpy.app.handlers.depsgraph_update_post.append(
                _conduct_check)
    except Exception:
        pass
    _register_tools()
    try:
        wm = bpy.context.window_manager
        kc = wm.keyconfigs.addon if wm else None
        if kc:
            km = kc.keymaps.new(name="3D View",
                                space_type="VIEW_3D")
            kmi = km.keymap_items.new("buddy.pie",
                                      type="ACCENT_GRAVE",
                                      value="PRESS")
            _BUDDY_KEYMAPS.append((km, kmi))
    except Exception:
        pass


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
                 "buddy_plan_retried", "buddy_expert_status",
                 "buddy_muted"):
        if hasattr(bpy.types.WindowManager, attr):
            delattr(bpy.types.WindowManager, attr)
    for attr in ("buddy_tour_started", "buddy_show_lesson",
                 "buddy_tour_epoch",
                 "buddy_tour_package"):
        if hasattr(bpy.types.Scene, attr):
            delattr(bpy.types.Scene, attr)
    for km, kmi in _BUDDY_KEYMAPS:
        try:
            km.keymap_items.remove(kmi)
        except Exception:
            pass
    _BUDDY_KEYMAPS.clear()
    _unregister_tools()
    try:
        bpy.types.VIEW3D_HT_header.remove(_buddy_header_draw)
    except Exception:
        pass
    try:
        bpy.app.handlers.depsgraph_update_post.remove(
            _conduct_check)
    except Exception:
        pass
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
