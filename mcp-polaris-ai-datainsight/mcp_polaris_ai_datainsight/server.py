import logging
from mcp.server.fastmcp import FastMCP
try:
    from .tools.datainsight_tool import call_datainsight_api
except ImportError:
    from mcp_polaris_ai_datainsight.tools.datainsight_tool import call_datainsight_api

logger = logging.getLogger(__name__)
mcp = FastMCP("polaris-ai-datainsight", dependencies=["polaris_ai_datainsight"])

mcp.add_tool(
    fn=call_datainsight_api,
    name="extract_content_from_document",
    description=
    """
    Extract the contents of a document into a structured JSON format. 
    Supports multiple file types including docx, doc, pptx, ppt, xlsx, xls, and hwp.
    `file_path` specifies the absolute path to the input document.
    `resources_dir` is the directory where image files extracted 
    from the document will be stored; it must be provided as an absolute path 
    and must have write permissions (read permissions are also recommended).
    Only works within allowed directories.
    """
)

def run():
    logger.info("Starting MCP server...")
    mcp.run()

if __name__ == "__main__":
    run()
