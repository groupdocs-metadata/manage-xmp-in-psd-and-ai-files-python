from groupdocs.metadata import Metadata
from groupdocs.metadata.standards.xmp import XmpArray, XmpArrayType, XmpPacketWrapper
from groupdocs.metadata.standards.xmp.schemes import XmpBasicPackage, XmpDublinCorePackage


def update_copyright_and_creator(input_path: str, output_path: str, copyright: str, creator: str) -> None:
    """
    Writes copyright and creator values into the Dublin Core XMP scheme of an Adobe file.

    Remarks:
        Ensures the Dublin Core scheme exists before setting dc:rights via set_rights and
        dc:creator via the inherited set(name, XmpArray) method. Also updates xmp:CreatorTool
        so tools reading the XmpBasic scheme surface the same identity.
    """
    with Metadata(input_path) as metadata:
        root = metadata.get_root_package()
        xmp = getattr(root, "xmp_package", None)
        if xmp is None:
            root.xmp_package = XmpPacketWrapper()
            xmp = root.xmp_package
        if xmp.schemes.dublin_core is None:
            xmp.schemes.dublin_core = XmpDublinCorePackage()

        dc = xmp.schemes.dublin_core
        dc.set_rights(copyright)
        dc.set("dc:creator", XmpArray.from_([creator], XmpArrayType.ORDERED))

        if xmp.schemes.xmp_basic is None:
            xmp.schemes.xmp_basic = XmpBasicPackage()
        xmp.schemes.xmp_basic.creator_tool = creator

        metadata.save(output_path)
