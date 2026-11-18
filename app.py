
import streamlit as st
from agent import ask_question

st.set_page_config(
    page_title="AI SQL Agent",
    page_icon="🤖"
)

st.title("🤖 AI SQL Analytics Agent")
st.write("Ask questions about your database using natural language.")

question = st.text_input(
    "Enter your question",
    placeholder="Which 5 products have the highest revenue?"
)

if st.button("Submit"):
    if question.strip():
        try:
            with st.spinner("AI Agent is processing your question..."):
                result = ask_question(question.strip())

            st.subheader("Generated SQL")
            st.code(result.get("sql", ""), language="sql")

            st.subheader("Query Results")
            columns = result.get("columns", [])
            rows = result.get("rows", [])

            if columns and rows:
                st.dataframe(
                    [dict(zip(columns, row)) for row in rows],
                    use_container_width=True
                )
            else:
                st.info("No matching records found.")

            st.subheader("AI Summary")
            st.write(
                result.get("summary")
                or result.get("error")
                or "No summary available."
            )

        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a question.")

