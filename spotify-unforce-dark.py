#!/usr/bin/env python3
"""Stop Spotify from forcing dark mode, so CSS `prefers-color-scheme` follows GNOME.

Spotify passes the Chromium switch `force-dark-mode` to its embedded browser,
which pins `prefers-color-scheme` to dark. This renames that one switch inside
the `spotify` executable to a name Chromium ignores. Nothing else is touched.

A Spotify update replaces the executable, so re-run `apply` afterwards.

Usage:
    spotify-unforce-dark.py status
    spotify-unforce-dark.py apply      # original kept next to it as spotify.orig
    spotify-unforce-dark.py restore

Quit Spotify before `apply`/`restore`, or restart it afterwards.
"""
import configparser
import os
import shutil
import sys

OLD = b"force-dark-mode"
NEW = b"force-dark-m0de"  # same length, not a switch Chromium knows

CONFIG = os.path.expanduser("~/.config/spicetify/config-xpui.ini")
DEFAULT_DIR = (
    "/var/lib/flatpak/app/com.spotify.Client/x86_64/stable/active/files/extra/share/spotify"
)


def spotify_dir():
    parser = configparser.ConfigParser()
    parser.read(CONFIG)
    return parser.get("Setting", "spotify_path", fallback="").strip() or DEFAULT_DIR


def state(data):
    if data.count(NEW) == 1 and data.count(OLD) == 0:
        return "patched"
    if data.count(OLD) == 1 and data.count(NEW) == 0:
        return "unpatched"
    return "unknown"


def main():
    action = sys.argv[1] if len(sys.argv) == 2 else ""
    if action not in ("status", "apply", "restore"):
        sys.exit(__doc__)

    binary = os.path.join(spotify_dir(), "spotify")
    backup = binary + ".orig"
    with open(binary, "rb") as fh:
        data = fh.read()
    current = state(data)

    if action == "status":
        print(f"{binary}: {current}" + (" (backup present)" if os.path.exists(backup) else ""))
        return

    if action == "restore":
        if not os.path.exists(backup):
            sys.exit(f"no backup at {backup}")
        os.replace(backup, binary)
        print(f"restored original {binary}")
        return

    if current == "patched":
        print("already patched, nothing to do")
        return
    if current != "unpatched":
        sys.exit(
            f"expected exactly one {OLD.decode()!r} in {binary}, found "
            f"{data.count(OLD)}; this Spotify build differs, not patching"
        )

    at = data.index(OLD)
    # Only rewrite a standalone C string, never part of a longer one.
    if data[at - 1] != 0 or data[at + len(OLD)] != 0:
        sys.exit(f"{OLD.decode()!r} at offset {at} is not a standalone string, not patching")

    patched = data[:at] + NEW + data[at + len(OLD):]
    tmp = binary + ".patching"
    with open(tmp, "wb") as fh:
        fh.write(patched)
    shutil.copymode(binary, tmp)
    os.replace(binary, backup)
    os.replace(tmp, binary)
    print(f"patched {binary} at offset {at}; original saved as {backup}")


if __name__ == "__main__":
    main()
