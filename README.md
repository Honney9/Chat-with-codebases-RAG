# 💬 Chat with Your Codebase (RAG)

Chat with any **local or GitHub codebase** using AI.  
This project uses **Retrieval-Augmented Generation (RAG)** to understand your repository and answer questions with **accurate code references and sources**.

Built with **Streamlit**, **LangChain**, **Vector Search**, and **LLMs**.

---

## ✨ Features

- 📁 Load **local repositories** or **GitHub repositories**
- 🔍 Intelligent **code search & retrieval**
- 🧠 Context-aware answers using **RAG**
- 📌 Exact **source citations** (file + line numbers)
- 🧾 Built-in **file explorer & code preview**
- 💬 Chat-style UI (like ChatGPT, but for your repo)
- ⚡ Fast re-indexing with caching
- 🎯 Supports **JS / TS / JSX / TSX / Python / Java / Go**

---

## 🖼️ UI Overview

**Left Panel**
- File Explorer
- Code Preview (click sources → jump to file)

**Right Panel**
- Chat messages
- Sources shown *per response*
- Persistent chat history

---

## 🧠 How It Works

1. Repository is loaded (local or GitHub)
2. Files are chunked intelligently
3. Chunks are embedded and stored in a vector database
4. User query retrieves relevant code snippets
5. Retrieved code is re-ranked
6. LLM generates an answer **grounded in your code**
7. Sources are attached to the response

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: OpenAI / Local LLM (configurable)
- **Embeddings**: Sentence Transformers
- **Vector Store**: MongoDB / Custom Vector Store
- **RAG Framework**: LangChain
- **Git**: GitPython

---

## 📦 Supported File Types

### Code
- `.py`
- `.js`
- `.jsx`
- `.ts`
- `.tsx`
- `.java`
- `.go`

### Docs (indexed, not previewed)
- `.md`
- `.json`
- `.yaml`
- `.yml`

---