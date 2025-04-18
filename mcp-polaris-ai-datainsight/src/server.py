from mcp.server.fastmcp import FastMCP
from .tools.datainsight_tool import call_datainsight_api

mcp = FastMCP("polaris-ai-datainsight", dependencies=["polaris_ai_datainsight"])

mcp.add_tool(
    func=call_datainsight_api,
    name="extract_content_from_document",
    description=
    """
    Extract the contents of a document into a structured JSON format. 
    Supports multiple file types including docx, doc, pptx, ppt, xlsx, xls, pdf, and hwp.
    `file_path` specifies the absolute path to the input document.
    `resources_dir` is the directory where image files extracted 
    from the document will be stored; it must be provided as an absolute path 
    and must have write permissions (read permissions are also recommended).
    Only works within allowed directories.
    """
)

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()