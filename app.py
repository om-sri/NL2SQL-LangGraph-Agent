import os
import streamlit as st
from dotenv import load_dotenv
from utils.db import load_csvs_to_sqlite, get_schema_string
from agent.graph import run_agent

load_dotenv()
os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY", "")

st.set_page_config(
    page_title="NL2SQL Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 NL2SQL Agent")
st.caption("Upload CSV files, ask questions in plain English — the agent writes and self-corrects SQL automatically.")

with st.expander("💡 Try with a sample dataset"):
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🚢 Titanic**")
        if st.button("Load Titanic Dataset"):
            import pandas as pd
            import sqlite3
            from utils.db import get_schema_string
            df = pd.read_csv("sample_data/titanic.csv")
            conn = sqlite3.connect(":memory:", check_same_thread=False)
            df.to_sql("titanic", conn, index=False, if_exists="replace")
            st.session_state.conn = conn
            st.session_state.tables = {"titanic": df}
            st.session_state.schema_info = get_schema_string(conn, {"titanic": df})
            st.session_state.history = []
            st.success("✅ Titanic dataset loaded!")
        st.caption("Try asking:")
        st.markdown("- How many passengers survived?")
        st.markdown("- What was the average age by passenger class?")
        st.markdown("- Which gender had a higher survival rate?")

    with col2:
        st.markdown("**🎬 Netflix**")
        if st.button("Load Netflix Dataset"):
            import pandas as pd
            import sqlite3
            from utils.db import get_schema_string
            df = pd.read_csv("sample_data/netflix_titles.csv")
            conn = sqlite3.connect(":memory:", check_same_thread=False)
            df.to_sql("netflix", conn, index=False, if_exists="replace")
            st.session_state.conn = conn
            st.session_state.tables = {"netflix": df}
            st.session_state.schema_info = get_schema_string(conn, {"netflix": df})
            st.session_state.history = []
            st.success("✅ Netflix dataset loaded!")
        st.caption("Try asking:")
        st.markdown("- How many movies vs TV shows are there?")
        st.markdown("- Which country has the most titles?")
        st.markdown("- What are the top 5 most common genres?")

# session state is streamlit's way of storing data across user interactions. Here we initialize the session state variables that will hold the database connection, loaded tables, schema information, and interaction history. 
# This allows the app to maintain state as the user uploads files and interacts with the agent.
if "conn" not in st.session_state:
    st.session_state.conn = None
if "tables" not in st.session_state:
    st.session_state.tables = {}
if "schema_info" not in st.session_state:
    st.session_state.schema_info = ""
if "history" not in st.session_state:
    st.session_state.history = []

# sidebar is to upload CSV files, load them into the in-memory SQLite database, and display the schema and table previews.
with st.sidebar:
    st.header("📂 Upload Data")
    uploaded_files = st.file_uploader(
        "Upload one or more CSV files",
        type=["csv"],
        accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Load Files", type="primary"):
            with st.spinner("Loading CSVs into database..."):
                conn, tables = load_csvs_to_sqlite(uploaded_files)
                schema_info = get_schema_string(conn, tables)
                st.session_state.conn = conn
                st.session_state.tables = tables
                st.session_state.schema_info = schema_info
                st.session_state.history = []
            st.success(f"✅ Loaded {len(tables)} table(s): {', '.join(tables.keys())}")

    if st.session_state.tables:
        st.divider()
        st.subheader("📋 Schema")
        st.code(st.session_state.schema_info, language="text")

        st.divider()
        st.subheader("🗂️ Table Previews")
        for name, df in st.session_state.tables.items():
            with st.expander(f"{name} ({len(df):,} rows)"):
                st.dataframe(df.head(5), use_container_width=True)

# This is chatbot interface where users can ask questions about their data. The agent processes the question, generates SQL, executes it, validates results, and explains the answer. 
# The interaction history is displayed with options to view the generated SQL and raw results for each question.
if not st.session_state.conn:
    st.info("👈 Upload one or more CSV files in the sidebar to get started.")
    st.stop()

for item in st.session_state.history:
    with st.chat_message("user"):
        st.write(item["question"])
    with st.chat_message("assistant"):
        st.write(item["answer"])
        with st.expander("🔍 SQL Query"):
            st.code(item["sql"], language="sql")
        with st.expander("📊 Raw Result"):
            st.text(item["result"])
        with st.expander("🪜 Agent Steps"):
            for step in item["steps"]:
                st.write(step)

question = st.chat_input("Ask a question about your data...")

if question:
    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):
        with st.spinner("Agent is thinking..."):
            result = run_agent(
                question=question,
                schema_info=st.session_state.schema_info,
                conn=st.session_state.conn
            )

        for step in result["steps_log"]:
            st.write(step)

        st.write(result["final_answer"])

        with st.expander("🔍 SQL Query"):
            st.code(result["sql_query"], language="sql")

        if result.get("sql_result"):
            with st.expander("📊 Raw Result"):
                st.text(result["sql_result"])

        st.session_state.history.append({
            "question": question,
            "answer": result["final_answer"],
            "sql": result["sql_query"],
            "result": result.get("sql_result", ""),
            "steps": result["steps_log"],
        })