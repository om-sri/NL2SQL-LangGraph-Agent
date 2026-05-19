# NL2SQL LangGraph Agent

An agentic Text-to-SQL system built with LangGraph and LangChain. Upload any CSV dataset and ask questions in plain English - the agent autonomously plans, writes, executes, and self-corrects SQL queries using LLM reasoning. No SQL knowledge required.

🚀 **Live Demo**: https://nl2sql-langgraph-agent.streamlit.app/

---

## What It Does

Most data tools require you to know SQL. This agent removes that barrier entirely. You upload a CSV (or multiple CSVs), ask a question like *"Which country has the most Netflix titles?"* and the agent:

1. Inspects your data schema automatically
2. Writes a SQL query based on your question
3. Executes it against an in-memory SQLite database
4. Validates whether the result actually answers your question
5. Self-corrects and retries if something went wrong
6. Returns a clean natural language answer with the SQL and raw result visible

---

## LangGraph Architecture

The agent is built as a stateful graph with 5 nodes and a self-correction cycle:

```
Schema Inspector → SQL Writer → SQL Executor → Result Validator → Answer Explainer
                                                      ↑                    |
                                                      └───── retry loop ───┘
                                                        (up to 3 attempts)
```

- **Schema Inspector** - reads uploaded tables, extracts column names, types, and sample values
- **SQL Writer** - uses LLM to write SQLite SQL based on the question and schema
- **SQL Executor** - runs the query against the in-memory database
- **Result Validator** - checks if the result is correct and meaningful; routes back to SQL Writer on failure
- **Answer Explainer** - translates raw query results into a plain English insight

The retry loop is the key feature - if the SQL errors or returns a wrong result, the agent injects the error back into the prompt and rewrites the query automatically.

---

## Features

- Upload single or multiple CSV files (multi-table join support)
- One-click sample datasets built into the UI (Titanic, Netflix)
- Self-correcting agent - retries up to 3 times on failure
- Live agent step visibility - see every node execute in real time
- Displays generated SQL and raw results alongside the answer
- Works on any tabular CSV dataset

---

## Tech Stack

| Category | Tools |
|---|---|
| Agent Framework | LangGraph, LangChain |
| LLM | OpenRouter API |
| Frontend | Streamlit |
| Database | SQLite (in-memory) |
| Data Processing | Pandas |
| Language | Python 3.11 |

---

## Run Locally

```bash
git clone https://github.com/om-sri/NL2SQL-LangGraph-Agent.git
cd NL2SQL-LangGraph-Agent
pip install -r requirements.txt
streamlit run app.py
```

Create a `.env` file in the root folder:

```
OPENROUTER_API_KEY=your_key_here
```

Get a free API key at [openrouter.ai](https://openrouter.ai)

<img width="1919" height="904" alt="image" src="https://github.com/user-attachments/assets/ed2d1a3e-7504-4108-bc6e-57ce53746518" />
<img width="1914" height="909" alt="image" src="https://github.com/user-attachments/assets/d5b00f10-0db7-4837-a641-b4ca02f4470a" />
<img width="1913" height="909" alt="image" src="https://github.com/user-attachments/assets/7ba7b19d-3430-4883-af78-ef8fc2ee9cc6" />

