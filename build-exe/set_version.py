"""
Sets the app version (shown in the window title / about dialog) and the version info of the exe.
Usage: python build-exe/set_version.py 2.5.0   (a leading "v" like in "v2.5.0" is ignored)
"""
import os
import re
import sys

BUILD_FILES = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(BUILD_FILES)
VERSION_PY = os.path.join(REPO, "packages", "Startup", "Version.py")
VERSION_FILE = os.path.join(BUILD_FILES, "VersionFile.txt")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    version = sys.argv[1].strip()
    if version.lower().startswith("v"):
        version = version[1:]
    numeric_part = re.match(r"^\d+(\.\d+){0,3}", version)
    if numeric_part is None:
        sys.exit(f"Invalid version: {sys.argv[1]}")
    # windows version info needs exactly four numbers, e.g. 2.5.0 -> (2, 5, 0, 0)
    numbers = numeric_part.group(0).split(".")
    version_tuple = "(" + ", ".join((numbers + ["0"] * 4)[:4]) + ")"

    with open(VERSION_PY, "w", encoding="utf-8", newline="\n") as file:
        file.write(f'Version = "{version}"\n')

    with open(VERSION_FILE, "r", encoding="utf-8") as file:
        content = file.read()
    content = re.sub(r"filevers=\([^)]*\)", f"filevers={version_tuple}", content)
    content = re.sub(r"prodvers=\([^)]*\)", f"prodvers={version_tuple}", content)
    content = re.sub(r"(StringStruct\(u'FileVersion', u')[^']*('\))", rf"\g<1>{version}\g<2>", content)
    content = re.sub(r"(StringStruct\(u'ProductVersion', u')[^']*('\))", rf"\g<1>{version}\g<2>", content)
    with open(VERSION_FILE, "w", encoding="utf-8", newline="\n") as file:
        file.write(content)
    print(f"Version set to {version} {version_tuple}")


if __name__ == "__main__":
    main()
