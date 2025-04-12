from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.preprocessors import DocumentSplitter
from haystack.components.writers import DocumentWriter
from haystack.components.generators.openai import OpenAIGenerator
from haystack.components.embedders.openai_text_embedder import OpenAITextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack.components.converters import PyPDFToDocument
from haystack.utils import Secret
from haystack.dataclasses import ChatMessage
from haystack.components.builders import AnswerBuilder,ChatPromptBuilder
from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

AzureOpenAIKey = Secret.from_env_var("HAYSTACK_API_KEY")
AzureOpenAIUrl = Secret.from_env_var("HAYSTACK_API_BASE_URL").resolve_value()
EmbeddingOpenAPIURL = Secret.from_env_var("HAYSTACK_API_EMBEDDINGS_URL").resolve_value()
EmbeddingOpenAPIKey = Secret.from_env_var("OPEN_AI_EMBEDDINGS_MODEL_KEY")
EmbeddingModelName = Secret.from_env_var("EMBEDDING_MODEL_NAME").resolve_value()

def analyze_report(filePath: str) -> str:
    # 1. Init components
    converter = PyPDFToDocument()
    splitter = DocumentSplitter(split_by="sentence", split_length=5)
    splitter.warm_up()
    doc_store = InMemoryDocumentStore()
    writer = DocumentWriter(document_store=doc_store)

    embedder = OpenAITextEmbedder(
        api_key=AzureOpenAIKey,
        api_base_url=AzureOpenAIUrl,
        model=EmbeddingModelName
    )

    retriever = InMemoryEmbeddingRetriever(document_store=doc_store)
    prompt_builder = PromptBuilder(template="What's the total price of the purchase order:\n{documents}")
    generator = OpenAIGenerator(
        api_key=AzureOpenAIKey,
        api_base_url=AzureOpenAIUrl,
        model="gpt-4o"  # or your deployed model on Azure
    )

    # Step 1: Convert and split PDF
    path = Path(filePath)
    assert path.exists(), f"File {path} does not exist."
    print(path)
    docs = converter.run(sources=[filePath])["documents"]
    split_docs = splitter.run({"documents": docs})["documents"]
    writer.run({"documents": split_docs})


    # Step 2: Embed documents and write to store
    doc_embeddings = embedder.run({"text": [doc.content for doc in split_docs]})
    for i, embedding in enumerate(doc_embeddings["embedding"]):
        split_docs[i].embedding = embedding
    doc_store.write_documents(split_docs, policy="overwrite")
    
    # Step 3: Embed the query
    query = "What's the total price of the purchase order?"
    query_embedding = embedder.run({"text": [query]})["embedding"][0]

    # Step 4: Retrieve and generate
    retrieved_docs = retriever.run({"query_embedding": query_embedding})["documents"]
    prompt = prompt_builder.run({"documents": retrieved_docs, "query": query})["prompt"]
    response = generator.run({"prompt": prompt})["replies"][0]

    return response
