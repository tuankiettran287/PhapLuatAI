# V-Legal Bot Backend

Backend API cho V-Legal Bot - Trợ lý Pháp luật Việt Nam.

## Tech Stack

- **Framework**: FastAPI
- **RAG**: LangChain
- **Vector DB**: ChromaDB
- **LLM**: Google Gemini 1.5 Pro
- **Embeddings**: multilingual-e5-base
- **Evaluation**: Evidently AI

## Cài đặt

### 1. Tạo virtual environment

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình

Copy file `.env.example` thành `.env`:

```bash
copy .env.example .env
```

Cập nhật `GEMINI_API_KEY` trong file `.env`.

### 4. Nạp dữ liệu

```bash
python scripts/ingest_data.py
```

### 5. Chạy server

```bash
python -m app.main
```

Hoặc:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API sẽ chạy tại: http://localhost:8000

## Cấu trúc

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Settings
│   ├── api/routes/
│   │   ├── chat.py          # Chat endpoints
│   │   └── admin.py         # Admin endpoints
│   ├── core/
│   │   ├── rag_engine.py    # RAG pipeline
│   │   ├── embeddings.py    # Embedding service
│   │   ├── vector_store.py  # ChromaDB
│   │   ├── llm.py           # Gemini integration
│   │   └── prompts.py       # System prompts
│   ├── services/
│   │   ├── document_processor.py
│   │   ├── metadata_extractor.py
│   │   └── legal_chunker.py
│   └── evaluation/
│       ├── benchmark.py
│       └── evidently_monitor.py
├── scripts/
│   ├── ingest_data.py
│   └── evidently_report.py
├── tests/
├── requirements.txt
└── .env.example
```

## API Endpoints

### Chat
- `POST /chat/` - Đặt câu hỏi pháp luật
- `POST /chat/search` - Tìm kiếm văn bản

### Admin
- `GET /admin/documents` - Danh sách văn bản
- `GET /admin/stats` - Thống kê hệ thống
- `POST /admin/upload` - Upload văn bản mới
- `DELETE /admin/documents/{filename}` - Xóa văn bản

## API Documentation

Swagger UI: http://localhost:8000/docs
