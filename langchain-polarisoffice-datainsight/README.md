# langchain-polarisoffice-datainsight

This package contains the LangChain integration with PODataInsight

## Installation

```bash
pip install -U langchain-polarisoffice-datainsight
```

And you should configure credentials by setting the following environment variables:

* TODO: fill this out

## Chat Models

`ChatPODataInsight` class exposes chat models from PODataInsight.

```python
from langchain_polarisoffice_datainsight import ChatPODataInsight

llm = ChatPODataInsight()
llm.invoke("Sing a ballad of LangChain.")
```

## Embeddings

`PODataInsightEmbeddings` class exposes embeddings from PODataInsight.

```python
from langchain_polarisoffice_datainsight import PODataInsightEmbeddings

embeddings = PODataInsightEmbeddings()
embeddings.embed_query("What is the meaning of life?")
```

## LLMs
`PODataInsightLLM` class exposes LLMs from PODataInsight.

```python
from langchain_polarisoffice_datainsight import PODataInsightLLM

llm = PODataInsightLLM()
llm.invoke("The meaning of life is")
```
