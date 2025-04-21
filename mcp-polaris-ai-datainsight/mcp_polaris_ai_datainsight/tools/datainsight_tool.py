import os
from pathlib import Path
from polaris_ai_datainsight import PolarisAIDataInsightExtractor

def call_datainsight_api(
    file_path: Path, resources_dir: Path
) -> str:
    # Check if API Key is set in the environment variable
    if "POLARIS_AI_DATA_INSIGHT_API_KEY" not in os.environ:
        return "Please set the `POLARIS_AI_DATA_INSIGHT_API_KEY` environment variable."
    
    # Check if the resources directory is accessible and writable
    try:
        resources_dir = Path(resources_dir)
        if not resources_dir.exists():
            return f"The `resources_dir` is not found. Retry with a absolute file path."
        if not resources_dir.is_dir():
            return f"The `resources_dir` Path is not a directory: {resources_dir}"
        if not os.access(resources_dir, os.W_OK):
            return f"The `resources_dir` is not writable: {resources_dir}"
    except Exception as e:
        return f"Error: {str(e)}"
    
    # Check if the file path is valid
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return f"File is not found. Retry with a absolute file path."
        if not file_path.is_file():
            return f"The Path is not a regular file: {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"
    
    try:
        extractor = PolarisAIDataInsightExtractor(file_path=file_path, resources_dir=resources_dir)
        docs = extractor.extract()
        if not docs:
            return "No content extracted."
        return docs
    except Exception as e:
        return f"Error: {str(e)}"
