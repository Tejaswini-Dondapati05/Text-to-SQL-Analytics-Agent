# Text-to-SQL Analytics Agent

An agentic AI app that turns plain-English business questions into SQL, validates the query,
fixes its own errors, and returns the result with a chart and a plain-language summary.

**Tech stack:** Python, LangChain, LangGraph, Gemini (LLM), SQLite, FastAPI, Streamlit, Pandas, Matplotlib

## How it works

```
Question -> get_schema -> generate_sql -> validate -> execute -> summarize -> answer
                              ^              |           |
                              |__ error feedback (max 3 tries) __|
```

1. **get_schema** reads table and column names from the database.
2. **generate_sql** sends the schema + question to Gemini and gets a SQL query.
3. **validate** allows only a single read-only SELECT query (blocks DROP, DELETE, UPDATE, etc.).
4. **execute** runs the query on a read-only database connection.
5. If validation or execution fails, the error is sent back to the LLM to correct the SQL (self-correction loop, 3 attempts).
6. **summarize** asks the LLM to explain the result in 2-3 sentences.
7. Streamlit shows the SQL, summary, table and a chart.

## Setup (step by step)

1. Install Python 3.10 or newer.
2. Open a terminal in this folder and create a virtual environment:
   - Windows: `python -m venv venv` then `venv\Scripts\activate`
   - Mac/Linux: `python3 -m venv venv` then `source venv/bin/activate`
3. Install packages: `pip install -r requirements.txt`
4. Get a free Gemini API key from Google AI Studio.
5. Copy `.env.example` to `.env` and paste your key after `GOOGLE_API_KEY=`.
6. Create the sample database: `python db.py` (creates `sales.db` and prints the schema).
7. Test the agent without the UI: `python agent.py`
8. Start the API (terminal 1): `uvicorn api:app --reload`
9. Start the UI (terminal 2, same folder, venv active): `streamlit run app.py`
10. Open the link Streamlit shows (usually http://localhost:8501) and ask questions.

## Sample questions to try

- Which 5 products have the highest revenue?
- Show total revenue by category
- How many orders were placed each month in 2025?
- Which city has the most customers?
- What percentage of orders were cancelled?
- Who are the top 3 customers by total spending?
- Which category sells the most in Hyderabad?

Also try: "Delete all orders" (it should be blocked) to show the safety check.

## Files

| File | Purpose |
|---|---|
| `db.py` | Creates the sample database, reads the schema, runs read-only queries |
| `agent.py` | LangGraph workflow (nodes, routing, self-correction loop) |
| `api.py` | FastAPI backend with `POST /ask` |
| `app.py` | Streamlit user interface |

## Use your own data

Replace the tables in `db.py` (or point `DB_PATH` to your own SQLite file). The agent reads
the schema automatically, so no other change is needed. If you load a CSV with Pandas, use
`df.to_sql("table_name", connection)`.

## Common problems

- **Model not found / 404:** change `GEMINI_MODEL` in `.env` to a current model name from Google AI Studio.
- **Could not reach the API:** the FastAPI server (step 8) must be running first.
- **503 or rate-limit error from Gemini:** wait a few seconds and try again.
