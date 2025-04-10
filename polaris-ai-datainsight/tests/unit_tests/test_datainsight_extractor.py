import mimetypes
from pathlib import Path
import tempfile
from polaris_ai_datainsight import PolarisAIDataInsightExtractor
import pytest

# -- For Success Test -- #
EXAMPLE_DOC_PATH = Path(__file__).parent.parent / "examples" / "example.docx"

# -- For Failure Test -- #
EXAMPLE_UNSUPPORTED_DOC_PATH = Path(__file__).parent.parent / "examples" / "example.txt"
EXAMPLE_NOT_EXIST_DOC_PATH = Path(__file__).parent.parent / "examples" / "no_file.docx"

@pytest.fixture
def temp_resources_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory(
            prefix="example_", 
            dir=Path(__file__).parent.parent / "examples"
        ) as temp_resources_dir:
        yield Path(temp_resources_dir)

######################
# -- SUCCESS TEST -- #
######################

@pytest.mark.parametrize("file_path", [EXAMPLE_DOC_PATH])
def test_init__load_blob_from_file_path(temp_resources_dir, file_path):
    """Test PolarisAIDataInsightLoader with file_path."""

    extractor = PolarisAIDataInsightExtractor(
        file_path=file_path,
        api_key="api_key",
        resources_dir=temp_resources_dir,
    )
    
    assert extractor.blob.mimetype == mimetypes.guess_type(file_path)[0]
    assert extractor.blob.metadata.get("filename") == file_path.name
    assert extractor.blob.data == file_path.read_bytes()

@pytest.mark.parametrize("file", [open(EXAMPLE_DOC_PATH, "rb").read()])
@pytest.mark.parametrize("filename", [EXAMPLE_DOC_PATH.name])
def test_init__load_blob_from_file_and_filename(temp_resources_dir, file: bytes, filename: str):
    """Test PolarisAIDataInsightLoader with file_path."""
    extractor = PolarisAIDataInsightExtractor(
        file=file,
        filename=filename,
        api_key="api_key",
        resources_dir=temp_resources_dir
    )
    
    assert extractor.blob.mimetype == mimetypes.guess_type(EXAMPLE_DOC_PATH)[0]
    assert extractor.blob.metadata.get("filename") == EXAMPLE_DOC_PATH.name
    assert extractor.blob.data == EXAMPLE_DOC_PATH.read_bytes()
    

######################
# -- FAILURE TEST -- #
######################

@pytest.mark.parametrize("file_path", [EXAMPLE_DOC_PATH])
@pytest.mark.parametrize("file", [open(EXAMPLE_DOC_PATH, "rb").read()])
@pytest.mark.parametrize("filename", [EXAMPLE_DOC_PATH.name])
def test_init__wrong_parameter_combination(temp_resources_dir, file_path: Path, file: bytes, filename: str):
    # When both file_path and file are provided
    with pytest.raises(ValueError):
        PolarisAIDataInsightExtractor(
            file_path=file_path,
            file=file,
            filename=filename,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )

    # When file is provided without filename
    with pytest.raises(ValueError):
        PolarisAIDataInsightExtractor(
            file=file,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )

def test_init__no_exist_api_key(temp_resources_dir):
    with pytest.raises(ValueError):
        PolarisAIDataInsightExtractor(
            file_path=EXAMPLE_DOC_PATH,
            api_key=None,
            resources_dir=temp_resources_dir,
        )


@pytest.mark.parametrize("file_path", [EXAMPLE_NOT_EXIST_DOC_PATH])
def test_init__no_exist_file(temp_resources_dir, file_path: Path):
    with pytest.raises(ValueError):
        PolarisAIDataInsightExtractor(
            file_path=file_path,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )

@pytest.mark.parametrize("file", [None])
@pytest.mark.parametrize("filename", [EXAMPLE_NOT_EXIST_DOC_PATH.name])
def test_init__empty_from_file(temp_resources_dir, file: bytes, filename: str):
    with pytest.raises(ValueError):
        PolarisAIDataInsightExtractor(
            file=file,
            filename=filename,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )

@pytest.mark.parametrize("file_path", [EXAMPLE_UNSUPPORTED_DOC_PATH])
@pytest.mark.parametrize("file", [open(EXAMPLE_UNSUPPORTED_DOC_PATH, "rb").read()])
@pytest.mark.parametrize("filename", [EXAMPLE_UNSUPPORTED_DOC_PATH.name])
def test_init__unsupported_extension(temp_resources_dir, file_path: Path, file: bytes, filename: str):
    # When file_path is provided, check supported file type
    with pytest.raises(ValueError):
        PolarisAIDataInsightExtractor(
            file_path=file_path,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )
    
    # When file is provided, check supported file type
    with pytest.raises(ValueError):
        PolarisAIDataInsightExtractor(
            file=file,
            filename=filename,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )
