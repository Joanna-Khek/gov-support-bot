import streamlit as st
import time
from gov_support_bot import utils, graph

st.title("Schemes Finder")

with st.expander(":orange[Information]", expanded=True):
    st.write("""
             Gov Support Bot is a tool that helps you find relevant government support schemes.
             Input a query and the bot will return the relevant support schemes.
             The support schemes are taken from https://supportgowhere.life.gov.sg/schemes
             """)

with st.sidebar:
    st.image("../../assets/logo.png", width=200)


def stream_response(response):
    for word in response.split():
        yield word + " "
        time.sleep(0.05)


def update_state_values(thread, update_key, values):
    current_values = graph.compiled_graph.get_state(thread)
    current_values.values[update_key] = values
    graph.compiled_graph.update_state(thread, current_values.values)


@st.fragment
def human_feedback_tags(data, thread):
    with st.container(border=True):
        st.subheader("Predicted Tags")
        selected_tags = st.pills(
            "Predicted Tags",
            options=utils.get_all_tags(data),
            key="selected_tags",
            selection_mode="multi",
            default=st.session_state.graph_results["predicted_tags"],
        )

        if st.button("Update", key="tags_update"):
            st.session_state.tags_updated = selected_tags
            st.session_state.predict_tags = True
            update_state_values(thread, "predicted_tags", selected_tags)
            st.rerun()


@st.fragment
def human_feedback_categories(data, thread):
    with st.container(border=True):
        st.subheader("Predicted Categories")
        selected_categories = st.pills(
            "Predicted Categories",
            options=utils.get_all_categories(data),
            selection_mode="multi",
            key="selected_categories",
            default=st.session_state.graph_results["predicted_categories"],
        )

        if st.button("Update", key="categories_update"):
            st.session_state.categories_updated = selected_categories
            st.session_state.predict_categories = True
            update_state_values(thread, "predicted_categories", selected_categories)
            st.rerun()


def main_conversation_ui(data, thread):
    if "predict_tags" not in st.session_state:
        st.session_state.predict_tags = False

    if "predict_categories" not in st.session_state:
        st.session_state.predict_categories = False

    if "graph_results" not in st.session_state:
        st.session_state.graph_results = False

    if "tags_updated" not in st.session_state:
        st.session_state.tags_updated = None

    if "categories_updated" not in st.session_state:
        st.session_state.categories_updated = None

    if "query" not in st.session_state:
        st.session_state.query = None

    query = st.text_area("Ask me anything...", key="query")

    # 1. Predict Tags
    if not st.session_state.predict_tags:
        if st.button("Submit") and query != "":
            initial_state = {
                "query": query,
                "tags_list": utils.get_all_tags(data),
                "categories_list": utils.get_all_categories(data),
                "max_generate_count": 3,
                "remarks": "None",
            }

            st.write_stream(
                stream_response(
                    "Based on your query, these are the predicted tags. Please update the tags if needed."
                )
            )
            with st.spinner("Predicting tags..."):
                result = graph.compiled_graph.invoke(initial_state, config=thread)
                st.session_state.graph_results = result
                human_feedback_tags(data, thread)

    # 2. Predict Categories
    if (not st.session_state.predict_categories) and st.session_state.predict_tags:
        st.write_stream(
            stream_response(
                "Based on your query, these are the predicted categories. Please update the categories if needed."
            )
        )
        with st.spinner("Predicting categories..."):
            result = graph.compiled_graph.invoke(None, config=thread)
            st.session_state.graph_results = result
            human_feedback_categories(data, thread)

    # 3. Generate Response
    if st.session_state.predict_tags and st.session_state.predict_categories:
        with st.spinner("Searching for schemes..."):
            result = graph.compiled_graph.invoke(None, config=thread)
            st.session_state.graph_results = result

            with st.container(border=True):
                st.markdown(result["answer"])


def initialise_setup():
    thread = {"configurable": {"thread_id": "1"}}
    data = utils.load_data("../../data/data.csv")
    return thread, data


def run():
    ready = True

    with st.sidebar:
        openai_api_key = st.text_input(
            "OpenAI API Key", key="chatbot_api_key", type="password"
        )

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        ready = False

    if ready:
        with st.sidebar:
            st.success("API Authenticated!")
        thread, data = initialise_setup()
        main_conversation_ui(data, thread)
    else:
        st.stop()


if __name__ == "__main__":
    run()
