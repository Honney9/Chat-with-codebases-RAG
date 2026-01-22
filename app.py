import streamlit as st
import time
from dotenv import load_dotenv

load_dotenv()

# -------------------------
# Imports (UNCHANGED)
# -------------------------
from ingest.load_repo import load_repository
from parse.apply_chunking import apply_code_chunking
from indexing.repo_utils import get_repo_id
from indexing.git_utils import get_repo_commit_hash
from indexing.chunk_id import make_chunk_id
from indexing.index_documents import index_documents
from indexing.repo_metadata import (
    is_repo_already_indexed,
    mark_repo_as_indexed
)
from indexing.mongo_vector_store import delete_repo_embeddings
from retrieval.retriever import retrieve_documents
from reranking.reranker import rerank_documents
from reranking.context_builder import build_context
from llm.query_builder import build_llm_input
from llm.llm_client import generate_answer

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="Chat with Your Codebase",
    page_icon="💬",
    layout="wide"
)

# -------------------------
# Session State
# -------------------------
if "repo_loaded" not in st.session_state:
    st.session_state.repo_loaded = False

if "messages" not in st.session_state:
    st.session_state.messages = []

if "repo_id" not in st.session_state:
    st.session_state.repo_id = None

if "all_chunks" not in st.session_state:
    st.session_state.all_chunks = []

if "selected_file" not in st.session_state:
    st.session_state.selected_file = None

if "last_sources" not in st.session_state:
    st.session_state.last_sources = []

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False

def detect_language(path: str) -> str:
    ext = path.split(".")[-1].lower()
    return {
        "js": "javascript",
        "jsx": "javascript",   # ✅ FIX
        "ts": "typescript",
        "tsx": "typescript",
        "py": "python",
        "html": "html",
        "css": "css",
        "json": "json",
    }.get(ext, "text")

CODE_EXTS = (".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go")
DOC_EXTS = (".md", ".json", ".yaml", ".yml")


