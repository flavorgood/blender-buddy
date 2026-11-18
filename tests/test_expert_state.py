"""Verify the saved task-mode choice and the floating card's single launcher."""
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blender_buddy as bb


bb.register()
try:
    with tempfile.TemporaryDirectory() as folder:
        state = Path(folder) / "task_mode.json"
        with patch.object(bb, "_task_mode_path", return_value=str(state)):
            bb._EXPERT_TASK_MODE = None
            wm = bpy.context.window_manager
            assert wm.buddy_agent is True
            assert not state.exists(), "reading the default must not write preferences"
            wm.buddy_agent = False
            assert state.read_bytes() == b"false"
            bpy.ops.wm.read_homefile(use_empty=True)
            bb._EXPERT_TASK_MODE = None  # Force a reread of the persisted choice.
            assert bpy.context.window_manager.buddy_agent is False
            bpy.context.window_manager.buddy_agent = True
            assert state.read_bytes() == b"true"
            bb._EXPERT_TASK_MODE = None
            assert bpy.context.window_manager.buddy_agent is True
    row = Mock()
    launcher = SimpleNamespace(layout=Mock())
    launcher.layout.row.return_value = row
    bb.VIEW3D_PT_buddy_expert_launcher.draw(launcher, bpy.context)
    row.operator.assert_called_once_with("buddy.expert_card_open", text="Open Buddy Expert")
    settings = Mock()
    bb._draw_expert(settings, bpy.context)
    settings.prop.assert_called_once_with(bpy.context.window_manager, "buddy_agent",
                                         text="Expert help with tasks")
    settings.operator.assert_called_once_with("buddy.open_prefs", text="Expert connection settings")
    bb._CARD.update(open=False)
    assert bpy.ops.buddy.expert_card_open() == {"FINISHED"}
    assert bb._CARD["open"]
finally:
    bb.unregister()
print("ALL EXPERT STATE TESTS PASSED")
