import streamlit as st
import pandas as pd
import plotly.express as px
import json
from werkzeug.security import check_password_hash
from database import get_db_connection
from utils import get_ai_analysis

# --- Page Configuration ---
st.set_page_config(page_title="Financial Analyst Chat-Bot", layout="wide")

# --- User Authentication ---
def login_page():
    """Displays the login form."""
    st.header("Login")
    with st.form("login_form"):
        username = st.text_input("Username").lower()
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

        if submitted:
            conn = get_db_connection()
            user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
            conn.close()
            
            if user and check_password_hash(user['password_hash'], password):
                st.session_state['logged_in'] = True
                st.session_state['user_id'] = user['id']
                st.session_state['username'] = user['username']
                st.session_state['role'] = user['role']
                st.rerun()
            else:
                st.error("Invalid username or password")

def get_user_accessible_companies(user_id):
    """Fetches the list of companies a user can access."""
    conn = get_db_connection()
    companies = conn.execute("""
        SELECT c.id, c.name FROM companies c
        JOIN user_company_permissions p ON c.id = p.company_id
        WHERE p.user_id = ?
        ORDER BY c.name
    """, (user_id,)).fetchall()
    conn.close()
    return {comp['name']: comp['id'] for comp in companies}

# --- Main Application ---
def main_app():
    """The main application interface after login."""
    st.sidebar.title(f"Welcome, {st.session_state['username'].capitalize()}")
    st.sidebar.write(f"Role: {st.session_state['role']}")
    if st.sidebar.button("Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.title("Financial Analyst Chat-Bot 📈")
    st.markdown("Select a company to analyze its balance sheet and ask performance-related questions.")

    accessible_companies = get_user_accessible_companies(st.session_state['user_id'])
    if not accessible_companies:
        st.warning("You do not have access to any company data. Please contact an administrator.")
        return

    selected_company_name = st.selectbox("Select a Company", options=list(accessible_companies.keys()))
    selected_company_id = accessible_companies[selected_company_name]

    # --- Data Loading and Display ---
    conn = get_db_connection()
    data_rows = conn.execute("""
        SELECT year, data_json FROM financial_data
        WHERE company_id = ? ORDER BY year DESC
    """, (selected_company_id,)).fetchall()
    conn.close()

    if not data_rows:
        st.error(f"No financial data found for {selected_company_name}. Please process the relevant documents.")
        return

    # Process data into a DataFrame
    all_data = []
    for row in data_rows:
        year_data = json.loads(row['data_json'])
        year_data['Year'] = row['year']
        all_data.append(year_data)
    
    df = pd.DataFrame(all_data).set_index('Year').sort_index()
    # Clean up data - convert to numeric, handling errors
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    st.subheader(f"Financial Overview for {selected_company_name}")
    st.dataframe(df.style.format("{:,.0f}"))

    # --- Visualizations ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Revenue and Profit Trends")
        fig_revenue = px.bar(df, y=['Revenue from Operations', 'Net Profit / (Loss) for the period'], 
                             barmode='group', title="Revenue vs. Net Profit")
        st.plotly_chart(fig_revenue, use_container_width=True)

    with col2:
        st.subheader("Assets vs. Liabilities")
        fig_assets = px.line(df, y=['Total Assets', 'Total Liabilities'], 
                              markers=True, title="Total Assets vs. Total Liabilities")
        st.plotly_chart(fig_assets, use_container_width=True)

    # --- Chat Interface ---
    st.subheader("Ask a Question")
    st.markdown("e.g., `What was the net profit margin in 2024?` or `Summarize the change in assets.`")

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Your question..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                response = get_ai_analysis(prompt, df)
                st.markdown(response)
        
        st.session_state.messages.append({"role": "assistant", "content": response})


# --- Main Logic ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if st.session_state['logged_in']:
    main_app()
else:
    login_page()