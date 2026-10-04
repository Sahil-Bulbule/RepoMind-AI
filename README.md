# 🐙 Ask My GitHub
  
> **Understand any codebase. Ask questions. Get answers from the source.**   
 
Ask My GitHub is an AI-powered GitHub repository explorer that lets users explore repositories and ask natural-language questions about their codebase.

Instead of manually searching through files, users can select a repository and ask questions about its architecture, files, technologies, functions, implementation details, and more.

The application uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant repository context before generating an answer with an LLM.

---

## ✨ Features
  
- 🔎 **GitHub Repository Explorer**
  - Fetch and explore repositories using the GitHub API.
  - View repository details, technologies, files and metadata.

- 💬 **AI Repository Chat**
  - Ask natural-language questions about a selected repository.
  - Get answers based on the repository's actual code and files.

- 🧠 **RAG-Powered Code Understanding**
  - Repository files are processed, chunked and converted into embeddings.
  - Relevant code chunks are retrieved for each user query.

- 📚 **Repository-Grounded AI**
  - Responses are generated using relevant repository context to keep answers focused on the selected codebase.

- 🧩 **Smart Response UI**
  - Structured answers
  - Code blocks
  - File references
  - Technology badges
  - Steps, summaries, tips and warnings

- 🔐 **User Isolation**
  - Repository indexing and chat context are separated to avoid mixing data between users/repositories.

- ⚡ **FastAPI Backend**
  - Clean API architecture with separate routes and services.

---

## 👨‍💻 Built By

### **Sahil Bulbule**

**AI/ML Engineer • Generative AI Developer • RAG & Agentic AI Builder**

I'm passionate about building AI-powered applications that solve real-world problems using Machine Learning, Deep Learning, NLP, Generative AI, LLMs, RAG and Agentic AI.

🔗 **GitHub:** [Sahil-Bulbule](https://github.com/Sahil-Bulbule)

---

### ⭐ Support

If you found **Ask My GitHub** useful, consider giving the repository a ⭐

**Built with by Sahil**

## 🏗️ How It Works

```text
                    ┌─────────────────────┐
                    │      GitHub API     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Repository Service │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    File Filtering   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Chunking       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     Embeddings      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      ChromaDB       │
                    │    Vector Store     │
                    └──────────┬──────────┘
                               │
                         User Question
                               │
                               ▼
                    ┌─────────────────────┐
                    │      Retriever      │
                    └──────────┬──────────┘
                               │
                    Relevant Code Context
                               │
                               ▼
                    ┌─────────────────────┐
                    │       Groq LLM      │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │     AI Response     │
                    └─────────────────────┘

---
