# 1.For multi query retrieval
QUERY_TRANSFORM_PROMPT = """You are a helpful assistant that generates multiple search \
queries based on a single input query. The query might have multiple intents. \
    
Use the following predicted categories and tags to help with generating the queries: \
Predicted Categories: {predicted_categories} \
Predicted Tags: {predicted_tags} \
    
Use the following remarks, if any, to help with the generation of multi-query retrieval: {remarks} \

For each intent, the generated queries must be as close to the original query as possible.\
Return the answer as a dictionary, which each intent as a key and the corresponding multiple search queries as the value. \

Query: {query}
Generate 5 search queries for each intent in the query.
"""


# 2. For prediction of tags
TAGS_PROMPT = """You are a helpful assistant. 
Classify this query {query} into the appropriate tags from this list: {tags_list}. Return results as a list."""


# 3. For prediction of categories
CATEGORIES_PROMPT = """You are a helpful assistant. Classify this query {query} 
into the appropriate categories from this list: {categories_list}. Return results as a list."""


# 4. For response generation
RESPONSE_PROMPT = """You are a helpful and friendly assistant for question-answering tasks.

You are given the following context information as dictionary. The keys of the dictionary represents
the different intent of the query.
Context: {context}

Answer the following question from the user.
Use only information from the previous context information. Do not invent stuff.
If you don't know the answer, say that you don't know.

In your answer, tell the user the different intents based on the query.
For each intent, provide all relevant schemes.

For each scheme, format the answer as follows:
1. Bold the name of the scheme
2. Provide a link to the scheme. Provide the full URL. Do not put it as "Metadata Link".
3. Provide a brief description of the scheme
4. Provide information on who is eligible for the scheme
5. Provide information on how to apply for the scheme

Question: {query}

Answer:"""


# 5. For checking if response is relevant
RELEVANT_ANSWER_PROMPT = """You are a helpful assistant that assesses the relevance of the answer to the query.
Given this query: {query}, and this context: {context}, where each key is an intent of the query, answer the following question.

Does the response: {generated_response} address all the intents in the query?

Please respond strictly in the following JSON format:
{{
    "relevance": "Yes/No. Yes if there are schemes that address all the intents in the query. No otherwise."
    "remarks": "Provide suggestion on how to improve the multi-query retrieval generation for related queries."
}}
"""