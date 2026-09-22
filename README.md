# ✨ AI Research Agent (Autonomous)

A highly advanced, fully autonomous web-research agent built with **Streamlit** and **CrewAI**. This application operates as an elite, omnichannel research analyst that actively queries the live web, synthesizes complex data, and outputs strictly formatted PDF/Markdown master reports. 

Recently updated to feature a fully persistent, ChatGPT-style conversational memory system mapped onto a stunning Glassmorphic "Bento Box" dashboard.

## 🚀 Core Capabilities
- **ChatGPT-Style Memory Engine:** Engage in a persistent, natural conversation with the agent. Follow-up instructions seamlessly pull context from past dialogue.
- **Offline Thread History:** All chats are securely written to a local JSON database database (`chat_history.json`), allowing you to effortlessly hop back and forth between past sessions exactly like ChatGPT!
- **Dynamic File Export Engine:** Instantly generate `.md` and `.pdf` files. Memory mapping ensures your generated downloads never mysteriously vanish after you click them.
- **Autonomous Web Browsing:** Live, unrestricted deep searching deployed via `ddgs` (DuckDuckGo Search engine module).
- **Quota Armor:** Intelligently hardcoded to utilize `gemini-3.5-flash-lite`, bypassing Google's strict 20-Request-Per-Day limit and granting you 500 Daily Requests!

## 📸 Architecture
- **Frontend Dashboard:** Streamlit natively wrapped in a highly appealing Glassmorphism aesthetic.
- **AI Core:** Langchain + CrewAI (`Agent` & `Task` modeling). 
- **LLM Engine:** Google Gemini (Integrated safely against 503 limits).

## 🛠️ Installation & Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/ayeshazafar-az/ai-research-agent.git
   cd ai-research-agent
   ```

2. Establish your environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Launch the Application:
   ```bash
   streamlit run app.py
   ```

## 🔒 Configuration & Streamlit Cloud Deployment
This application was engineered explicitly to be continuously deployed on **Streamlit Community Cloud**.

When deploying for production, ensure you map your API Key natively inside Streamlit Cloud's `Advanced settings > Secrets` modal to prevent public exposure:
```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "AIzaSyYourSecretKey..."
```

*Note: The frontend allows you to paste the API Key directly into the sidebar if you are running bare-metal locally!*

---
**Built by Ayesha** | *2026 Architectural Codebase*
