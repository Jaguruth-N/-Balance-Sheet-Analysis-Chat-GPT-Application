# AI-Powered Financial Analyst Chat Bot 📈

An intelligent web application powered by Google Gemini for analyzing financial statements from PDF reports. This tool provides secure, role-based access to financial data, interactive visualizations, and a conversational Q&A interface.



## About The Project

This application was developed to automate and enhance the process of balance sheet analysis. It addresses the need for a tool that can quickly parse dense financial documents, provide high-level insights, and maintain strict data confidentiality for different management levels.

The system uses Google's Gemini Pro to extract key metrics, a Streamlit frontend for an interactive user experience, and a secure backend with role-based access control.

---
## Key Features

* **🤖 AI-Powered Data Extraction:** Automatically reads PDF reports and structures key financial metrics using Google Gemini.
* **🔒 Secure Multi-Tenant System:** Features Role-Based Access Control (RBAC) to ensure CEOs and management only see the data they are authorized to view.
* **📊 Interactive Dashboards:** Visualizes financial trends for revenue, assets, and liabilities using Plotly.
* **💬 Conversational Q&A:** Allows users to ask complex questions in natural language and receive instant, data-driven answers.
* **☁️ Publicly Deployed:** Designed for and deployed on Streamlit Community Cloud.

---
## Tech Stack

* **Backend:** Python
* **Frontend:** Streamlit
* **AI Model:** Google Gemini Pro
* **Database:** SQLite
* **PDF Parsing:** PyMuPDF
* **Data Handling:** Pandas, Tabulate

---
## Getting Started

Follow these steps to set up and run the project on your local machine.

### Prerequisites

* **Python (3.9+):** Make sure Python is installed on your system.
* **Git:** You'll need Git to clone the repository.
* **Google Gemini API Key:** You must have an active API key from [Google AI Studio](https://aistudio.google.com/).

### Installation & Setup

1.  **Clone the Repository**
    ```sh
    git clone [https://github.com/Jaguruth-N/Financial-Analyst-Chat-Bot.git](https://github.com/Jaguruth-N/Financial-Analyst-Chat-Bot.git)
    ```

2.  **Navigate to the Project Directory**
    ```sh
    cd Financial-Analyst-Chat-Bot
    ```

3.  **Create a Virtual Environment**
    ```sh
    python -m venv venv
    ```

4.  **Activate the Virtual Environment**
    * On Windows (PowerShell):
        ```powershell
        .\venv\Scripts\Activate.ps1
        ```
    * On macOS/Linux (Bash):
        ```bash
        source venv/bin/activate
        ```

5.  **Install Dependencies**
    ```sh
    pip install -r requirements.txt
    ```

6.  **Configure Your API Key**
    * Create a folder named `.streamlit` in the root of your project directory.
    * Inside the `.streamlit` folder, create a file named `secrets.toml`.
    * Add your Google Gemini API key to this file:
        ```toml
        GOOGLE_API_KEY="YOUR_GEMINI_API_KEY_HERE"
        ```

7.  **Download Sample Data**
    * Create a folder named `data` in the root directory.
    * Download the sample balance sheet PDF from [this link](https://www.ril.com/ar2023-24/pdf/consolidated.pdf) and save it inside the `data` folder as `consolidated.pdf`.

8.  **Seed the Database (One-Time Setup)**
    * Run the seeding script to create the database, set up users, and process the PDF with the AI. This step uses your API key and may take a few minutes.
    * Create a folder named `db` in the root directory before running the script.
        ```sh
        python seed_database.py
        ```

---
## Usage

### Running the Application

Once the setup is complete, launch the Streamlit application:
```sh
streamlit run app.py