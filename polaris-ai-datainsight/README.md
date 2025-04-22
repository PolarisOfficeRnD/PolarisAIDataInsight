# ![logo](https://raw.githubusercontent.com/PolarisOfficeRnD/PolarisAIDataInsight/main/assets/logo/polarisoffice-logo-small.svg) polaris-ai-datainsight

This package is Python SDK for Polaris AI DataInsight.

Converts documents in various formats—including Word, HWP, Sheets, and Slides—into structured JSON data.

## Installation and Setup

You need to install a python package:

```bash
pip install -U polaris-ai-datainsight
```

And you should configure credentials by setting the following environment variables:

```bash
export POLARIS_AI_DATA_INSIGHT_API_KEY="your-api-key"
```

Refer to [here](https://datainsight.polarisoffice.com/documentation/quickstart) how to get an Polaris AI DataInsight API key.


## Document Extractor

Set the file path to extract and the directory path to store resource files included in the file:

```python
from polaris_ai_datainsight import PolarisAIDataInsightExtractor

loader = PolarisAIDataInsightExtractor(
    file_path="path/to/file",
    resources_dir="path/to/dir"
)
```

Extract document data:

```python
dict_data = loader.extract()
```