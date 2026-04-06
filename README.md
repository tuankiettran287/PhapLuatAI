# V-Legal Bot - RAG Chatbot Pháp Luật Việt Nam

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Giới thiệu

V-Legal Bot là hệ thống trợ lý ảo thông minh chuyên biệt trong lĩnh vực pháp luật Việt Nam. Sử dụng kiến trúc **RAG (Retrieval-Augmented Generation)** để truy xuất thông tin chính xác từ kho dữ liệu pháp lý và tạo câu trả lời đáng tin cậy.

### Tính năng chính

- 💬 **Hỏi đáp pháp luật**: Trả lời câu hỏi dựa trên văn bản pháp luật thực tế
- 📚 **Trích dẫn nguồn**: Mọi câu trả lời đều kèm theo trích dẫn Điều, Khoản cụ thể
- 🔍 **Tìm kiếm thông minh**: Tìm kiếm ngữ nghĩa trong kho văn bản pháp luật
- 📁 **Quản lý văn bản**: Upload và quản lý các văn bản pháp luật
- 📊 **Đánh giá chất lượng**: Tích hợp Evidently AI để benchmark và giám sát

## 🛠️ Công nghệ

| Component | Technology |
|-----------|------------|
| Backend | Python + FastAPI |
| RAG Framework | LangChain |
| Vector Database | ChromaDB |
| LLM | Google Gemini 1.5 Pro |
| Embeddings | multilingual-e5-base |
| Evaluation | Evidently AI |

## 📂 Cấu trúc Project

```
PhapLuatAI/
├── backend/                 # Backend API (FastAPI)
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── services/
│   │   └── evaluation/
│   ├── scripts/
│   ├── tests/
│   ├── requirements.txt
│   └── .env.example
├── frontend/                # Frontend UI (Next.js)
│   ├── src/
│   │   ├── app/
│   │   ├── components/
│   │   └── services/
│   └── package.json
├── Data/                    # Văn bản pháp luật (.docx)
├── vectordb/                # ChromaDB storage
└── README.md
```

## 🚀 Cài đặt

### 1. Clone và tạo môi trường

```bash
cd PhapLuatAI/backend
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

Copy file `.env.example` thành `.env` và cập nhật API key:

```bash
copy .env.example .env
```

Chỉnh sửa `.env`:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Nạp dữ liệu

Đặt các file văn bản pháp luật (.docx) vào thư mục `Data/`, sau đó chạy:

```bash
python scripts/ingest_data.py
```

### 5. Chạy server

```bash
python -m app.main
```

## 📖 Sử dụng API

### Chat endpoint

```bash
curl -X POST "http://localhost:8000/chat/" \
  -H "Content-Type: application/json" \
  -d '{"question": "Quyền sở hữu tài sản được quy định như thế nào?"}'
```

### Tìm kiếm văn bản

```bash
curl "http://localhost:8000/chat/search?query=quyền+sở+hữu&top_k=5"
```

### Xem danh sách văn bản

```bash
curl "http://localhost:8000/admin/documents"
```

### Upload văn bản mới

```bash
curl -X POST "http://localhost:8000/admin/upload" \
  -F "file=@Luat_Moi.docx" \
  -F "status=Còn hiệu lực"
```

## 📊 API Documentation

Truy cập Swagger UI: http://localhost:8000/docs

## 🧪 Chạy Benchmark

```bash
# Tạo bộ test mẫu
python scripts/evidently_report.py --create-sample

# Chạy benchmark
python scripts/evidently_report.py --gold-dataset ./benchmark_results/gold_dataset.json

# Quick test
python scripts/evidently_report.py --quick-test "Thời hiệu khởi kiện là bao lâu?"
```

## 📝 Workflow cho Developer

1. **Chuẩn bị**: Thu thập văn bản pháp luật dạng .docx
2. **Upload**: Sử dụng Admin API hoặc đặt vào thư mục `Data/`
3. **Ingest**: Chạy `python scripts/ingest_data.py`
4. **Benchmark**: Chạy `python scripts/evidently_report.py`
5. **Deploy**: Triển khai sau khi pass benchmark

## ⚠️ Lưu ý

- Chatbot **CHỈ** trả lời dựa trên dữ liệu đã được nạp
- Không thay thế tư vấn pháp lý chuyên nghiệp
- Cần cập nhật văn bản khi có thay đổi pháp luật

## 🖥️ Frontend UI

Project bao gồm giao diện người dùng Next.js với các tính năng:

- 💬 **Chat**: Giao diện chat thân thiện với gợi ý câu hỏi
- 🔍 **Tìm kiếm**: Tìm kiếm semantic trong văn bản pháp luật  
- 📁 **Quản lý**: Upload/xóa văn bản, xem thống kê
- 📊 **Dashboard**: Biểu đồ phân tích dữ liệu

### Chạy Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:3000
Backend: http://localhost:8000

## 📄 License

MIT License - Xem file LICENSE để biết thêm chi tiết.

## 🤝 Đóng góp

Mọi đóng góp đều được hoan nghênh! Vui lòng tạo Issue hoặc Pull Request.
