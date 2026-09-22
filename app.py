import streamlit as st
import os
import requests
import json
import uuid
from crewai import Agent, Task, Crew, LLM
from fpdf import FPDF
import markdown
from crewai.tools import tool
from ddgs import DDGS

st.set_page_config(page_title="AI Research Agent", layout="wide", initial_sidebar_state="expanded")

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
    pdf.set_font("Helvetica", size=11)
    
    # Process rich markdown formatting utilizing native HTML hooks in fpdf2
    safe_text = text_content.encode('latin-1', 'ignore').decode('latin-1')
    html_content = markdown.markdown(safe_text)
    
    # Strip unresolvable internal markdown links (e.g., footnotes [1](#footer)) to prevent fpdf2 crashes
    import re
    html_content = re.sub(r'<a[^>]*href="#[^"]*"[^>]*>(.*?)</a>', r'\1', html_content)
    
    pdf.write_html(html_content)
    return bytes(pdf.output())

# ==========================================
# UI Styling & Layout
# ==========================================
st.set_page_config(page_title="AI Research Agent", page_icon="✨", layout="wide")

# We extracted the Engine Settings from here and shift it further down to a dedicated Right Column.

# Custom Dashboard CSS (Bento Box / Glassmorphism)
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }
    
    /* Global App Background */
    .stApp {
        background-color: #020617 !important;
        background-image: 
            radial-gradient(circle at 0% 0%, rgba(124, 58, 237, 0.12) 0%, transparent 50%),
            radial-gradient(circle at 100% 100%, rgba(6, 182, 212, 0.12) 0%, transparent 50%) !important;
    }
    
    /* Glassmorphism Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(10, 14, 23, 0.7) !important;
        backdrop-filter: blur(15px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Bento Box Borders */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.02) !important;
        backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5) !important;
    }
    
    /* Headings */
    .main-title {
        background: linear-gradient(90deg, #00F2FE, #4FACFE);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #94A3B8;
        font-size: 1.1rem;
        margin-top: -10px;
        margin-bottom: 20px;
    }
    
    /* Chat Messages */
    [data-testid="stChatMessage"] {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        padding: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
    }

    /* Primary Start Button (Fix for Streamlit Cloud missing identifiers) */
    button[kind="primary"] {
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
    button[kind="primary"]:hover {
        transform: translateY(-3px) scale(1.02) !important;
        box-shadow: 0px 12px 40px rgba(0, 242, 254, 0.6) !important;
    }
    
    /* Secondary Buttons (History Items) */
    button[kind="secondary"] {
        border-radius: 8px !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        color: #94A3B8 !important;
        transition: all 0.2s ease !important;
        text-align: left !important;
    }
    button[kind="secondary"]:hover {
        background-color: rgba(255, 255, 255, 0.08) !important;
        border-color: rgba(255, 255, 255, 0.2) !important;
        color: white !important;
    }
    
    /* Specialized Delete Button Styles */
    .del-btn-wrapper button {
        background-color: rgba(255, 59, 48, 0.15) !important;
        border: 1px solid rgba(255, 59, 48, 0.4) !important;
        color: #FF3B30 !important;
    }
    .del-btn-wrapper button:hover {
        background-color: rgba(255, 59, 48, 0.35) !important;
        border-color: #FF3B30 !important;
        box-shadow: 0px 0px 15px rgba(255, 59, 48, 0.5) !important;
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

import uuid

# Memory Management: Isolated Per-Session Memory (Stateless Deployment)
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {}

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

# Active chat reference
active_chat = st.session_state.all_chats[st.session_state.current_chat_id]

# Bento Box Dashboard Layout
with st.sidebar:
    if st.button("➕ New Chat", use_container_width=True, type="primary") or not active_chat:
        new_id = str(uuid.uuid4())
        st.session_state.current_chat_id = new_id
        st.session_state.all_chats[new_id] = {
            "title": "New Chat",
            "messages": [{"role": "assistant", "content": "System Online. What would you like to research today?"}]
        }

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
                
                st.markdown('<div class="del-btn-wrapper">', unsafe_allow_html=True)
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
                
                    else:
                        st.session_state.confirm_delete = chat_id
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

# Layout Split Setup
chat_col, settings_col = st.columns([75, 25], gap="large")

with settings_col:
    with st.container(border=True):
        st.header("⚙️ AI Engine Settings")
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
    if st.button("🗑️ Clear All History", use_container_width=True):
        st.session_state.all_chats = {}
        st.rerun()

with chat_col:
    with st.container(border=True):
        st.subheader(f"🎯 Command Center: {active_chat['title']}")
            
        # Hydrate Chat History
        chat_slug = active_chat['title'].lower().replace(" ", "_").replace(".", "").replace(":", "")[:30]
        
        # ChatGPT-Style Dynamic Welcome Screen
        if len(active_chat["messages"]) == 1:
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("<h3 style='text-align: center; color: #94A3B8;'>How can I help you research today?</h3>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            cap_col1, cap_col2 = st.columns(2)
            with cap_col1:
                st.markdown("""
                <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; margin-bottom: 10px;'>
                🌐 <b>Live Web Access</b><br>
                <span style='color: #94A3B8; font-size: 0.9em;'>Bypasses static training data by searching the Live Internet via DuckDuckGo.</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 12px;'>
                🧠 <b>Deep Synthesis</b><br>
                <span style='color: #94A3B8; font-size: 0.9em;'>Uses CrewAI Agents to contextually reason over data before responding.</span>
                </div>
                """, unsafe_allow_html=True)
            with cap_col2:
                st.markdown("""
                <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 12px; margin-bottom: 10px;'>
                🛡️ <b>Quota Protections</b><br>
                <span style='color: #94A3B8; font-size: 0.9em;'>Dynamically utilizes Gemini 3.5 Flash Lite to ensure a 500-request daily limit.</span>
                </div>
                """, unsafe_allow_html=True)
                st.markdown("""
                <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05); padding: 15px; border-radius: 12px;'>
                📄 <b>Dynamic Exporting</b><br>
                <span style='color: #94A3B8; font-size: 0.9em;'>Generates downloadable PDF and Markdown reports asynchronously.</span>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("<br><br>", unsafe_allow_html=True)
        
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