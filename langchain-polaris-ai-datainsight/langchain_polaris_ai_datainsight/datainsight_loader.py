"""PODataInsight document loader."""
from pathlib import Path
from typing import Dict, Iterator, Literal, Optional, Tuple, overload, get_args
from langchain_core.document_loaders.base import BaseLoader
from langchain_core.documents import Document
from polaris_ai_datainsight import PolarisAIDataInsightExtractor

DataInsightModeType = Literal["single", "page", "element"]

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
        mode: DataInsightModeType = "single"
    ): ...

    @overload
    def __init__(
        self,
        *,
        file: bytes,
        filename: str,
        api_key: Optional[str],
        resources_dir: str | Path = "app/",
        mode: DataInsightModeType = "single"
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
        
        self.mode = kwargs.get("mode")
        self.doc_extractor: PolarisAIDataInsightExtractor = None
        
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
                api_key=kwargs.get("api_key"),
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
                api_key=kwargs.get("api_key"),
                resources_dir=kwargs.get("resources_dir", "app/"),
            )            
        
        else:
            raise ValueError("Either file_path or file/filename must be provided.")

    @property
    def supported_modes(self) -> list[str]:
        return get_args(DataInsightModeType)

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
                    element_content, element_metadata = self._parse_doc_element(doc_element)
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
                # Parse elements in the page
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(doc_element)

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
                for doc_element in doc_page["elements"]:
                    element_content, element_metadata = self._parse_doc_element(doc_element)
                    
                    # Add element content to document content
                    doc_content += element_content + "\n"
                    
                    # Add element metadata to document metadata
                    if "resources" in element_metadata:
                        doc_metadata["resources"].update(element_metadata.pop("resources"))
                    doc_metadata["elements"].append(element_metadata)

            return [Document(page_content=doc_content, metadata=doc_metadata)]

    def _parse_doc_element(self, doc_element: Dict) -> Tuple[str, Dict]:
        """ Parse a document element and extract its content and metadata.

        Args:
            doc_element (Dict): The document element to parse.        
        
        Returns:
            Tuple[str, Dict]: The extracted content and metadata.
        """
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
            # TODO: Add table metadata
            element_content = content.get("json")
        else:
            image_path = content.get("src")   # image filename
            if not image_path:
                raise ValueError(f"Image path not found for {image_filename}")
            image_filename = Path(image_path).name
                    
            # Make html tag for image resource
            element_content = f'\n\n<img src="#" alt="" id="{image_filename}"/>\n\n'
                                        
            # Add metadata for image file access
            if element_metadata.get("resources") is None:
                element_metadata["resources"] = {}
            element_metadata["resources"][image_filename] = image_path
        
        return element_content, element_metadata

    def _validate_data_structure(self, json_data):
        if "pages" not in json_data:
            raise ValueError("Invalid JSON data structure.")
        if "elements" not in json_data["pages"][0]:
            raise ValueError("Invalid JSON data structure.")
