from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from gov_support_bot import nodes, utils

# Intialize the graph builder
graph_builder = StateGraph(nodes.State)

graph_builder.add_node("predict_tags", nodes.predict_tags)
graph_builder.add_node("predict_categories", nodes.predict_categories)
graph_builder.add_node("generate_queries_langchain", nodes.generate_queries_langchain)
graph_builder.add_node("retrieve_relevant_documents", nodes.retrieve_relevant_documents)
graph_builder.add_node("rerank_results", nodes.rerank_results)
graph_builder.add_node("filter_categories", nodes.filter_categories)
graph_builder.add_node("filter_tags", nodes.filter_tags)
graph_builder.add_node("combine_context", nodes.combine_context)
graph_builder.add_node("generate_response", nodes.generate_response)

graph_builder.add_conditional_edges("generate_response", 
                                    nodes.check_relevant_answer,
                                    {END: END, "re-generate": "generate_queries_langchain"})

graph_builder.add_edge(START, "predict_tags")
graph_builder.add_edge("predict_tags", "predict_categories")
graph_builder.add_edge("predict_categories", "generate_queries_langchain")
graph_builder.add_edge("generate_queries_langchain", "retrieve_relevant_documents")
graph_builder.add_edge("retrieve_relevant_documents", "rerank_results")
graph_builder.add_edge("rerank_results", "filter_categories")
graph_builder.add_edge("filter_categories", "filter_tags")
graph_builder.add_edge("filter_tags", "combine_context")
graph_builder.add_edge("combine_context", "generate_response")

# Set up memory
memory = MemorySaver()

# Compile the graph
compiled_graph = graph_builder.compile(checkpointer=memory,
                                       interrupt_after=["predict_tags", "predict_categories"])
