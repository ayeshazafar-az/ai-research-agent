# AI Research Agent 🤖

A beginner-friendly Streamlit web application that uses **CrewAI** and the **Groq API** to perform internet research and write comprehensive summary reports on any topic.

## Features
* **Single Agent Setup:** Uses a Senior Research Analyst persona to conduct research.
* **Internet Searching:** Integrated with `ddgs` to search the live web for factual data.
* **Beginner Friendly:** Clean, easy to read code with inline comments explaining each step.
* **Secure API Keys:** No hardcoded secrets! Users can enter their API key via the web sidebar, or you can deploy securely using Streamlit Secrets.

## Installation (Local Testing)

1. **Clone or Download** this repository.
2. **Create a virtual environment** (optional but recommended):
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # Mac/Linux:
   source .venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
5. You can enter your Groq API key securely in the browser sidebar when the app opens!

## How to Deploy to Streamlit Community Cloud (Without Leaking Secrets!)

When you deploy a public app, you **never** want to paste your API keys directly into `app.py`. Instead, follow these steps:

1. **Upload to GitHub:**
   - Initialize a Git repository in this folder.
   - Commit `app.py`, `requirements.txt`, and `.gitignore`.
   - Push it to a public or private GitHub repository.

2. **Connect to Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io/).
   - Click **New App** and select your GitHub repository.

3. **Set up Secrets (So you don't have to type it in UI):**
   - Click on **Advanced Settings** before deploying (or go to App Settings > Secrets after deploying).
   - Add your API Key into the Secrets text box exactly like this:
     ```toml
     GROQ_API_KEY = "gsk_your_real_api_key_here..."
     ```
   - *The code in `app.py` is already set up to automatically read `GROQ_API_KEY` from Streamlit secrets and skip the sidebar prompt if it's there!*
