
import os
from pathlib import Path
import tempfile
from typing import Any, Dict
from unittest.mock import MagicMock, patch
from polaris_ai_datainsight import PolarisAIDataInsightExtractor
import pytest

EXAMPLE_DOC_PATH: Path = Path(__file__).parent.parent / "examples" / "example.docx"
MOCK_RESPONSE_ZIP_PATH: Path = Path(__file__).parent.parent / "examples" / "example.zip"

@pytest.fixture
def temp_resources_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory(
            prefix="example_", 
            dir=Path(__file__).parent.parent / "examples"
        ) as temp_resources_dir:
        yield Path(temp_resources_dir)

@pytest.fixture
def mock_extractor(temp_resources_dir):
    extractor = PolarisAIDataInsightExtractor(
        file_path=EXAMPLE_DOC_PATH,
        api_key="api_key",
        resources_dir=temp_resources_dir,
    )
    
    # Make mock response for DataInsight API call
    patcher = patch("requests.post")
    mock_response = patcher.start()
    mock_response.return_value = MagicMock(
        status_code=200,
        content=MOCK_RESPONSE_ZIP_PATH.read_bytes(),
    )
    
    # Return extrator instance
    yield extractor
    patcher.stop()

######################
# -- SUCCESS TEST -- #
######################

def test_extract__validate_extracted_json(mock_extractor):    
    # Call the method
    doc = mock_extractor.extract()
        
    # Check if the result is in JSON format
    assert isinstance(doc, dict)
    
    # Check if the result contains the expected keys
    assert "pages" in doc
    assert "elements" in doc.get("pages")[0]
    
    # Check if the result contains the expected number of contents
    assert len(doc.get("pages")) == 2
    assert len(doc.get("pages")[0].get("elements")) == 7
    
def test_extract__validate_resource_dir_and_files(temp_resources_dir: Path, mock_extractor: PolarisAIDataInsightExtractor):
    # Call the method
    doc = mock_extractor.extract()
    
    # Check if the resources directory for each extract() call is created
    resources_dirs = [p for p in temp_resources_dir.iterdir() if p.is_dir()]    
    assert len(resources_dirs) == 1
    
    # Check if it is a directory, and contains the expected number of files
    resources_dir = resources_dirs[0]
    assert resources_dir.is_dir()
    assert len(list(resources_dir.glob("*.png"))) == 5
    
    # Check if the resources is saved in the resources directory
    for page in doc.get("pages"):
        for element in page.get("elements"):
            if element.get("type") != "text":
                image_path = element.get("content").get("src")
                assert Path(image_path).exists()
                assert Path(image_path).is_file()
                assert Path(image_path).parent == resources_dir