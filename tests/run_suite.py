"""Run the repository tests in separate Blender processes with disposable homes.

python tests/run_suite.py --blender /path/to/blender [--only test_login test_agent]
The printed report directory contains each test's console output and a JSON summary.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time


TESTS = Path(__file__).resolve().parent
REPO = TESTS.parent


def run_case(test, blender, report_dir, online):
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="buddy-" + test.stem + "-") as private:
        root = Path(private)
        # Older suites write demo scenes next to the source and exports under ~.
        # Give each process a private copy of both locations.
        repo = root / "repo"
        repo.mkdir()
        (repo / "demo").mkdir()
        (repo / "tests").mkdir()
        shutil.copy2(test, repo / "tests" / test.name)
        snapshot = test.parents[1]
        shutil.copy2(snapshot / "blender_buddy.py", repo)
        for distribution in ("blender_buddy", "extension_src"):
            shutil.copytree(snapshot / distribution, repo / distribution,
                            ignore=shutil.ignore_patterns("__pycache__"))
        home = root / "home"
        env = os.environ.copy()
        env.update(USERPROFILE=str(home), HOME=str(home), PYTHONDONTWRITEBYTECODE="1")
        for key, path in {
            "APPDATA": home / "AppData/Roaming", "LOCALAPPDATA": home / "AppData/Local",
            "XDG_CONFIG_HOME": home / ".config", "XDG_CACHE_HOME": home / ".cache",
            "BLENDER_USER_RESOURCES": home / "blender",
            "BLENDER_USER_CONFIG": home / "blender/config",
            "BLENDER_USER_EXTENSIONS": home / "blender/extensions",
            "BLENDER_USER_DATAFILES": home / "blender/datafiles",
            "BLENDER_USER_SCRIPTS": home / "blender/scripts",
            "TEMP": home / "blender/temp", "TMP": home / "blender/temp", "TMPDIR": home / "blender/temp",
        }.items():
            path.mkdir(parents=True, exist_ok=True)
            env[key] = str(path)
        cmd = [blender, "--background", "--factory-startup", "--threads", "2",
               "--online-mode" if online else "--offline-mode",
               "--disable-autoexec", "--python-exit-code", "70",
               "--python", str(repo / "tests" / test.name)]
        result = subprocess.run(cmd, cwd=repo, env=env, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, timeout=600)
    label = test.stem
    if label == "test_expert_online_access":
        label += "_online" if online else "_offline"
    (report_dir / (label + ".log")).write_bytes(result.stdout)
    seconds = round(time.monotonic() - started, 1)
    print(f"{label}: {'PASS' if result.returncode == 0 else 'FAIL'} ({seconds}s)", flush=True)
    return {"test": label, "online": online, "exit_code": result.returncode, "seconds": seconds}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blender", required=True)
    parser.add_argument("--only", nargs="+")
    parser.add_argument("--jobs", type=int, default=2)
    args = parser.parse_args()
    report = Path(tempfile.mkdtemp(prefix="blender-buddy-suite-"))
    print(f"Writing test logs to {report}", flush=True)
    with tempfile.TemporaryDirectory(prefix="buddy-suite-src-") as directory:
        snapshot = Path(directory)
        shutil.copy2(REPO / "blender_buddy.py", snapshot)
        for name in ("blender_buddy", "extension_src"):
            shutil.copytree(REPO / name, snapshot / name, ignore=shutil.ignore_patterns("__pycache__"))
        digest = hashlib.sha256((snapshot / "blender_buddy.py").read_bytes()).hexdigest()
        for name in ("blender_buddy", "extension_src"):
            assert hashlib.sha256((snapshot / name / "__init__.py").read_bytes()).hexdigest() == digest
        (snapshot / "tests").mkdir()
        tests = [Path(shutil.copy2(path, snapshot / "tests")) for path in sorted(TESTS.glob("test_*.py"))]
        if args.only:
            unknown = set(args.only) - {test.stem for test in tests}
            if unknown:
                parser.error("unknown tests: " + ", ".join(sorted(unknown)))
            tests = [test for test in tests if test.stem in args.only]
        # These existing suites exercise online routes; all providers are stubbed
        # except test_agent's verified public resource search.
        online_tests = {"test_agent", "test_context", "test_expert", "test_expert_card", "test_login"}
        cases = [(test, online) for test in tests for online in
                 ((False, True) if test.stem == "test_expert_online_access" else (test.stem in online_tests,))]
        with ThreadPoolExecutor(max_workers=args.jobs) as pool:
            results = list(pool.map(lambda case: run_case(case[0], args.blender, report, case[1]), cases))
    summary = {"blender": args.blender,
               "source_sha256": digest,
               "tests": results}
    (report / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    raise SystemExit(int(any(row["exit_code"] for row in results)))
