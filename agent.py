
"""
LangGraph SQL Agent:
get_schema -> generate_sql -> validate -> execute -> summarize

If validation or SQL execution fails, retry SQL generation
with the previous error, up to MAX_ATTEMPTS.
"""

import os
import re
from pathlib import Path
from typing import Any, List, TypedDict

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from db import get_schema, init_db, run_query


# --------------------------------------------------
# 1. ENVIRONMENT CONFIGURATION
# --------------------------------------------------

env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)

API_KEY = os.getenv("GOOGLE_API_KEY")
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()
if not API_KEY:
    raise ValueError(
        "GOOGLE_API_KEY is missing. Check your project .env file."
    )

print("Gemini API key loaded:", bool(API_KEY))
print("Gemini model:", MODEL_NAME)

MAX_ATTEMPTS = 3

FORBIDDEN = [
    "insert", "update", "delete", "drop", "alter",
    "create", "replace", "truncate", "attach",
    "detach", "pragma", "vacuum"
]


# --------------------------------------------------
# 2. AGENT STATE
# --------------------------------------------------

class AgentState(TypedDict, total=False):
    question: str
    schema: str
    sql: str
    error: str
    columns: List[str]
    rows: List[List[Any]]
    attempts: int
    summary: str


# --------------------------------------------------
# 3. GEMINI INITIALIZATION
# --------------------------------------------------

_llm = None

def get_llm():
    global _llm

    if _llm is None:
        _llm = ChatGoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=API_KEY,
            temperature=0,
            max_retries=2,
            timeout=30,
        )

    return _llm


def call_llm(prompt: str) -> str:
    """Call Gemini and return plain text."""

    try:
        response = get_llm().invoke(prompt)
        return text_of(response)

    except Exception as e:
        raise RuntimeError(
            f"Gemini API request failed.\n"
            f"Model: {MODEL_NAME}\n"
            f"Details: {type(e).__name__}: {e}\n\n"
            "Check your API key, model availability, "
            "internet connection and API quota."
        ) from e


# --------------------------------------------------
# 4. RESPONSE CLEANING
# --------------------------------------------------

def text_of(response) -> str:
    content = response.content

    if isinstance(content, list):
        parts = []

        for p in content:
            if isinstance(p, dict):
                parts.append(p.get("text", ""))
            else:
                parts.append(str(p))

        return "".join(parts)

    return str(content)


