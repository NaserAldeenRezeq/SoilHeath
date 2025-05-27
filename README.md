# 🌱 Soil Health AI Assistant

> **Your AI-Powered Soil Intelligence Lab**
> A full-stack LLM-powered system for intelligent document analysis, real-time chat, secure access, and beautiful dashboards — all tailored for soil health insights.

---

## 🚀 Features at a Glance

* ✅ **Secure Login** with JWT Authentication
* 📂 **Upload PDFs & `.txt` Files**
* ✂️ **Text Chunking** for Better Embedding
* 🧠 **Generate Embeddings** Using Integrated Models
* 💬 **Interactive Chatbot** for Soil-Related Queries
* ⚙️ **LLM Configuration Panel** (Model, Quantization, Temp)
* 🔄 **Live RAG Endpoint** for Real-Time Retrieval-Augmented Generation
* 📈 **Monitoring Dashboard** with Logs & System Stats
* 🖥️ **Full Web Dashboard** – Control Everything in One Place

---

## 🧠 Architecture Overview

```
Frontend (HTML, CSS, JS via Jinja2 Templates)
            │
            ▼
     🚀 FastAPI Backend
            │
 ┌──────────┴──────────┐
 │     SQLite DB       │
 │     Qdrant DB       │
 └──────────┬──────────┘
            ▼
     🧬 Embedding Models
            │
            ▼
      🤖 LLM Chatbot
```

---

## 🖼️ Dashboard Tour

A visual walkthrough of each step in your soil health pipeline — from login to chat:

| Home (Login)                                                                                       | Upload                                                                                               |
| -------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| ![Login](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/login.png) | ![Upload](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/upload.png) |

| Chunking                                                                                                   | Embeddings                                                                                                        |
| ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| ![Chunking](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/docChunker.png) | ![Embeddings](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/embeddingchunks.png) |

| LLM Settings                                                                                                     | Chat                                                                                                 |
| ---------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------- |
| ![LLM Settings](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/llmsSettings.png) | ![Chat](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/liveChat.png) |

| Live RAG                                                                                                  | Monitoring                                                                                                         |
| --------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| ![Live RAG](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/live_rage.png) | ![Monitoring](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/monitroignsLoges.png) |

---

## 🔍 FastAPI Interactive Docs

View and test all your backend endpoints in real time:

| API Docs                                                                                                       |
| -------------------------------------------------------------------------------------------------------------- |
| ![FastAPI 1](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/fastAPIDocs-1.png) |
| ![FastAPI 2](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/fastAPIDocs-2.png) |
| ![FastAPI 3](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/fastAPIDocs-3.png) |
| ![FastAPI 4](https://github.com/AlRashid-AlKiswane/Naseer/blob/main/assets/images/fastAPIDocs-4.png) |

---

## 🧪 Tech Stack

| Layer        | Tech Used                        |
| ------------ | -------------------------------- |
| **Backend**  | FastAPI, SQLite, Qdrant          |
| **Frontend** | Jinja2, HTML, CSS, JavaScript    |
| **Models**   | HuggingFace, Local LLMs          |
| **Auth**     | JWT, Cookie Session              |
| **Deploy**   | Docker-ready                     |
| **Logging**  | Custom Logger + Resource Monitor |

---

## 📁 Project Structure

```bash
soil-health-ai/
├── assets/                  # Static files and UI images
├── database/                # DB initialization scripts
├── src/
│   ├── controllers/         # Core business logic
│   ├── db_vector/           # Qdrant vector DB interface
│   ├── dbs/                 # SQLite setup and queries
│   ├── embedding/           # Embedding model logic
│   ├── enums/               # Enum definitions
│   ├── helpers/             # Configs and utilities
│   ├── llm/                 # LLM model loading and inference
│   ├── login/               # Auth logic (JWT + sessions)
│   ├── logs/                # Logging and monitoring
│   ├── prompt/              # Prompt templates
│   ├── routes/              # FastAPI routes
│   ├── schemes/             # Pydantic schemas
│   ├── web/                 # HTML/CSS frontend (Jinja2)
│   ├── __init__.py
│   └── __main__.py          # App entry point
├── .env.example             # Sample environment file
├── requirements.txt         # Python dependencies
└── README.md                # You’re reading it.
```

---

## 🛠️ Getting Started

### 1. Installation

```bash
# Clone the repository
git clone 
cd Naseer

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env variables
cp .env.example .env
```

### 2. Run the App

```bash
python -m src
```

Visit your browser:
🌐 [http://localhost:8000](http://localhost:8000)

---

## 🔐 Default Login

> You can change this later in the login module.

* **Username**: `admin`
* **Password**: `admin`

---

## 🗃️ Image Assets Directory

All UI screenshots are stored here:

🔗 [assets/images/](https://github.com/AlRashid-AlKiswane/Naseer/tree/main/assets/images)

| Filename               |
| ---------------------- |
| `docChunker.png`       |
| `embeddingchunks.png`  |
| `fastAPIDocs-1.png`    |
| `fastAPIDocs-2.png`    |
| `fastAPIDocs-3.png`    |
| `fastAPIDocs-4.png`    |
| `liveChat.png`         |
| `live_rage.png`        |
| `llmsSettings.png`     |
| `login.png`            |
| `main.png`             |
| `monitroignsLoges.png` |
| `test.png`             |
| `upload.png`           |

---

## 🌍 Upcoming Features

* 🌐 **Arabic & Multilingual Support**
* 🧠 **LLM Fine-Tuning via Dashboard**
* 💾 **Downloadable Chat Transcripts**
* 📊 **Soil Health Reports**
* 🌤️ **Weather API for Field Conditions**

---

## 🪪 License

This project is open-source under the **[MIT License](LICENSE)**.

---

## 👨‍🔬 Author

**Naseer**

> “Coding with the precision of a surgeon and the soul of a poet.”
> Made with ☕, 🌙 nights, and Manjaro Linux.
