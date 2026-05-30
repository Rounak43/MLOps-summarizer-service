# AI-Powered Active Recall Material Generator

A production-ready, highly-optimized, and AWS-compatible academic summarizer and study materials generator. It extracts text from PDFs, DOCX files, or raw text blocks, builds concise summarizations using NLP algorithms, and dynamically structures study materials—specifically **active recall Q&A flashcards** and **multiple-choice MCQ quizzes**—without external API keys.

---

## ☁️ Target AWS Cloud Architecture

This repository has been fully refactored and prepared for a seamless migration to **Amazon Web Services (AWS)** using standard cloud services:

```
                      +-----------------------------+
                      |      AWS Amplify            |
                      |  (React Vite Web Hosting)   |
                      +--------------+--------------+
                                     |  HTTP REST
                                     v
+------------------+  +--------------+--------------+  +------------------+
|   AWS Cognito    |  |   Elastic Beanstalk ALB     |  |      AWS S3      |
|  (User Auth Pools)|<-+  (Flask WSGI Backend)      +->|  (Document Buckets)|
+------------------+  +--------------+--------------+  +------------------+
                                     |
                                     v
                      +--------------+--------------+
                      |      AWS RDS                |
                      |  (PostgreSQL Database)      |
                      +-----------------------------+
```

1. **Frontend Hosting (AWS Amplify)**: Decoupled and fully compatible with static frontend builds. Environment configurations load dynamically from variables.
2. **Backend Server (AWS Elastic Beanstalk)**: Run by Gunicorn behind an Application Load Balancer. Ready for fast scaling.
3. **Database Layer (AWS RDS PostgreSQL)**: Relational data mapping backed by SQLAlchemy with auto-schema provisions.
4. **Auth Layer (AWS Cognito User Pools)**: Decoupled via `AuthService` wrappers. Token intercepts authorize API headers.
5. **Storage Layer (Amazon S3)**: Abstracted via `StorageManager` to stream document uploads directly into highly-available buckets.

---

## 📂 Project Structure

```
project-root/
│
├── frontend/                  # React + Vite Web App
│   ├── src/
│   │   ├── api/               # Centralized Axios client & services
│   │   ├── auth/              # Decoupled auth adapters (Firebase & Cognito)
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Layout view pages
│   │   ├── context/           # React State Contexts
│   │   └── main.jsx
│   ├── package.json
│   └── .env.example
│
├── backend/                   # Flask Production Backend (WSGI + Factory)
│   ├── app.py                 # Application Factory setup (create_app)
│   ├── wsgi.py                # WSGI Server Entry Point
│   ├── config/                # Environment-based config class
│   ├── routes/                # Modular blueprint endpoint routers
│   ├── summarization/         # Advanced NLP extraction pipeline
│   ├── flashcards/            # Flashcard generator domain
│   ├── quizzes/               # MCQ generator domain
│   ├── database/              # SQLAlchemy initializations
│   ├── models/                # User and Summary SQL models
│   ├── auth/                  # JWT token verify middlewares
│   ├── storage/               # Local / AWS S3 storage manager
│   ├── uploads/               # Temporary local files folder
│   ├── requirements.txt       # Production dependencies
│   └── .env.example
│
├── docker-compose.yml         # Local orchestration
├── .gitignore
└── README.md
```

---

## 🛠️ Local Development Setup

### Option 1: Multi-Container Docker (Recommended & RDS-ready)

This spins up the frontend web app, the backend Flask server, and a local PostgreSQL database container matching the RDS production engine.

1. **Prerequisites**: Make sure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is running.
2. **Launch Application**:
   ```bash
   docker-compose up --build
   ```
