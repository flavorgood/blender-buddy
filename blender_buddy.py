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
import ipaddress
import math
import os
import random
import re
import shutil
import filecmp
import shutil
import subprocess
import sys
import tempfile
import textwrap
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import Future
from difflib import SequenceMatcher

import bpy
from bpy.props import (BoolProperty, EnumProperty, IntProperty,
                       StringProperty)
from bpy.types import AddonPreferences, Menu, Operator, Panel, WorkSpaceTool

bl_info = {
    "name": "Blender Buddy - Blender in Plain Words",
    "author": "Blender Buddy prototype",
    "version": (3, 2, 7),
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
    dict(id="reshape_as_circle", section="4. Shape it",
         plain="Turn the selected mesh into a flat circle outline",
         does="Shows a flat circle on this same object. Remove the Flat Circle modifier to bring its original shape back.",
         real="Mesh Circle geometry modifier", key="-", icon="MESH_CIRCLE",
         kind="custom", target="reshape_as_circle", needs="object", words="convert cube mesh ring outline flat circle"),
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


def _custom_reshape_as_circle(context):
    from mathutils import Vector

    obj = context.object
    if not obj or obj.type != "MESH" or context.mode != "OBJECT":
        raise ValueError("Pick a mesh in Object Mode first.")
    evaluated = obj.evaluated_get(context.evaluated_depsgraph_get())
    if not len(evaluated.data.vertices):
        raise ValueError("This mesh has no shape to size the circle from.")
    corners = [Vector(co) for co in evaluated.bound_box]
    center = sum(corners, Vector()) / len(corners)
    axes = evaluated.matrix_world.to_3x3()
    x, y = axes.col[0], axes.col[1]
    radius = max((max(co[i] for co in corners) - min(co[i] for co in corners))
                 * axes.col[i].length for i in (0, 1)) / 2
    # Rotate the node's axes to compensate for both non-uniform scale and
    # sheared parent transforms. The ring stays circular in the object's XY plane.
    angle = 0.5 * math.atan2(2 * x.dot(y), x.length_squared - y.length_squared)
    c, s = math.cos(angle), math.sin(angle)
    scale_x, scale_y = (x*c + y*s).length, (y*c - x*s).length
    if min(radius, scale_x, scale_y) <= 1e-8:
        raise ValueError("The mesh needs a nonzero width and an uncollapsed XY plane.")

    group = bpy.data.node_groups.new("Buddy Flat Circle", "GeometryNodeTree")
    modifier = None
    try:
        for direction in ("INPUT", "OUTPUT"):
            group.interface.new_socket(name="Geometry", in_out=direction,
                                       socket_type="NodeSocketGeometry")
        circle = group.nodes.new("GeometryNodeMeshCircle")
        circle.location = (-400, 0)
        circle.fill_type = "NONE"
        circle.inputs["Vertices"].default_value = 64
        circle.inputs["Radius"].default_value = radius
        transform = group.nodes.new("GeometryNodeTransform")
        transform.location = (-170, 0)
        transform.inputs["Translation"].default_value = center
        transform.inputs["Rotation"].default_value = (0, 0, angle)
        transform.inputs["Scale"].default_value = (1/scale_x, 1/scale_y, 1)
        output = group.nodes.new("NodeGroupOutput")
        output.location = (80, 0)
        group.links.new(circle.outputs["Mesh"], transform.inputs["Geometry"])
        group.links.new(transform.outputs["Geometry"], output.inputs["Geometry"])
        modifier = obj.modifiers.new("Flat Circle", "NODES")
        modifier.node_group = group
    except Exception:
        if modifier is not None:
            obj.modifiers.remove(modifier)
        bpy.data.node_groups.remove(group)
        raise
    return {"FINISHED"}


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


def _set_default_picture_path(scene):
    path = (scene.render.filepath or "").strip()
    if not path or os.path.normpath(path) == os.path.normpath("/tmp"):
        scene.render.filepath = _home("blender_buddy_picture.png")


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
    _set_default_picture_path(scene)
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
    "reshape_as_circle": _custom_reshape_as_circle,
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
                "file_operator": cat in _PLAN_TOOL_CATEGORIES and any(
                    p.subtype in {"FILE_PATH", "DIR_PATH", "FILE_NAME"}
                    for p in rna.properties if p.type == "STRING"),
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


def _principled(mat, rgba, roughness, subsurface=0.0,
                sss_radius=None, sss_scale=None):
    """Set a material up the way the tutorial does: a real Principled
    material with a base colour, a roughness, and - for food - his
    subsurface recipe: Weight all the way up, Radius dragged to
    (1, 1, 1), the amount steered with Scale."""
    mat.diffuse_color = rgba
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf is not None:
        bsdf.inputs["Base Color"].default_value = rgba
        bsdf.inputs["Roughness"].default_value = roughness
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = subsurface
        if sss_radius is not None and \
                "Subsurface Radius" in bsdf.inputs:
            bsdf.inputs["Subsurface Radius"].default_value = \
                tuple(sss_radius)
        if sss_scale is not None and \
                "Subsurface Scale" in bsdf.inputs:
            bsdf.inputs["Subsurface Scale"].default_value = sss_scale


def _paint(obj, mat_name, rgba, roughness=0.55, subsurface=0.0,
           sss_radius=None, sss_scale=None):
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)
    _principled(mat, rgba, roughness, subsurface,
                sss_radius=sss_radius, sss_scale=sss_scale)
    obj.data.materials.clear()
    obj.data.materials.append(mat)


# ----------------------------------------------------------------------------
# The Donut package: the follow-along companion to Blender Guru's
# NEW donut series - "Blender Donut Tutorial (2025)", taught in
# Blender 5.0. One step per part:
#   Part 1 (2026) - navigation, the donut AND the cup, first saves
#   Part 2 Basic Modelling - the cup becomes the mug, from a photo
#   Part 3 Basic Organic Modelling - icing that drips and hugs
#   Part 4 Basic Materials - plate, lattice, SSS, first picture
#   Part 5 Basic Texturing - photo textures as a three-map recipe
#   Part 6 Basic UV Unwrapping - seams on the mug, coffee foam
#   Part 7 How to Scatter in Blender 5.0 - Scatter on Surface
#   Part 8 The Basics of Lighting and Rendering - the finale
#
# REPLICATION DOCTRINE (the fidelity audit, redesign/
# DONUT_FIDELITY_AUDIT.md, is the spec): the steps, the checks
# and the reference builds follow what he actually does -
# movement for movement, value for value. Values he states are
# used exactly and cited in comments. Values he sets by eye are
# marked UNSTATED wherever the reference build has to pick one:
# the build picks a plausible number and the comment says the
# video leaves it open - it is never presented as his. The
# checks grade the scene HIS procedure produces at each part's
# end: objects are found by role (shape, structure, material),
# never by name alone, because he assigns half the names in
# Part 8 - or, for the foam, a different name than you'd guess.
# The video teaches; these steps orient (which part, what he
# is about to do), verify (the tick is the scene's proof, never
# a button press) and rescue (the missing text names what your
# screen is still missing). The run functions are the reference
# builds the tests prove the checks against - the panel never
# offers them.
# ----------------------------------------------------------------------------

# His scale: the whole series lives at a tenth of the size
# Blender's defaults suggest. The donut's ring is 0.1 m across
# its middle; the cup starts as a 0.13 m radius cylinder.
DONUT_MAJOR = 0.1        # Part 1: Major Radius 1 m -> 0.1
DONUT_MINOR = 0.057      # Part 1: Minor Radius, dragged to ~0.057
CUP_RADIUS = 0.13        # Part 1: cylinder Radius 0.13
CUP_DEPTH = 0.24         # Part 1: depth dragged by eye - UNSTATED
TABLE_TOP = -0.080       # staging: where the Part 4 table's top sits


def _find_dough(context, objects=None):
    """The dough ring, found by shape: a mesh with a real hole
    through its middle whose underside curves all the way
    around (the icing shell, which shares the hole, has no
    underside near the hole - its bottom half was deleted).
    His name for it ("Donut", from Part 3) is the fast path.
    With objects given, that list is searched instead of
    the live scene."""
    if objects is None:
        named = _scene_obj(context, "Donut")
        if named is not None and named.type == "MESH":
            return named
        named = _scene_obj(context, "Dough")
        if named is not None and named.type == "MESH":
            return named
        objects = context.scene.objects
    else:
        for want in ("Donut", "Dough"):
            for obj in objects:
                if obj.type == "MESH" and obj.name == want:
                    return obj
    for obj in objects:
        if obj.type != "MESH" or len(obj.data.vertices) < 100:
            continue
        verts = obj.data.vertices
        rs = [math.hypot(v.co.x, v.co.y) for v in verts]
        r_max = max(rs)
        if r_max <= 0 or min(rs) < 0.2 * r_max:
            continue  # no hole through the middle
        zs = [v.co.z for v in verts]
        z_mid = (max(zs) + min(zs)) / 2
        z_span = max(zs) - min(zs)
        if z_span <= 0:
            continue
        # Underside near the hole: verts low on the shape and
        # well inside its outer radius - only the full ring
        # (the dough) has them; the icing's low verts are its
        # drips, all out at the rim.
        if any(v.co.z < z_mid - 0.36 * z_span
               and math.hypot(v.co.x, v.co.y) < 0.7 * r_max
               for v in verts):
            return obj
    return None


def _find_icing(context, dough=None):
    """The icing: the other ring - a shell with the same hole,
    sitting exactly where the dough sits (it was duplicated
    from it in place), but not the dough itself."""
    if dough is None:
        dough = _find_dough(context)
    named = _scene_obj(context, "Icing")
    if named is not None and named.type == "MESH" \
            and named is not dough:
        return named
    if dough is None:
        return None
    for obj in context.scene.objects:
        if obj.type != "MESH" or obj is dough:
            continue
        if len(obj.data.vertices) < 100:
            continue
        verts = obj.data.vertices
        rs = [math.hypot(v.co.x, v.co.y) for v in verts]
        if max(rs) <= 0 or min(rs) < 0.2 * max(rs):
            continue
        # Duplicated in place: its origin rides with the
        # dough's origin, even after Part 8's parenting.
        gap = (obj.matrix_world.translation
               - dough.matrix_world.translation).length
        if gap < 0.35 * DONUT_MINOR + 0.02:
            return obj
    return None


def _radius_profile(obj):
    """(r_body, height, z_min, z_max, radii, heights) for a
    mesh cage, or None. r_body is the body's own wall radius,
    read as the MEDIAN radius of the middle height band and
    refined once toward the verts that cluster near it: in
    that band the wall is the crowd, and everything else -
    a handle, an inset ring - is a minority spread thin, so
    the median lands on the wall itself.

    The read this replaces took the 90th percentile of ALL
    radii. On the low-vertex cage the card's own procedure
    leaves behind, a grown handle is more than a tenth of
    the verts and holds all of the largest radii, so the
    percentile read the HANDLE as the body (measured on a
    walked mug: r_body 0.283 on a 0.13 wall), the wall test
    collapsed, and steps 1 and 2 un-ticked together the
    moment Part 2's centrepiece was done - the learner was
    stranded mid-part with no message. Walkthrough gap 2.13:
    checks must grade the mesh the taught procedure
    produces, not the reference build's mesh."""
    verts = obj.data.vertices
    if len(verts) < 12:
        return None
    rs = [math.hypot(v.co.x, v.co.y) for v in verts]
    zs = [v.co.z for v in verts]
    z_min, z_max = min(zs), max(zs)
    height = z_max - z_min
    if height <= 0:
        return None
    band = [r for r, z in zip(rs, zs)
            if z_min + 0.15 * height < z < z_max - 0.15 * height]
    if len(band) < 6:
        band = list(rs)
    band_sorted = sorted(band)
    med = band_sorted[len(band_sorted) // 2]
    if med <= 0:
        return None
    near = [r for r in band if 0.8 * med < r < 1.25 * med]
    r_body = sum(near) / len(near) if near else med
    return r_body, height, z_min, z_max, rs, zs


def _point_in_poly(x, y, pts):
    """Even-odd ray cast in the floor plan. A point sitting
    on a vertex counts as inside - a triangle-fan cap has a
    vert exactly on the axis, and it still roofs the cup."""
    n = len(pts)
    for px, py in pts:
        if abs(px - x) < 1e-6 and abs(py - y) < 1e-6:
            return True
    inside = False
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = (x2 - x1) * (y - y1) / (y2 - y1) + x1
            if x < xin:
                inside = not inside
    return inside


def _top_open(obj, r_body, z_max, height):
    """The top is really open: no face up there roofs the
    middle. A cylinder cap's verts all sit ON the rim, so a
    probe counting centre verts (the old read) can never see
    a cap that was never deleted - the cap is a FACE, so
    faces are what is tested: project each top-band face to
    the floor plan and ask whether it covers the axis. A
    thickened cup's rim annulus does not cover the axis; a
    cap - n-gon or triangle fan - does. (Gap 1.17: the
    'open cup' condition was, for the cap style this very
    step creates, untested.)"""
    verts = obj.data.vertices
    z_cut = z_max - 0.25 * height
    for poly in obj.data.polygons:
        if poly.center.z < z_cut:
            continue
        pts = [(verts[i].co.x, verts[i].co.y)
               for i in poly.vertices]
        if any(math.hypot(px, py) < 0.05 * r_body
               for px, py in pts):
            return False
        if _point_in_poly(0.0, 0.0, pts):
            return False
    return True


def _is_container(obj):
    """A cup/mug-shaped thing: a round wall standing around an
    empty middle, roughly as tall as it is wide, with an open
    top. Judged on the object's own cage, in its own space,
    by the robust profile - so the mug stays a container
    after its handle grows (the regression that stranded
    the walk), while the dough ring and the icing shell,
    which wrap an inner wall through their middle band,
    never qualify."""
    if obj is None or obj.type != "MESH":
        return False
    prof = _radius_profile(obj)
    if prof is None:
        return False
    r_body, height, z_min, z_max, rs, zs = prof
    ratio = r_body / height
    if ratio < 0.28 or ratio > 1.05:
        return False
    # The wall is the crowd: most verts live at the body's
    # radius. A handle's verts, out past it, are the
    # minority and do not count against the wall.
    wall = sum(1 for r in rs if 0.70 * r_body < r < 1.32 * r_body)
    if wall < 0.5 * len(rs):
        return False
    # Nothing reaches into the middle at mid height: a ring
    # (the dough) and a half shell (the icing) both carry an
    # inner wall through the centre band and are not cups.
    band = [(r, z) for r, z in zip(rs, zs)
            if z_min + 0.2 * height < z < z_max - 0.2 * height]
    if band:
        inner = sum(1 for r, z in band if r < 0.62 * r_body)
        if inner > 0.12 * len(band):
            return False
    return _top_open(obj, r_body, z_max, height)


def _proud_cluster(obj):
    """The verts that stick out past a container's wall,
    partway up its side - the raw material of a handle.
    Returns (proud, r_wall, height, z_min, z_max) with
    proud a list of (radius, z, angle), or None."""
    if obj is None or obj.type != "MESH":
        return None
    prof = _radius_profile(obj)
    if prof is None:
        return None
    r_wall, height, z_min, z_max, rs, zs = prof
    verts = obj.data.vertices
    proud = [(r, z, math.atan2(verts[i].co.y, verts[i].co.x))
             for i, (r, z) in enumerate(zip(rs, zs))
             if r > 1.18 * r_wall
             and z_min + 0.12 * height < z
             < z_max - 0.08 * height]
    return proud, r_wall, height, z_min, z_max


def _wedge(proud):
    """(arc, centre) of the smallest angular wedge holding
    every proud vert, in radians. A ring, a flare or a
    belly bulge wraps the whole body - its arc is the full
    circle. A handle lives on ONE side of the mug."""
    angs = sorted(a for _r, _z, a in proud)
    if not angs:
        return 0.0, 0.0
    gaps = [(angs[(i + 1) % len(angs)] - angs[i]) % (2 * math.pi)
            for i in range(len(angs))]
    widest = max(range(len(angs)), key=lambda i: gaps[i])
    arc = 2 * math.pi - gaps[widest]
    centre = angs[(widest + 1) % len(angs)] + arc / 2
    return arc, centre


def _has_handle(obj):
    """A handle grown from a container's wall: verts
    sticking well out past the wall, partway up the side -
    the extruded loop his Part 2 walks around. The wall it
    is measured against is the robust body radius, so the
    answer survives the handle's own verts joining the
    cage (gap 2.13 measured this returning True while the
    container test beside it failed).

    Round 2 (re-walk M2): the old read counted ANY verts
    past 1.18x the wall - and the taught reshape itself
    (belly scaled out, foot flared, rings slid) lives
    within a few percent of that line, so a handle-less
    mug crossed it: step 2 ticked at the Solidify Apply
    with no handle grown at all. A handle is not merely
    FARTHER out than the wall - it is a LOCALIZED, DEEP
    protrusion: its verts cluster in one wedge of the
    circle (a ring or a bulge wraps all the way round)
    and its crown reaches past every shaping move the
    procedure teaches - the walked reshape peaks at
    about 1.09x the wall, while the reference build's
    own handle crowns at 1.24x and the walked mug's at
    over 2x. Both tests are required now, and the crown
    line sits between those measured classes."""
    got = _proud_cluster(obj)
    if got is None:
        return False
    proud, r_wall, _h, _lo, _hi = got
    if len(proud) < 4:
        return False
    arc, _centre = _wedge(proud)
    if arc > math.radians(170):
        return False
    return max(r for r, _z, _a in proud) >= 1.16 * r_wall


def _boundary_loops(obj):
    """Boundary edges (edges exactly one face uses) grouped
    into loops by shared verts. A finished mug has exactly
    one - its mouth - or none at all once its walls are
    baked solid. Every other loop is a hole nobody closed."""
    uses = {}
    for poly in obj.data.polygons:
        for a, b in poly.edge_keys:
            key = (a, b) if a < b else (b, a)
            uses[key] = uses.get(key, 0) + 1
    boundary = [k for k, n in uses.items() if n == 1]
    if not boundary:
        return []
    by_vert = {}
    for i, (a, b) in enumerate(boundary):
        by_vert.setdefault(a, []).append(i)
        by_vert.setdefault(b, []).append(i)
    seen = set()
    loops = []
    for i in range(len(boundary)):
        if i in seen:
            continue
        comp = []
        stack = [i]
        while stack:
            j = stack.pop()
            if j in seen:
                continue
            seen.add(j)
            comp.append(j)
            a, b = boundary[j]
            stack.extend(by_vert.get(a, ()))
            stack.extend(by_vert.get(b, ()))
        loops.append([boundary[j] for j in comp])
    return loops


def _dead_end_cap(obj, targets, rs, zs, r_body, line):
    """True when the handle's far end is a cap that was
    never joined - the touching state the taught pull
    produces before any sewing.

    The question is asked at the tube's two ends, and
    nowhere else. Take the verts that are not wall-ring
    verts - a height shared by a full ring of verts,
    eight or more at one radius, is a ring of the cup's
    own wall, and those are the ANCHORED verts - and
    the connected components holding the spanning
    faces' wall-side verts are the handle tube. Walk
    the tube's graph diameter: the two farthest verts
    mark its two ends, and each end's rim is the two
    layers of verts at that end (a rectangular ring's
    verts sit one graph step apart from each other,
    so a single layer would catch only half the rim).
    An end is ATTACHED when any of its rim verts has
    an edge to an anchored vert: the root end always
    is, because the tube grew out of the wall, and a
    sewn, bridged or welded far end is too, because
    those joins are built on the wall's own points. A
    capped end merely resting against the wall shares
    no point with it, so exactly one end attached
    means the far end is a dead end and the veto
    fires. Both ends attached - or no tube to judge -
    is not this veto's to block.

    Round 3's version scanned for a single FACE shaped
    like a cap: all verts wall-side of the line, at
    least two of them targets, no wall-ring vert among
    them, no edge to one, nothing buried, and cutting
    its verts away stranding no other target. Fix
    round 4's diagnosis measured that scan on the
    walked scenes and it never sees a real cap: one
    walked end dips its top corners below the buried
    line, the other's cap faces hold no targets at
    all. What it fires on, in touching scenes and
    joined ones alike, is a plain tube face of the
    handle's own descent - the tube's cross-section
    is the extruded wall face's rectangle, two
    wall-side verts and two crown verts per ring, so
    cutting one face's verts can never strand the end
    beyond it, and the articulation clause waves every
    mid-tube face through. The scan held the touching
    states by that accident and vetoed every genuine
    join the card teaches (the bridged walked mug
    read False), which is why the test lives at the
    ends now.

    Round 5 corrects where the ends are measured.
    Round 4's version seeded the tube search with
    every target, wall-ring verts included, so the
    wall's own verts sat inside the measured set -
    and a sewn landing ties the end ring straight to
    wall verts of the root's own rim (on the walked
    mug the patch's top pair IS the root face's
    bottom pair). The diameter then ran through the
    wall: root and landing measured one step apart,
    the arc's crown was the farthest point left, and
    the crown read as the dead end. The anchored
    verts now seed the tube's components but never
    enter them, and the diameter is walked from a
    vert of the tube itself."""
    buckets = {}
    for i in range(len(zs)):
        buckets.setdefault(round(zs[i] / 0.004),
                           []).append(i)
    anchored = set()
    for idxs in buckets.values():
        if len(idxs) < 8:
            continue
        ring = sorted(rs[i] for i in idxs)
        med = ring[len(ring) // 2]
        for i in idxs:
            if abs(rs[i] - med) < 0.012:
                anchored.add(i)
    if not anchored or not targets:
        return False
    full = {}
    for edge in obj.data.edges:
        a, b = edge.vertices
        full.setdefault(a, set()).add(b)
        full.setdefault(b, set()).add(a)

    def bfs(src, allowed):
        dist = {src: 0}
        frontier = [src]
        while frontier:
            nxt = []
            for g in frontier:
                for h in full.get(g, ()):
                    if h in allowed and h not in dist:
                        dist[h] = dist[g] + 1
                        nxt.append(h)
            frontier = nxt
        return dist

    # The tube: the components of the anchored-free
    # graph that hold at least one target. (A target
    # that is itself a wall-ring vert still seeds its
    # component - the tube's first ring hangs off the
    # wall face it grew from.)
    free = set(full) - anchored
    tube = set()
    for t in targets:
        if t not in tube:
            tube |= set(bfs(t, free))
    # The anchored verts themselves never enter the
    # measured set. Round 4's version let them in as
    # BFS seeds, and a sewn landing ties the end ring
    # straight to wall verts of the root's own rim -
    # on the walked mug the patch's top pair IS the
    # root face's bottom pair - so the diameter's
    # path short-circuited through the wall: root and
    # landing sat one step apart, the farthest point
    # left standing was the arc's crown, and the
    # crown, which touches nothing, read as the dead
    # end (fix round 5's diagnosis has the walked
    # measurements). With the wall's verts out of the
    # graph, the sew's edges lead OUT of the tube,
    # where they count as attachment, and the
    # diameter runs the tube's own length again.
    tube -= anchored
    if not tube:
        return False
    # The tube's two ends, by graph diameter: farthest
    # from a vert of the tube itself - a free target
    # when one exists (stray wall fragments a seed
    # pulled in carry no targets and are never the
    # tube) - then farthest from that. Each end's rim
    # is the two farthest layers from the OTHER end,
    # drawn from the layers the search actually
    # reached: with the wall's verts out of the set,
    # a pulled-in fragment is its own component and
    # is never reached.
    seeds = targets & tube
    d0 = bfs(min(seeds) if seeds else min(tube), tube)
    end_a = max(d0, key=lambda v: d0[v])
    da = bfs(end_a, tube)
    end_b = max(da, key=lambda v: da[v])
    db = bfs(end_b, tube)
    span = db[end_a]
    rim_a = {v for v in db if db[v] >= span - 1}
    rim_b = {v for v in da if da[v] >= span - 1}

    def attached(rim):
        return any(h in anchored for v in rim
                   for h in full.get(v, ()))

    return attached(rim_a) != attached(rim_b)


def _handle_returns(obj):
    """The handle comes BACK to the body. A "spanning"
    face - one with verts on both sides of the wall
    line - exists wherever handle meets body: the grown
    tube's first segment spans it at the root, and a
    finished join spans it again at the landing (sewing
    faces, bridge faces, a weld). Collect the wall-side
    verts of every spanning face and measure how far
    apart they reach ALONG THE WALL's own vert graph:

    - one attachment (a handle grown and left hanging,
      capped or not): its wall-side verts are one wall
      face's rim - a four-corner ring, whose farthest
      corners sit two steps apart;
    - two attachments: the landing's rim joins the set,
      and the farthest wall-side verts sit at least
      three steps apart - across the root rim and down
      the landing's own rim - even when the landing is
      the very face below the root and the two rims
      share an edge (the suite's construction);
    - an end pushed INTO the wall (the walk's
      overshoot) never welds: its spanning faces' inner
      verts form a separate island in the wall graph,
      and the island's verts sit buried in the body,
      well inside the wall's own radius - which proves
      the second attachment. An end merely TOUCHING the
      wall, cap on and unsewn, also forms an island,
      but its verts sit ON the wall's radius, not buried
      in it - and proves nothing.

    Distances are counted in wall rings, never in
    metres or heights - the walked handle lands at its
    root's own height, and the reference build's handle
    hugs the wall at 1.24x it; both pass, and a hanging
    handle fails at any size.

    Round 3 closes the hole that reasoning leaves: a
    grown handle whose descent runs along the wall -
    the taught pull brings it home hugging the surface
    - contributes wall-side verts at BOTH ends of its
    own arc, the root rim and the rings of its descent,
    and those sit three or more steps apart along the
    wall, so the distance clause alone reads the one
    attachment as two (re-walk #2, gap #3: the step
    ticked on a bare re-evaluation event, the end face
    unsewn and hovering at the wall, both inside faces
    still present). The distance clause therefore runs
    only after _dead_end_cap has had its say: a capped
    end with no shared topology at the landing is a
    dead end, and a dead end vetoes the tick however
    far apart the approach's own verts measure. A real
    join - F-faces sewn corner to corner, a bridge, a
    weld - shares topology at the landing by
    construction, so the veto never sees it.

    Round 4 corrects that last claim: round 3's veto
    DID see real joins - its face-shaped scan mistook
    a mid-descent tube face for the cap and vetoed the
    walked mug's finished bridge (fix round 4's
    diagnosis has the measurements). The veto's
    question is unchanged - is the far end attached
    to the wall, or merely resting on it? - but
    _dead_end_cap now answers it at the tube's two
    ends, the only places the answer lives."""
    prof = _radius_profile(obj)
    if prof is None:
        return False
    r_body = prof[0]
    rs = prof[4]
    line = 1.15 * r_body
    wall_side = set()
    for poly in obj.data.polygons:
        prs = [rs[i] for i in poly.vertices]
        if max(prs) > line and min(prs) < line:
            wall_side.update(i for i in poly.vertices
                             if rs[i] < line)
    if len(wall_side) < 4:
        return False
    adj = {}
    for edge in obj.data.edges:
        a, b = edge.vertices
        if rs[a] < line and rs[b] < line:
            adj.setdefault(a, set()).add(b)
            adj.setdefault(b, set()).add(a)
    targets = set(wall_side)
    if _dead_end_cap(obj, targets, rs, prof[5],
                     r_body, line):
        return False
    for start in wall_side:
        dist = {start: 0}
        frontier = [start]
        while frontier:
            nxt = []
            for g in frontier:
                for h in adj.get(g, ()):
                    if h not in dist:
                        dist[h] = dist[g] + 1
                        nxt.append(h)
            frontier = nxt
        reached = targets & set(dist)
        unreached = targets - reached
        if unreached and any(rs[t] < r_body - 0.010
                             for t in unreached):
            return True
        if any(dist[t] >= 3 for t in reached):
            return True
    return False


def _join_closed(obj):
    """The handle is JOINED, not merely touching. Step 2's
    check never tested the join at all (gap 2.14) - a
    handle grown and never joined satisfied every graded
    condition.

    Round 2 (re-walk M3): the read this replaces failed
    on ANY boundary loop that was not the mouth. That
    revoked the tick mid-procedure by design: the card's
    own bridge route OPENS the joint first (delete both
    inside faces, then Bridge Edge Loops), and the card's
    main method ends by deleting those same two faces.
    Worse, its flip side never required a join at all - a
    capped handle hanging in mid-air has the mouth as its
    only loop and passed (the hole behind the Apply false
    tick). The join is now tested positively, in every
    state the procedure legitimately passes through:

    - Open loops are accepted only as the joint's own
      pair: two rims at the handle, pulled together (gap
      at most 0.02) - the bridge route staged, or a join
      opened exactly where the handle lands. A lone hole,
      or two holes that are not a pair at the handle (the
      walked scene kept two, 0.125 m apart on different
      sides of the mug), still fails.
    - With no open loops, the handle must prove it came
      back (_handle_returns): sewn, bridged, welded and
      embedded ends all pass; the capped handle floating
      in air finally fails."""
    prof = _radius_profile(obj)
    if prof is None:
        return False
    r_body, height, z_min, z_max, rs, zs = prof
    verts = obj.data.vertices
    # Open rims, grouped by shared verts rather than
    # walked edge by edge: where a learner's faces
    # overlap (his grown tube doubles a face along the
    # root rim), one rim edge can carry two faces and
    # still border the hole, and an edge-walk reads the
    # rim as a broken path of three. The verts are the
    # rim either way.
    uses = {}
    for poly in obj.data.polygons:
        for a, b in poly.edge_keys:
            key = (a, b) if a < b else (b, a)
            uses[key] = uses.get(key, 0) + 1
    bedges = [k for k, n in uses.items() if n < 2]
    by_vert = {}
    for ei, (a, b) in enumerate(bedges):
        by_vert.setdefault(a, []).append(ei)
        by_vert.setdefault(b, []).append(ei)
    comps = []
    seen = set()
    for ei in range(len(bedges)):
        if ei in seen:
            continue
        comp = set()
        stack = [ei]
        while stack:
            j = stack.pop()
            if j in seen:
                continue
            seen.add(j)
            a, b = bedges[j]
            comp.add(a)
            comp.add(b)
            stack.extend(by_vert.get(a, ()))
            stack.extend(by_vert.get(b, ()))
        comps.append(comp)
    open_rims = []
    for comp in comps:
        mouth = min(zs[i] for i in comp) \
            > z_max - 0.20 * height \
            and max(rs[i] for i in comp) < 1.2 * r_body
        if not mouth:
            open_rims.append(comp)
    if not open_rims:
        return _handle_returns(obj)
    got = _proud_cluster(obj)
    if got is None:
        return False
    arc, centre = _wedge(got[0])

    def in_wedge(comp):
        cx = sum(verts[i].co.x for i in comp) / len(comp)
        cy = sum(verts[i].co.y for i in comp) / len(comp)
        diff = (math.atan2(cy, cx) - centre) % (2 * math.pi)
        if diff > math.pi:
            diff -= 2 * math.pi
        return abs(diff) <= arc / 2 + math.radians(40)

    def gap(a, b):
        pa = [verts[i].co for i in a]
        pb = [verts[i].co for i in b]
        return min((x - y).length for x in pa for y in pb)

    for comp in open_rims:
        if not in_wedge(comp):
            return False
        if not any(other is not comp
                   and gap(comp, other) <= 0.02
                   for other in open_rims):
            return False
    return True


def _containers(context, skip=(), objects=None):
    """Every cup/mug-shaped mesh in the scene, minus the
    pieces other finders have already claimed. With
    objects given, that list is graded instead of the
    live scene, with the very same tests."""
    out = []
    for obj in (context.scene.objects if objects is None
                else objects):
        if obj.type != "MESH" or obj in skip:
            continue
        if _is_container(obj):
            out.append(obj)
    return out


def _find_mug(context):
    """The mug: the container that has grown a handle. (While
    it is still the plain cup, this returns None - by design:
    Part 2 is what turns the cup into the mug.)"""
    for obj in _containers(context):
        if _has_handle(obj):
            return obj
    return None


def _find_plate(context, dough=None):
    """The plate: a wide, flat mesh the donut rests in -
    wider than the donut, far thinner than it is wide,
    centred under it. (His stays named "Circle" until
    Part 8; shape is the only honest way to find it.)"""
    if dough is None:
        dough = _find_dough(context)
    named = _scene_obj(context, "Plate")
    if named is not None and named.type == "MESH":
        return named
    if dough is None:
        return None
    d_center = dough.matrix_world.translation
    d_size = max(dough.dimensions.x, dough.dimensions.y)
    for obj in context.scene.objects:
        if obj.type != "MESH" or obj is dough:
            continue
        w = max(obj.dimensions.x, obj.dimensions.y)
        h = obj.dimensions.z
        if w <= 0 or h <= 0:
            continue
        if not (1.05 * d_size < w < 3.4 * d_size):
            continue
        if h > 0.28 * w:
            continue
        c = obj.matrix_world.translation
        if math.hypot(c.x - d_center.x, c.y - d_center.y) \
                > 0.35 * d_size:
            continue
        top = c.z + h / 2
        if top > d_center.z + 0.02:
            continue  # the donut rests IN it, not under it
        return obj
    return None


def _find_table(context, dough=None):
    """The table: the big flat thing at the bottom of the
    set, many times wider than the donut and barely thick.
    (His stays named "Plane" until Part 8.)"""
    if dough is None:
        dough = _find_dough(context)
    named = _scene_obj(context, "Table")
    if named is not None and named.type == "MESH":
        return named
    if dough is None:
        return None
    d_size = max(dough.dimensions.x, dough.dimensions.y)
    best = None
    for obj in context.scene.objects:
        if obj.type != "MESH" or obj is dough:
            continue
        w = max(obj.dimensions.x, obj.dimensions.y)
        if w < 2.6 * d_size:
            continue
        if obj.dimensions.z > 0.06 * w:
            continue
        if best is None or w > max(best.dimensions.x,
                                   best.dimensions.y):
            best = obj
    return best


def _find_foam(context, mug=None):
    """The coffee foam: a small mesh of its own sitting
    inside the mug's rim, up at the top of the mug - his is
    separated from the mug's own rim loop in Part 6 and
    named "Foam"."""
    if mug is None:
        mug = _find_mug(context)
    named = _scene_obj(context, "Foam")
    if named is not None and named.type == "MESH" \
            and named is not mug:
        return named
    if mug is None:
        return None
    from mathutils import Vector
    m_center = mug.matrix_world.translation
    m_top = m_center.z + mug.dimensions.z / 2
    m_r = max(mug.dimensions.x, mug.dimensions.y) / 2
    for obj in context.scene.objects:
        if obj.type != "MESH" or obj is mug:
            continue
        if len(obj.data.vertices) > 3000:
            continue
        # Judge by the geometry's world box, not the object
        # origin: a separated piece keeps the mug's own
        # origin, so its origin sits at mug-centre while
        # its surface rides up at the rim.
        corners = [obj.matrix_world @ Vector(corner)
                   for corner in obj.bound_box]
        lo = Vector((min(c.x for c in corners),
                     min(c.y for c in corners),
                     min(c.z for c in corners)))
        hi = Vector((max(c.x for c in corners),
                     max(c.y for c in corners),
                     max(c.z for c in corners)))
        c = (lo + hi) / 2
        if math.hypot(c.x - m_center.x, c.y - m_center.y) \
                > 0.6 * m_r:
            continue
        if abs(c.z - (m_top - 0.12 * mug.dimensions.z)) \
                > 0.22 * mug.dimensions.z:
            continue
        w = max(hi.x - lo.x, hi.y - lo.y)
        if w > 1.15 * 2 * m_r:
            continue
        return obj
    return None


def _render_proof(context):
    """A picture exists because someone rendered: Buddy
    recorded a completed render on the scene itself (the
    record is saved with the file; the Render Result's
    pixels are not, and on Blender 5.3 - and in any
    background render - that image reads size (0, 0) with
    has_data False even after a render completes, so it
    cannot be the only witness), the Render Result still
    holds it, or a render file was written to the scene's
    output path during this tour."""
    try:
        if getattr(context.scene, "buddy_render_done", False):
            return True
    except Exception:
        pass
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


def _final_render_proof(context):
    """The finale's render clause: a render that belongs
    to the final stage. _render_proof proves A render
    happened during the tour - its recorded flag fires on
    the first render of any step, and its output-path
    branch is guarded only by the tour's start - so the
    render that ticks Part 4 would also tick Part 8 with
    no finale render in existence (W4, GAP 8-4: the tour
    completed at the depth-of-field save on the strength
    of Part 4's rescue render). This clause reads only
    the final-stage record: the render-complete handler
    sets buddy_final_render_done when a render finishes
    with the finale's rig standing complete around it.
    The record is saved with the file, so the proof still
    reads from the scene alone. A file saved before the
    record existed carries none, and one fresh F12 with
    the rig standing makes it - the record cannot be
    invented retroactively, and an earlier stage's render
    at the same output path is not the finale's."""
    try:
        return bool(getattr(
            context.scene, "buddy_final_render_done", False))
    except Exception:
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


def _sss_recipe(obj):
    """His subsurface recipe, read off an object's materials:
    (weight, radius, scale) of the strongest-SSS material, or
    None. His recipe, stated in Part 4 and restated in Parts
    5, 7 and 8: Weight 1, Radius (1, 1, 1), amount by Scale."""
    if obj is None or obj.type != "MESH":
        return None
    best = None
    for mat in obj.data.materials:
        if mat is None or not mat.use_nodes or mat.node_tree is None:
            continue
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        if bsdf is None or "Subsurface Weight" not in bsdf.inputs:
            continue
        weight = float(bsdf.inputs["Subsurface Weight"]
                       .default_value)
        radius = None
        if "Subsurface Radius" in bsdf.inputs:
            radius = tuple(float(c) for c in
                           bsdf.inputs["Subsurface Radius"]
                           .default_value[:3])
        scale = None
        if "Subsurface Scale" in bsdf.inputs:
            scale = float(bsdf.inputs["Subsurface Scale"]
                          .default_value)
        if best is None or weight > best[0]:
            best = (weight, radius, scale)
    return best


def _recipe_ok(obj):
    """True when the object's food glow is his recipe: weight
    all the way up and the radius corrected to (1, 1, 1) -
    not the red-tinted skin default he warns about."""
    recipe = _sss_recipe(obj)
    if recipe is None:
        return False
    weight, radius, _scale = recipe
    if weight < 0.99:
        return False
    if radius is None:
        return False
    return all(abs(c - 1.0) < 0.05 for c in radius)


def _set_active(context, obj):
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    context.view_layer.objects.active = obj
    if context.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")


def _apply_modifier(context, obj, name):
    """Apply one modifier for real, the way his Apply clicks
    do - the stack above it is evaluated into the mesh."""
    _set_active(context, obj)
    bpy.ops.object.modifier_apply(modifier=name)


def _ensure_mod_order(context, obj, want):
    """Force the modifier stack into the given top-to-bottom
    order (his drags, made deterministic): try Blender's own
    move buttons first; if that fails, rebuild the stack -
    safe because this runs before anything is applied."""
    names = [m.name for m in obj.modifiers]
    if names == want:
        return
    _set_active(context, obj)
    try:
        for _ in range(len(want) * 2):
            names = [m.name for m in obj.modifiers]
            if names == want:
                return
            for i, name in enumerate(want):
                if names.index(name) != i:
                    while names.index(name) > i:
                        bpy.ops.object.modifier_move_up(
                            modifier=name)
                        names = [m.name for m in obj.modifiers]
                    break
    except Exception:
        pass
    if [m.name for m in obj.modifiers] == want:
        return
    keep = {m.name: m for m in obj.modifiers}
    for m in list(obj.modifiers):
        obj.modifiers.remove(m)
    for name in want:
        src = keep[name]
        new = obj.modifiers.new(src.name, src.type)
        for prop in src.bl_rna.properties:
            if prop.is_readonly or prop.identifier == "name":
                continue
            try:
                setattr(new, prop.identifier,
                        getattr(src, prop.identifier))
            except Exception:
                continue


def _mod_inputs(mod):
    """A geometry-nodes modifier's inputs, read by the NAME
    his UI shows (never by socket identifier - those are an
    implementation detail that shifts between versions).
    Returns {name: input-property}."""
    out = {}
    grp = getattr(mod, "node_group", None)
    if grp is None:
        return out
    try:
        inputs = mod.properties.inputs
    except Exception:
        return out
    for item in grp.interface.items_tree:
        if getattr(item, "in_out", None) != "INPUT":
            continue
        try:
            out[item.name] = getattr(inputs, item.identifier)
        except Exception:
            continue
    return out


def _set_mod_input(mod, name, value):
    prop = _mod_inputs(mod).get(name)
    if prop is None:
        return False
    prop.value = value
    return True


def _try_unwrap(context, obj):
    """A real U -> Unwrap (Angle Based), his method where the
    build needs one. Falls back to leaving the primitive UVs
    if the operator won't run in this context."""
    try:
        _set_active(context, obj)
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.uv.unwrap(method="ANGLE_BASED")
        bpy.ops.object.mode_set(mode="OBJECT")
        return True
    except Exception:
        try:
            bpy.ops.object.mode_set(mode="OBJECT")
        except Exception:
            pass
        return False


def _make_texture_set(name, rgb, seed, rough_mid):
    """Three small photo-like maps drawn in pixels here - a
    mottled colour map, a roughness map (data), and a normal
    map (data) - plus a displacement height map for the dough.
    No downloads; they stand in for his Poliigon textures
    (the audit is explicit that the real sets are external
    assets - these are labelled stand-ins, not his surfaces).
    Saved as files and packed, so they travel with the scene."""
    folder = os.path.join(tempfile.gettempdir(),
                          "buddy_donut_textures")
    os.makedirs(folder, exist_ok=True)
    rng = random.Random(seed)
    size = 256

    def octave(cells_n, amp):
        grid = [[rng.uniform(-amp, amp) for _ in range(cells_n)]
                for _ in range(cells_n)]

        def sample(u, v):
            gx = u * cells_n
            gy = v * cells_n
            x0 = int(gx) % cells_n
            y0 = int(gy) % cells_n
            x1 = (x0 + 1) % cells_n
            y1 = (y0 + 1) % cells_n
            fx = gx - int(gx)
            fy = gy - int(gy)
            sx = fx * fx * (3.0 - 2.0 * fx)
            sy = fy * fy * (3.0 - 2.0 * fy)
            top = grid[y0][x0] * (1 - sx) + grid[y0][x1] * sx
            bot = grid[y1][x0] * (1 - sx) + grid[y1][x1] * sx
            return top * (1 - sy) + bot * sy

        return sample

    # One surface, three readings of it: the same smooth
    # mottling drives the colour, the roughness and the bump,
    # the way a real photo set describes one material. (An
    # earlier version's hard 8-pixel cells printed across the
    # dough as checkerboard facets.)
    o1 = octave(9, 0.13)
    o2 = octave(27, 0.06)
    o3 = octave(81, 0.02)

    def noise(u, v):
        return o1(u, v) + o2(u, v) + o3(u, v)

    def build(kind):
        img = bpy.data.images.get(f"{name} {kind}")
        if img is not None and img.size[0] != size:
            bpy.data.images.remove(img)
            img = None
        if img is None:
            img = bpy.data.images.new(f"{name} {kind}", size, size)
        px = []
        for y in range(size):
            v = y / size
            for x in range(size):
                n = noise(x / size, v)
                if kind == "Colour":
                    px.extend((max(0.0, rgb[0] * (1 + n)),
                               max(0.0, rgb[1] * (1 + n)),
                               max(0.0, rgb[2] * (1 + n)), 1.0))
                elif kind == "Roughness":
                    vv = max(0.05, min(0.95, rough_mid + n))
                    px.extend((vv, vv, vv, 1.0))
                elif kind == "Displacement":
                    # A height map's swing is multiplied by
                    # the Displacement Scale (his stated 0.12)
                    # in metres. A photographic height map
                    # sits near mid-grey almost everywhere,
                    # with sparse pores; a uniform noise
                    # stand-in displaces EVERY point hard
                    # (spikes through the icing shell, a
                    # toothed shadow edge). Shape the
                    # stand-in's histogram the same way -
                    # quadratic falloff: typical points
                    # barely move, rare cells dip as pores.
                    shaped = math.copysign(
                        (abs(n) / 0.21) ** 2, n) * 0.21
                    vv = max(0.0, min(1.0,
                                      0.5 + shaped * 0.30))
                    px.extend((vv, vv, vv, 1.0))
                else:  # Normal: mostly flat, gently bumpy
                    px.extend((0.5 + n * 0.35, 0.5 + n * 0.25,
                               1.0, 1.0))
        # Colour space FIRST: changing it afterwards throws the
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
            "normal": build("Normal"), "disp": build("Displacement")}


def _apply_pbr(obj, tex, sss=None, displacement=None,
               map_scale=None):
    """Wire a texture set into the object's material the way
    Part 5 teaches: colour into Base Color (the only sRGB
    picture), roughness as Non-Color data, a Normal Map node
    into the Normal socket. sss, when given, is his recipe as
    (weight, radius, scale). displacement, when given, is the
    Displacement node's Scale with the height map plugged
    into the Material Output - his dough treatment."""
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
    if sss is not None:
        weight, radius, scale = sss
        if "Subsurface Weight" in bsdf.inputs:
            bsdf.inputs["Subsurface Weight"].default_value = weight
        if radius is not None and "Subsurface Radius" in bsdf.inputs:
            bsdf.inputs["Subsurface Radius"].default_value = \
                tuple(radius)
        if scale is not None and "Subsurface Scale" in bsdf.inputs:
            bsdf.inputs["Subsurface Scale"].default_value = scale
    coord = nt.nodes.new("ShaderNodeTexCoord")
    mapping = nt.nodes.new("ShaderNodeMapping")
    if map_scale is not None:
        mapping.inputs["Scale"].default_value = \
            (map_scale, map_scale, map_scale)
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
    if displacement is not None and tex.get("disp") is not None:
        dsp = tex_node(tex["disp"], (0, -560))
        dnode = nt.nodes.new("ShaderNodeDisplacement")
        dnode.location = (300, -560)
        dnode.inputs["Scale"].default_value = displacement
        nt.links.new(dsp.outputs["Color"], dnode.inputs["Height"])
        nt.links.new(dnode.outputs["Displacement"],
                     out.inputs["Displacement"])
        mat.displacement_method = "BOTH"
    obj.data.materials.clear()
    obj.data.materials.append(mat)
    return mat


def _reference_image(context):
    """A small stand-in for the mug reference photo he links
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


def _ring_verts(bm, z_target, tol=0.004):
    """Verts of the cup cage sitting on one height ring."""
    return [v for v in bm.verts if abs(v.co.z - z_target) < tol]


def _scale_ring(bm, z_target, factor, tol=0.004):
    for v in _ring_verts(bm, z_target, tol):
        v.co.x *= factor
        v.co.y *= factor


def _subdivide_verticals(bm, z_lo, z_hi):
    """One loop cut (Ctrl+R): the vertical edges that SPAN
    the middle of the given height band are cut once;
    returns the new ring's height (the cut edges' midpoint).
    Span, not containment - a band edge falling mid-edge
    must not silently skip the cut."""
    import bmesh
    z_target = (z_lo + z_hi) / 2
    bm.edges.ensure_lookup_table()
    edges = [e for e in bm.edges
             if abs(e.verts[0].co.z - e.verts[1].co.z)
             > 3 * math.hypot(e.verts[0].co.x - e.verts[1].co.x,
                              e.verts[0].co.y - e.verts[1].co.y)
             and min(e.verts[0].co.z, e.verts[1].co.z) < z_target
             < max(e.verts[0].co.z, e.verts[1].co.z)]
    if not edges:
        return None
    z_mid = sum((e.verts[0].co.z + e.verts[1].co.z) / 2
                for e in edges) / len(edges)
    bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1)
    bm.verts.ensure_lookup_table()
    return z_mid


def _slide_ring(bm, z_from, z_to, tol=0.004):
    for v in _ring_verts(bm, z_from, tol):
        v.co.z = z_to


def _tour_step_first_cup(context):
    import bmesh
    # Part 1, his order: the splash goes, he learns to move,
    # deletes the default CUBE ONLY - his Camera and Light
    # stay in the scene for the whole series (the camera makes
    # Part 4's first render; the lamp becomes Part 8's sun).
    cube = _scene_obj(context, "Cube")
    if cube is not None:
        bpy.data.objects.remove(cube, do_unlink=True)
    # The donut comes FIRST in this part (06:41), before the
    # cup: Shift+A -> Mesh -> Torus, sized in the operator
    # panel (F9 brings it back): Major Radius 0.1, Minor
    # Radius dragged to about 0.057, Major Segments 48,
    # Minor Segments 18, then right-click -> Shade Smooth.
    if _scene_obj(context, "Torus") is None \
            and _find_dough(context) is None:
        bpy.ops.mesh.primitive_torus_add(
            major_radius=DONUT_MAJOR, minor_radius=DONUT_MINOR,
            major_segments=48, minor_segments=18,
            location=(0, 0, 0))
        donut = context.object
        for poly in donut.data.polygons:
            poly.use_smooth = True
    # Then the cup (10:27): Cylinder, Radius 0.13, Depth
    # dragged to about mug height (UNSTATED - 0.24 picked),
    # Vertices 14 on purpose (a Subsurf is coming). Moved
    # behind the donut with G.
    bpy.ops.mesh.primitive_cylinder_add(
        radius=CUP_RADIUS, depth=CUP_DEPTH, vertices=14,
        location=(0.23, 0.19, CUP_DEPTH / 2))
    cup = context.object
    bm = bmesh.new()
    bm.from_mesh(cup.data)
    # Edit Mode, Face Select: delete the top FACE (17:57) -
    # faces only, the opening of the cup.
    bm.faces.ensure_lookup_table()
    top = [f for f in bm.faces
           if f.calc_center_median().z > CUP_DEPTH / 2 - 0.001]
    bmesh.ops.delete(bm, geom=top, context="FACES")
    # Loop cuts (22:43): one slid up near the rim, one down
    # near the base, to tighten the Subsurf's shape.
    z_mid = _subdivide_verticals(bm, -CUP_DEPTH / 2, CUP_DEPTH / 2)
    if z_mid is not None:
        _slide_ring(bm, z_mid, CUP_DEPTH / 2 - 0.024)
    z_low = _subdivide_verticals(bm, -CUP_DEPTH / 2, 0.0)
    if z_low is not None:
        _slide_ring(bm, z_low, -CUP_DEPTH / 2 + 0.020)
    # The bottom face gets an Inset (25:38), dragged by eye -
    # UNSTATED amount, 0.025 picked.
    bm.faces.ensure_lookup_table()
    bottom = [f for f in bm.faces
              if f.calc_center_median().z < -CUP_DEPTH / 2 + 0.001]
    if bottom:
        bmesh.ops.inset_region(bm, faces=bottom, thickness=0.025,
                               depth=0.0)
    bm.to_mesh(cup.data)
    bm.free()
    for poly in cup.data.polygons:
        poly.use_smooth = True
    # Modifiers, in his order: Solidify FIRST (18:47 - this
    # is the cup's thickness; its value is dragged by eye and
    # never stated - 0.004 picked, revisited at 26:47), then
    # Subdivision Surface (20:42; he raises it 1-2-3 on
    # camera to show the doubling - the resting level is
    # UNSTATED, 2 picked).
    walls = cup.modifiers.new("Solidify", "SOLIDIFY")
    walls.thickness = 0.004
    sub = cup.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 2
    # His last move of Part 1 (27:11): Save As.
    if not bpy.data.filepath:
        bpy.ops.wm.save_as_mainfile(
            filepath=_home("blender_buddy_my_donut.blend"))


def _tour_step_mug_reference(context):
    import bmesh
    cup = _containers(context)
    cup = cup[0] if cup else None
    if cup is None:
        raise RuntimeError("The cup comes first - that is Part 1.")
    # The reference photo (his is linked from the series
    # page): Add -> Image -> Reference, Alt+R clears its
    # rotation, R X 90 stands it upright, scaled to the mug
    # by eye against the front view (UNSTATED size).
    img = _reference_image(context)
    if not any(o.type == "EMPTY"
               and o.empty_display_type == "IMAGE"
               for o in context.scene.objects):
        bpy.ops.object.empty_add(
            type="IMAGE", location=(0.23, 0.33, 0.13),
            rotation=(math.pi / 2, 0, 0))
        ref = context.object
        ref.name = "Mug Reference"
        ref.data = img
        ref.empty_display_size = 0.30
    # The same cup is edited IN PLACE for the whole part -
    # no new cylinder is ever added. The reshaping is by eye
    # against the photo (every amount UNSTATED): rim loop
    # scaled in a little, the loop below about halfway toward
    # it, the mid loop slid to about 20% of the height and
    # scaled out (the mug's widest point), the bottom face
    # scaled in, extruded down a touch for the foot, and two
    # loop cuts bracketing the bottom to tighten the lip.
    bm = bmesh.new()
    bm.from_mesh(cup.data)
    _scale_ring(bm, CUP_DEPTH / 2, 0.94)
    _scale_ring(bm, CUP_DEPTH / 2 - 0.024, 0.97)
    z_mid = _subdivide_verticals(bm, -0.11, 0.10)
    if z_mid is not None:
        _slide_ring(bm, z_mid, -CUP_DEPTH / 2 + 0.2 * CUP_DEPTH)
        _scale_ring(bm, -CUP_DEPTH / 2 + 0.2 * CUP_DEPTH, 1.06)
    _scale_ring(bm, -CUP_DEPTH / 2, 0.93)
    bm.faces.ensure_lookup_table()
    bottom = [f for f in bm.faces
              if f.calc_center_median().z < -CUP_DEPTH / 2 + 0.001
              and len(f.verts) > 4]
    if bottom:
        out = bmesh.ops.extrude_face_region(bm, geom=bottom)
        new_verts = [g for g in out["geom"]
                     if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=new_verts,
                            vec=(0, 0, -0.010))
    for _ in range(2):
        _subdivide_verticals(bm, -CUP_DEPTH / 2 - 0.02,
                             -CUP_DEPTH / 2 + 0.03)
    bm.to_mesh(cup.data)
    bm.free()
    # The part's pivotal move (15:21): APPLY the Solidify -
    # so the handle, modelled next, does not get thickened
    # too. The Subsurf stays live.
    for mod in list(cup.modifiers):
        if mod.type == "SOLIDIFY":
            _apply_modifier(context, cup, mod.name)
            break
    _build_handle(context, cup)


def _build_handle(context, cup):
    """The handle, his way (Part 2, 16:44 onwards): one side
    face of the mug is extruded out and walked around with
    E / G / R until its end meets the body lower down; the
    two internal faces are deleted and the joint is closed
    with Bridge Edge Loops - the faster alternative he shows
    at 23:36, and the one a script can walk exactly. The
    path itself is drawn against the photo (UNSTATED)."""
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(cup.data)
    bm.faces.ensure_lookup_table()
    # The handle needs joint rows of its own: the cup's
    # tall middle band is a single face tall, and a handle
    # joins the body at two heights. Cut the vertical edges
    # that SPAN each joint height and set the new ring
    # exactly there - the definition his reshape leaves in
    # the wall where the handle lands.
    def cut_at(z_target):
        bm.edges.ensure_lookup_table()
        edges = [e for e in bm.edges
                 if abs(e.verts[0].co.z - e.verts[1].co.z)
                 > 3 * math.hypot(
                     e.verts[0].co.x - e.verts[1].co.x,
                     e.verts[0].co.y - e.verts[1].co.y)
                 and min(e.verts[0].co.z, e.verts[1].co.z)
                 < z_target
                 < max(e.verts[0].co.z, e.verts[1].co.z)]
        if not edges:
            return
        out = bmesh.ops.subdivide_edges(bm, edges=edges, cuts=1)
        for v in out["geom"]:
            if isinstance(v, bmesh.types.BMVert):
                v.co.z = z_target
        bm.faces.ensure_lookup_table()

    cut_at(-0.02)
    cut_at(-0.055)

    def face_at(angle, z_lo, z_hi, r_min=0.10, exclude=None):
        best = None
        for f in bm.faces:
            if f is exclude:
                continue
            c = f.calc_center_median()
            r = math.hypot(c.x, c.y)
            if r < r_min or not (z_lo < c.z < z_hi):
                continue
            a = abs((math.atan2(c.y, c.x) - angle + math.pi)
                    % (2 * math.pi) - math.pi)
            if a < 0.25 and (best is None or a < best[0]):
                best = (a, f)
        return best[1] if best else None

    start = face_at(0.0, 0.0, 0.10)
    if start is None:
        bm.free()
        raise RuntimeError("No side face found for the handle.")
    # Walk the extrusion out, up, over and down: cumulative
    # (x, z) steps at his scale - the handle stands about
    # 0.045 proud of the wall at its widest.
    path = [(0.020, 0.010), (0.014, 0.006), (0.006, -0.012),
            (-0.006, -0.022), (-0.014, -0.020), (-0.012, -0.014)]
    face = start
    for dx, dz in path:
        out = bmesh.ops.extrude_face_region(bm, geom=[face])
        new_verts = [g for g in out["geom"]
                     if isinstance(g, bmesh.types.BMVert)]
        bmesh.ops.translate(bm, verts=new_verts, vec=(dx, 0, dz))
        caps = [g for g in out["geom"]
                if isinstance(g, bmesh.types.BMFace)
                and all(v in new_verts for v in g.verts)]
        if not caps:
            break
        face = caps[0]
    end_center = face.calc_center_median()
    # The body face the handle's end lands on, lower down.
    joint = face_at(0.0, end_center.z - 0.03, end_center.z + 0.03,
                    exclude=face)
    if joint is not None and joint is not face:
        end_edges = list(face.edges)
        joint_edges = list(joint.edges)
        bmesh.ops.delete(bm, geom=[face, joint], context="FACES")
        bm.edges.ensure_lookup_table()
        live = [e for e in end_edges + joint_edges if e.is_valid]
        try:
            bmesh.ops.bridge_loops(bm, edges=live)
        except Exception:
            pass
    bm.faces.ensure_lookup_table()
    # Shade Smooth, and Shift+N - recalculated normals - for
    # the shading artifacts the join leaves behind.
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(cup.data)
    bm.free()
    for poly in cup.data.polygons:
        poly.use_smooth = True


def _tour_step_icing_hug(context):
    import bmesh
    dough = _find_dough(context)
    if dough is None:
        raise RuntimeError("The donut comes first - that is Part 1.")
    mug = _find_mug(context)
    # Part 3 opens with housekeeping (0:00): the mug object
    # is renamed "Mug", the torus "Donut", and the reference
    # image - its job done - is deleted.
    if mug is not None:
        mug.name = "Mug"
        # The mug moves out of frame (G -> X) while the
        # donut gets the stage.
        mug.location.x += 0.55
    dough.name = "Donut"
    for obj in list(context.scene.objects):
        if obj.type == "EMPTY" \
                and obj.empty_display_type == "IMAGE":
            bpy.data.objects.remove(obj, do_unlink=True)
    # The icing: Shift+D duplicates the Donut, Esc leaves the
    # copy exactly in place; the copy is renamed "Icing".
    if _scene_obj(context, "Icing") is None:
        icing = dough.copy()
        icing.data = dough.data.copy()
        context.scene.collection.objects.link(icing)
        icing.name = "Icing"
    icing = _scene_obj(context, "Icing")
    bm = bmesh.new()
    bm.from_mesh(icing.data)
    # Edit Mode, Vertex Select, X-Ray ON (Alt+Z - without it
    # the drag-select only catches the visible shell): select
    # the BOTTOM half and delete FACES - not vertices, or the
    # middle ring the icing needs would go with them.
    bm.faces.ensure_lookup_table()
    under = [f for f in bm.faces if f.calc_center_median().z < -0.001]
    bmesh.ops.delete(bm, geom=under, context="FACES")
    # Proportional Editing (O): a rim vertex pulled down (G Z)
    # drags its neighbours into a wavy, uneven edge; then the
    # drips - two adjacent rim points extruded (E Z) and
    # pulled down, all around, varying length and shape.
    # Amounts are by eye (UNSTATED); the wave and the drip
    # lengths here are seeded so the reference is stable.
    rng = random.Random(4)
    p1, p2, p3 = (rng.uniform(0, 6.28), rng.uniform(0, 6.28),
                  rng.uniform(0, 6.28))

    def wave(a):
        return (math.sin(a * 3 + p1) * 0.5
                + math.sin(a * 7 + p2) * 0.3
                + math.sin(a * 13 + p3) * 0.2)

    bm.verts.ensure_lookup_table()
    bm.edges.ensure_lookup_table()
    rim = [v for v in bm.verts if abs(v.co.z) < 0.004]
    for v in rim:
        a = math.atan2(v.co.y, v.co.x)
        v.co.z -= max(0.0, wave(a)) * 0.016
    # One ring up gets a whisper of the same pull - the
    # proportional falloff.
    for v in bm.verts:
        if 0.004 < v.co.z < 0.03:
            a = math.atan2(v.co.y, v.co.x)
            v.co.z -= max(0.0, wave(a)) * 0.006
    # The drips: boundary edges around the rim, extruded
    # down in runs of two, at seeded spots and lengths.
    bm.edges.ensure_lookup_table()
    boundary = [e for e in bm.edges if len(e.link_faces) == 1
                and abs(e.verts[0].co.z) < 0.02
                and math.hypot(e.verts[0].co.x,
                               e.verts[0].co.y) > 0.12]
    boundary.sort(key=lambda e: math.atan2(
        (e.verts[0].co + e.verts[1].co).y / 2,
        (e.verts[0].co + e.verts[1].co).x / 2))
    n = len(boundary)
    if n >= 8:
        step = max(2, n // 14)
        for i in range(0, n - 1, step):
            pair = [boundary[i], boundary[i + 1]]
            length = rng.uniform(0.012, 0.034)
            out = bmesh.ops.extrude_edge_only(bm, edges=pair)
            new_verts = [g for g in out["geom"]
                         if isinstance(g, bmesh.types.BMVert)]
            bmesh.ops.translate(bm, verts=new_verts,
                                vec=(0, 0, -length))
            # A second, shorter pull on some - the dribble
            # within the drip.
            bm.edges.ensure_lookup_table()
            tips = [e for e in bm.edges
                    if len(e.link_faces) == 1
                    and all(v in new_verts for v in e.verts)]
            if tips and rng.random() < 0.6:
                out = bmesh.ops.extrude_edge_only(bm, edges=tips)
                new_verts = [g for g in out["geom"]
                             if isinstance(g, bmesh.types.BMVert)]
                bmesh.ops.translate(
                    bm, verts=new_verts,
                    vec=(0, 0, -length * rng.uniform(0.3, 0.6)))
    bm.to_mesh(icing.data)
    bm.free()
    for poly in icing.data.polygons:
        poly.use_smooth = True
    # The modifier stack, added in his order, then put in
    # its final order: Solidify (Offset = 1 - the one setting
    # he states here; thickness by eye, UNSTATED, 0.003
    # picked), Subdivision Surface (viewport Levels = 2),
    # Shrinkwrap (Target = the Donut) - then Shrinkwrap is
    # dragged to the TOP of the stack (at the wrong order
    # the icing Z-fights the dough).
    for mod in list(icing.modifiers):
        icing.modifiers.remove(mod)
    thick = icing.modifiers.new("Solidify", "SOLIDIFY")
    thick.thickness = 0.003
    thick.offset = 1.0
    sub = icing.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 2
    hug = icing.modifiers.new("Shrinkwrap", "SHRINKWRAP")
    hug.target = dough
    _ensure_mod_order(context, icing,
                      ["Shrinkwrap", "Solidify", "Subdivision"])
    # Solidify's Edge Crease, set so the icing's edge hugs
    # instead of ballooning (value UNSTATED - full crease).
    thick.edge_crease_outer = 1.0
    # Then he APPLIES the modifiers, top to bottom (Ctrl+A
    # applies the active one): Shrinkwrap, Solidify, Subsurf.
    # The finished icing carries NO live modifiers - the
    # snapping is gone, by design.
    _apply_modifier(context, icing, "Shrinkwrap")
    _apply_modifier(context, icing, "Solidify")
    _apply_modifier(context, icing, "Subdivision")
    # Sculpt Mode: the Inflate/Deflate brush over the drip
    # heads and edges (thickness variation), the Grab brush
    # to shape. Amounts by eye (UNSTATED) - this gentle
    # seeded push along the normals stands in for the brush
    # pass a script cannot make.
    bm = bmesh.new()
    bm.from_mesh(icing.data)
    rng2 = random.Random(9)
    for v in bm.verts:
        r = math.hypot(v.co.x, v.co.y)
        if v.co.z < 0.005 and r > 0.09:
            push = rng2.uniform(0.0004, 0.0016)
            n = v.normal
            v.co.x += n.x * push
            v.co.y += n.y * push
            v.co.z += n.z * push
    bm.to_mesh(icing.data)
    bm.free()


def _build_plate(context):
    """The plate, modelled the way Part 4 models it (his
    Part 3 homework, shown at 00:00): a Circle with an NGON
    fill, three extrusions walked out and up into a rim,
    Subdivision Surface at level 2, then Solidify dragged
    ABOVE the Subsurf. Amounts are by eye (UNSTATED); the
    proportions are a dinner plate's against his donut."""
    import bmesh
    # The circle starts one Solidify thickness ABOVE the
    # tabletop: the shell grows downward from the floor,
    # so the plate's underside is what rests on the table.
    # Start the floor exactly on the tabletop instead and
    # the two surfaces land coplanar - the render then
    # shows the table through the well (z-fighting), a
    # black toothed disc where the plate should read.
    bpy.ops.mesh.primitive_circle_add(
        vertices=48, radius=0.235, fill_type="NGON",
        location=(0, 0, TABLE_TOP + 0.0025))
    plate = context.object  # his object is named "Circle"
    bm = bmesh.new()
    bm.from_mesh(plate.data)
    # His first two moves - extrude the face in place, then
    # delete the top face only - net out to exactly this:
    # the disc stays as the plate's floor and its rim loop
    # stands free, ready to be walked out into the rim.
    bm.verts.ensure_lookup_table()

    def rim_loop():
        zs = [v.co.z for v in bm.verts]
        z_top = max(zs)
        return [v for v in bm.verts if abs(v.co.z - z_top) < 1e-6
                and math.hypot(v.co.x, v.co.y) > 0.01]

    def scale_loop(factor):
        for v in rim_loop():
            v.co.x *= factor
            v.co.y *= factor

    def extrude_loop(dz=0.0):
        bm.edges.ensure_lookup_table()
        loop_verts = set(rim_loop())
        edges = [e for e in bm.edges
                 if len(e.link_faces) == 1
                 and all(v in loop_verts for v in e.verts)]
        out = bmesh.ops.extrude_edge_only(bm, edges=edges)
        new_verts = [g for g in out["geom"]
                     if isinstance(g, bmesh.types.BMVert)]
        if dz:
            bmesh.ops.translate(bm, verts=new_verts,
                                vec=(0, 0, dz))
        bm.verts.ensure_lookup_table()
        return new_verts

    scale_loop(1.06)          # the lip begins (S, by eye)
    extrude_loop()
    scale_loop(1.10)          # a flat rim section
    extrude_loop(0.016)       # the rim's rise (E, Z, pull up)
    # A loop cut slid toward the rim to sharpen it.
    bm.edges.ensure_lookup_table()
    verticals = [e for e in bm.edges
                 if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.004]
    if verticals:
        bmesh.ops.subdivide_edges(bm, edges=verticals, cuts=1)
    bm.to_mesh(plate.data)
    bm.free()
    for poly in plate.data.polygons:
        poly.use_smooth = True
    # Subdivision Surface, Levels = 2 - then Solidify,
    # dragged above it (final order: Solidify -> Subsurf).
    # Thickness UNSTATED, 0.0025 picked.
    sub = plate.modifiers.new("Subdivision", "SUBSURF")
    sub.levels = 2
    walls = plate.modifiers.new("Solidify", "SOLIDIFY")
    walls.thickness = 0.0025
    _ensure_mod_order(context, plate, ["Solidify", "Subdivision"])
    return plate


def _tour_step_first_picture(context):
    scene = context.scene
    dough = _find_dough(context)
    icing = _find_icing(context, dough)
    mug = _find_mug(context)
    if dough is None or icing is None:
        raise RuntimeError("The donut comes first - that is Part 3.")
    # The plate (his Part 3 homework, modelled at the top of
    # Part 4) and the table under everything.
    plate = _find_plate(context, dough)
    if plate is None:
        plate = _build_plate(context)
    if _find_table(context, dough) is None:
        # A Plane, scaled up a little (UNSTATED amount): it
        # is a card - only the top shows. The set is stood on
        # it: plate's foot and mug's base on its top face.
        bpy.ops.mesh.primitive_plane_add(
            size=2, location=(0, 0, TABLE_TOP))
        table = context.object  # his object is named "Plane"
        table.scale = (2.4, 2.4, 1.0)
    # The set, stood on the table: the donut rests in the
    # plate's well (whose floor stands one shell thickness
    # over the tabletop - see _build_plate); the mug - out
    # of frame since Part 3 - comes back in behind the
    # donut, standing on the table.
    dough.location.z = (TABLE_TOP + 0.0025 + DONUT_MINOR
                        + 0.002)
    icing.location = dough.location
    if mug is not None:
        mug.location.x = 0.205
        mug.location.y = 0.115
        mug.location.z = TABLE_TOP + 0.124
    # The Lattice (10:38): select BOTH the Donut and the
    # Icing -> Lattice Deform Selected (5.0's one-click
    # path; done longhand here so it runs on any version -
    # a lattice fitted to the pair, one Lattice modifier on
    # each). Resolution raised with a division in the middle
    # (exact U/V/W UNSTATED - 5 x 5 x 3 picked).
    if _scene_obj(context, "Lattice") is None:
        lat_data = bpy.data.lattices.new("Lattice")
        lat_data.points_u = 5
        lat_data.points_v = 5
        lat_data.points_w = 3
        lat = bpy.data.objects.new("Lattice", lat_data)
        scene.collection.objects.link(lat)
        lat.location = (dough.location.x, dough.location.y,
                        dough.location.z)
        lat.scale = (0.37, 0.37, 0.16)
        # The middle ring of points, scaled IN (Proportional
        # Editing OFF): the concave fry-line around the
        # donut's equator. A few single points nudged for
        # puffy spots - all by eye (UNSTATED amounts).
        for point in lat_data.points:
            cx, cy, cz = point.co_deform
            rr = math.hypot(cx, cy)
            if abs(cz) < 0.01 and rr > 0.18:
                point.co_deform.x = cx * 0.86
                point.co_deform.y = cy * 0.86
        pts = [p for p in lat_data.points
               if abs(p.co_deform.z) > 0.01]
        if len(pts) > 4:
            pts[3].co_deform.z += 0.012
            pts[7].co_deform.x += 0.010
        for target in (dough, icing):
            mod = target.modifiers.new("Lattice", "LATTICE")
            mod.object = lat
        # Applied to both, and the lattice object deleted -
        # his order, so the deform is baked into both meshes
        # and neither can drift from the other.
        _apply_modifier(context, dough, "Lattice")
        _apply_modifier(context, icing, "Lattice")
        bpy.data.objects.remove(lat, do_unlink=True)
    # Render Properties: Eevee Ray Tracing ON (20:48 - he
    # calls the off default "a mistake"; it is what produces
    # bounce light and crevice detail from here on).
    try:
        scene.eevee.use_raytracing = True
    except Exception:
        pass
    # Basic materials (23:28): icing pink by eye with
    # Roughness about 0.2 (stated); the mug near-black and
    # glossy - a placeholder, never full black; the plate
    # the same idea, slightly shinier; the donut light
    # brown. Colours by eye (UNSTATED).
    _paint(icing, "Buddy Pink", (0.88, 0.17, 0.41, 1.0),
           roughness=0.2)
    if mug is not None:
        _paint(mug, "Buddy Mug Placeholder",
               (0.03, 0.03, 0.03, 1.0), roughness=0.25)
    _paint(plate, "Buddy Plate Placeholder",
           (0.55, 0.55, 0.56, 1.0), roughness=0.18)
    # Subsurface, his recipe (26:59): Weight all the way to
    # 1 ("this value is supposed to be zero or one"), Radius
    # dragged across R, G, B to (1, 1, 1) - the (1, 2, 0.1)
    # default is for skin and makes food look red - and the
    # amount steered with Scale, by eye (UNSTATED: 0.05 on
    # the icing, 0.10 on the dough, picked milky/buttery).
    for obj, mat_name, rgba, rough, scale in (
            (icing, "Buddy Pink", (0.88, 0.17, 0.41, 1.0), 0.2, 0.05),
            (dough, "Buddy Dough", (0.55, 0.32, 0.12, 1.0), 0.5, 0.10)):
        _paint(obj, mat_name, rgba, roughness=rough, subsurface=1.0,
               sss_radius=(1.0, 1.0, 1.0), sss_scale=scale)
    # The first picture (16:02) comes from the scene's
    # ORIGINAL default camera - the one that has been there
    # since Part 1. He frames it with Lock Camera to View
    # (18:12): orbit the view itself until the shot sits
    # right, then uncheck. The framing is by eye (UNSTATED);
    # the camera's display size is reduced so its icon stops
    # dominating a small scene (UNSTATED amount).
    cam = scene.camera
    if cam is not None:
        from mathutils import Vector
        cam.location = (0.40, -0.92, 0.34)
        cam.rotation_euler = (
            Vector((0.04, 0.01, -0.02)) - cam.location
        ).to_track_quat("-Z", "Y").to_euler()
        cam.data.display_size = 0.1
    _set_default_picture_path(scene)
    bpy.ops.render.render(write_still=True)


def _lift_icing_over_displacement(dough, icing):
    """Lift the icing shell along its own vertex normals by
    just over the dough material's true displacement peak.

    The frame round's first recommendation, folded in: the
    dough's render-time displacement rises through the
    icing, which Part 3 shrinkwrapped onto the UNDISPLACED
    dough - dough-coloured patches on the finished donut in
    every engine, proven by control renders in
    demo/checks/FRAME_RESTART_LOG.md. The peak is computed
    from the height picture's real range and the
    Displacement node's Scale - never a guessed number -
    so the relief peaks stay under the icing's skin while
    the hug reads unchanged. Returns the lift used (0.0
    when there is nothing to clear)."""
    peak = 0.0
    for mat in dough.data.materials:
        if mat is None or not mat.use_nodes \
                or mat.node_tree is None:
            continue
        for node in mat.node_tree.nodes:
            if node.type != "DISPLACEMENT":
                continue
            try:
                scale = float(
                    node.inputs["Scale"].default_value)
                mid = float(
                    node.inputs["Midlevel"].default_value) \
                    if "Midlevel" in node.inputs else 0.5
            except Exception:
                continue
            img = None
            for link in node.inputs["Height"].links:
                if link.from_node.type == "TEX_IMAGE":
                    img = link.from_node.image
            if img is None:
                continue
            px = list(img.pixels)
            if px:
                peak = max(peak, scale * (max(px[0::4]) - mid))
    if peak <= 0 or icing is None:
        return 0.0
    lift = peak * 1.15 + 0.0005
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(icing.data)
    for v in bm.verts:
        n = v.normal
        sx, sy, sz = n.x * lift, n.y * lift, n.z * lift
        # Never let the lift push a point TOWARD the ring's
        # axis. On the shell's hole-facing wall the normals
        # point inward; shoving those points at the axis buys
        # no clearance (the dough's relief is hidden inside
        # the hole there) and it narrows the hole until the
        # shape test that finds the icing by its ring stops
        # recognising it. The outward and upward parts of
        # the step stay - the relief pokes through there.
        r = math.hypot(v.co.x, v.co.y)
        if r > 1e-6:
            radial = (sx * v.co.x + sy * v.co.y) / r
            if radial < 0.0:
                sx -= radial * v.co.x / r
                sy -= radial * v.co.y / r
        v.co.x += sx
        v.co.y += sy
        v.co.z += sz
    bm.to_mesh(icing.data)
    bm.free()
    return lift


def _tour_step_real_surfaces(context):
    dough = _find_dough(context)
    icing = _find_icing(context, dough)
    plate = _find_plate(context, dough)
    table = _find_table(context, dough)
    mug = _find_mug(context)
    if None in (dough, icing, plate, table):
        raise RuntimeError("The scene comes first - that is Part 4.")
    # The table, wired BY HAND (00:00-15:55) - the one
    # surface he builds node by node: the concrete set from
    # poliigon.com/donut (a stand-in set here), colour into
    # Base Color, the normal picture through a Normal Map
    # node, the roughness picture into Roughness - every map
    # but the colour set to Non-Color. (The tiling repeat is
    # the stand-in's own - his capture is a 30 x 30 cm tile.)
    _apply_pbr(table, _make_texture_set(
        "Table Concrete", (0.62, 0.60, 0.57), 41, 0.75),
        map_scale=6.0)
    # The plate (18:08) gets its ceramic through the
    # Poliigon add-on in the video; nothing shows until it
    # is unwrapped (U -> Unwrap, Angle Based) - so: unwrap
    # first, then the surface. (Stand-in set here.)
    _try_unwrap(context, plate)
    _apply_pbr(plate, _make_texture_set(
        "Plate Ceramic", (0.80, 0.79, 0.80), 22, 0.3))
    # The icing (21:25): the glaze set goes on; then he
    # repairs what the add-on overrode - the Base Color
    # texture is disconnected (its colour is negligible),
    # and the subsurface is set BY HAND again: pink by eye,
    # Weight 1, Radius (1, 1, 1), Scale by eye (UNSTATED -
    # the Part 4 setting, 0.05, kept).
    _try_unwrap(context, icing)
    glaze = _make_texture_set(
        "Icing Glaze", (0.88, 0.17, 0.41), 24, 0.2)
    mat = _apply_pbr(icing, glaze,
                     sss=(1.0, (1.0, 1.0, 1.0), 0.05))
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    for link in list(bsdf.inputs["Base Color"].links):
        nt.links.remove(link)
    bsdf.inputs["Base Color"].default_value = \
        (0.88, 0.17, 0.41, 1.0)
    # The unlinked colour picture's node is then removed
    # outright: a picture node feeding nothing pretends the
    # surface is textured when it is a flat hand-set colour
    # (frame round's third recommendation). The roughness
    # and normal pictures stay wired - those are his
    # recipe, and the surface check reads them.
    for node in list(nt.nodes):
        if node.type == "TEX_IMAGE" \
                and node.image is glaze["colour"]:
            nt.nodes.remove(node)
    # The donut (27:39): the scanned-donut set (a stand-in
    # here), then displacement - the height map into the
    # Material Output's Displacement socket, the material's
    # setting to "Displacement and Bump", a Subdivision
    # Surface at viewport 3 / render 3 to carry the detail,
    # and the Displacement Scale tuned down 0.2 -> 0.15 ->
    # 0.12 (stated), stopping when the dough no longer
    # clips through the icing. Subsurface set by hand again:
    # Weight 1, Radius (1, 1, 1), Scale by eye (UNSTATED -
    # 0.10 kept, "buttery").
    mat = _apply_pbr(dough, _make_texture_set(
        "Dough Crumb", (0.55, 0.32, 0.12), 23, 0.55),
        sss=(1.0, (1.0, 1.0, 1.0), 0.10), displacement=0.12)
    if not any(m.type == "SUBSURF" for m in dough.modifiers):
        sub = dough.modifiers.new("Subdivision", "SUBSURF")
        sub.levels = 3
        sub.render_levels = 3
    # With the displacement live, the icing gets its
    # clearance lift - the dough's relief peaks must never
    # poke through the shell Part 3 shrinkwrapped onto the
    # undisplaced dough (see _lift_icing_over_displacement).
    _lift_icing_over_displacement(dough, icing)
    # The mug is explicitly deferred - "the final object to
    # texture is our mug, and I'm going to do that in the
    # next part." Nothing touches it here.
    _ = mug


def _tour_step_unwrap_mug(context):
    import bmesh
    mug = _find_mug(context)
    table = _find_table(context)
    if mug is None:
        raise RuntimeError("The mug comes first - that is Part 2.")
    # The mug's texture arrives (00:00): "Rustic Gold
    # Ceramic" through the add-on (a stand-in set here). It
    # lands half-right on the primitive UVs - the handle's
    # UVs are garbage - which is the part's problem to solve.
    _apply_pbr(mug, _make_texture_set(
        "Mug Ceramic", (0.36, 0.21, 0.10), 26, 0.35))
    # Mug material cleanup (his order comes after the
    # unwrap, but the tree is simplest tended now): the
    # Roughness map is disconnected and roughness steered
    # with the slider (value UNSTATED - 0.3 picked).
    mat = mug.data.materials[0]
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    for link in list(bsdf.inputs["Roughness"].links):
        nt.links.remove(link)
    bsdf.inputs["Roughness"].default_value = 0.3
    # The Subsurf's On Cage display goes ON, so the cage
    # doesn't hide mesh while unwrapping; Live Unwrap is on
    # in his UI (a display preference - nothing to build).
    for mod in mug.modifiers:
        if mod.type == "SUBSURF":
            mod.show_on_cage = True
    # The seams (Ctrl+E -> Mark Seam), in his layout: the
    # ring at the handle's top joint, the ring at its bottom
    # joint (the handle becomes its own island), a vertical
    # line just beside the handle (hidden), the loop inside
    # the mug at its base, a vertical line down the inside,
    # and the loop around the underside. The build finds
    # them by shape - the layout is his, the search is by
    # the same landmarks he names.
    bm = bmesh.new()
    bm.from_mesh(mug.data)
    verts = list(bm.verts)
    zs = [v.co.z for v in verts]
    z_min, z_max = min(zs), max(zs)
    height = z_max - z_min
    rs = {v: math.hypot(v.co.x, v.co.y) for v in verts}
    r_max = max(rs.values())
    # The handle lives outside the wall (r beyond the body's
    # own radius); its joints are where it leaves and lands.
    handle = [v for v in verts if rs[v] > 1.12 * 0.13]
    h_angles = [math.atan2(v.co.y, v.co.x) for v in handle]
    a_handle = sum(h_angles) / len(h_angles) if h_angles else 0.0

    def ang_gap(v, target):
        return abs((math.atan2(v.co.y, v.co.x) - target
                    + math.pi) % (2 * math.pi) - math.pi)

    bm.edges.ensure_lookup_table()
    for e in bm.edges:
        a, b = e.verts
        mid = (a.co + b.co) / 2
        r_mid = math.hypot(mid.x, mid.y)
        seam = False
        # Handle joint rings: edges among handle verts near
        # the handle's top and bottom ends.
        if a in handle and b in handle:
            if mid.z > z_min + 0.62 * height \
                    or mid.z < z_min + 0.30 * height:
                seam = True
        # The hidden vertical beside the handle (outer wall),
        # and its twin down the inside.
        vertical = abs(a.co.z - b.co.z) > 0.004 \
            and math.hypot(a.co.x - b.co.x,
                           a.co.y - b.co.y) < 0.004
        if vertical and ang_gap(a, a_handle) > 0.15 \
                and ang_gap(a, a_handle) < 0.45:
            seam = True
        # The loops: inside base, and the underside.
        ring = abs(a.co.z - b.co.z) < 0.002
        if ring and mid.z < z_min + 0.06 * height:
            seam = True
        if ring and mid.z > z_max - 0.03 * height \
                and r_mid < 0.85 * r_max:
            seam = True
        if seam:
            e.seam = True
    bm.to_mesh(mug.data)
    bm.free()
    # U -> Unwrap (Live Unwrap has been updating all along).
    _try_unwrap(context, mug)
    # The table's colour surgery (21:52) - where the finale's
    # dark counter is actually made: an RGB Curves node
    # between the colour texture and the Principled (pull
    # the shadows down, lift the top slightly - the pale
    # concrete goes dark and contrasty), then a Hue
    # Saturation Value node dropping the saturation until
    # the yellow-green cast is gone. Both shapes UNSTATED.
    if table is not None and table.data.materials:
        tmat = table.data.materials[0]
        if tmat is not None and tmat.use_nodes:
            nt = tmat.node_tree
            tbsdf = nt.nodes.get("Principled BSDF")
            links = list(tbsdf.inputs["Base Color"].links)
            if links:
                src = links[0].from_socket
                for link in links:
                    nt.links.remove(link)
                curves = nt.nodes.new("ShaderNodeRGBCurve")
                curves.location = (120, 200)
                comp = curves.mapping.curves[3]
                comp.points[0].location = (0.0, 0.0)
                comp.points[1].location = (1.0, 1.0)
                comp.points.new(0.30, 0.16)
                comp.points.new(0.70, 0.74)
                curves.mapping.update()
                hsv = nt.nodes.new("ShaderNodeHueSaturation")
                hsv.location = (220, 200)
                hsv.inputs["Saturation"].default_value = 0.55
                nt.links.new(src, curves.inputs["Color"])
                nt.links.new(curves.outputs["Color"],
                             hsv.inputs["Color"])
                nt.links.new(hsv.outputs["Color"],
                             tbsdf.inputs["Base Color"])
    # The coffee foam (25:05), built from the mug itself -
    # not a new primitive: the mug's inner rim loop is
    # duplicated in place and Separated (P) into its own
    # object, "Foam"; the ring is filled (F), inset (I),
    # its centre lowered (G Z - the meniscus whose raised
    # edge catches light), and inset once more. Amounts by
    # eye (UNSTATED).
    if _find_foam(context, mug) is None:
        bm = bmesh.new()
        bm.from_mesh(mug.data)
        bm.verts.ensure_lookup_table()
        top_z = max(v.co.z for v in bm.verts)
        rim = [v for v in bm.verts
               if v.co.z > top_z - 0.02
               and 0.08 < math.hypot(v.co.x, v.co.y) < 0.121]
        rim.sort(key=lambda v: math.atan2(v.co.y, v.co.x))
        coords = [tuple(v.co) for v in rim]
        bm.free()
        if len(coords) >= 8:
            n = len(coords)
            fmesh = bpy.data.meshes.new("Foam")
            fmesh.from_pydata(
                coords, [(i, (i + 1) % n) for i in range(n)],
                [list(range(n))])
            fmesh.update()
            foam = bpy.data.objects.new("Foam", fmesh)
            context.scene.collection.objects.link(foam)
            foam.matrix_world = mug.matrix_world.copy()
            bm = bmesh.new()
            bm.from_mesh(fmesh)
            bm.faces.ensure_lookup_table()
            # A lone filled ring is all boundary, so the
            # inset must explicitly include the boundary
            # (the UI's default); bmesh otherwise leaves it
            # untouched and returns only its new side faces.
            bmesh.ops.inset_region(
                bm, faces=list(bm.faces), thickness=0.012,
                depth=0.0, use_boundary=True)
            bm.faces.ensure_lookup_table()
            # The inset's centre is the remaining face whose
            # middle sits closest to the mug's axis.
            inner = min(
                bm.faces,
                key=lambda f: math.hypot(
                    f.calc_center_median().x,
                    f.calc_center_median().y),
                default=None)
            if inner is not None:
                iverts = list(inner.verts)
                bmesh.ops.translate(bm, verts=iverts,
                                    vec=(0, 0, -0.006))
                bmesh.ops.inset_region(bm, faces=[inner],
                                       thickness=0.008, depth=0.0)
            bm.to_mesh(fmesh)
            bm.free()
            for poly in fmesh.polygons:
                poly.use_smooth = True
            # Its texture: the "Coffee Foam Atlas" (nine
            # designs on one sheet; a bubbly stand-in set
            # here). UVs from the top view, the island scaled
            # down over ONE of the nine designs - his pick
            # was "that one at the top"; the learner chooses.
            uv = fmesh.uv_layers.new(name="UVMap")
            xs = [c[0] for c in coords]
            ys = [c[1] for c in coords]
            span = max(max(xs) - min(xs), max(ys) - min(ys), 1e-6)
            for loop in fmesh.loops:
                co = fmesh.vertices[loop.vertex_index].co
                uv.data[loop.index].uv = (
                    0.345 + (co.x - min(xs)) / span * 0.30,
                    0.675 + (co.y - min(ys)) / span * 0.30)
            _apply_pbr(foam, _make_texture_set(
                "Foam Atlas", (0.80, 0.70, 0.55), 27, 0.5))


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
    import bmesh
    from mathutils import Vector
    grp = _scatter_group()
    if grp is None:
        raise RuntimeError(
            "Scatter on Surface is one of Blender 5.0's new "
            "tools, and this copy of Blender does not have it. "
            "This step waits for Blender 5.0 or newer - every "
            "other step works on what you have.")
    dough = _find_dough(context)
    icing = _find_icing(context, dough)
    if icing is None:
        raise RuntimeError("Sprinkles need the icing first - "
                           "that is Part 3.")
    # One sprinkle (00:00): the 3D cursor is planted on the
    # donut's top first (new objects are born at the cursor
    # - the part's first lesson). The sprinkle itself is a
    # Cylinder - he rejects spheres: Radius dragged to
    # nearly nothing then a touch back, Depth lengthened,
    # Vertices = 6 (both amounts UNSTATED: 0.0016 / 0.02
    # picked at his scale), a Subdivision Surface, loop cuts
    # near both ends to round the caps, Shade Smooth, and
    # the name "Sprinkle" (F2).
    if _scene_obj(context, "Sprinkle") is None:
        top = dough.matrix_world.translation.z \
            + dough.dimensions.z / 2
        context.scene.cursor.location = (
            dough.matrix_world.translation.x + 0.03,
            dough.matrix_world.translation.y, top + 0.004)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=0.0016, depth=0.02, vertices=6,
            location=context.scene.cursor.location)
        spr = context.object
        spr.name = "Sprinkle"
        bm = bmesh.new()
        bm.from_mesh(spr.data)
        edges = [e for e in bm.edges
                 if abs(e.verts[0].co.z - e.verts[1].co.z) > 0.01]
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=2)
        bm.to_mesh(spr.data)
        bm.free()
        for poly in spr.data.polygons:
            poly.use_smooth = True
        sub = spr.modifiers.new("Subdivision", "SUBSURF")
        sub.levels = 1
    # The variants (04:23): duplicate the sprinkle several
    # times and twist, bend and resize each BY HAND into
    # variants - his count on screen is six sharing the
    # material later. (The deformations here are seeded
    # stand-ins for hand work - the shapes are the learner's
    # modelling practice in the real part.)
    variants = [_scene_obj(context, "Sprinkle")]
    rng = random.Random(21)
    for i in range(5):
        src = variants[0]
        if _scene_obj(context, f"Sprinkle.{i + 1:03d}") is None:
            dup = src.copy()
            dup.data = src.data.copy()
            context.scene.collection.objects.link(dup)
            dup.location = src.location + Vector(
                (0.03 * (i + 1), 0.012 * (i % 3), 0))
            dup.rotation_euler = (
                rng.uniform(-0.5, 0.5), rng.uniform(0, 3.14),
                rng.uniform(0, 6.28))
            dup.scale = (rng.uniform(0.85, 1.1),
                         rng.uniform(0.85, 1.1),
                         rng.uniform(0.8, 1.25))
        variants.append(_scene_obj(
            context, f"Sprinkle.{i + 1:03d}"))
    variants = [v for v in variants if v is not None]
    # Origins to geometry (24:09's companion move, done
    # while they're all in hand): instances spawn from
    # their origins, and centred origins intersect less.
    _set_active(context, variants[0])
    for v in variants:
        v.select_set(True)
    try:
        bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY",
                                  center="BOUNDS")
    except Exception:
        pass
    # All variants into a NEW Collection named "Sprinkles"
    # (M -> Move to Collection), then the collection is
    # UNCHECKED - hidden from viewport and render; the
    # scatter still reads it.
    coll = bpy.data.collections.get("Sprinkles")
    if coll is None:
        coll = bpy.data.collections.new("Sprinkles")
        context.scene.collection.children.link(coll)
    for v in variants:
        for parent in list(v.users_collection):
            parent.objects.unlink(v)
        coll.objects.link(v)
    coll.hide_viewport = True
    coll.hide_render = True
    # One material for ALL the sprinkles, named "Sprinkles"
    # (Ctrl+L -> Link -> Materials in the video; assigned
    # directly here). The colours are randomized PER
    # INSTANCE in its node tree - Object Info's Random into
    # a Color Ramp set to CONSTANT (one flat colour per
    # sprinkle, never a gradient): aqua the primary, then
    # purple, pink, white, yellow, pastel, saturation under
    # 100%. Roughness "a little bit shiny" (UNSTATED - 0.35
    # picked); subsurface his recipe with the Scale "really
    # low" (UNSTATED - 0.02 picked; Part 8 retunes it to
    # the stated 0.08).
    mat = bpy.data.materials.get("Sprinkles")
    if mat is None:
        mat = bpy.data.materials.new("Sprinkles")
    mat.use_nodes = True
    nt = mat.node_tree
    for node in list(nt.nodes):
        nt.nodes.remove(node)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (560, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (340, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    bsdf.inputs["Roughness"].default_value = 0.35
    if "Subsurface Weight" in bsdf.inputs:
        bsdf.inputs["Subsurface Weight"].default_value = 1.0
    if "Subsurface Radius" in bsdf.inputs:
        bsdf.inputs["Subsurface Radius"].default_value = \
            (1.0, 1.0, 1.0)
    if "Subsurface Scale" in bsdf.inputs:
        bsdf.inputs["Subsurface Scale"].default_value = 0.02
    info = nt.nodes.new("ShaderNodeObjectInfo")
    info.location = (0, 120)
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (170, 120)
    ramp.color_ramp.interpolation = "CONSTANT"
    stops = [(0.00, (0.45, 0.85, 0.80, 1.0)),
             (0.55, (0.45, 0.85, 0.80, 1.0)),
             (0.62, (0.60, 0.40, 0.85, 1.0)),
             (0.72, (0.95, 0.55, 0.70, 1.0)),
             (0.82, (0.97, 0.96, 0.94, 1.0)),
             (0.92, (0.95, 0.85, 0.35, 1.0)),
             (1.00, (0.95, 0.85, 0.35, 1.0))]
    els = ramp.color_ramp.elements
    els[0].position, els[0].color = stops[0]
    els[1].position, els[1].color = stops[-1]
    for pos, col in stops[1:-1]:
        el = els.new(pos)
        el.color = col
    nt.links.new(info.outputs["Random"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])
    for v in variants:
        v.data.materials.clear()
        v.data.materials.append(mat)
    # The painted mask (12:44): Weight Paint mode on the
    # icing, Front Faces Only on, the top painted red
    # (weight 1) where sprinkles belong, softer at the
    # edges. It writes into a VERTEX GROUP - his keeps the
    # default name "Group". (Painted here by the icing's
    # own shape: full weight on top, a soft falloff down
    # the sides, none underneath.)
    vg = icing.vertex_groups.get("Group")
    if vg is None:
        vg = icing.vertex_groups.new(name="Group")
    zs = [v.co.z for v in icing.data.vertices]
    z_top = max(zs)
    z_bot = min(zs)
    full = []
    soft = []
    for v in icing.data.vertices:
        t = (v.co.z - z_bot) / max(z_top - z_bot, 1e-6)
        if t > 0.62:
            full.append(v.index)
        elif t > 0.38:
            soft.append((v.index, (t - 0.38) / 0.24 * 0.85))
    if full:
        vg.add(full, 1.0, "REPLACE")
    for i, w in soft:
        vg.add([i], w, "REPLACE")
    # His standing colour choice for the series' renders,
    # set in this part (33:34): Colour Management Look -
    # Medium High Contrast, stored under whichever spelling
    # this Blender's enum uses.
    _set_series_look(context.scene)
    # The modifier (08:35): Scatter on Surface on the
    # Icing. Every setting below is his, written through the
    # group's own input names and read back by the check:
    # Instancing Type Collection -> "Sprinkles", Pick
    # Instance ON, Reset Transform (its default ON state is
    # what his button press restores), Alignment Axis Y,
    # Randomize ON with Rotation Y = 360 degrees and X "a
    # little bit" (UNSTATED - 0.35 rad picked), Surface
    # Offset raised "very, very slightly" (UNSTATED - 0.0008
    # picked), the painted "Group" wired as the DISTRIBUTION
    # MASK attribute - not the Density input (his warning),
    # Density Method = Density at Density = 900 (stated),
    # Distribution Method = Poisson Disk with a Minimum
    # Distance (UNSTATED - 0.012 picked) and a cycled Seed
    # (UNSTATED - 3 picked).
    if not any(m.type == "NODES" and m.node_group is grp
               for m in icing.modifiers):
        mod = icing.modifiers.new("Scatter on Surface", "NODES")
        mod.node_group = grp
        _set_mod_input(mod, "Instance Type", "Collection")
        _set_mod_input(mod, "Collection", coll)
        _set_mod_input(mod, "Pick Instance", True)
        _set_mod_input(mod, "Alignment Axis", "Y")
        _set_mod_input(mod, "Randomize", True)
        _set_mod_input(mod, "Randomize Rotation",
                       (0.35, 6.2832, 0.0))
        _set_mod_input(mod, "Surface Offset", 0.0008)
        _set_mod_input(mod, "Masking", True)
        _set_mod_input(mod, "Density Method", "Density")
        _set_mod_input(mod, "Density", 900.0)
        _set_mod_input(mod, "Distribution Method", "Poisson Disk")
        _set_mod_input(mod, "Minimum Distance", 0.012)
        _set_mod_input(mod, "Seed", 3)
        mask = _mod_inputs(mod).get("Distribution Mask")
        if mask is not None:
            try:
                mask.type = "ATTRIBUTE"
            except Exception:
                pass
            mask.attribute_name = "Group"


def _set_series_look(scene):
    """His standing Colour Management Look for the series'
    renders - Medium High Contrast, set in Part 7 (33:34).
    The enum's spelling differs across Blender versions
    ('AgX - Medium High Contrast' on 5.x, the bare name on
    4.2), and the built scene must store it on either: the
    shipped demo scene carried NO look because the one
    spelling the build tried silently failed on the other
    version (frame round's fifth recommendation)."""
    for name in ("AgX - Medium High Contrast",
                 "Medium High Contrast"):
        try:
            scene.view_settings.look = name
            return
        except Exception:
            continue


def _park_out_of_frame(context, obj):
    """Move a window blocker sideways - along the camera's
    own right - until every corner of it projects outside
    the scene camera's frame.

    His blockers are never IN frame (that is the trick);
    the build shipped them bare and never checked the
    frame, and the finale render wore one as a pale slab
    in the corner (frame round's fourth recommendation).
    The blockers keep their height, their tilt and their
    place in the sun's path - only the sideways step
    changes - so the sliver of light they leave is the
    same sliver, seen from a camera they no longer
    photobomb. They still render and still cast: only
    their position moves."""
    from mathutils import Vector
    from bpy_extras.object_utils import world_to_camera_view
    scene = context.scene
    cam = scene.camera
    if cam is None:
        return
    context.view_layer.update()
    right = cam.matrix_world.to_3x3() @ Vector((1, 0, 0))
    right.z = 0.0
    if right.length < 1e-6:
        return
    right.normalize()

    def span():
        corners = [obj.matrix_world @ Vector(c)
                   for c in obj.bound_box]
        xs = [world_to_camera_view(scene, cam, c).x
              for c in corners]
        return min(xs), max(xs)

    lo, hi = span()
    if lo >= 1.03 or hi <= -0.03:
        return  # already clear of the frame
    direction = 1.0 if (lo + hi) / 2 >= 0.5 else -1.0
    for _ in range(80):
        obj.location += right * (0.02 * direction)
        context.view_layer.update()
        lo, hi = span()
        if lo >= 1.03 or hi <= -0.03:
            break


def _parent_keep(context, child, parent):
    """Ctrl+P -> Object (Keep Transform): the child keeps
    exactly where it sits in the world, now riding with the
    parent."""
    if child is None or parent is None or child is parent:
        return
    context.view_layer.update()
    inv = parent.matrix_world.inverted()
    child.parent = parent
    child.matrix_parent_inverse = inv


def _tour_step_final_picture(context):
    from mathutils import Vector
    scene = context.scene
    dough = _find_dough(context)
    icing = _find_icing(context, dough)
    mug = _find_mug(context)
    plate = _find_plate(context, dough)
    table = _find_table(context, dough)
    foam = _find_foam(context, mug)
    if None in (dough, icing, mug, plate, table):
        raise RuntimeError("The whole set comes first - "
                           "that is Parts 1-7.")
    # Housekeeping first (00:15): parenting, Ctrl+P ->
    # Object (Keep Transform) four times - Icing rides the
    # Donut, the Donut rides the Plate, the Foam rides the
    # Mug, and the Plate and Mug ride the table.
    _parent_keep(context, icing, dough)
    _parent_keep(context, dough, plate)
    _parent_keep(context, foam, mug)
    _parent_keep(context, plate, table)
    _parent_keep(context, mug, table)
    # And the renames arrive HERE, in the finale: the plane
    # becomes "Table", the plate object becomes "Plate".
    table.name = "Table"
    plate.name = "Plate"
    # The sun (02:11): the scene's ORIGINAL lamp - there
    # since Part 1 - is renamed "Sun" and its type changed
    # to SUN. Strength about 10 ("I keep this around 10").
    # Its Temperature (the Kelvin slider, a 4.5+ feature) is
    # warmed until it looks right - no number is stated
    # (UNSTATED: 4200 K, an early-morning warmth, picked -
    # and only set where the running Blender has the
    # slider). Rotation: early-morning light, from the
    # frame's right (UNSTATED angle).
    sun = next((o for o in scene.objects if o.type == "LIGHT"
                and o.name in ("Light", "Sun")), None)
    if sun is None:
        sun = next((o for o in scene.objects
                    if o.type == "LIGHT"), None)
    sun.name = "Sun"
    sun.data.type = "SUN"
    sun.data.energy = 10.0
    if hasattr(sun.data, "use_temperature"):
        sun.data.use_temperature = True
        sun.data.temperature = 4200.0
    sun_dir = Vector((-0.62, 0.18, -0.55)).normalized()
    sun.rotation_euler = sun_dir.to_track_quat(
        "-Z", "Y").to_euler()
    # The window trick (05:28): two blocker PLanes the sun
    # shines between, leaving only a sliver across the set.
    # Blocker 1: Shift+A -> Plane, moved to the light's
    # side, R -> X -> Ctrl-held -> exactly 90 degrees.
    # Blocker 2: Shift+D, R -> Z -> 90 degrees. Sizes and
    # positions are worked by eye until the sliver sits
    # right (UNSTATED - placed for this set, at his scale).
    blockers = []
    for i, (loc, rot, scl) in enumerate((
            ((0.56, -0.02, 0.40), (math.pi / 2, 0, 0), 0.30),
            ((0.58, 0.10, 0.52), (math.pi / 2, 0, math.pi / 2),
             0.24))):
        name = "Blocker" if i == 0 else "Blocker.001"
        if _scene_obj(context, name) is None:
            bpy.ops.mesh.primitive_plane_add(
                size=2, location=loc, rotation=rot)
            blk = context.object
            blk.name = name
            blk.scale = (scl, scl, scl)
            # A single-face plane is a shy shadow-caster in
            # Eevee; a whisper of thickness makes its shadow
            # reliable (the frame round's own scene fix).
            thick = blk.modifiers.new("Solidify", "SOLIDIFY")
            thick.thickness = 0.002
        blockers.append(_scene_obj(context, name))
    # Restaging inside the light (07:26): the mug goes
    # further back, in the table's plane (G -> Shift+Z in
    # the video; the set positions are by eye, UNSTATED).
    # It is also turned a little, so the handle reads from
    # the camera instead of hiding behind the body - a mug
    # whose handle cannot be seen reads as a plain cup.
    mug.location.x = 0.25
    mug.location.y = 0.155
    mug.rotation_euler.z = -0.6
    # Organisation (08:16): lights and blockers into a new
    # Collection named "Lighting" (M -> Move to Collection).
    coll = bpy.data.collections.get("Lighting")
    if coll is None:
        coll = bpy.data.collections.new("Lighting")
        scene.collection.children.link(coll)
    # The sky (08:49): the sun duplicated (Shift+D), named
    # "Sky", its type changed to POINT. The temperature tint
    # is cleared and a soft blue, slightly purple colour set
    # by eye (UNSTATED - (0.58, 0.62, 1.0) picked). Position
    # high, at window height (UNSTATED). Its Radius is
    # increased "by a lot" - the sky is a dome-sized light,
    # so its shadows must be very soft (UNSTATED amount -
    # 0.5 picked at his scale; the property Blender keeps
    # it in is the light's shadow soft size).
    if _scene_obj(context, "Sky") is None:
        sky = sun.copy()
        sky.data = sun.data.copy()
        scene.collection.objects.link(sky)
        sky.name = "Sky"
        sky.data.type = "POINT"
        sky.data.energy = 10.0
        if hasattr(sky.data, "use_temperature"):
            sky.data.use_temperature = False
        sky.data.color = (0.58, 0.62, 1.0)
        sky.data.shadow_soft_size = 0.5
        sky.location = (0.15, 0.25, 0.62)
        sky.rotation_euler = (0, 0, 0)
    sky = _scene_obj(context, "Sky")
    # The bounce (13:23): the Sky duplicated again, named
    # "Indoor Bounce", colour cleared to default white and
    # Power back to the default 10 (both stated - they are
    # the defaults he returns to). Positioned off to the
    # dark side, as if bounced off a cafe wall (UNSTATED).
    if _scene_obj(context, "Indoor Bounce") is None:
        bounce = sky.copy()
        bounce.data = sky.data.copy()
        scene.collection.objects.link(bounce)
        bounce.name = "Indoor Bounce"
        bounce.data.color = (1.0, 1.0, 1.0)
        bounce.data.energy = 10.0
        bounce.location = (-0.50, -0.18, 0.28)
    bounce = _scene_obj(context, "Indoor Bounce")
    for obj in [sun, sky, bounce] + blockers:
        if obj is None:
            continue
        for parent in list(obj.users_collection):
            parent.objects.unlink(obj)
        coll.objects.link(obj)
    # Camera (15:05): Lock Camera to View ON, pulled closer
    # (a tighter framing on the donut), then unchecked. The
    # amount is by eye from the Part 4 framing (UNSTATED) -
    # no lens change is made or stated, so the lens stays.
    cam = scene.camera
    if cam is not None:
        cam.location = (0.33, -0.74, 0.27)
        cam.rotation_euler = (
            Vector((0.045, 0.015, -0.01)) - cam.location
        ).to_track_quat("-Z", "Y").to_euler()
    # With the camera placed, the blockers are parked out
    # of its frame (see _park_out_of_frame) - in the video
    # they never appear; in the shipped build one stood in
    # the finale render as a pale slab.
    for blk in blockers:
        if blk is not None:
            _park_out_of_frame(context, blk)
    # The Eevee quality pass (15:36): shadow Steps to 16 -
    # the MAXIMUM ("the default value right here for steps
    # is wrong... it should be maxed out"). Samples, read
    # aloud as they stand: viewport 16, render 64.
    try:
        scene.eevee.shadow_step_count = 16
        scene.eevee.taa_samples = 16
        scene.eevee.taa_render_samples = 64
    except Exception:
        pass
    # Material retune under the new light (stated values):
    # Icing Subsurface Scale 0.03; Sprinkles 0.08 (he tries
    # 0.06 first, settles on 0.08).
    for obj, want in ((icing, 0.03),):
        for mat in obj.data.materials:
            if mat is None or not mat.use_nodes:
                continue
            bsdf = mat.node_tree.nodes.get("Principled BSDF")
            if bsdf is not None \
                    and "Subsurface Scale" in bsdf.inputs:
                bsdf.inputs["Subsurface Scale"].default_value = want
    smat = bpy.data.materials.get("Sprinkles")
    if smat is not None and smat.use_nodes:
        bsdf = smat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None and "Subsurface Scale" in bsdf.inputs:
            bsdf.inputs["Subsurface Scale"].default_value = 0.08
    # The Light Probe Volume (20:17): Shift+Right-click the
    # donut (cursor there), Shift+A -> Light Probe ->
    # Volume; scaled to encapsulate the set, its points
    # just above the table; Resolution 4 (stated - "I
    # probably only need about three. No, I'll go four");
    # Bake Light Cache. (The shuffle of individual points
    # - one on the plate's edge, one inside the donut - is
    # a viewport edit the bake here stands in for.)
    if not any(o.type == "LIGHT_PROBE" for o in scene.objects):
        context.scene.cursor.location = \
            dough.matrix_world.translation
        try:
            bpy.ops.object.lightprobe_add(
                type="VOLUME",
                location=dough.matrix_world.translation)
            probe = context.object
            probe.name = "Light Probe Volume"
            probe.scale = (0.45, 0.45, 0.17)
            probe.location.z -= 0.01
            probe.data.resolution_x = 4
            probe.data.resolution_y = 4
            probe.data.resolution_z = 4
            _set_active(context, probe)
            # The bake itself needs a live GPU context: on
            # a headless machine the attempt aborts the
            # whole process natively (no Python error to
            # catch), so the reference build only presses
            # Bake in an interactive session. The probe and
            # its stated resolution are the graded state.
            if not bpy.app.background:
                try:
                    bpy.ops.object.lightprobe_cache_bake()
                except Exception:
                    pass
        except Exception:
            pass
    # Depth of Field (22:30): camera DOF ON, Focus Object =
    # the Icing (picked in the Outliner when the probe
    # volume intercepts clicks). The F-Stop: no number is
    # stated (UNSTATED - Blender's own 2.8 stands).
    if cam is not None:
        cam.data.dof.use_dof = True
        cam.data.dof.focus_object = icing
    # Sun -> Shadow -> Jitter ON (24:36) - the benefit is in
    # the render; viewport jitter stays off (his warning).
    sun.data.use_shadow_jitter = True
    try:
        scene.eevee.use_shadow_jitter_viewport = False
    except Exception:
        pass
    # The comparison renders (25:25): Eevee and Cycles in
    # different slots, flipped between with J. (His Cycles
    # setup starts in Preferences -> System -> Render
    # Devices -> GPU - a machine setting the build cannot
    # make for anyone.) The build renders once, through the
    # tour's own engine, as the keepsake. The scene's saved
    # end state also carries his standing Look (set in
    # Part 7) - stored here too, so the finale file reads
    # right on either Blender spelling.
    _set_series_look(scene)
    scene.render.filepath = _home("blender_buddy_donut_final.png")
    bpy.ops.render.render(write_still=True)


# --- the checks: the scene itself is the only proof -----------

def _check_saved(context):
    # Shared with the job flows: the work exists as a file.
    return bool(bpy.data.filepath)


def _check_picture(context):
    # Shared with the job flows: a picture was rendered.
    return _render_proof(context)


def _walls_evidence(obj):
    """The cup has real walls: either the Solidify modifier
    is still live on it (Part 1's state), or its thickness
    has been baked into the cage (Part 2 applies it) - an
    inner wall of verts running at a second, smaller radius
    through the middle of the height. A one-layer tube that
    never met Solidify has neither."""
    if any(m.type == "SOLIDIFY" for m in obj.modifiers):
        return True
    prof = _radius_profile(obj)
    if prof is None:
        return False
    r_body, height, z_min, z_max, rs, zs = prof
    # A true second surface RUNS the cup's height: ask for
    # a run of inner-radius verts spanning a real stretch
    # of it - not a height window (a handle arcing above
    # the rim stretches the mesh's height and shifts every
    # window off the cup), and not a bare count (one ring
    # squeezed inward is a shaping choice, not a wall: its
    # inner-radius verts all sit at one height, span ~0).
    inner = [z for r, z in zip(rs, zs)
             if 0.55 * r_body < r < 0.99 * r_body]
    if len(inner) < 8:
        return False
    return max(inner) - min(inner) >= 0.35 * height


def _inset_evidence(obj):
    """The bottom face was inset: somewhere in the bottom
    band there is a FACE that is the inset's inner face -
    flat, low, and wholly inside the wall's radius, its
    centre well inside too. That is the shape an inset
    leaves and nothing else does:

    - the untouched cap is a single face whose verts sit
      ON the rim (radius = the wall's) - rejected;
    - a triangle-fan cap has a centre vert but its rim
      verts are on the wall too - rejected;
    - pressing I and dragging NOWHERE (thickness 0, the
      re-walk's exact state) leaves the inner face exactly
      on the rim - rejected: the old read counted the
      bottom plane's FACE COUNT instead, and the ring of
      quads the I key creates instantly satisfied it, so
      step 1 ticked at the bare keystroke;
    - the baked inner cap of a cup whose walls were
      applied with no inset ever made sits at the wall
      minus one thickness (about 0.96x) - rejected;
    - a real inset, dragged even a centimetre, puts its
      inner face at 0.85x the wall or less - accepted,
      and it survives the Part 2 apply in the cage."""
    prof = _radius_profile(obj)
    if prof is None:
        return False
    r_body, height, z_min, z_max, rs, zs = prof
    verts = obj.data.vertices
    for poly in obj.data.polygons:
        fz = [verts[i].co.z for i in poly.vertices]
        if max(fz) > z_min + 0.10 * height:
            continue
        if max(fz) - min(fz) > 0.02 * height:
            continue
        if max(rs[i] for i in poly.vertices) >= 0.90 * r_body:
            continue
        if math.hypot(poly.center.x, poly.center.y) \
                < 0.85 * r_body:
            return True
    return False


def _ring_levels(obj):
    """How many distinct heights the wall's rings sit at.
    His Part 1 cup has four: the base, the cut near the
    base, the cut near the rim, the rim itself. A cup with
    one loop cut - or none - is not the shape he leaves."""
    prof = _radius_profile(obj)
    if prof is None:
        return 0
    r_body, height, z_min, z_max, rs, zs = prof
    levels = {}
    for r, z in zip(rs, zs):
        if r > 0.88 * r_body:
            key = round((z - z_min) / (0.02 * height))
            levels[key] = levels.get(key, 0) + 1
    return sum(1 for n in levels.values() if n >= 6)


def _part1_cup_ok(cup):
    """Part 1's end state on ONE container, clause by
    clause - every clause is a thing his procedure does
    and the old check never asked for (gap 1.17: the tick
    fired with no Solidify, no Subsurf, no inset and one
    misplaced loop cut). The clauses are written to
    survive Part 2: the walls count live or baked, the
    Subsurf he never applies stays live, and the inset
    ring and cut rings persist in the cage he reshapes."""
    if not _walls_evidence(cup):
        return False
    if not any(m.type == "SUBSURF" for m in cup.modifiers):
        return False
    if not _inset_evidence(cup):
        return False
    return _ring_levels(cup) >= 4


_SAVED_PART1 = {"key": None, "ok": False}


def _grade_saved_part1(context):
    """Grade the scene exactly as it stands at a save -
    or at a load, where the live scene IS the file's
    content and nothing has been edited yet - and bind
    the verdict to the file as it lies on disk, keyed on
    (path, mtime, size). A save is a faithful write of
    the scene at that moment, so the verdict describes
    the stored file exactly, with no re-read: Blender
    refuses to library-load the file that is currently
    open ("Cannot load from the current blend file"), so
    the two moments the file's content is known for
    certain are the moments it is written and read."""
    ok = False
    try:
        if _find_dough(context) is not None:
            ok = any(_part1_cup_ok(cup)
                     for cup in _containers(context))
    except Exception:
        ok = False
    key = None
    path = bpy.data.filepath
    if path:
        try:
            st = os.stat(path)
            key = (path, st.st_mtime_ns, st.st_size)
        except OSError:
            key = None
    _SAVED_PART1.update(key=key, ok=ok)


@bpy.app.handlers.persistent
def _buddy_grade_save(*_args):
    try:
        _grade_saved_part1(bpy.context)
    except Exception:
        pass


@bpy.app.handlers.persistent
def _buddy_mark_render(*args):
    """A render just completed: record it on the scene that
    was rendered. The record has to live on the scene
    because the render itself leaves no trace the checks
    can read back: the Render Result's pixels are never
    saved into the file, and after a completed render that
    image reports size (0, 0) and has_data False on
    Blender 5.3 (and in every background render) - so a
    learner who pressed F12 exactly as the Part 4 card
    teaches, with no output path set (the card never sets
    one), proved nothing to the old _render_proof and
    step 4 could never tick (W4, GAP 4-8). render_complete
    fires on 4.2.5 and 5.3.0, in the GUI and headless -
    probed on both before this fix was written."""
    try:
        scene = args[0] if args else None
        if not isinstance(scene, bpy.types.Scene):
            scene = bpy.context.scene
        if scene is not None:
            scene.buddy_render_done = True
    except Exception:
        pass
    try:
        # The finale's own record (GAP 8-4): a render also
        # counts toward the last step when it completed
        # with the finale's rig standing complete around
        # it - the state the render is OF. An earlier
        # step's render, however it was saved, was made
        # with no rig standing and leaves this record
        # unset. The gate is the rig, not the tour's
        # pointer: on a Blender where an earlier step
        # waits for a newer version (Part 7's Scatter on
        # pre-5.0), the tour can never stand at the final
        # step, yet the finale's work and its render are
        # fully performable there - the record has to be
        # earnable in exactly that state.
        if scene is not None and bpy.context.scene is scene:
            if _final_picture_rig(bpy.context):
                scene.buddy_final_render_done = True
    except Exception:
        pass


def _saved_part1_ok(context):
    """The saved file holds the ring and the finished cup
    - the tick text's actual claim. The old step-1 check
    read only that A path existed (_check_saved), so a
    stale save of the unfinished probe scene ticked the
    step the moment the live mesh caught up (re-walk M1).
    The verdict comes from _grade_saved_part1, captured
    at the save itself (a save_post handler) and keyed to
    the file on disk: any later save re-grades, and a
    file whose key was never graded earns a verdict only
    when nothing is unsaved - the one state where the
    live scene provably equals the file's content."""
    path = bpy.data.filepath
    if not path:
        return False
    try:
        st = os.stat(path)
    except OSError:
        return False
    key = (path, st.st_mtime_ns, st.st_size)
    if _SAVED_PART1["key"] != key:
        if bpy.data.is_dirty:
            return False
        _grade_saved_part1(context)
        if _SAVED_PART1["key"] != key:
            return False
    return _SAVED_PART1["ok"]


def _check_first_cup(context):
    # Part 1's end state, as his procedure leaves it: the
    # file saved (his last move of the part), the donut ring
    # made, and the cup standing open beside it - with its
    # walls, its smoother, its inset and its two loop cuts,
    # the whole procedure the card teaches. (The old check
    # ticked on the save alone, then on shape alone; both
    # false passes are closed here. Round 2: the save is
    # graded too - the file's stored scene must hold the
    # finished cup, not just exist; see _saved_part1_ok.)
    if not _check_saved(context):
        return False
    if _find_dough(context) is None:
        return False
    if not any(_part1_cup_ok(cup)
               for cup in _containers(context)):
        return False
    return _saved_part1_ok(context)


def _check_mug_reference(context):
    # Part 2's end state: the cup ITSELF has become the mug
    # - a container with a handle grown from its own wall
    # AND JOINED BACK ON (the join is graded: boundary
    # edges may form only the mouth - gap 2.14), its
    # Solidify applied away (his pivotal 15:21 move, before
    # the handle grows) - and no plain, unworked cup is
    # still standing next to it (a second "mug" mesh built
    # beside an untouched cup is not his procedure and must
    # not tick). The reference photo itself is deleted in
    # Part 3, so its presence is not graded here - the
    # modelled mug is the proof.
    containers = _containers(context)
    if not containers:
        return False
    handled = [o for o in containers if _has_handle(o)]
    plain = [o for o in containers if not _has_handle(o)]
    if not handled or plain:
        return False
    mug = handled[0]
    if any(m.type == "SOLIDIFY" for m in mug.modifiers):
        return False
    return _join_closed(mug)


def _check_icing_hug(context):
    # Part 3's FINISHED state: his icing after the applies
    # and the sculpt pass - a closed solid shell (the
    # Solidify is IN the mesh, not on it), its rim pulled
    # into uneven drips, sitting exactly on the dough, with
    # NO live Shrinkwrap or Solidify left. The half-done
    # state - modifiers still live, no drips - must not
    # tick: that was the old check's certified stopping
    # point, and it is exactly where he tells you to keep
    # going.
    dough = _find_dough(context)
    if dough is None:
        return False
    icing = _find_icing(context, dough)
    if icing is None:
        return False
    if any(m.type in ("SHRINKWRAP", "SOLIDIFY")
           for m in icing.modifiers):
        return False
    # A closed solid: no edge belongs to just one face.
    edge_uses = {}
    for poly in icing.data.polygons:
        for a, b in poly.edge_keys:
            key = (a, b) if a < b else (b, a)
            edge_uses[key] = edge_uses.get(key, 0) + 1
    if any(n < 2 for n in edge_uses.values()):
        return False
    # Drips: the rim's low verts are uneven - some pulled
    # well down, most not.
    verts = icing.data.vertices
    zs = [v.co.z for v in verts]
    z_span = max(zs) - min(zs)
    if z_span <= 0:
        return False
    # A skin, not a second whole donut: the state this
    # step STARTS from - a plain duplicate of the dough -
    # reaches all the way around the dough's underside
    # (its lowest point IS the dough's lowest point,
    # fraction 0), but the shell his procedure leaves -
    # bottom half deleted, drips pulled down the OUTSIDE
    # - stays in the dough's top reaches: the reference
    # build's deep drips bottom out at 0.115 of the
    # dough's height (0.050 after Part 5's displacement
    # reshapes the dough under it), the walked icing at
    # 0.237. Without
    # this, the duplicate alone satisfied every clause
    # here - it is closed, carries no live modifiers,
    # and a whole tube's own z-spread reads as drips -
    # so step 3 could tick before any icing work existed
    # (re-walk M3's counter flips began at the
    # duplicate). Both rings share an origin in every
    # taught state, so local heights compare directly.
    dzs = [v.co.z for v in dough.data.vertices]
    if min(zs) < min(dzs) + 0.025 * (max(dzs) - min(dzs)):
        return False
    rim_low = [v.co.z for v in verts
               if math.hypot(v.co.x, v.co.y) > 0.11]
    if not rim_low:
        return False
    dipped = sum(1 for z in rim_low
                 if z < max(zs) - 0.72 * z_span)
    shallow = sum(1 for z in rim_low
                  if z > max(zs) - 0.45 * z_span)
    if dipped < 3 or shallow < 3:
        return False
    # It hugs: the icing's centre rides with the dough's.
    gap = (icing.matrix_world.translation
           - dough.matrix_world.translation).length
    return gap < 0.35 * DONUT_MINOR + 0.02


def _check_first_picture(context):
    # Part 4's end state: the donut resting on a plate on a
    # table (found by role - his are still named "Circle"
    # and "Plane" here), Eevee ray tracing ON (the switch
    # he calls a mistaken default), the food glow set to his
    # recipe on BOTH dough and icing (Weight 1, Radius
    # (1, 1, 1) - not any epsilon above zero), and a first
    # render made.
    dough = _find_dough(context)
    icing = _find_icing(context, dough)
    if dough is None or icing is None:
        return False
    if _find_plate(context, dough) is None:
        return False
    if _find_table(context, dough) is None:
        return False
    try:
        if not context.scene.eevee.use_raytracing:
            return False
    except Exception:
        pass
    if not _recipe_ok(icing) or not _recipe_ok(dough):
        return False
    return _render_proof(context)


def _pbr_pattern(mat):
    """(photo wired toward the Principled, a data map among
    the feeding pictures, a Normal Map node in the feed) for
    one material's node recipe - read per surface, never
    pooled across objects."""
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
    normal = any(n.type == "NORMAL_MAP" and n in feeding
                 for n in nt.nodes)
    return wired, noncolor, normal


def _surface_ok(obj, need_colour=True):
    """One surface wearing his Part 5 recipe: a photo wired
    in, at least one Non-Color data map feeding the
    Principled, and a Normal Map node in the feed. For the
    icing, whose colour picture he disconnects in his
    repair, need_colour is False."""
    if obj is None:
        return False
    for mat in obj.data.materials:
        wired, noncolor, normal = _pbr_pattern(mat)
        if not (wired and noncolor and normal):
            continue
        if not need_colour:
            return True
        bsdf = mat.node_tree.nodes.get("Principled BSDF")
        # The colour picture may reach Base Color through
        # the colour-surgery nodes he adds in Part 6 (RGB
        # Curves, then Hue/Saturation) - follow the chain
        # back instead of demanding a direct wire.
        stack = [link.from_node
                 for link in bsdf.inputs["Base Color"].links]
        seen = set()
        while stack:
            node = stack.pop()
            if node in seen:
                continue
            seen.add(node)
            if node.type == "TEX_IMAGE":
                return True
            for sock in node.inputs:
                stack.extend(link.from_node
                             for link in sock.links)
    return False


def _check_real_surfaces(context):
    # Part 5's end state, per surface (his recipe is
    # per-surface - the old check pooled its clauses across
    # objects, so one wired surface carried three bare
    # ones): table, plate and dough fully wired; the icing
    # wired with its colour picture disconnected and the
    # subsurface re-set by hand (his repair); the dough
    # carrying his displacement treatment.
    dough = _find_dough(context)
    icing = _find_icing(context, dough)
    plate = _find_plate(context, dough)
    table = _find_table(context, dough)
    if None in (dough, icing, plate, table):
        return False
    if not _surface_ok(table):
        return False
    if not _surface_ok(plate):
        return False
    if not _surface_ok(icing, need_colour=False):
        return False
    if not _recipe_ok(icing):
        return False
    if not _surface_ok(dough):
        return False
    # The dough's displacement: a Displacement node (or a
    # texture) feeding the Material Output's Displacement
    # socket, the material set to use it, and a Subdivision
    # Surface at level 3 to carry the detail (his stated
    # levels: viewport 3, render 3).
    disp_ok = False
    for mat in dough.data.materials:
        if mat is None or not mat.use_nodes \
                or mat.node_tree is None:
            continue
        if mat.displacement_method not in ("DISPLACEMENT", "BOTH"):
            continue
        for node in mat.node_tree.nodes:
            if node.type != "OUTPUT_MATERIAL":
                continue
            if any(link.from_node.type in ("DISPLACEMENT",
                                           "TEX_IMAGE")
                   for link in node.inputs["Displacement"].links):
                disp_ok = True
    if not disp_ok:
        return False
    return any(m.type == "SUBSURF" and m.levels >= 3
               and m.render_levels >= 3
               for m in dough.modifiers)


def _check_unwrap_mug(context):
    # Part 6's end state: the mug wearing a real set of
    # seams (ten or more seam edges - the card teaches his
    # six-cut layout, and the count is what is graded here,
    # not the layout's placement; W4 GAP 6-6), a UV map,
    # and the foam sitting inside its rim with a material
    # of its own - the foam found by where it sits, under
    # his name for it ("Foam") or by its place in the mug.
    mug = _find_mug(context)
    if mug is None:
        return False
    seams = sum(1 for e in mug.data.edges if e.use_seam)
    if seams < 10:
        return False
    if not mug.data.uv_layers:
        return False
    foam = _find_foam(context, mug)
    if foam is None:
        return False
    if not foam.data.materials or foam.data.materials[0] is None:
        return False
    # His foam is built from the rim and inset - it has a
    # raised edge and a lowered middle, never one flat
    # plane. A plain disc dropped in must not tick.
    fzs = [v.co.z for v in foam.data.vertices]
    return max(fzs) - min(fzs) > 0.002


def _check_scatter(context):
    # Part 7's end state, read off the modifier itself (by
    # input NAME - the check verifies the wiring, the way
    # the panel would show it): Scatter on Surface on the
    # icing, instancing from the Sprinkles collection with
    # Pick Instance on, Density Method = Density at his
    # stated 900, Poisson Disk distribution, and the painted
    # vertex group wired as the Distribution Mask ATTRIBUTE
    # - with real paint in it (full weight somewhere, soft
    # somewhere, none somewhere). The variants in that
    # collection share ONE material whose colours come from
    # Object Info's Random through a CONSTANT Color Ramp -
    # his system, not a fixed colour per shape.
    icing = _scene_obj(context, "Icing")
    if icing is None:
        dough = _find_dough(context)
        icing = _find_icing(context, dough)
    if icing is None:
        return False
    mod = next((m for m in icing.modifiers
                if m.type == "NODES" and m.node_group is not None
                and "Scatter on Surface" in m.node_group.name),
               None)
    if mod is None:
        return False
    inputs = _mod_inputs(mod)
    if not inputs:
        return False

    def val(name):
        prop = inputs.get(name)
        return getattr(prop, "value", None) if prop else None

    if val("Instance Type") != "Collection":
        return False
    coll = val("Collection")
    if coll is None:
        return False
    variants = [o for o in coll.objects if o.type == "MESH"]
    if len(variants) < 2:
        return False
    if val("Pick Instance") is not True:
        return False
    if val("Density Method") != "Density":
        return False
    density = val("Density")
    if density is None or abs(float(density) - 900.0) > 1.0:
        return False
    if val("Distribution Method") != "Poisson Disk":
        return False
    mask = inputs.get("Distribution Mask")
    if mask is None or getattr(mask, "type", None) != "ATTRIBUTE":
        return False
    group_name = getattr(mask, "attribute_name", "")
    vg = icing.vertex_groups.get(group_name)
    if vg is None:
        return False
    weights = []
    for v in icing.data.vertices:
        try:
            weights.append(vg.weight(v.index))
        except RuntimeError:
            weights.append(0.0)
    if not weights or max(weights) < 0.9 or min(weights) > 0.05:
        return False
    if not any(0.05 < w < 0.95 for w in weights):
        return False
    # One shared material, Object Info Random -> Color Ramp
    # (Constant) -> Base Color.
    mats = []
    for v in variants:
        if v.data.materials and v.data.materials[0] is not None:
            mats.append(v.data.materials[0])
    if not mats or any(m is not mats[0] for m in mats):
        return False
    nt = mats[0].node_tree
    if nt is None:
        return False
    ramp = next((n for n in nt.nodes if n.type == "VALTORGB"),
                None)
    if ramp is None or ramp.color_ramp.interpolation != "CONSTANT":
        return False
    info = next((n for n in nt.nodes if n.type == "OBJECT_INFO"),
                None)
    if info is None:
        return False
    return any(link.from_node == ramp
               for bsdf in nt.nodes if bsdf.type == "BSDF_PRINCIPLED"
               for link in bsdf.inputs["Base Color"].links)


def _check_final_picture(context):
    # Part 8's end state: his rig standing complete (see
    # _final_picture_rig) AND a fresh render - the
    # finale's own, recorded with the rig standing (see
    # _final_render_proof), not any render from earlier
    # in the tour.
    return _final_picture_rig(context) and \
        _final_render_proof(context)


def _final_picture_rig(context):
    # Part 8's rig, structurally: the
    # original lamp become a SUN at about 10 (his stated
    # strength), two blocker planes standing in its light
    # (single-face meshes, not horizontal - the table is a
    # plane too, and it lies flat), a blue POINT "sky", a
    # white POINT "bounce" at the default 10 he returns to,
    # a Light Probe Volume at resolution 4 (stated), shadow
    # Steps at the stated maximum 16, the camera's depth of
    # field focused on the icing, the parenting he does
    # first (icing on donut, donut on plate, foam on mug,
    # plate and mug on the table), the SSS scales he retunes
    # (icing 0.03, sprinkles 0.08).
    dough = _find_dough(context)
    icing = _find_icing(context, dough)
    mug = _find_mug(context)
    plate = _find_plate(context, dough)
    table = _find_table(context, dough)
    foam = _find_foam(context, mug)
    if None in (dough, icing, mug, plate, table, foam):
        return False
    suns = [o for o in context.scene.objects
            if o.type == "LIGHT" and o.data.type == "SUN"]
    if not any(8.0 <= s.data.energy <= 12.0 for s in suns):
        return False
    points = [o for o in context.scene.objects
              if o.type == "LIGHT" and o.data.type == "POINT"]

    def is_blue(light):
        c = light.data.color
        return c[2] > c[0] and c[2] > c[1] + 0.02

    def is_white(light):
        c = light.data.color
        return max(c) - min(c) < 0.05

    if not any(is_blue(p) for p in points):
        return False
    if not any(is_white(p) and 7.0 <= p.data.energy <= 13.0
               for p in points):
        return False
    blockers = 0
    for obj in context.scene.objects:
        if obj.type != "MESH" or len(obj.data.polygons) != 1:
            continue
        if obj is table:
            continue
        normal = obj.data.polygons[0].normal
        world_n = (obj.matrix_world.to_3x3() @ normal)
        if abs(world_n.normalized().z) < 0.5:
            blockers += 1
    if blockers < 2:
        return False
    probes = [o for o in context.scene.objects
              if o.type == "LIGHT_PROBE"
              and getattr(o.data, "type", "") == "VOLUME"]
    if not probes:
        return False
    if getattr(probes[0].data, "resolution_x", None) != 4:
        return False
    try:
        if context.scene.eevee.shadow_step_count != 16:
            return False
    except Exception:
        pass
    if icing.parent is not dough or dough.parent is not plate:
        return False
    if foam.parent is not mug:
        return False
    if plate.parent is not table or mug.parent is not table:
        return False
    recipe = _sss_recipe(icing)
    if recipe is None or recipe[2] is None \
            or not (0.02 <= recipe[2] <= 0.045):
        return False
    smat = bpy.data.materials.get("Sprinkles")
    if smat is not None and smat.use_nodes:
        bsdf = smat.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None and "Subsurface Scale" in bsdf.inputs:
            if not (0.06 <= float(bsdf.inputs["Subsurface Scale"]
                                  .default_value) <= 0.10):
                return False
    cam = context.scene.camera
    if cam is None or not cam.data.dof.use_dof:
        return False
    if cam.data.dof.focus_object is not icing:
        return False
    return True


# --- the eight steps ------------------------------------------------

TOUR_STEPS = [
    {
        "id": "first_cup",
        "package": "donut",
        "title": "Part 1 - Your first donut and cup",
        "how": "A plain ring and a plain cup. Everything in this series is built from these.",
        "video": {"url": "https://www.youtube.com/watch?v=-tbSCMbJA6o", "label": "Watch Part 1 on YouTube"},
        "skill": "First shapes: adding a ring and a tube, the little Add panel that vanishes (and F9, the key that brings it back), opening a cup, loop cuts, inset, and your first two modifiers - Solidify and Subdivision Surface",
        "missing": "The saved file holding the ring and the finished cup: top opened, walls from the Solidify effect, the Subdivision smoother still on it, the bottom inset, and the two loop cuts in place. Saving alone does not tick it - the cup has to be built.",
        "tools": ["add_ring", "add_tube", "loop_cut", "inset_face", "give_thickness", "make_smoother", "save_work"],
        "teach": [
            "Part 1 of the Donut Tutorial (2026) builds the two shapes everything else stands on. Open Blender and press play - Buddy keeps your place while you work. First, moving around, because he teaches it before anything else: hold the middle mouse button and drag to orbit around the scene; hold Shift and the middle button to pan sideways; scroll to zoom. Press Numpad . (the dot on the number pad) and the view jumps to the picked thing - he uses it constantly. Mouse without a middle button: Preferences, Input, tick Emulate 3-Button Mouse, and Alt+left-drag orbits instead.",
            "DELETE THE CUBE. Click the cube so it is outlined orange, then press X. X is Blender's delete key - a small menu asks you to confirm, so click Delete. Only the cube goes: the Camera and the Light that start in the scene STAY - the series uses both later (the camera takes Part 4's first picture; the lamp becomes Part 8's sun). The cube is just the starter block Blender opens with, and the donut starts cleaner without it. Wrong click somewhere? Ctrl+Z undoes your last move - it works everywhere in Blender, and it will rescue you all series long.",
            "MAKE THE DOUGH RING. Shift+A opens the Add menu (Shift+A is 'add something'), then Mesh, then Torus. That ring is your dough. Before you click anything else, find the small 'Add Torus' panel at the bottom left of the screen - it holds this shape's settings, and it VANISHES at your next click. If it goes, press F9: F9 brings back the last tool's settings panel. In that panel: Major Segments 48 and Minor Segments 18 (segments are the ring's slices - more slices, smoother ring). Major Radius: type 0.1 m - his donut is built at real scale, 10 cm, not the giant 1-metre default. Minor Radius: drag to about 0.057 m, holding Shift while you drag for fine steps - that is the dough tube's thickness. Type the sizes here, in this panel: there is no shrink step coming later, so what you type is what you get.",
            "MAKE IT LOOK LIKE DOUGH. Right-click the ring and choose Shade Smooth: the ring's flat facets melt into one smooth surface. That is the whole trick - almost every shape in this series gets smoothed this way.",
            "MAKE THE CUP. Shift+A, Mesh, Cylinder - and in its vanishing panel (F9 brings it back): Radius 0.13 m. Vertices: 14. That low number is on purpose: a rounding effect coming later in THIS part - Subdivision Surface - will smooth the 14 sides into a curve, and fewer corners now means a cleaner curve then. Depth: he never types it - drag until the cylinder stands about as tall as a mug beside the donut.",
            "MOVE THE CUP OUT OF THE WAY. Press G (G is grab - it moves the picked thing, following your mouse) and slide the cup behind the donut, then click to place it. His two shapes stand side by side from here, not on top of each other. (Pressing X, Y or Z right after G locks the move to that one direction.)",
            "OPEN THE TOP. Press Tab. Tab switches between Object Mode - moving whole things - and Edit Mode, where you change a shape's own faces and points; you need Edit Mode now. Press 3 for Face Select (the three icons at the top left of the 3D window: 1 picks points, 2 picks edges, 3 picks faces). Click the cylinder's top face so it highlights. Press X - the delete key again - and this time choose Faces from the menu. Why Faces: it removes only that top surface and leaves the rim ring standing; choosing Vertices would take the rim's corner points with it and tear the top of the wall away. The cup is open at the top now, like a real cup.",
            "GIVE THE CUP ITS WALLS. Press Tab back to Object Mode first - Tab flips between the two modes, and you have been in Edit Mode since opening the top. The next two moves are effects stacked onto the whole object at once, and Object Mode is the mode for whole-object moves; the loop cuts after them will send you back into Edit Mode. With the cup picked, click the wrench tab on the right - the Modifiers tab. A modifier is a live effect stacked on a shape: it changes how the shape looks and behaves while the shape underneath stays simple, and you can change or remove it at any time. Click Add Modifier, Generate, Solidify. Solidify turns the one-layer tube into a tube with real thickness - an inside and an outside. Drag its Thickness slider by eye until the wall reads like a real cup's wall; he never states a number, so match the video. NOW CHECK IT LANDED: the list in the Modifiers tab should show 'Solidify'. If the list is empty, the effect is not on the cup - click the cup once so it is outlined orange, then add it again. (This step's own Thickness tool in Buddy's tools above does the same add and tells you when it lands.)",
            "MAKE IT CURVY. Add Modifier again: Generate, Subdivision Surface. This is the great smoother of Blender - it chops every face into smaller faces and rounds the result, and it is what turns the 14-sided tube into a believable cup. He raises its Levels Viewport 1, then 2, then 3 on camera just to show the rounding doubling each time; where it should rest he never says. Buddy's suggestion: leave it at 2 - smooth to look at, light on your computer.",
            "TWO LOOP CUTS. Press Tab back into Edit Mode. A loop cut is a new ring of edges around a shape, and its job here is control: the smoother wants to round EVERYTHING, and a ring near an edge holds that edge crisp. Press Ctrl+R (Ctrl+R is loop cut), hover over the cup's side until a yellow ring appears around it, click once, then slide the ring up close to the rim and click again to set it. That is ONE ring. Now a second, separate Ctrl+R, slid down near the base. One at a time, far apart - the rim ring guards the lip, the base ring guards the foot. (The mouse wheel during Ctrl+R adds extra rings, but they slide together as a bunch - that is not this move.)",
            "SHAPE THE BOTTOM. Still in Edit Mode, still in Face Select (3): orbit underneath the cup (middle-drag) and click its bottom face. Press I - I is Inset Faces. A smaller face appears inside the bottom, ringed by new faces; drag until that inner face is about the size of his in the video. This inset is the base detail - it is what makes the underside read as a made object instead of a flat disc once the smoother rounds it. (It does not thicken anything - the walls came from Solidify. This one shapes the bottom.)",
            "ONE REFINEMENT HE MAKES. Near the end he clicks the Solidify in the Modifiers list and drags Thickness once more - chunkier, then thinner - settling where the wall looks right against the now-smoothed cup. The effects being live is the whole point: nothing is final until you say so.",
            "SAVE. Shift+Ctrl+S is Save As. Give the file a name YOU choose - he leaves the name to you (his own ends in a number he bumps up as he works) - and save it somewhere you will find it. Guru ends every part by saving; so do you. Buddy ticks this step when the saved file holds the ring and the finished cup: open top, walls from Solidify, the Subdivision smoother still on it, its bottom inset, and the two loop cuts in place. One thing before you save: you are still in Edit Mode - the loop cuts and the inset all happened there - so press Tab back to Object Mode first, then save. Tab swaps between the two modes, and your last Edit Mode changes only settle into the shape itself as you Tab out of it; a save taken from inside Edit Mode can leave Buddy reading the cup as it was before those changes, so the step looks stuck even though your work is done.",
        ],
        "check": _check_first_cup,
        "run": _tour_step_first_cup,
    },
    {
        "id": "mug_reference",
        "package": "donut",
        "title": "Part 2 - The cup becomes a mug",
        "how": "The reference photo moves in, the cup is reshaped against it, and a handle grows out of its own side.",
        "video": {"url": "https://www.youtube.com/watch?v=K1UyEdmSttQ", "label": "Watch Part 2 on YouTube"},
        "skill": "Working from a photo: reshaping a profile by eye with Alt+click loop selection and GG slides, extruding a handle out of the cup's own wall, and joining it back with hand-built faces",
        "missing": "The cup itself becomes a mug - a handle grown from its own wall and joined back on, with no open holes left at the joint - its walls made permanent, and no plain, unworked cup still standing beside it.",
        "tools": ["pull_face", "look_smooth", "save_work"],
        "teach": [
            "Part 2 turns your plain cup into a coffee mug. Everything in this part happens to the cup you already have - the mug IS the cup, reshaped. Nothing new is modelled beside it.",
            "BRING IN THE PHOTO. Get a photo of a real mug to copy from - his is a handmade mug, and the link to it sits in the description under Part 2's video on YouTube (the series page links it too). Any clear, side-on photo of a handled mug works - the photo is a shape to copy, not an ingredient. You are still in Edit Mode from Part 1's inset, so press Tab back to Object Mode first: in Edit Mode the Shift+A menu offers only mesh shapes - the Image entry this move needs lives in the Object Mode Add menu, and hunting for it in the wrong menu reads exactly like it does not exist. Add it his way: Shift+A, then Image, then Reference; pick the file, and a flat picture stands in your scene. Pictures arrive lying at whatever angle the file had, so first press Alt+R: R is rotate, and Alt+R clears a thing's rotation back to zero - which is why the next turn lands exact. Then press R, then X, then type 90 and press Enter: R starts a rotate, X locks it to the tipping axis, and 90 stands the picture upright.",
            "FIT THE PHOTO TO THE CUP. Press Numpad 1 for the Front view, and if the view is in Perspective, press Numpad 5 to switch it to Orthographic - in a flat front view, sizes compare honestly, nothing shrinking with distance. Ignore the picture frame's own size: the frame (Blender calls it an Empty) arrives 5 metres tall, and only the mug INSIDE the picture matters. Press S (S is scale) and shrink the picture until the pictured mug stands the same height as your cup. Then click your cup, press G, and stand it beside the photo with the rims level - this comparison is what you shape against.",
            "RESHAPE THE CUP - THE METHOD (from about 5:00 in the video). Tab into Edit Mode. Press 2 for Edge Select (the middle of the three icons at the top left: 1 points, 2 edges, 3 faces). Alt+click a ring of edges: Alt+click selects a whole LOOP at once - an entire ring in one click - which is why he never picks edges one by one. Alt+click the top ring and press S (scale) to pull it in slightly, toward the photo's lip. Alt+click the ring below it and S it about halfway toward the first - his words are 'about halfway', because this is shaping by eye, not measuring. Now press G twice - GG - on the middle ring: that is edge slide, walking a ring up or down the wall without disturbing the shape around it. Slide it up to about 20% of the mug's height - the photo's widest point, its belly - and S it outward to meet the photo's curve. Keep going in the same rhythm - Alt+click a ring, GG to slide it, S to size it - until your cup's outline sits on the photo's outline.",
            "THE BOTTOM AND THE FOOT. Press 3 for Face Select and click the bottom face; S it in a little - the base is narrower than the belly. Then press E and click straight away: E is extrude, pulling new shape out of the picked face, and this small drop becomes the mug's foot - the lip a real mug stands on. Guard it with two rings: Ctrl+R (loop cut) right at the very bottom, then Ctrl+R again just above it - rings near an edge hold that edge crisp while the smoother rounds everything else.",
            "MAKE THE WALLS PERMANENT. Tab back to Object Mode first - the reshaping left you in Edit Mode, and Apply only works in Object Mode: in Edit Mode the Apply entry sits greyed out, and its own tooltip tells you this operation is not allowed from Edit mode. In Object Mode, find the Solidify effect in the Modifiers tab (the wrench) and click its dropdown arrow, then Apply (about 15:21). Applying bakes a live effect into the shape itself - the walls become real mesh. This has to happen BEFORE the handle grows: leave Solidify live and it would thicken the handle too. The Subdivision smoother stays live - he never applies that one. IF SOLIDIFY IS NOT IN THE LIST: Part 1's walls never landed on your cup. Add it now - Add Modifier, Generate, Solidify - give it a sensible thickness, and Apply it here. The mug ends up the same either way.",
            "GROW THE HANDLE OUT OF THE CUP (about 16:44). The handle is not a new object - it is the cup's own wall, pulled out and walked around. Tab into Edit Mode, then press 3 for Face Select - you are in Object Mode (the walls were just made permanent there), and Face Select only exists in Edit Mode. Choose ONE face on the cup's side, dead centre at the height where a handle starts. Pick it from the Right view (Numpad 3): that view looks straight at the wall the handle leaves from, so the face sitting squarely in the middle of that wall is unmistakable. Then check the choice in the Top view (Numpad 7): it should sit squarely on the side the handle leaves from. Then work in the Front view (Numpad 1). Dead centre matters more than it looks: a face even ONE segment around the curve starts the handle at an angle, and every move after this one travels in the screen's flat plane, so each new segment lands a little further sideways than the last - by the end, the handle's end passes BESIDE the wall instead of meeting it, and no amount of pulling makes it land. If the end is not coming home, do not wrestle a wrong start: Ctrl+Z back to before the first E and pick the dead-centre face. Press E to extrude that face outward; press G (grab) and move the new segment up a little; press R (rotate) and turn it to follow the mug's slant. Add a ring near the handle's base - Ctrl+R - and GG-slide its top edge down a little to thin the handle where it leaves the cup: for that cut, hover the mouse over the HANDLE itself, over one of its long edges, so the yellow preview ring circles the handle - the same hover move as the cup's own rings in Part 1 - and do it from the Right view (Numpad 3) or a three-quarter orbit, not the flat Front view: from the front, the handle's long edges squash flat against the cup on screen and the preview ring has nothing clear to land on. The cut follows whatever your mouse is over, so if the preview ring wraps the cup instead, slide the mouse onto the handle before you click. Then keep walking: E to pull out the next segment, G to place it, R to turn it, over and down in small steps, until the end of the handle comes back to the cup's wall lower down - the loop in the photo. (His speed trick once the rhythm feels slow: Ctrl+right-click drops the next segment where your cursor is.)",
            "JOIN IT BACK ON - HIS WAY (about 21:37 to 23:31). Ctrl+R a ring around the cup's body exactly at the height where the handle's end will land - hover over the cup's WALL so the yellow preview ring circles the cup, not the handle; the cut follows your mouse - and pull the handle's end face out until it touches the body. Judge that last approach from the Right view (Numpad 3) - looking straight at the wall the handle lands on - or orbit to a three-quarter view (hold the middle mouse button down and drag): in the flat Front view you have been working in, the end and the wall overlap on screen, and touching and hovering look exactly the same. Now build the joint BY HAND, the way he does it, and it is built POINT TO POINT: press 1 for Vertex Select - points, the first of the three icons at the top left. That switch is the whole move: in Face Select a click takes a whole face, never one corner point, so the sewing below cannot even start there - and F pressed on a crowd like that makes one big many-sided face (an n-gon) sprawled across the joint, not a sewn side. Before you pick a single point, CHANGE WHAT YOU ARE LOOKING AT: in the Front view, the end face's four corner points stack into just two spots on screen - the front pair hides the back pair - so two of the four corners cannot be clicked at all. Orbit to a three-quarter view (middle mouse button held down, drag) or press Numpad 3 for the Right view, looking at the wall from the handle's side, until all four corners of the end stand apart on screen. Then press Alt+Z: X-Ray. X-Ray makes the mesh see-through FOR SELECTING, so the far corners - the ones hidden behind the end face from where you sit - can be clicked through the surface. Part 3's icing step leans on this same X-Ray trick to catch the far side of the ring; here it is what makes the back two corners pickable at all. Now look at the BODY side of the joint before you pick a single point: the ring you just cut runs straight through the patch of body the end covers, so that patch is TWO body faces now - one above the ring, one below it - and the outline of the patch has SIX points, not four: a top pair (the top corners of the upper face), a middle pair (the ring's own two points, where the two faces meet), and a bottom pair (the bottom corners of the lower face). The sew joins the handle end's four corners to those six points, in SIX new faces. THE TOP FIRST: click the end's two top corner points, then Shift+click the body's top pair - FOUR points picked in all - and press F: F makes a face from the picked points, and that face sews the top shut. Why four: two points can only make an edge, a line with no surface on it, and a face is what closes the gap. THE BOTTOM NEXT: the end's two bottom corner points, then Shift+click the body's bottom pair, and F again - the same four-point move at the patch's other end. EACH SIDE then takes TWO faces, and the ring's point on that side is why: it sits halfway down the side of the patch, and one straight face from the end's top corner to its bottom corner would jump clean past it, leaving that point joined to nothing with a slit of open hole beside it. The side's first face: click the end's top corner point on that side, then Shift+click the body's top point on that side, the ring's point on that side, and the end's bottom corner point on that side - four points - and press F. What is still open on that side is now a three-cornered gap, so the side's second face takes only THREE points: the end's bottom corner point, the ring's point once more, and the body's bottom point on that side - press F, and a triangle closes it; a triangle is a proper face, not a shortcut. Build the same two faces on the other side, and the joint is sewn the whole way round - six new faces, and every point of the patch joined to something. Shift+click is the picker throughout this step: it adds ONE thing to your selection. Never Ctrl+click here: Ctrl+click selects the whole shortest PATH between the two clicked points - it would grab a swath of handle and wall faces, and the delete below would destroy them. Last, press 3 for Face Select again, and delete the THREE faces now hidden INSIDE the joint - the handle's end face and the two body faces the end covers, the one above the JOIN ring and the one below it: they sit inside the sewn joint where you cannot see them, which is the other thing X-Ray is for - still see-through, click the end face through the surface, Shift+click both body faces it covers, X, then Faces. Press Alt+Z once more to turn X-Ray off now the joint is done. Faces, because the rim edges around them must stay - your six new faces hang from them. Both body faces, never just one: leave either behind and it keeps an edge along the ring with no face on its other side - a slit of open hole hidden inside the finished joint, and the step will not pass it. (The video also shows a faster alternative at the end: with the end pulled to the body, press 3 for Face Select, delete both of those inside faces FIRST (click one, Shift+click the other, X, Faces), then press 2 for Edge Select and pick the two open rims edge by edge with Shift+clicks - a one-face hole has no ring to click; its four edges are picked by hand - then Edge, Bridge Edge Loops, and Blender sews them. It only works when both rims have the SAME number of edges, which is why the hand-built join is his main method.)",
            "TIGHTEN AND SMOOTH. Where the handle meets the cup, the smoother can pinch: add a Ctrl+R ring near each attachment and GG-slide edges until the join reads clean - small rings near a join hold its shape the way the rim rings held the cup's lip. Then the shading: still in Edit Mode, press A (A is select all), then Shift+N - that recalculates which way every face points, Blender's fix for dark, inside-out-looking patches after a join. If black patches remain, press A then Shift+N once more NOW, while you are still in Edit Mode - both keys speak to the mesh being edited, so after the next move they do nothing at all. Then Tab back to Object Mode, right-click the mug, Shade Smooth.",
            "SAVE (Ctrl+S). Buddy ticks this step when the cup itself has become the mug: a handle grown from its own wall AND joined back on - a handle ending in open holes does not tick, and neither does a separate mug modelled beside an untouched cup. (His homework, if you want it: model a saucer with these same moves - he shows his at the start of Part 4.)",
        ],
        "check": _check_mug_reference,
        "run": _tour_step_mug_reference,
    },
    {
        "id": "icing_hug",
        "package": "donut",
        "title": "Part 3 - Icing that hugs the donut",
        "how": "A copy of the dough becomes the icing: shrink-wrapped on, thickened, dripped, applied, and sculpted.",
        "video": {"url": "https://www.youtube.com/watch?v=9OA2asQdi_U", "label": "Watch Part 3 on YouTube"},
        "skill": "Copying and modifier order: duplicate-in-place, the stack in his order - Shrinkwrap, Solidify, Subdivision Surface - applying modifiers top to bottom, and a first sculpting pass",
        "missing": "A finished icing shell sitting on the dough: drips at its rim, all three modifiers applied away, and the file saved. Live Shrinkwrap or Solidify still showing means the part is half done.",
        "tools": ["copy_it", "wrap_onto", "give_thickness", "make_smoother", "start_sculpting", "save_work"],
        "teach": [
            "Part 3 puts the icing on. Guru does not model it from nothing - he copies the dough and turns the copy into icing, which is why it fits perfectly.",
            "TIDY FIRST. In the Outliner (the list of things, top right) double-click the cup's name and rename it Mug; rename the ring Donut (F2 does the same on a picked thing). Click the reference photo and press X, Delete - its job is done. Then click the Mug, press G, then X, and slide it sideways, well out of the shot: the icing work needs the donut alone in frame. (G then X is move, locked to the sideways direction - the mug keeps its height and depth while it slides.)",
            "COPY THE DOUGH. Click the Donut and press Shift+D - duplicate: an exact copy appears, following your mouse. Press Esc straight away, so the copy stays exactly where the original is instead of sliding away. Press F2 and name the copy Icing. You now have two identical rings occupying the same space; the copy becomes the icing.",
            "TAKE THE BOTTOM OFF. Press Numpad 1 (Front view) and Tab into Edit Mode on the Icing. Press 1 for Vertex Select - points now (1 is the first of the three icons at the top left). Press Alt+Z: X-Ray. X-Ray makes the mesh see-through FOR SELECTING, so a drag catches the far side too - without it, a drag-select catches only the points you can see, and the far side's bottom survives as a thin fin sticking through your finished icing. Drag a box over the whole bottom half of the ring - both sides, thanks to X-Ray. Press X, then Faces. Why Faces and not Vertices: deleting vertices would eat the middle ring of points too - the ring the icing's edge hangs from - while Faces removes only the bottom surfaces and leaves every point standing. Press Alt+Z again to switch X-Ray off. What remains is a curved shell - the top skin of the donut.",
            "GIVE IT A SKIN - Solidify first, before any shaping (from about 11:29). You are still in Edit Mode from taking the bottom off, and you can stay right there: the Modifiers tab works the same in either mode, and the wavy edge after this needs Edit Mode anyway. Click the Icing, Modifiers tab (the wrench), Add Modifier, Generate, Solidify. Set Offset to 1: Offset chooses which way the new thickness grows, and at 1 it grows OUTWARD, away from the dough - at the default it grows inward and swallows the surface the icing has to show, the classic 'something's broken' of this part. Thickness itself: drag by eye; he never states a number in this part. Then, on the Solidify's header, click the monitor icon - its viewport display - OFF while you edit: with it on, the thickened skin hides the very points you are about to pull. You are only hiding the preview; the effect still lands when it is applied.",
            "THE WAVY EDGE. This is point work, so you need Edit Mode: you are still in it from taking the bottom off and adding the skin - stay there. (If you Tabbed out somewhere along the way, press Tab to come back - the rim points below can only be picked in Edit Mode.) Turn Proportional Editing ON (the target-like button in the top bar of the 3D window, or press O): when you move one point, its neighbours follow with a soft falloff - which is what makes waves instead of spikes. Click a point on the shell's rim, press G, then Z - G moves, Z locks the move straight up and down - and pull the point down a little. The white circle around your cursor is the falloff's reach: scroll the mouse wheel (or press Page Up / Page Down) to grow or shrink it - a bigger circle makes a wider, lazier wave. Shrink the circle right down FIRST, until it is only a little wider than the one wave you are about to pull: it can take nine or ten Page Down presses to get there from the size the circle opens with, so do not count presses - the endpoint is the instruction, and the circle on screen tells you when you are there. At the size it opens with, the circle can cover the whole shell, and a single pull then drags everything at once as one lump instead of a wave. Work around the rim, varying the pulls - he works by eye (about 8:24 to 10:45), and the unevenness is the look.",
            "THE RUNOFF DRIPS. Click TWO neighbouring rim points - click one, then Shift+click the next (Shift+click adds one point to the selection). Press E, then Z: E pulls new surface out of the picked points, Z keeps it dropping straight down. Pull down into a drip and click to set it. Repeat all around - little dribbles everywhere, varying the length and shape as you go. Machine-even drips read as fake; the variety is the realism.",
            "SMOOTH IT, THEN GLUE IT ON. Add Modifier, Generate, Subdivision Surface - the smoother rounds the drip blocks into droplets. Then Add Modifier, Deform, Shrinkwrap: Shrinkwrap glues a shape onto another one - set its Target to Donut (click the Target box and pick Donut from the list). NOW ARRANGE THE STACK: drag Shrinkwrap by its grip strip to the TOP, so the list reads top to bottom: Shrinkwrap, Solidify, Subdivision Surface. Order is not decoration - each effect feeds the next. Wrap first and the thickness grows a clean shell on the wrapped skin; shrinkwrap after thickening and the icing fights the dough for the same space - that flickering where two surfaces coincide.",
            "FINISH THE STACK. On the Subdivision Surface, set Levels Viewport to 2 - the preview smoothness he works at. On the Solidify, find Edge Data and raise the Crease values - Blender lists the crease as three numbers, Inner, Outer and Rim; raise all three together. The crease tells the smoother to hold the icing's edge tight against the dough instead of ballooning off it. How far is by eye - he never states a value; raise it until the edge sits ON the dough. Then, with proportional editing still on, pull a few rim points back UP a touch (G, then Z, as before) - spots where the dough peeks through make the icing read as poured, not printed.",
            "APPLY ALL THREE - about 13:30, and this is the step everyone skips. You have to be in Object Mode for this: if the wavy edge and the drips left you in Edit Mode, press Tab first - in Edit Mode every Apply sits greyed out, the same trap as Part 2's walls. In Object Mode, starting from the TOP of the stack, click each modifier's dropdown and Apply, one at a time, top to bottom: Shrinkwrap, then Solidify, then Subdivision Surface. (His shortcut: Ctrl+A applies the top one.) Applying bakes each effect into the mesh. When you are done the icing has NO live modifiers left, and it no longer needs them - it IS the shape now. Buddy's tick checks exactly this: live, un-applied modifiers mean the part is half done.",
            "SCULPT THE WAVES - about 14:26. Stay right here in the Buddy Model screen: switch the mode menu (top left of the 3D window) from Object Mode to Sculpt Mode. Sculpting is a MODE of this screen in Buddy's layout - there is no separate Sculpting tab to hunt for. (In plain Blender it is the Sculpting workspace along the top; the brushes are the same.) Press Numpad . to centre your view on the icing. Start with the Inflate/Deflate brush - it puffs or dents the surface: run it over the drip heads and along the edges, where hand-poured icing is never even. Size the brush with F - F is brush size: move the mouse until the circle fits, then click. Then the Grab brush: pull gentle waves and dips into the surface, working around the ring until it looks poured rather than machine-made.",
            "SAVE (Ctrl+S). The tick comes when the icing sits on the dough as a finished, closed shell - drips at its rim, effects applied away, and the file saved. The sculpting above is the finishing touch - it is what makes the icing look poured - but the tick grades the shell itself, not the sculpting. If your modifiers are still live, you are at his halfway point, and the tick waits - keep going, exactly like he does. (His homework this part: a plate for the donut - Part 4 opens with his.)",
        ],
        "check": _check_icing_hug,
        "run": _tour_step_icing_hug,
    },
    {
        "id": "first_picture",
        "package": "donut",
        "title": "Part 4 - Plate, table, and a first picture",
        "how": "The donut gets a plate and a table, a "
                 "lattice bends it into a real shape, colour "
                 "goes on, and the first render happens.",
        "video": {"url": "https://www.youtube.com/watch?v=5Xlu2zwbJd0", "label": "Watch Part 4 on YouTube"},
        "skill": "Setting a scene: a plate built from a flat circle, the Lattice bend, first colours, the subsurface glow recipe, ray tracing, and your first render",
        "missing": "The donut resting on a plate on a table, ray tracing on, the glow recipe (Weight 1, Radius 1 1 1) on both dough and icing, and a render made.",
        "tools": ["add_circle", "add_sheet", "give_colour", "take_picture", "save_work"],
        "teach": [
            "Part 4 puts the donut somewhere: on a plate, on a "
            "table, with colour - and ends with your first real "
            "picture of it.",
            "THE PLATE - from a flat circle, at about 3:57. "
            "First, leave Sculpt Mode: Part 3 ended with you "
            "sculpting the icing, and in Sculpt Mode Shift+A "
            "does nothing at all - there is no Add menu there, "
            "because sculpting only reshapes the one thing you "
            "are working on. Switch the mode menu (top left of "
            "the 3D window) from Sculpt Mode back to Object "
            "Mode - the mode for moving whole things and "
            "adding new ones. Now Shift+A, Mesh, Circle. In "
            "the Add Circle panel set "
            "the Fill Type to Ngon - one big face filling the "
            "circle. The radius is yours to drag until the "
            "circle looks like his plate under the donut (he "
            "never states a number - match the picture). Tab "
            "into Edit Mode, press E and click straight away: "
            "the face is extruded in place. Press X, Faces, and "
            "delete the top face only - you can see through the "
            "plate from above now; that is correct. What remains "
            "is the plate's floor with its rim edge standing "
            "free. Select that rim edge (Alt+click it), then "
            "walk it outward into the plate's rim the way he "
            "does, about 5:33 to 7:24: E then S grows it out a "
            "little; E then up (Z) raises the lip; E and S once "
            "more flares it outward. Each move is by eye - watch "
            "his rim grow and match the profile.",
            "FINISH THE PLATE. Ctrl+R and add one loop cut "
            "around the rim's wall so the curve later holds its "
            "shape. Press Tab back to Object Mode before the "
            "next moves: the loop cut was Edit Mode work on the "
            "plate's own edges, but a modifier is an effect "
            "stacked on the whole object, and the section "
            "after this one adds a brand-new object - "
            "whole-object work, both of them. Stay in Edit "
            "Mode and THE TABLE's Shift+A would grow the "
            "table out of the plate's own mesh instead of "
            "standing it beside the plate. Modifiers tab: "
            "Subdivision Surface, levels "
            "2 - the rim curve appears. Then Solidify ABOVE it "
            "in the stack (drag it up): his order for the plate "
            "is Subdivision first, then Solidify dragged to the "
            "top, its Thickness dragged thin by eye. The plate "
            "has a real edge now, not a paper cutout.",
            "THE TABLE. Shift+A, Mesh, Plane. Press S and type "
            "2.4 - his exact number - and Enter: the plane "
            "scales to his table size. Slide it down (G, then Z) "
            "until its top is where the plate should rest.",
            "SET THE TABLE. Slide the donut and its plate onto "
            "the table, and bring the Mug back in from where it "
            "was parked: G moves the selected object; set them "
            "down like his frame at about 9:03 - donut on plate "
            "at the middle, mug beside them, everything resting "
            "on the tabletop, nothing floating.",
            "BEND IT REAL - the Lattice, at about 10:38. A real "
            "donut sags a little; a perfect torus does not. The "
            "Lattice is a cage you bend, and the shape inside "
            "follows. Press Shift+S and choose Cursor to "
            "Selected with the donut picked - the 3D cursor (the "
            "little target new objects are born at) jumps to the "
            "donut. Shift+A, Lattice. In its panel set Resolution "
            "W to 3. Scale the lattice (S) until it just wraps "
            "the donut AND its icing. Then select donut and "
            "icing, Shift+click the lattice last, and press "
            "Ctrl+P, Set Parent To, Object: they are parented - "
            "they now ride with the lattice. Now hang the "
            "Lattice modifier on the donut: click the donut, "
            "open the Modifiers tab (the wrench tab on the "
            "right - the same tab the plate's modifiers went "
            "on), click Add Modifier, Deform, Lattice, and in "
            "the new modifier's Object box pick the lattice. "
            "The Modifiers tab is the only door for this - "
            "the right-click menu has no Modifiers entry in "
            "it. Do the same for the icing: click it, Add "
            "Modifier, Deform, Lattice, Object box, the "
            "lattice. Tab into Edit Mode ON THE LATTICE "
            "and squeeze its middle ring inward - the donut "
            "pinches slightly, like it settled under its own "
            "weight. Nudge a couple of other points while you "
            "are there; he does this by eye.",
            "MAKE THE BEND PERMANENT. Press Tab back to Object "
            "Mode first: you are still in Edit Mode on the "
            "lattice, where your clicks keep landing on the "
            "lattice's own points - Blender will not let you "
            "pick another object at all - and Apply does not "
            "exist there anyway; applying a modifier is a "
            "whole-object job, the same trap as Part 2's "
            "walls. In Object Mode, select the donut, find its "
            "Lattice modifier, dropdown, Apply. Same for the "
            "icing. Then delete the lattice itself (select it, "
            "X). The sag stays - it is baked into the shapes "
            "now - and the cage is gone.",
            "FIRST COLOUR - about 16:17. His word for these is "
            "placeholder: close enough to judge the picture, "
            "replaced by real surfaces in Part 5. Click the "
            "icing, open the Material Properties tab (the "
            "checkerboard sphere), click New, and set Base Color "
            "to a hot pink; set Roughness to 0.2 - his stated "
            "number, the slider in the same panel. The mug and "
            "the plate need the same first move before any "
            "colour can go on: neither one has a material yet "
            "- nothing in Parts 1 to 3 ever made one - so "
            "click the mug, open the Material Properties tab, "
            "click New, and only then set its Base Color "
            "nearly black. Same for the plate: click it, "
            "click New, then set a plain mid grey. Clicking "
            "New is what creates the material - the box every "
            "colour and glow setting lives in; without it "
            "there is no panel to set anything in. Both "
            "colours by eye, both placeholders.",
            "THE FAMOUS GLOW - subsurface scattering, at about "
            "24:38. Real frosting and dough are not solid all "
            "the way through: light sinks in a little and "
            "glows back out, which is why food looks soft and "
            "edible. Blender's setting for it is called "
            "Subsurface, in the same material panel. The icing "
            "already wears the material you made in FIRST "
            "COLOUR. The dough does not - no step has ever "
            "given it one - so when you reach the dough, "
            "click it, open the Material Properties tab and "
            "click New first: a plain new material is all it "
            "needs, because what matters here is the glow "
            "recipe below, and the recipe needs a material to "
            "live in (its real surface arrives in Part 5). On "
            "the icing and then the dough: set Subsurface "
            "Weight "
            "all the way to 1 (he says 'let's just turn the "
            "weight all the way up to one'), and set the Radius "
            "to 1, 1, 1 - he clears the default numbers and "
            "types 1 into all three boxes. The Scale box beside "
            "them is how far the light travels once it sinks "
            "in - different foods want different distances; he "
            "leaves it standing in this part. Remember this "
            "recipe - weight 1, radius 1 1 1 - Buddy checks it "
            "exactly, because a weight of 0.2 is the same slider "
            "at a setting he never used.",
            "TURN RAY TRACING ON - about 20:48. In the Render "
            "Properties tab (the camera-back icon), find Ray "
            "Tracing and switch it ON. Guru is blunt about it: "
            "it should have been on by default. It is what makes "
            "Eevee's light bounce believably.",
            "LINE UP THE CAMERA. The lock for this lives in "
            "the sidebar: press N if the sidebar is closed, "
            "open its View tab, find the View Lock section "
            "and tick the box labelled Camera to View. It is "
            "not in the 3D window's View menu and not in the "
            "camera's own panel - the sidebar's View tab is "
            "its only home. The tick glues the camera to your "
            "view: drag your view around and the camera "
            "follows, so you frame the shot by simply looking "
            "at it. Drag until the frame looks like his first "
            "picture - donut left of centre, mug behind it. "
            "Untick Camera to View when it sits right, so the "
            "camera stays where you put it. The framing is "
            "by eye; he states no camera numbers anywhere in "
            "the series.",
            "RENDER. Press F12 - or Render menu, Render Image. "
            "Your first picture of the donut appears. (Render "
            "Slots: each render can live in its own slot - "
            "press J over the picture to flip between two and "
            "compare, the way he does at 21:04.) SAVE the file "
            "(Ctrl+S). Buddy ticks when the plate, table, glow "
            "recipe and ray tracing are all in place and a "
            "render exists - objects found by their job in the "
            "scene, because Guru does not name the plate and "
            "table until Part 8, and your names are your own.",
        ],
        "check": _check_first_picture,
        "run": _tour_step_first_picture,
    },
    {
        "id": "real_surfaces",
        "package": "donut",
        "title": "Part 5 - Real surfaces",
        "how": "Photo textures on every surface: the table "
                 "wired by hand, the rest by the texture "
                 "add-on - or by the same hand wiring - and "
                 "the dough gets real displacement.",
        "video": {"url": "https://www.youtube.com/watch?v=h30ZJQrb4s8", "label": "Watch Part 5 on YouTube"},
        "skill": "Photo textures: wiring colour, roughness, normal and displacement pictures by hand, sRGB versus Non-Color, and real displacement on the dough",
        "missing": "Every surface wearing the recipe on its own: table, plate and dough fully wired; the icing wired with its colour set by hand and its glow re-set; the dough displaced with a level-3 Subdivision Surface.",
        "tools": ["paint_picture", "push_with_picture", "save_work"],
        "teach": [
            "Part 5 replaces Part 4's placeholder colours with "
            "photographed surfaces. The real textures come from "
            "Poliigon (his link is under the video) and most go "
            "on with the Poliigon add-on - Buddy's tick does not "
            "care how a texture got there, only that each "
            "surface truly wears the recipe below.",
            "NO POLIIGON? You are not stuck. The add-on is only "
            "a shortcut: all it does is wire the same boxes you "
            "are about to wire by hand on the table. So the hand "
            "route IS the whole recipe - learn it on the table, "
            "then repeat it on every other surface in this part, "
            "as each section below describes. For the pictures "
            "themselves you need picture FILES on your computer: "
            "the same texture sets can be downloaded as ordinary "
            "image files (Poliigon gives its sets away file by "
            "file too, and other free texture libraries do the "
            "same), and your own photographs work as well. Each "
            "surface needs the same kinds of picture he uses: a "
            "colour photo, a roughness map, a normal map - and "
            "the dough needs a displacement map as well. Where "
            "a section below says the add-on does it, your hands "
            "do the table's wiring on that surface instead.",
            "THE WORKSPACE. This step works in Blender's "
            "Shading workspace - and Buddy's own screens along "
            "the top do not include one, so add it: click the "
            "+ at the right end of the top tab row, then "
            "General, then Shading. This is the material "
            "workshop: your object above, "
            "its material as a chain of boxes - nodes - below. "
            "A node's output plugs into the next node's input; "
            "the chain ends at the Principled BSDF, the box "
            "that decides how the surface answers light.",
            "THE TABLE, WIRED BY HAND - about 0:00 to 7:27. He "
            "deliberately does this one manually, 'because I "
            "think it's good for you to know how to do this "
            "stuff manually.' Click the table to select it "
            "first: it has no material yet (Part 4 coloured "
            "only the icing, the mug and the plate), so click "
            "New in the node editor's header to give it one - "
            "a fresh material is a single Principled BSDF box "
            "wired to the output, and that box is what every "
            "picture below plugs into; with no material there "
            "is nothing to wire into. His concrete set has four "
            "pictures: the colour photo, a roughness map (which "
            "areas shine), a normal map (fake fine bumps), and "
            "a displacement map (real height). For EACH picture: "
            "Shift+A in the node area, Texture, Image Texture, "
            "and open the picture. (One navigation note for "
            "this whole part: Blender 5's Add menu has no "
            "Vector heading, though older written guides use "
            "it - where a route below names a heading you "
            "cannot find, type the node's name into the search "
            "box at the top of the Add menu instead; the "
            "search finds every node, in every version.) Then "
            "the rule that matters: "
            "the COLOUR picture keeps its Color Space at sRGB; "
            "every other picture gets Color Space set to "
            "Non-Color - data maps are measurements, not "
            "colours, and Blender must not 'correct' them. Wire "
            "them: colour into Base Color; roughness into "
            "Roughness; normal through a Normal Map node "
            "(Shift+A, Displacement, Normal Map) into Normal; "
            "the "
            "displacement picture waits for the dough - the "
            "table keeps its own simpler wiring here. Above the "
            "chain, add a Texture Coordinate node and a Mapping "
            "node (Shift+A: Texture Coordinate under Input, "
            "Mapping under Displacement) feeding every "
            "picture's Vector socket, and raise the Mapping's "
            "Scale until the concrete's grain is the size it is "
            "in his frame.",
            "THE PLATE - about 7:46. First it is unwrapped: Tab "
            "into Edit Mode, select all, U, Smart UV Project - "
            "unwrapping flattens the shape's skin into a flat "
            "map so a photo can wrap it without stretching (his "
            "seams go where Part 3's icing crease runs, and the "
            "plate follows the same idea). Then its texture set "
            "goes on with the Poliigon add-on: select the plate "
            "in the add-on, pick the ceramic set, and it wires "
            "colour, roughness and normal the same way you just "
            "did by hand. By hand instead: wire the plate's own "
            "material with the table's recipe - its ceramic set "
            "as picture files: colour into Base Color, "
            "roughness into Roughness, normal through a Normal "
            "Map node into Normal, and a Texture Coordinate "
            "and a Mapping node feeding every picture's Vector "
            "socket.",
            "THE ICING - about 12:57, and a repair at 16:22. "
            "Its glaze set goes on the same add-on way - or by "
            "hand, with the table's wiring done on the icing's "
            "own material. Then "
            "Guru finds a mistake: Part 4's hand-set pink "
            "survived, fighting the glazed look. His fix, in the "
            "Shading workspace: DELETE the wire from the "
            "texture's Color output into Base Color, and set "
            "Base Color back to a pink by hand. The roughness "
            "and normal pictures stay wired - they are what "
            "make the glaze look wet - and he re-sets the "
            "Subsurface by hand here too: Weight 1, Radius "
            "1 1 1, the Part 4 recipe. Buddy's tick allows the "
            "icing's colour to be hand-set exactly this way; "
            "what it will not pass is a surface with no real "
            "texture wiring at all.",
            "THE DOUGH - about 19:05, the part's showpiece. Its "
            "bread set goes on like the others - by the "
            "add-on, or wired by hand the table's way. Then "
            "real "
            "DISPLACEMENT: a Displacement node (Shift+A, then "
            "type Displacement into the search) takes the "
            "dough's displacement "
            "picture and plugs into the Material Output node's "
            "Displacement socket - the last node in the chain. "
            "In the Material Properties panel set the Surface "
            "Displacement dropdown to 'Displacement and Bump' - "
            "that switch is what lets the height map move real "
            "geometry instead of just faking shade. Add a "
            "Subdivision Surface modifier to the dough with "
            "Levels Viewport 3 and Render 3 - his stated "
            "levels, because displacement needs a fine mesh to "
            "carve. Then tune the Displacement node's Scale: he "
            "tries 0.2, finds it too strong, and settles at "
            "0.12 - his numbers. The crust goes craggy and real.",
            "THE MUG waits: its texture is Part 6's job, and "
            "Guru leaves it alone here - so does Buddy's tick.",
            "SAVE (Ctrl+S). The tick reads every surface on its "
            "own: table, plate and dough fully wired (colour, "
            "a Non-Color data map, a normal map), the icing "
            "wired with its hand-set colour and re-set glow, "
            "and the dough carrying displacement at his "
            "levels. One good surface cannot carry three bare "
            "ones - that pooling was the old check's hole.",
        ],
        "check": _check_real_surfaces,
        "run": _tour_step_real_surfaces,
    },
    {
        "id": "unwrap_mug",
        "package": "donut",
        "title": "Part 6 - Mug seams, unwrapping, and coffee foam",
        "how": "The mug gets its texture the proper way - "
                 "seams, a clean unwrap - and the coffee's foam "
                 "is built out of the mug itself.",
        "video": {"url": "https://www.youtube.com/watch?v=yxAqN8TzFbo", "label": "Watch Part 6 on YouTube"},
        "skill": "Unwrapping: seams marked where they hide, Live Unwrap, and a new surface - the coffee foam - built out of the mug's own rim",
        "missing": "The mug wearing a real set of seams and a UV map, and the foam in its rim with a raised edge and a dipped middle - never a flat disc.",
        "tools": ["split_off", "inset_face", "paint_picture", "save_work"],
        "teach": [
            "Part 6 gives the mug its real texture. The texture "
            "arrives fine and lands wrong - the handle's UVs "
            "are garbage - so this part is about unwrapping "
            "properly: cutting the skin so it lies flat.",
            "PUT THE TEXTURE ON - 0:00. Through the Poliigon "
            "add-on, put the Rustic Gold Ceramic set on the "
            "Mug. No Poliigon? Put a ceramic set on by hand, "
            "the way Part 5's table taught: picture files of a "
            "ceramic set (downloaded as plain images, or your "
            "own photos), wired colour (sRGB) into Base Color, "
            "roughness (Non-Color) into Roughness, and the "
            "normal picture (Non-Color) through a Normal Map "
            "node into Normal, with a Texture Coordinate and a "
            "Mapping node feeding the pictures' Vector "
            "sockets. Either way the pictures land the same - "
            "the unwrapping below is what makes them sit "
            "right. The free-rotation handles appear at the mug's "
            "base: that unfinished look is what this part fixes.",
            "A SMALL CLEANUP at 1:37: in the mug's material, "
            "find the Roughness picture's wire into the "
            "Principled and delete it (click the wire, X), then "
            "set Roughness with its plain slider - he steers it "
            "by eye to a soft sheen. That wire exists because "
            "the ceramic set just went on - both routes wire a "
            "roughness picture in. If your mug still wears "
            "only its plain Part 4 colour, there is no wire to "
            "delete: just set the slider.",
            "TURN ON ON CAGE. In the Modifiers tab, the mug's "
            "Subdivision Surface has a small triangle button - "
            "On Cage. Switch it on: the low-poly cage stops "
            "hiding under its smoothed preview, which matters "
            "because you are about to edit the cage.",
            "MARK THE SEAMS - Ctrl+E, Mark Seam, from about "
            "2:42. A seam is a cut line: where the skin will be "
            "split to lie flat, like the seam of a garment. "
            "This needs Edit Mode with Edge Select: Tab into "
            "Edit Mode on the mug, then press 2 (or click the "
            "middle of the three select-mode icons at the top "
            "left) - Alt+click only picks an edge loop in Edge "
            "Select; in Vertex Select, where Edit Mode opens, "
            "it picks points instead. Select an edge loop "
            "(Alt+click an edge), then "
            "Ctrl+E and Mark Seam - it turns orange-red. His "
            "layout, all of it: one loop at the handle's TOP "
            "joint; one loop at its BOTTOM joint (the handle "
            "becomes its own island); one vertical line down the "
            "mug's side, just beside the handle where nobody "
            "looks; the loop around the INSIDE at the base; one "
            "vertical line down the inside; and the loop around "
            "the UNDERSIDE. Six cuts, each where a real mug's "
            "glaze would hide them.",
            "LIVE UNWRAP. This lives in the UV Editing "
            "workspace, which Buddy's own screens do not "
            "include - add it with the + at the right end of "
            "the top tab row: Add Workspace, General, UV "
            "Editing. In that workspace, the flat map on the "
            "left is the UV Editor; open its UV menu (in that "
            "editor's own header) and tick Live Unwrap - from "
            "then on, every seam you mark re-flattens the map "
            "instantly, so you can watch each cut fix the "
            "stretching. Then his UV "
            "toolkit finishes the job: the Mio3 UV add-on's "
            "buttons (an extension he uses; its absence never "
            "blocks the tick) and Gridify, which straightens the "
            "curved side panel into a clean rectangle - watch "
            "how much tidier the texture sits afterwards.",
            "THE TABLE GOES DARK - about 21:52, off to the side "
            "of the part and easy to miss: it is where the "
            "finale's dark counter actually comes from. In the "
            "Shading workspace, on the TABLE's material, add an "
            "RGB Curves node (Shift+A, Color, RGB Curves) "
            "between the colour picture and the Principled's "
            "Base Color, and bend its line into a gentle S - "
            "drag the shadow end DOWN and the top end up a "
            "touch: the pale concrete darkens and gains "
            "contrast. Then add a Hue Saturation Value node "
            "(Shift+A, Color) after it and pull Saturation down "
            "until the concrete's yellow-green cast is gone. "
            "Both amounts are by eye - match his frame.",
            "THE COFFEE FOAM - about 25:05, built from the mug "
            "itself, never a new disc. Tab into Edit Mode on "
            "the Mug, switch to Edge Select (press 2 - the "
            "Alt+click below only picks an edge loop in Edge "
            "Select), and select the loop of edges around the "
            "INSIDE of its rim - the coffee's edge. Shift+D "
            "duplicates it in place; press Esc; then press P "
            "(Separate) and choose Selection: the loop becomes "
            "its own object. Tab out, select it, F2, name it "
            "Foam. Back in Edit Mode on the Foam: select all "
            "and press F - Fill: a skin stretches across the "
            "ring. Press I and inset a little, creating the "
            "foam's raised edge; select the new middle face and "
            "press G, then Z, and lower it slightly - the dip "
            "in the middle is what catches the light and reads "
            "as a liquid surface. Press I once more for the "
            "inner detail. Right-click, Shade Smooth.",
            "FOAM TEXTURE - the 'Coffee Foam Atlas': one photo "
            "holding NINE foam designs, and you use one. In the "
            "UV editor, scale the foam's flattened shape down "
            "until it covers just one design - he drags his "
            "onto 'that one at the top', but any of the nine is "
            "a legal coffee; his point is one design per cup, "
            "not the whole sheet stretched across. No atlas? "
            "Any single photo of coffee foam does the same "
            "job - a photo of a real cup, taken yourself, is "
            "ideal: give the Foam its own material (Material "
            "Properties, New), wire the photo in as an Image "
            "Texture into Base Color, and scale the foam's UV "
            "shape onto the part of the photo you want in the "
            "cup.",
            "SAVE (Ctrl+S). Buddy ticks when the mug wears a "
            "real set of seams - ten or more seam edges and a "
            "UV map: a stray edge or two will not pass. Buddy "
            "counts the seams; it does not grade where they "
            "lie, so his six-cut layout above is not the tick "
            "talking - it is what makes the unwrap actually "
            "lie flat, which is why you follow it - and the "
            "foam sits in the rim with its edge raised and its "
            "middle dipped - a flat dark disc dropped in the "
            "top is not his coffee and will not tick.",
        ],
        "check": _check_unwrap_mug,
        "run": _tour_step_unwrap_mug,
    },
    {
        "id": "scatter",
        "package": "donut",
        "title": "Part 7 - Sprinkles, scattered for real",
        "how": "One sprinkle, a handful of hand-shaped "
                 "variants, one shared rainbow material, and "
                 "Blender 5's own scatter system does the rest.",
        "video": {"url": "https://www.youtube.com/watch?v=_-QsGTL7pS0", "label": "Watch Part 7 on YouTube"},
        "skill": "Scatter on Surface (Blender 5): collection instancing, weight-painting a distribution mask, and one material colouring every copy at random",
        "missing": "The scatter modifier reading the way he set it: the Sprinkles collection with Pick Instance on, Density 900, Poisson Disk, and your painted Group wired as the Distribution Mask.",
        "tools": ["add_tube", "paint_it", "save_work"],
        "teach": [
            "Part 7 covers the donut in sprinkles - hundreds of "
            "them, placed by a system, not by hand. This part "
            "needs Blender 5.0 or newer: the scatter tool below "
            "is one of its new features, and there is no older-"
            "Blender version of this step.",
            "PLANT THE CURSOR FIRST - about 0:00. Before making "
            "anything, he clicks on the donut's top with Shift+"
            "right-click: that plants the 3D cursor there. The "
            "cursor is where new objects are born - it is why "
            "the sprinkle appears on the donut instead of at "
            "the world's centre.",
            "ONE SPRINKLE. Shift+A, Mesh, Cylinder. Work in "
            "the Add Cylinder panel - the small panel that "
            "appears at the bottom left of the 3D view the "
            "moment the cylinder is born: drag Radius down to "
            "nearly nothing, then "
            "back up a touch; lengthen the Depth; and set "
            "Vertices to 6 - his exact number; a sprinkle is a "
            "hexagonal sliver, not a tube. Set those numbers "
            "BEFORE you click anything else: that panel is the "
            "only place Vertices can be set, and it vanishes "
            "at your next click - if it is already gone, "
            "delete the cylinder (select it, X) and add it "
            "again so the panel comes back. The radius and "
            "depth "
            "amounts are dragged by eye; there is no typed "
            "value. Add a Subdivision Surface modifier and two "
            "loop cuts (Ctrl+R) near the ends so the caps round "
            "off; right-click, Shade Smooth; press F2 and name "
            "it Sprinkle.",
            "THE VARIANTS - about 4:23. Real sprinkles are not "
            "identical, so: Shift+D duplicates the sprinkle "
            "several times (his screen ends with six), and each "
            "copy is twisted, bent and resized BY HAND until "
            "they are all cousins, not clones. While they are "
            "all selected, right-click and Set Origin, Origin "
            "to Geometry - each sprinkle's centre dot moves "
            "into its middle, so scattered copies sit INTO the "
            "icing instead of floating on their ends. Watch "
            "that submenu as you pick: Origin to 3D Cursor "
            "sits right next to Origin to Geometry in it, and "
            "it is the wrong row - it moves the centre dots "
            "onto the 3D cursor instead of into each "
            "sprinkle's middle, and a sprinkle thrown that far "
            "out of shape can momentarily read as a plain cup "
            "and drop the tour back. If you pick it by "
            "mistake, no harm done: Ctrl+Z undoes it, or just "
            "run Set Origin, Origin to Geometry again on the "
            "same selection.",
            "FILE THEM AWAY. Select all the variants and press "
            "M, Move to Collection, New Collection, and name it "
            "Sprinkles. Then, in the Outliner (the list of "
            "everything, top right), untick the checkbox beside "
            "the Sprinkles collection: the originals vanish "
            "from view AND from renders. They are not deleted - "
            "the scatterer is about to read them from that "
            "collection.",
            "ONE MATERIAL FOR ALL OF THEM - about 6:26. He is "
            "explicit about the system: ONE material, named "
            "Sprinkles, on every variant - not a colour per "
            "shape. (Link materials between the copies with "
            "Ctrl+L, Link, Materials.) The rainbow lives in its "
            "nodes: in the Shading workspace, add an Object "
            "Info node (Shift+A, Input, Object Info) - its "
            "Random output is a different steady number for "
            "every scattered copy - and a Color Ramp node "
            "(Shift+A, Color, Color Ramp - Blender 5's Add "
            "menu has no Converter heading; the ramp lives "
            "under Color). Wire Random into "
            "the ramp's Fac, set the ramp's interpolation to "
            "Constant (the dropdown on the ramp - Constant means "
            "each copy gets ONE flat colour, never a blend), "
            "wire the ramp's Color into Base Color, and fill "
            "the ramp with his palette: aqua takes most of the "
            "bar (it is the primary colour), then purple, pink, "
            "white and yellow in smaller slices, saturation "
            "kept under full. Set Roughness by eye - 'a little "
            "bit shiny' - and the Subsurface recipe from Part "
            "4, with the Scale turned really low (his words; "
            "the finale retunes it to a stated number).",
            "SCATTER - the modifier, about 8:35 in his order "
            "of work and the heart of the part. Select the "
            "Icing, Modifiers tab, Add Modifier, and add "
            "Scatter on Surface (one of the new built-in "
            "geometry systems in Blender 5). Its panel opens "
            "with four rows at the top - Density Method, "
            "Distribution Method, Density, and the "
            "Distribution Mask - and in his order those are "
            "set LATER (the mask needs the paint you are about "
            "to do), so leave the top rows for now and work "
            "the sections below them. INSTANCING: set Instance "
            "Type to Collection, and the Collection box to "
            "your Sprinkles collection; Pick Instance ON (each "
            "scatter point then takes a whole variant, not a "
            "slice of one). TRANSFORM: nudge Surface Offset up "
            "very, very slightly, so they sit ON the icing "
            "instead of in it, and set Alignment Axis to Y (a "
            "sprinkle's length now follows its Y, so it lies "
            "along the icing instead of standing on end). One "
            "setting in this system has no button anywhere in "
            "the panel: Reset Transform. There is nothing to "
            "press - the scatterer starts with it already on, "
            "and that is what lets the sprinkles lie down "
            "along the surface; it is already doing its job. "
            "RANDOMIZE: switch it ON, with Rotation Y at 360 "
            "degrees and X turned just a little - his words, "
            "no number given.",
            "PAINT WHERE THEY MAY LAND - about 12:44. Select "
            "the Icing and enter Weight Paint mode (the mode "
            "dropdown, top left). Weight painting paints an "
            "invisible strength map onto a shape: red is full "
            "strength, blue is none. Turn on Front Faces Only "
            "so you do not paint through to the underside: it "
            "lives in the header's Brush menu, in the Advanced "
            "section - tick it there. Paint the top of the "
            "icing red; paint softer - lighter pressure - down "
            "the edges. The values live in a VERTEX GROUP (a "
            "named list of points with strengths); Blender "
            "names yours 'Group' automatically, and his keeps "
            "that name - do not rename it: the mask in the "
            "next section points at that exact name.",
            "THE MASK - about 17:00, and he warns about this "
            "one himself: the Distribution Mask is a row of "
            "its own near the TOP of the scatter panel - it is "
            "NOT inside the Masking section lower down (that "
            "section holds an image picker, a different tool). "
            "The row starts out showing a plain number; at its "
            "right end is a small icon that switches the row "
            "to take an attribute name instead - click it, and "
            "type Group: your painted group. NOT the Density "
            "input (plugging the paint there is the mistake he "
            "calls out). Sprinkles now only grow where you "
            "painted, thick on top, thinning at the edges, "
            "none underneath.",
            "DENSITY - about 26:58, back at the top rows of "
            "the same panel. Set the Density Method "
            "dropdown to Density and the Density itself to "
            "900 - his stated number. (The other method, Total, "
            "spreads a fixed count over the whole surface "
            "however big it is; Density keeps them evenly "
            "packed.) Set the Distribution Method to Poisson "
            "Disk and give the Minimum Distance a small value "
            "- by eye, until the sprinkles stop touching - and "
            "cycle the Seed number until a random arrangement "
            "pleases you; both of those are taste, and his are "
            "never stated.",
            "ONE GLOBAL LOOK - about 33:34. In the Render "
            "Properties, under Color Management, set the Look "
            "to Medium High Contrast. He makes it a standing "
            "choice for the series - it is the same contrast "
            "the final Part 8 picture is rendered with.",
            "SAVE (Ctrl+S). Buddy's tick reads the scatter "
            "modifier itself: collection instancing with Pick "
            "Instance, Density at 900, Poisson Disk, the "
            "painted group wired as the mask attribute with "
            "real paint in it, and the variants sharing the one "
            "Object Info rainbow material. Scattering sprinkles "
            "by any other system does not tick - this part is "
            "about HIS new system.",
        ],
        "check": _check_scatter,
        "run": _tour_step_scatter,
    },
    {
        "id": "final_picture",
        "package": "donut",
        "title": "Part 8 - The final picture",
        "how": "Sun, window light through two blockers, a "
                 "blue sky light and a warm bounce, a light "
                 "probe, depth of field - and the photograph.",
        "video": {"url": "https://www.youtube.com/watch?v=WobATxh3i-g", "label": "Watch Part 8 on YouTube"},
        "skill": "Lighting a photograph: a sun through window blockers, sky and bounce point lights, a Light Probe Volume, depth of field, shadow Steps",
        "missing": "His rig in place - sun at about 10, two upright blockers, blue Sky and white Indoor Bounce, the probe at resolution 4, shadow Steps at 16, the camera focused on the icing, the set parented - and a fresh render.",
        "tools": ["add_sun", "add_lamp", "add_sheet", "take_picture", "save_work"],
        "teach": [
            "Part 8 is photography: the scene is done, and now "
            "it gets lit, framed and shot like a cafe photo on "
            "a magazine page.",
            "HOUSEKEEPING - about 0:15. Parenting first: "
            "selecting a child, then Shift+clicking its parent "
            "and pressing Ctrl+P, Object (Keep Transform) makes "
            "the child ride with the parent without jumping. "
            "Do it four times: the Icing parents to the Donut; "
            "the Donut to the Plate; the Foam to the Mug; and "
            "the Plate and the Mug to the Table. Now moving the "
            "table carries the whole set. Then the last two "
            "names of the series: F2 on the plane - Table. F2 "
            "on the plate - Plate. (Yes, here at the end is "
            "where those names come from.)",
            "THE SUN - about 2:11. Select the lamp that has "
            "been in your scene since Part 1 and press F2: "
            "Sun. In its Light panel, change its Type to Sun - "
            "a sun light throws even, parallel light across "
            "everything, like real daylight - and set its "
            "Strength to about 10 ('I keep this around 10'). "
            "Its Temperature slider (the Kelvin colour of the "
            "light, a newer-Blender feature where your copy "
            "has it) is warmed until the light looks like an "
            "early morning - he states no number; warm it by "
            "eye. Angle the sun so the light comes from the "
            "right of your frame.",
            "THE WINDOW TRICK - about 5:28. A bare sun floods "
            "everything; a sun seen through a window lays one "
            "bright sliver across the table. Shift+A, Mesh, "
            "Plane - a blocker. Move it to stand between the "
            "sun and the set, then R, then X, then hold Ctrl "
            "while rotating until it snaps to exactly 90 "
            "degrees, standing upright. Shift+D duplicates it; "
            "R, Z, 90 turns the copy upright the other way. "
            "Two walls of light-shade, with a gap between them "
            "- slide them (G) until a sliver of sun falls "
            "across the donut and the rest of the table sits "
            "in softer shade. The sizes and exact positions are "
            "worked by eye; watch his light, then place yours.",
            "A LITTLE RESTAGING - about 7:26: with the light "
            "placed, he slides the mug further back (G, and "
            "Shift+Z keeps it sliding flat across the table's "
            "plane instead of floating) until the composition "
            "balances - donut front and bright, mug behind in "
            "the shade's edge. By eye, as always with framing.",
            "FILE THE LIGHTS AWAY - about 8:16: select the sun "
            "and both blockers, press M, Move to Collection, "
            "New Collection, and name it Lighting. The stage "
            "hands live in one drawer now.",
            "THE SKY - about 8:49. Select the Sun and Shift+D: "
            "a copy. F2 - Sky. Change its Type to Point (a "
            "light that glows out in all directions from one "
            "spot, like a bulb). This dome of sky does the soft "
            "ambient fill: set its Colour by clicking the "
            "colour box and choosing a soft, slightly purple "
            "blue (he clears the warm temperature tint first) "
            "- the value is by eye. Move it up high, to where a "
            "window's sky would be. And increase its Radius 'by "
            "a lot' - a big light source makes very soft "
            "shadows, and the sky's shadows should be nearly "
            "shadowless. Amount unstated; open it right up.",
            "THE BOUNCE - about 13:23. Shift+D the Sky: F2 - "
            "Indoor Bounce. Clear its Colour back to plain "
            "white (the default) and set its Power back to "
            "10 - the default, his stated resting value. "
            "Position it off on the set's dark side, lower, "
            "where light that hit a cafe wall would bounce "
            "back from. This is the gentlest light in the rig - "
            "it just lifts the shadows so they are dark, not "
            "dead.",
            "THE CAMERA - about 15:05. Turn on Camera to "
            "View - the lock lives in the sidebar: press N "
            "if the sidebar is closed, open its View tab, "
            "find the View Lock section and tick the box "
            "labelled Camera to View. It is not in the 3D "
            "window's View menu and not in the camera's own "
            "panel - the sidebar's View tab is its only "
            "home. The tick glues the camera to your view, "
            "so you frame the shot by simply looking at it: "
            "pull your view closer until the donut fills the "
            "frame the way his does - big, left of centre, the "
            "mug behind it right, the plate running off the "
            "bottom edge. Untick the lock when it sits "
            "right, so the camera stays where you put it. "
            "No lens change is "
            "made or stated anywhere in the series - the "
            "framing is distance and angle, both by eye.",
            "EEVEE QUALITY - about 15:36. In the Render "
            "Properties, under Shadows, find Steps and set it "
            "to 16 - the maximum. His words: the default 'is "
            "wrong' and 'should be maxed out' - at 16 the "
            "sun's shadow edges turn clean. The render samples "
            "he reads off as they stand: Viewport 16, Render "
            "64. (Ray tracing was switched on back in Part 4 - "
            "it stays on.)",
            "RETUNE UNDER THE LIGHT - the subsurface Scale is "
            "the one material number the finale states twice: "
            "on the ICING set the Subsurface Scale to 0.03; on "
            "the SPRINKLES material set it to 0.08 (he tries "
            "0.06 on the sprinkles first, then decides 0.08 - "
            "0.08 is the value that ships). Weight stays 1 and "
            "Radius 1 1 1 everywhere, as set in Part 4.",
            "THE LIGHT PROBE - about 20:17. Eevee's fast "
            "renderer needs help with bounced light indoors: a "
            "Light Probe Volume is a box that samples the "
            "light around the set and feeds it back as soft "
            "bounce. Shift+right-click the donut (cursor "
            "there), Shift+A, Light Probe, Volume. Fit the "
            "box to the set as one whole object: move it (G) "
            "and scale it (S) until it just encapsulates the "
            "set, its bottom sitting just above the table. "
            "Set its "
            "Resolution to 4 - his stated value ('I probably "
            "only need about three. No, I'll go four'). He "
            "then nudges a couple of the box's points by hand - "
            "one to the plate's edge, one inside the donut - "
            "but in this version of Blender a Volume probe "
            "has no Edit Mode at all (its mode menu holds "
            "Object Mode only), so there are no points to "
            "grab: the whole-box fit you just made, by the "
            "object's own position and scale, is the fitting "
            "this version offers. He also bakes the probe - "
            "Blender pre-cooks the bounce into it - but in "
            "this version the Render Properties carry no "
            "Bake Light Cache button: the panel's sections "
            "hold no indirect-lighting bake at all, so there "
            "is nothing to press and nothing to hunt for. "
            "The probe and its resolution are what Buddy "
            "grades, and the picture renders without the "
            "bake.",
            "DEPTH OF FIELD - about 22:30. Click the camera, "
            "open its Depth of Field section, switch it ON, "
            "and set Focus Object to the Icing - click the "
            "eyedropper, then the icing (he picks it in the "
            "Outliner because the probe box intercepts clicks "
            "in the view). The background now falls softly out "
            "of focus like a real camera's. The F-Stop he "
            "never states - Blender's own resting value "
            "stands; widening or narrowing it is your taste.",
            "SUN SHADOW JITTER - about 24:36: on the Sun, in "
            "its Shadow settings, switch Jitter ON. It softens "
            "the shadow edge in the final render. His warning "
            "comes with it: leave the VIEWPORT jitter off - in "
            "the working view it just looks like noise.",
            "THE COMPARISON - about 25:25. He renders twice: "
            "F12 for the Eevee picture, then switches the "
            "render engine to Cycles (the Render Properties' "
            "top dropdown - on his machine the GPU does it: "
            "Preferences, System, Cycles Render Devices) and "
            "renders again into another slot, flipping between "
            "them with J. Eevee is the series' photograph; "
            "Cycles is the slower, truer second opinion. Judge "
            "yours the same way.",
            "SAVE (Ctrl+S) - and the series is done. Buddy "
            "ticks the finale on the rig itself: a sun at "
            "about 10, two upright blockers, the blue sky "
            "point and the white bounce at 10, a probe volume "
            "at resolution 4, shadow steps at 16, the camera's "
            "focus on the icing, the parenting done, the "
            "retuned glow - and a fresh render on file. When "
            "it ticks, you have built the donut the way he "
            "built it: every part, in order, with nothing "
            "done for you.",
        ],
        "check": _check_final_picture,
        "run": _tour_step_final_picture,
    },
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
                obj = context.object
                before = {m.name for m in obj.modifiers} \
                    if obj is not None else set()
                result = bpy.ops.object.modifier_add(type=act["target"])
                mod = None
                if obj is not None:
                    for m in obj.modifiers:
                        if m.type == act["target"] \
                                and m.name not in before:
                            mod = m
                            break
                if mod is None:
                    # A press must never be a silent no-op
                    # (walkthrough gap 1.16: the step card's
                    # own modifier buttons produced nothing
                    # and said nothing - the saved file held
                    # no modifiers at all, and the NEXT step's
                    # instruction dead-ended on the missing
                    # effect). Verify the effect exists, and
                    # say plainly when it does not.
                    self.report(
                        {"ERROR"},
                        f"No effect was added - '{act['plain']}' "
                        "did not land on the picked thing. Click "
                        "the shape itself once so it is outlined "
                        "orange, then press the button again. "
                        "When it works, the effect's name "
                        "appears in the Modifiers tab (the "
                        "wrench) on the right.")
                    return {"CANCELLED"}
                for prop, value in _MOD_DEFAULTS.get(
                        act["target"], {}).items():
                    if hasattr(mod, prop):
                        setattr(mod, prop, value)
                self.report(
                    {"INFO"},
                    f"Done - {act['plain']}: '{mod.name}' is "
                    f"now on '{obj.name}'. See it in the "
                    "Modifiers tab (the wrench) on the right - "
                    "that list is where it lives.")
                return {"FINISHED"}
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
# the job, drawn as one press the user makes themselves. The Expert
# is an assistant to a creator: it answers, explains, sets exact
# values, wires nodes and fetches ingredients for bounded tasks the
# user asks for - the user is always the author. The key is the
# user's own, stored in Blender's preferences on their own computer;
# Buddy brings no key and charges nothing.
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


_EXPERT_TASK_MODE = None


def _task_mode_path(create=False):
    folder = bpy.utils.user_resource("CONFIG", path="blender_buddy", create=create)
    if not folder:
        raise OSError("Blender's configuration folder is unavailable")
    return os.path.join(folder, "task_mode.json")


def _task_mode_get(_owner):
    global _EXPERT_TASK_MODE
    if _EXPERT_TASK_MODE is None:
        try:
            with open(_task_mode_path(), encoding="utf-8") as stream:
                _EXPERT_TASK_MODE = json.load(stream) is not False
        except (OSError, ValueError):
            _EXPERT_TASK_MODE = True
    return _EXPERT_TASK_MODE


def _task_mode_set(_owner, value):
    global _EXPERT_TASK_MODE
    # Saving Blender's preferences here would also commit unrelated edits.
    # Keep this single choice beside the profile, including with auto-save off.
    path = _task_mode_path(create=True)
    temp = tempfile.NamedTemporaryFile(mode="w", encoding="utf-8",
                                       dir=os.path.dirname(path), delete=False)
    try:
        with temp:
            json.dump(bool(value), temp)
        os.replace(temp.name, path)
    finally:
        if os.path.exists(temp.name):
            os.unlink(temp.name)
    _EXPERT_TASK_MODE = bool(value)


class BUDDY_Preferences(AddonPreferences):
    bl_idname = __name__

    expert_task_mode: BoolProperty(
        name="Expert help with tasks",
        description="Draft steps to review and run. Turn off for advice only",
        default=True, get=_task_mode_get, set=_task_mode_set)
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
        name="Floating Expert card",
        description="Show the Buddy Expert as a floating card over "
                    "the 3D window: drag it by its title bar, "
                    "resize it from its bottom-right corner, "
                    "minimise it to the corner chip, and ask the "
                    "expert right there. On by default - the setup "
                    "controls stay in the panel",
        default=True)
    expert_card_x: IntProperty(
        name="Expert card left",
        description="Where the floating Expert card sits in the "
                    "3D window - set by dragging it",
        default=-1)
    expert_card_y: IntProperty(
        name="Expert card bottom",
        description="Where the floating Expert card sits in the "
                    "3D window - set by dragging it",
        default=-1)
    expert_card_w: IntProperty(
        name="Expert card width",
        description="How wide the floating Expert card is - set "
                    "by dragging its bottom-right corner",
        default=440, min=320, max=1600)
    expert_card_h: IntProperty(
        name="Expert card height",
        description="How tall the floating Expert card is - set "
                    "by dragging its bottom-right corner",
        default=360, min=240, max=1600)
    expert_card_min: BoolProperty(
        name="Expert card minimised",
        description="The floating Expert card is minimised to "
                    "its corner chip",
        default=False)

    def draw(self, context):
        global _WRAP_CAP
        _WRAP_CAP = _fit_width(context)
        layout = self.layout
        layout.prop(self, "expert_service")
        if self.expert_service == "CODEX" and not bpy.app.online_access:
            _wrap(layout, _OFFLINE_MESSAGE)
        elif self.expert_service == "CODEX":
            # Status FIRST, with the remedy as a button: the login
            # is one click from here, not a treasure hunt.
            found = _find_codex()
            if found:
                signed = _codex_login_status(found)
                if signed == "in":
                    _wrap(layout, f"Codex: found at {found}, and "
                                  "signed in. The expert can ask "
                                  "through your ChatGPT login.")
                elif signed == "out":
                    _wrap(layout, f"Codex: found at {found}, but "
                                  "not signed in yet. Open it and "
                                  "sign in with your ChatGPT "
                                  "account - that's the whole setup.")
                else:
                    _wrap(layout, f"Codex: found at {found}. If "
                                  "you're signed in there, the "
                                  "expert works through your "
                                  "ChatGPT login.")
                layout.operator("buddy.open_codex",
                                text="Open Codex to sign in")
            else:
                _wrap(layout, 'Codex command-line program: not located from Blender. This does not prove the desktop app is missing or that you need to sign in again. Restart Blender after Codex finishes updating, then test again.')
            _wrap(layout, "The key, address and model fields "
                          "don't apply to the ChatGPT route - "
                          "Codex uses its own - so they're hidden "
                          "here rather than pretending to matter.")
        elif self.expert_service == "LOCAL":
            layout.prop(self, "expert_url")
            layout.prop(self, "expert_model")
            _wrap(layout, "A local AI needs no key and no login - "
                          "it just has to be running (for example "
                          "Ollama). Buddy checks it's answering "
                          "before it asks.")
        else:
            layout.prop(self, "expert_key")
            layout.prop(self, "expert_url")
            layout.prop(self, "expert_model")
        layout.prop(self, "expert_task_mode")
        layout.prop(self, "expert_float")
        layout.operator("buddy.test_expert",
                        text="Test this connection")
        try:
            status = context.window_manager.buddy_expert_status
        except Exception:
            status = ""
        if (status or "").strip():
            _wrap(layout, status)
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
                      "Blender's own preferences. One honest "
                      "exception to picture: on the ChatGPT route "
                      "the question goes to OpenAI's Codex program "
                      "on your computer, and that program does its "
                      "own work there - Buddy hands it the same "
                      "question and scene description, no more.")


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
    try:
        parts = urllib.parse.urlsplit(url or "")
        if parts.scheme not in {"http", "https"} or parts.username is not None:
            return False
        host = parts.hostname
        return host == "localhost" or ipaddress.ip_address(host or "").is_loopback
    except ValueError:
        return False


_OFFLINE_MESSAGE = ("Blender's online access is off. Use a local model on this computer "
                    "or allow online access in Blender to contact the service.")


def _expert_access_allowed(settings):
    # Read Blender's permission only on the main thread, before starting work.
    return (bpy.app.online_access or
            (settings.get("service") != "CODEX" and _is_local_url(settings.get("url"))))


class _LoopbackRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _is_local_url(newurl):
            raise _ExpertFault("offline")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _expert_urlopen(request, timeout, loopback_only=False):
    if not loopback_only:
        return urllib.request.urlopen(request, timeout=timeout)
    if not _is_local_url(request.full_url):
        raise _ExpertFault("offline")
    # A permitted local call must also stay local after redirects, and must
    # never pick up an external HTTP proxy from the user's environment.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), _LoopbackRedirect())
    return opener.open(request, timeout=timeout)


_LOCAL_PROBE = {"at": 0.0, "ok": False, "url": ""}


def _local_alive(url):
    """Is a local AI actually answering at this address right now?
    Probed for real (a short GET on the server's own version page),
    cached for a few seconds so the panel can ask on every draw
    without hammering. Until this existed, 'ready' for a local AI
    was a guess that was always yes - so when the server was off,
    the ask failed and the one message written for exactly that
    failure could never be shown."""
    if not bpy.app.online_access and not _is_local_url(url):
        return False
    base = (url or "").split("/v1/")[0].rstrip("/")
    if not base:
        return False
    now = time.monotonic()
    if _LOCAL_PROBE["url"] == base and now - _LOCAL_PROBE["at"] < 8.0:
        return _LOCAL_PROBE["ok"]
    ok = False
    try:
        req = urllib.request.Request(base + "/api/version",
                                     method="GET")
        with _expert_urlopen(req, timeout=0.7, loopback_only=not bpy.app.online_access) as resp:
            ok = resp.status == 200
    except Exception:
        ok = False
    _LOCAL_PROBE.update(at=now, ok=ok, url=base)
    return ok


def _expert_ready(settings):
    """Can the expert actually be asked right now? A key for key
    services, the Codex program for ChatGPT login, and for a local
    AI: the local AI itself, answering."""
    if not _expert_access_allowed(settings):
        return False
    service = settings.get("service", "KEY")
    if service == "CODEX":
        return _find_codex() is not None
    if service == "LOCAL":
        return _local_alive(settings.get("url"))
    return bool(settings.get("key")) or _is_local_url(settings.get("url"))


def _expert_setup_message(settings):
    if not _expert_access_allowed(settings):
        return _OFFLINE_MESSAGE
    service = settings.get("service", "KEY")
    if service == "CODEX":
        return ("The expert is set to use your ChatGPT login, but Buddy couldn't locate the Codex command-line program. This does not mean the desktop app is missing or that you need to sign in again.")
    if service == "LOCAL":
        return ("The expert is set to a local AI, but nothing is "
                "answering on this computer. Start your local AI "
                "(for example Ollama), then ask again - a local AI "
                "needs no key and no internet, it just has to be "
                "running.")
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


class _ExpertFault(Exception):
    """An expert failure that already knows what it is. The
    transports raise these with a plain kind; _fault_message turns
    the kind into the exact words the user reads. Until this
    existed, every failure - wrong key, rate limit, dead local
    server, missing model, signed-out Codex - collapsed into one
    sentence about checking the setup and being online."""
    def __init__(self, kind, detail=""):
        super().__init__(kind)
        self.kind = kind
        self.detail = detail


def _fault_message(settings, exc):
    """Name the actual fault, in plain words, with the remedy.
    This is the ONLY way an ask failure reaches the user."""
    service = (settings or {}).get("service", "KEY")
    model = (settings or {}).get("model", "") or "the named model"
    if isinstance(exc, _ExpertFault):
        kind, detail = exc.kind, exc.detail
        if kind == "offline":
            return _OFFLINE_MESSAGE
        if kind == "key_refused":
            if service == "CLAUDE":
                return ("Your Claude key was refused by Anthropic "
                        "(the service answered: not accepted). Check "
                        "the key in the expert's setup - a copied key "
                        "with a missing character reads exactly like "
                        "this - then ask again.")
            return ("Your key was refused by the AI service (the "
                    "service answered: not accepted). Check the key "
                    "in the expert's setup - a copied key with a "
                    "missing character reads exactly like this - "
                    "then ask again.")
        if kind == "rate_limited":
            return ("The AI service says too many asks in a row "
                    "(a rate limit). Wait a minute, then ask again "
                    "- nothing is broken.")
        if kind == "model_missing":
            if service == "LOCAL":
                return (f"Your local AI is running, but the model "
                        f"'{model}' isn't downloaded yet, so it "
                        f"can't answer. Download it first (for "
                        f"Ollama: ollama pull {model}), then ask "
                        f"again.")
            return (f"The AI service doesn't know a model called "
                    f"'{model}'. Check the model name in the "
                    f"expert's setup, then ask again.")
        if kind == "unreachable":
            if service == "LOCAL" or _is_local_url(
                    (settings or {}).get("url")):
                return ("Your local AI isn't running - nothing "
                        "answered at its address on this computer. "
                        "Start it (for example Ollama), then ask "
                        "again.")
            return ("Nothing answered at the AI service's address "
                    "- the service may be down, or this computer "
                    "may be offline. Give it a moment, then ask "
                    "again.")
        if kind == "timeout":
            if detail:
                return f"The expert did not finish within {detail} seconds. You can ask again."
            if service == "CODEX":
                return ("Codex didn't finish this request within two "
                        "minutes. You can ask again.")
            if service == "LOCAL" or _is_local_url(
                    (settings or {}).get("url")):
                return ("Your local AI is running, but it didn't "
                        "finish an answer even given several "
                        "minutes. On a computer without a graphics "
                        "card a local model thinks slowly, and "
                        "Buddy describes your scene in detail - "
                        "that combination can simply be slow, not "
                        "broken. A smaller or faster local model "
                        "answers sooner; the key and ChatGPT routes "
                        "answer in seconds.")
            return ("The AI service didn't answer in time - it "
                    "may be busy or this connection may be slow. "
                    "Nothing is wrong with your setup; ask again "
                    "in a moment.")
        if kind == "service_error":
            return (f"The AI service answered with an error "
                    f"(code {detail}). That's the service's side, "
                    f"not your scene - give it a moment, then ask "
                    f"again.")
        if kind == "codex_missing":
            return ("The expert is set to use your ChatGPT login, but Buddy couldn't locate the Codex command-line program. This does not mean the desktop app is missing or that you need to sign in again.")
        if kind == "codex_signed_out":
            return ("The Codex program is on this computer, but "
                    "you're not signed in to it yet. Open Codex "
                    "(there's a button in the expert's setup), sign "
                    "in with your ChatGPT account once, then ask "
                    "again.")
        if kind == "codex_failed":
            tail = f" Its own last words: {detail}" if detail else ""
            return ("The Codex program didn't answer properly."
                    f"{tail} Try once more; if it keeps happening, "
                    "open Codex itself and check it's signed in and "
                    "well.")
        if kind == "empty_reply":
            return ("The expert answered with nothing readable. "
                    "Ask once more - if it repeats, the model name "
                    "in the setup may not be one the service knows.")
    return ("The expert didn't answer - something went wrong that "
            "Buddy can't name yet"
            + (f" ({str(exc)[:70]})" if str(exc) else "")
            + ". Ask once more; if it keeps happening, the setup "
            "in the add-on's preferences shows the ways to connect.")


def _run_cli(argv, timeout=120, include_stderr=False, *, input_text=None):
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
    proc = subprocess.run(argv, input=input_text, capture_output=True,
                          text=True, encoding="utf-8", errors="replace",
                          timeout=timeout, cwd=tempfile.gettempdir())
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip()[-200:]
        raise RuntimeError(tail or "the AI program didn't answer")
    if include_stderr:
        return "\n".join(part for part in (proc.stdout, proc.stderr) if part)
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


def _codex_login_status(path):
    """Ask the Codex program itself whether it's signed in:
    'in', 'out', or 'unknown' (the check itself failed - proceed
    and let the ask speak). Uses the program's own status
    command; Buddy never touches the login itself."""
    try:
        out = _run_cli([path, "login", "status"], timeout=20, include_stderr=True)
    except Exception:
        return "unknown"
    text = (out or "").lower()
    if "not logged in" in text or "not signed in" in text:
        return "out"
    if "logged in" in text or "signed in" in text:
        return "in"
    return "unknown"


def _ask_via_codex(system, user):
    path = _find_codex()
    if not path:
        raise _ExpertFault("codex_missing")
    if _codex_login_status(path) == "out":
        raise _ExpertFault("codex_signed_out")
    # Take the reply from the program's own final-message file,
    # not its whole output: the raw output can carry the agent's
    # working narration, which padded answers and tripped the
    # connection test on a working route.
    fd, outfile = tempfile.mkstemp(prefix="buddy_codex_",
                                   suffix=".txt")
    os.close(fd)
    try:
        out = ""
        try:
            # A full plan's Blender tool list exceeds the Windows command-line limit.
            out = _run_cli([path, "exec", "-s", "read-only",
                            "--skip-git-repo-check",
                            "--output-last-message", outfile, "-"],
                           input_text=f"{system}\n\n{user}")
        except subprocess.TimeoutExpired:
            raise _ExpertFault("timeout") from None
        except RuntimeError as exc:
            tail = str(exc)
            if "not logged in" in tail.lower() or \
                    "sign in" in tail.lower() or "login" in tail.lower():
                raise _ExpertFault("codex_signed_out")
            raise _ExpertFault("codex_failed", tail[-140:])
        text = ""
        try:
            with open(outfile, encoding="utf-8") as fh:
                text = fh.read().strip()
        except OSError:
            text = ""
        if not text:
            text = (out or "").strip()
    finally:
        try:
            os.unlink(outfile)
        except OSError:
            pass
    if not text:
        raise _ExpertFault("empty_reply")
    return text


def _scene_summary(context):
    """What the expert is told about the scene. It used to be
    counts and a mode - not enough to teach against, and nothing
    at all about materials or node trees, which made the headline
    use case (node work) impossible at the first step. Now: names,
    the picked thing's modifiers and material, its tree in brief,
    the renderer, and the current brush values - so relative
    asks ('a bit bigger than now') have something to bite on."""
    objs = list(context.scene.objects)
    counts = {}
    for o in objs:
        counts[o.type] = counts.get(o.type, 0) + 1
    parts = [f"{n} {t.lower()}{'s' if n > 1 else ''}"
             for t, n in sorted(counts.items())]
    names = ", ".join(o.name for o in objs[:10])
    if len(objs) > 10:
        names += f", and {len(objs) - 10} more"
    obj = context.object
    picked = "Nothing picked."
    if obj is not None:
        picked = f"Picked: {obj.name} ({obj.type.lower()})."
        mods = [f"{m.name} ({m.type.lower()})"
                for m in getattr(obj, "modifiers", []) or []]
        if mods:
            picked += f" Its modifiers: {', '.join(mods)}."
        mat = getattr(obj, "active_material", None)
        if mat is not None:
            picked += f" Its material: {mat.name}."
            if mat.use_nodes and mat.node_tree is not None:
                picked += (" Its node tree: "
                           + _tree_digest(mat.node_tree) + ".")
    engine = {"BLENDER_EEVEE_NEXT": "Eevee", "CYCLES": "Cycles"}.get(
        context.scene.render.engine, context.scene.render.engine)
    render = f"Renderer: {engine}"
    if engine == "Cycles":
        render += f", {context.scene.cycles.samples} samples"
    render += "."
    brush = ""
    try:
        b = context.tool_settings.sculpt.brush
        if b is not None:
            brush = (f" Sculpt brush right now: size {b.size}, "
                     f"strength {round(float(b.strength), 2)}, "
                     f"falloff {_get_falloff(b)}.")
    except Exception:
        brush = ""
    checks, current = (tour_state(context)
                       if getattr(context.scene, "buddy_tour_started", False)
                       else (None, None))
    tour = ""
    if checks is not None:
        tour = (f" Guided project: {current} of {len(checks)} steps done"
                + (f", current step: {TOUR_STEPS[current]['title']}."
                   if current < len(checks) else " - finished."))
    return (f"Scene has: {', '.join(parts) or 'nothing'}"
            f"{f' ({names})' if names else ''}. {picked} "
            f"Mode: {context.mode}. {render}{brush}{tour} "
            f"Saved file: {'yes' if bpy.data.filepath else 'not yet'}.")


def _expert_system_prompt():
    buttons = "; ".join(f"{a['id']} = {a['plain']}" for a in _expert_buttons().values())
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


def _expert_buttons():
    stale = _stale_map()
    return {a["id"]: a for a in ACTIONS if a["id"] not in stale
            and not (a["kind"] == "custom" and a["target"] in _EXPERT_MANUAL_ACTIONS)
            and not (a["kind"] == "op" and a["target"] in _REFUSED_TOOLS)}


def _plan_tools():
    return {entry["idname"]: entry for entry in build_index()
            if entry["cat"] in _PLAN_TOOL_CATEGORIES
            and entry["idname"] not in _REFUSED_TOOLS
            and not entry.get("file_operator")}


def _agent_ops_list():
    """The Blender tools the expert may use in a plan: the everyday
    categories, as 'idname = name' lines. Cached. This list IS the
    parser's gate - a plan may only name tools printed here, so
    what the prompt advertises and what the code allows are the
    same set. Session/file categories (wm, screen) are not in it:
    a plan never opens, saves or quits the user's work."""
    global _AGENT_OPS_CACHE
    if _AGENT_OPS_CACHE is not None:
        return _AGENT_OPS_CACHE
    lines = [f"{e['idname']} = {e['label']}"
             for e in _plan_tools().values()]
    _AGENT_OPS_CACHE = "\n".join(lines)
    return _AGENT_OPS_CACHE


def _expert_agent_prompt(context=None):
    buttons = "; ".join(f"{a['id']} = {a['plain']}" for a in _expert_buttons().values())
    stale_settings = _stale_settings()
    settings = "\n".join(
        f"STEP: set:{spec['desc']}"
        for key, spec in SETTINGS.items() if key not in stale_settings)
    stale_styles = _stale_styles()
    styles = "; ".join(f"{k} = {v[0]}" for k, v in STYLES.items()
                       if k not in stale_styles)
    nodes = "; ".join(f"{k} = {v}" for k, v in _NODE_ADD_TYPES.items())
    tree = ""
    if context is not None:
        obj = getattr(context, "object", None)
        mat = getattr(obj, "active_material", None) if obj else None
        if mat is not None and mat.use_nodes and mat.node_tree:
            tree = ("\nThe picked thing's material tree right now "
                    "(node steps and ramp steps work on this tree):\n"
                    + _tree_digest(mat.node_tree, with_values=True))
    return (
        "You are the Buddy Expert, a patient Blender teacher inside "
        "a beginner add-on called Blender Buddy. The user is the "
        "creator and the author of their project; you assist with "
        "bounded tasks they ask for - you never do their whole "
        "project, and you prefer the smallest steps that do exactly "
        "what they asked. For a request to reshape the selected object, keep "
        "that object and prefer a reversible modifier. Replace it only if "
        "the user requests a replacement. Reply with a plan the add-on will run, "
        "step by step, in their Blender - they check it and press "
        "Run themselves. You can press buttons, run Blender tools, "
        "adjust exact settings (like giving them the precise sculpt "
        "brush they describe), apply node-tree styles, wire node "
        "trees, set colour ramps, look up real add-ons, models and "
        "textures, and grow simple ingredients (a low tree, a flat "
        "picture of a thing). Format EXACTLY:\n"
        "SUMMARY: <one plain sentence that teaches what the plan "
        "does and why>\n"
        "STEP: button:<id>   (an add-on button, preferred)\n"
        "STEP: tool:<idname>   (a Blender tool from the list below, "
        "when no button fits)\n"
        "STEP: set:<setting>:<value>   (an exact setting from the "
        "settings list)\n"
        "STEP: style:<style name>   (a node-tree style for the "
        "picked thing)\n"
        "STEP: node:add:<node type>   (add a node to the picked "
        "thing's material tree)\n"
        "STEP: node:set:<node name>:<input name>:<value>   (set an "
        "exact value on a node in the tree below)\n"
        "STEP: node:link:<from node>:<from socket>:<to node>:<to "
        "socket>   (wire two nodes together)\n"
        "STEP: node:remove:<node name>   (remove a node from the "
        "tree)\n"
        "STEP: ramp:<node name>:<position>=<#RRGGBB>;<position>="
        "<#RRGGBB>   (set a colour ramp's stops)\n"
        "STEP: find:<words>   (look up real add-ons, models or "
        "textures for these words)\n"
        "STEP: grow:tree   (grow a simple low tree as an "
        "ingredient)\n"
        "STEP: grow:sprite   (make a flat picture of the picked "
        "thing, to stand in the background)\n"
        "One STEP per line, in the order they must run. Prefer "
        "buttons - they are safe and beginner-shaped. Use at most 8 "
        "steps. Only use ids from the lists below; anything else is "
        "dropped. No other text.\n"
        f"Buttons: {buttons}\n"
        f"Settings you may adjust:\n{settings}\n"
        f"Styles: {styles}\n"
        f"Node types you may add: {nodes}\n"
        f"Tools:\n{_agent_ops_list()}"
        f"{tree}")


def _first_modifier(context, mtype):
    obj = context.object
    if obj is None:
        return None
    for mod in obj.modifiers:
        if mod.type == mtype:
            return mod
    return None


_BUDDY_BRUSH = None


def _sculpt_brush(context):
    """The brush the brush settings land on: the user's current
    sculpt brush whenever one is active (always, in a real
    session). On Blender 5.3 a bare file has NO active brush and
    the slot is read-only from Python (brushes are assets now),
    so Buddy keeps its own brush datablock for that case and the
    set/get pair still agree with each other."""
    global _BUDDY_BRUSH
    ts = context.tool_settings
    brush = ts.sculpt.brush if ts.sculpt else None
    if brush is not None:
        return brush
    if _BUDDY_BRUSH is None or _BUDDY_BRUSH.name not in bpy.data.brushes:
        _BUDDY_BRUSH = bpy.data.brushes.new("Buddy Brush", mode="SCULPT")
    if ts.sculpt:
        try:
            ts.sculpt.brush = _BUDDY_BRUSH
        except Exception:
            pass
    return _BUDDY_BRUSH


# The five falloff shapes, as curve control points. Blender's own
# preset machinery differs per version (curve_preset up to 4.x,
# curve_distance_falloff_preset from 5.x) and in a headless write
# both only RECORD the name without rebuilding the curve - so
# Buddy writes the shape itself, into whichever curve the running
# Blender actually uses, and reads the shape back from the curve.
_FALLOFF_PROFILES = {
    "SMOOTH": [(0.0, 1.0), (0.25, 0.84), (0.5, 0.5), (0.75, 0.16),
               (1.0, 0.0)],
    "SPHERE": [(0.0, 1.0), (0.25, 0.97), (0.5, 0.87), (0.75, 0.66),
               (1.0, 0.0)],
    "SHARP": [(0.0, 1.0), (0.2, 0.5), (0.4, 0.13), (1.0, 0.0)],
    "LIN": [(0.0, 1.0), (1.0, 0.0)],
    "CONSTANT": [(0.0, 1.0), (0.9, 1.0), (1.0, 0.0)],
}


def _brush_falloff_curve(brush):
    for attr in ("curve_distance_falloff", "curve"):
        cm = getattr(brush, attr, None)
        if cm is not None:
            return cm
    return None


def _write_curve_profile(cm, profile):
    curve = cm.curves[0]
    pts = curve.points
    while len(pts) > len(profile):
        pts.remove(pts[len(pts) // 2])
    while len(pts) < len(profile):
        pts.new(0.5, 0.5)
    for point, (x, y) in zip(pts, profile):
        point.location = (x, y)
    cm.update()


def _profile_samples(profile, xs):
    out = []
    for x in xs:
        y = profile[-1][1]
        for (x0, y0), (x1, y1) in zip(profile, profile[1:]):
            if x0 <= x <= x1:
                t = 0.0 if x1 == x0 else (x - x0) / (x1 - x0)
                y = y0 + t * (y1 - y0)
                break
        out.append(y)
    return out


def _classify_falloff(cm):
    """Name the falloff shape a curve actually has, by sampling
    it against the five profiles. Used when Blender's own preset
    name says CUSTOM (a hand-edited curve)."""
    curve = cm.curves[0]
    xs = [i / 10 for i in range(1, 10)]
    try:
        got = [cm.evaluate(curve, x) for x in xs]
    except Exception:
        return "SMOOTH"
    best, best_d = "SMOOTH", None
    for name, profile in _FALLOFF_PROFILES.items():
        want = _profile_samples(profile, xs)
        d = sum(abs(a - b) for a, b in zip(got, want))
        if best_d is None or d < best_d:
            best, best_d = name, d
    return best


def _set_falloff(brush, preset):
    cm = _brush_falloff_curve(brush)
    if cm is not None:
        _write_curve_profile(cm, _FALLOFF_PROFILES[preset])
    props = brush.bl_rna.properties
    if "curve_preset" in props:
        brush.curve_preset = preset
    elif "curve_distance_falloff_preset" in props:
        brush.curve_distance_falloff_preset = preset


def _get_falloff(brush):
    props = brush.bl_rna.properties
    if "curve_preset" in props:
        return brush.curve_preset
    if "curve_distance_falloff_preset" in props:
        value = brush.curve_distance_falloff_preset
        if value in _FALLOFF_PROFILES:
            return value
    cm = _brush_falloff_curve(brush)
    if cm is None:
        return "SMOOTH"
    return _classify_falloff(cm)


def _falloff_alive():
    props = bpy.types.Brush.bl_rna.properties
    return "curve_preset" in props or "curve_distance_falloff" in props


def _need_modifier(context, mtype, plain):
    mod = _first_modifier(context, mtype)
    if mod is None:
        raise RuntimeError(f"the picked thing has no {plain} yet - "
                           "add one first, then set it")
    return mod


def _set_camera_focal(c, v):
    """Buddy's own pattern: help instead of fail. A scene with no
    camera gets one, then the lens is set."""
    cam = c.scene.camera
    if cam is None:
        data = bpy.data.cameras.new("Buddy Camera")
        cam = bpy.data.objects.new("Buddy Camera", data)
        c.scene.collection.objects.link(cam)
        c.scene.camera = cam
    cam.data.lens = float(v)


def _get_camera_focal(c):
    if c.scene.camera is None:
        raise RuntimeError("the scene has no camera yet")
    return c.scene.camera.data.lens


def _picked_not_light(c):
    obj = c.object
    if obj is None:
        return "nothing is picked"
    return f"the picked thing is '{obj.name}' (a {obj.type.lower()})"


def _set_light_energy(c, v):
    obj = c.object
    if obj is None or obj.type != "LIGHT":
        raise RuntimeError(f"{_picked_not_light(c)}, not a light - "
                           "pick a light first, then set its strength")
    obj.data.energy = float(v)


def _get_light_energy(c):
    obj = c.object
    if obj is None or obj.type != "LIGHT":
        raise RuntimeError(f"{_picked_not_light(c)}, not a light")
    return obj.data.energy


def _rna_has(type_name, prop):
    t = getattr(bpy.types, type_name, None)
    return t is not None and prop in t.bl_rna.properties


def _cycles_samples_alive():
    """Probe render.samples against the LIVE scene's Cycles
    settings, not bpy.types: on Blender 5.3 the CyclesRenderSettings
    type exists and works on the scene but is no longer reachable
    as bpy.types.CyclesRenderSettings, so the type-name probe
    reported a live setting dead (found by the 5.3 suite run,
    2026-11-13). An instance can't lie about its own properties."""
    try:
        return "samples" in bpy.context.scene.cycles.bl_rna.properties
    except Exception:
        return True


def _light_energy_alive():
    """Probe light.energy instance-first (bpy.types lookups are
    not guaranteed across versions) - read-only either way: this
    can be called while a panel is drawing, so it must never
    create or remove data. With no instance to ask and no type
    to check, the answer is alive: never hide on a guess."""
    if _rna_has("Light", "energy"):
        return True
    for light in bpy.data.lights:
        try:
            return "energy" in light.bl_rna.properties
        except Exception:
            return True
    return True


# Settings the agent may adjust directly - the "give me the exact
# brush" layer. Each has a plain description (which is also what the
# AI sees), a setter, and a reader so a run step can verify its own
# work landed. "range" is the contract the description promises -
# enforced when a step is parsed, not just described. "probe" is
# how the anti-stale guard checks the setting still exists in the
# running Blender, the same discipline ACTIONS already had.
SETTINGS = {
    "brush.size": {
        "label": "Sculpt brush size",
        "desc": "brush.size:<pixels 1-500> - the sculpt brush's size",
        "set": lambda c, v: setattr(_sculpt_brush(c), "size", int(v)),
        "get": lambda c: _sculpt_brush(c).size,
        "range": (1, 500), "probe": ("Brush", "size"),
    },
    "brush.strength": {
        "label": "Sculpt brush strength",
        "desc": "brush.strength:<0-1> - how hard the sculpt brush pushes",
        "set": lambda c, v: setattr(_sculpt_brush(c), "strength", float(v)),
        "get": lambda c: _sculpt_brush(c).strength,
        "range": (0.0, 1.0), "probe": ("Brush", "strength"),
    },
    "brush.falloff": {
        "label": "Sculpt brush falloff",
        "desc": "brush.falloff:<SMOOTH|SPHERE|SHARP|LIN|CONSTANT> - "
                "the shape of the sculpt brush's edge",
        "set": lambda c, v: _set_falloff(_sculpt_brush(c), str(v)),
        "get": lambda c: _get_falloff(_sculpt_brush(c)),
        "probe": _falloff_alive,
    },
    "bevel.width": {
        "label": "Edge rounding width",
        "desc": "bevel.width:<0-1> - width of the picked thing's bevel "
                "(needs a bevel on it first, e.g. from 'Round off a "
                "sharp edge')",
        "set": lambda c, v: setattr(
            _need_modifier(c, "BEVEL", "bevel"), "width", float(v)),
        "get": lambda c: _need_modifier(c, "BEVEL", "bevel").width,
        "range": (0.0, 1.0), "probe": ("BevelModifier", "width"),
    },
    "bevel.segments": {
        "label": "Edge rounding smoothness",
        "desc": "bevel.segments:<1-10> - segments of the bevel",
        "set": lambda c, v: setattr(
            _need_modifier(c, "BEVEL", "bevel"), "segments", int(v)),
        "get": lambda c: _need_modifier(c, "BEVEL", "bevel").segments,
        "range": (1, 10), "probe": ("BevelModifier", "segments"),
    },
    "subdivision.levels": {
        "label": "Smoothness levels",
        "desc": "subdivision.levels:<0-6> - the picked thing's "
                "subdivision (needs one first, e.g. 'Make it smoother "
                "& rounder')",
        "set": lambda c, v: setattr(
            _need_modifier(c, "SUBSURF", "subdivision"), "levels", int(v)),
        "get": lambda c: _need_modifier(c, "SUBSURF", "subdivision").levels,
        "range": (0, 6), "probe": ("SubsurfModifier", "levels"),
    },
    "solidify.thickness": {
        "label": "Shell thickness",
        "desc": "solidify.thickness:<0-1> - the picked thing's "
                "solidify thickness (needs one first)",
        "set": lambda c, v: setattr(
            _need_modifier(c, "SOLIDIFY", "solidify"), "thickness", float(v)),
        "get": lambda c: _need_modifier(c, "SOLIDIFY", "solidify").thickness,
        "range": (0.0, 1.0), "probe": ("SolidifyModifier", "thickness"),
    },
    "array.count": {
        "label": "Copies in a row",
        "desc": "array.count:<1-50> - copies in the picked thing's "
                "array (needs one first, e.g. 'Make a row of copies')",
        "set": lambda c, v: setattr(
            _need_modifier(c, "ARRAY", "array"), "count", int(v)),
        "get": lambda c: _need_modifier(c, "ARRAY", "array").count,
        "range": (1, 50), "probe": ("ArrayModifier", "count"),
    },
    "render.samples": {
        "label": "Picture quality (Cycles samples)",
        "desc": "render.samples:<1-4096> - more samples = a cleaner "
                "picture that takes longer (counts when the scene "
                "renders in Cycles)",
        "set": lambda c, v: setattr(c.scene.cycles, "samples", int(v)),
        "get": lambda c: c.scene.cycles.samples,
        "range": (1, 4096), "probe": _cycles_samples_alive,
    },
    "light.energy": {
        "label": "Picked light brightness",
        "desc": "light.energy:<number> - the picked light's strength "
                "(the picked thing must be a light)",
        "set": _set_light_energy,
        "get": _get_light_energy,
        "range": (0.0, 10000.0), "probe": _light_energy_alive,
    },
    "camera.focal": {
        "label": "Camera zoom (lens mm)",
        "desc": "camera.focal:<10-200> - the scene camera's lens "
                "(adds a camera first if the scene has none)",
        "set": _set_camera_focal,
        "get": _get_camera_focal,
        "range": (10.0, 200.0), "probe": ("Camera", "lens"),
    },
}


_STALE_SETTINGS_CACHE = None


def _stale_settings():
    """SETTINGS whose backing property no longer exists in the
    running Blender - the same self-check ACTIONS get, extended
    to the registry that shipped a dead brush.falloff on 5.3
    unnoticed. A check that cannot be made counts as alive:
    Buddy never hides a tool on a guess."""
    global _STALE_SETTINGS_CACHE
    if _STALE_SETTINGS_CACHE is not None:
        return _STALE_SETTINGS_CACHE
    stale = set()
    for key, spec in SETTINGS.items():
        probe = spec.get("probe")
        if probe is None:
            continue
        try:
            alive = probe() if callable(probe) else _rna_has(*probe)
        except Exception:
            alive = True
        if not alive:
            stale.add(key)
    _STALE_SETTINGS_CACHE = stale
    return stale


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
    """The Principled node, found by TYPE - the old code looked
    it up by its English name, which failed on renamed nodes and
    non-English Blender interfaces on trees that plainly had one."""
    for node in mat.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            return node
    raise RuntimeError("the material has no Principled node to "
                       "style - it may be a special material "
                       "Buddy doesn't style")


def _buddy_node(tree, style_key, bl_idname, plain):
    """A node Buddy adds for a style, under a name that says so -
    so a style run twice replaces its own nodes instead of
    stacking a second chain on the tree."""
    name = f"Buddy {style_key} {plain}"
    old = tree.nodes.get(name)
    if old is not None:
        tree.nodes.remove(old)
    node = tree.nodes.new(bl_idname)
    node.name = name
    node.label = f"Buddy style: {style_key}"
    return node


def _base_colour_free(bsdf):
    return not bsdf.inputs["Base Color"].links


def _style_chrome(obj):
    bsdf = _bsdf(_style_material(obj))
    if _base_colour_free(bsdf):
        bsdf.inputs["Base Color"].default_value = (0.9, 0.9, 0.92, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.08


def _style_brushed_metal(obj):
    mat = _style_material(obj)
    bsdf = _bsdf(mat)
    if _base_colour_free(bsdf):
        bsdf.inputs["Base Color"].default_value = (0.75, 0.75, 0.78, 1.0)
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.35
    tree = mat.node_tree
    noise = _buddy_node(tree, "brushed_metal", "ShaderNodeTexNoise",
                        "Noise")
    noise.inputs["Scale"].default_value = 150.0
    bump = _buddy_node(tree, "brushed_metal", "ShaderNodeBump", "Bump")
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
    noise = _buddy_node(tree, "wood", "ShaderNodeTexNoise", "Noise")
    noise.inputs["Scale"].default_value = 3.0
    noise.inputs["Detail"].default_value = 6.0
    ramp = _buddy_node(tree, "wood", "ShaderNodeValToRGB", "Ramp")
    ramp.color_ramp.elements[0].color = (0.25, 0.12, 0.04, 1.0)
    ramp.color_ramp.elements[1].color = (0.55, 0.33, 0.14, 1.0)
    bump = _buddy_node(tree, "wood", "ShaderNodeBump", "Bump")
    bump.inputs["Strength"].default_value = 0.3
    tree.links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    if _base_colour_free(bsdf):
        tree.links.new(ramp.outputs["Color"],
                       bsdf.inputs["Base Color"])
    tree.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    tree.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.55


def _style_marble(obj):
    mat = _style_material(obj)
    bsdf = _bsdf(mat)
    tree = mat.node_tree
    vor = _buddy_node(tree, "marble", "ShaderNodeTexVoronoi", "Voronoi")
    vor.inputs["Scale"].default_value = 4.0
    ramp = _buddy_node(tree, "marble", "ShaderNodeValToRGB", "Ramp")
    ramp.color_ramp.elements[0].color = (0.85, 0.85, 0.87, 1.0)
    ramp.color_ramp.elements[1].color = (0.35, 0.35, 0.40, 1.0)
    tree.links.new(vor.outputs["Distance"], ramp.inputs["Fac"])
    if _base_colour_free(bsdf):
        tree.links.new(ramp.outputs["Color"],
                       bsdf.inputs["Base Color"])
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


def _apply_style(key, obj):
    """Apply a style READ-BEFORE-WRITE: the tree is digested
    before and after, and the caller is told honestly whether
    anything changed and what couldn't land. Until this existed,
    a style step reported 'Done' unconditionally - including on
    textured materials where several styles were silent no-ops,
    the whole product's one rule (the scene proves it) broken by
    the Expert itself."""
    mat = _style_material(obj)
    tree = mat.node_tree
    bsdf = _bsdf(mat)
    linked = not _base_colour_free(bsdf)
    before = _tree_digest(tree, with_values=True)
    STYLES[key][1](obj)
    after = _tree_digest(tree, with_values=True)
    changed = before != after
    note = ""
    if linked and changed:
        note = ("Your texture still drives the base colour - the "
                "style landed around it (surface values and any "
                "grain), not over it.")
    elif linked and not changed:
        note = ("the style changed nothing - your texture drives "
                "the base colour and the rest of this style had "
                "nothing to take hold of")
    elif not changed:
        note = "the style changed nothing in the tree"
    return changed, note


_STALE_STYLES_CACHE = None


def _stale_styles():
    """STYLES that cannot run on this Blender at all, proven by
    dry-running each on a scratch material - the settings/styles
    half of the anti-stale guard. Anything the probe can't judge
    counts as alive."""
    global _STALE_STYLES_CACHE
    if _STALE_STYLES_CACHE is not None:
        return _STALE_STYLES_CACHE
    stale = set()
    before = {m.name for m in bpy.data.materials}
    probe_obj = None
    try:
        mesh = bpy.data.meshes.new("Buddy Style Probe")
        probe_obj = bpy.data.objects.new("Buddy Style Probe", mesh)
        for key in STYLES:
            try:
                _apply_style(key, probe_obj)
            except Exception:
                stale.add(key)
    except Exception:
        stale = set()
    finally:
        if probe_obj is not None:
            mesh = probe_obj.data
            bpy.data.objects.remove(probe_obj)
            try:
                bpy.data.meshes.remove(mesh)
            except Exception:
                pass
        for mat in list(bpy.data.materials):
            if mat.name not in before:
                try:
                    bpy.data.materials.remove(mat)
                except Exception:
                    pass
    _STALE_STYLES_CACHE = stale
    return stale


# ---------------------------------------------------------------------
# Node work - the headline capability (owner: "nodes themselves,
# natural language prompting of tedious shit"). The machinery the
# audit found absent in kind: the tree is SERIALIZED into what the
# expert sees, node steps EDIT the named tree, and every step is
# verified by reading the tree back. The tree is the proof, as the
# scene is for the guided projects.
# ---------------------------------------------------------------------

_NODE_ADD_TYPES = {
    "ShaderNodeTexNoise": "Noise Texture",
    "ShaderNodeTexVoronoi": "Voronoi Texture",
    "ShaderNodeTexWave": "Wave Texture",
    "ShaderNodeTexGradient": "Gradient Texture",
    "ShaderNodeTexBrick": "Brick Texture",
    "ShaderNodeTexChecker": "Checker Texture",
    "ShaderNodeTexImage": "Image Texture",
    "ShaderNodeValToRGB": "Colour Ramp",
    "ShaderNodeBump": "Bump",
    "ShaderNodeNormalMap": "Normal Map",
    "ShaderNodeDisplacement": "Displacement",
    "ShaderNodeMix": "Mix",
    "ShaderNodeMath": "Math",
    "ShaderNodeVectorMath": "Vector Math",
    "ShaderNodeMapping": "Mapping",
    "ShaderNodeTexCoord": "Texture Coordinate",
    "ShaderNodeRGB": "RGB Colour",
    "ShaderNodeValue": "Value",
    "ShaderNodeHueSaturation": "Hue Saturation",
    "ShaderNodeInvert": "Invert Colour",
    "ShaderNodeGamma": "Gamma",
    "ShaderNodeBrightContrast": "Bright Contrast",
    "ShaderNodeFresnel": "Fresnel",
    "ShaderNodeLayerWeight": "Layer Weight",
    "ShaderNodeSeparateXYZ": "Separate XYZ",
    "ShaderNodeCombineXYZ": "Combine XYZ",
    "ShaderNodeRGBToBW": "RGB to BW",
}

# Tools a plan may never name, whatever the categories say:
# session and file machinery (a plan never opens, saves, undoes
# or quits the user's work) and outright deletion.
_PLAN_TOOL_CATEGORIES = {"mesh", "object", "view3d", "render", "scene",
                         "transform", "curve", "surface", "armature", "material"}
_REFUSED_TOOLS = {"object.delete", "scene.delete",
                  "object.multires_external_save", "scene.freestyle_module_open",
                  "object.simulation_nodes_cache_delete", "object.geometry_node_bake_delete_single",
                  "object.geometry_node_bake_pack_single", "object.geometry_node_bake_unpack_single",
                  "object.multires_external_pack", "object.collection_external_asset_drop"}
# These shortcuts remain available for a user's direct button press. Their
# implementations delete entire objects or write to user-visible output files.
_EXPERT_MANUAL_ACTIONS = {"delete_object", "save_work", "export_glb", "export_stl",
                          "export_obj", "render_picture"}


def _fmt_value(v):
    if isinstance(v, bool):
        return "on" if v else "off"
    if isinstance(v, (int, float)):
        return f"{float(v):.3g}"
    try:
        seq = list(v)
    except TypeError:
        return str(v)[:24]
    if len(seq) in (3, 4) and all(
            isinstance(x, (int, float)) for x in seq):
        return "(" + ", ".join(f"{float(x):.2f}" for x in seq) + ")"
    return str(v)[:24]


def _tree_digest(tree, with_values=False):
    """A bounded, exact description of a node tree: node names
    and types, key input values, and every link. This is what the
    expert sees, and what style/node verification diffs."""
    if tree is None:
        return "no tree"
    parts = []
    for node in list(tree.nodes)[:60]:
        line = f"{node.name} [{node.bl_idname}]"
        if with_values:
            shown = []
            for sock in node.inputs:
                if sock.links or not hasattr(sock, "default_value"):
                    continue
                shown.append(f"{sock.name}={_fmt_value(sock.default_value)}")
                if len(shown) >= 6:
                    break
            if shown:
                line += " " + ", ".join(shown)
        parts.append(line)
    links = [f"{l.from_node.name}.{l.from_socket.name} -> "
             f"{l.to_node.name}.{l.to_socket.name}"
             for l in tree.links]
    out = "; ".join(parts)
    if links:
        out += " | links: " + "; ".join(links[:40])
    return out


def _find_node(tree, name):
    node = tree.nodes.get(name)
    if node is not None:
        return node
    low = (name or "").lower()
    hits = [n for n in tree.nodes if n.name.lower() == low]
    if len(hits) == 1:
        return hits[0]
    hits = [n for n in tree.nodes if n.name.lower().startswith(low)]
    return hits[0] if len(hits) == 1 else None


def _find_socket(sockets, name):
    for s in sockets:
        if s.name == name:
            return s
    low = (name or "").lower()
    for s in sockets:
        if s.name.lower() == low:
            return s
    return None


def _active_tree(context):
    obj = context.object
    if obj is None:
        raise RuntimeError("pick the thing whose material tree "
                           "to work on first")
    mat = getattr(obj, "active_material", None)
    if mat is None:
        mat = _style_material(obj)
    mat.use_nodes = True
    if mat.node_tree is None:
        raise RuntimeError(f"'{obj.name}'s material has no node "
                           "tree to work on")
    return mat.node_tree


def _coerce_node_value(sock, raw):
    """Turn a plan's text value into the socket's own type."""
    t = sock.type
    raw = str(raw).strip()
    if t == "VALUE":
        return float(raw)
    if t == "INT":
        return int(float(raw))
    if t == "BOOLEAN":
        return raw.lower() in ("true", "1", "yes", "on")
    if t in ("RGBA", "VECTOR"):
        if raw.startswith("#") and len(raw) == 7:
            vals = [int(raw[i:i + 2], 16) / 255.0 for i in (1, 3, 5)]
        else:
            vals = [float(p) for p in raw.split(",")]
        if t == "RGBA" and len(vals) == 3:
            vals.append(1.0)
        return vals
    return raw


def _values_match(got, want):
    try:
        return abs(float(got) - float(want)) < 1e-4
    except (TypeError, ValueError):
        pass
    try:
        g, w = list(got), list(want)
        return len(g) == len(w) and all(
            abs(float(a) - float(b)) < 1e-3 for a, b in zip(g, w))
    except (TypeError, ValueError):
        return str(got) == str(want)


def _exec_node_step(context, step):
    """Run one node step against the picked thing's material
    tree and verify it by reading the tree back.
    Returns (ok, note, fail_why)."""
    tree = _active_tree(context)
    op = step["op"]
    if op == "add":
        bl_idname = step["type"]
        node = tree.nodes.new(bl_idname)
        return True, f"Added the node '{node.name}'.", ""
    if op == "remove":
        node = _find_node(tree, step["node"])
        if node is None:
            return False, "", (f"there's no node called "
                               f"'{step['node']}' in this tree")
        name = node.name
        tree.nodes.remove(node)
        if _find_node(tree, name) is not None:
            return False, "", "the node is still there"
        return True, f"Removed the node '{name}'.", ""
    if op == "set":
        node = _find_node(tree, step["node"])
        if node is None:
            return False, "", (f"there's no node called "
                               f"'{step['node']}' in this tree")
        sock = _find_socket(node.inputs, step["input"])
        if sock is None:
            return False, "", (f"'{node.name}' has no input called "
                               f"'{step['input']}'")
        if sock.links:
            src = sock.links[0].from_node.name
            return False, "", (f"'{node.name}'s {sock.name} is wired "
                               f"from '{src}' - a wired input has no "
                               "set value; change it at the other end")
        if not hasattr(sock, "default_value"):
            return False, "", (f"'{node.name}'s {sock.name} can't be "
                               "set to a value")
        try:
            value = _coerce_node_value(sock, step["value"])
        except (TypeError, ValueError):
            return False, "", (f"'{step['value']}' isn't a value "
                               f"'{node.name}'s {sock.name} can take")
        sock.default_value = value
        if not _values_match(sock.default_value, value):
            return False, "", (f"the value didn't land - it reads "
                               f"back as {_fmt_value(sock.default_value)}")
        return True, (f"Set '{node.name}' {sock.name} to "
                      f"{step['value']} - read back from the tree."), ""
    if op == "link":
        src = _find_node(tree, step["from"])
        dst = _find_node(tree, step["to"])
        if src is None or dst is None:
            missing = step["from"] if src is None else step["to"]
            return False, "", f"there's no node called '{missing}' in this tree"
        out_sock = _find_socket(src.outputs, step["from_socket"])
        in_sock = _find_socket(dst.inputs, step["to_socket"])
        if out_sock is None:
            return False, "", (f"'{src.name}' has no output called "
                               f"'{step['from_socket']}'")
        if in_sock is None:
            return False, "", (f"'{dst.name}' has no input called "
                               f"'{step['to_socket']}'")
        if in_sock.links:
            other = in_sock.links[0].from_node.name
            return False, "", (f"'{dst.name}'s {in_sock.name} is "
                               f"already wired from '{other}'")
        tree.links.new(out_sock, in_sock)
        landed = any(l.from_node == src and l.to_node == dst
                     and l.from_socket == out_sock
                     and l.to_socket == in_sock for l in tree.links)
        if not landed:
            return False, "", "the wire didn't take"
        return True, (f"Wired '{src.name}' {out_sock.name} into "
                      f"'{dst.name}' {in_sock.name}."), ""
    return False, "", "unknown node step"


def _exec_ramp_step(context, step):
    """Set a colour ramp's stops from a description, then read
    them back from the tree (the colour-mapping ingredient)."""
    tree = _active_tree(context)
    node = _find_node(tree, step["node"])
    if node is None:
        node = tree.nodes.new("ShaderNodeValToRGB")
        node.name = step["node"]
        created = True
    else:
        created = False
    if node.bl_idname != "ShaderNodeValToRGB":
        return False, "", (f"'{step['node']}' is a "
                           f"{node.bl_idname}, not a colour ramp")
    stops = sorted(step["stops"], key=lambda s: s[0])
    ramp = node.color_ramp
    while len(ramp.elements) > len(stops):
        ramp.elements.remove(ramp.elements[-1])
    while len(ramp.elements) < len(stops):
        ramp.elements.new(0.5)
    for el, (pos, colour) in zip(ramp.elements, stops):
        el.position = pos
        el.color = colour
    for el, (pos, colour) in zip(ramp.elements, stops):
        if abs(el.position - pos) > 0.02 or not _values_match(
                el.color, colour):
            return False, "", "the ramp stops didn't land as described"
    words = ", ".join(f"{int(pos * 100)}% {_fmt_value(colour)}"
                      for pos, colour in stops)
    return True, (f"{'Added' if created else 'Set'} the colour ramp "
                  f"'{node.name}': {words} - read back from the "
                  f"tree."), ""


# ---------------------------------------------------------------------
# Ingredients: real resources (links checked before they're
# shown) and generated set-dressing (a low tree, a flat picture).
# The expert fetches or builds the ingredient; the creator picks,
# places and judges. Invented listings are the failure mode -
# every result below was verified to resolve before it is shown.
# ---------------------------------------------------------------------

_RESOURCE_CACHE = {}


def _fetch_json(url, timeout=10):
    req = urllib.request.Request(
        url, headers={"User-Agent": "BlenderBuddy/3.2"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _verify_url(url, timeout=6):
    try:
        req = urllib.request.Request(
            url, headers={"User-Agent": "BlenderBuddy/3.2"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read(256)
            return resp.status == 200
    except Exception:
        return False


def _find_resources(words):
    """Named, real results whose links resolve - checked now,
    not promised. Sources: the Blender Extensions catalogue and
    Poly Haven's public asset index."""
    if not bpy.app.online_access:
        raise RuntimeError("Resource lookup needs Blender's online access. No websites were contacted.")
    results = []
    ext_url = ("https://extensions.blender.org/search/?q="
               + urllib.parse.quote(words))
    if _verify_url(ext_url):
        results.append({
            "name": f"Add-ons matching '{words}'",
            "url": ext_url, "source": "Blender Extensions"})
    try:
        assets = _RESOURCE_CACHE.get("polyhaven")
        if assets is None:
            assets = _fetch_json(
                "https://api.polyhaven.com/assets"
                "?t=models,textures,hdris")
            _RESOURCE_CACHE["polyhaven"] = assets
        tokens = [t for t in re.split(r"\W+", words.lower())
                  if len(t) > 2]
        hits = []
        for aid, info in (assets or {}).items():
            name = str(info.get("name") or aid)
            hay = (name + " " + aid.replace("_", " ")).lower()
            if tokens and all(t in hay for t in tokens[:2]):
                hits.append((aid, name))
        for aid, name in hits[:3]:
            url = f"https://polyhaven.com/a/{aid}"
            if _verify_url(url):
                results.append({"name": name, "url": url,
                                "source": "Poly Haven"})
    except Exception:
        pass
    return results[:5]


def _grow_tree(context):
    """A simple low tree, grown from Blender's own mesh machinery:
    a tapered trunk, branches, and a three-blob canopy, standing
    at the scene target. An ingredient - the creator places and
    art-directs it. Returns the object names."""
    import bmesh
    from mathutils import Matrix, Vector
    cursor = Vector(context.scene.cursor.location)
    made = []

    def _obj(name, bm, matrix, mat_name, rgba, rough):
        nonlocal_mesh = bpy.data.meshes.new(name)
        bm.to_mesh(nonlocal_mesh)
        bm.free()
        obj = bpy.data.objects.new(name, nonlocal_mesh)
        obj.matrix_world = matrix
        context.scene.collection.objects.link(obj)
        _paint(obj, mat_name, rgba, roughness=rough)
        made.append(obj.name)
        return obj

    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=7, radius1=0.16,
                          radius2=0.05, depth=2.0)
    _obj("Buddy Tree Trunk", bm,
         Matrix.Translation(cursor + Vector((0, 0, 1.0))),
         "Buddy Bark", (0.23, 0.14, 0.08, 1.0), 0.9)
    for i, (dx, dy, tilt) in enumerate(((0.4, 0.1, 0.7),
                                        (-0.35, 0.25, -0.6),
                                        (0.05, -0.4, 0.5))):
        bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=5,
                              radius1=0.05, radius2=0.015, depth=0.9)
        m = (Matrix.Translation(cursor + Vector((dx, dy, 2.1)))
             @ Matrix.Rotation(tilt, 4, "Y")
             @ Matrix.Rotation(tilt * 0.6, 4, "X")
             @ Matrix.Translation(Vector((0, 0, 0.45))))
        _obj(f"Buddy Tree Branch {i + 1}", bm, m,
             "Buddy Bark", (0.23, 0.14, 0.08, 1.0), 0.9)
    bm = bmesh.new()
    for dx, dy, dz, s in ((0, 0, 3.1, 1.0), (0.55, 0.2, 2.75, 0.7),
                          (-0.5, -0.25, 2.8, 0.75)):
        bmesh.ops.create_icosphere(
            bm, subdivisions=1, radius=0.85,
            matrix=Matrix.Translation(Vector((dx, dy, dz)))
            @ Matrix.Scale(s, 4) @ Matrix.Scale(0.8, 4, Vector((0, 0, 1))))
    _obj("Buddy Tree Leaves", bm, Matrix.Translation(cursor),
         "Buddy Leaves", (0.16, 0.36, 0.12, 1.0), 0.85)
    return made


def _grow_sprite(context):
    """A flat picture of the picked thing (a billboard sprite):
    render it alone with transparency, then stand the picture on
    a plane. Returns the plane's name."""
    obj = context.object
    if obj is None or obj.type != "MESH":
        raise RuntimeError("pick a shape first - a sprite is a "
                           "picture of the picked thing")
    scene = context.scene
    render = scene.render
    keep = {
        "filepath": render.filepath,
        "format": render.image_settings.file_format,
        "transparent": render.film_transparent,
        "engine": render.engine,
        "res": (render.resolution_x, render.resolution_y,
                render.resolution_percentage),
        "samples": scene.cycles.samples if hasattr(scene, "cycles")
                   else None,
        "hidden": {o.name: o.hide_render for o in scene.objects},
    }
    path = os.path.join(tempfile.gettempdir(),
                        f"buddy_sprite_{obj.name}.png")
    try:
        for o in scene.objects:
            o.hide_render = o is not obj
        render.engine = "CYCLES"
        if keep["samples"] is not None:
            scene.cycles.samples = 16
        render.resolution_x = render.resolution_y = 128
        render.resolution_percentage = 100
        render.film_transparent = True
        render.image_settings.file_format = "PNG"
        render.filepath = path
        bpy.ops.render.render(write_still=True)
    finally:
        render.filepath = keep["filepath"]
        render.image_settings.file_format = keep["format"]
        render.film_transparent = keep["transparent"]
        render.engine = keep["engine"]
        render.resolution_x, render.resolution_y, \
            render.resolution_percentage = keep["res"]
        if keep["samples"] is not None:
            scene.cycles.samples = keep["samples"]
        for o in scene.objects:
            if o.name in keep["hidden"]:
                o.hide_render = keep["hidden"][o.name]
    if not os.path.isfile(path) or os.path.getsize(path) == 0:
        raise RuntimeError("the picture of it didn't render")
    img = bpy.data.images.load(path)
    width = max(obj.dimensions.x, obj.dimensions.y, 0.5)
    height = max(obj.dimensions.z, 0.5)
    bpy.ops.mesh.primitive_plane_add(size=1.0)
    plane = context.object
    plane.name = f"Buddy Sprite of {obj.name}"
    plane.dimensions = (width, height, 0.0)
    plane.location = (scene.cursor.location.x,
                      scene.cursor.location.y,
                      scene.cursor.location.z + height / 2.0)
    mat = bpy.data.materials.new(f"Buddy Sprite {obj.name}")
    mat.use_nodes = True
    tree = mat.node_tree
    tree.nodes.clear()
    out = tree.nodes.new("ShaderNodeOutputMaterial")
    bsdf = tree.nodes.new("ShaderNodeBsdfPrincipled")
    tex = tree.nodes.new("ShaderNodeTexImage")
    tex.image = img
    tree.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    tree.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
    tree.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    plane.data.materials.append(mat)
    return plane.name


# ---------------------------------------------------------------------
# Capability questions are answered by Buddy itself, from the
# real registries - no AI connection, no setup. The first
# question a person asks must never dead-end on setup (owner's
# live proof: "what can you do for me" met a connection error).
# ---------------------------------------------------------------------

_CAPABILITY_PHRASES = (
    "what can you do", "what do you do", "what can i ask",
    "what are you able to do", "what can the expert do",
    "what help can you give", "your capabilities",
    "what can buddy do", "what does buddy do",
)


def _is_capability_question(question):
    q = " ".join((question or "").lower().split()).strip(" ?!.")
    if q in ("help", "help me"):
        return True
    return any(p in q for p in _CAPABILITY_PHRASES)


def _capability_answer(context):
    available = _available_actions(context)
    sample = ", ".join(a["plain"] for a in available[:6])
    settings = [spec["label"].lower() for key, spec in
                SETTINGS.items() if key not in _stale_settings()]
    styles = [desc for key, (desc, _fn) in STYLES.items()
              if key not in _stale_styles()]
    projects = ", ".join(p["name"] for p in PACKAGES)
    return (
        "Plenty - and this answer needed no connection at all. "
        f"Right now your scene can use {len(available)} of my "
        f"plain-words tools (things like: {sample}). Ask me in "
        "your own words and I can explain any step for YOUR scene, "
        "and - with task help on - draft steps you check and run "
        "yourself: press tools for you, set exact values "
        f"({', '.join(settings[:5])} and more), wire node trees "
        "(add a node, set its value, join sockets), set a colour "
        f"ramp from a description, apply a style ({', '.join(styles[:4])} "
        "and more), look up real add-ons, models and textures "
        "(I check every link before I show it), and grow simple "
        "ingredients - a low tree, or a flat picture of a thing "
        f"for the background. I can also walk you through guided "
        f"projects: {projects}. You stay the author throughout - "
        "I assist with the task in front of you.")


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
    raise ValueError. A plan step is only kept when this succeeds.
    The documented range is part of the contract: a value outside
    it is dropped here, not landed (Blender's own ranges are
    wider than the promised ones - brush strength reads back fine
    at 2.5 against a promised 0-1)."""
    if key in _SETTING_ENUMS:
        value = str(raw).upper()
        if value not in _SETTING_ENUMS[key]:
            raise ValueError(f"{value} is not one of the falloff shapes")
        return value
    if key in _SETTING_INT_KEYS:
        value = int(raw)
    else:
        value = float(raw)
    lo_hi = SETTINGS[key].get("range")
    if lo_hi is not None and not lo_hi[0] <= value <= lo_hi[1]:
        raise ValueError(
            f"{key} must be between {lo_hi[0]} and {lo_hi[1]}")
    return value


_PLAN_MAX_STEPS = 8


def _clean_plan_line(line):
    """Strip the furniture real models wrap protocol lines in:
    code fences, bold marks, list numbering and bullets."""
    s = line.strip().strip("`").strip()
    s = re.sub(r"^\d+[.)]\s*", "", s)
    s = re.sub(r"^[-*]\s+", "", s)
    s = s.replace("**", "").replace("__", "")
    return s.strip()


def _parse_hex_colour(text):
    h = text.strip().lstrip("#")
    if len(h) != 6:
        raise ValueError("colour must be #RRGGBB")
    return (int(h[0:2], 16) / 255.0, int(h[2:4], 16) / 255.0,
            int(h[4:6], 16) / 255.0, 1.0)


def _parse_plan(text):
    """(summary, steps, dropped) from an agent reply. Steps are
    only kept when everything they name is verifiably real AND
    inside the advertised gate: buttons that exist and aren't
    stale, tools from the SAME everyday list the prompt prints
    (session/file tools and deletion are refused outright),
    settings and styles that exist in this Blender, node types
    from the node list. The 8-step cap and dedupe are enforced
    here, in code - they used to live only in the prompt. Lines
    that look like steps but can't be read count as dropped, so
    the 'left out' note tells the truth."""
    summary = ""
    steps = []
    dropped = 0
    valid_tools = None
    valid_buttons = _expert_buttons()
    stale_settings = _stale_settings()
    stale_styles = _stale_styles()

    def gate_tools():
        nonlocal valid_tools
        if valid_tools is None:
            valid_tools = _plan_tools()
        return valid_tools

    def keep(step):
        nonlocal dropped
        if step in steps:
            dropped += 1
            return
        if len(steps) >= _PLAN_MAX_STEPS:
            dropped += 1
            return
        steps.append(step)

    for raw_line in (text or "").splitlines():
        line = _clean_plan_line(raw_line)
        if not line:
            continue
        m = re.match(r"(?i)SUMMARY:\s*(.+)$", line)
        if m:
            summary = m.group(1).strip()
            continue
        m = re.match(r"(?i)STEP:\s*(button|tool|style|find):\s*(\S.*?)\s*$",
                     line)
        if m:
            kind, ident = m.group(1).lower(), m.group(2).strip()
            if kind == "button" and ident in valid_buttons:
                keep({"kind": "button", "id": ident})
            elif kind == "tool" and ident in gate_tools():
                keep({"kind": "tool", "id": ident})
            elif kind == "style" and ident in STYLES \
                    and ident not in stale_styles:
                keep({"kind": "style", "id": ident})
            elif kind == "find" and 0 < len(ident) <= 60:
                keep({"kind": "find", "id": ident})
            else:
                dropped += 1
            continue
        m = re.match(r"(?i)STEP:\s*set:\s*([a-z_.]+):\s*(\S+)\s*$", line)
        if m:
            key, raw = m.group(1).lower(), m.group(2)
            if key in SETTINGS and key not in stale_settings:
                try:
                    value = _coerce_setting(key, raw)
                except (TypeError, ValueError):
                    dropped += 1
                else:
                    keep({"kind": "set", "id": key, "value": value})
            else:
                dropped += 1
            continue
        m = re.match(r"(?i)STEP:\s*node:add:\s*([A-Za-z0-9_]+)\s*$", line)
        if m:
            bl_idname = m.group(1)
            if bl_idname in _NODE_ADD_TYPES:
                keep({"kind": "node", "op": "add", "type": bl_idname})
            else:
                dropped += 1
            continue
        m = re.match(r"(?i)STEP:\s*node:set:\s*(.+)$", line)
        if m:
            parts = m.group(1).split(":", 2)
            if len(parts) == 3 and all(p.strip() for p in parts):
                keep({"kind": "node", "op": "set",
                      "node": parts[0].strip(),
                      "input": parts[1].strip(),
                      "value": parts[2].strip()})
            else:
                dropped += 1
            continue
        m = re.match(r"(?i)STEP:\s*node:link:\s*(.+)$", line)
        if m:
            parts = m.group(1).split(":", 3)
            if len(parts) == 4 and all(p.strip() for p in parts):
                keep({"kind": "node", "op": "link",
                      "from": parts[0].strip(),
                      "from_socket": parts[1].strip(),
                      "to": parts[2].strip(),
                      "to_socket": parts[3].strip()})
            else:
                dropped += 1
            continue
        m = re.match(r"(?i)STEP:\s*node:remove:\s*(.+?)\s*$", line)
        if m:
            keep({"kind": "node", "op": "remove",
                  "node": m.group(1).strip()})
            continue
        m = re.match(r"(?i)STEP:\s*ramp:\s*([^:]+):\s*(.+)$", line)
        if m:
            stops = []
            ok = True
            for chunk in m.group(2).split(";"):
                sm = re.match(r"\s*([0-9.]+)\s*=\s*(#[0-9A-Fa-f]{6})\s*$",
                              chunk)
                if not sm:
                    ok = False
                    break
                try:
                    pos = float(sm.group(1))
                    colour = _parse_hex_colour(sm.group(2))
                except ValueError:
                    ok = False
                    break
                if not 0.0 <= pos <= 1.0:
                    ok = False
                    break
                stops.append((pos, colour))
            if ok and 2 <= len(stops) <= 8:
                keep({"kind": "ramp", "node": m.group(1).strip(),
                      "stops": stops})
            else:
                dropped += 1
            continue
        m = re.match(r"(?i)STEP:\s*grow:\s*(tree|sprite)\s*$", line)
        if m:
            keep({"kind": "grow", "what": m.group(1).lower()})
            continue
        if re.match(r"(?i)STEP\b", line):
            # A step-shaped line we couldn't read at all. It
            # counts - the old parser let these vanish silently.
            dropped += 1
    return summary, steps, dropped


def _raise_http_fault(exc):
    """Turn a raw HTTP failure into a named _ExpertFault."""
    if isinstance(exc, TimeoutError) or isinstance(
            getattr(exc, "reason", None), TimeoutError):
        raise _ExpertFault("timeout") from exc
    if isinstance(exc, urllib.error.HTTPError):
        body = ""
        try:
            body = exc.read().decode("utf-8", "replace")
        except Exception:
            pass
        if exc.code in (401, 403):
            raise _ExpertFault("key_refused") from exc
        if exc.code == 429:
            raise _ExpertFault("rate_limited") from exc
        if exc.code == 404 and "model" in body.lower():
            raise _ExpertFault("model_missing") from exc
        raise _ExpertFault("service_error", str(exc.code)) from exc
    raise _ExpertFault("unreachable",
                       str(getattr(exc, "reason", exc))[:60]) from exc


def _expert_http_claude(url, key, payload, *, loopback_only=False):
    """Anthropic's service speaks a different shape than the
    OpenAI-style one: the key rides in its own header, with the
    service's version header alongside."""
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers={"Content-Type": "application/json",
                 "x-api-key": key,
                 "anthropic-version": _CLAUDE_VERSION})
    try:
        with _expert_urlopen(req, timeout=30, loopback_only=loopback_only) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        _raise_http_fault(exc)


def _ask_via_claude(settings, system, user):
    payload = {"model": settings["model"], "max_tokens": 1024,
               "system": system,
               "messages": [{"role": "user", "content": user}]}
    options = {"loopback_only": True} if settings.get("_loopback_only") else {}
    data = _expert_http_claude(settings["url"], settings["key"], payload, **options)
    parts = [b.get("text", "") for b in data.get("content", [])
             if b.get("type") == "text"]
    text = "\n".join(p for p in parts if p).strip()
    if not text:
        raise _ExpertFault("empty_reply")
    return text


def _ask_ai(settings, system, user):
    if settings.get("service") == "CODEX":
        return _ask_via_codex(system, user)
    if settings.get("service") == "CLAUDE":
        return _ask_via_claude(settings, system, user)
    payload = {"model": settings["model"],
               "messages": [{"role": "system", "content": system},
                            {"role": "user", "content": user}]}
    options = {"loopback_only": True} if settings.get("_loopback_only") else {}
    data = _expert_http(settings["url"], settings["key"], payload, **options)
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError, TypeError, AttributeError):
        raise _ExpertFault("empty_reply")


def _step_label(step):
    if step["kind"] == "button":
        act = next((a for a in ACTIONS if a["id"] == step["id"]), None)
        return act["plain"] if act else step["id"]
    if step["kind"] == "set":
        return f"Set {SETTINGS[step['id']]['label'].lower()} to {step['value']}"
    if step["kind"] == "style":
        return f"Style it: {STYLES[step['id']][0]}"
    if step["kind"] == "find":
        return f"Find real add-ons, models and textures for: {step['id']}"
    if step["kind"] == "node":
        if step["op"] == "add":
            plain = _NODE_ADD_TYPES.get(step["type"], step["type"])
            return f"Add a node: {plain}"
        if step["op"] == "set":
            return (f"Set '{step['node']}' {step['input']} to "
                    f"{step['value']}")
        if step["op"] == "link":
            return (f"Wire '{step['from']}' {step['from_socket']} "
                    f"into '{step['to']}' {step['to_socket']}")
        return f"Remove the node '{step['node']}'"
    if step["kind"] == "ramp":
        return f"Set the colour ramp '{step['node']}' from a description"
    if step["kind"] == "grow":
        if step["what"] == "tree":
            return "Grow a low tree (an ingredient to place)"
        return "Make a flat picture of the picked thing (a sprite)"
    for e in build_index():
        if e["idname"] == step["id"]:
            return f"{e['label']} (Blender tool)"
    return step["id"]


def _expert_http(url, key, payload, *, loopback_only=False):
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), method="POST",
        headers=headers)
    # A local AI thinks on the user's own processor, and Buddy's
    # scene description is long: on a machine without a graphics
    # card, one honest answer can take minutes (measured on the
    # test VM: 52s for a short advice answer from the smallest
    # local model). A flat 30-second cap made every local answer
    # die as a fake 'unreachable'. The wait runs off the interface
    # thread and Esc stops it, so a local address gets the time
    # the work actually takes; a hosted service keeps 30s.
    timeout = 300 if _is_local_url(url) else 30
    try:
        with _expert_urlopen(req, timeout=timeout, loopback_only=loopback_only) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        _raise_http_fault(exc)


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


# ---------------------------------------------------------------------
# Asking without freezing Blender: an expert call can take 30s on
# a service or two minutes through Codex, and it used to run
# inside the button press - the whole interface froze, which read
# as a crash. Now the call runs on a worker thread and a small
# modal operator watches for it; Esc stops the wait. Headless
# there is no interface to freeze, so the call runs inline.
# ---------------------------------------------------------------------

_EXPERT_JOB = {"id": 0, "busy": False, "kind": "", "text": "",
               "error": None, "extra": None, "settings": None, "future": None, "wm": None}


def _expert_selection(context):
    """Capture session-local identities, including the empty selection."""
    def identity(item):
        if item is None:
            return None
        return (item.as_pointer(), getattr(item, "session_uid", None))
    return (identity(context.scene), context.mode, identity(context.view_layer.objects.active),
            frozenset(identity(obj) for obj in context.selected_objects))


@bpy.app.handlers.persistent
def _expert_job_discard(*_args):
    # The worker owns only its own future. A late reply can never
    # publish into a different request, or into a newly opened file.
    _EXPERT_JOB.update(id=_EXPERT_JOB["id"] + 1, busy=False, kind="",
                       future=None, extra=None, settings=None, wm=None, text="", error=None)


def _expert_job_start(kind, settings, system, user, extra=None):
    if _EXPERT_JOB["busy"]:
        raise RuntimeError("An expert request is already running.")
    settings = dict(settings, _loopback_only=not bpy.app.online_access)
    future = Future()
    if settings.get("service") == "CODEX":
        limit = 140  # 20s for login status, then 120s for the reply.
    elif settings.get("service") == "LOCAL" or _is_local_url(settings.get("url")):
        limit = 300
    else:
        limit = 30
    _EXPERT_JOB.update(id=_EXPERT_JOB["id"] + 1, busy=True, kind=kind,
                       text="", error=None, extra=extra, settings=settings,
                       future=future, started=time.monotonic(), limit=limit, last_draw=-1,
                       wm=bpy.context.window_manager)

    if not _expert_access_allowed(settings):
        _expert_job_finish("", _ExpertFault("offline"))
        return

    def work():
        try:
            text, err = _ask_ai(settings, system, user), None
        except Exception as exc:
            text, err = "", exc
        future.set_result((time.monotonic(), text, err))

    if bpy.app.background:
        work()
        _, text, err = future.result()
        _expert_job_finish(text, err)
        return
    try:
        if not bpy.app.timers.is_registered(_expert_job_tick):
            bpy.app.timers.register(_expert_job_tick, first_interval=0.15)
        threading.Thread(target=work, daemon=True).start()
    except Exception as exc:
        _expert_job_finish("", exc)
        return
    # This operator provides Esc. The app timer delivers results even
    # when the originating window or its modal handler disappears.
    try:
        bpy.ops.buddy.expert_wait("INVOKE_DEFAULT")
    except RuntimeError:
        pass


def _expert_job_tick():
    job = _EXPERT_JOB
    if not job["busy"]:
        return None
    now = time.monotonic()
    deadline = job["started"] + job["limit"]
    future = job["future"]
    if future.done():
        finished, text, err = future.result()
        if finished <= deadline:
            _expert_job_finish(text, err)
            return None
    elif now < deadline:
        elapsed = int(now - job["started"])
        if elapsed != job["last_draw"]:
            job["last_draw"] = elapsed
            _card_tag_redraw()
        return 0.25
    _expert_job_finish("", _ExpertFault("timeout", str(job["limit"])))
    return None


def _expert_job_finish(text, err):
    wm = _EXPERT_JOB["wm"]
    kind = _EXPERT_JOB["kind"]
    _EXPERT_JOB.update(kind="", busy=False, future=None, wm=None, text=text, error=err)
    try:
        if kind == "ask":
            _finish_ask(wm)
        elif kind == "test":
            _finish_test(wm)
        elif kind == "replan":
            _finish_replan(wm)
    except Exception as exc:
        # A bad reply must leave the card usable for a fresh request.
        _EXPERT_JOB["error"] = exc
        message = _fault_message(_EXPERT_JOB["settings"], exc)
        if kind == "test":
            wm.buddy_expert_status = message
        else:
            wm.buddy_plan = ""
            wm.buddy_suggested = ""
            wm.buddy_answer = message
    _card_tag_redraw()


class BUDDY_OT_expert_wait(Operator):
    bl_idname = "buddy.expert_wait"
    bl_label = "Waiting for the Expert"
    bl_description = ("Wait for the expert's answer without "
                      "freezing Blender - you can keep working; "
                      "press Esc in the 3D view to stop waiting")
    bl_options = {"INTERNAL"}

    _timer = None
    _job_id = -1

    def invoke(self, context, event):
        self._job_id = _EXPERT_JOB["id"]
        self._timer = context.window_manager.event_timer_add(
            0.25, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if self._job_id != _EXPERT_JOB["id"] or not _EXPERT_JOB["busy"]:
            self._stop(context)
            return {"FINISHED", "PASS_THROUGH"}
        if event.type == "ESC" and event.value == "PRESS":
            kind = _EXPERT_JOB["kind"]
            base = (_EXPERT_JOB.get("extra") or {}).get("base", "")
            _expert_job_discard()
            self._stop(context)
            wm = context.window_manager
            if kind == "ask":
                wm.buddy_answer = "Stopped waiting for the expert. You can ask again."
            elif kind == "test":
                wm.buddy_expert_status = "Stopped waiting for the connection test."
            elif kind == "replan":
                wm.buddy_answer = (base + " Stopped waiting for revised steps.").strip()
                wm.buddy_plan_report = wm.buddy_answer
            _card_tag_redraw()
            return {"CANCELLED"}
        return {"PASS_THROUGH"}

    def _stop(self, context):
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None


def _extract_suggestion(text):
    """(answer_text, suggested_button_id) from an advice reply.
    The extractor and the stripper are the same case-insensitive
    match now - a lowercase 'button:' line used to be removed
    from the answer while the extractor found nothing, so words
    silently vanished."""
    suggested = ""
    kept = []
    for line in (text or "").splitlines():
        m = re.match(r"(?i)\s*BUTTON:\s*([a-z0-9_]+)[.\s]*$", line)
        if m:
            if m.group(1) in _expert_buttons():
                suggested = m.group(1)
            continue
        kept.append(line)
    return "\n".join(kept).strip(), suggested


def _finish_ask(wm):
    global _EXPERT_TIP
    settings = _EXPERT_JOB.get("settings") or _expert_settings()
    extra = _EXPERT_JOB.get("extra") or {}
    question = extra.get("question", "")
    error = _EXPERT_JOB["error"]
    text = _EXPERT_JOB["text"]
    if error is not None:
        wm.buddy_answer = _fault_message(settings, error)
        wm.buddy_suggested = ""
        return
    if extra.get("agent"):
        summary, steps, dropped = _parse_plan(text)
        if steps:
            wm.buddy_plan = json.dumps(steps)
            _EXPERT_JOB["reviewed_target"] = (wm.buddy_plan, extra.get("target"))
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
            _EXPERT_TIP = (f"Plan ready: {len(steps)} steps. "
                           "Press Run these steps.")
            return
        # No usable plan came back. Say so, and show what DID
        # come back labelled as advice - the old code silently
        # made a second call and presented its answer as if the
        # first had never happened.
        advice, suggested = _extract_suggestion(text)
        wm.buddy_answer = (
            "The expert's plan didn't come through in a shape "
            "Buddy can run, so here is its answer as advice "
            "instead:\n" + advice if advice else
            "The expert answered, but not in a shape Buddy can "
            "turn into steps or advice. Ask it another way - a "
            "smaller, single task works best.")
        wm.buddy_suggested = suggested
        return
    answer, suggested = _extract_suggestion(text)
    wm.buddy_answer = answer
    wm.buddy_suggested = suggested
    first = answer.split(". ")[0].strip()
    _EXPERT_TIP = (first[:110] + ("..." if len(first) > 110 else ""))


class BUDDY_OT_ask_expert(Operator):
    bl_idname = "buddy.ask_expert"
    bl_label = "Ask the Expert"
    bl_description = ("Ask the AI expert about your scene, in your own "
                      "words. It answers in plain words and points at "
                      "the right button when Buddy has one")
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return not _EXPERT_JOB["busy"]

    def execute(self, context):
        wm = context.window_manager
        settings = _expert_settings()
        question = (wm.buddy_ask or "").strip()
        # A displayed plan belongs to the preceding question. Retire it
        # before returning any local answer, setup error, or new request.
        _EXPERT_JOB["reviewed_target"] = None
        wm.buddy_plan = wm.buddy_plan_summary = wm.buddy_plan_report = ""
        wm.buddy_plan_retried = wm.buddy_answer = wm.buddy_suggested = ""
        if not question:
            wm.buddy_answer = ("Type a question first - anything, "
                               "in your own words.")
            wm.buddy_suggested = ""
            return {"CANCELLED"}
        if _is_capability_question(question):
            wm.buddy_answer = _capability_answer(context)
            wm.buddy_suggested = ""
            self.report({"INFO"}, "What the expert can do - it's "
                                  "in the floating card, no connection needed.")
            return {"FINISHED"}
        if not _expert_ready(settings):
            wm.buddy_answer = _expert_setup_message(settings)
            wm.buddy_suggested = ""
            return {"CANCELLED"}
        agent = wm.buddy_agent
        if agent:
            system = _expert_agent_prompt(context)
            user = f"{_scene_summary(context)}\n\nGoal: {question}"
        else:
            system = _expert_system_prompt()
            user = f"{_scene_summary(context)}\n\nQuestion: {question}"
        _expert_job_start("ask", settings, system, user,
                          extra={"question": question, "agent": agent,
                                 "target": _expert_selection(context) if agent else None})
        if bpy.app.background:
            self.report({"INFO"}, "The expert answered in the floating card.")
        return {"FINISHED"}


def _finish_test(wm):
    settings = _EXPERT_JOB.get("settings") or _expert_settings()
    error = _EXPERT_JOB["error"]
    reply = _EXPERT_JOB["text"]
    if error is not None:
        msg = _fault_message(settings, error)
    elif "BUDDY OK" in (reply or ""):
        msg = ("It works - your expert answered the test "
               "question. Ask it anything in the floating card.")
    else:
        msg = ("Something answered, but not cleanly: "
               + (reply or "")[:90])
    try:
        wm.buddy_expert_status = msg
    except Exception:
        pass


def _finish_replan(wm):
    global _EXPERT_TIP
    base = (_EXPERT_JOB.get("extra") or {}).get("base", "")
    if _EXPERT_JOB["error"] is not None:
        reason = _fault_message(_EXPERT_JOB["settings"], _EXPERT_JOB["error"])
        wm.buddy_plan_report = base + " " + reason
        wm.buddy_answer = wm.buddy_plan_report
        return
    summary, new_steps, _d = _parse_plan(_EXPERT_JOB["text"])
    if new_steps:
        wm.buddy_answer = ""
        wm.buddy_plan = json.dumps(new_steps)
        _EXPERT_JOB["reviewed_target"] = (wm.buddy_plan, (_EXPERT_JOB.get("extra") or {}).get("target"))
        wm.buddy_plan_summary = summary or wm.buddy_plan_summary
        wm.buddy_plan_retried = "1"
        wm.buddy_plan_report = (
            base + " The expert replanned around it - check the "
            "new plan below and press Run again.")
        _EXPERT_TIP = "The plan hit a snag; the expert replanned."
    else:
        wm.buddy_plan_report = base
        wm.buddy_answer = base


class BUDDY_OT_test_expert(Operator):
    """Send one tiny test question through the expert route the
    user picked, and say plainly whether it answered. The Codex
    setup failed silently before this existed (owner, 2026-11-12:
    "setting up codex doesnt work") - now there is proof either
    way, in words, and a failure names the actual fault."""
    bl_idname = "buddy.test_expert"
    bl_label = "Test the Expert Connection"
    bl_description = ("Send one tiny test question through the "
                      "expert route you picked above and show, in "
                      "plain words, whether it answered")

    @classmethod
    def poll(cls, context):
        return not _EXPERT_JOB["busy"]

    def execute(self, context):
        settings = _expert_settings()
        service = settings.get("service", "KEY")
        if service == "CODEX" and _expert_access_allowed(settings) and _find_codex() is None:
            try:
                context.window_manager.buddy_expert_status = \
                    _fault_message(settings,
                                   _ExpertFault("codex_missing"))
            except Exception:
                pass
            self.report({"WARNING"}, "Buddy couldn't locate the Codex command-line program")
            return {"FINISHED"}
        _expert_job_start("test", settings,
                          "You are a connection test.",
                          "Reply with exactly: BUDDY OK")
        status = ""
        try:
            status = context.window_manager.buddy_expert_status
        except Exception:
            pass
        self.report({"INFO"} if status.startswith("It works")
                    else {"WARNING"}, (status or "Testing...")[:240])
        return {"FINISHED"}


class BUDDY_OT_open_codex(Operator):
    """Open OpenAI's Codex program so the user can sign in to it -
    the login lives in their program, so Buddy takes the user to
    its door instead of describing a treasure hunt."""
    bl_idname = "buddy.open_codex"
    bl_label = "Open Codex to Sign In"
    bl_description = ("Open OpenAI's Codex program on this "
                      "computer. Sign in there with your ChatGPT "
                      "account once - then Buddy can ask through it")

    @classmethod
    def poll(cls, context):
        return _find_codex() is not None

    def execute(self, context):
        path = _find_codex()
        if not path:
            self.report({"WARNING"}, "Buddy couldn't locate the Codex command-line program")
            return {"CANCELLED"}
        try:
            if os.name == "nt" and path.lower().endswith((".cmd", ".bat")):
                subprocess.Popen(["cmd", "/c", "start", "", path])
            else:
                subprocess.Popen([path])
        except Exception as exc:
            self.report({"WARNING"},
                        f"Buddy found Codex but couldn't open it: {exc}")
            return {"CANCELLED"}
        self.report({"INFO"}, "Opened Codex - sign in there with "
                              "your ChatGPT account, then come back "
                              "and ask.")
        return {"FINISHED"}


class BUDDY_OT_run_plan(Operator):
    bl_idname = "buddy.run_plan"
    bl_label = "Run These Steps"
    bl_description = ("Run the expert's plan, step by step, in your "
                      "Blender. It stops at the first step that can't "
                      "run and tells you plainly what happened")
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return not _EXPERT_JOB["busy"]

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
        reviewed = _EXPERT_JOB.get("reviewed_target")
        if (reviewed and reviewed[0] == wm.buddy_plan and reviewed[1] is not None
                and reviewed[1] != _expert_selection(context)):
            _EXPERT_JOB["reviewed_target"] = None
            wm.buddy_plan = wm.buddy_plan_summary = wm.buddy_suggested = ""
            wm.buddy_answer = wm.buddy_plan_report = (
                "The scene, mode or selection changed since you asked. Nothing ran. "
                "Ask for a new plan with the intended selection.")
            self.report({"WARNING"}, wm.buddy_plan_report)
            return {"CANCELLED"}
        # Old or externally supplied plans may predate the parser's guard.
        # Preflight every command before making the first scene edit.
        buttons = _expert_buttons()
        tools = _plan_tools()
        if not isinstance(steps, list) or any(
                not isinstance(s, dict)
                or (s.get("kind") in ("button", "tool") and not isinstance(s.get("id"), str))
                or (s.get("kind") == "button" and s.get("id") not in buttons)
                or (s.get("kind") == "tool" and s.get("id") not in tools)
                for s in steps):
            wm.buddy_plan = wm.buddy_plan_summary = wm.buddy_suggested = ""
            wm.buddy_answer = wm.buddy_plan_report = "This plan contains an unavailable Expert step. Ask for a new plan."
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
                    if ok and step["id"] == "render.samples" \
                            and context.scene.render.engine != "CYCLES":
                        notes.append(
                            "Heads-up: this scene renders with "
                            "Eevee right now, so the Cycles sample "
                            "count won't change its picture - it "
                            "counts when a scene renders in Cycles.")
                elif step["kind"] == "style":
                    changed, snote = _apply_style(step["id"],
                                                   context.object)
                    ok = changed
                    if snote:
                        notes.append(snote)
                    if not ok:
                        fail_why = snote
                elif step["kind"] == "find":
                    results = _find_resources(step["id"])
                    if results:
                        wm.buddy_find = json.dumps(results)
                        listing = "; ".join(
                            f"{r['name']} ({r['source']})"
                            for r in results)
                        notes.append(
                            f"Found for '{step['id']}' - every "
                            f"link checked just now: {listing}. "
                            "Open Found resources in the Blender Buddy "
                            "sidebar to visit a link.")
                        ok = True
                    else:
                        fail_why = (
                            f"no page for '{step['id']}' could be "
                            "checked and confirmed just now - "
                            "results are only shown once their "
                            "links prove real")
                        ok = False
                elif step["kind"] == "node":
                    ok, note, why = _exec_node_step(context, step)
                    if note:
                        notes.append(note)
                    if not ok:
                        fail_why = why
                elif step["kind"] == "ramp":
                    ok, note, why = _exec_ramp_step(context, step)
                    if note:
                        notes.append(note)
                    if not ok:
                        fail_why = why
                elif step["kind"] == "grow":
                    if step["what"] == "tree":
                        names = _grow_tree(context)
                        notes.append(
                            "Grew a low tree at the target: "
                            + ", ".join(names) + ". Move it where "
                            "you want it - it's yours now.")
                    else:
                        name = _grow_sprite(context)
                        notes.append(
                            f"Made '{name}' - a flat picture of "
                            "the picked thing, standing at the "
                            "target.")
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
            _EXPERT_JOB["reviewed_target"] = None
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
        if done:
            # Retrying an already applied prefix would duplicate scene edits.
            wm.buddy_plan = wm.buddy_suggested = ""
            _EXPERT_JOB["reviewed_target"] = None
        # One replan: send the failure back and let the expert route
        # around it. The new plan is SHOWN, never auto-run. In a
        # window the ask goes on the job thread like any other -
        # a replan used to freeze the interface too.
        settings = _expert_settings()
        if _expert_ready(settings) and not wm.buddy_plan_retried:
            target = _expert_selection(context)
            user = (f"{_scene_summary(context)}\n\n"
                    f"Goal: {wm.buddy_ask}\n"
                    f"Your previous plan stopped at step "
                    f"{fail_at + 1} ('{label}'): {fail_why}. "
                    f"Give a revised plan that still reaches the "
                    f"goal from the scene as it is now.")
            if bpy.app.background:
                try:
                    text = _ask_ai(dict(settings, _loopback_only=not bpy.app.online_access),
                                   _expert_agent_prompt(context), user)
                except Exception:
                    text = ""
                summary, new_steps, _d = _parse_plan(text)
                if new_steps:
                    wm.buddy_plan = json.dumps(new_steps)
                    _EXPERT_JOB["reviewed_target"] = (wm.buddy_plan, target)
                    wm.buddy_plan_summary = summary or wm.buddy_plan_summary
                    wm.buddy_plan_retried = "1"
                    wm.buddy_plan_report = (
                        base + " The expert replanned around it - "
                        "check the new plan below and press Run again.")
                    _EXPERT_TIP = "The plan hit a snag; the expert replanned."
                    self.report({"WARNING"}, wm.buddy_plan_report)
                    return {"CANCELLED"}
            else:
                wm.buddy_plan_report = (
                    base + " Asking the expert for a revised plan...")
                # Already-run steps cannot be approved a second time.
                wm.buddy_plan = ""
                wm.buddy_suggested = ""
                _EXPERT_JOB["reviewed_target"] = None
                wm.buddy_answer = wm.buddy_plan_report
                _expert_job_start("replan", settings,
                                  _expert_agent_prompt(context), user,
                                  extra={"base": base, "target": target})
                return {"CANCELLED"}
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
        _EXPERT_JOB["reviewed_target"] = None
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


# ----------------------------------------------------------------------------
# The floating Expert card: the Expert's full front end, floating
# over the 3D window (owner, 2026-11-18: "a floating popup...
# that you can resize and move freely, minimize to the corner").
# It replaces the old read-only tip float - there is exactly ONE
# floating thing now. The card is only a front end: every state it
# shows lives in the same WindowManager properties and _EXPERT_JOB
# the panel uses, asking goes through buddy.ask_expert itself, and
# a plan still runs only when the user presses the card's (or the
# panel's) Run button. Geometry and the minimised flag persist in
# the addon preferences; the rest is session state in _CARD.
# ----------------------------------------------------------------------------

_CARD_MIN_W = 320
_CARD_MIN_H = 240
_CARD_DEF_W = 440
_CARD_DEF_H = 360
_CARD_TITLE_H = 26
_CARD_STATUS_H = 15
_CARD_NOTICE_H = 15
_CARD_FIELD_H = 24
_CARD_FOOTER_H = 30
_CARD_PAD = 10
_CARD_LINE_H = 15
_CARD_ASK_W = 88
_CARD_CHIP_W = 158
_CARD_CHIP_H = 26

_CARD = {"open": True, "text": "", "caret": 0, "focused": False,
         "scroll": 0, "drag": None, "live": None, "hover": None,
         "modal": False, "sig": None, "cache_key": None,
         "cache_lines": [], "cache_footer": None,
         "focus_region": None}

_CARD_INPUT_WINDOWS = set()


def _card_has_listener(window):
    # Opening a file removes native modal handlers without calling Python.
    operators = getattr(window, "modal_operators", None)
    if operators is not None:
        for op in operators:
            # Other add-ons can leave null or invalid RNA handles after reload.
            try:
                if getattr(op, "bl_idname", None) == "BUDDY_OT_expert_card_modal":
                    return True
            except (ReferenceError, RuntimeError):
                continue
        return False
    return window.as_pointer() in _CARD_INPUT_WINDOWS


@bpy.app.handlers.persistent
def _card_file_loaded(_unused):
    _CARD_INPUT_WINDOWS.clear()
    _CARD.update(modal=False, focused=False, focus_region=None, drag=None, live=None)
    # A plan saved by an earlier version cannot identify its original objects
    # after a file load. New programmatically supplied plans remain supported.
    _EXPERT_JOB["reviewed_target"] = None
    wm = bpy.context.window_manager
    if wm and getattr(wm, "buddy_plan", ""):
        wm.buddy_plan = wm.buddy_plan_summary = wm.buddy_suggested = ""
        wm.buddy_answer = wm.buddy_plan_report = "Ask for a new plan in this file."

_CARD_ROUTES = {"KEY": "AI key", "CLAUDE": "Claude key",
                "CODEX": "ChatGPT login", "LOCAL": "local AI"}


def _card_prefs():
    """The card's persisted state, with the designed defaults when
    the preferences can't be read (headless test runs)."""
    try:
        p = bpy.context.preferences.addons[__name__].preferences
        return {"float": bool(p.expert_float),
                "x": int(p.expert_card_x), "y": int(p.expert_card_y),
                "w": int(p.expert_card_w), "h": int(p.expert_card_h),
                "min": bool(p.expert_card_min)}
    except Exception:
        return {"float": True, "x": -1, "y": -1,
                "w": _CARD_DEF_W, "h": _CARD_DEF_H, "min": False}


def _card_save_geo(geo):
    try:
        p = bpy.context.preferences.addons[__name__].preferences
        p.expert_card_x, p.expert_card_y = int(geo[0]), int(geo[1])
        p.expert_card_w, p.expert_card_h = int(geo[2]), int(geo[3])
    except Exception:
        pass


def _card_save_min(flag):
    try:
        p = bpy.context.preferences.addons[__name__].preferences
        p.expert_card_min = bool(flag)
    except Exception:
        pass


def _card_clamp_geo(region_w, region_h, geo):
    """Resolve a stored (x, y, w, h) into the rect the card can
    actually occupy in this region: size clamped to the card's
    minimums and the region, an unset position (-1) landing at the
    old tip card's proven spot (x=72, top margin 96), and any
    stored position pulled back inside the region. Pure math -
    headless-tested."""
    x, y, w, h = geo
    w = max(_CARD_MIN_W, min(int(w), max(_CARD_MIN_W, region_w)))
    h = max(_CARD_MIN_H, min(int(h), max(_CARD_MIN_H, region_h)))
    if x < 0:
        x = 72
    if y < 0:
        y = region_h - h - 96
    x = max(0, min(int(x), max(0, region_w - w)))
    y = max(0, min(int(y), max(0, region_h - h)))
    return (x, y, w, h)


def _card_layout(geo, minimized=False, notice=False, footer=None):
    """Every named element rect of the card for one frame, as
    (x0, y0, x1, y1) in region pixels. Pure - headless-tested."""
    x, y, w, h = geo
    if minimized:
        chip = (10, 10, 10 + _CARD_CHIP_W, 10 + _CARD_CHIP_H)
        return {"card": chip, "chip": chip}
    lay = {"card": (x, y, x + w, y + h)}
    top = y + h
    lay["title"] = (x, top - _CARD_TITLE_H, x + w, top)
    lay["btn_min"] = (x + w - 54, top - _CARD_TITLE_H + 4,
                      x + w - 32, top - 4)
    lay["btn_close"] = (x + w - 28, top - _CARD_TITLE_H + 4,
                        x + w - 6, top - 4)
    cy = top - _CARD_TITLE_H
    lay["status"] = (x + _CARD_PAD, cy - _CARD_STATUS_H,
                     x + w - _CARD_PAD, cy)
    cy -= _CARD_STATUS_H
    if notice:
        lay["notice"] = (x + _CARD_PAD, cy - _CARD_NOTICE_H,
                         x + w - _CARD_PAD, cy)
        cy -= _CARD_NOTICE_H
    fy1 = cy - 4
    fy0 = fy1 - _CARD_FIELD_H
    lay["field"] = (x + _CARD_PAD, fy0,
                    x + w - _CARD_PAD - _CARD_ASK_W, fy1)
    lay["btn_ask"] = (x + w - _CARD_PAD - _CARD_ASK_W + 6, fy0,
                      x + w - _CARD_PAD, fy1)
    cy = fy0
    body_bottom = y + 6
    lay["footer_kind"] = footer
    if footer == "plan":
        lay["footer"] = (x, y, x + w, y + _CARD_FOOTER_H)
        lay["btn_run"] = (x + _CARD_PAD, y + 5,
                          x + _CARD_PAD + 132, y + _CARD_FOOTER_H - 5)
        lay["btn_clear"] = (x + _CARD_PAD + 140, y + 5,
                            x + _CARD_PAD + 262, y + _CARD_FOOTER_H - 5)
        body_bottom = y + _CARD_FOOTER_H + 4
    elif footer == "do":
        lay["footer"] = (x, y, x + w, y + _CARD_FOOTER_H)
        lay["btn_do"] = (x + _CARD_PAD, y + 5,
                         x + _CARD_PAD + 262, y + _CARD_FOOTER_H - 5)
        body_bottom = y + _CARD_FOOTER_H + 4
    lay["body"] = (x + _CARD_PAD, body_bottom,
                   x + w - _CARD_PAD, cy - 6)
    lay["grip"] = (x + w - 18, y, x + w, y + 18)
    lay["body_lines"] = max(
        1, int((lay["body"][3] - lay["body"][1]) // _CARD_LINE_H))
    return lay


def _card_hit(layout, mx, my):
    """Which card element is at (mx, my), or None. Buttons and the
    grip win over the areas they sit on. Pure - headless-tested."""
    def inside(rect):
        return rect and rect[0] <= mx <= rect[2] and \
            rect[1] <= my <= rect[3]
    if "chip" in layout:
        return "chip" if inside(layout["chip"]) else None
    for name in ("btn_close", "btn_min", "btn_ask", "btn_run",
                 "btn_clear", "btn_do", "grip", "field", "title",
                 "body"):
        if name in layout and inside(layout[name]):
            if name in ("btn_run", "btn_clear") and \
                    layout.get("footer_kind") != "plan":
                continue
            if name == "btn_do" and layout.get("footer_kind") != "do":
                continue
            return name
    if inside(layout.get("card")):
        return "card"
    return None


def _card_text_px(text, size=11):
    """Measured pixel width of text in the card's font, or None
    when it cannot be measured in this session."""
    try:
        import blf
        blf.size(0, size)
        return blf.dimensions(0, text)[0]
    except Exception:
        return None


def _card_wrap(text, max_px, size=11):
    """Wrap text to a measured pixel width, the card's version of
    the panel's hard-won rule: words survive whole and in order,
    and a single word wider than the space is hard-split rather
    than dropped. Pure when _card_text_px is stubbed - tested."""
    out = []
    for para in (text or "").split("\n"):
        if not para.strip():
            out.append("")
            continue
        cur = ""
        for word in para.split(" "):
            trial = f"{cur} {word}" if cur else word
            width = _card_text_px(trial, size)
            if cur and width is not None and width > max_px:
                out.append(cur)
                cur = word
            else:
                cur = trial
            while cur and len(cur) > 1 and \
                    (_card_text_px(cur, size) or 0) > max_px:
                cut = len(cur) - 1
                while cut > 1 and \
                        (_card_text_px(cur[:cut], size) or 0) > max_px:
                    cut -= 1
                out.append(cur[:cut])
                cur = cur[cut:]
        out.append(cur)
    return out


def _card_clamp_scroll(scroll, total, visible):
    """Bound a scroll offset (lines from the top). Pure - tested."""
    return max(0, min(int(scroll), max(0, total - visible)))


def _card_status_text(settings):
    """The card's status line: the same readiness truth the panel
    shows, in one line (the panel's full setup words appear in the
    card's body, exactly as in the panel)."""
    if _EXPERT_JOB["busy"]:
        elapsed = int(time.monotonic() - _EXPERT_JOB["started"])
        return f"Waiting for the expert: {elapsed}s of {_EXPERT_JOB['limit']}s. Esc stops waiting."
    route = _CARD_ROUTES.get(settings.get("service", "KEY"),
                             "AI key")
    if _expert_ready(settings):
        return f"Ready - answers come through your {route}."
    return "Not set up yet - ask anyway, I'll explain what's missing."


def _card_sync_content(context, max_px):
    """The body's display lines + footer kind for the current
    Expert state, cached by content. Mirrors the panel: a plan
    (report, summary, numbered steps) beats the plain answer; the
    setup message fills the body before any ask on a route that
    isn't ready, so the card explains itself like the panel does."""
    wm = context.window_manager
    settings = _expert_settings()
    plan = []
    try:
        plan = json.loads(wm.buddy_plan or "[]")
    except Exception:
        plan = []
    answer = wm.buddy_answer or ""
    key = (answer, wm.buddy_plan or "", wm.buddy_plan_report or "",
           wm.buddy_plan_summary or "", wm.buddy_suggested or "",
           _expert_ready(settings), int(max_px))
    if _CARD["cache_key"] == key:
        return _CARD["cache_lines"], _CARD["cache_footer"]
    lines = []
    footer = None
    if plan:
        footer = "plan"
        if (wm.buddy_plan_report or "").strip():
            lines += _card_wrap(wm.buddy_plan_report, max_px)
            lines.append("")
        if (wm.buddy_plan_summary or "").strip():
            lines += _card_wrap(
                f"The plan: {wm.buddy_plan_summary}", max_px)
        for number, step in enumerate(plan, start=1):
            try:
                label = _step_label(step)
            except Exception:
                label = str(step.get("id", "Step"))
            lines += _card_wrap(f"{number}. {label}", max_px)
    elif answer.strip():
        lines = _card_wrap(answer, max_px)
        if wm.buddy_suggested and wm.buddy_suggested in _expert_buttons():
            footer = "do"
    elif wm.buddy_plan_report.strip():
        lines = _card_wrap(wm.buddy_plan_report, max_px)
    elif not _expert_ready(settings):
        lines = _card_wrap(_expert_setup_message(settings), max_px)
    else:
        lines = _card_wrap(
            "Ask me anything about your scene, in your own words. "
            "Try: what can you do for me", max_px)
    _CARD["cache_key"] = key
    _CARD["cache_lines"] = lines
    _CARD["cache_footer"] = footer
    _CARD["scroll"] = _card_clamp_scroll(
        _CARD["scroll"], len(lines), 1)
    return lines, footer


def _card_tag_redraw():
    try:
        for win in bpy.context.window_manager.windows:
            for area in win.screen.areas:
                if area.type == "VIEW_3D":
                    for region in area.regions:
                        if region.type == "WINDOW":
                            region.tag_redraw()
    except Exception:
        pass


def _card_signature(context):
    try:
        wm = context.window_manager
        return (bool(_EXPERT_JOB["busy"]), wm.buddy_answer,
                wm.buddy_plan, wm.buddy_plan_report,
                wm.buddy_suggested, _EXPERT_TIP, _CARD["open"],
                _CARD["focused"], _CARD["text"])
    except Exception:
        return None


def _card_field_view(text, caret, max_px, size=11):
    """(visible_text, caret_px) for the question field: the window
    of the buffer that keeps the caret on screen. Pure when
    _card_text_px is stubbed - headless-tested."""
    caret = max(0, min(caret, len(text)))
    start = 0
    while start < caret and \
            (_card_text_px(text[start:caret], size) or 0) > max_px:
        start += 1
    visible = text[start:]
    while visible and \
            (_card_text_px(visible, size) or 0) > max_px:
        visible = visible[:-1]
    return visible, (_card_text_px(text[start:caret], size) or 0)


def _card_fill(shader, rect, color, r=6):
    from gpu_extras.batch import batch_for_shader
    x0, y0, x1, y1 = rect
    batch = batch_for_shader(
        shader, "TRIS",
        {"pos": _fan_tris((x0 + x1) / 2, (y0 + y1) / 2,
                          _rounded_rect_points(x0, y0, x1, y1, r))})
    shader.uniform_float("color", color)
    batch.draw(shader)


def _card_text(x, y, text, size, color):
    import blf
    blf.size(0, size)
    blf.color(0, *color)
    blf.position(0, x, y, 0)
    blf.draw(0, text)


def _card_button(shader, rect, label, hover=False, accent=False,
                 dim=False):
    fill = (0.24, 0.24, 0.30, 0.97) if hover else \
        (0.16, 0.16, 0.20, 0.97)
    _card_fill(shader, rect, fill, r=5)
    colour = (0.55, 0.55, 0.58, 1.0) if dim else \
        (1.0, 0.85, 0.4, 1.0) if accent else (0.95, 0.95, 0.95, 1.0)
    width = _card_text_px(label, 11) or len(label) * 6.0
    _card_text(rect[0] + (rect[2] - rect[0] - width) / 2,
               rect[1] + 6, label, 11, colour)


def _draw_expert_card():
    """The floating Expert card over the 3D window. Drawn by
    Blender itself; must never raise."""
    try:
        prefs = _card_prefs()
        if not prefs["float"] or not _CARD["open"]:
            return
        region = bpy.context.region
        if region is None or region.type != "WINDOW":
            return
        import gpu
        wm = bpy.context.window_manager
        settings = _expert_settings()
        geo = _card_clamp_geo(
            region.width, region.height,
            _CARD["live"] or (prefs["x"], prefs["y"],
                              prefs["w"], prefs["h"]))
        shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        gpu.state.blend_set("ALPHA")
        shader.bind()
        if prefs["min"]:
            lay = _card_layout(geo, minimized=True)
            chip = lay["chip"]
            _card_fill(shader, chip, (0.05, 0.05, 0.07, 0.97), r=7)
            _card_fill(shader, (chip[0], chip[1] + 6, chip[0] + 5,
                                chip[3] - 6),
                       (1.0, 0.75, 0.25, 0.95), r=2)
            _card_text(chip[0] + 13, chip[1] + 8, "Buddy Expert",
                       11, (1.0, 0.85, 0.4, 1.0))
            _card_text(chip[2] - 18, chip[1] + 8, "+",
                       12, (0.95, 0.95, 0.95, 1.0))
            gpu.state.blend_set("NONE")
            return
        text_w = geo[2] - 2 * _CARD_PAD
        lines, footer = _card_sync_content(bpy.context, text_w)
        answer = (wm.buddy_answer or "").strip()
        plan = []
        try:
            plan = json.loads(wm.buddy_plan or "[]")
        except Exception:
            plan = []
        notice = bool((_EXPERT_TIP or "").strip()) and not answer \
            and not plan and not _EXPERT_JOB["busy"]
        lay = _card_layout(geo, notice=notice, footer=footer)
        lay["footer_kind"] = footer
        x, y, w, h = geo
        # The card itself, then its gold stripe and title band.
        _card_fill(shader, lay["card"], (0.05, 0.05, 0.07, 0.97),
                   r=10)
        _card_fill(shader, (x, y + 10, x + 5, y + h - 10),
                   (1.0, 0.75, 0.25, 0.95), r=2)
        _card_fill(shader, (x, lay["title"][1], x + w, y + h),
                   (0.10, 0.10, 0.13, 0.97), r=10)
        _card_fill(shader, (x, lay["title"][1], x + w,
                            lay["title"][1] + 10),
                   (0.10, 0.10, 0.13, 0.97), r=0)
        _card_text(x + 14, y + h - 18, "Buddy Expert", 13,
                   (1.0, 0.85, 0.4, 1.0))
        _card_button(shader, lay["btn_min"], "–",
                     hover=_CARD["hover"] == "btn_min")
        _card_button(shader, lay["btn_close"], "×",
                     hover=_CARD["hover"] == "btn_close")
        # Status line: the readiness truth, one line.
        status_lines = _card_wrap(_card_status_text(settings),
                                  text_w, 10)
        if status_lines:
            _card_text(lay["status"][0], lay["status"][1] + 3,
                       status_lines[0], 10, (0.75, 0.78, 0.85, 1.0))
        if notice:
            tip = _card_wrap(_EXPERT_TIP, text_w, 10)
            if tip:
                _card_text(lay["notice"][0], lay["notice"][1] + 3,
                           tip[0], 10, (1.0, 0.85, 0.4, 1.0))
        # Question field + Ask button.
        field = lay["field"]
        border = (1.0, 0.75, 0.25, 0.9) if _CARD["focused"] else \
            (0.35, 0.35, 0.40, 0.9)
        _card_fill(shader, (field[0] - 1, field[1] - 1,
                            field[2] + 1, field[3] + 1), border, r=6)
        _card_fill(shader, field, (0.02, 0.02, 0.03, 0.97), r=5)
        text = _CARD["text"]
        if not text and not _CARD["focused"]:
            _card_text(field[0] + 7, field[1] + 7,
                       "Ask in your own words...", 11,
                       (0.55, 0.55, 0.60, 1.0))
        else:
            caret = _CARD["caret"] if _CARD["focused"] else len(text)
            visible, caret_px = _card_field_view(
                text, caret, field[2] - field[0] - 14)
            _card_text(field[0] + 7, field[1] + 7, visible, 11,
                       (0.95, 0.95, 0.95, 1.0))
            if _CARD["focused"]:
                cx = field[0] + 7 + caret_px
                _card_fill(shader, (cx, field[1] + 5, cx + 1.5,
                                    field[3] - 5),
                           (1.0, 0.85, 0.4, 1.0), r=0)
        _card_button(shader, lay["btn_ask"], "Ask",
                     hover=_CARD["hover"] == "btn_ask", accent=True,
                     dim=bool(_EXPERT_JOB["busy"]))
        # Body: the answer / plan lines, scrolled.
        visible_n = lay["body_lines"]
        scroll = _card_clamp_scroll(_CARD["scroll"], len(lines),
                                    visible_n)
        _CARD["scroll"] = scroll
        body = lay["body"]
        for i, line in enumerate(lines[scroll:scroll + visible_n]):
            _card_text(body[0], body[3] - 12 - i * _CARD_LINE_H,
                       line, 11, (0.95, 0.95, 0.95, 1.0))
        if len(lines) > visible_n:
            track_x = body[2] + 4
            track = (track_x, body[1], track_x + 3, body[3])
            _card_fill(shader, track, (0.25, 0.25, 0.30, 0.8), r=2)
            frac = visible_n / len(lines)
            thumb_h = max(14, (body[3] - body[1]) * frac)
            off = (body[3] - body[1] - thumb_h) * \
                (scroll / max(1, len(lines) - visible_n))
            _card_fill(shader, (track_x, body[3] - thumb_h - off,
                                track_x + 3, body[3] - off),
                       (1.0, 0.75, 0.25, 0.9), r=2)
        # Footer buttons: the plan's Run press, or the advice
        # answer's one verified "Do it" press.
        if footer == "plan":
            _card_button(shader, lay["btn_run"], "Run these steps",
                         hover=_CARD["hover"] == "btn_run",
                         accent=True)
            _card_button(shader, lay["btn_clear"], "Throw away",
                         hover=_CARD["hover"] == "btn_clear")
        elif footer == "do":
            act = next((a for a in ACTIONS
                        if a["id"] == wm.buddy_suggested), None)
            if act:
                _card_button(shader, lay["btn_do"],
                             f"Do it: {act['plain']}"[:40],
                             hover=_CARD["hover"] == "btn_do",
                             accent=True)
        # Resize grip: two small bars in the bottom-right corner.
        grip = lay["grip"]
        _card_fill(shader, (grip[0] + 5, grip[1] + 3, grip[2] - 3,
                            grip[1] + 5), (0.45, 0.45, 0.50, 0.9), r=1)
        _card_fill(shader, (grip[2] - 5, grip[1] + 3, grip[2] - 3,
                            grip[3] - 4), (0.45, 0.45, 0.50, 0.9), r=1)
        gpu.state.blend_set("NONE")
    except Exception:
        pass


def _card_current_layout(context):
    """(layout, geo) for the event's region right now, or None when
    the card isn't up in it."""
    region = getattr(context, "region", None)
    area = getattr(context, "area", None)
    if region is None or region.type != "WINDOW":
        return None
    if area is None or area.type != "VIEW_3D":
        return None
    prefs = _card_prefs()
    if not prefs["float"] or not _CARD["open"]:
        return None
    geo = _card_clamp_geo(
        region.width, region.height,
        _CARD["live"] or (prefs["x"], prefs["y"],
                          prefs["w"], prefs["h"]))
    if prefs["min"]:
        return _card_layout(geo, minimized=True), geo
    wm = context.window_manager
    _lines, footer = _card_sync_content(
        context, geo[2] - 2 * _CARD_PAD)
    answer = (wm.buddy_answer or "").strip()
    plan = []
    try:
        plan = json.loads(wm.buddy_plan or "[]")
    except Exception:
        plan = []
    notice = bool((_EXPERT_TIP or "").strip()) and not answer \
        and not plan and not _EXPERT_JOB["busy"]
    lay = _card_layout(geo, notice=notice, footer=footer)
    lay["footer_kind"] = footer
    return lay, geo


def _card_do_ask(context):
    """Ask from the card: the exact panel path - the buffer becomes
    wm.buddy_ask and buddy.ask_expert does the rest (capability
    answers, setup messages, named faults, plan parsing)."""
    if _EXPERT_JOB["busy"]:
        return
    context.window_manager.buddy_ask = _CARD["text"]
    _CARD["scroll"] = 0
    try:
        bpy.ops.buddy.ask_expert()
    except Exception:
        context.window_manager.buddy_answer = "Buddy couldn't submit this request. Try Ask again."
    _card_tag_redraw()


class BUDDY_OT_expert_card_open(Operator):
    bl_idname = "buddy.expert_card_open"
    bl_label = "Open the Floating Expert"
    bl_description = ("Show the Buddy Expert as a floating card "
                      "over the 3D window - drag it by its title "
                      "bar, resize it from its corner, minimise "
                      "it to the corner chip")
    bl_options = {"REGISTER"}

    def execute(self, context):
        _CARD["open"] = True
        try:
            prefs = bpy.context.preferences.addons[
                __name__].preferences
            if not prefs.expert_float:
                prefs.expert_float = True
            if prefs.expert_card_min:
                prefs.expert_card_min = False
        except Exception:
            pass
        _card_autostart()
        _card_tag_redraw()
        return {"FINISHED"}


class BUDDY_OT_expert_card_modal(Operator):
    bl_idname = "buddy.expert_card_modal"
    bl_label = "Buddy Expert Card"
    bl_description = ("Run the floating Expert card: drag, resize, "
                      "minimise, type - everything outside the card "
                      "passes straight through to Blender")
    bl_options = {"INTERNAL"}

    _timer = None

    def invoke(self, context, event):
        if _card_has_listener(context.window):
            return {"CANCELLED"}
        self._timer = context.window_manager.event_timer_add(
            0.25, window=context.window)
        context.window_manager.modal_handler_add(self)
        _CARD_INPUT_WINDOWS.add(context.window.as_pointer())
        _CARD["modal"] = True
        return {"RUNNING_MODAL"}

    def _stop(self, context):
        if self._timer is not None:
            try:
                context.window_manager.event_timer_remove(self._timer)
            except Exception:
                pass
            self._timer = None
        _CARD_INPUT_WINDOWS.discard(context.window.as_pointer())
        _CARD["modal"] = bool(_CARD_INPUT_WINDOWS)
        _CARD["drag"] = None
        _CARD["live"] = None

    def modal(self, context, event):
        try:
            if not _CARD["open"] or not _card_prefs()["float"]:
                self._stop(context)
                return {"FINISHED"}
            if event.type == "TIMER":
                return self._modal(context, event)
            # Modal context can point to the viewport where it started even
            # when the user is interacting with a newly split 3D View.
            for area in context.window.screen.areas:
                if area.type != "VIEW_3D":
                    continue
                for region in area.regions:
                    if region.type != "WINDOW":
                        continue
                    if _CARD["drag"]:
                        accepts = _CARD["drag"].get("region") == region.as_pointer()
                    else:
                        accepts = (region.x <= event.mouse_x < region.x + region.width and
                                   region.y <= event.mouse_y < region.y + region.height)
                    if accepts:
                        with context.temp_override(window=context.window, area=area, region=region):
                            return self._modal(context, event)
            if event.type == "LEFTMOUSE" and event.value == "PRESS":
                _CARD["focused"] = False
            return {"PASS_THROUGH"}
        except Exception:
            return {"PASS_THROUGH"}

    def _modal(self, context, event):
        if event.type == "TIMER":
            sig = _card_signature(context)
            if sig != _CARD["sig"]:
                _CARD["sig"] = sig
                _card_tag_redraw()
            return {"PASS_THROUGH"}
        # An in-progress drag owns the mouse until it lets go,
        # wherever the pointer has wandered.
        if _CARD["drag"] is not None:
            if event.type == "MOUSEMOVE":
                self._drag_move(context, event)
                return {"RUNNING_MODAL"}
            if event.type == "LEFTMOUSE" and \
                    event.value == "RELEASE":
                if _CARD["live"] is not None:
                    _card_save_geo(_CARD["live"])
                _CARD["drag"] = None
                _CARD["live"] = None
                _card_tag_redraw()
                return {"RUNNING_MODAL"}
            return {"PASS_THROUGH"}
        prefs = _card_prefs()
        if not prefs["float"] or not _CARD["open"]:
            self._stop(context)
            return {"FINISHED"}
        got = _card_current_layout(context)
        if got is None:
            if event.type == "LEFTMOUSE" and event.value == "PRESS":
                _CARD["focused"] = False
            return {"PASS_THROUGH"}
        lay, geo = got
        mx, my = event.mouse_x - context.region.x, event.mouse_y - context.region.y
        hit = _card_hit(lay, mx, my)
        if _CARD["focused"] and _CARD["focus_region"] == context.region.as_pointer() and \
                event.value == "PRESS" and \
                self._type_key(context, event):
            return {"RUNNING_MODAL"}
        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            return self._click(context, lay, geo, hit, mx, my)
        if event.type in ("WHEELUPMOUSE", "WHEELDOWNMOUSE"):
            if hit is not None:
                lines, _f = _card_sync_content(
                    context, geo[2] - 2 * _CARD_PAD)
                step = 3 if event.type == "WHEELDOWNMOUSE" else -3
                _CARD["scroll"] = _card_clamp_scroll(
                    _CARD["scroll"] + step, len(lines),
                    lay.get("body_lines", 1))
                _card_tag_redraw()
                return {"RUNNING_MODAL"}
            return {"PASS_THROUGH"}
        if event.type == "MOUSEMOVE":
            if hit != _CARD["hover"]:
                _CARD["hover"] = hit
                _card_tag_redraw()
            return {"PASS_THROUGH"}
        return {"PASS_THROUGH"}

    def _click(self, context, lay, geo, hit, mx, my):
        if hit is None:
            _CARD["focused"] = False
            return {"PASS_THROUGH"}
        if hit == "chip":
            _card_save_min(False)
            _card_tag_redraw()
            return {"RUNNING_MODAL"}
        if hit == "btn_close":
            _CARD["open"] = False
            _CARD["focused"] = False
            _card_tag_redraw()
            self._stop(context)
            return {"FINISHED"}
        if hit == "btn_min":
            _card_save_min(True)
            _CARD["focused"] = False
            _card_tag_redraw()
            return {"RUNNING_MODAL"}
        if hit == "btn_ask":
            _card_do_ask(context)
            return {"RUNNING_MODAL"}
        if hit == "btn_run":
            _CARD["scroll"] = 0
            try:
                bpy.ops.buddy.run_plan()
            except Exception:
                pass
            _card_tag_redraw()
            return {"RUNNING_MODAL"}
        if hit == "btn_clear":
            try:
                bpy.ops.buddy.clear_plan()
            except Exception:
                pass
            _card_tag_redraw()
            return {"RUNNING_MODAL"}
        if hit == "btn_do":
            sid = context.window_manager.buddy_suggested
            if sid in _expert_buttons():
                try:
                    bpy.ops.buddy.action(action_id=sid)
                except Exception:
                    pass
            _card_tag_redraw()
            return {"RUNNING_MODAL"}
        if hit == "title":
            _CARD["drag"] = {"mode": "move", "dx": mx - geo[0],
                             "dy": my - geo[1], "geo": geo, "region": context.region.as_pointer()}
            _CARD["live"] = geo
            return {"RUNNING_MODAL"}
        if hit == "grip":
            _CARD["drag"] = {"mode": "resize", "mx": mx, "my": my,
                             "geo": geo, "region": context.region.as_pointer()}
            _CARD["live"] = geo
            return {"RUNNING_MODAL"}
        if hit == "field":
            _CARD["focused"] = True
            _CARD["focus_region"] = context.region.as_pointer()
            _CARD["caret"] = len(_CARD["text"])
            _card_tag_redraw()
            return {"RUNNING_MODAL"}
        # Any other press on the card is the card's, not Blender's.
        _CARD["focused"] = False
        return {"RUNNING_MODAL"}

    def _drag_move(self, context, event):
        drag = _CARD["drag"]
        region = context.region
        mx, my = event.mouse_x - region.x, event.mouse_y - region.y
        sx, sy, sw, sh = drag["geo"]
        if drag["mode"] == "move":
            geo = (mx - drag["dx"], my - drag["dy"], sw, sh)
        else:
            # The grip is the BOTTOM-right corner and region y
            # grows upward: dragging right widens, dragging down
            # lengthens - with the card's TOP edge held fixed.
            nw = sw + (mx - drag["mx"])
            nh = sh + (drag["my"] - my)
            geo = (sx, sy + sh - nh, nw, nh)
        _CARD["live"] = _card_clamp_geo(region.width, region.height,
                                        geo)
        _card_tag_redraw()

    def _type_key(self, context, event):
        """One keypress while the question field is focused.
        Returns True when the card took it."""
        text = _CARD["text"]
        caret = max(0, min(_CARD["caret"], len(text)))
        if event.type == "ESC":
            _CARD["focused"] = False
            _card_tag_redraw()
            return True
        if event.type in ("RET", "NUMPAD_ENTER"):
            _card_do_ask(context)
            return True
        if event.type == "BACK_SPACE":
            if caret > 0:
                _CARD["text"] = text[:caret - 1] + text[caret:]
                _CARD["caret"] = caret - 1
            _card_tag_redraw()
            return True
        if event.type == "DEL":
            if caret < len(text):
                _CARD["text"] = text[:caret] + text[caret + 1:]
            _card_tag_redraw()
            return True
        if event.type == "LEFT_ARROW":
            _CARD["caret"] = max(0, caret - 1)
            _card_tag_redraw()
            return True
        if event.type == "RIGHT_ARROW":
            _CARD["caret"] = min(len(text), caret + 1)
            _card_tag_redraw()
            return True
        if event.type == "HOME":
            _CARD["caret"] = 0
            _card_tag_redraw()
            return True
        if event.type == "END":
            _CARD["caret"] = len(text)
            _card_tag_redraw()
            return True
        if event.type == "V" and (event.ctrl or (sys.platform == "darwin" and event.oskey)):
            try:
                clip = context.window_manager.clipboard or ""
            except Exception:
                clip = ""
            if clip:
                clip = " ".join(clip.split())
                _CARD["text"] = text[:caret] + clip + text[caret:]
                _CARD["caret"] = caret + len(clip)
            _card_tag_redraw()
            return True
        ch = getattr(event, "unicode", "") or ""
        if ch and ch.isprintable():
            _CARD["text"] = text[:caret] + ch + text[caret:]
            _CARD["caret"] = caret + 1
            _card_tag_redraw()
            return True
        return False


def _card_autostart():
    """Keep the drawn card interactive after opening a file or another window."""
    if bpy.app.background:
        return None
    if _CARD["open"] and _card_prefs()["float"]:
        windows = bpy.context.window_manager.windows
        _CARD_INPUT_WINDOWS.intersection_update(win.as_pointer() for win in windows)
        for win in windows:
            if _card_has_listener(win):
                continue
            origin = next(((a, r) for a in win.screen.areas if a.type == "VIEW_3D"
                           for r in a.regions if r.type == "WINDOW"), None)
            if origin is None:
                continue
            area, region = origin
            try:
                with bpy.context.temp_override(window=win, area=area, region=region):
                    bpy.ops.buddy.expert_card_modal("INVOKE_DEFAULT")
            except (ReferenceError, RuntimeError):
                continue  # The window may be changing workspaces or loading a file.
    return 0.75


# ----------------------------------------------------------------------------
# The panel
# ----------------------------------------------------------------------------

_WRAP_CAP = 64
_WRAP_PX = None


def _fit_width(context):
    """How many characters actually fit across the panel right now.
    Blender cuts off (with '...') any label longer than the panel,
    so wrapping has to aim at the real width, not a guess. That was
    learned from actual screenshots of this panel (v0.9): at the
    default sidebar width the old fixed guesses clipped words.
    Also records the panel's pixel width in _WRAP_PX: the char
    estimate alone still lost words inside nested boxes (the
    guided-project card sits two boxes deep, narrower than the
    region it was measured against - walkthrough gap X1), so
    _wrap now verifies every line by measurement, below."""
    global _WRAP_PX
    try:
        w = context.region.width
    except Exception:
        return 44
    if not w:
        return 44
    _WRAP_PX = w
    return max(26, min(64, int((w - 48) / 6.2)))


def _text_px(text):
    """The measured pixel width of a line in the panel's font,
    or None when it cannot be measured in this session."""
    try:
        import blf
        scale = 1.0
        try:
            scale = float(
                bpy.context.preferences.view.ui_scale) or 1.0
        except Exception:
            pass
        blf.size(0, max(8, int(round(11 * scale))))
        return blf.dimensions(0, text)[0]
    except Exception:
        return None


def _fit_line(line, max_px):
    """Split one wrapped line until every piece MEASURES
    inside max_px. Words move whole to the next piece; a
    single word wider than the panel is hard-split. Nothing
    is ever dropped - losing words mid-sentence was gap X1's
    whole injury."""
    width = _text_px(line)
    if width is None or width <= max_px:
        return [line]
    out = []
    cur = ""
    # A standalone dash glues to the word after it: split
    # on its other side and the dash is stranded at a line
    # end or alone on a line (re-walk minor m2).
    words = []
    for word in line.split(" "):
        if words and words[-1] == "-":
            words[-1] = "- " + word
        else:
            words.append(word)
    for word in words:
        trial = f"{cur} {word}" if cur else word
        if cur and (_text_px(trial) or 0) > max_px:
            out.append(cur)
            cur = word
        else:
            cur = trial
        while cur and (_text_px(cur) or 0) > max_px \
                and len(cur) > 1:
            cut = len(cur) - 1
            while cut > 1 and (_text_px(cur[:cut]) or 0) > max_px:
                cut -= 1
            out.append(cur[:cut])
            cur = cur[cut:]
    if cur:
        out.append(cur)
    return out


def _wrap_lines(text, width=44):
    """The lines _wrap will draw for a string: wrapped by the
    char estimate, then - when this panel's real pixel width
    is known - every line is re-split until it measures
    inside the space the deepest card actually gets (region
    width minus the nesting: section indent, card box and
    label padding), with a safety margin for font variance.
    The words of the text survive whole, in order - the
    invariant the X1 regression test asserts."""
    width = max(20, min(width, _WRAP_CAP))
    # break_on_hyphens=False: a key name like
    # "Alt+left-drag" or "Ctrl+right-click" must never be
    # chopped at its hyphen across lines - a chopped key
    # name reads as a different, wrong instruction.
    lines = textwrap.wrap(text, width=width,
                          break_on_hyphens=False) or [""]
    budget = None
    if _WRAP_PX:
        budget = (_WRAP_PX - 72) * 0.92
        if budget > 40:
            fitted = []
            for line in lines:
                fitted.extend(_fit_line(line, budget))
            lines = fitted
        else:
            budget = None
    # A dash that wraps onto a line of its own reads as a
    # stray mark on the card (re-walk minor m2): glue it
    # onto the line it belongs with - the next one when
    # that still measures inside the budget, else the end
    # of the previous one. Only line breaks move; the
    # words themselves never change, so the no-lost-words
    # invariant the tests assert still holds.
    merged = []
    i = 0
    while i < len(lines):
        if lines[i].strip() == "-" and i + 1 < len(lines):
            joined = "- " + lines[i + 1]
            if budget is None or (_text_px(joined) or 0) <= budget:
                merged.append(joined)
                i += 2
                continue
            if merged and (_text_px(merged[-1] + " -") or 0) \
                    <= budget:
                merged[-1] = merged[-1] + " -"
                i += 1
                continue
            if budget:
                # Neither side has room: refit the pair as
                # one string (the dash stays glued to its
                # word inside _fit_line).
                merged.extend(_fit_line(joined, budget))
                i += 2
                continue
        merged.append(lines[i])
        i += 1
    return merged


def _wrap(layout, text, width=44):
    for line in _wrap_lines(text, width=width):
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


def _query_active(context):
    wm = getattr(context, "window_manager", None)
    return bool(wm and (wm.buddy_query or "").strip())


def _start_screen_active(context):
    ws = getattr(context, "workspace", None)
    return (ws is not None and ws.name == "Buddy Start"
            and not getattr(context.scene, "buddy_tour_started",
                            False))


class VIEW3D_PT_buddy_expert_launcher(Panel):
    bl_idname = "VIEW3D_PT_buddy_expert_launcher"
    bl_label = "Buddy Expert"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender Buddy"
    bl_options = {"HIDE_HEADER"}
    bl_order = -1000

    def draw(self, context):
        row = self.layout.row()
        row.scale_y = 1.25
        row.operator("buddy.expert_card_open", text="Open Buddy Expert")


class VIEW3D_PT_blender_buddy(Panel):
    """The host panel. It used to draw EVERYTHING itself - one
    long scrolling tab (owner, 2026-11-13: "blender buddy cannot
    be 1 long tab, needs to be collapsible sections"). Now every
    major block is its own collapsible section under this host:
    the guided project, Where you are, Heads up, For right now,
    the Expert, the tool drawers, projects, search and the full
    index. Only the live blocks open by default; the rest are a
    tidy list of named drawers. This host draws just the Start
    screen (a whole-panel mode) and the changed-tools notice,
    which must never hide inside a closed drawer."""
    bl_idname = "VIEW3D_PT_blender_buddy"
    bl_label = "Blender Buddy - in plain words"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Blender Buddy"

    def draw(self, context):
        global _WRAP_CAP
        _WRAP_CAP = _fit_width(context)
        layout = self.layout
        if not _query_active(context) and _start_screen_active(context):
            _draw_start(layout, context)
            return
        stale = _stale_map()
        stale_settings = _stale_settings()
        # Peek only: the styles probe creates and removes data,
        # which Blender forbids during a panel draw - when it ran
        # from here, every style failed its dry-run at once and
        # all seven were hidden as stale on a Blender where they
        # work (GUI proof, 2026-11-13). register() runs the probe;
        # until it has, the notice simply omits styles.
        stale_styles = _STALE_STYLES_CACHE or set()
        if stale or stale_settings or stale_styles:
            box = layout.box()
            box.label(text="This Blender changed some tools",
                      icon="ERROR")
            bits = []
            if stale:
                names = "; ".join(ACTIONS_BY_ID[i]["plain"]
                                  for i in stale)
                bits.append(f"{len(stale)} of Buddy's buttons: "
                            f"{names}")
            if stale_settings:
                names = "; ".join(SETTINGS[k]["label"]
                                  for k in stale_settings)
                bits.append(f"expert settings: {names}")
            if stale_styles:
                names = "; ".join(STYLES[k][0] for k in stale_styles)
                bits.append(f"expert styles: {names}")
            _wrap(box, "Some of what Buddy offers was made for an "
                       f"older Blender and doesn't match this one "
                       f"(Blender {bpy.app.version_string}), so it's "
                       f"hidden instead of failing on you - "
                       + "; ".join(bits)
                       + ". Everything else works as normal, and "
                       "every tool this Blender actually has is in "
                       "the index below.")


def _draw_tour(layout, context):
    """The guided project's strip + step card, in its own
    section, shown only while a project runs."""
    global _TOUR_TIP_STEP, _EXPERT_TIP
    wm = context.window_manager
    show_real = getattr(wm, "buddy_show_real", True)
    scene = context.scene
    _draw_strip(layout, context)
    box = layout.box()
    pkg = _active_package(context)
    steps = pkg["steps"]
    checks, current = tour_state(context)
    # Done = the passing PREFIX, the same number the
    # header's "step N of 8" derives from. This used to be
    # sum(checks) - every passing check anywhere - so a
    # later step passing early (or an earlier one dropping
    # out mid-procedure) made "Done so far" contradict the
    # header and flip between unrelated operations
    # (re-walk M3: 1 -> 2 -> 1 -> 2 under a header that
    # never left step 2). One computation serves both.
    done = current
    if current != _TOUR_TIP_STEP:
        _TOUR_TIP_STEP = current
        if current >= len(steps):
            _EXPERT_TIP = "You finished it. Ask me anything."
        else:
            _EXPERT_TIP = (f"{pkg['name']}, step {current + 1}: "
                           f"{steps[current]['title']}.")
    if current >= len(steps):
        box.label(text=f"You finished: {pkg['name']}",
                  icon="CHECKMARK")
        skills = "; ".join(s["skill"].split(":")[0] for s in steps)
        _wrap(box, "You did every step yourself, in real "
                   "Blender. Skills this project touched: "
                   f"{skills}. Everything after this is "
                   "just more tools, in the drawers below.")
        box.operator("buddy.tour_hide", text="Hide this")
        return
    step = steps[current]
    box.label(text=f"Step {current + 1} of {len(steps)}: "
                   f"{pkg['name']}", icon="MESH_TORUS")
    _wrap(box, step["title"])
    _wrap(box, step["how"])
    video = step.get("video")
    if video:
        op = box.operator("wm.url_open", text=video["label"],
                          icon="URL")
        op.url = video["url"]
    box.prop(scene, "buddy_show_lesson",
             text="Hide the full lesson"
             if getattr(scene, "buddy_show_lesson", False)
             else "Show the full lesson", toggle=True)
    if getattr(scene, "buddy_show_lesson", False):
        _wrap(box, f"The skill: {step['skill']}.")
        for line in step["teach"]:
            _wrap(box, line)
    shown = []
    for tid in step.get("tools") or []:
        act = ACTIONS_BY_ID.get(tid)
        if act and _action_available(act, context):
            shown.append(act)
    if shown:
        box.label(text="Tools for this step", icon="TOOL_SETTINGS")
        for act in shown:
            _draw_action(box, act, show_real)
    if not checks[current]:
        _wrap(box, f"Not yet: {step['missing']}")
    _wrap(box, f"Done so far: {done} of {len(steps)}. "
               "Do the step up there in Blender - "
               "this card watches your scene and "
               "moves on by itself when it's done.")
    box.operator("buddy.tour_hide", text="Hide for now")


def _draw_now(layout, context):
    wm = context.window_manager
    show_real = getattr(wm, "buddy_show_real", True)
    _wrap(layout, _hint(context))
    facts = _scene_facts(context)
    for act in _now_deck(context, facts=facts):
        _draw_action(layout, act, show_real)
    _wrap(layout, f"Buddy is showing the "
                  f"{len(_available_actions(context, facts))} "
                  f"tools (of {len(ACTIONS)}) that can be used "
                  f"right now. The rest appear the moment "
                  f"they're usable - pick something, switch "
                  f"mode, and this panel keeps up. Everything "
                  f"Blender has is always in the index at the "
                  f"bottom.")


def _draw_expert(layout, context):
    wm = context.window_manager
    layout.prop(wm, "buddy_agent", text="Expert help with tasks")
    _wrap(layout, "Turn on to review a plan before running it. Turn off for advice.")
    settings = _expert_settings()
    if not _expert_ready(settings):
        _wrap(layout, _expert_setup_message(settings))
    layout.operator("buddy.open_prefs", text="Expert connection settings")


def _draw_found_resources(layout, context):
    wm = context.window_manager
    results = []
    try:
        results = json.loads(wm.buddy_find or "[]")
    except Exception:
        results = []
    if results:
        layout.label(text="Found for you - links checked",
                     icon="URL")
        for r in results:
            op = layout.operator(
                "wm.url_open",
                text=f"{r['name']} ({r['source']})")
            op.url = r["url"]


def _draw_search(layout, context):
    wm = context.window_manager
    show_real = getattr(wm, "buddy_show_real", True)
    _wrap(layout, "Type what you want to do in your own "
                  "words - 'make it round', 'copy it', 'make "
                  "a hole'. What you can use right now appears "
                  "below.")
    layout.prop(wm, "buddy_query", text="")
    query = getattr(wm, "buddy_query", "")
    if query.strip():
        hits = search_actions(query, available_only=True,
                              context=context)
        if hits:
            for act in hits[:10]:
                _draw_action(layout, act, show_real)
        else:
            _wrap(layout, "Nothing you can use right now matches "
                          "that. It may need a picked thing or a "
                          "different mode first - or try everyday "
                          "words: round, copy, hole, smooth, move, "
                          "thicker, colour, delete.")
    layout.prop(wm, "buddy_show_real",
                text="Also show Blender's real names")


def _draw_index(layout, context):
    wm = context.window_manager
    query = getattr(wm, "buddy_query", "")
    index = build_index()
    _wrap(layout, f"The plain-words buttons above are the everyday set. "
                  f"Blender has {len(index)} tools in total in this "
                  f"version - and every single one of them is reachable "
                  f"from here, so nothing is lost. Type any part of a "
                  f"name or job in the search box at the top and matches "
                  f"appear below, with Blender's own one-line explanation.")
    if query.strip():
        hits = search_index(query)
        if hits:
            for e in hits:
                row = layout.row(align=True)
                op = row.operator("buddy.run_any",
                                  text=e["label"] or e["idname"])
                op.op_id = e["idname"]
                col = layout.column()
                col.scale_y = 0.8
                if e["desc"]:
                    _wrap(col, e["desc"])
                _wrap(col, f"Blender's name for it: {e['idname']}", width=52)
                layout.separator(factor=0.6)
        else:
            _wrap(layout, "No tool in the whole of Blender matches that. "
                          "Try fewer or different words.")
    else:
        _wrap(layout, "These keep Blender's own names - they're the long "
                      "tail, there are thousands, and most people need "
                      "only a few. If you find yourself using one a lot, "
                      "it deserves a plain-words button above.")


def _make_block_panel(idname, label, order, draw_fn, poll_fn=None,
                      default_closed=False, icon=None):
    """One collapsible section of the main panel - the same
    factory discipline as the tool drawers (layout.panel doesn't
    exist in 4.2.5's Python API), applied to the panel's own
    blocks so the tab is a list of sections, not a scroll."""
    def draw(self, context):
        global _WRAP_CAP
        _WRAP_CAP = _fit_width(context)
        draw_fn(self.layout, context)

    def poll(cls, context):
        if poll_fn is None:
            return True
        try:
            return poll_fn(context)
        except Exception:
            return True

    attrs = {
        "bl_idname": idname,
        "bl_label": label,
        "bl_space_type": "VIEW_3D",
        "bl_region_type": "UI",
        "bl_category": "Blender Buddy",
        "bl_parent_id": "VIEW3D_PT_blender_buddy",
        "bl_order": order,
        "draw": draw,
        "poll": classmethod(poll),
    }
    if default_closed:
        attrs["bl_options"] = {"DEFAULT_CLOSED"}
    return type(idname, (Panel,), attrs)


def _poll_not_searching(context):
    return not _query_active(context) and not _start_screen_active(context)


def _poll_tour(context):
    return (getattr(context.scene, "buddy_tour_started", False)
            and not _query_active(context))


def _poll_headsup(context):
    return (_poll_not_searching(context)
            and bool(_visible_traps(context)))


VIEW3D_PT_buddy_tour = _make_block_panel(
    "VIEW3D_PT_buddy_tour", "Guided project", -100, _draw_tour,
    poll_fn=_poll_tour)
VIEW3D_PT_buddy_where = _make_block_panel(
    "VIEW3D_PT_buddy_where", "Where you are", -90,
    lambda layout, context: _draw_where(layout, context, boxed=False),
    poll_fn=_poll_not_searching)
VIEW3D_PT_buddy_headsup = _make_block_panel(
    "VIEW3D_PT_buddy_headsup", "Heads up", -80,
    lambda layout, context: _draw_heads_up(layout, context,
                                           boxed=False),
    poll_fn=_poll_headsup)
VIEW3D_PT_buddy_now = _make_block_panel(
    "VIEW3D_PT_buddy_now", "For right now", -70, _draw_now,
    poll_fn=_poll_not_searching)
VIEW3D_PT_buddy_expert = _make_block_panel(
    "VIEW3D_PT_buddy_expert", "Expert settings", -60, _draw_expert,
    poll_fn=_poll_not_searching, default_closed=True)
VIEW3D_PT_buddy_found_resources = _make_block_panel(
    "VIEW3D_PT_buddy_found_resources", "Found resources", -59, _draw_found_resources,
    poll_fn=lambda context: bool(context.window_manager.buddy_find))
VIEW3D_PT_buddy_search = _make_block_panel(
    "VIEW3D_PT_buddy_search", "What do you want to do?", 100,
    _draw_search, default_closed=True)
VIEW3D_PT_buddy_index = _make_block_panel(
    "VIEW3D_PT_buddy_index", "Everything else Blender can do", 110,
    _draw_index, default_closed=True)



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
        if target == "reshape_as_circle":
            return otype == "MESH" and mode == "OBJECT"
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
        # Land the learner on Buddy's own panel: starting a job
        # promises "step 1 is at the top of the Blender Buddy
        # panel", so the sidebar must at least be OPEN when
        # conducting moves the learner (fix round 13, finding
        # F1). Which tab it shows is the workspace's saved
        # state - Python cannot set a region's active panel
        # category (read-only at runtime, proven on 4.2.5 and
        # 5.3.0 in that round) - so the Buddy template's screens
        # are saved with Buddy's own tab active instead.
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            for space in area.spaces:
                if space.type == "VIEW_3D":
                    try:
                        space.show_region_ui = True
                    except Exception:
                        pass
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


def _draw_where(layout, context, boxed=True):
    box = layout.box() if boxed else layout
    if boxed:
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


def _draw_heads_up(layout, context, boxed=True):
    for trap in _visible_traps(context):
        box = layout.box() if boxed else layout
        if boxed:
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
                row.label(text=f"Step {current + 1} of "
                               f"{len(pkg['steps'])}: "
                               f"{pkg['name']}")
            else:
                row.label(text=f"Finished: {pkg['name']}")
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
    box.label(text=f"Step {current + 1} of "
                   f"{len(pkg['steps'])}: {pkg['name']}",
              icon="INFO")
    _wrap(box, step["title"])
    for act in _now_deck(context, limit=4):
        _draw_action_compact(box, act)


# The honest scope, stated where a learner lands first
# (owner, 2026-11-19): Buddy covers modeling follow-alongs
# today; it does not yet cover sculpting, animation, or the
# other crafts, and nothing may imply it does. The Donut's
# little sculpting passage is a finishing touch inside a
# modeling project, not sculpting coverage - the box says
# so. Each craft arrives in its own shape, taught the way
# that craft actually works.
_COVERAGE_TITLE = "What Buddy covers today"
_COVERAGE_LINES = (
    "Buddy teaches modeling. The Donut below is a "
    "follow-along: empty scene to finished picture, your "
    "work checked as you go. The tools are plain-words "
    "buttons for the everyday modeling jobs.",
    "It does not teach sculpting, animation, or the other "
    "crafts yet.",
    "The Donut does use a little sculpting near the end, "
    "as a finishing touch on the icing. That is a taste "
    "of it - not sculpting lessons.",
    "Each craft is being added one at a time, taught the "
    "way that craft actually works - a sculpt is not "
    "made the way a model is.",
)


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
                  "keyboard).")
    box = layout.box()
    box.label(text=_COVERAGE_TITLE, icon="INFO")
    for line in _COVERAGE_LINES:
        _wrap(box, line)
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
           BUDDY_OT_expert_wait, BUDDY_OT_open_codex,
           BUDDY_OT_expert_card_open, BUDDY_OT_expert_card_modal,
           BUDDY_OT_pie, BUDDY_OT_build_screens,
           BUDDY_OT_mode_back, BUDDY_OT_origin_center,
           BUDDY_OT_origin_bottom, BUDDY_OT_cursor_home,
           BUDDY_OT_cursor_to_picked, BUDDY_OT_lock_in,
           BUDDY_OT_show_everything, BUDDY_OT_mute_trap,
           VIEW3D_MT_buddy_pie,
           VIEW3D_PT_buddy_expert_launcher, VIEW3D_PT_blender_buddy,
           VIEW3D_PT_buddy_tour, VIEW3D_PT_buddy_where,
           VIEW3D_PT_buddy_headsup, VIEW3D_PT_buddy_now,
           VIEW3D_PT_buddy_expert, VIEW3D_PT_buddy_found_resources,
           VIEW3D_PT_buddy_search,
           VIEW3D_PT_buddy_index,
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
    bpy.types.Scene.buddy_render_done = BoolProperty(
        name="A render was completed",
        description="Buddy's render-complete handler sets this the "
                    "moment a render finishes, so the picture steps "
                    "can prove a render happened even after the "
                    "file is saved and reopened (the Render Result "
                    "itself is not saved, and on Blender 5.3 it "
                    "reports no data even while it is on screen)",
        default=False,
    )
    bpy.types.Scene.buddy_final_render_done = BoolProperty(
        name="A final-stage render was completed",
        description="Buddy's render-complete handler sets this "
                    "when a render finishes with the finale's "
                    "rig standing complete, so the last step can "
                    "prove its render belongs to the finale - an "
                    "earlier step's render cannot prove that "
                    "(W4, GAP 8-4)",
        default=False,
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
        name="Expert help with tasks",
        description="On: describe a job and the expert drafts the "
                    "steps for it - you check them, and you run "
                    "them when you're ready. Off: the expert gives "
                    "advice, explanations and exact values for you "
                    "to use yourself",
        default=True, options={"SKIP_SAVE"}, get=_task_mode_get, set=_task_mode_set)
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
    bpy.types.WindowManager.buddy_find = StringProperty(
        name="Expert resource results", default="")
    bpy.types.WindowManager.buddy_muted = StringProperty(
        name="Heads-ups already got",
        description="Which plain-words heads-ups you've "
                    "already said 'got it' to (this session)",
        default="[]")
    global _EXPERT_HANDLE
    try:
        _EXPERT_HANDLE = bpy.types.SpaceView3D.draw_handler_add(
            _draw_expert_card, (), "WINDOW", "POST_PIXEL")
    except Exception:
        _EXPERT_HANDLE = None
    if _card_file_loaded not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_card_file_loaded)
    if not bpy.app.background:
        try:
            # persistent: a non-persistent timer is wiped when the
            # startup file loads, which is exactly when this one
            # is registered (rig proof, fix round 11).
            bpy.app.timers.register(_card_autostart,
                                    first_interval=0.6,
                                    persistent=True)
        except Exception:
            pass
    _install_template()
    if _expert_job_discard not in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.append(_expert_job_discard)
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
    try:
        if _buddy_grade_save not in bpy.app.handlers.save_post:
            bpy.app.handlers.save_post.append(_buddy_grade_save)
        if _buddy_grade_save not in bpy.app.handlers.load_post:
            bpy.app.handlers.load_post.append(_buddy_grade_save)
    except Exception:
        pass
    try:
        if _buddy_mark_render not in \
                bpy.app.handlers.render_complete:
            bpy.app.handlers.render_complete.append(
                _buddy_mark_render)
    except Exception:
        pass
    _register_tools()
    # Run the styles dry-probe HERE, in register's context: it
    # creates and removes a scratch object and materials, work
    # Blender forbids while a panel is drawing. A probe failure
    # must never break registration - it just leaves the cache
    # unset, and operator contexts will run the probe later.
    try:
        _stale_styles()
    except Exception:
        pass
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
    _expert_job_discard()
    if _expert_job_discard in bpy.app.handlers.load_pre:
        bpy.app.handlers.load_pre.remove(_expert_job_discard)
    if bpy.app.timers.is_registered(_expert_job_tick):
        bpy.app.timers.unregister(_expert_job_tick)
    if _card_file_loaded in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(_card_file_loaded)
    _CARD_INPUT_WINDOWS.clear()
    try:
        if bpy.app.timers.is_registered(_card_autostart):
            bpy.app.timers.unregister(_card_autostart)
    except Exception:
        pass
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
                 "buddy_find", "buddy_muted"):
        if hasattr(bpy.types.WindowManager, attr):
            delattr(bpy.types.WindowManager, attr)
    for attr in ("buddy_tour_started", "buddy_show_lesson",
                 "buddy_tour_epoch", "buddy_render_done",
                 "buddy_final_render_done", "buddy_tour_package"):
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
    for _handlers in (bpy.app.handlers.save_post,
                      bpy.app.handlers.load_post):
        try:
            _handlers.remove(_buddy_grade_save)
        except Exception:
            pass
    try:
        bpy.app.handlers.render_complete.remove(
            _buddy_mark_render)
    except Exception:
        pass
    for cls in reversed(CLASSES):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
