from typing import TypedDict, Optional


class AgentState(TypedDict):
    user_question: str
    schema_info: str
    sql_query: str
    sql_result: Optional[str]
    sql_error: Optional[str]
    validation_status: str
    retry_count: int
    final_answer: str
    steps_log: list[str]