# langchain-polaris-ai-datainsight

This package contains the LangChain integration with PODataInsight

## Installation

```bash
pip install -U langchain-polaris-ai-datainsight
```

And you should configure credentials by setting the following environment variables:

```bash
export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
```

## Document Loaders

`PolarisAIDataInsightLoader` class exposes document loader from PODataInsight.

```python
from langchain_community.document_loaders import PolarisAIDataInsightLoader

loader = PolarisAIDataInsightLoader(
    file_path="path/to/file",
    resources_dir="path/to/dir"
)
```