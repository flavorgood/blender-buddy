"""Run in factory-startup background Blender with both --offline-mode and --online-mode.

Every transport in this test is a stub. No credentials, child processes or network are needed.
"""
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch
import urllib.request

import bpy


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import blender_buddy as bb
real_ask_ai = bb._ask_ai
network = Mock(side_effect=AssertionError("unexpected network or subprocess"))
provider = Mock(return_value="BUDDY OK")


def settings(service="KEY", url="https://example.invalid/chat"):
    return {"service": service, "url": url, "key": "dummy", "model": "test"}


class OnlineAccess(unittest.TestCase):
    def test_loopback_classification(self):
        for endpoint in ("http://localhost:11434/v1/", "http://127.0.0.2:80/chat",
                         "https://[::1]:443/v1", "HTTP://LOCALHOST/model"):
            self.assertTrue(bb._is_local_url(endpoint), endpoint)
        for endpoint in ("http://localhost.example.invalid/", "http://127.0.0.1.example.invalid/",
                         "https://localhost@other.invalid/", "file:///tmp/x",
                         "http://10.2.3.4/", "http://[invalid", None):
            self.assertFalse(bb._is_local_url(endpoint), endpoint)

    def test_ask_test_direct_dispatch_and_replan(self):
        wm = bpy.context.window_manager
        for name in ("KEY", "CODEX", "CLAUDE", "LOCAL"):
            cfg = settings(name)
            provider.reset_mock()
            with self.subTest(name=name), patch.object(bb, "_expert_settings", return_value=cfg), \
                    patch.object(bb, "_find_codex", return_value="stub"), \
                    patch.object(bb, "_local_alive", return_value=True) as probe:
                wm.buddy_ask = "what can you do for me"
                bpy.ops.buddy.ask_expert()
                self.assertIn("no connection", wm.buddy_answer)
                wm.buddy_ask = "explain the selected cube"
                bpy.ops.buddy.ask_expert()
                if not bpy.app.online_access:
                    self.assertIn("online access is off", wm.buddy_answer)
                bpy.ops.buddy.test_expert()
                for kind in ("ask", "test", "replan"):
                    bb._expert_job_start(kind, cfg, "system", "user")
                if bpy.app.online_access:
                    self.assertGreaterEqual(provider.call_count, 5)
                    self.assertFalse(provider.call_args.args[0]["_loopback_only"])
                else:
                    probe.assert_not_called()
                    provider.assert_not_called()
                    self.assertIn("online access is off", wm.buddy_expert_status)
                    self.assertFalse(bb._EXPERT_JOB["busy"])

    def test_loopback_can_run(self):
        provider.reset_mock()
        cfg = settings("LOCAL", "http://[::1]:11434/v1/chat/completions")
        bb._expert_job_start("test", cfg, "system", "user")
        provider.assert_called_once()
        self.assertEqual(provider.call_args.args[0]["_loopback_only"], not bpy.app.online_access)

    def test_private_loopback_transport(self):
        request = urllib.request.Request("http://localhost:11434/v1/")
        with patch.object(urllib.request, "build_opener") as build:
            bb._expert_urlopen(request, 1, loopback_only=True)
            proxy, redirects = build.call_args.args
            self.assertEqual(proxy.proxies, {})
            self.assertIsInstance(redirects, urllib.request.HTTPRedirectHandler)
            with self.assertRaises(bb._ExpertFault):
                redirects.redirect_request(request, None, 302, "", {}, "https://example.invalid/out")
            result = redirects.redirect_request(request, None, 302, "", {}, "http://127.0.0.1/in")
            self.assertEqual(result.full_url, "http://127.0.0.1/in")
            with self.assertRaises(bb._ExpertFault):
                bb._expert_urlopen(urllib.request.Request("https://example.invalid/"), 1, True)
            self.assertEqual(build.call_count, 1)

    def test_offline_flag_reaches_each_local_http_transport(self):
        for service in ("KEY", "LOCAL", "CLAUDE"):
            cfg = settings(service, "http://127.0.0.1:11434/chat")
            cfg["_loopback_only"] = True
            payload = ({"content": [{"type": "text", "text": "local"}]} if service == "CLAUDE"
                       else {"choices": [{"message": {"content": "local"}}]})
            reply = io.BytesIO(json.dumps(payload).encode("utf-8"))
            with self.subTest(service=service), patch.object(bb, "_expert_urlopen", return_value=reply) as open_request:
                self.assertEqual(real_ask_ai(cfg, "system", "user"), "local")
                self.assertIs(open_request.call_args.kwargs["loopback_only"], True)

    @unittest.skipIf(bpy.app.online_access, "offline only")
    def test_resource_lookup_and_probe_stop_before_contact(self):
        with self.assertRaisesRegex(RuntimeError, "online access"):
            bb._find_resources("wood")
        self.assertFalse(bb._local_alive("https://localhost.example.invalid/v1/"))
        for service in ("LOCAL", "KEY", "CLAUDE"):
            self.assertFalse(bb._expert_ready(settings(service, "https://localhost.example.invalid/v1/")))


if __name__ == "__main__":
    with patch("socket.create_connection", network), patch("subprocess.Popen", network), \
            patch("urllib.request.urlopen", network), patch.object(bb, "_ask_ai", provider), \
            patch.object(bb, "_install_template"):
        bb.register()
        try:
            result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(OnlineAccess))
            assert result.wasSuccessful()
            network.assert_not_called()
        finally:
            bb.unregister()
