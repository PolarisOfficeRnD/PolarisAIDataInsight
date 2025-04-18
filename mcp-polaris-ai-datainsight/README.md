# ![logo](/assets/logo/polarisoffice-logo-small.svg) mcp-polaris-ai-datainsight

[Polaris AI DataInsight](https://datainsight.polarisoffice.com/) is an API service that easily converts documents in various formats into structured data (such as JSON).

This tool supports the extraction of text, images, and other elements from various document formats (e.g., .doc, .docx, .ppt, .pptx, .xls, .xlsx, .hwp, .hwpx, .pdf).

For more details, please refer to the [documentation](https://datainsight.polarisoffice.com/documentation/overview).

## Feature

### Doc Extract
Extract text, images, and other elements from various document formats.
- Images in the document are stored on local storage, and the corresponding image paths are included in the JSON output.
- Tables are represented in JSON format, as illustrated in [this example](examples/example_tool_output.json).

## Installation and Setup

1. Generate an API key
    - Refer to [this guide](https://datainsight.polarisoffice.com/documentation/quickstart) to generate an API key.

2. Choose an installation method

### Method 1: CLI Installation

~~TODO: Supported clients: cursor, claude~~

### Method 2: Manual Configuration

If you prefer a manual setup, add the following configuration to your IDE's MCP config file:

```json
{
  "mcpServers": {
    "": {
      "command": "npx",
      "args": [],
      "env": {}
    }
  }
}
```

Config file locations:

- Cursor: `~/.cursor/mcp.json`
- Claude: `~/.claude/mcp_config.json`

### Method 3: VS Code Installation

~~TODO~~

### Method 4: Clone git repository

Preinstall `uv` and `poetry`.

1. Clone repository
    ```sh
    git clone --branch main https://github.com/PolarisOfficeRnD/PolarisAIDataInsight.git
    ```
    If you want to clone only `mcp-polaris-ai-datainsight` directory:
    ```sh
    # Git Version >= 2.25
    git clone --filter=blob:none --sparse --branch main https://github.com/PolarisOfficeRnD/PolarisAIDataInsight.git
    ```
    ```sh
    cd PolarisAIDataInsight
    ```
    ```sh
    git sparse-checkout set mcp-polaris-ai-datainsight
    ```
2. Install python dependencies in virtual environment
    ```sh
    cd mcp-polaris-ai-datainsight
    ```
    ```sh
    uv venv .venv

    # Linux
    source .venv/bin/activate
    # Windows
    .venv\bin\activate
    ```
    ```sh
    poetry install
    ```
3. Set API Key as environment value and Run server
    ```sh
    # Linux
    export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
    # Windows
    set POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
    ```
    ```sh
    # Linux
    uv run src/server.py
    # Windows
    uv run src\server.py
    ```

## Output

- Refer to [this example](examples/example_tool_output.json) for a sample output.
- Alternatively, you can test our API using the [playground](https://datainsight.polarisoffice.com/playground/doc-extract).