# -------------------------
# Header
# -------------------------
# ================================
# HERO SECTION
# ================================
st.markdown(
    """
    <div style="
        padding: 3rem 2rem;
        border-radius: 16px;
        background: linear-gradient(135deg, #0f172a, #020617);
        border: 1px solid #1e293b;
    ">
        <h1 style="font-size: 3rem; margin-bottom: 0.5rem;">
            💬 Chat with Your Codebase
        </h1>
        <p style="font-size: 1.2rem; color: #cbd5f5;">
            Ask natural language questions and instantly understand any repository.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

st.info("🚀 This app runs on Streamlit Cloud and supports **public GitHub repositories only**.")

st.markdown("<br>", unsafe_allow_html=True)

cols = st.columns(3)

with cols[0]:
    st.markdown(
        """
        ### 📁 Explore
        Browse files, preview code, and navigate your repo structure effortlessly.
        """
    )

with cols[1]:
    st.markdown(
        """
        ### 🧠 Ask Anything
        Ask questions like *“Where is authentication handled?”* or  
        *“Explain this React component.”*
        """
    )

with cols[2]:
    st.markdown(
        """
        ### 📌 Grounded Answers
        Every response is backed by **real code snippets and sources**.
        """
    )


# -------------------------
# Sidebar – Repository Loader
# -------------------------
with st.sidebar:
    st.header("📁 Repository Settings")

    repo_path = st.text_input(
        "GitHub Repository URL",
        placeholder="https://github.com/username/repository"
    )


    force_reindex = st.checkbox("🔄 Rebuild repository index")

    if st.button("🚀 Load Repository"):
        if not repo_path.strip():
            st.error("Please provide a GitHub repository URL.")
            st.stop()

        if not repo_path.startswith("https://github.com/"):
            st.error("Only public GitHub repositories are supported.")
            st.stop()


        with st.spinner("Loading repository..."):
            docs, local_repo_path = load_repository(repo_path)

        repo_id = get_repo_id(repo_path)
        commit_hash = get_repo_commit_hash(local_repo_path)

        chunks = apply_code_chunking(docs)

        for chunk in chunks:
            chunk.metadata["repo_id"] = repo_id
            chunk.metadata["commit_hash"] = commit_hash
            chunk.metadata["chunk_id"] = make_chunk_id(
                repo_id,
                chunk.metadata["file_path"],
                chunk.metadata.get("start_line"),
                chunk.metadata.get("end_line"),
                commit_hash
            )

        if force_reindex:
            delete_repo_embeddings(repo_id, commit_hash)

        if force_reindex or not is_repo_already_indexed(repo_id, commit_hash):
            with st.spinner("Indexing documents..."):
                index_documents(chunks, repo_id=repo_id, force=True)
                mark_repo_as_indexed(repo_id, commit_hash)
            st.success("✅ Repository indexed")
        else:
            st.success("✅ Repository already indexed")

        st.session_state.repo_loaded = True
        st.session_state.repo_id = repo_id
        st.session_state.all_chunks = chunks
        st.session_state.selected_file = None

LEFT_PANEL_HEIGHT = 630
RIGHT_PANEL_HEIGHT = 650

TOP_LEFT_HEIGHT = LEFT_PANEL_HEIGHT // 2
BOTTOM_LEFT_HEIGHT = LEFT_PANEL_HEIGHT // 2

TOP_RIGHT_HEIGHT = 640
BOTTOM_RIGHT_HEIGHT = 60

# -------------------------
# Main Layout
# -------------------------
if not st.session_state.repo_loaded:
    st.markdown(
        """
        <div style="
            margin-top: 2rem;
            padding: 1.5rem;
            border-radius: 12px;
            background-color: #020617;
            border: 1px dashed #334155;
        ">
            <h3>🚀 Get Started</h3>
            <p style="color: #94a3b8;">
                Paste a public GitHub repository URL from the sidebar to begin chatting
                with your codebase.
            </p>
            <ul style="color: #94a3b8;">
                <li>Understand unfamiliar code</li>
                <li>Find where logic lives</li>
                <li>Debug faster with context</li>
            </ul>
            <p>👈 Use the sidebar to load a repository</p>
        </div>
        """,
        unsafe_allow_html=True
    )


else:
    left_col, right_col = st.columns([1, 2], gap="small")

    # =====================================================
    # LEFT COLUMN — FILE EXPLORER + CODE PREVIEW
    # =====================================================
    with left_col:
        st.subheader("📁 File Explorer")

        with st.container(height=TOP_LEFT_HEIGHT):

            code_files = sorted({
                c.metadata["file_path"]
                for c in st.session_state.all_chunks
                if c.metadata["file_path"].endswith(CODE_EXTS)
            })

            doc_files = sorted({
                c.metadata["file_path"]
                for c in st.session_state.all_chunks
                if c.metadata["file_path"].endswith(DOC_EXTS)
            })

            with st.expander("🧠 Code Files", expanded=True):
                selected_code = st.radio(
                    "Code",
                    code_files,
                    label_visibility="collapsed"
                )

            with st.expander("📄 Docs & Config", expanded=False):
                selected_doc = st.radio(
                    "Docs",
                    doc_files,
                    label_visibility="collapsed"
                )
            st.session_state.selected_file = selected_code or selected_doc


        with st.container(height=BOTTOM_LEFT_HEIGHT):
            if st.session_state.selected_file:
                file_chunks = [
                    c for c in st.session_state.all_chunks
                    if c.metadata["file_path"] == st.session_state.selected_file
                    and c.metadata["file_path"].endswith(CODE_EXTS)
                ]

                if file_chunks:
                    full_code = "\n".join(c.page_content for c in file_chunks)

                    st.code(
                        full_code,
                        language=detect_language(st.session_state.selected_file)
                    )


    # =====================================================
    # RIGHT COLUMN — CHAT + SOURCES
    # =====================================================
    # ---------- Handle Chat Submission ----------
    
    with right_col:
        st.subheader("💬 Chat")

        # ---------- Chat messages + sources ----------
        with st.container(height=TOP_RIGHT_HEIGHT):
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

                    if msg["role"] == "assistant" and msg.get("sources"):
                        st.divider()
                        st.subheader("📌 Sources")
                        seen = set()
                        for doc in msg["sources"]:
                            path = doc.metadata.get("file_path")
                            if path in seen:
                                continue
                            seen.add(path)

                            label = f"{path} (Lines {doc.metadata.get('start_line')}-{doc.metadata.get('end_line')})"
                            with st.expander(label):
                                st.code(
                                    doc.page_content,
                                    language=detect_language(path)  # ✅ instead of split(".")[-1]
                                )


        # ---------- Chat input (NO height) ----------
        user_query = st.chat_input(
            "Ask about the codebase...",
            disabled=st.session_state.is_generating
        )

        if user_query and not st.session_state.is_generating:
            st.session_state.is_generating = True

            st.session_state.messages.append({
                "role": "user",
                "content": user_query
            })

            # Placeholder assistant message
            st.session_state.messages.append({
                "role": "assistant",
                "content": "🔍 Searching codebase...",
                "sources": []
            })

            st.rerun()

        if st.session_state.is_generating:
            last_user_msg = next(
                msg["content"]
                for msg in reversed(st.session_state.messages)
                if msg["role"] == "user"
            )

            retrieved = retrieve_documents(
                last_user_msg,
                repo_id=st.session_state.repo_id,
                k=8
            )

            reranked = rerank_documents(last_user_msg, retrieved)[:6]
            context = build_context(reranked)
            llm_input = build_llm_input(last_user_msg, context)
            answer = generate_answer(llm_input)

            # Replace loading placeholder
            st.session_state.messages[-1]["content"] = answer
            st.session_state.messages[-1]["sources"] = reranked
            st.session_state.is_generating = False

            st.rerun()