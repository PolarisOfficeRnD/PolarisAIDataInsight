from pathlib import Path
import tempfile
from polaris_ai_datainsight import PolarisAIDataInsightExtractor
from langchain_polaris_ai_datainsight import PolarisAIDataInsightLoader
import pytest

# -- For Success Test -- #
EXAMPLE_DOC_PATH = Path(__file__).parent.parent / "examples" / "example.docx"

# -- For Failure Test -- #
EXAMPLE_UNSUPPORTED_DOC_PATH = Path(__file__).parent.parent / "examples" / "example.txt"
EXAMPLE_NOT_EXIST_DOC_PATH = Path(__file__).parent.parent / "examples" / "no_file.docx"

@pytest.fixture
def temp_resources_dir():
    """Create a temporary directory."""
    with tempfile.TemporaryDirectory(dir=Path(__file__).parent.parent / "examples") as temp_dir:
        yield temp_dir
        
######################
# -- SUCCESS TEST -- #
######################

@pytest.mark.parametrize("file_path", [EXAMPLE_DOC_PATH])
def test_init__from_file_path(temp_resources_dir, file_path: Path):
    loader = PolarisAIDataInsightLoader(
        file_path=file_path,
        api_key="api_key",
        resources_dir=temp_resources_dir
    )
    
    assert loader.doc_extractor is not None
    assert isinstance(loader.doc_extractor, PolarisAIDataInsightExtractor)
    

@pytest.mark.parametrize("file", [open(EXAMPLE_DOC_PATH, "rb").read()])
@pytest.mark.parametrize("filename", [EXAMPLE_DOC_PATH.name])
def test_init__from_file_and_filename(temp_resources_dir, file: bytes, filename: str):
    loader = PolarisAIDataInsightLoader(
        file=file,
        filename=filename,
        api_key="api_key",
        resources_dir=temp_resources_dir
    )
    
    assert loader.doc_extractor is not None
    assert isinstance(loader.doc_extractor, PolarisAIDataInsightExtractor)

######################
# -- FAILURE TEST -- #
######################

@pytest.mark.parametrize("file_path", [EXAMPLE_DOC_PATH])
@pytest.mark.parametrize("file", [open(EXAMPLE_DOC_PATH, "rb").read()])
@pytest.mark.parametrize("filename", [EXAMPLE_DOC_PATH.name])
def test_init__wrong_parameter_combination(temp_resources_dir, file_path: Path, file: bytes, filename: str):
    # When both file_path and file are provided
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file_path=file_path,
            file=file,
            filename=filename,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )
    
    # When file is provided without filename
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file=file,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )

@pytest.mark.parametrize("file_path", [EXAMPLE_NOT_EXIST_DOC_PATH])
def test_init__no_exist_file(temp_resources_dir, file_path: Path):
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file_path=file_path,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )

@pytest.mark.parametrize("file", [None])
@pytest.mark.parametrize("filename", [EXAMPLE_NOT_EXIST_DOC_PATH.name])
def test_init__empty_from_file(temp_resources_dir, file: bytes, filename: str):
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
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
        PolarisAIDataInsightLoader(
            file_path=file_path,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )
    
    # When file is provided, check supported file type
    with pytest.raises(ValueError):
        PolarisAIDataInsightLoader(
            file=file,
            filename=filename,
            api_key="api_key",
            resources_dir=temp_resources_dir,
        )
