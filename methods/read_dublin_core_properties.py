from groupdocs.metadata import Metadata


def read_dublin_core_properties(adobe_file_path: str) -> dict:
    """
    Reads the Dublin Core XMP scheme (dc:*) from an Adobe file into a name -> value dict.

    Remarks:
        Enumerates the Dublin Core scheme's properties (Format, Coverage, Identifier, Source,
        Title, Creator, Description, Subject, Rights). Dublin Core is the interoperability
        layer used by most digital-asset-management systems.
    """
    result: dict = {}
    with Metadata(adobe_file_path) as metadata:
        root = metadata.get_root_package()
        xmp = getattr(root, "xmp_package", None)
        if xmp is None:
            return result
        dc = xmp.schemes.dublin_core
        if dc is None:
            return result
        for p in dc:
            value = str(p.interpreted_value) if p.interpreted_value is not None else (str(p.value) if p.value is not None else "")
            result[p.name] = value
    return result
