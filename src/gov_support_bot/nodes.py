import json
from typing import Dict
import ast
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from typing import TypedDict
from langgraph.graph import END
from langchain_core.output_parsers import JsonOutputParser
from pydantic.v1 import BaseModel, Field
from langchain.load import dumps, loads
from gov_support_bot import utils, prompts


# Initialise LLM
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
retriever = utils.load_vector_store("faiss_index")


# Initialise the state graph
class State(TypedDict):
    query: str
    multiple_queries: Dict[str, list]
    relevant_documents: Dict[str, list]
    tags_list: list
    categories_list: list
    predicted_tags: list
    predicted_categories: list
    rank_results: Dict[str, list]
    filtered_docs: Dict[str, list]
    context: Dict[str, list]
    answer: str
    generate_count: int
    max_generate_count: int
    remarks: str


def generate_queries_langchain(state: State):
    prompt = PromptTemplate(
        template=prompts.QUERY_TRANSFORM_PROMPT, input_variables=["query"]
    )

    generate_queries_chain = prompt | llm

    generated_queries_dict = generate_queries_chain.invoke(
        {
            "query": state["query"],
            "predicted_tags": state["predicted_tags"],
            "predicted_categories": state["predicted_categories"],
            "remarks": state["remarks"],
        }
    )

    # Extract and process the content
    generated_queries_dict = json.loads(generated_queries_dict.content)

    return {
        "multiple_queries": generated_queries_dict,
        "generate_count": state.get("generate_count", 0) + 1,
    }


def predict_tags(state: State):
    prompt = PromptTemplate(
        template=prompts.TAGS_PROMPT, input_variables=["query", "tags_list"]
    )

    pred_tag_chain = prompt | llm

    pred_tag = pred_tag_chain.invoke(
        {"query": state["query"], "tags_list": state["tags_list"]}
    )
    # Extract and clean the content
    raw_tags = pred_tag.content.strip()  # Remove unnecessary spaces
    flat_string = "".join(raw_tags)  # Join into a single string
    predicted_tags = ast.literal_eval(flat_string)  # Convert to Python list

    return {"predicted_tags": predicted_tags}


def predict_categories(state: State):
    prompt = PromptTemplate(
        template=prompts.CATEGORIES_PROMPT, input_variables=["query", "categories_list"]
    )
    pred_cat_chain = prompt | llm

    pred_cat = pred_cat_chain.invoke(
        {"query": state["query"], "categories_list": state["categories_list"]}
    )
    # Extract and clean the content
    raw_categories = pred_cat.content.strip()  # Remove unnecessary spaces
    flat_string = "".join(raw_categories)  # Join into a single string
    predicted_categories = ast.literal_eval(flat_string)  # Convert to Python list

    return {"predicted_categories": predicted_categories}


def retrieve_relevant_documents(state: State):
    overall_results = {}

    for intent, multiple_queries in state["multiple_queries"].items():
        sub_query_results = []
        for query in multiple_queries:
            sub_query_results.append(retriever.invoke(query))
        overall_results[intent] = sub_query_results
    return {"relevant_documents": overall_results}


def rerank_results(state: State):
    intent_fused_scores = {}

    for intent, intent_docs in state["relevant_documents"].items():
        fused_scores = {}
        for docs in intent_docs:
            # Assumes the docs are returned in sorted order of relevance
            for rank, doc in enumerate(docs):
                doc_str = dumps(doc)
                if doc_str not in fused_scores:
                    fused_scores[doc_str] = 0
                fused_scores[doc_str] += 1 / (rank + 60)

        reranked_results = [
            loads(doc)
            for doc, score in sorted(
                fused_scores.items(), key=lambda x: x[1], reverse=True
            )
        ]

        # Take top 5 results
        intent_fused_scores[intent] = reranked_results[:5]

    return {"rank_results": intent_fused_scores}


def filter_categories(state: State):
    results = {}

    for intent, cat_docs in state["rank_results"].items():
        results[intent] = utils.filter_documents_by_category(
            cat_docs, state["predicted_categories"]
        )

    return {"filtered_docs": results}


def filter_tags(state: State):
    results = {}
    for intent, tag_docs in state["filtered_docs"].items():
        results[intent] = utils.filter_documents_by_tag(
            tag_docs, state["predicted_tags"]
        )

    return {"filtered_docs": results}


def combine_context(state: State):
    combined_dict = {}
    for intent, docs in state["filtered_docs"].items():
        combined = [
            f"Content: {doc.page_content}\nMetadata: {doc.metadata["link"]}"
            for doc in docs
        ]
        # context = "\n\n".join(combined)
        combined_dict[intent] = combined

    return {"context": combined_dict}


def generate_response(state: State):
    llm_prompt = PromptTemplate(
        template=prompts.RESPONSE_PROMPT, input_variables=["context", "query"]
    )

    generate_response_chain = llm_prompt | llm

    response = generate_response_chain.invoke(
        {"query": state["query"], "context": state["context"]}
    )

    return {"answer": response.content}


def check_relevant_answer(state: State):
    # Define your desired data structure.
    class Evaluator(BaseModel):
        relevance: str = Field(description="Is this response relevant to the query")
        remarks: str = Field(description="Remarks on how to improve the response")

    # Set up a parser + inject instructions into the prompt template.
    parser = JsonOutputParser(pydantic_object=Evaluator)

    # Checks if generate answer is relevant to the user query
    prompt = PromptTemplate(
        template=prompts.RELEVANT_ANSWER_PROMPT,
        input_variables=["query", "generated_response", "context"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    check_relevance_chain = prompt | llm | parser

    response = check_relevance_chain.invoke(
        {
            "query": state["query"],
            "generated_response": state["answer"],
            "context": state["context"],
        }
    )

    if (response["relevance"] == "No") and (
        state["generate_count"] < state["max_generate_count"]
    ):
        state["remarks"] = response["remarks"]
        return "regenerate"
    else:
        return END
