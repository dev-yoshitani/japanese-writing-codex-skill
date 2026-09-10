"""Build deterministic Lite/full ZIPs and smoke-test the extracted full archive."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from jw import __version__

SKIP = {".git", "dist", "build", "__pycache__", ".venv"}
ROOT_FILES = {"SKILL.md", "README.md", "README_EN.md", "README_v2.md", "pyproject.toml", "CHANGELOG.md",
              "ARCHITECTURE.md", "SECURITY.md", "THIRD_PARTY_SOURCES.md", "VERIFICATION_v1.1.0.md",
              "SHA256SUMS", "repo-guard.json", ".gitignore"}
FOLDERS = {"agents", "references", "src", "scripts", "glossary", "examples", "tests", "bench", "docs", "tools", ".github", "research"}


def paths(lite):
    result = []
    for path in sorted(ROOT.rglob("*")):
        relative = path.relative_to(ROOT)
        if not path.is_file() or any(p in SKIP or p.endswith(".egg-info") for p in relative.parts) or path.suffix == ".pyc":
            continue
        if lite:
            include = relative.as_posix() == "SKILL.md" or relative.parts[0] in {"agents", "references"}
        else:
            include = relative.as_posix() in ROOT_FILES or relative.parts[0] in FOLDERS
        if include:
            result.append((path, "japanese-writing/" + relative.as_posix()))
    return result


def build(destination, lite):
    selected = paths(lite)
    with zipfile.ZipFile(destination, "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path, name in selected:
            info = zipfile.ZipInfo(name, date_time=(2026, 9, 9, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    with zipfile.ZipFile(destination) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Invalid archive")
        if archive.namelist() != [name for _, name in selected]:
            raise RuntimeError("Archive entry mismatch")
        for path, name in selected:
            if archive.read(name) != path.read_bytes():
                raise RuntimeError("Archive content mismatch")
    return {"file": destination.name, "files": len(selected), "sha256": hashlib.sha256(destination.read_bytes()).hexdigest()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    args = parser.parse_args()
    output = Path(args.output_dir).resolve()
    # Do not silently package archives into directories recursively selected above.
    if output.is_relative_to(ROOT) and output != ROOT / "dist":
        raise ValueError("Inside the project, use dist as the output directory")
    output.mkdir(parents=True, exist_ok=True)
    full = output / f"japanese-writing-{__version__}.zip"
    lite = output / f"japanese-writing-lite-{__version__}.zip"
    checksum = output / "SHA256SUMS"
    verification = output / "package-verification.json"
    if any(p.exists() for p in (full, lite, checksum, verification)):
        raise ValueError("Package output already exists; use a new directory")
    results = [build(full, False), build(lite, True)]
    with tempfile.TemporaryDirectory(prefix="jw-package-") as temporary:
        extraction = Path(temporary).resolve()
        with zipfile.ZipFile(full) as archive:
            for member in archive.namelist():
                if not (extraction / member).resolve().is_relative_to(extraction):
                    raise ValueError("Unsafe ZIP entry")
            archive.extractall(extraction)
        directory = extraction / "japanese-writing"
        process = subprocess.run([sys.executable, "-X", "utf8", "scripts/jw.py", "compare", "examples/source.txt", "examples/changed.txt", "--json"],
                                 cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=30)
        if process.returncode != 1 or json.loads(process.stdout)["status"] != "FAIL":
            raise RuntimeError("Extracted CLI did not reject the known numeric mutation")
        replay = subprocess.run([sys.executable, "-X", "utf8", "scripts/jw.py", "replay", "examples/source.txt", "examples/replay.json", "--output", "accepted.txt", "--json"],
                                cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=30)
        if replay.returncode != 0 or not (directory / "accepted.txt").is_file():
            raise RuntimeError("Extracted replay example failed")
        accepted = (directory / "accepted.txt").read_text(encoding="utf-8")
        if "12 mm" not in accepted or "2026年4月3日" not in accepted:
            raise RuntimeError("Extracted replay failed to preserve protected values")
        suite = subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests"],
                               cwd=directory, capture_output=True, text=True, encoding="utf-8", timeout=60)
        if suite.returncode:
            raise RuntimeError("Extracted archive tests failed: " + suite.stderr)
    checksum.write_text("".join(f"{r['sha256']}  {r['file']}\n" for r in results), encoding="utf-8")
    verification.write_text(json.dumps({"version": __version__, "archives": results, "extracted_cli": "PASS", "extracted_replay": "PASS", "extracted_test_suite": "PASS"}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"archives": results, "extracted_cli": "PASS", "extracted_replay": "PASS", "extracted_test_suite": "PASS"}, indent=2))


if __name__ == "__main__":
    main()
