import streamlit as st
import os
import requests
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF
from crewai.tools import tool
from ddgs import DDGS

def get_best_gemini_model(api_key: str) -> str:
    """Dynamically fetch the best available Gemini model, avoiding 3.6 due to 503 errors."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        response = requests.get(url, timeout=5)
        data = response.json()
        active_models = [m['name'].replace("models/", "gemini/") for m in data.get('models', []) if 'generateContent' in m.get('supportedGenerationMethods', [])]
        for m in active_models:
            if "flash" in m.lower() and "3.6" not in m: return m
        return active_models[0]
    except Exception:
        return "gemini/gemini-1.5-flash-8b"

@tool("Internet Search Tool")
def internet_search_tool(query: str) -> str:
    """Search the Internet for relevant information based on a query."""
    try:
        results = DDGS().text(query, max_results=3)
        search_text = "\n".join([result['body'] for result in results])
        return search_text if search_text else "No useful results found."
    except Exception as e:
        return f"Search failed: {e}"

def generate_pdf(text_content):
    """Converts the text to a downloadable PDF bytearray."""
    class PDF(FPDF):
        def header(self):
            self.set_font("Helvetica", "B", 15)
            self.set_text_color(40, 40, 40)
            self.cell(0, 10, "Autonomous AI Research Report", align="C")
            self.ln(20)
        def footer(self):
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Helvetica", size=11)
    pdf.set_text_color(20, 20, 20)
    
    # Clean text to prevent FPDF unicode errors
    safe_text = text_content.encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 6, txt=safe_text)
    return bytes(pdf.output())

# ==========================================
# UI Styling
# ==========================================
st.set_page_config(page_title="AI Research Assistant", page_icon="✨", layout="centered")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    st.markdown("Ensure your API key is loaded below.")
    
    cloud_key = st.secrets.get("GEMINI_API_KEY", "") if "GEMINI_API_KEY" in st.secrets else ""
    if cloud_key:
        api_key = cloud_key
        st.success("API Key loaded securely! ✅")
    else:
        api_key = st.text_input("🔑 Google Gemini API Key:", type="password")

    st.divider()
    st.markdown("🎨 **Theme Customization**")
    primary_color = st.color_picker("Primary Accent Color", "#00e5ff")
    bg_gradient = st.color_picker("Background Gradient Fade", "#8a2be2")
    bg_body = st.color_picker("App Background", "#09090b")
    
    st.divider()
    st.markdown("👨‍💻 **Built by Ayesha**")

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_body};
    }}
    .main-title {{
        background: linear-gradient(90deg, {primary_color}, {bg_gradient});
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 900;
        font-size: 3.5rem;
        margin-bottom: 0px;
        padding-bottom: 0px;
        letter-spacing: -1.5px;
        text-align: center;
    }}
    .sub-title {{
        color: #a1a1aa;
        font-size: 1.15rem;
        margin-bottom: 35px;
        font-weight: 400;
        text-align: center;
    }}
    .stButton>button {{
        width: 100%;
        border-radius: 50px;
        background: linear-gradient(90deg, {primary_color}, {bg_gradient});
        color: white;
        border: none;
        height: 52px;
        font-weight: 800;
        font-size: 1.15rem;
        box-shadow: 0px 4px 20px {primary_color}40;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0px 8px 25px {primary_color}60;
        color: white;
    }}
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>✨ AI Research Desk</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Enter your topic below to generate a beautiful web report.</p>", unsafe_allow_html=True)


# Main Interface
col1, col2, col3 = st.columns([1, 6, 1])

with col2:
    topic = st.text_input("🔍 What would you like to research?", placeholder="e.g. 2026 App Development Roadmaps")
    
    # Clean, literal button text
    if st.button("✨ Generate Report"):
        if not api_key:
            st.error("⚠️ Please configure your API Key in the sidebar.")
        elif not topic:
            st.warning("⚠️ Please provide a research topic.")
        else:
            with st.status("📡 Generating Report...", expanded=True) as status:
                try:
                    st.write("🔍 Acquiring target backend parameters...")
                    os.environ["LITELLM_MAX_RETRIES"] = "0"
                    active_model = get_best_gemini_model(api_key)
                    
                    llm = LLM(model=active_model, api_key=api_key, temperature=0.3, max_retries=0)
                    
                    st.write("🧠 Booting CrewAI Reasoning Engine...")
                    researcher = Agent(
                        role="Elite Research Specialist",
                        goal=f"Deep-dive research into: {topic}. Print a gorgeous finalized markdown report.",
                        backstory="You are Orion, a top-tier analyst capable of searching the web and synthesizing complex technical subjects.",
                        tools=[internet_search_tool],
                        llm=llm,
                        verbose=True,
                        max_iter=2,
                        allow_delegation=False
                    )

                    task = Task(
                        description=f"Query the web for the absolute latest data on '{topic}'. Compile it into a master report.",
                        expected_output="A robust markdown report containing actionable takeaways.",
                        agent=researcher
                    )

                    crew = Crew(agents=[researcher], tasks=[task])
                    
                    st.write("🔎 Agents deployed to the web! Synthesizing data...")
                    result = crew.kickoff()
                    
                    status.update(label="✅ Orion has finished the report!", state="complete", expanded=False)

                    # Export & Formatting
                    final_text = str(result.raw) if result and hasattr(result, 'raw') and result.raw else "Analysis failed to produce a valid response."
                    
                    st.divider()
                    st.markdown("### 📊 Official Report")
                    with st.container(border=True):
                        st.markdown(final_text)

                    st.divider()
                    st.markdown("### 💾 Export Assets")
                    
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        st.download_button(
                            label="📄 Download as Markdown",
                            data=final_text,
                            file_name="orion_report.md",
                            mime="text/markdown"
                        )
                    with dl_col2:
                         # Generate PDF
                        pdf_bytes = generate_pdf(final_text)
                        st.download_button(
                            label="🖍️ Download as PDF",
                            data=pdf_bytes,
                            file_name="orion_report.pdf",
                            mime="application/pdf"
                        )

                except Exception as e:
                    status.update(label="❌ Mission Failed", state="error", expanded=True)
                    error_msg = str(e)
                    if "503" in error_msg or "UNAVAILABLE" in error_msg:
                        st.error("🚦 **Google Traffic Spike!** Wait 10 seconds and redeploy the agent.")
                    elif "500" in error_msg or "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                        st.warning("⏳ **Google Quota Temporarily Exhausted.** Need a fresh project API key!")
                    else:
                        st.error(f"⚠️ **Critical System Failure:**\n\n{error_msg}")