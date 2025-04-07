import mimetypes
from pathlib import Path
import tempfile
from langchain_polaris_ai_datainsight import PolarisAIDataInsightLoader
import pytest

# -- For Success Test -- #
EXAMPLE_DOC_PATH = Path(__file__).parent.parent / "examples" / "example.docx"

# -- For Failure Test -- #
EXAMPLE_UNSUPPORTED_DOC_PATH = Path(__file__).parent.parent / "examples" / "example.txt"
EXAMPLE_NOT_EXIST_DOC_PATH = Path(__file__).parent.parent / "examples" / "no_file.docx"

@pytest.fixture
def temp_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory(dir=Path(__file__).parent.parent / "examples") as temp_dir:
        yield temp_dir
        

# -- SUCCESS TEST -- #
def test_init__load_blob_from_file_path(temp_dir):
    """Test PolarisAIDataInsightLoader with file_path."""

    loader = PolarisAIDataInsightLoader(
        file_path=EXAMPLE_DOC_PATH,
        api_key="api_key",
        resources_dir=temp_dir,
    )
    
    assert loader.blob.mimetype == mimetypes.guess_type(EXAMPLE_DOC_PATH)[0]
    assert loader.blob.metadata.get("filename") == EXAMPLE_DOC_PATH.name
    assert loader.blob.as_bytes() == EXAMPLE_DOC_PATH.read_bytes()

def test_init__load_blob_from_file_and_filename(temp_dir):
    """Test PolarisAIDataInsightLoader with file_path."""

    print(EXAMPLE_DOC_PATH.name)
    loader = PolarisAIDataInsightLoader(
        file=open(EXAMPLE_DOC_PATH, "rb").read(),
        filename=EXAMPLE_DOC_PATH.name,
        api_key="api_key",
        resources_dir=temp_dir,
    )
    
    assert loader.blob.mimetype == mimetypes.guess_type(EXAMPLE_DOC_PATH)[0]
    assert loader.blob.metadata.get("filename") == EXAMPLE_DOC_PATH.name
    assert loader.blob.as_bytes() == EXAMPLE_DOC_PATH.read_bytes()
    

# -- FAILURE TEST -- #
def test_init__wrong_parameter_combination_1(temp_dir):
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file_path=EXAMPLE_DOC_PATH,
            file=open(EXAMPLE_DOC_PATH, "rb").read(),
            filename=EXAMPLE_DOC_PATH.name,
            api_key="api_key",
            resources_dir=temp_dir,
        )

def test_init__wrong_parameter_combination_2(temp_dir):
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file=open(EXAMPLE_DOC_PATH, "rb").read(),
            api_key="api_key",
            resources_dir=temp_dir,
        )

def test_init__no_exist_api_key(temp_dir):
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file_path=EXAMPLE_DOC_PATH,
            api_key=None,
            resources_dir=temp_dir,
        )
        
def test_init__no_file_from_file_path(temp_dir):
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file_path=EXAMPLE_NOT_EXIST_DOC_PATH,
            api_key="api_key",
            resources_dir=temp_dir,
        )

def test_init__empty_from_file(temp_dir):
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file=None,
            filename="no_file.docx",
            api_key="api_key",
            resources_dir=temp_dir,
        )

def test_init__unsupported_extension_from_file_path(temp_dir):
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file_path=EXAMPLE_UNSUPPORTED_DOC_PATH,
            api_key="api_key",
            resources_dir=temp_dir,
        )

def test_init__unsupported_extension_from_filename(temp_dir):
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file=b"",
            filename="example.txt",
            api_key="api_key",
            resources_dir=temp_dir,
        )

