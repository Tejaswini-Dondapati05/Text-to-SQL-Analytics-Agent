
# 🚀 Text-to-SQL Analytics Agent

### AI-Powered Natural Language to SQL Analytics System

An intelligent AI-powered analytics application that converts natural language questions into SQL queries and provides meaningful business insights.

Built using **Google Gemini, LangGraph, LangChain, FastAPI, Streamlit, and SQLite**, this project enables users to interact with databases using simple English without writing SQL manually.

## ✨ Key Features

- 🤖 **Natural Language to SQL:** Convert English questions into SQL queries.
- 🧠 **AI-Powered SQL Generation:** Generate SQL using Google Gemini.
- 🔄 **Self-Correction:** Automatically fix SQL errors using LLM feedback (up to 3 attempts).
- 🛡️ **SQL Validation:** Restrict queries to read-only SELECT statements.
- ⚡ **Safe Query Execution:** Execute queries using a read-only SQLite connection.
- 📊 **Data Visualization:** Display query results using charts and tables.
- 💡 **AI Business Insights:** Generate easy-to-understand summaries.
- 🌐 **FastAPI Backend:** Provide REST API access.
- 🎨 **Streamlit Interface:** Interactive user-friendly dashboard.

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming |
| Google Gemini | AI-powered SQL generation |
| LangChain | LLM integration |
| LangGraph | Agent workflow orchestration |
| SQLite | Database management |
| FastAPI | Backend API |
| Streamlit | Interactive frontend |
| Pandas | Data processing |
| Matplotlib | Data visualization |

## 🏗️ System Architecture

```text
       User Question
             |
             v
       Get Database Schema
             |
             v
       Generate SQL (Gemini)
             |
             v
       Validate SQL Query
             |
             v
       Execute SQL Query
             |
       +-----+------+
       |            |
     Error        Success
       |            |
       v            v
  Send Error     Summarize
  to Gemini      Results
       |            |
       v            v
  Regenerate     Final Answer
      SQL         + Chart
       |
   Max 3 Attempts
```

## 🔄 Agent Workflow

The LangGraph agent follows these steps:

1. **Get Schema:** Retrieves database tables and columns.
2. **Generate SQL:** Gemini generates SQL based on the user's question.
3. **Validate:** Checks that the generated query follows read-only SQL rules.
4. **Execute:** Runs the query against SQLite.
5. **Self-Correction:** Sends validation or execution errors back to Gemini for correction, up to three attempts.
6. **Summarize:** Generates a business-friendly explanation of the results.
7. **Visualize:** Streamlit displays the results in tables and charts.

## 📁 Project Structure

```text
Text-to-SQL-Analytics-Agent/
│
├── agent.py
├── api.py
├── app.py
├── db.py
├── check_models.py
├── test_gemini.py
├── requirements.txt
├── README.md
├── .gitignore
└── sales.db (generated locally)
```

## ⚙️ Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Tejaswini-Dondapati05/Text-to-SQL-Analytics-Agent.git

cd Text-to-SQL-Analytics-Agent
```

### 2. Create virtual environment

```bash
python -m venv venv
```

Activate it:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API Key

Create a `.env` file in the project folder:

```env
GOOGLE_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
```

Replace the API key with your own valid Google AI Studio API key. Use a model currently available to your API account.

### 5. Initialize the database

```bash
python db.py
```

### 6. Run the FastAPI backend

```bash
uvicorn api:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

### 7. Run the Streamlit application

Open another terminal and activate the virtual environment.

```bash
streamlit run app.py
```

Open:

http://localhost:8501

## 💬 Sample Questions

Try asking these questions:

- Which 5 products have the highest revenue?
- Show total revenue by category.
- How many orders were placed each month in 2025?
- Which city has the most customers?
- What percentage of orders were cancelled?
- Who are the top 3 customers by total spending?
- Which category sells the most in Hyderabad?

## 🔐 Security Features

- Only read-only SQL queries are permitted.
- Multiple SQL statements are rejected.
- Dangerous SQL keywords are blocked.
- Database queries execute using a read-only connection.
- SQL validation and execution errors are used for self-correction.

**Note:** This is a demonstration-level SQL safety layer, not a complete production SQL security system.

## 🎯 Project Objective

The main objective is to simplify business data analysis by allowing users to interact with databases using natural language.

This project demonstrates practical applications of Generative AI, LLM-based agents, database automation, API development, and data visualization.

## 👩‍💻 Author

**Tejaswini Dondapati**

GitHub: [Tejaswini-Dondapati05](https://github.com/Tejaswini-Dondapati05)

## ⭐ Support

If you find this project useful, consider giving it a ⭐ on GitHub!
