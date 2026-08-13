import os
import sys

from groupdocs.metadata import License

from methods.read_xmp_metadata import read_xmp_metadata
from methods.read_dublin_core_properties import read_dublin_core_properties
from methods.update_copyright_and_creator import update_copyright_and_creator
from methods.add_keywords import add_keywords
from methods.read_photoshop_scheme_properties import read_photoshop_scheme_properties


LICENSE_PATH = r"YOUR-LICENSE-PATH-HERE"
HERE = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(HERE, "resources")
OUTPUT_DIR = os.path.join(HERE, "output")


def set_license():
    if os.path.exists(LICENSE_PATH):
        License().set_license(LICENSE_PATH)
        print("License applied")
    else:
        print(f"WARN license file not found at {LICENSE_PATH}; running in evaluation mode")


def do_assert(condition: bool, message: str):
    if not condition:
        raise AssertionError(f"assert failed: {message}")
    print(f"PASS {message}")


def file_contains(path: str, needle: str) -> bool:
    with open(path, "rb") as f:
        data = f.read()
    return needle.encode("utf-8") in data


def contains_any_value(d: dict, needle: str) -> bool:
    for k, v in d.items():
        if needle in (v or "") or needle in (k or ""):
            return True
    return False


def count_non_empty(d: dict) -> int:
    return sum(1 for v in d.values() if v)


def main() -> int:
    try:
        set_license()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        src = os.path.join(INPUT_DIR, "sample.psd")
        if not os.path.exists(src):
            print(f"FAIL missing input at {src}")
            return 2

        all_xmp = read_xmp_metadata(src)
        do_assert(len(all_xmp) > 0, f"read_xmp_metadata returned {len(all_xmp)} XMP properties")

        dc = read_dublin_core_properties(src)
        do_assert(True, f"read_dublin_core_properties returned {len(dc)} DC fields (populated: {count_non_empty(dc)})")

        out1 = os.path.join(OUTPUT_DIR, "with-copyright.psd")
        update_copyright_and_creator(src, out1, "(C) 2026 GroupDocs Sample", "Digital Asset Team")
        do_assert(os.path.exists(out1) and os.path.getsize(out1) > 0,
                  f"update_copyright_and_creator wrote {os.path.getsize(out1)} bytes")

        xmp_after = read_xmp_metadata(out1)
        rights_present = contains_any_value(xmp_after, "GroupDocs") or file_contains(out1, "GroupDocs Sample")
        do_assert(rights_present, "dc:rights persisted after write (bytes contain 'GroupDocs')")
        creator_present = contains_any_value(xmp_after, "Digital Asset Team") or file_contains(out1, "Digital Asset Team")
        do_assert(creator_present, "dc:creator persisted after write (bytes contain 'Digital Asset Team')")

        out2 = os.path.join(OUTPUT_DIR, "with-keywords.psd")
        add_keywords(src, out2, ["landscape", "sunset", "commercial"])
        do_assert(os.path.exists(out2) and os.path.getsize(out2) > 0,
                  f"add_keywords wrote {os.path.getsize(out2)} bytes")

        do_assert(file_contains(out2, "landscape"),
                  "dc:subject bytes include 'landscape' after add_keywords")

        ps = read_photoshop_scheme_properties(src)
        do_assert(True, f"read_photoshop_scheme_properties returned {len(ps)} Photoshop fields (populated: {count_non_empty(ps)})")

        print()
        print("ALL PASS")
        return 0
    except Exception as ex:
        print(f"FAIL {type(ex).__name__}: {ex}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
