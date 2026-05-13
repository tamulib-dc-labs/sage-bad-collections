#!/usr/bin/env python3
import os
import subprocess
import sys

CROPPED_DIR = "/Volumes/digital_project_management/Service_Unit_Maps/Cropped"


def find_tiffs(root):
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            if name.lower().endswith((".tif", ".tiff")) and not name.startswith("."):
                yield os.path.join(dirpath, name)


def jp2_path(tif_path):
    base, _ = os.path.splitext(tif_path)
    return base + ".jp2"


def convert(tif_path):
    out = jp2_path(tif_path)
    if os.path.exists(out):
        print(f"  SKIP (exists): {os.path.basename(out)}")
        return True
    result = subprocess.run(
        ["opj_compress", "-i", tif_path, "-o", out, "-r", "0"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"  FAIL: {os.path.basename(tif_path)}")
        print(f"        {result.stderr.strip()}")
        return False
    print(f"  OK:   {os.path.basename(tif_path)} -> {os.path.basename(out)}")
    return True


def main():
    if not os.path.isdir(CROPPED_DIR):
        sys.exit(f"ERROR: directory not found: {CROPPED_DIR}")

    tiffs = sorted(find_tiffs(CROPPED_DIR))
    if not tiffs:
        sys.exit("No TIFF files found.")

    print(f"Found {len(tiffs)} TIFF file(s). Converting to lossless JP2...\n")
    failures = []
    for i, tif in enumerate(tiffs, 1):
        rel = os.path.relpath(tif, CROPPED_DIR)
        print(f"[{i}/{len(tiffs)}] {rel}")
        if not convert(tif):
            failures.append(tif)

    print(f"\nDone. {len(tiffs) - len(failures)}/{len(tiffs)} converted successfully.")
    if failures:
        print("\nFailed files:")
        for f in failures:
            print(f"  {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
