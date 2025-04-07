"""PODataInsight document loader."""

from enum import Enum
import io
import json
import mimetypes
import os
import tempfile
import typing
import zipfile
from pathlib import Path
from typing import Dict, Iterator, Literal, Optional, Tuple, overload

import requests
from langchain_core.document_loaders import Blob
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document

POLARISOFFICE_DATAINSIGHT_BASE_URL = os.environ.get("DATA_INSIGHT_BASE_URL")

SUPPORTED_EXTENSTIONS = ['.doc', '.docx', '.ppt', '.pptx', '.xls', '.xlsx', '.hwp', '.hwpx', '.pdf']

DataInsightModeType = Literal["element", "page", "single"]
DATAINSIGHT_MODE_TYPE_DEFAULT: DataInsightModeType = "single"

def create_temp_dir(dir_path: str) -> Path:
    temp_dir = Path(tempfile.mkdtemp(dir=dir_path))
    return temp_dir
    
def determine_mime_type(filename: str) -> str:
    mime_type = mimetypes.guess_type(filename)[0]
    if mime_type is None:
        mime_type = "application/octet-stream"
    return mime_type

def validate_extension(file_path: str | Path, valid_extensions: list[str]) -> bool:
    extension = Path(file_path).suffix.lower()
    return extension in valid_extensions

