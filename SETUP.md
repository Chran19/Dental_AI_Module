# Dental AI Module - Project Setup Guide

Complete guide for setting up and running the Dental AI Module project (both backend and frontend).

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Project Structure](#project-structure)
3. [Quick Start (Local Development)](#quick-start-local-development)
4. [Backend Setup](#backend-setup)
5. [Frontend Setup](#frontend-setup)
6. [Docker Setup](#docker-setup)
7. [Database Setup](#database-setup)
8. [Environment Variables](#environment-variables)
9. [Running the Project](#running-the-project)
10. [Common Commands](#common-commands)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have the following installed on your system:

### Required Software

- **Python 3.10+** (3.12 recommended)
- **Node.js 16+** (18+ recommended)
- **npm** or **yarn** (comes with Node.js)
- **PostgreSQL 12+**
- **Docker & Docker Compose** (for containerized setup)
- **Git**

### Verify Installation

```bash
# Check Python version
python --version

# Check Node.js version
node --version

# Check npm version
npm --version

# Check PostgreSQL version
psql --version

# Check Docker version
docker --version
docker-compose --version
```

---

## Project Structure

```
Dental_AI_Module/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── main.py                  # Application entry point
│   │   ├── config.py                # Configuration settings
│   │   ├── database.py              # Database setup
│   │   ├── dependencies.py          # Dependency injection
│   │   ├── models/                  # Database models
│   │   ├── routes/                  # API endpoints
│   │   ├── schemas/                 # Request/response schemas
│   │   └── services/                # Business logic
│   ├── requirements.txt             # Python dependencies
│   ├── Dockerfile                   # Docker image definition
│   └── seed_db.py                   # Database seeding script
├── frontend/                        # Next.js Frontend
│   ├── app/                         # Application pages
│   ├── components/                  # React components
│   ├── lib/                         # Utilities & helpers
│   ├── package.json                 # Node dependencies
│   ├── tsconfig.json               # TypeScript configuration
│   └── next.config.ts              # Next.js configuration
├── ml/                              # Machine Learning Module
│   ├── models/                      # Trained ML models
│   ├── services/                    # ML services
│   ├── training/                    # Training scripts
│   └── evaluation/                  # Evaluation utilities
├── tests/                           # Test suite
├── docs/                            # Documentation
├── start_server.py                  # Server startup script
└── SETUP.md                         # This file
```

---

## Quick Start (Local Development)

### Option 1: Automated Setup (Recommended for Windows)

```bash
# From project root directory
python start_server.py
```

This will:

- Create virtual environment (if needed)
- Install dependencies
- Start the backend on http://localhost:8000
- Open API documentation at http://localhost:8000/docs

Then in a new terminal:

```bash
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

### Option 2: Manual Setup (Linux/macOS/Windows)

See [Backend Setup](#backend-setup) and [Frontend Setup](#frontend-setup) sections below.

---

## Backend Setup

### Step 1: Create Virtual Environment

```bash
# Navigate to project root
cd Dental_AI_Module

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate

# On macOS/Linux:
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
# Make sure virtual environment is activated
pip install --upgrade pip

# Install dependencies
pip install -r backend/requirements.txt
```

### Step 3: Verify Installation

```bash
# Check installed packages
pip list

# You should see fastapi, sqlalchemy, torch, etc.
```

### Step 4: Create .env File

Create a `.env` file in the project root:

```bash
# From project root
cp backend/.env.example .env  # If example exists
# OR create manually with contents from Environment Variables section
```

### Step 5: Start Backend Server

```bash
# From project root
python start_server.py

# OR manually with uvicorn:
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at:

- **API**: http://localhost:8000
- **API Docs (Swagger)**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory

```bash
cd frontend
```

### Step 2: Install Dependencies

```bash
# Using npm
npm install

# OR using yarn
yarn install

# OR using pnpm
pnpm install
```

### Step 3: Create Environment File (Optional)

Create `.env.local` in the `frontend/` directory:

```bash
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Add other environment variables here
```

### Step 4: Start Development Server

```bash
# Using npm
npm run dev

# OR using yarn
yarn dev

# OR using pnpm
pnpm dev
```

Frontend will be available at:

- **Application**: http://localhost:3000
- **Auto-reload**: Enabled (changes refresh automatically)

---

## Docker Setup

### Using Docker Compose (Recommended)

#### Step 1: Create docker-compose.yml

Create a `docker-compose.yml` in the project root:

```yaml
version: "3.8"

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: chairside_postgres
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: chairside_companion
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  # FastAPI Backend
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: chairside_backend
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/chairside_companion
      SECRET_KEY: ${SECRET_KEY:-change-me-in-production}
      DEBUG: ${DEBUG:-false}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  # Next.js Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: chairside_frontend
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  postgres_data:

networks:
  default:
    name: chairside_network
```

#### Step 2: Build and Run with Docker Compose

```bash
# Build all services
docker-compose build

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Remove volumes (caution: deletes database data)
docker-compose down -v
```

#### Step 3: Verify Services

```bash
# Check running containers
docker-compose ps

# Access services:
# - Backend API: http://localhost:8000
# - Frontend: http://localhost:3000
# - Database: localhost:5432
```

### Building Individual Docker Images

#### Backend Docker Build

```bash
# From project root
cd backend

# Build image
docker build -t chairside-backend:latest .

# Run container
docker run -d \
  --name chairside_backend \
  -p 8000:8000 \
  -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/chairside_companion \
  -e SECRET_KEY=your-secret-key \
  chairside-backend:latest

# View logs
docker logs chairside_backend

# Stop container
docker stop chairside_backend
```

#### Frontend Docker Build

```bash
# Create Dockerfile in frontend directory if it doesn't exist
cd frontend

# Build image
docker build -t chairside-frontend:latest .

# Run container
docker run -d \
  --name chairside_frontend \
  -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  chairside-frontend:latest

# View logs
docker logs chairside_frontend

# Stop container
docker stop chairside_frontend
```

---

## Database Setup

### Option 1: Local PostgreSQL

#### Install PostgreSQL

**Windows**: Download from [postgresql.org](https://www.postgresql.org/download/windows/)

**macOS**:

```bash
brew install postgresql@15
brew services start postgresql@15
```

**Linux (Ubuntu)**:

```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start
```

#### Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Inside psql:
CREATE DATABASE chairside_companion;
\q
```

### Option 2: Use Docker PostgreSQL

```bash
# Run PostgreSQL container
docker run -d \
  --name chairside_postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=chairside_companion \
  -p 5432:5432 \
  postgres:15-alpine

# Verify connection
psql -U postgres -h localhost -d chairside_companion
```

### Initialize Database Schema

```bash
# From project root with virtual environment activated

# Run migrations (if using Alembic)
alembic upgrade head

# OR seed database with sample data
python backend/seed_db.py
```

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# ─── Application Settings ───────────────────────────────────
APP_NAME=Chairside Companion
APP_VERSION=1.0.0-mvp
DEBUG=False

# ─── Database Configuration ────────────────────────────────
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/chairside_companion

# ─── Security ─────────────────────────────────────────────
SECRET_KEY=your-super-secret-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRY_MINUTES=15

# ─── CORS Settings ────────────────────────────────────────
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000

# ─── Rate Limiting ────────────────────────────────────────
AI_RATE_LIMIT_PER_DAY=100

# ─── File Upload ──────────────────────────────────────────
MAX_UPLOAD_SIZE_MB=50
MAX_REQUEST_BODY_MB=1
UPLOAD_DIR=uploads

# ─── Frontend Settings ────────────────────────────────────
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### For Production:

Update `.env` with:

```bash
DEBUG=False
SECRET_KEY=<generate-secure-random-key>
DATABASE_URL=postgresql+asyncpg://user:password@prod-db-host:5432/chairside_companion
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

---

## Running the Project

### Running Everything Locally

**Terminal 1 - Backend:**

```bash
# From project root
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

pip install -r backend/requirements.txt
python start_server.py
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm install
npm run dev
```

**Terminal 3 (Optional) - PostgreSQL:**

```bash
# Only needed if not using Docker
psql -U postgres -d chairside_companion
```

Then navigate to:

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Database: localhost:5432

### Running with Docker Compose

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down
```

### Running in Production

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f
```

---

## Common Commands

### Backend Commands

```bash
# Start backend server
python start_server.py

# Run with uvicorn directly
uvicorn backend.app.main:app --reload

# Start without reload (production)
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Run specific test
pytest tests/test_module1.py

# Run with coverage
pytest --cov=backend tests/

# Format code
ruff format backend/

# Lint code
ruff check backend/

# Seed database
python backend/seed_db.py

# Create database backup
pg_dump -U postgres chairside_companion > backup.sql

# Restore from backup
psql -U postgres chairside_companion < backup.sql
```

### Frontend Commands

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Run linter
npm run lint

# Format code (if prettier is configured)
npm run format

# Clean build artifacts
rm -rf .next node_modules
npm install
npm run build
```

### Docker Commands

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down

# View service status
docker-compose ps

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Execute command in running container
docker-compose exec backend python -m pytest

# Access database in container
docker-compose exec postgres psql -U postgres -d chairside_companion

# Remove all containers and volumes
docker-compose down -v

# Rebuild and restart specific service
docker-compose up -d --build backend
```

### Database Commands

```bash
# Connect to PostgreSQL
psql -U postgres -h localhost -d chairside_companion

# List databases
\l

# Connect to database
\c chairside_companion

# List tables
\dt

# Run SQL file
psql -U postgres -d chairside_companion -f script.sql

# Export database
pg_dump -U postgres chairside_companion > backup.sql

# Import database
psql -U postgres chairside_companion < backup.sql

# Create database user
createuser -U postgres -P new_user

# Delete database
dropdb -U postgres chairside_companion
```

---

## Troubleshooting

### Backend Issues

#### Python Module Not Found

```bash
# Solution: Ensure virtual environment is activated
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r backend/requirements.txt
```

#### Database Connection Error

```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT version();"

# Verify DATABASE_URL in .env
# Default: postgresql+asyncpg://postgres:postgres@localhost:5432/chairside_companion

# If using Docker:
docker-compose ps postgres
docker-compose logs postgres
```

#### Port 8000 Already in Use

```bash
# Find process using port 8000
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# OR use different port:
uvicorn backend.app.main:app --port 8001
```

#### Import Errors

```bash
# Ensure PYTHONPATH is set correctly
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"  # macOS/Linux
set PYTHONPATH=%cd%\backend  # Windows

# Then restart server
```

### Frontend Issues

#### Node Modules Corrupted

```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

#### Port 3000 Already in Use

```bash
# Find process using port 3000
lsof -i :3000  # macOS/Linux
netstat -ano | findstr :3000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# OR use different port:
PORT=3001 npm run dev
```

#### API Connection Refused

```bash
# Check NEXT_PUBLIC_API_URL in .env.local
# Should be: http://localhost:8000 (development)

# Verify backend is running:
curl http://localhost:8000/docs

# If backend is on different host:
NEXT_PUBLIC_API_URL=http://your-backend-url npm run dev
```

### Docker Issues

#### Container Won't Start

```bash
# Check logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild containers
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

#### Disk Space Issues

```bash
# Remove unused images, containers, and volumes
docker system prune -a --volumes

# Check Docker disk usage
docker system df
```

#### Permission Denied

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
sudo newgrp docker

# Run without sudo
docker-compose up -d
```

### Database Issues

#### Cannot Connect to PostgreSQL

```bash
# Check if PostgreSQL service is running
sudo service postgresql status  # Linux
brew services list | grep postgres  # macOS

# Start service
sudo service postgresql start  # Linux
brew services start postgresql  # macOS

# Verify port 5432
netstat -an | grep 5432  # macOS/Linux
netstat -ano | findstr :5432  # Windows
```

#### Database Locked

```bash
# Kill active connections
psql -U postgres -c "
  SELECT pg_terminate_backend(pg_stat_activity.pid)
  FROM pg_stat_activity
  WHERE pg_stat_activity.datname = 'chairside_companion'
  AND pid <> pg_backend_pid();
"

# Recreate database
dropdb -U postgres chairside_companion
createdb -U postgres chairside_companion
python backend/seed_db.py
```

---

## Support & Documentation

- **API Documentation**: http://localhost:8000/docs (Swagger)
- **ReDoc**: http://localhost:8000/redoc
- **Project README**: See [README.md](docs/README.md)
- **Error Handling Guide**: See [ERROR_HANDLING_STRATEGY.md](docs/ERROR_HANDLING_STRATEGY.md)
- **Refactoring Tasks**: See [REFACTORING_TASKS.md](REFACTORING_TASKS.md)

---

## Quick Reference

| Task                        | Command                                   |
| --------------------------- | ----------------------------------------- |
| Activate venv (Windows)     | `.venv\Scripts\activate`                  |
| Activate venv (macOS/Linux) | `source .venv/bin/activate`               |
| Install backend deps        | `pip install -r backend/requirements.txt` |
| Start backend               | `python start_server.py`                  |
| Start frontend              | `cd frontend && npm run dev`              |
| Start with Docker           | `docker-compose up -d`                    |
| View logs                   | `docker-compose logs -f`                  |
| Run tests                   | `pytest tests/`                           |
| Access API docs             | `http://localhost:8000/docs`              |
| Access frontend             | `http://localhost:3000`                   |
| Stop Docker                 | `docker-compose down`                     |

---

**Last Updated**: March 2026
**For questions or issues, refer to the troubleshooting section above.**
