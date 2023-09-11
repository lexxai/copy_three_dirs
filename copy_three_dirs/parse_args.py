import argparse
import os
import sys
from pefile import PE
from pathlib import Path

if sys.version_info >= (3, 8):
    from importlib.metadata import version
else:
    from importlib_metadata import version


def get_version_pe():
    if getattr(sys, "frozen", False):
        pe = PE(sys.executable)
        if "VS_FIXEDFILEINFO" not in pe.__dict__:
            print("ERROR: Oops, has no version info. Can't continue.")
            return None
        if not pe.VS_FIXEDFILEINFO:
            print("ERROR: VS_FIXEDFILEINFO field not set for. Can't continue.")
            return None
        verinfo = pe.VS_FIXEDFILEINFO[0]
        # print(verinfo)
        filever = (
            verinfo.FileVersionMS >> 16,
            verinfo.FileVersionMS & 0xFFFF,
            verinfo.FileVersionLS >> 16,
            # verinfo.FileVersionLS & 0xFFFF,
        )
        return "{}.{}.{}".format(*filever)


def get_version():
    try:
        version_str = version(__package__)
        print(f"{version_str=}")
    except Exception:
        version_str = get_version_pe()
        if version_str is None:
            version_str = "undefined"
    pack = __package__ if __package__ else Path(sys.executable).name
    return f"Version: '{version_str}', package: {pack}"


def app_arg():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "-V",
        "--version",
        action="version",
        version=get_version(),
        help="show version of app",
    )
    ap.add_argument(
        "--work",
        help="Directory for work. Is prefix for all other directories that is not absolute, default ''",
        default="",
    )
    ap.add_argument(
        "--input1", help="Directory for input1 (source list)", required=True
    )
    ap.add_argument(
        "--input2", help="Directory for input2 (compare list)", required=True
    )
    ap.add_argument(
        "--output", help="Directory for output, default 'Output'", default="Output"
    )
    ap.add_argument(
        "--found",
        help="Directory for found, default 'Found'",
        default="Found",
    )
    ap.add_argument(
        "--notfound",
        help="Directory for notfound, default 'Notfound'",
        default="Notfound",
    )
    ap.add_argument(
        "--joined",
        help="Directory for joined images of 'output' and 'found' directories, default 'Joined'",
        default="Joined",
    )

    ap.add_argument(
        "--join",
        help="to join images of 'output' and 'found' directories",
        action="store_true",
    )

    ap.add_argument(
        "--join_only",
        help="to join images of 'output' and 'found' directories, without all other operations",
        action="store_true",
    )

    ap.add_argument(
        "--verbose",
        help="verbose output",
        action="store_true",
    )
    args = vars(ap.parse_args())
    # print(f"{args=}")
    return args
