import streamlit as st
import os
from crewai import Agent, Task, Crew, LLM

import crewai.llms.cache as _crewai_cache
# Monkey-patch to fix CrewAI appending 'cache_breakpoint' to Groq models
_crewai_cache.mark_cache_breakpoint = lambda msg: msg

# pyrefly: ignore [missing-import]
from crewai.tools import tool
# pyrefly: ignore [missing-import]
from ddgs import DDGS
import requests
import json

def get_active_groq_model(api_key: str) -> str:
    """Dynamically fetch an active Groq model to prevent decommissioning errors!"""
    try:
        response = requests.get(
            'https://api.groq.com/openai/v1/models', 
            headers={'Authorization': f'Bearer {api_key}'},
            timeout=5
        )
        data = response.json()
        models = [m['id'] for m in data.get("data", [])]
        # Prioritize a fast, cheap 8B llama model if available to avoid limits
        for m in models:
            if "llama" in m.lower() and ("8b" in m.lower() or "instant" in m.lower()):
                return f"groq/{m}"
        # Fallback to the first LLAMA model found
        for m in models:
            if "llama" in m.lower(): return f"groq/{m}"
        # Absolute fallback to whatever the primary active model is
        return f"groq/{models[0]}"
    except Exception:
        # If API fetch fails because of your local machine's firewall/proxy, fallback to Mixtral
        return "groq/mixtral-8x7b-32768"

# ==========================================
# 1. Setup the Custom Search Tool
# ==========================================
@tool("Internet Search Tool")
def internet_search_tool(query: str) -> str:
    """Search the Internet for relevant information based on a query."""
    try:
        results = DDGS().text(keywords=query, max_results=3)
        search_text = "\n".join([result['body'] for result in results])
        return search_text if search_text else "No useful results found."
    except Exception as e:
        return f"Search failed: {e}"

# ==========================================
# 2. Streamlit Web Interface Setup
# ==========================================
st.set_page_config(page_title="AI Research Agent", layout="centered")
st.title("🤖 AI Research Agent")
st.markdown("Enter a topic below. The agent will search the web and write a comprehensive report.")

# Sidebar for API Keys
with st.sidebar:
    st.header("Configuration")
    st.markdown("For this app to work, you need a Groq API Key.")
    
    try:
        cloud_api_key = st.secrets.get("GROQ_API_KEY", "")
    except Exception:
        cloud_api_key = ""
    
    if cloud_api_key:
        api_key = cloud_api_key
        st.success("API Key loaded securely from Secrets! ✅")
    else:
        api_key = st.text_input("Enter your Groq API Key:", type="password")
        st.caption("Required to power the Groq model.")

# Main Input
topic = st.text_input("What would you like me to research?")

# ==========================================
# 3. Execution Logic
# ==========================================
if st.button("Generate Report"):
    if not api_key:
        st.error("Please enter your Groq API Key in the sidebar or add it to Streamlit Secrets.")
    elif not topic:
        st.warning("Please enter a research topic.")
    else:
        with st.spinner("Agent is researching and writing... This may take a minute."):
            try:
                # Dynamically Auto-Find the model!
                active_model = get_active_groq_model(api_key)
                
                llm = LLM(
                    model=active_model,
                    api_key=api_key,
                    temperature=0.3
                )

                researcher = Agent(
                    role="Senior Research Analyst",
                    goal=f"Conduct thorough research and write a detailed, factual report on: {topic}",
                    backstory="You are an expert researcher known for finding accurate information and summarizing it clearly.",
                    tools=[internet_search_tool],
                    llm=llm,
                    verbose=True,
                    max_iter=3,
                    allow_delegation=False
                )

                research_task = Task(
                    description=f"Search the web for the latest information on '{topic}'. Compile the findings into a well-structured report.",
                    expected_output="A detailed markdown report covering the key aspects of the topic.",
                    agent=researcher
                )

                crew = Crew(
                    agents=[researcher],
                    tasks=[research_task]
                )
                
                result = crew.kickoff()

                st.success("Research Complete!")
                st.markdown("---")
                st.markdown(result.raw)

            except Exception as e:
                error_msg = str(e)
                if "503" in error_msg or "UNAVAILABLE" in error_msg:
                    st.info(f"🚦 **Whoops! Groq servers are a little too busy right now.** Traffic spikes are normal for the free tier. Take a breath and click Generate again in a few seconds! \n\n *(Error: {error_msg})*")
                elif "500" in error_msg or "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                    st.warning(f"⏳ **Groq API limit reached.** Give it a minute and try again! \n\n *(Exact Rate Limit Hit: {error_msg})*")
                else:
                    st.error(f"⚠️ **Oh no! An unexpected error occurred:**\n\n{error_msg}")