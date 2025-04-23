"""PODataInsight document loader."""

import os
import re
from pathlib import Path
from typing import Any, Dict, Iterator, Literal, Optional, Tuple, get_args, overload

from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from polaris_ai_datainsight import PolarisAIDataInsightExtractor

DataInsightModeType = Literal["single", "page", "element"]
StrPath = str | Path


class PolarisAIDataInsightLoader(BaseLoader):
    """
    Polaris AI DataInsight Document Loader.

    This loader extracts text, images, and other objects from various document formats.

    Supported file formats:
    `.doc`, `.docx`, `.ppt`, `.pptx`, `.xls`, `.xlsx`, `.hwp`, `.hwpx`

    Setup:
        Install ``langchain-polaris-ai-datainsight`` and
        set environment variable ``POLARIS_AI_DATA_INSIGHT_API_KEY``.

        ```bash
            pip install -U langchain-polaris-ai-datainsight
            export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
        ```

    Instantiate:
        - Using a file path:

            ```python
            from langchain_community.document_loaders import PolarisAIDataInsightLoader

            loader = PolarisAIDataInsightLoader(
                file_path="path/to/file.docx",
                resources_dir="path/to/save/resources/"
            )
            ```

        - Using file data and filename:

            ```python
            from langchain_community.document_loaders import PolarisAIDataInsightLoader

            loader = PolarisAIDataInsightLoader(
                file=open("path/to/file.docx", "rb").read(),
                filename="file.docx",
                resources_dir="path/to/save/resources/"
            )
            ```

    Lazy load:
        ```python
            docs = []
            docs_lazy = loader.lazy_load()

            for doc in docs_lazy:
                docs.append(doc)

            print(docs[0].page_content[:100])
            print(docs[0].metadata)
        ```
    """

    @overload
    def __init__(
        self,
        *,
        file_path: StrPath,
        api_key: Optional[str],
        resources_dir: StrPath = "app/",
        mode: DataInsightModeType = "single",
    ): ...

    @overload
    def __init__(
        self,
        *,
        file: bytes,
        filename: str,
        api_key: Optional[str],
        resources_dir: StrPath = "app/",
        mode: DataInsightModeType = "single",
    ): ...

    def __init__(self, *args, **kwargs):
        """
        Initialize the instance.

        The instance can be initialized in two ways:
        1. Using a file path: provide the `file_path` parameter
        2. Using bytes data: provide both `file` and `filename` parameters

        Note:
            If you provide both `file_path` and `file`/`filename`,
            a ValueError will be raised.

        Args:
            `file_path` (str, Path): Path to the file to process.
            Use instead of `file` and `filename`.
            `file` (bytes): Bytes data of the file to process
            . Use instead of `file_path` and must be provided with `filename`.
            `filename` (str): Name of the file when using bytes data.
            Must be provided with `file`.
            `api_key` (str, optional): API authentication key. If not provided,
            the API key will be retrieved from an environment variable.
            If no API key is found, a ValueError is raised.
            `resources_dir` (str, optional): Resource directory path. If the
            directory does not exist, it will be created. Defaults to "app/".
            `mode` (str, optional): Document loader mode. Valid options are "element",
            "page", or "single". Defaults to "single".

        Mode:
            The mode parameter determines how the document is loaded:
                `element`: Load each element in the pages as a separate Document object.
                `page`: Load each page in the document as a separate Document object.
                `single`: Load the entire document as a single Document object.

        Example:
            - Using a file path:

                ```python
                loader = PolarisAIDataInsightLoader(
                    file_path="path/to/file.docx",
                    api_key="your-api-key",         # or set as environment variable
                    resources_dir="path/to/save/resources/"
                )
                ```

            - Using file data and filename:

                ```python
                loader = PolarisAIDataInsightLoader(
                    file=open("path/to/file.docx", "rb").read(),
                    filename="file.docx",
                    api_key="your-api-key",         # or set as environment variable
                    resources_dir="path/to/save/resources/"
                )
                ```
        """

        self.mode: DataInsightModeType = kwargs.get("mode")
        self.doc_extractor: PolarisAIDataInsightExtractor = None
        _api_key = kwargs.get(
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

            self.doc_extractor = PolarisAIDataInsightExtractor(
                file_path=kwargs["file_path"],
                api_key=_api_key,
                resources_dir=kwargs.get("resources_dir", "app/"),
            )

        # Check if the file is provided
        elif "file" in kwargs and "filename" in kwargs:
            file = kwargs["file"]
            filename = kwargs["filename"]

            if not isinstance(file, bytes):
                raise ValueError("`file` must be a bytes object.")

            if not isinstance(filename, str):
                raise ValueError("`filename` must be a string.")

            self.doc_extractor = PolarisAIDataInsightExtractor(
                file=kwargs["file"],
                filename=kwargs["filename"],
                api_key=_api_key,
                resources_dir=kwargs.get("resources_dir", "app/"),
            )

        else:
            raise ValueError("Either file_path or file/filename must be provided.")

    @property
    def supported_modes(self) -> list[str]:
        return list(get_args(DataInsightModeType))

    def lazy_load(self) -> Iterator[Document]:
        json_data = self.doc_extractor.extract()

        # Convert the JSON data to Document objects
        document_list = self._convert_json_to_documents(json_data)

        yield from document_list

    def _convert_json_to_documents(self, json_data: Dict) -> list[Document]:
        """
        Convert JSON data to Document objects.

        Args:
            json_data (Dict): JSON data to convert.

        Returns:
            list[Document]: List of Document objects.
        """
        if self.mode == "element":
            document_list = []
            for doc_page in json_data["pages"]:
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(
                        doc_element
                    )
                    document_list.append(
                        Document(
                            page_content=element_content, metadata=element_metadata
                        )
                    )
            return document_list
        elif self.mode == "page":
            document_list = []
            for doc_page in json_data["pages"]:
                page_content = ""
                page_metadata: Dict[str, Any] = {
                    "elements": [],
                    "resources": {},  # {"image id" : "image path"}
                }
                # Parse elements in the page
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(
                        doc_element
                    )

                    # Add element content to page content
                    page_content += element_content + "\n"

                    # Add element metadata to page metadata
                    if "resources" in element_metadata:
                        page_metadata["resources"].update(
                            element_metadata.pop("resources")
                        )
                    page_metadata["elements"].append(element_metadata)

                # Add page document
                document_list.append(
                    Document(page_content=page_content, metadata=page_metadata)
                )
            return document_list
        else:
            doc_content = ""
            doc_metadata: Dict[str, Any] = {
                "elements": [],
                "resources": {},  # {"image id" : "image path"}
            }
            # Parse elements in the document
            for doc_page in json_data["pages"]:
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(
                        doc_element
                    )

                    # Add element content to document content
                    doc_content += element_content + "\n"

                    # Add element metadata to document metadata
                    if "resources" in element_metadata:
                        doc_metadata["resources"].update(
                            element_metadata.pop("resources")
                        )
                    doc_metadata["elements"].append(element_metadata)

            return [Document(page_content=doc_content, metadata=doc_metadata)]

    def _parse_doc_element(self, doc_element: Dict) -> Tuple[str, Dict]:
        """Parse a document element and extract its content and metadata.

        Args:
            doc_element (Dict): The document element to parse.

        Returns:
            Tuple[str, Dict]: The extracted content and metadata.
        """
        element_id = doc_element.get("id")
        data_type = doc_element.pop("type")
        content = doc_element.pop("content")
        boundary_box = doc_element.pop("boundaryBox")

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
            table_id = f"di.table.{element_id}"
            if "json" in content:
                table_content = content.get("json")
            elif "csv" in content:
                table_content = content.get("csv")
            else:
                raise ValueError(f"Table content not found for {element_id} element")

            element_content = f'\n\n<div id="{table_id}"/>\n'

            if element_metadata.get("resources") is None:
                element_metadata["resources"] = {}
            element_metadata["resources"][table_id] = table_content

        elif data_type == "chart":
            chart_id = f"di.chart.{element_id}"
            chart_image_path = content.get("src")
            chart_content = content.get("csv")
            if not chart_image_path:
                raise ValueError(f"Image path not found for {chart_image_path}")
            if not chart_content:
                raise ValueError(f"Chart content not found for {element_id} element")

            element_content = f'\n\n<div id="{chart_id}"/>\n'

            if element_metadata.get("resources") is None:
                element_metadata["resources"] = {}
            element_metadata["resources"][chart_id] = {
                "src": chart_image_path,
                "csv": chart_content,
            }

        else:  # image and shape for data_type
            image_id = f"di.image.{element_id}"
            image_path = content.get("src")  # image filename
            if not image_path:
                raise ValueError(f"Image path not found for {image_path}")

            # Make html tag for image resource
            element_content = f'\n\n<img src="#" alt="" id="{image_id}"/>\n\n'

            # Add metadata for image file access
            if element_metadata.get("resources") is None:
                element_metadata["resources"] = {}
            element_metadata["resources"][image_id] = image_path

        return element_content, element_metadata

    def _validate_data_structure(self, json_data):
        if "pages" not in json_data:
            raise ValueError("Invalid JSON data structure.")
        if "elements" not in json_data["pages"][0]:
            raise ValueError("Invalid JSON data structure.")

    @staticmethod
    def get_ids_from_document(document: Document) -> list[str]:
        """
        Look for image and table ids in the document's page content, and return list of ids.

        Args:
            document (Document): Document object to extract resource ids from.

        Returns:
            List[str]: List of resource ids.
        """
        if not isinstance(document, Document):
            raise ValueError("The document must be an instance of Document.")
        if "resources" not in document.metadata:
            return []

        # result dictionary
        resource_ids = []

        page_content = document.page_content
        page_content_split = page_content.split("\n\n")
        for content in page_content_split:
            if content.startswith('<img src="#" alt="" id="di.') or content.startswith(
                '<div id="di.'
            ):
                resource_id = re.search(r'id="(.*?)"', content)
                if resource_id:
                    resource_id = resource_id.group(1)
                    resource_ids.append(resource_id)
        return resource_ids

    @staticmethod
    def get_resource_by_id(document: Document, resource_id: str) -> str | list[dict]:
        """
        Get resource by id from the document.

        Args:
            document (Document): Document object to extract resource from.
            resource_id (str): Resource id to extract.

        Returns:
            str | list[dict]: Resource data.
        """
        if not isinstance(document, Document):
            raise ValueError("The document must be an instance of Document.")
        if "resources" not in document.metadata:
            return {}

        resource = document.metadata["resources"].get(resource_id)
        if not resource:
            raise ValueError(f"Resource with id {resource_id} not found.")
        return resource

    @staticmethod
    def get_resources_from_documents(documents: list[Document]) -> dict:
        """
        Get resources from documents.

        Args:
            documents (list[Document]): List of Document objects to extract resources from.

        Returns:
            dict: Dictionary of resources.
        """
        if not isinstance(documents, list):
            raise ValueError("The documents must be a list of Document objects.")

        resources = {}
        for document in documents:
            if "resources" in document.metadata:
                resources.update(document.metadata["resources"])
        return resources
