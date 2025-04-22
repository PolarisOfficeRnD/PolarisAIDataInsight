# ![logo](https://raw.githubusercontent.com/PolarisOfficeRnD/PolarisAIDataInsight/main/assets/logo/polarisoffice-logo-small.svg) langchain-polaris-ai-datainsight

This package covers Polaris AI DataInsight integration with LangChain.

Converts documents in various formats—including Word, HWP, Sheets, and Slides—into List of Document.

## Installation and Setup

To use PolarisAIDataInsight model, you need to install a python package:

```bash
pip install -U langchain-polaris-ai-datainsight
```

And you should configure credentials by setting the following environment variables:

```bash
export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
```

Refer to [here](https://datainsight.polarisoffice.com/documentation/quickstart) how to get an Polaris AI DataInsight API key.


## Document Loaders


```python
from langchain_polaris_ai_datainsight import PolarisAIDataInsightLoader

loader = PolarisAIDataInsightLoader(
    file_path="path/to/file",
    resources_dir="path/to/dir"
)
```