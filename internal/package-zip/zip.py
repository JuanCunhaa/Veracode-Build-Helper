import argparse
import fnmatch
import glob
import os
import pathlib
import sys
import zipfile


def _split_lines(value: str) -> list[str]:
    lines = []
    for raw in (value or "").splitlines():
        line = raw.strip()
        if not line:
            continue
        lines.append(line)
    return lines


def _norm_rel(path: pathlib.Path) -> str:
    return path.as_posix().lstrip("./")


def _matches_any(patterns: list[str], candidate: str) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(candidate, pat):
            return True
    return False


def _expand_patterns(base: pathlib.Path, patterns: list[str]) -> set[pathlib.Path]:
    matched: set[pathlib.Path] = set()
    for pat in patterns:
        absolute_pattern = str((base / pat).resolve())
        for found in glob.glob(absolute_pattern, recursive=True):
            p = pathlib.Path(found)
            matched.add(p)
    return matched


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--working-directory", required=True)
    parser.add_argument("--output-zip", required=True)
    parser.add_argument("--include", default="")
    parser.add_argument("--include-file", default="")
    parser.add_argument("--exclude", default="")
    parser.add_argument("--exclude-file", default="")
    parser.add_argument("--fail-on-empty-zip", default="true")
    args = parser.parse_args()

    workspace = pathlib.Path(os.environ.get("GITHUB_WORKSPACE") or os.getcwd()).resolve()
    base = (workspace / args.working_directory).resolve()

    include_value = args.include
    if args.include_file:
        include_value = pathlib.Path(args.include_file).read_text(encoding="utf-8")

    exclude_value = args.exclude
    if args.exclude_file:
        exclude_value = pathlib.Path(args.exclude_file).read_text(encoding="utf-8")

    include_patterns = _split_lines(include_value) or ["."]
    exclude_patterns = _split_lines(exclude_value)

    output_zip_path = (workspace / args.output_zip).resolve()
    output_zip_path.parent.mkdir(parents=True, exist_ok=True)
    if output_zip_path.exists():
        output_zip_path.unlink()

    candidates = _expand_patterns(base, include_patterns)
    files: list[pathlib.Path] = []

    for path in sorted(candidates):
        if path.is_dir():
            for root, _, filenames in os.walk(path):
                for filename in filenames:
                    files.append(pathlib.Path(root) / filename)
        elif path.is_file():
            files.append(path)

    # Deduplicate and filter
    uniq: dict[str, pathlib.Path] = {}
    for f in files:
        try:
            rel = f.resolve().relative_to(base.resolve())
        except Exception:
            continue
        rel_str = _norm_rel(rel)
        if not rel_str or rel_str == ".":
            continue
        if _matches_any(exclude_patterns, rel_str):
            continue
        uniq[rel_str] = f

    rel_paths = sorted(uniq.keys())

    with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for rel_str in rel_paths:
            zf.write(uniq[rel_str], arcname=rel_str)

    zip_bytes = output_zip_path.stat().st_size if output_zip_path.exists() else 0
    zip_files = len(rel_paths)

    fail_on_empty = (args.fail_on_empty_zip or "").strip().lower() == "true"
    if fail_on_empty and zip_files == 0:
        print("Zip vazio (nenhum arquivo selecionado). Verifique include_paths/exclude_paths.", file=sys.stderr)
        return 2

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        rel_zip_path = os.path.relpath(output_zip_path, workspace).replace("\\", "/")
        with open(github_output, "a", encoding="utf-8") as f:
            f.write(f"zip_path={rel_zip_path}\n")
            f.write(f"zip_bytes={zip_bytes}\n")
            f.write(f"zip_files={zip_files}\n")

    print(f"Zip gerado: {output_zip_path} ({zip_files} files, {zip_bytes} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