def clean_sql(text: str) -> str:
    text = re.sub(
        r"```(?:sql)?",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = text.replace("```", "")

    return text.strip().rstrip(";").strip()


# --------------------------------------------------
# 5. SQL VALIDATION
# --------------------------------------------------

def validate_sql(sql: str) -> str:

    if not sql:
        return "The SQL query is empty."

    # Allow only one SQL statement.
    if ";" in sql:
        return "Only one SQL statement is allowed."

    # Allow SELECT and WITH queries only.
    if not re.match(
        r"^(select|with)\b",
        sql.strip(),
        flags=re.IGNORECASE
    ):
        return "Only SELECT queries are allowed."

    # Reject forbidden SQL keywords.
    for word in FORBIDDEN:
        if re.search(
            rf"\b{word}\b",
            sql,
            flags=re.IGNORECASE
        ):
            return (
                f"Forbidden keyword found: {word.upper()}. "
                "Only read-only queries are allowed."
            )

    return ""


# --------------------------------------------------
# 6. LANGGRAPH NODES
# --------------------------------------------------

def get_schema_node(state: AgentState) -> AgentState:

    print("\n[1] Fetching database schema...")

    return {
        "schema": get_schema(),
        "attempts": 0,
        "error": "",
        "sql": "",
        "rows": [],
        "columns": [],
        "summary": "",
    }


def generate_sql_node(state: AgentState) -> AgentState:

    attempt = state.get("attempts", 0) + 1

    print(f"\n[2] Generating SQL (Attempt {attempt}/{MAX_ATTEMPTS})...")

    prompt = (
        "You are an expert SQLite database analyst.\n"
        "Generate ONE SQLite SELECT query to answer the question.\n"
        "Use only tables and columns present in the schema.\n"
        "Return ONLY SQL without markdown or explanations.\n\n"

        "Business rules:\n"
        "Revenue = order_items.quantity * products.price.\n"
        "Unless the user specifies otherwise, exclude orders "
        "with status 'Cancelled' or 'Returned' "
        "when calculating revenue or sales.\n\n"

        "SQL safety:\n"
        "Only read-only SELECT queries are permitted.\n\n"

        f"SCHEMA:\n{state['schema']}\n\n"
        f"QUESTION:\n{state['question']}\n"
    )

    # Send previous error to Gemini for self-correction.
    if state.get("error"):

        prompt += (
            "\nYour previous SQL query failed.\n"
            f"Previous SQL: {state.get('sql', '')}\n"
            f"Error: {state['error']}\n\n"
            "Correct the SQL query based on this error.\n"
            "Return ONLY the corrected SQL.\n"
        )

    sql = clean_sql(call_llm(prompt))

    print("Generated SQL:", sql)

    return {
        "sql": sql,
        "attempts": attempt,
        "error": "",
    }


def validate_node(state: AgentState) -> AgentState:

    print("\n[3] Validating SQL...")

    error = validate_sql(state["sql"])

    if error:
        print("Validation failed:", error)
    else:
        print("SQL validation successful.")

    return {"error": error}


def execute_node(state: AgentState) -> AgentState:

    print("\n[4] Executing SQL...")

    try:
        columns, rows = run_query(state["sql"])

        print(f"Execution successful. Rows returned: {len(rows)}")

        return {
            "columns": columns,
            "rows": rows,
            "error": "",
        }

    except Exception as e:

        error = f"SQL execution error: {type(e).__name__}: {e}"

        print(error)

        return {
            "error": error,
            "columns": [],
            "rows": [],
        }


def summarize_node(state: AgentState) -> AgentState:

    print("\n[5] Summarizing results...")

    if not state.get("rows"):
        return {
            "summary": "No matching records were found."
        }

    preview = state["rows"][:20]

    prompt = (
        "Explain the following SQL query results to a "
        "non-technical business user in 2 or 3 short sentences.\n"
        "Use only the numbers shown. Do not invent information.\n\n"

        f"Question: {state['question']}\n"
        f"Columns: {state['columns']}\n"
        f"Rows: {preview}\n"
    )

    summary = call_llm(prompt).strip()

    return {"summary": summary}


# --------------------------------------------------
# 7. GRAPH ROUTING
# --------------------------------------------------

def route_after_validate(state: AgentState) -> str:

    if state.get("error"):

        if state.get("attempts", 0) < MAX_ATTEMPTS:
            return "retry"

        return "give_up"

    return "execute"


def route_after_execute(state: AgentState) -> str:

    if state.get("error"):

        if state.get("attempts", 0) < MAX_ATTEMPTS:
            return "retry"

        return "give_up"

    return "summarize"


# --------------------------------------------------
# 8. BUILD LANGGRAPH
# --------------------------------------------------

def build_graph():

    g = StateGraph(AgentState)

    g.add_node("get_schema", get_schema_node)
    g.add_node("generate_sql", generate_sql_node)
    g.add_node("validate", validate_node)
    g.add_node("execute", execute_node)
    g.add_node("summarize", summarize_node)

    g.set_entry_point("get_schema")

    g.add_edge("get_schema", "generate_sql")
    g.add_edge("generate_sql", "validate")

    g.add_conditional_edges(
        "validate",
        route_after_validate,
        {
            "retry": "generate_sql",
            "give_up": END,
            "execute": "execute",
        }
    )

    g.add_conditional_edges(
        "execute",
        route_after_execute,
        {
            "retry": "generate_sql",
            "give_up": END,
            "summarize": "summarize",
        }
    )

    g.add_edge("summarize", END)

    return g.compile()


# --------------------------------------------------
# 9. MAIN FUNCTION
# --------------------------------------------------

_graph = None


def ask_question(question: str) -> dict:

    global _graph

    if not question or not question.strip():
        raise ValueError("Please enter a valid question.")

    init_db()

    if _graph is None:
        _graph = build_graph()

    print("\n" + "=" * 55)
    print("QUESTION:", question)
    print("=" * 55)

    try:
        result = _graph.invoke({
            "question": question.strip()
        })

        return {
            "question": question,
            "sql": result.get("sql", ""),
            "columns": result.get("columns", []),
            "rows": result.get("rows", []),
            "summary": result.get("summary", ""),
            "error": result.get("error", ""),
            "attempts": result.get("attempts", 0),
        }

    except Exception as e:

        print("\nAGENT ERROR:", e)

        return {
            "question": question,
            "sql": "",
            "columns": [],
            "rows": [],
            "summary": "",
            "error": str(e),
            "attempts": 0,
        }


# --------------------------------------------------
# 10. RUN AGENT
# --------------------------------------------------

if __name__ == "__main__":

    out = ask_question(
        "Which 5 products have the highest revenue?"
    )

    print("\n" + "=" * 55)
    print("FINAL RESULT")
    print("=" * 55)

    print("\nSQL:")
    print(out["sql"])

    print("\nCOLUMNS:")
    print(out["columns"])

    print("\nROWS:")

    for row in out["rows"]:
        print(row)

    print("\nSUMMARY:")
    print(out["summary"])

    if out["error"]:
        print("\nERROR:")
        print(out["error"])

    print("\nATTEMPTS:")
    print(out["attempts"])
