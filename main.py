import streamlit as st
import sqlite3
import os
import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate # CORRECTED IMPORT
from langchain_core.output_parsers import StrOutputParser # NEW IMPORT for LCEL
import base64
from contextlib import contextmanager

# --- 1. Setup and Configuration ---

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Set Streamlit page config
st.set_page_config(
    page_title="AI Content Workflow Tool",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. Database Management (SQLite) ---

DB_NAME = "content_workflow.db"

@contextmanager
def get_db_connection():
    """Context manager for SQLite database connection."""
    conn = sqlite3.connect(DB_NAME)
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize the SQLite database and create the content table."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS content (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            content_type TEXT,
            tone TEXT,
            length TEXT,
            topic TEXT,
            idea TEXT,
            outline TEXT,
            draft TEXT,
            final_content TEXT,
            clarity_score INTEGER,
            engagement_score INTEGER
        )
        """)
        conn.commit()

def save_content(content_type, tone, length, topic, idea, outline, draft, final_content, clarity, engagement):
    """Save a full content workflow run to the database."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO content (content_type, tone, length, topic, idea, outline, draft, final_content, clarity_score, engagement_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (content_type, tone, length, topic, idea, outline, draft, final_content, clarity, engagement))
        conn.commit()
    st.toast("Content saved to database!", icon="✅")

# --- 3. Prompt Engineering & Few-Shot Examples ---

# This dict simulates few-shot prompting by providing specific style examples.
FEW_SHOT_EXAMPLES = {
    "Professional": """
    **Example:** "We are pleased to announce our quarterly earnings, which demonstrate significant growth in key sectors. Our strategic initiatives have yielded positive results, and we anticipate continued success."
    """,
    "Witty": """
    **Example:** "You know what's great? Saving money. You know what's not great? Missing this sale. Don't be the person who misses the sale. Your wallet will thank you (and so will we)."
    """,
    "Casual": """
    **Example:** "Hey everyone, just wanted to share a quick update. We've been working on this new feature and it's finally ready. Check it out and let us know what you think!"
    """,
    "Informative": """
    **Example:** "The new Series 8 processor utilizes a 4nm architecture, which allows for a 20% increase in computational efficiency while reducing power consumption by 15% compared to the previous generation."
    """
}

# --- 4. LangChain Configuration (NOW USING LCEL) ---

# Check for API Key
if not API_KEY:
    st.error("OPENAI_API_KEY not found. Please add it to your .env file.")
    st.stop()

# Initialize the LLM (Using gpt-4o-mini for a balance of cost and capability)
llm = ChatOpenAI(
    temperature=0.7,
    model_name="gpt-4o-mini",
    openai_api_key=API_KEY
)

# Initialize the simple output parser
parser = StrOutputParser()

# Chain 1: Idea Generation (LCEL Pipeline: Prompt | LLM | Parser)
idea_template = PromptTemplate(
    input_variables=["topic", "content_type"],
    template="Generate 3 distinct content ideas for a {content_type} about {topic}. Present them as a bulleted list."
)
idea_chain = idea_template | llm | parser # LCEL setup

# Chain 2: Outline (LCEL Pipeline: Prompt | LLM | Parser)
outline_template = PromptTemplate(
    input_variables=["idea"],
    template="Create a detailed, multi-point outline for the following content idea. The outline should be structured to flow logically from introduction to conclusion.\n\nIdea:\n{idea}"
)
outline_chain = outline_template | llm | parser # LCEL setup

# Chain 3: Draft (LCEL Pipeline: Prompt | LLM | Parser)
draft_template = PromptTemplate(
    input_variables=["outline", "tone", "length", "few_shot_example"],
    template="Write a draft that is approximately {length} words long, based on the following outline. \n\nAdopt a {tone} tone. For reference, here is an example of that tone:\n{few_shot_example}\n\nOutline:\n{outline}"
)
draft_chain = draft_template | llm | parser # LCEL setup

# Chain 4: SEO & Tone Refinement (LCEL Pipeline: Prompt | LLM | Parser)
refine_template = PromptTemplate(
    input_variables=["draft", "tone"],
    template="""Refine the following draft.
    1.  Improve clarity and flow.
    2.  Ensure the {tone} tone is consistent throughout.
    3.  Suggest 3-5 relevant SEO keywords.

    Return your response in two parts, separated by '---NOTES---'.
    Part 1: The full, refined content.
    Part 2: Your SEO and refinement notes.

    Draft:\n{draft}
    """
)
refine_chain = refine_template | llm | parser # LCEL setup

# --- 5. Helper Functions ---

def get_download_link(content, filename, text):
    """Generates a link to download content as a file."""
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{filename}" style="text-decoration: none; padding: 6px 12px; background-color: #0068c9; color: white; border-radius: 8px;">{text}</a>'

# --- 6. Streamlit UI ---

st.title("🤖 AI Content Workflow Tool")
st.caption("Generate and refine content using AI-powered prompt chaining.")

# Initialize database
init_db()

# Initialize session state variables
if "idea" not in st.session_state:
    st.session_state.idea = ""
if "outline" not in st.session_state:
    st.session_state.outline = ""
if "draft" not in st.session_state:
    st.session_state.draft = ""
if "final_content" not in st.session_state:
    st.session_state.final_content = ""
if "notes" not in st.session_state:
    st.session_state.notes = ""

