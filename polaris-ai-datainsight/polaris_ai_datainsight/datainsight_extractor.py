"""PolarisAIDataInsight document content extractor."""

import io
import json
import os
import zipfile
from pathlib import Path
from typing import Dict, Literal, Optional, Tuple, get_args, overload
import requests
try:
    from .utils.file_utils import create_temp_dir
    from .utils.http_utils import Blob, determine_mime_type
except ImportError:
    from polaris_ai_datainsight.utils.file_utils import create_temp_dir
    from polaris_ai_datainsight.utils.http_utils import Blob, determine_mime_type

POLARISOFFICE_DATAINSIGHT_BASE_URL = os.environ.get("DATA_INSIGHT_BASE_URL")

SupportedExtensionType = Literal[
    ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".hwp", ".hwpx"
]
StrPath = str | Path


class PolarisAIDataInsightExtractor:
    """
    Polaris AI DataInsight Document Loader.

    This loader extracts text, images, and other objects from various document formats.

    Supported file formats: `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.hwp`, `.hwpx`

    Setup:
        Install ``polaris-ai-datainsight`` and set environment variable ``POLARIS_AI_DATA_INSIGHT_API_KEY``.

        ```bash
            pip install -U polaris-ai-datainsight
            export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
        ```

    Instantiate:
        - Using a file path:

            ```python
                from polaris_ai_datainsight import PolarisAIDataInsightExtractor

                extractor = PolarisAIDataInsightExtractor(
                    file_path="path/to/file.docx",
                    api_key="your-api-key",
                    resources_dir="path/to/save/resources/"
                )
            ```

        - Using file data and filename:

            ```python
                from polaris_ai_datainsight import PolarisAIDataInsightExtractor

                extractor = PolarisAIDataInsightExtractor(
                    file=open("path/to/file.docx", "rb").read(),
                    filename="file.docx",
                    api_key="your-api-key",
                    resources_dir="path/to/save/resources/"
                )
            ```

    Extract:
        ```python
            docs = extractor.extract()

            # Elements in first page
            doc_elements = dict_data.get("pages")[0].get("elements")

            # Elements in all pages
            all_elements = []
            for page in dict_data.get("pages"):
                all_elements.extend(page.get("elements"))
        ```
    """

    @overload
    def __init__(
        self,
        *,
        file_path: StrPath,
        api_key: Optional[str],
        resources_dir: StrPath = "app/",
    ): ...

    @overload
    def __init__(
        self,
        *,
        file: bytes,
        filename: str,
        api_key: Optional[str],
        resources_dir: StrPath = "app/",
    ): ...

    def __init__(self, *args, **kwargs):
        """
        Initialize the instance.

        The instance can be initialized in two ways:
        1. Using a file path: provide the `file_path` parameter
        2. Using bytes data: provide both `file` and `filename` parameters

        Note:
            If you provide both `file_path` and `file`/`filename`, a ValueError will be raised.

        Args:
            `file_path` (str, Path): Path to the file to process. Use instead of `file` and `filename`.
            `file` (bytes): Bytes data of the file to process. Use instead of `file_path` and must be provided with `filename`.
            `filename` (str): Name of the file when using bytes data. Must be provided with `file`.
            `api_key` (str, optional): API authentication key. If not provided, the API key will be
                retrieved from an environment variable. If no API key is found, a ValueError is raised.
            `resources_dir` (str, optional): Resource directory path. If the
                directory does not exist, it will be created. Defaults to "app/".

        Example:
            - Using a file path:

                ```python
                extractor = PolarisAIDataInsightExtractor(
                    file_path="path/to/file.docx",
                    api_key="your-api-key",         # or set as environment variable
                    resources_dir="path/to/save/resources/"
                )
                ```

            - Using file data and filename:

                ```python
                extractor = PolarisAIDataInsightExtractor(
                    file=open("path/to/file.docx", "rb").read(),
                    filename="file.docx",
                    api_key="your-api-key",         # or set as environment variable
                    resources_dir="path/to/save/resources/"
                )
                ```
        """
        self._api_base_url = (
            "https://datainsight-api.polarisoffice.com/api/v1/datainsight/doc-extract"
        )
        self._supported_extensions = get_args(SupportedExtensionType)
        self.blob: Blob = None
        self.resources_dir: StrPath = kwargs.get("resources_dir", "app/")
        self.api_key: str = kwargs.get(
            "api_key", os.environ.get("POLARIS_AI_DATA_INSIGHT_API_KEY")
        )

        # Check if the file_path is provided
        if "file_path" in kwargs:
            if "file" in kwargs or "filename" in kwargs:
                raise ValueError(
                    "Both file_path and file/filename provided."
                    " Please provide only one valid combination."
                )

            file_path = kwargs["file_path"]
            if not isinstance(file_path, (str, Path)):
                raise ValueError("`file_path` must be a string or Path object.")

            if not Path(file_path).exists():
                raise ValueError(f"File {file_path} does not exist.")

            self.blob = Blob.from_path(
                path=file_path,
                mime_type=determine_mime_type(file_path),
                metadata={"filename": Path(file_path).name},
            )

        # Check if the file is provided
        elif "file" in kwargs and "filename" in kwargs:
            file = kwargs["file"]
            filename = kwargs["filename"]

            if not isinstance(file, bytes):
                raise ValueError("`file` must be a bytes object.")

            if not isinstance(filename, str):
                raise ValueError("`filename` must be a string.")

            self.blob = Blob.from_data(
                data=file,
                mime_type=determine_mime_type(filename),
                metadata={"filename": filename},
            )

        else:
            raise ValueError("Either file_path or file/filename must be provided.")

        # Validate the file extension
        if not self.validate_extension(self.blob.metadata.get("filename")):
            raise ValueError(
                "Unsupported file extension."
                f" Supported extensions are: {self._supported_extensions}"
            )

        # create the directory if it does not exist
        if not Path(self.resources_dir).exists():
            Path(self.resources_dir).mkdir(parents=True, exist_ok=True)

        # Set the API key
        if not self.api_key:
            raise ValueError(
                "API key is not provided."
                " Please pass the `api_key` as a parameter,"
                " or set the `POLARIS_AI_DATA_INSIGHT_API_KEY` environment variable."
            )

    @property
    def supported_extensions(self) -> list[str]:
        """
        Returns a list of supported file extensions.
        """
        return self._supported_extensions

    def validate_extension(self, file_path: StrPath) -> bool:
        """
        Validates if the file extension is supported.

        Args:
            filename (str): The name of the file to validate.

        Returns:
            bool: True if the file extension is supported, False otherwise.
        """
        extension = Path(file_path).suffix.lower()
        return extension in self._supported_extensions

    def extract(self) -> Dict:
        # Create a temporary directory for unzipping the response file
        unzip_dir_path = create_temp_dir(self.resources_dir)

        # Get the input file path
        response = self._get_response(self.blob)

        # Unzip the response and get the JSON data
        json_data, images_path_map = self._unzip_response(response, unzip_dir_path)

        # Check if the "page", "elements" keys are present in the JSON data
        self._validate_data_structure(json_data)

        # Post-process the JSON data to replace image filenames with paths
        self._postprocess_json(json_data, images_path_map)

        return json_data

    def _get_response(self, blob: Blob) -> requests.Response:
        try:
            # Prepare the request
            filename = blob.metadata.get("filename")
            files = {"file": (filename, blob.data, blob.mimetype)}
            headers = {"x-po-di-apikey": self.api_key}

            # Send the request
            response = requests.post(self._api_base_url, headers=headers, files=files)
            response.raise_for_status()
            return response
        except requests.HTTPError as e:
            raise ValueError(f"HTTP error: {e.response.text}")
        except requests.RequestException as e:
            # Handle any request-related exceptions
            raise ValueError(f"Failed to send request: {e}")
        except Exception as e:
            # Handle any other exceptions
            raise ValueError(f"An error occurred: {e}")

    def _unzip_response(
        self, response: requests.Response, dir_path: str
    ) -> Tuple[Dict, Dict]:
        # Unzip the response
        zip_content = response.content
        json_data = {}

        # Unzip the response
        with zipfile.ZipFile(io.BytesIO(zip_content), "r") as zip_ref:
            zip_ref.extractall(dir_path)

            # Find .json file
            json_files = list(Path(dir_path).rglob("*.json"))
            if not json_files:
                raise ValueError("No JSON file found in the response.")

            # Find .png file and create a dictionary of image paths
            image_path_list = list(Path(dir_path).rglob("*.png"))
            images_path_map = {}
            for image_path in image_path_list:
                image_filename = Path(image_path).name
                images_path_map[image_filename] = image_path.absolute()

            # Read the JSON file
            with open(json_files[0], "r", encoding="utf-8") as json_file:
                data = json_file.read()

            # Parse the JSON data
            try:
                json_data = json.loads(data)
                return json_data, images_path_map
            except json.JSONDecodeError as e:
                # Handle JSON decode errors
                raise ValueError(f"Failed to decode JSON response: {e}")

    def _postprocess_json(self, json_data: Dict, images_path_map: Dict):
        for doc_page in json_data["pages"]:
            for doc_element in doc_page["elements"]:
                if doc_element.get("type") != "text":
                    self._replace_image_filenames_with_paths(
                        doc_element, images_path_map
                    )

    def _replace_image_filenames_with_paths(
        self, doc_element: Dict, images_path_map: Dict
    ):
        # Convert image filename to image path
        if "src" not in doc_element.get("content", {}):
            return

        image_filename = doc_element.get("content").get("src")  # image filename
        image_path = images_path_map.get(image_filename)
        if not image_path:
            raise ValueError(f"Image path not found for {image_filename}")

        doc_element["content"]["src"] = image_path

    def _validate_data_structure(self, json_data):
        if "pages" not in json_data:
            raise ValueError("Invalid JSON data structure.")
        if "elements" not in json_data["pages"][0]:
            raise ValueError("Invalid JSON data structure.")
