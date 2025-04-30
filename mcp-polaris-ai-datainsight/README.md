# ![logo](https://raw.githubusercontent.com/PolarisOfficeRnD/PolarisAIDataInsight/main/assets/logo/polarisoffice-logo-small.svg) mcp-polaris-ai-datainsight

[Polaris AI DataInsight](https://datainsight.polarisoffice.com/) is an API service that easily converts documents in various formats into structured data (such as JSON).

This tool supports the extraction of text, images, and other elements from various document formats (e.g., .doc, .docx, .ppt, .pptx, .xls, .xlsx, .hwp, .hwpx).

For more details, please refer to the [documentation](https://datainsight.polarisoffice.com/documentation/overview).

## Feature

### Extract content from document
Extract text, images, and other elements from various document formats.
- Images in the document are stored on local storage, and the corresponding image paths are included in the JSON output.
- Tables are represented in JSON format, as illustrated in [this example](examples/example_tool_output.json).

>⚠️ **It is recommended to use [`file_system` MCP Server](https://github.com/modelcontextprotocol/servers/tree/main/src/filesystem) together with this.**

`file_system` is required whenever your workflow needs to  

- create directories to store resources, or  
- verify existing file paths.  

Below is an example configuration how to use `file_system` with Claude:
```yaml
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/path/to/allowed/directory_1",
        "/path/to/allowed/directory_2",
        "..."
      ]
    }
  }
}
```


## Installation and Setup

1. Generate an API key
    - Refer to [this guide](https://datainsight.polarisoffice.com/documentation/quickstart) to generate an API key.

2. Choose an installation method

### Method 1: Manual Configuration

Prerequirement: [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/).

If you prefer a manual setup, add the following configuration to your IDE's MCP config file:

```json
{
  "mcpServers": {
    "datainsight": {
      "command": "uvx",
      "args": ["--no-cache", "mcp-polaris-ai-datainsight@latest"],
      "env": {
        "POLARIS_AI_DATA_INSIGHT_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Method 2: Docker Container

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
2. Build Docker image:
    ```sh
    cd mcp-polaris-ai-datainsight

    docker build . -t mcp-polaris-ai-datainsight
    ```
3. Use this MCP Server config:
    ```json
    {
      "mcpServers": {
        "datainsight": {
          "command": "docker",
          "args": [
            "run",
            "-i",
            "--rm",
            "-e",
            "POLARIS_AI_DATA_INSIGHT_API_KEY=your-api-key"
            "mcp-polaris-ai-datainsight",
          ]
        }
      }
    }
    ```

### Method 3: Clone git repository 

Preinstall `uv` and `poetry`.

1. Clone repository (please refer to __Method 4__ if you want to clone only `mcp-polaris-ai-datainsight` directory)
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

    
    poetry install --no-root
    ```
3. Set API Key as environment value and Run server
    ```sh
    # Linux
    export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
    # Windows
    set POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
    ```
    ```sh
    python -m mcp_polaris_ai_datainsight.server
    ```

## Output

- Refer to [this example](examples/example_tool_output.json) for a sample output.
- Alternatively, you can test our API using the [playground](https://datainsight.polarisoffice.com/playground/doc-extract).
