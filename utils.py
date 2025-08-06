import fitz  # PyMuPDF
import google.generativeai as genai # <-- CHANGE: New library import
import json
import streamlit as st
import pandas as pd
import re

# --- CHANGE: Configure the Gemini client ---
try:
    # Use the new key from secrets.toml
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception:
    print("Google API key not found. Please check your secrets.toml file.")


def extract_text_from_pdf(pdf_path):
    """Extracts text from a given PDF file."""
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text

def get_financial_data_from_llm(text_chunk):
    """
    Sends text to Google Gemini API to extract structured financial data.
    """
    # --- CHANGE: New model instantiation and updated prompt for Gemini ---
    model = genai.GenerativeModel('gemini-2.5-pro')
    # Prompt engineering for Gemini to ensure it returns only JSON.
    prompt = """
    You are an expert financial analyst. Your task is to extract key financial metrics from the provided text of a company's consolidated balance sheet and income statement.
    Find the following metrics for the last two available fiscal years:
    - Revenue from Operations
    - Other Income
    - Total Income
    - Net Profit / (Loss) for the period
    - Total Assets
    - Total Liabilities
    - Total Equity
    - Earnings Per Share (Basic, in ₹)

    Analyze the provided text and return a single, valid JSON object and nothing else. Do not include any explanatory text before or after the JSON. The JSON object should be enclosed in ```json ... ```.
    If a value is not found, represent it as null.
    
    Example format:
    ```json
    {
      "2024": {
        "Revenue from Operations": 800000,
        "Net Profit": 50000
      },
      "2023": {
        "Revenue from Operations": 750000,
        "Net Profit": 45000
      }
    }
    ```
    Here is the financial document text:

    """ + text_chunk

    try:
        # --- CHANGE: New API call syntax ---
        response = model.generate_content(prompt)
        
        # --- CHANGE: Logic to parse JSON from Gemini's text response ---
        # Find the JSON block within the markdown-style code block
        json_match = re.search(r'```json\n(.*)\n```', response.text, re.DOTALL)
        if json_match:
            json_string = json_match.group(1)
            return json.loads(json_string)
        else:
            # Fallback for when the model doesn't use the markdown block
            return json.loads(response.text)

    except Exception as e:
        print(f"\n---!!! GEMINI API ERROR !!!---")
        print(f"An error occurred while communicating with the Gemini model: {e}")
        print(f"---!!! END OF ERROR !!!---\n")
        st.error(f"An error occurred while communicating with the AI model: {e}")
        return None

def process_and_store_pdf(pdf_path, company_id, conn):
    """Main function to process a PDF and store extracted data in the DB."""
    print(f"Processing {pdf_path} for company ID {company_id}...")
    
    full_text = extract_text_from_pdf(pdf_path)
    text_chunk = full_text[:80000] 

    extracted_data = get_financial_data_from_llm(text_chunk)
    
    if extracted_data:
        cursor = conn.cursor()
        for year, data in extracted_data.items():
            try:
                cursor.execute(
                    """
                    INSERT INTO financial_data (company_id, year, data_json, source_document)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(company_id, year) DO UPDATE SET
                    data_json = excluded.data_json,
                    source_document = excluded.source_document
                    """,
                    (company_id, int(year), json.dumps(data), pdf_path.split('/')[-1])
                )
                print(f"Stored data for Company ID {company_id}, Year {year}")
            except Exception as e:
                print(f"Error storing data for year {year}: {e}")
        conn.commit()
        print("Data storage complete.")
        return True
    else:
        print("Failed to extract data from LLM.")
        return False

def get_ai_analysis(user_query, financial_data_df):
    """Generates AI analysis based on user query and financial data."""
    # --- CHANGE: New model instantiation and updated prompt for Gemini ---
    model = genai.GenerativeModel('gemini-2.5-pro')
    
    # For Gemini, we combine the system instructions and user data into a single prompt.
    prompt = f"""
    You are a helpful financial analyst assistant for top management. Your tone should be professional, insightful, and concise.
    Based on the financial data provided below in Markdown format, answer the user's question.
    Provide clear insights, calculate relevant ratios if asked (like Debt-to-Equity, Net Profit Margin), and offer a brief summary of performance.
    Format your response using Markdown for readability.

    FINANCIAL DATA:
    {financial_data_df.to_markdown()}

    USER QUESTION:
    {user_query}
    """
    
    try:
        # --- CHANGE: New API call syntax ---
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating analysis: {e}")
        return "Sorry, I was unable to generate an analysis at this time."