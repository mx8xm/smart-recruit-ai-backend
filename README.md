
# 📂 **ملفات التوثيق والإعداد**

## **ملف 1: `README.md`**

# 🚀 Smart Recruit AI - Backend

AI-Powered CV Filtering System for HR Recruitment using FastAPI

## 📋 Features

- ✅ **JWT Authentication** - Secure user registration and login
- 📝 **Job Management** - Create and manage job postings
- 📄 **Bulk CV Upload** - Upload up to 1000 CVs simultaneously
- 🤖 **AI Processing**:
  - Text extraction from PDF/DOCX files (Docling)
  - Candidate name extraction (mDeBERTa)
  - Semantic CV matching (Sentence Transformers)
- ⚡ **Background Processing** - Non-blocking CV analysis
- 🎯 **Smart Ranking** - Automatic candidate scoring
- 🗄️ **PostgreSQL Database** - Production-ready async database

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.109+
- **Database**: PostgreSQL + SQLAlchemy (Async)
- **Authentication**: JWT (python-jose)
- **AI Models**:
  - `timpal0l/mdeberta-v3-base-squad2` (Name Extraction)
  - `paraphrase-multilingual-MiniLM-L12-v2` (Semantic Matching)
  - `Docling` (PDF/DOCX Text Extraction)

## 📦 Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd smart-recruit-ai-backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
python -m app.ai.model_loader

# source venv/bin/activate  # Linux/Mac
```
```bash

(venv) C:\Users\Max\Desktop\EST S4\pfe\smart-recruit-ai-backend-main - Copy>python -m app.ai.model_loader
2026-03-06 10:06:35.287648: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set 
the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
2026-03-06 10:06:38.246736: I tensorflow/core/util/port.cc:153] oneDNN custom operations are on. You may see slightly different numerical results due to floating-point round-off errors from different computation orders. To turn them off, set 
the environment variable `TF_ENABLE_ONEDNN_OPTS=0`.
WARNING:tensorflow:From C:\Users\Max\AppData\Local\Programs\Python\Python310\lib\site-packages\tf_keras\src\losses.py:2976: The name tf.losses.sparse_softmax_cross_entropy is deprecated. Please use tf.compat.v1.losses.sparse_softmax_cross_entropy instead.

C:\Users\Max\AppData\Local\Programs\Python\Python310\lib\runpy.py:126: RuntimeWarning: 'app.ai.model_loader' found in sys.modules after import of package 'app.ai', but prior to execution of 'app.ai.model_loader'; this may result in unpredictable behaviour
  warn(RuntimeWarning(msg))
C:\Users\Max\AppData\Local\Programs\Python\Python310\lib\site-packages\huggingface_hub\file_download.py:949: FutureWarning: `resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`.
  warnings.warn(
model.safetensors: 100%|███████████████████████████████████████████████████████████| 1.16G/1.16G [09:29<00:00, 2.03MB/s]
pytorch_model.bin: 100%|███████████████████████████████████████████████████████████| 1.16G/1.16G [09:35<00:00, 2.01MB/s]
Fetching 5 files: 100%|██████████████████████████████████████████████████████████████████| 5/5 [09:36<00:00, 115.33s/it]
tokenizer_config.json: 100%|█████████████████████████████████████████████████████████████████| 52.0/52.0 [00:00<?, ?B/s]
config.json: 100%|██████████████████████████████████████████████████████████████████████| 579/579 [00:00<00:00, 495kB/s]
spm.model: 100%|███████████████████████████████████████████████████████████████████| 4.31M/4.31M [00:01<00:00, 2.28MB/s]
C:\Users\Max\AppData\Local\Programs\Python\Python310\lib\site-packages\transformers\convert_slow_tokenizer.py:566: UserWarning: The sentencepiece tokenizer that you are converting to a fast tokenizer uses the byte fallback option which is not implemented in the fast tokenizers. In practice this means that the fast version of the tokenizer can produce unknown tokens whereas the sentencepiece version would have converted these unknown tokens into a sequence of byte tokens matching 
the original piece of text.
  warnings.warn(

(venv) C:\Users\Max\Desktop\EST S4\pfe\smart-recruit-ai-backend-main - Copy>python run.py
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

Install PostgreSQL and create database:

```sql
CREATE DATABASE smart_recruit_db;
```

### 5. Configure Environment

Copy `.env.example` to `.env` and update:

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

Edit `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://postgres:YOUR_PASSWORD@localhost:5432/smart_recruit_db
SECRET_KEY=your-super-secret-key-min-32-characters
```

### 6. Run Migrations

```bash
alembic upgrade head
```

### 7. Start Server

```bash
python run.py
```

Server will start at: **http://localhost:8000**

## 📖 API Documentation

Once running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔑 API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new HR user
- `POST /api/v1/auth/login` - Login and get JWT token
- `GET /api/v1/auth/me` - Get current user info

### Jobs
- `POST /api/v1/jobs/` - Create job posting
- `GET /api/v1/jobs/` - List all my jobs
- `GET /api/v1/jobs/{job_id}` - Get job details with applications
- `PUT /api/v1/jobs/{job_id}` - Update job
- `DELETE /api/v1/jobs/{job_id}` - Delete job

### Applications
- `POST /api/v1/applications/{job_id}/upload` - Upload CVs (bulk)
- `GET /api/v1/applications/{job_id}/applications` - List all applications
- `GET /api/v1/applications/application/{id}` - Get application details

## 🧪 Testing

```bash
pytest tests/
```

## 📁 Project Structure

```
smart-recruit-ai-backend/
├── app/
│   ├── ai/              # AI processing modules
│   ├── api/             # API endpoints
│   ├── core/            # Config & security
│   ├── models/          # Database models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── utils/           # Helper functions
├── alembic/             # Database migrations
├── uploads/             # Uploaded CV files
└── tests/               # Unit tests
```

## 🤝 Contributing

Contributions welcome! Please open an issue or PR.

## 📄 License

MIT License

***

## 🚀 **خطوات التشغيل النهائية:**

### **1. تثبيت PostgreSQL**
```bash
# قم بتثبيت PostgreSQL من:
# https://www.postgresql.org/download/windows/
```

### **2. إنشاء قاعدة البيانات**
```sql
-- افتح pgAdmin أو psql
CREATE DATABASE smart_recruit_db;
```

### **3. تفعيل البيئة الافتراضية**
```cmd
cd smart-recruit-ai-backend
venv\Scripts\activate
```

### **4. تشغيل السيرفر**
```cmd
python run.py
```

### **5. افتح المتصفح**
```
http://localhost:8000/docs
```

for me how creat requirements.txt stable : pip freeze > requirements.txt

***

cd "C:\Users\Max\Desktop\EST S4\pfe\mx8xm\smart-recruit-ai-backend"
venv\Scripts\activate
python download_models.py
python run.py
