import os
import warnings
from .dataset_metadata import read_dataset_metadata, write_dataset_metadata
from .view_metadata import get_default_view
from ..validation import validate_source_metadata, validate_view_metadata


def _get_image_metadata(source_name, xml_path, type_):
    # eventually we need to support more data formats here (ome.zarr)
    source_metadata = {
        type_: {
            "imageData": {
                "fileSystem": {
                    "format": "bdv.n5",
                    "source": xml_path
                }
            }
        }
    }
    return source_metadata


def _get_table_metadata(table_location):
    table_metadata = {
        "fileSystem": {
            "format": "tsv",
            "source": table_location
        }
    }
    return table_metadata


def get_image_metadata(source_name, xml_path):
    return _get_image_metadata(source_name, xml_path, "image")


def get_segmentation_metadata(source_name, xml_path, table_location=None):
    source_metadata = _get_image_metadata(source_name, xml_path, "segmentation")
    if table_location is not None:
        source_metadata["segmentation"]["tableData"] = _get_table_metadata(table_location)
    return source_metadata


def add_source_metadata(
    dataset_folder,
    source_type,
    source_name,
    xml_path,
    view=None,
    table_folder=None,
    overwrite=True
):
    """ Add metadata entry for a souce to MoBIE dataset.

    Arguments:
        dataset_folder [str] - path to the dataset folder.
        source_type [str] - type of the source, either 'image' or 'segmentation'.
        source_name [str] - name of the source.
        xml_path [str] - path to the xml for the image data corresponding to this source.
        view [dict] - default view for this source. (default: None)
        table_folder [str] - table folder for segmentations. (default: None)
        overwrite [bool] - whether to overwrite existing entries (default: True)
    """
    dataset_metadata = read_dataset_metadata(dataset_folder)
    sources_metadata = dataset_metadata["sources"]
    view_metadata = dataset_metadata["views"]

    # validate the arguments
    if source_type not in ('image', 'segmentation'):
        raise ValueError(f"Expect source_type to be 'image' or 'segmentation', got {source_type}")

    if source_name in sources_metadata or source_name in view_metadata:
        msg = f"A source with name {source_name} already exists for the dataset {dataset_folder}"
        if overwrite:
            warnings.warn(msg)
        else:
            raise ValueError(msg)

    # create the metadata for this source
    relative_xml_path = os.path.relpath(xml_path, dataset_folder)

    if source_type == "image":
        source_metadata = get_image_metadata(source_name, relative_xml_path)
    else:
        relative_table_folder = None if table_folder is None else os.path.relpath(table_folder, dataset_folder)
        source_metadata = get_segmentation_metadata(source_name, relative_xml_path, relative_table_folder)
    validate_source_metadata(source_name, source_metadata, dataset_folder)

    if view is None:
        view = get_default_view(source_type, source_name)
    validate_view_metadata(view)

    sources_metadata[source_name] = source_metadata
    view_metadata[source_name] = view

    dataset_metadata["sources"] = sources_metadata
    dataset_metadata["views"] = view_metadata
    write_dataset_metadata(dataset_folder, dataset_metadata)


# TODO
def update_source_metadata():
    pass
