import re
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from langchain_core.documents import Document

from langchain_polaris_ai_datainsight import PolarisAIDataInsightLoader

EXAMPLE_DOC_PATH = Path(__file__).parent.parent / "examples" / "example.docx"
MOCK_RESPONSE_ZIP_PATH = Path(__file__).parent.parent / "examples" / "example.zip"

# -- For checking the test result -- #
MOCK_RESPONSE_DATA_STRUCTURE = {
    "elements": {
        "total": 10,
        "text": 5,
        "image": 5,
    },
    "pages": {
        "total": 2,
        "1": {
            "total": 7,
            "text": 5,
            "image": 2,
        },
        "2": {
            "total": 3,
            "image": 3,
        },
    },
}


@pytest.fixture
def temp_resources_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory(
        prefix="example_", dir=Path(__file__).parent.parent / "examples"
    ) as temp_resources_dir:
        yield Path(temp_resources_dir)


@pytest.fixture
def mock_response():
    # Make mock response for DataInsight API call
    patcher = patch("requests.post")
    mock_response = patcher.start()
    mock_response.return_value = MagicMock(
        status_code=200,
        content=MOCK_RESPONSE_ZIP_PATH.read_bytes(),
    )

    yield mock_response

    patcher.stop()


######################
# -- SUCCESS TEST -- #
######################


@pytest.mark.usefixtures("temp_resources_dir")
@pytest.mark.usefixtures("mock_response")
def test_lazy_load__load_with_element_mode(
    temp_resources_dir: Path, mock_response: MagicMock
) -> None:
    loader = PolarisAIDataInsightLoader(
        file_path=EXAMPLE_DOC_PATH,
        api_key="api_key",
        resources_dir=temp_resources_dir,
        mode="element",
    )
    docs = list(loader.lazy_load())

    # Check if the result is a list of Document objects
    assert isinstance(docs[0], Document)

    # Check if the number of documents is correct
    assert len(docs) == MOCK_RESPONSE_DATA_STRUCTURE["elements"]["total"]

    for doc in docs:
        # Check if the document has the correct attributes
        if doc.metadata.get("type") == "text":
            assert doc.page_content != ""
            assert doc.metadata.get("resources") is None
        else:
            # Check if the page_content has a resource id
            match = re.search(r'id="([^"]+)"', doc.page_content)
            if match:
                resource_id = match.group(1)
            else:
                assert False, "Resource(Image) ID not found in page content"

            # Check if the metadata has the correct attributes
            assert doc.metadata.get("resources") is not None

            # Check if the resources path is correct
            resource_path = doc.metadata.get("resources").get(resource_id)
            assert Path(resource_path).exists()
            assert Path(resource_path).is_file()
            assert Path(resource_path).parent.parent == temp_resources_dir


@pytest.mark.usefixtures("temp_resources_dir")
@pytest.mark.usefixtures("mock_response")
def test_lazy_load__load_with_page_mode(
    temp_resources_dir: Path, mock_response: MagicMock
) -> None:
    loader = PolarisAIDataInsightLoader(
        file_path=EXAMPLE_DOC_PATH,
        api_key="api_key",
        resources_dir=temp_resources_dir,
        mode="page",
    )
    docs = list(loader.lazy_load())

    # Check if the result is a list of Document objects
    assert isinstance(docs[0], Document)

    # Check if the number of documents is correct
    assert len(docs) == MOCK_RESPONSE_DATA_STRUCTURE["pages"]["total"]

    for page_id, doc in enumerate(docs):
        # Check number of elements in the page
        assert (
            len(doc.metadata.get("elements"))
            == MOCK_RESPONSE_DATA_STRUCTURE["pages"][str(page_id + 1)]["total"]
        )
        assert (
            len(doc.metadata.get("resources"))
            == MOCK_RESPONSE_DATA_STRUCTURE["pages"][str(page_id + 1)]["image"]
        )

        # Check if the number of resource ids
        #           in page_content equals the number of images
        resource_ids = re.findall(
            r'<img src="#" alt="" id="([^"]+)"/>', doc.page_content
        )
        assert (
            len(resource_ids)
            == MOCK_RESPONSE_DATA_STRUCTURE["pages"][str(page_id + 1)]["image"]
        )

        for resource_id in resource_ids:
            # Check if the metadata has the correct attributes
            assert doc.metadata.get("resources") is not None

            # Check if the resources path is correct
            resource_path = doc.metadata.get("resources").get(resource_id)
            assert Path(resource_path).exists()
            assert Path(resource_path).is_file()
            assert Path(resource_path).parent.parent == temp_resources_dir


@pytest.mark.usefixtures("temp_resources_dir")
@pytest.mark.usefixtures("mock_response")
def test_lazy_load__load_with_single_mode(
    temp_resources_dir: Path, mock_response: MagicMock
) -> None:
    loader = PolarisAIDataInsightLoader(
        file_path=EXAMPLE_DOC_PATH,
        api_key="api_key",
        resources_dir=temp_resources_dir,
        mode="single",
    )
    docs = list(loader.lazy_load())

    # Check if the result is a list of Document objects
    assert isinstance(docs[0], Document)

    # Check if the number of documents is correct
    assert len(docs) == 1

    doc = docs[0]

    # Check if the number of resource ids in page_content equals the number of images
    resource_ids = re.findall(r'<img src="#" alt="" id="([^"]+)"/>', doc.page_content)
    assert len(resource_ids) == MOCK_RESPONSE_DATA_STRUCTURE["elements"]["image"]

    for resource_id in resource_ids:
        # Check if the metadata has the correct attributes
        assert doc.metadata.get("resources") is not None

        # Check if the resources path is correct
        resource_path = doc.metadata.get("resources").get(resource_id)
        assert Path(resource_path).exists()
        assert Path(resource_path).is_file()
        assert Path(resource_path).parent.parent == temp_resources_dir
