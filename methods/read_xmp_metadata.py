from groupdocs.metadata import Metadata


def read_xmp_metadata(adobe_file_path: str) -> dict:
    """
    Reads the full XMP metadata packet from an Adobe file into a name -> value dict.

    Remarks:
        Opens the file with GroupDocs.Metadata, resolves the root XMP package, and walks
        every registered scheme (Dublin Core, Photoshop, XmpBasic, CameraRaw, ...) plus the
        deep property tree. Foundation for DAM ingestion pipelines that need a complete
        snapshot of the file's XMP payload.
    """
    result: dict = {}
    with Metadata(adobe_file_path) as metadata:
        root = metadata.get_root_package()
        xmp = getattr(root, "xmp_package", None)
        if xmp is not None:
            for p in xmp:
                _put(result, p)

            schemes = xmp.schemes
            for scheme in (schemes.dublin_core, schemes.xmp_basic, schemes.photoshop,
                           schemes.camera_raw, schemes.paged_text, schemes.xmp_dynamic_media,
                           schemes.xmp_media_management):
                if scheme is None:
                    continue
                for p in scheme:
                    _put(result, p)

        for p in metadata.find_properties(lambda p: p.name is not None):
            if p.name not in result:
                _put(result, p)
    return result


def _put(result: dict, prop) -> None:
    value = str(prop.interpreted_value) if prop.interpreted_value is not None else (str(prop.value) if prop.value is not None else "")
    result[prop.name] = value
