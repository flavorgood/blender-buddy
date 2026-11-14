"""Portable Windows discovery regressions, no Blender or credentials required."""
import ast
import os
from pathlib import Path
import shutil
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'blender_buddy.py').read_text()
nodes = [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)
         and n.name in ('_find_codex', '_desktop_codex_candidates')]
ns = {'os': os, 'shutil': shutil}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(ROOT / 'blender_buddy.py'), 'exec'), ns)

class Discovery(unittest.TestCase):
    def test_path_priority(self):
        with patch.object(shutil, 'which', return_value='/known/codex'):
            self.assertEqual(ns['_find_codex'](), '/known/codex')

    def test_desktop_versioned_cli_without_path(self):
        with tempfile.TemporaryDirectory() as d:
            cli = Path(d) / 'OpenAI/Codex/bin/f71a721e0e6193a9/codex.exe'
            cli.parent.mkdir(parents=True)
            cli.write_bytes(b'fixture, not executable')
            with patch.object(os, 'name', 'nt'), patch.object(shutil, 'which', return_value=None), patch.dict(os.environ, {'LOCALAPPDATA': d}, clear=True):
                self.assertEqual(ns['_find_codex'](), str(cli))

    def test_newest_file_wins_hash_is_not_version(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / 'OpenAI/Codex/bin'
            for folder, stamp in [('zz-old', 100), ('aa-new', 200)]:
                p = root / folder / 'codex.exe'; p.parent.mkdir(parents=True); p.write_bytes(b'x'); os.utime(p, (stamp, stamp))
            self.assertEqual(ns['_desktop_codex_candidates'](d)[0], str(root / 'aa-new/codex.exe'))

    def test_missing_inaccessible_and_nested_not_scanned(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(ns['_desktop_codex_candidates'](d), [])
            nested = Path(d) / 'OpenAI/Codex/bin/bad/nested/codex.exe'
            nested.parent.mkdir(parents=True); nested.write_bytes(b'x')
            self.assertEqual(ns['_desktop_codex_candidates'](d), [])
            with patch.object(os, 'scandir', side_effect=PermissionError):
                self.assertEqual(ns['_desktop_codex_candidates'](d), [])

    def test_install_copies_identical(self):
        for p in ['blender_buddy/__init__.py', 'extension_src/__init__.py']:
            self.assertEqual((ROOT / p).read_text(), source)

if __name__ == '__main__': unittest.main()
