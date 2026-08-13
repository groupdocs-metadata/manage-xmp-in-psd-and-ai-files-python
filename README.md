# XMP Metadata in Adobe PSD and AI Files

[![Product Page](https://img.shields.io/badge/Product%20Page-2865E0?style=for-the-badge&logo=appveyor&logoColor=white)](https://github.com/groupdocs-metadata/GroupDocs.Metadata-Docs) 
[![Docs](https://img.shields.io/badge/Docs-2865E0?style=for-the-badge&logo=Hugo&logoColor=white)](https://docs.groupdocs.com/metadata/python-net/) 
[![Blog](https://img.shields.io/badge/Blog-2865E0?style=for-the-badge&logo=WordPress&logoColor=white)](https://blog.groupdocs.com/categories/groupdocs.metadata-product-family/) 
[![Free Support](https://img.shields.io/badge/Free%20Support-2865E0?style=for-the-badge&logo=Discourse&logoColor=white)](https://forum.groupdocs.com/c/metadata/) 
[![Temporary License](https://img.shields.io/badge/Temporary%20License-2865E0?style=for-the-badge&logo=rocket&logoColor=white)](https://purchase.groupdocs.com/temp-license/100216)

## 📖 About This Repository

manage-xmp-in-psd-and-ai-files-python is a runnable Python demo that reads and writes the XMP packet inside Photoshop PSD and Illustrator AI files. It uses GroupDocs.Metadata for Python via .NET (`groupdocs-metadata-net`, pinned to 26.5) and ships with one sample of each format, so the whole flow runs the moment dependencies install. Five documented functions read the full XMP tree, the Dublin Core scheme, and the Photoshop scheme, then write copyright, creator, and keyword values back. The examples are for developers wiring Adobe assets into digital-asset-management ingestion, search, or licensing pipelines.

## The Challenge

Design teams hand off PSD and AI files that must carry ownership and search data inside the file itself. A press image without dc:rights is a licensing question waiting to happen, and an asset without dc:subject keywords is invisible to DAM search. I started this demo after chasing a missing copyright notice across a folder of 300 press images; the fix belonged in the files, not in a spreadsheet next to them.

Getting at that data programmatically is the hard part. XMP is an XML packet embedded in a binary container, and its values are spread across schemes: Dublin Core for interoperable fields, the Photoshop scheme for editorial context, XmpBasic for tool identity. Parsing PSD structures by hand to find and rewrite one packet is real work, and AI files arrange the container differently.

**What is GroupDocs.Metadata?**

GroupDocs.Metadata for Python via .NET is a metadata read/write library covering 170+ file formats, per the [product documentation](https://docs.groupdocs.com/metadata/python-net/). Key features for this scenario include:

- One `Metadata` entry point that opens PSD and AI files identically
- Typed access to XMP schemes: `dublin_core`, `photoshop`, `xmp_basic`, `camera_raw`, and more
- Write support with scheme creation, so files without existing XMP still accept values
- `XmpArray` handling for ordered creator lists and unordered keyword bags
- A `find_properties` search that sweeps the whole property tree with one predicate

The write functions in this repo create missing schemes before setting values, which is the detail that makes them safe for freshly exported assets that carry no XMP at all.

## Prerequisites

- **Python 3** – any actively supported CPython release with pip
- **GroupDocs.Metadata package** – `pip install groupdocs-metadata-net==26.5` (or `pip install -r requirements.txt`)
- **License (optional)** – `main.py` runs in evaluation mode when `LICENSE_PATH` does not point at a `.lic` file

## Repository Structure

```
manage-xmp-in-psd-and-ai-files-python/
│
├── main.py
├── requirements.txt
├── methods/
│   ├── __init__.py
│   ├── add_keywords.py
│   ├── read_dublin_core_properties.py
│   ├── read_photoshop_scheme_properties.py
│   ├── read_xmp_metadata.py
│   └── update_copyright_and_creator.py
├── output/
│   ├── with-copyright.psd
│   └── with-keywords.psd
└── resources/
    ├── sample.ai
    └── sample.psd
```

- **main.py** – runs the five functions against `sample.psd` and asserts the written values persist
- **requirements.txt** – pins `groupdocs-metadata-net==26.5`
- **methods/read_xmp_metadata.py** – full XMP snapshot as a name → value dict
- **methods/read_dublin_core_properties.py** – the dc:* interoperability fields
- **methods/read_photoshop_scheme_properties.py** – photoshop:* editorial and location fields
- **methods/update_copyright_and_creator.py** – writes dc:rights, dc:creator, and xmp:CreatorTool
- **methods/add_keywords.py** – writes the dc:subject keyword bag
- **output/** – the two PSD files a full run produces
- **resources/** – seeded `sample.psd` and `sample.ai` inputs

### Does this work the same for PSD and AI files?

Yes. Both formats carry their XMP packet the same way, and every function here resolves it through get_root_package() plus the xmp_package attribute. The repo ships sample.psd and sample.ai so you can run the pipeline against each. The only practical difference is that a fresh AI export often arrives with fewer populated schemes than a Photoshop save.

## Code Examples

### Reads the full XMP metadata packet from an Adobe file

The snapshot function walks the root packet, then every registered scheme, then sweeps the whole property tree for anything the schemes missed. The result is one flat dict a DAM ingestion job can index directly.

```python
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
```

The scheme loop reads seven named schemes explicitly, and the trailing `find_properties` pass catches custom or vendor packets. The small module-level `_put` helper stores each property under its qualified name, preferring `interpreted_value` so dates and enumerations arrive human-readable.

### Reads the Dublin Core XMP scheme (dc:*)

Dublin Core is the interoperability layer most DAM systems agree on: Title, Creator, Description, Subject, Rights, Format, Identifier, Source, Coverage. This function returns just that scheme as a dict.

```python
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
        value = (str(p.interpreted_value) if p.interpreted_value is not None
                 else (str(p.value) if p.value is not None else ""))
        result[p.name] = value
return result
```

Both early returns matter in production: files with no XMP packet and files with XMP but no Dublin Core scheme are common, and each yields an empty dict rather than an exception.

### Reads the Adobe Photoshop-specific XMP scheme (photoshop:*)

Editorial and location context lives outside Dublin Core: ColorMode, IccProfile, City, Country, DateCreated, CaptionWriter, Credit, Source. These are the fields Bridge, Lightroom, and DAM search filters read for Adobe files.

```python
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
```

Each field maps to a typed property on the scheme object, read through `getattr` with a `None` default so partially populated files never raise. Empty strings in the result mean the field exists in the standard but not in this file.

### Writes copyright and creator into the Dublin Core scheme

Ownership stamping is a write in three places: dc:rights for the legal notice, dc:creator as an ordered XMP array, and xmp:CreatorTool so XmpBasic readers surface the same identity.

```python
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
```

The guards create `XmpPacketWrapper`, `XmpDublinCorePackage`, and `XmpBasicPackage` on demand, so the function works on assets that never carried XMP. `main.py` verifies persistence by re-reading the output and checking the written strings survive in the file bytes.

### Adds keywords to the dc:subject list

dc:subject is the canonical tag vocabulary DAM tools index. The function writes the whole keyword list as one unordered array, replacing the previous bag.

```python
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
```

`XmpArrayType.UNORDERED` is the semantically correct container for keywords: order carries no meaning, which is how Bridge and downstream DAM indexers treat the bag. The demo writes `["landscape", "sunset", "commercial"]` and asserts the first keyword lands in the saved bytes.

## Related Topics to Explore

If you're working with XMP metadata in Adobe or image files, the following resources may be helpful:

* **Step-by-step use case guide in the documentation** – this scenario as a documented walkthrough with the same five operations: [Read the guide →](https://docs.groupdocs.com/metadata/python-net/use-cases/xmp-metadata-in-adobe-psd-and-ai/)

* **In-depth blog article about this project** – the DAM context and full pipeline behind this repo: [Read the article →](https://blog.groupdocs.com/metadata/xmp-metadata-in-adobe-psd-and-ai-python-net/)

* **Edit and Clean XMP Metadata Packages in SVG Images** – the same XMP API applied to SVG, including packet removal: [Read the article →](https://blog.groupdocs.com/metadata/edit-and-clean-xmp-in-svg/)

* **Manage XMP and EXIF Data of HEIF/HEIC Images using C#** – scheme-level XMP editing on Apple's image container: [Read the article →](https://blog.groupdocs.com/metadata/manage-xmp-and-exif-data-of-heif-heic-images-using-csharp/)

* **Edit Metadata in Python Applications** – the wider read/update/remove API surface this demo draws from: [Read the article →](https://blog.groupdocs.com/metadata/edit-metadata-in-python/)

* **Working with XMP metadata** – reference documentation for reading, updating, and removing XMP: [Read the docs →](https://docs.groupdocs.com/metadata/python-net/working-with-xmp-metadata/)

## Keywords

`xmp metadata python`, `psd metadata`, `ai file metadata`, `dublin core xmp`, `photoshop scheme`, `dc:subject keywords`, `dc:rights copyright`, `dc:creator`, `xmp packet`, `adobe file metadata`, `digital asset management`, `dam ingestion`, `read xmp python`, `write xmp python`, `groupdocs metadata`, `python via .net`, `xmp basic scheme`, `creator tool`, `image keywords`, `asset licensing metadata`
