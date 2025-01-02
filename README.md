# Agentic RAG: Gov Support Bot
Building on my experience with a [Naive RAG project](https://github.com/Joanna-Khek/hdb-bto-chatbot), I sought to delve deeper into the concept of Agentic RAG while incorporating advanced RAG features. This project represents the culmination of that exploration.

## Project Description
This project leverages Retrieval-Augmented Generation (RAG) with an agentic workflow to assist users in finding support schemes that truly align with their needs. Unlike the current implementation on the main website, where users are limited to filtering schemes and often receive irrelevant results, this system ensures more personalized and precise recommendations.

![Picture2](https://github.com/user-attachments/assets/081f61e2-fbee-4152-89f5-68983a39b81c)

The key features of the project are:
- **Multi-Query Retrieval**: Mitigates low-quality user queries by leveraging an LLM to generate multiple queries from different perspectives. For each query, a set of relevant documents is retrieved, ensuring a broader and more diverse context pool.
- **Reciprocal Rank Fusion:** Enhances the quality of retrieved documents by ranking them using this advanced fusion method, combining results from multiple queries into a cohesive and high-quality set of documents.
- **Human-in-the-Loop:** Incorporates user feedback dynamically, modifying the graph state to ensure results are continuously improved.
- **Iterative Workflow:** Utilizes an evaluator to determine if the response aligns with user intent. If not, the system refines the output by looping back to earlier stages in the workflow.

This project utilises [Langgraph](https://langchain-ai.github.io/langgraph/), which is a library for building stateful, multi-actor applications with LLMs, used to create agent and multi-agent workflows

![image](https://github.com/user-attachments/assets/4b853f2a-c986-45fa-aa4c-3fe33e27e78b)

## Architecture

![](https://github.com/Joanna-Khek/gov-support-bot/blob/main/assets/graph.png)

- Given the query, the LLM first categorise it into different intents.
- For each intent, a LLM will predict the tags and categories.
- Human-in-the-loop is employed to obtain feedback. Users can modify the predicted tags and predicted categories.
- Based on the query, multi-query retrieval is employed to generate multiple queries.
- For each generated query, we obtain relevant documents from the FAISS vector store.
- Then we rank these documents according to the reciprocal rank fusion methodology.
- We then further filter the documents according to the predicted tags and categories to ensure that only the most relevant documents are returned and used as context.
- An LLM will generate a response based on the context.
- An evaluator LLM will assess whether the response is adequate. If it is, then the workflow will end. If not, the workflow goes back to generating multiple queries, where the remarks given by the evaluator LLM will be ingested so that we can improve on the queries generated.


## Demo
![](https://github.com/Joanna-Khek/gov-support-bot/blob/main/assets/demo.gif)
