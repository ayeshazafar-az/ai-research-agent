import streamlit as st
import os
import requests
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF
from crewai.tools import tool
from ddgs import DDGS

def get_best_gemini_model(api_key: str) -> str:
    """Return a highly permissive model that bypasses strict Free Tier quotas."""
    return "gemini/gemini-3.5-flash-lite"

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
    pdf.multi_cell(w=0, h=6, text=safe_text)
    return bytes(pdf.output())

# ==========================================
# UI Styling & Layout
# ==========================================
st.set_page_config(page_title="AI Research Agent", page_icon="✨", layout="wide")

# Sidebar Customization
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/8636/8636906.png", width=80)
    st.header("⚙️ Engine Settings")
    st.markdown("Ensure your API key is loaded to authorize the AI Engine.")
    
    cloud_key = st.secrets.get("GEMINI_API_KEY", "") if "GEMINI_API_KEY" in st.secrets else ""
    if cloud_key:
        api_key = cloud_key
        st.success("API Key Status: **Authorized** ✅")
    else:
        api_key = st.text_input("🔑 Google Gemini API Key:", type="password")

    st.divider()
    st.markdown("### 📊 Metrics")
    st.metric(label="Agent Status", value="Online", delta="Connected")
    st.metric(label="Model Version", value="Gemini Flash", delta="Current")
    
    st.divider()
    st.markdown("👨‍💻 **Built by Ayesha**")

