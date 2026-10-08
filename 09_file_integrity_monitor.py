# ============================================================
# PROJECT 9: FILE INTEGRITY MONITOR
# ------------------------------------------------------------
# What it does: takes a "fingerprint" (hash) of every file in a
# folder and saves it. Later you check again and the program tells
# you which files were CHANGED, ADDED or DELETED. If a file changes
# even by one letter, its fingerprint is completely different.
#
# How to run:
#   python 09_file_integrity_monitor.py baseline my_folder    (first: save fingerprints)
#   python 09_file_integrity_monitor.py check my_folder       (later: compare)
# ============================================================

import hashlib     # creates the fingerprints
import json        # saves/loads data as a text file
import os          # walking through folders
import sys

BASELINE_FILE = "baseline.json"     # where the fingerprints are stored


def hash_file(path):
    """Return the SHA-256 fingerprint of one file."""
    h = hashlib.sha256()                    # create an empty hash calculator
    with open(path, "rb") as f:             # open the file as raw bytes
        while True:
            chunk = f.read(65536)           # read 64 KB at a time (works for big files)
            if not chunk:                   # nothing left to read
                break
            h.update(chunk)                 # feed this piece into the calculator
    return h.hexdigest()                    # the final fingerprint as text


def scan_folder(folder):
    """Return a dictionary {file path: fingerprint} for all files in the folder."""
    result = {}
    # os.walk visits the folder and all sub-folders
    for root, dirs, files in os.walk(folder):
        for name in files:
            path = os.path.join(root, name)     # full path of the file
            if name == BASELINE_FILE:
                continue                        # skip our own data file (compare just the file name)
            try:
                result[path] = hash_file(path)
            except Exception:
                pass                            # skip files we cannot read
    return result


if len(sys.argv) < 3 or sys.argv[1] not in ("baseline", "check"):
    print("Usage:")
    print("  python 09_file_integrity_monitor.py baseline FOLDER")
    print("  python 09_file_integrity_monitor.py check FOLDER")
    sys.exit()                                  # stop the program here

mode = sys.argv[1]
folder = sys.argv[2]
current = scan_folder(folder)                   # fingerprints right now

if mode == "baseline":
    with open(BASELINE_FILE, "w") as f:
        json.dump(current, f, indent=2)         # write the dictionary to the file
    print(f"Saved fingerprints of {len(current)} files to {BASELINE_FILE}")
else:
    with open(BASELINE_FILE) as f:
        old = json.load(f)                      # load the saved fingerprints
    changes = 0
    for path, fingerprint in current.items():
        if path not in old:
            print("ADDED:   ", path)
            changes += 1
        elif old[path] != fingerprint:
            print("CHANGED: ", path)
            changes += 1
    for path in old:
        if path not in current:
            print("DELETED: ", path)
            changes += 1
    if changes == 0:
        print("All files are unchanged.")