class PolarisAIDataInsightLoader(BaseLoader):
    """
    PODataInsight document loader integration

    Setup:
        Install ``langchain-polaris-ai-datainsight`` and set environment variable ``POLARIS_AI_DATA_INSIGHT_API_KEY``.

        .. code-block:: bash
            pip install -U langchain-polaris-ai-datainsight
            export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"

    Instantiate:
        .. code-block:: python
            from langchain_community.document_loaders import PolarisAIDataInsightLoader

            loader = PolarisAIDataInsightLoader(
                file_path="path/to/file",
                resources_dir="path/to/dir"
            )

    # Load
    Lazy load:
        .. code-block:: python
            docs = []
            docs_lazy = loader.lazy_load()

            for doc in docs_lazy:
                docs.append(doc)
            print(docs[0].page_content[:100])
            print(docs[0].metadata)
    """    
    
    @overload
    def __init__(
        self,
        *,
        file_path: str | Path,
        api_key: Optional[str],
        resources_dir: str | Path = "app/",
        mode: DataInsightModeType = DATAINSIGHT_MODE_TYPE_DEFAULT
    ): ...

    @overload
    def __init__(
        self,
        *,
        file: bytes,
        filename: str,
        api_key: Optional[str],
        resources_dir: str | Path = "app/",
        mode: DataInsightModeType = DATAINSIGHT_MODE_TYPE_DEFAULT
    ): ...
        
    def __init__(self, *args, **kwargs):
        """
        This class is used to load document contents from the Polaris Office Data Insight API response.
        
        This constructor supports two methods for specifying file input:

        Method 1:
            Provide the ``file_path`` parameter.
            - ``file_path`` (str or Path): The path to the file.

        Method 2:
            Provide both the ``file`` and ``filename`` parameters.
            - ``file`` (bytes): The file data.
            - ``filename`` (str): The name of the file.

        Additional parameters:
            - ``api_key`` (Optional[str]): Optional API key. If not provided, the API key from the environment
            variable will be used.
            - ``resources_dir`` (str or Path, optional): The directory for saving resource files. Defaults to ``"app/"``.
            - ``mode`` (DataInsightModeType, optional): Extraction mode. Must be one of ``"element"``, ``"page"``, or
            ``"single"``. Defaults to ``"single"``.

        Raises:
            ValueError: If neither ``file_path`` nor both ``file`` and ``filename`` are provided, or if an invalid
                        combination of parameters is given.
        """
        self.blob: Blob = None
        
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
            
            self._init_from_file_path(file_path)

        # Check if the file is provided
        elif "file" in kwargs and "filename" in kwargs:
            file = kwargs["file"]
            filename = kwargs["filename"]
            
            if not isinstance(file, bytes):
                raise ValueError("`file` must be a bytes object.")
            
            if not isinstance(filename, str):
                raise ValueError("`filename` must be a string.")
            
            self._init_from_file_and_filename(file, filename)
        
        else:
            raise ValueError("Either file_path or file/filename must be provided.")
        
        # Validate the file extension
        if not validate_extension(self.blob.metadata.get("filename"), SUPPORTED_EXTENSTIONS):
            raise ValueError( "Unsupported file extension."
                             f" Supported extensions are: {SUPPORTED_EXTENSTIONS}")
        
        # Set other attributes
        self.api_key = kwargs.get("api_key", os.environ.get("POLARIS_AI_DATA_INSIGHT_API_KEY"))
        self.resources_dir = kwargs.get("resources_dir", "app/")
        self.mode = kwargs.get("mode", DATAINSIGHT_MODE_TYPE_DEFAULT)
        
        # create the directory if it does not exist
        if not Path(self.resources_dir).exists():
            Path(self.resources_dir).mkdir(parents=True, exist_ok=True)
        
        # Set the API key
        if not self.api_key:
            raise ValueError("API key is not provided."
                             " Please pass the `api_key` as a parameter,"
                             " or set the `POLARIS_AI_DATA_INSIGHT_API_KEY` environment variable.")
    
    def _init_from_file_path(self, file_path):        
        if not Path(file_path).exists():
            raise ValueError(f"File {file_path} does not exist.")
        
        self.blob = Blob.from_path(
            path=file_path, 
            mime_type=determine_mime_type(file_path),
            metadata={"filename": Path(file_path).name}
        )

    def _init_from_file_and_filename(self, file, filename):                        
        self.blob = Blob.from_data(
            data=file,
            mime_type=determine_mime_type(filename),
            metadata={"filename": filename}
        )

    def lazy_load(self) -> Iterator[Document]:
        # Create a temporary directory for unzipping the response file
        unzip_dir_path = create_temp_dir(self.resources_dir)
        
        # Get the input file path
        response = self._get_response(self.blob)

        # Unzip the response and get the JSON data
        json_data, images_path_map = self._unzip_response(response, unzip_dir_path)

        # Check if the "page", "elements" keys are present in the JSON data
        self._validate_data_structure(json_data)

        # Convert the JSON data to Document objects
        document_list = self._convert_json_to_documents(json_data, images_path_map)

        yield from document_list

    def _get_response(self, blob: Blob) -> requests.Response:
        try:
            # Prepare the request
            filename = blob.metadata.get("filename")
            files = {
                "file": (filename, blob.as_bytes(), blob.mimetype)
            }
            headers={"x-po-di-apikey": self.api_key},

            # Send the request
            response = requests.post(POLARISOFFICE_DATAINSIGHT_BASE_URL, headers=headers, files=files)
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

    def _unzip_response(self, response: requests.Response, dir_path: str) -> Tuple[Dict, Dict]:
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
                images_path_map[image_filename] = image_path

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

    def _convert_json_to_documents(self, json_data: Dict, images_path_map: Dict) -> list[Document]:
        """
        Convert JSON data to Document objects.
        
        Args:
            json_data (Dict): JSON data to convert.
            images_path_map (Dict): Dictionary mapping image file name to image path.
                
        Returns:
            list[Document]: List of Document objects.        
        """
        if self.mode == "element":
            document_list = []
            for doc_page in json_data["pages"]:
                page_size = (doc_page["pageWidth"], doc_page["pageHeight"])
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(
                        doc_element, images_path_map, page_size
                    )
                    document_list.append(
                        Document(page_content=element_content, metadata=element_metadata)
                    )
            return document_list
        elif self.mode == "page":
            document_list = []
            for doc_page in json_data["pages"]:
                page_content = ""
                page_metadata = {
                    "elements": [],  # [{"type": "...", "coordinates": {"left": 0, "top": 0, "right": 0, "bottom": 0}}, ...]
                    "resources": {}     # {"image id" : "image path"}
                }            
                page_size = (doc_page["pageWidth"], doc_page["pageHeight"])
                # Parse elements in the page
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(
                        doc_element, images_path_map, page_size
                    )

                    # Add element content to page content
                    page_content += element_content + "\n"
                    
                    # Add element metadata to page metadata
                    if "resources" in element_metadata:
                        page_metadata["resources"].update(element_metadata.pop("resources"))
                    page_metadata["elements"].append(element_metadata)
                
                # Add page document
                document_list.append(
                    Document(page_content=page_content, metadata=page_metadata)
                )
            return document_list
        else:
            doc_content = ""
            doc_metadata = {
                "elements": [],  # [{"type": "...", "coordinates": {"left": 0, "top": 0, "right": 0, "bottom": 0}}, ...]
                "resources": {}     # {"image id" : "image path"}
            }
            # Parse elements in the document
            for doc_page in json_data["pages"]:
                page_size = (doc_page["pageWidth"], doc_page["pageHeight"])
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(
                        doc_element, images_path_map, page_size
                    )
                    
                    # Add element content to document content
                    doc_content += element_content + "\n"
                    
                    # Add element metadata to document metadata
                    if "resources" in element_metadata:
                        doc_metadata["resources"].update(element_metadata.pop("resources"))
                    doc_metadata["elements"].append(element_metadata)

            return [Document(page_content=doc_content, metadata=doc_metadata)]

    def _parse_doc_element(self, doc_element: Dict, images_path_map: Dict, page_size: Tuple[int, int]) -> Tuple[str, Dict]:
        """ Parse a document element and extract its content and metadata.

        Args:
            doc_element (Dict): The document element to parse.
            images_path_map (Dict): Dictionary mapping image file name to image path.
        
        Exceptions:
            ValueError: If the image path is not found.
        
        Returns:
            Tuple[str, Dict]: The extracted content and metadata.
        """
        data_type = doc_element.pop("type")
        content = doc_element.pop("content")
        boundary_box = doc_element.pop("boundaryBox")
   
        # Convert absolute coordinates to relative coordinates
        if page_size[0] > 0:
            boundary_box["left"] = boundary_box["left"] / page_size[0]
            boundary_box["right"] = boundary_box["right"] / page_size[0]
        if page_size[1] > 0:
            boundary_box["top"] = boundary_box["top"] / page_size[1]
            boundary_box["bottom"] = boundary_box["bottom"] / page_size[1]

        # Result dictionary
        element_content = ""
        element_metadata = {
            "type": data_type,
            "coordinates": boundary_box,
        }
        
        # Extract the content data based on the data type
        if data_type == "text":
            element_content = content.get("text")
        elif data_type == "table":
            # TODO: Add table metadata
            element_content = content.get("json")
        else:
            image_filename = content.get("src")   # image filename
            image_path = images_path_map.get(image_filename)
            if not image_path:
                raise ValueError(f"Image path not found for {image_filename}")
                    
            # Make html tag for image resource
            element_content = f'\n\n<img src="#" alt="" id="{image_filename}"/>\n\n'
                                        
            # Add metadata for image file access
            element_metadata["resources"][image_filename] = image_path
        
        return element_content, element_metadata

    def _validate_data_structure(self, json_data):
        if "pages" not in json_data:
            raise ValueError("Invalid JSON data structure.")
        if "elements" not in json_data["pages"][0]:
            raise ValueError("Invalid JSON data structure.")
