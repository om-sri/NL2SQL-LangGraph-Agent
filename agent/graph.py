import sqlite3
from functools import partial
from langgraph.graph import StateGraph, END
from agent.state import AgentState
from agent.nodes import (
    schema_inspector_node,
    sql_writer_node,
    sql_executor_node,
    result_validator_node,
    answer_explainer_node,
    should_retry,
)

# function to arrange the nodes in a graph structure and define the flow of the agent's reasoning process.
# And return graphical sequence of nodes that the agent will execute in order to process the user's question, generate SQL, execute it, validate results, and explain the answer.
def build_graph(conn: sqlite3.Connection):
    graph = StateGraph(AgentState)

    executor = partial(sql_executor_node, conn=conn)

    graph.add_node("schema_inspector", schema_inspector_node)
    graph.add_node("sql_writer", sql_writer_node)
    graph.add_node("sql_executor", executor)
    graph.add_node("result_validator", result_validator_node)
    graph.add_node("answer_explainer", answer_explainer_node)

    graph.set_entry_point("schema_inspector")

    graph.add_edge("schema_inspector", "sql_writer")
    graph.add_edge("sql_writer", "sql_executor")
    graph.add_edge("sql_executor", "result_validator")

    graph.add_conditional_edges(
        "result_validator",
        should_retry,
        {
            "retry": "sql_writer",
            "explain": "answer_explainer",
            "end": END,
        }
    )

    graph.add_edge("answer_explainer", END)

    return graph.compile()

# function to run the agent by providing the user's question, database schema information, and the SQLite connection.
# And returns the final state of the agent after processing the question, which includes the generated SQL query, results, any errors, and the final answer explanation.
def run_agent(question: str, schema_info: str, conn: sqlite3.Connection) -> AgentState:
    app = build_graph(conn)

    initial_state: AgentState = {
        "user_question": question,
        "schema_info": schema_info,
        "sql_query": "",
        "sql_result": None,
        "sql_error": None,
        "validation_status": "",
        "retry_count": 0,
        "final_answer": "",
        "steps_log": [],
    }

    return app.invoke(initial_state)