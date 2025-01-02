import ast
import pandas as pd
from typing import List
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders.csv_loader import CSVLoader


def load_data(filepath: str) -> pd.DataFrame:
    loader = CSVLoader(
        file_path=filepath,
        encoding="utf-8",
        metadata_columns=["tags", "link", "category"],
    )
    data = loader.load()
    return data
    
def load_vector_store(name: str, k: int = 10):
    # Initialize embeddings (e.g., OpenAI embeddings)
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")

    # Load in Vector Store
    vector_store = FAISS.load_local(
        name, embeddings, allow_dangerous_deserialization=True
    )
    
    # Define Retriever
    retriever = vector_store.as_retriever(search_type="mmr", ## Maximum Marginal Relevance (MMR) for search
                                        search_kwargs={"k": k})
    
    return retriever

def get_all_tags(data: List) -> List:
    """Obtain all unique tags

    Args:
        data (List): Langchain Document List

    Returns:
        List: List of unique tags
    """
    unqiue_tags = set()
    for d in data:
        for tag in ast.literal_eval(d.metadata["tags"]):
            unqiue_tags.add(tag)
    return list(unqiue_tags)


def get_all_categories(data: List) -> List:
    """Obtain all unique categories

    Args:
        data (List): Langchain Document List

    Returns:
        List: List of unique tags
    """
    unique_categories = set()
    for d in data:
        for cat in ast.literal_eval(d.metadata["category"]):
            unique_categories.add(cat)
    return list(unique_categories)


def filter_documents_by_tag(documents: list, target_tags: list) -> List:
    """
    Filters a list of documents based on whether any of the target tags are present in the document's tags.

    Parameters:
        documents (list): List of Document objects.
        target_tags (list): List of target tags to filter by.

    Returns:
        List: Filtered list of Document objects.
    """
    filtered_docs = [
        doc
        for doc in documents
        if any(tag in doc.metadata.get("tags", []) for tag in target_tags)
    ]
    return filtered_docs

def filter_documents_by_category(raw_results: list, category_tags: list) -> List:
    """
    Filters a list of documents on whether any of the category tags are present in the document's categories

    Args:
        raw_results (list): List of initial filtered Document objects
        category_tags (list): List of category tags to filter by

    Returns:
        List: Filtered list of Document objects.
    """
    filtered_docs = [
        doc
        for doc in raw_results
        if any(cat in doc.metadata.get("category", []) for cat in category_tags)
    ]
    return filtered_docs