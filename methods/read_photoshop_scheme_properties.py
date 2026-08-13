from groupdocs.metadata import Metadata


def read_photoshop_scheme_properties(adobe_file_path: str) -> dict:
    """
    Reads the Adobe Photoshop-specific XMP scheme (photoshop:*) from a PSD or AI file.

    Remarks:
        Extracts photographic and location context (ColorMode, IccProfile, City, Country,
        DateCreated, CaptionWriter, Credit) which live outside Dublin Core. These fields
        power Bridge, Lightroom, and third-party DAM search filters targeting Adobe files.
    """
    result: dict = {}
    with Metadata(adobe_file_path) as metadata:
        root = metadata.get_root_package()
        xmp = getattr(root, "xmp_package", None)
        if xmp is None:
            return result
        ps = xmp.schemes.photoshop
        if ps is None:
            return result

        def _to_str(v):
            return str(v) if v is not None else ""

        result["photoshop:ColorMode"] = _to_str(getattr(ps, "color_mode", None))
        result["photoshop:IccProfile"] = _to_str(getattr(ps, "icc_profile", None))
        result["photoshop:City"] = _to_str(getattr(ps, "city", None))
        result["photoshop:Country"] = _to_str(getattr(ps, "country", None))
        result["photoshop:DateCreated"] = _to_str(getattr(ps, "date_created", None))
        result["photoshop:CaptionWriter"] = _to_str(getattr(ps, "caption_writer", None))
        result["photoshop:Credit"] = _to_str(getattr(ps, "credit", None))
        result["photoshop:Source"] = _to_str(getattr(ps, "source", None))
    return result
