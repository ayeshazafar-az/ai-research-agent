<div align="center">
  <img src="https://raw.githubusercontent.com/FortAwesome/Font-Awesome/master/svgs/solid/robot.svg" width="80" alt="Robot Icon" style="filter: invert(100%);">
  <h1>🌌 Orion AI Research Agent</h1>
  <p><b>Autonomous Omnichannel Workflows Powered by Google Gemini</b></p>
  
  [![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)
  [![Python](https://img.shields.io/badge/Python-3.13-blue.svg?logo=python&logoColor=white)](https://python.org)
  [![CrewAI](https://img.shields.io/badge/Agent-CrewAI-FF3B30.svg?logo=android&logoColor=white)](#)
  [![Status](https://img.shields.io/badge/Status-Production_Ready-00FF87.svg)](#)
</div>

<br>

> **Orion** is not just a static script. It is a fully persistent, hyper-intelligent web analyst. Wrapped in a breathtaking Glassmorphic **Bento Box Dashboard**, it mimics the native ChatGPT experience while possessing the raw power to actively browse the web and instantly synthesize live data into downloadable master reports.

## 🎥 Live Demonstration
*(Drag and drop your 22-second `.mp4` file directly over this text in the GitHub Web Editor to automatically upload and embed the video!)*

## ✨ High-Fidelity Features

| 🌟 Capability | 🛠️ Implementation & Mechanic |
|---|---|
| **🧠 ChatGPT-Style Memory** | Infinite conversational persistence. Jump back into past chat threads natively from your sidebar! Powered by a dynamic, automatic JSON database mapping. |
| **🌐 Autonomous Web Access** | Agents are armed with `ddgs` (DuckDuckGo Search) tools to scrape and pull live, real-time data from the open internet without any API costs. |
| **🎨 Bento Box Aesthetics** | A premium, dark-mode glassmorphic interface built entirely via custom Streamlit CSS injection. Features animated neon-gradients and explicit danger states! |
| **🛡️ 500-Query Quota Armor** | Engineered to bypass aggressive Gemini rate limits (429 errors) by dynamically defaulting to the highly permissive `gemini-3.5-flash-lite` LLM layer. |
| **💾 Dynamic Export Engine** | Generates completely custom `.pdf` and `.md` reports natively in the chat flow. Memory mapping guarantees your downloads never inexplicably vanish on click. |
| **🔒 Safe Deletion** | Multi-stepped "Confirm to Delete" mechanics prevent accidental destruction of your valuable research architecture. |

---

## 📸 Architecture Stack
- **Frontend Dashboard:** [Streamlit](https://streamlit.io/) (Natively wrapped in custom CSS HTML blocks)
- **AI Core:** [Langchain](https://python.langchain.com/) + [CrewAI](https://crewai.com/)
- **LLM Engine:** [Google Gemini API](https://ai.google.dev/)
- **Document Exporting:** `fpdf2` & `markdown`

---

## � Installation & Local Boot 

**1. Clone the repository natively:**
```bash
git clone https://github.com/ayeshazafar-az/ai-research-agent.git
cd ai-research-agent
```

**2. Establish your isolated environment:**
```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Mac/Linux
pip install -r requirements.txt
```

**3. Launch the Application Grid:**
```bash
streamlit run app.py
```
*(You can paste your API key securely into the sidebar once the UI boots!)*

---

## 🔒 Streamlit Cloud Deployment

This codebase was explicitly engineered to be continuously deployed natively onto **Streamlit Community Cloud**.

When deploying for production, ensure you map your API Key safely behind Streamlit Cloud's `Advanced settings > Secrets` modal to prevent GitHub exposure!

```toml
# .streamlit/secrets.toml
GEMINI_API_KEY = "AIzaSyYourSecretKey..."
```

<div align="center">
  <br>
  <b><i>Built with ❤️ by Ayesha | 2026 Architectural Codebase</i></b>
</div>
