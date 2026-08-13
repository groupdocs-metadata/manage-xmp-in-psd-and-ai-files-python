from groupdocs.metadata import Metadata
from groupdocs.metadata.standards.xmp import XmpArray, XmpArrayType, XmpPacketWrapper
from groupdocs.metadata.standards.xmp.schemes import XmpDublinCorePackage


def add_keywords(input_path: str, output_path: str, keywords: list) -> None:
    """
    Adds one or more keywords to the dc:subject list of an Adobe file's XMP packet.

    Remarks:
        dc:subject is the canonical DAM tag vocabulary. Writes the whole keyword list as an
        Unordered XmpArray so downstream DAM tools and Bridge can index the file consistently.
        The Dublin Core scheme is created if the file did not previously carry XMP data.
    """
    with Metadata(input_path) as metadata:
        root = metadata.get_root_package()
        xmp = getattr(root, "xmp_package", None)
        if xmp is None:
            root.xmp_package = XmpPacketWrapper()
            xmp = root.xmp_package
        if xmp.schemes.dublin_core is None:
            xmp.schemes.dublin_core = XmpDublinCorePackage()

        xmp.schemes.dublin_core.set(
            "dc:subject",
            XmpArray.from_(list(keywords), XmpArrayType.UNORDERED))
        metadata.save(output_path)
