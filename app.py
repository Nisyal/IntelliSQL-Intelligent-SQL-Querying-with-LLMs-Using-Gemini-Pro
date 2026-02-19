import streamlit as st
import os
import sqlite3
from dotenv import load_dotenv
load_dotenv()
from google import genai

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
print("API KEY LOADED:", os.getenv("GOOGLE_API_KEY"))


prompt = """
You are an expert in converting English questions to SQL queries.

The SQL database has one table named Students with the following columns:
name, class, marks, company.

Examples:
How many entries are present?
SQL: SELECT COUNT(*) FROM Students;

Tell me all the students studying in MCom class?
SQL: SELECT * FROM Students WHERE class='MCom';

Only return the SQL query. Do not explain anything.
"""

def get_response(que, prompt):
    response = client.models.generate_content(
        model="models/gemini-2.5-flash",
        contents=prompt + "\n" + que,
    )

    sql = response.text.strip()

    # Remove markdown formatting if present
    sql = sql.replace("```sql", "")
    sql = sql.replace("```", "")
    sql = sql.strip()

    return sql


def read_query(sql, db):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    conn.commit()
    conn.close()
    return rows

def page_home():
    st.markdown("""
        <style>
        body {
            background-color: #2E2E2E;
        }

        .main-title {
            text-align: center;
            color: #4CAF50; /* Green color for headings */
            font-size: 2.5em;
        }

        .sub-title {
            text-align: center;
            color: #4CAF50; /* Green color for headings */
            font-size: 1.5em;
        }

        .offerings {
            padding: 20px;
            color: white; /* White color for body text */
        }

        .offerings h2 {
            color: #4CAF50; /* Green color for headings */
        }

        .offerings ul {
            list-style-type: none;
            padding: 0;
        }

        .offerings li {
            margin: 10px 0;
            font-size: 18px;
        }

        .custom-sidebar {
            background-color: #2E2E2E;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 class='main-title'>Welcome to IntelliSQL!</h1>", unsafe_allow_html=True)
    st.markdown("<h2 class='sub-title'>Revolutionizing Database Querying with Advanced LLM Capabilities</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])

    with col1:
        st.image(
    "https://cdn1.iconfinder.com/data/icons/business-dual-color-glyph-set-3/128/Data_warehouse-1024.png",
    width="stretch"
)


    with col2:
        st.markdown("""
            <div class='offerings'>
                <h2>Wide Range of Offerings</h2>
                <ul>
                    <li>🔍 Intelligent Query Assistance</li>
                    <li>📊 Data Exploration and Insights</li>
                    <li>⚡ Efficient Data Retrieval</li>
                    <li>🚀 Performance Optimization</li>
                    <li>🛠 Syntax Suggestions</li>
                    <li>📈 Trend Analysis</li>
                </ul>
            </div>
        """, unsafe_allow_html=True)

def page_about():
    st.markdown("""
        <style>
        .content {
            color: white; /* White color for body text */
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='color: #4CAF50;'>About IntelliSQL</h1>", unsafe_allow_html=True)
    st.markdown("<div class='content'>", unsafe_allow_html=True)

    st.markdown("""
        <h2>IntelliSQL is an innovative project aimed at revolutionizing database querying 
        using advanced Language Model capabilities.</h2>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.image(
        "https://download.logo.wine/logo/Oracle_SQL_Developer/Oracle_SQL_Developer-Logo.wine.png",
        width="stretch"
    )

def page_intelligent_query_assistance():
    st.markdown("""
        <style>
        .tool-input {
            margin-bottom: 20px;
            color: white; /* White color for body text */
        }

        .response {
            margin-top: 20px;
            color: white; /* White color for body text */
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("<h1 style='color: #4CAF50;'>Intelligent Query Assistance</h1>", unsafe_allow_html=True)

    st.write("""
    IntelliSQL enhances the querying process by providing intelligent assistance to users.
    Whether they are novice or experienced SQL users.
    """)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("<div class='tool-input'>", unsafe_allow_html=True)

        que = st.text_input("Enter Your Query:", key="sql_query")
        submit = st.button("Get Answer", key="submit_button", help="Click to retrieve the SQL data")

        st.markdown("</div>", unsafe_allow_html=True)

        if submit or que:
            try:
                response = get_response(que, prompt)
                st.write(f"**Generated SQL Query:** {response}")

                response = read_query(response, "data.db")

                st.markdown("<div class='response'>", unsafe_allow_html=True)
                st.subheader("The Response is:")
                st.table(response)
                st.markdown("</div>", unsafe_allow_html=True)

            except Exception as e:
                st.subheader("Error:")
                st.error(f"An error occurred: {e}")

    with col2:
        st.image(
            "https://cdn-icons-png.flaticon.com/512/9850/9850877.png",
            width="stretch"
        )

def main():
    st.set_page_config(
        page_title="IntelliSQL",
        page_icon="🌟",
        layout="wide"
    )

    st.sidebar.title("Navigation")

    st.sidebar.markdown(
        "<style>.sidebar .sidebar-content {background-color: #2E2E2E; color: white;}</style>",
        unsafe_allow_html=True
    )

    pages = {
        "Home": page_home,
        "About": page_about,
        "Intelligent Query Assistance": page_intelligent_query_assistance,
    }

    selection = st.sidebar.radio("Go to", list(pages.keys()))
    page = pages[selection]
    page()


if __name__ == "__main__":
    main()

