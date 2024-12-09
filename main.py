import os
import pandas as pd
import streamlit as st

from sql_agent import get_sql_query_from_user_question, \
    get_db_data_with_sql_query
from visualization import get_suggested_visualization_response_from_ai, \
    plot_visualization_for_user_question
from helpers import save_to_sqlite

# Streamlit page config
st.set_page_config(
    page_title="Free Forecaster",
    page_icon="",
    layout="wide"
)

st.title("Forecast at will!")
st.sidebar.title("Upload your Dataset")
uploaded_file = st.sidebar.file_uploader("Upload a CSV file", type=["csv"])
df = pd.read_csv(uploaded_file)
save_to_sqlite(df, "working.db", "working_table")

# Taking open api key as user input
openai_key_input_placeholder = st.empty()
if 'is_open_ai_api_key_set' not in st.session_state:
    openai_key = openai_key_input_placeholder.text_input(
        "OpenAI API Key", type="password")
    if openai_key:
        # Save the input into session state
        st.session_state.is_open_ai_api_key_set = True
        os.environ['OPENAI_API_KEY'] = openai_key
        openai_key_input_placeholder.empty()
    else:
        st.stop()

timegpt_key_input_placeholder = st.empty()
if 'is_time_gpt_api_key_set' not in st.session_state:
    time_gpt_api_key = timegpt_key_input_placeholder.text_input(
        "TimeGPT API Key", type="password")
    if time_gpt_api_key:
        # Save the input into session state
        st.session_state.is_time_gpt_api_key_set = True
        os.environ['TIME_GPT_API_KEY'] = time_gpt_api_key
        timegpt_key_input_placeholder.empty()
    else:
        st.stop()


# Appending Initial message
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = [
        {
            "role": "assistant",
            "content": "How can I help you?"
         }
    ]

# Rendering existing messages
for message in st.session_state.chat_history:
    if 'df_content' in message:
        st.chat_message(message["role"]).dataframe(
            message["df_content"], hide_index=True)
    else:
        st.chat_message(message["role"]).write(message["content"])


# user input question placeholder
user_question = st.chat_input(placeholder="Ask me about your data!")


if user_question:
    st.session_state.chat_history.append(
        {
            "role": "user",
            "content": user_question
        }
    )
    st.chat_message("user").write(user_question)

    #Step 2

    with st.chat_message("assistant"):
        # Get the SQL Query corresponding to user question
        sql_query = get_sql_query_from_user_question(user_question)

    # Step 3

        if sql_query:
            # Get the table data from the SQL Query
            query_output_df = get_db_data_with_sql_query(sql_query)

            # save the query result in session state
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "df_content": query_output_df
                }
            )

            # display the query result
            st.dataframe(query_output_df, hide_index=True)

    # Step 4
            with st.spinner("Looking for a visualization to display the data..."):
                # Get the visualization type & graph parameters passing in the
                # user question & sql query
                visualization_response = get_suggested_visualization_response_from_ai(
                    sql_query, user_question)

    # Step 5
                plot_visualization_for_user_question(
                    visualization_response, query_output_df)
        else:
            print("Cannot Find SQL Query for user query :", user_question)
