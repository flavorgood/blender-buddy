"""Blender Buddy loose-search proof (v0.3).

Run with:
  blender -b --factory-startup --python tests/test_search.py

The standard: someone who does NOT know what a tool is called still
finds it - everyday synonyms, half-words, US spellings and outright
typos - while gibberish still finds nothing.
"""
import os
import sys
import time

import bpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import blender_buddy as bb  # noqa: E402

bb.register()


def curated(query):
    return [a["id"] for a in bb.search_actions(query)]


def indexed(query):
    return [e["idname"] for e in bb.search_index(query)]


# --- curated: loose language finds the plain-words buttons -------------------
CASES = [
    ("bevell", "round_edge"),          # typo of bevel
    ("extrud", "pull_face"),           # half-word
    ("squish it flat", "tool_size"),   # loose everyday word
    ("spin the thing", "tool_turn"),   # synonym
    ("color it red", "give_colour"),   # US spelling
    ("make a hole", "cut_hole"),
    ("clone this", "copy_it"),         # synonym for duplicate
    ("doughnut shape", "add_ring"),
    ("pointy roof", "add_cone"),
    ("take a photo", "take_picture"),
    ("watch the movie", "play_it"),
    ("glow in the dark", "add_lamp"),
    ("hair on it", "add_particles"),
    ("bumpy surface", "push_with_picture"),
    ("glue them together", "glue_together"),
    ("steps up the side", "row_of_them"),
    ("sharpen the edges", "crisp_edges_mod"),
    ("hollow it out", "give_thickness"),
]
for query, want in CASES:
    got = curated(query)
    assert want in got[:5], f"{query!r} -> {got[:5]}, wanted {want}"
    print(f"SEARCH_PASS {query!r} -> {want}")

# gibberish must still find nothing
assert curated("xyzqq zzz blorp") == [], curated("xyzqq zzz blorp")
assert indexed("xyzqq zzz blorp") == [], indexed("xyzqq zzz blorp")
print("SEARCH_PASS gibberish finds nothing")

# --- the full index: loose language across all 2,410 tools -------------------
t0 = time.time()
assert "mesh.bevel" in indexed("bevell")[:5], indexed("bevell")[:5]
print("SEARCH_PASS index typo 'bevell' -> mesh.bevel")
assert "render.render" in indexed("render the picture")[:5], \
    indexed("render the picture")[:5]
print("SEARCH_PASS index 'render the picture' -> render.render")
assert any(h.startswith("object.") and "shade" in h
           for h in indexed("smooth shading")[:8]), indexed("smooth shading")[:8]
print("SEARCH_PASS index 'smooth shading'")
elapsed = time.time() - t0
print(f"INDEX_SEARCH_SECONDS {elapsed:.2f}")
assert elapsed < 20, elapsed

bb.unregister()
print("ALL SEARCH TESTS PASSED")