# --- Sidebar Controls ---
with st.sidebar:
    st.header("⚙️ Workflow Controls")
    st.markdown("Configure the content generation parameters.")

    content_type = st.selectbox(
        "Content Type",
        ["Blog Post", "Ad Copy", "Social Media Caption"],
        key="content_type"
    )
    
    tone = st.selectbox(
        "Tone / Personality",
        ["Professional", "Witty", "Casual", "Informative"],
        key="tone"
    )
    
    length = st.select_slider(
        "Approximate Length",
        options=["Short (50 words)", "Medium (150 words)", "Long (300 words)"],
        key="length"
    )
    
    st.divider()
    user_topic = st.text_input("Enter your main topic or keyword:", key="user_topic")

# --- Main Workflow Area ---
st.subheader("1. Idea Generation")
st.session_state.idea = st.text_area(
    "Generated Ideas",
    value=st.session_state.idea,
    height=150,
    key="idea_text",
    help="Ideas will appear here. You can edit them before the next step."
)
if st.button("1. Generate Ideas", use_container_width=True, type="primary"):
    if user_topic:
        with st.spinner("Generating ideas..."):
            # LCEL execution using .invoke()
            response = idea_chain.invoke({"topic": user_topic, "content_type": content_type})
            st.session_state.idea = response
            st.rerun() # Rerun to update the text area
    else:
        st.warning("Please enter a topic in the sidebar.")

st.subheader("2. Outline")
st.session_state.outline = st.text_area(
    "Generated Outline",
    value=st.session_state.outline,
    height=200,
    key="outline_text",
    help="The outline will appear here. You can edit it before drafting."
)
if st.button("2. Generate Outline", use_container_width=True, type="primary"):
    if st.session_state.idea:
        with st.spinner("Generating outline..."):
            # We use the (potentially edited) text from the box
            # LCEL execution using .invoke()
            response = outline_chain.invoke({"idea": st.session_state.idea_text})
            st.session_state.outline = response
            st.rerun()
    else:
        st.warning("Please generate an idea first.")

st.subheader("3. Draft Content")
st.session_state.draft = st.text_area(
    "Generated Draft",
    value=st.session_state.draft,
    height=300,
    key="draft_text",
    help="The first draft will appear here. You can edit it before refinement."
)
if st.button("3. Generate Draft", use_container_width=True, type="primary"):
    if st.session_state.outline:
        with st.spinner("Generating draft..."):
            few_shot_example = FEW_SHOT_EXAMPLES.get(st.session_state.tone, "No example available.")
            
            # LCEL execution using .invoke()
            response = draft_chain.invoke({
                "outline": st.session_state.outline_text,
                "tone": st.session_state.tone,
                "length": st.session_state.length.split(" ")[0], # e.g., "Short"
                "few_shot_example": few_shot_example
            })
            st.session_state.draft = response
            st.rerun()
    else:
        st.warning("Please generate an outline first.")

st.subheader("4. SEO & Tone Refinement")
st.session_state.final_content = st.text_area(
    "Refined Content",
    value=st.session_state.final_content,
    height=300,
    key="final_content_text",
    help="The final, polished content will appear here."
)
if st.button("4. Refine Content", use_container_width=True, type="primary"):
    if st.session_state.draft:
        with st.spinner("Refining content..."):
            # LCEL execution using .invoke()
            response = refine_chain.invoke({
                "draft": st.session_state.draft_text,
                "tone": st.session_state.tone
            })
            # Split the output based on the separator
            parts = response.split("---NOTES---")
            st.session_state.final_content = parts[0].strip()
            if len(parts) > 1:
                st.session_state.notes = parts[1].strip()
            else:
                st.session_state.notes = "No notes provided."
            st.rerun()
    else:
        st.warning("Please generate a draft first.")

# Display Refinement Notes
if st.session_state.notes:
    with st.expander("View SEO & Refinement Notes"):
        st.markdown(st.session_state.notes)

st.divider()

# --- 5. Evaluation, Saving, and Exporting ---
st.subheader("5. Evaluate, Save & Export")

if st.session_state.final_content:
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        clarity_score = st.slider("Clarity Score", 1, 5, 3)
    with col2:
        engagement_score = st.slider("Engagement Score", 1, 5, 3)
    
    with col3:
        st.markdown("---") # For vertical alignment
        if st.button("Save to History", use_container_width=True):
            save_content(
                st.session_state.content_type,
                st.session_state.tone,
                st.session_state.length,
                st.session_state.user_topic,
                st.session_state.idea_text,
                st.session_state.outline_text,
                st.session_state.draft_text,
                st.session_state.final_content_text,
                clarity_score,
                engagement_score
            )
    
    st.markdown("---")
    
    # Prepare export content
    export_md_content = f"""
# Topic: {st.session_state.user_topic}
(Type: {st.session_state.content_type}, Tone: {st.session_state.tone}, Length: {st.session_state.length})

## 1. Ideas
{st.session_state.idea_text}

## 2. Outline
{st.session_state.outline_text}

## 3. Draft
{st.session_state.draft_text}

## 4. Final Refined Content
{st.session_state.final_content_text}

## 5. Refinement Notes
{st.session_state.notes}
"""
    
    # Export Buttons
    export_col1, export_col2 = st.columns(2)
    with export_col1:
        st.markdown(
            get_download_link(export_md_content, "ai_content.md", "Export as Markdown (.md)"), 
            unsafe_allow_html=True
        )
    with export_col2:
        st.markdown(
            get_download_link(export_md_content, "ai_content.txt", "Export as Text (.txt)"), 
            unsafe_allow_html=True
        )
else:
    st.info("Generate content to enable saving and exporting.")
