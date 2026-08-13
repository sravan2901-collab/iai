# 🤖 AksharAI — Open-Source Local AI Model Setup Guide (Ollama)

AksharAI includes a hybrid AI learning engine. It supports local open-source Large Language Models (LLMs) via **[Ollama](https://ollama.com)** for dynamic lesson generation and personalized learning roadmaps, while maintaining a 100% resilient rule-based fallback when offline.

---

## ⚡ Quick Start Instructions

### 1. Install Ollama (Free & Open-Source)
* **Windows / macOS / Linux**: Download and run the installer from **[https://ollama.com/download](https://ollama.com/download)**.

### 2. Pull an Open-Source Model
Open your terminal or PowerShell and pull a lightweight open-weight model:
```bash
# Recommended lightweight model for fast local inference (Llama 3.1 8B):
ollama pull llama3.1

# Alternative fast models:
ollama pull mistral
ollama pull gemma2:2b
```

### 3. Run Ollama Local Service
Start the local server daemon:
```bash
ollama serve
```
*(Default endpoint listens at `http://localhost:11434`)*.

---

## ⚙️ Environment Configuration (`backend/.env`)

Ensure the following variables are defined in your `backend/.env` file:

```env
# Enable AI Local Generation Engine
AI_LEARNING_ENGINE_ENABLED=True

# Ollama Endpoint Configuration
OLLAMA_BASE_URL="http://localhost:11434"
OLLAMA_MODEL="llama3.1"
OLLAMA_TIMEOUT_SECONDS=15
```

---

## 🛡️ Hybrid Fallback Architecture

| Scenario | Behavior | Performance |
| :--- | :--- | :--- |
| **Ollama Daemon Running** | Dynamic AI lesson planning & multilingual content generation (`ai_content_service.py`) | ~1-3s Local Inference |
| **Ollama Service Stopped / Offline** | Automatic, seamless fallback to deterministic DB repository selection (`learning_path_engine.py`) | ~10ms Instant Fallback |
| **Model Timeout / Bad JSON** | Instant fallback to pre-seeded literacy curriculum modules | ~10ms Instant Fallback |

---

## 🎓 College & Evaluator Demo Notes
* **Zero Billing Risk**: Ollama runs 100% locally on your machine with **no cloud API keys or credit card requirements**.
* **Cloud API Interchangeability**: If cloud evaluators require hosted endpoints (e.g. Groq, Together AI, Anyscale), the JSON contract in `ai_content_service.py` is identical — simply update the HTTP endpoint URL.