# Custom Dashboard CSS (Bento Box / Glassmorphism)
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Sleek Title */
    .main-title {
        font-family: 'Inter', sans-serif;
        font-weight: 900;
        font-size: 3.2rem;
        background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: -15px;
    }
    .sub-title {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-bottom: 30px;
    }
    
    /* Container Borders to make them look like Glass Cards */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        background-color: rgba(26, 19, 47, 0.4) !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        padding: 10px;
    }

    /* Primary Start Button with Mix Colors */
    button[data-testid="baseButton-primary"] {
        width: 100% !important;
        border-radius: 12px !important;
        height: 55px !important;
        background: linear-gradient(90deg, #6236FF 0%, #00F2FE 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 800 !important;
        font-size: 1.15rem !important;
        box-shadow: 0px 8px 30px rgba(98, 54, 255, 0.4) !important;
        transition: transform 0.3s ease !important;
        text-transform: uppercase !important;
        letter-spacing: 1.5px !important;
    }
    button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0px 12px 40px rgba(0, 242, 254, 0.6) !important;
    }
    
    /* Dedicated Red Delete Button Styling via Tooltip Target */
    button[title="Delete chat"] {
        background-color: rgba(255, 59, 48, 0.15) !important;
        border: 1px solid rgba(255, 59, 48, 0.4) !important;
        color: #FF3B30 !important;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    button[title="Delete chat"]:hover {
        background-color: rgba(255, 59, 48, 0.35) !important;
        border-color: #FF3B30 !important;
        box-shadow: 0px 0px 15px rgba(255, 59, 48, 0.5);
    }
    
    /* Secondary Buttons (History Items) */
    button[data-testid="baseButton-secondary"] {
        border-radius: 8px;
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease;
        text-align: left !important;
    }
    button[data-testid="baseButton-secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.05) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    st.markdown("<h1 class='main-title'>AI Research Agent</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-title'>Autonomous Omnichannel Workflows Powered by AI</p>", unsafe_allow_html=True)
with col_head2:
    st.markdown("<br>", unsafe_allow_html=True)
    st.info("🟢 **System Ready** | Awaiting Command")

st.divider()

import json
import uuid

# Load Chat History
HISTORY_FILE = "chat_history.json"

def load_chats():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_chats(chats):
    with open(HISTORY_FILE, "w") as f:
        json.dump(chats, f)

if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_chats()

if "current_chat_id" not in st.session_state:
    # Set to newest chat or create new
    if st.session_state.all_chats:
        st.session_state.current_chat_id = list(st.session_state.all_chats.keys())[-1]
    else:
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.all_chats[new_id] = {
            "title": "New Chat",
            "messages": [{"role": "assistant", "content": "System Online. What would you like to research today?"}]
        }
        save_chats(st.session_state.all_chats)

# Active chat reference
active_chat = st.session_state.all_chats[st.session_state.current_chat_id]

# Bento Box Dashboard Layout
main_col, side_col = st.columns([7, 3], gap="large")

with side_col:
    if st.button("➕ New Chat", use_container_width=True, type="primary"):
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.all_chats[new_id] = {
            "title": "New Chat",
            "messages": [{"role": "assistant", "content": "System Online. What would you like to research today?"}]
        }
        save_chats(st.session_state.all_chats)
        st.rerun()

    with st.container(border=True):
        st.subheader("📚 Chat History")
        
        # Display chat history buttons
        for chat_id, chat_data in reversed(list(st.session_state.all_chats.items())):
            # Active chat gets a special style
            is_active = (chat_id == st.session_state.current_chat_id)
            
            hist_col1, hist_col2 = st.columns([6, 1])
            with hist_col1:
                # Truncate long titles in the sidebar button cleanly
                display_title = chat_data['title'][:22] + "..." if len(chat_data['title']) > 22 else chat_data['title']
                if st.button(f"""{"🔵" if is_active else "📄"} {display_title}""", key=chat_id, use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            with hist_col2:
                # Two-Step Confirmation Delete Logic
                is_confirming = st.session_state.get('confirm_delete') == chat_id
                btn_icon = ":material/warning:" if is_confirming else ":material/delete:"
                btn_help = "Confirm delete" if is_confirming else "Delete chat"
                
                if st.button(" ", icon=btn_icon, key=f"del_{chat_id}", help=btn_help):
                    if is_confirming:
                        del st.session_state.all_chats[chat_id]
                        st.session_state.confirm_delete = None
                        # Automatically instantiate a new chat if the final one was deleted
                        if not st.session_state.all_chats:
                            new_id = str(uuid.uuid4())
                            st.session_state.current_chat_id = new_id
                            st.session_state.all_chats[new_id] = {
                                "title": "New Chat",
                                "messages": [{"role": "assistant", "content": "System Online. What would you like to research today?"}]
                            }
                        elif st.session_state.current_chat_id == chat_id:
                            st.session_state.current_chat_id = list(st.session_state.all_chats.keys())[-1]
                        save_chats(st.session_state.all_chats)
                    else:
                        st.session_state.confirm_delete = chat_id
                    st.rerun()

    with st.container(border=True):
        st.subheader("⚡ Capabilities")
        st.markdown("""
        - 🌐 **Web Access**: Live internet searching via DDGS.
        - 🧠 **Synthesis**: Deep reasoning and pattern reduction.
        - 📊 **Export**: Generates dynamic PDFs on the fly.
        - 🛡️ **Rate Limited**: Built-in quotas loop protections.
        - 💬 **Memory**: ChatGPT-style persistent conversations!
        """)
        
    st.divider()
    if st.button("🗑️ Clear All History", use_container_width=True):
        st.session_state.all_chats = {}
        if os.path.exists(HISTORY_FILE):
            os.remove(HISTORY_FILE)
        st.rerun()

with main_col:
    with st.container(border=True):
        st.subheader(f"🎯 Command Center: {active_chat['title']}")
            
        # Hydrate Chat History
        chat_slug = active_chat['title'].lower().replace(" ", "_").replace(".", "").replace(":", "")[:30]
        
        for i, msg in enumerate(active_chat["messages"]):
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                
                # Check if this specific message contains an export object
                if msg.get("md_text"):
                    st.divider()
                    st.markdown("##### 💾 Export Report")
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        st.download_button(
                            label="📄 Download as Markdown",
                            data=msg["md_text"],
                            file_name=f"{chat_slug}_report.md",
                            mime="text/markdown",
                            key=f"dl_md_{st.session_state.current_chat_id}_{i}"
                        )
                    with dl_col2:
                        st.download_button(
                            label="🖍️ Download as PDF",
                            data=generate_pdf(msg["md_text"]), # Generate dynamically to bypass JSON serialize crash!
                            file_name=f"{chat_slug}_report.pdf",
                            mime="application/pdf",
                            key=f"dl_pdf_{st.session_state.current_chat_id}_{i}"
                        )

        # Main Chat Input trigger
        if prompt := st.chat_input("🔍 Enter a topic or follow-up instruction..."):
            if not api_key:
                st.error("⚠️ Please configure your API Key in the sidebar before initiating.")
            else:
                # Meta-update title if it's a new chat
                if active_chat["title"] == "New Chat":
                    active_chat["title"] = prompt[:25] + "..." if len(prompt) > 25 else prompt
                
                # Instantly display user prompt
                active_chat["messages"].append({"role": "user", "content": prompt})
                save_chats(st.session_state.all_chats)
                
                with st.chat_message("user"):
                    st.markdown(prompt)
                    
                # Initiate Assistant Action
                with st.chat_message("assistant"):
                    with st.status("📡 **Deploying AI Agent to the Web...**", expanded=True) as status:
                        try:
                            st.write("🔍 Acquiring target backend parameters...")
                            os.environ["LITELLM_MAX_RETRIES"] = "0"
                            active_model = get_best_gemini_model(api_key)
                            
                            llm = LLM(model=active_model, api_key=api_key, temperature=0.3, max_retries=0)
                            
                            st.write("🧠 Formatting Session History for Context...")
                            # Serialize history so the agent remembers past instructions
                            history_str = "\\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in active_chat["messages"][:-1]])
                            
                            st.write("🧠 Booting CrewAI Reasoning Engine...")
                            researcher = Agent(
                                role="Elite Research Specialist",
                                goal=f"Conduct deep research on: {prompt}. Ensure you factor in any previous chat history.",
                                backstory="You are an autonomous analyst. Use the internet to extract highly accurate data.",
                                tools=[internet_search_tool],
                                llm=llm,
                                verbose=True,
                                max_iter=2,
                                allow_delegation=False
                            )

                            task = Task(
                                description=f"Chat History:\\n{history_str}\\n\\nCurrent Directive: '{prompt}'. \\n\\nExecute the directive deeply. Compile a finalized robust markdown response.",
                                expected_output="A highly detailed and well-formatted markdown analytical response.",
                                agent=researcher
                            )

                            crew = Crew(agents=[researcher], tasks=[task])
                            
                            st.write("🔎 Agents deployed! Synthesizing data...")
                            result = crew.kickoff()
                            
                            status.update(label="✅ Agent cycle complete!", state="complete", expanded=False)

                            # Final Text 
                            final_text = str(result.raw) if result and hasattr(result, 'raw') and result.raw else "Analysis failed to produce a valid response."

                            # Push to memory state (Excluding pure raw bytes so JSON doesn't crash!)
                            active_chat["messages"].append({
                                "role": "assistant",
                                "content": final_text,
                                "md_text": final_text
                            })
                            save_chats(st.session_state.all_chats)
                            
                            # Force rerun to natively render the new message into the loop above!
                            st.rerun()

                        except Exception as e:
                            status.update(label="❌ Mission Failed", state="error", expanded=True)
                            error_msg = str(e)
                            if "503" in error_msg or "UNAVAILABLE" in error_msg:
                                st.error("🚦 **Google Traffic Spike!** Wait 10 seconds and redeploy.")
                            elif "500" in error_msg or "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                                st.warning("⏳ **Google Quota Temporarily Exhausted.** Need a fresh project API key!")
                            else:
                                st.error(f"⚠️ **Critical System Failure:**\\n\\n{error_msg}")