3. **Endpoints**:
   * Frontend Web Portal: [http://localhost:3000](http://localhost:3000)
   * Backend REST APIs: [http://localhost:5000](http://localhost:5000)
   * Local PostgreSQL Port: `5432`

---

### Option 2: Native Dev Environments (Fast Bypasses)

#### Step A: Flask Backend Setup

1. **Navigate to backend**:
   ```bash
   cd backend
   ```
2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # On Windows
   source .venv/bin/activate # On Unix/macOS
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
4. **Create `.env` file**:
   Copy `backend/.env.example` to `backend/.env` and edit configurations.
5. **Start server**:
   ```bash
   python wsgi.py
   ```
   *(Backend starts on [http://localhost:5000](http://localhost:5000))*

#### Step B: React Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```
2. **Install Node modules**:
   ```bash
   npm install
   ```
3. **Create `.env` file**:
   Copy `frontend/.env.example` to `frontend/.env` and edit configurations.
4. **Start Vite developer server**:
   ```bash
   npm run dev
   ```
   *(Frontend starts on [http://localhost:5173](http://localhost:5173))*

---

## 🚀 AWS Production Deployment Playbook

### Step 1: AWS RDS PostgreSQL Provisioning
1. Open the **Amazon RDS console** and create a **PostgreSQL** Database.
2. Select **Free Tier** or Production class. Set your username and master password.
3. Under Connectivity, ensure your security groups allow inbound TCP traffic on port `5432` from your Elastic Beanstalk security group.
4. Copy the connection endpoint. Your production environment variable will be:
   `DATABASE_URL=postgresql://your_master_user:your_master_password@rds-endpoint-url:5432/db_name`

### Step 2: AWS S3 Document Storage
1. Open the **Amazon S3 console** and create a bucket (e.g., `academic-recall-uploads`).
2. Keep public access blocked (safer setup).
3. Attach an IAM execution role to your Elastic Beanstalk instance with `s3:PutObject`, `s3:GetObject`, and `s3:DeleteObject` permissions on this bucket.
4. Update your backend environment variables:
   * `STORAGE_PROVIDER=s3`
   * `S3_BUCKET=academic-recall-uploads`

### Step 3: AWS Cognito Auth Pool Setup
1. Create a **Cognito User Pool** inside the AWS console.
2. Configure Sign-in options (e.g., Email).
3. Under App Integration, create a **Client App** (generate client ID, disable client secret for frontend SPA web apps).
4. Update environment configurations:
   * Frontend: `VITE_AUTH_PROVIDER=cognito`, `VITE_AWS_COGNITO_USER_POOL_ID=us-east-1_xxxxx`, `VITE_AWS_COGNITO_CLIENT_ID=xxxxx`
   * Backend: `AUTH_PROVIDER=cognito`, `COGNITO_USER_POOL_ID=us-east-1_xxxxx`, `COGNITO_CLIENT_ID=xxxxx`

### Step 4: Flask Backend Deployment (AWS Elastic Beanstalk)
1. In the `backend/` folder, run a command to compress files into a zip package (exclude `.venv`, `uploads/`, or local SQLite caches):
   ```bash
   git archive -o backend-deploy.zip HEAD
   ```
2. Go to **AWS Elastic Beanstalk**, choose **Create Application**, and select the **Python platform** (Python 3.10+ recommended).
3. Upload `backend-deploy.zip` as application code.
4. Under **Configuration -> Software**, add your production Environment Properties (`DATABASE_URL`, `STORAGE_PROVIDER`, `AUTH_PROVIDER`, etc.).
5. Deploy. Elastic Beanstalk will automatically execute `wsgi.py` via Gunicorn.

### Step 5: React Frontend Hosting (AWS Amplify)
1. Connect your GitHub repository to **AWS Amplify Console**.
2. Select the `frontend` directory as the build root.
3. Configure the build spec. AWS Amplify automatically builds static files using `npm run build` and hosts them on a fast CDN.
4. In **Amplify App Settings -> Environment Variables**, add your production keys (e.g., `VITE_API_URL` pointing to your Elastic Beanstalk load balancer URL, `VITE_AUTH_PROVIDER`, `VITE_DB_TYPE=postgres`).
5. Trigger a deployment.

---

## 🔒 Security Best Practices
* **Secret Isolation**: Never commit active credentials, access tokens, or certificate keys to source control. Always copy the `.env.example` file and manage real variables via the OS environment or AWS Parameter Store.
* **IAM Role Policies**: Adhere strictly to the principle of least privilege. AWS EC2 server instances should only have access to their designated RDS cluster and specific S3 buckets.
