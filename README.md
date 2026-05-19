# 🚀 IntelliSQL: Intelligent SQL Querying with Multi-Agent AI (Next.js & FastAPI)

## 📌 Overview

**IntelliSQL** is a production-grade, AI-powered web application that translates natural language questions into highly optimized SQL statements, validates them against SQL injection, and executes them against a live PostgreSQL database. 

Rather than relying on a single language model, IntelliSQL employs a **split-work multi-agent pipeline** using **Llama 3.3 70B** as a Query Planner and **Qwen 2.5 Coder 32B** as a SQL Developer. This combination ensures highly logical query construction and syntax-perfect SQL compilation.

---

## ⭐ Features

*   **Multi-Agent Split-Work Pipeline**:
    *   **Phase 1: Query Plan** by *Llama 3.3 70B* – Matches schema columns, plans filters, aggregates, and outlines logical steps.
    *   **Phase 2: Final SQL** by *Qwen 2.5 Coder 32B* – Translates the conceptual plan into optimized, syntax-highlighted PostgreSQL.
*   **Dynamic Schema Introspection**: Introspects live database schemas (tables, columns, and relationships) and injects them directly into the LLM system prompts for maximum accuracy.
*   **Confidence Scoring Engine**: Computes a 100-point quality score covering Syntax (sqlparse-checked), Schema matching, and User Intent, with explanations.
*   **Secure Validation Guardrails**: Restricts execution to read-only queries (SELECTs), strips malicious syntax, and prevents statement chaining.
*   **Chronological Query History**: Review past queries, track scores/execution metrics, and reload previous generations back to the console with one click.
*   **Authentication & Security**: Features secure, production-grade JWT-based user authentication.

---

## 🛠 Tech Stack

| Category             | Technology                                                  |
| -------------------- | ----------------------------------------------------------- |
| **Frontend**         | Next.js 14, Tailwind CSS, Shadcn/UI, Axios, Lucide React     |
| **Backend**          | FastAPI (Python), Uvicorn                                   |
| **Database & ORM**   | PostgreSQL (Neon), SQLAlchemy                               |
| **AI LLM API**       | OpenRouter (Qwen 2.5 Coder 32B & Llama 3.3 70B)             |
| **Libraries**        | sqlparse (SQL validation), PyJWT (Auth), date-fns           |

---

## 🏗 Architecture

```
User (Browser) ──> Next.js Console UI 
                         │
                         ▼
                   FastAPI Backend
                         │
        ┌────────────────┴────────────────┐
        ▼                                 ▼
   OpenRouter API                 PostgreSQL Database
 ┌──────────────────────┐        (Secure read-only EXECUTE)
 │ Llama 3.3 (Planner)  │
 │          │           │
 │          ▼           │
 │ Qwen 2.5 (Coder)     │
 └──────────────────────┘
```

---

## ⚙ Installation & Setup

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/intellisql.git
cd intellisql
```

### 2️⃣ Configure Environment Variables

**Backend (`/Project_Files/backend/.env`):**
```env
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
LLM_API_KEY=your_openrouter_api_key
LLM_BASE_URL=https://openrouter.ai/api/v1
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440
CORS_ORIGINS=http://localhost:3000
```

### 3️⃣ Running the Backend (FastAPI)
```bash
cd Project_Files/backend
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
python seed.py # Seed mock tables (students, class grades)
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 4️⃣ Running the Frontend (Next.js)
```bash
cd "../frontend"
npm install
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** in your browser!

---

## 🔐 Security Standards

1.  **Read-Only Database Enforcement**: The execution endpoint strictly forbids modification queries (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `TRUNCATE`, `ALTER`) through middleware validation.
2.  **No Statement Chaining**: Semi-colon chaining is disabled to prevent SQL Injection attempts.
3.  **Authentication**: Protected endpoints require a valid JWT token passed in the Authorization header.
