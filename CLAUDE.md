# Clinote Backend API - Complete Documentation

## Project Overview

**Clinote Backend API** is a production-ready FastAPI backend for the AI-powered chiropractic documentation assistant. It securely handles Gemini AI integration, user authentication, data persistence, and audit logging for HIPAA compliance.

**Current Status:** ✅ Fully implemented and ready for frontend integration

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                  CLINOTE FRONTEND                        │
│               (React + TypeScript + Vite)               │
│                http://localhost:5173                     │
└──────────────────────────┬───────────────────────────────┘
                           │ HTTP REST API
                           │ JWT Bearer Token Auth
                           ↓
┌─────────────────────────────────────────────────────────┐
│              CLINOTE BACKEND API (FastAPI)              │
│                http://localhost:8000                     │
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  API Routes (app/routes/)                      │    │
│  │  • /api/auth/*        - Register, Login, Me    │    │
│  │  • /api/ai/*          - Generate Note          │    │
│  │  • /api/encounters/*  - CRUD Operations        │    │
│  └────────────────────────────────────────────────┘    │
│                          │                               │
│  ┌────────────────────────┴─────────────────────────┐  │
│  │  Services (app/services/)                        │  │
│  │  • gemini_service.py  - Gemini 2.0 Flash API    │  │
│  │  • auth_service.py    - JWT & Password Hashing  │  │
│  └──────────────────────────────────────────────────┘  │
│                          │                               │
│  ┌────────────────────────┴─────────────────────────┐  │
│  │  Models (app/models.py)                          │  │
│  │  • User       - Providers/Doctors                │  │
│  │  • Encounter  - Patient visits & SOAP notes      │  │
│  │  • AuditLog   - Compliance tracking              │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────┬───────────────────────────────┘
                          │ SQLAlchemy ORM
                          ↓
┌─────────────────────────────────────────────────────────┐
│         PostgreSQL Database (Supabase Hosted)           │
│        <YOUR_SUPABASE_HOST>:5432/postgres               │
│                                                          │
│  Tables:                                                 │
│  • users         - User accounts & authentication       │
│  • encounters    - Patient encounters (JSONB records)   │
│  • audit_logs    - Compliance audit trail               │
└─────────────────────────────────────────────────────────┘
                          ↑
                          │ Secure API Key (server-side)
                          │
                    ┌─────┴──────┐
                    │ Google     │
                    │ Gemini AI  │
                    │ 2.0 Flash  │
                    └────────────┘
```

---

## Tech Stack

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | 0.109.0 | Modern async Python web framework |
| **Database** | PostgreSQL | 14+ | Relational database (Supabase hosted) |
| **ORM** | SQLAlchemy | 2.0.25 | Database models and queries |
| **Migrations** | Alembic | 1.13.1 | Database schema versioning |
| **AI** | Google Gemini | 2.0 Flash Exp | Structured data extraction from text |
| **Auth** | JWT | python-jose 3.3.0 | JSON Web Token authentication |
| **Validation** | Pydantic | 2.5.3 | Request/response validation |
| **Password** | bcrypt | passlib 1.7.4 | Secure password hashing |
| **Server** | Uvicorn | 0.27.0 | ASGI web server |
| **Testing** | pytest | 7.4.4 | Unit and integration tests |

---

## Project Structure

```
clinoteBE/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI app, CORS, startup/shutdown
│   ├── config.py                # Settings (env vars) with Pydantic
│   ├── database.py              # SQLAlchemy setup & session management
│   ├── models.py                # SQLAlchemy ORM models (User, Encounter, AuditLog)
│   ├── schemas.py               # Pydantic schemas (validation & serialization)
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py              # POST /register, /login, GET /me
│   │   ├── ai.py                # POST /generate-note (Gemini integration)
│   │   └── encounters.py        # CRUD: POST, GET, PUT, DELETE, POST /sign
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_service.py    # Gemini AI integration (structured output)
│   │   └── auth_service.py      # JWT creation, password hashing/verification
│   │
│   └── middleware/
│       ├── __init__.py
│       └── auth.py              # JWT authentication dependency
│
├── alembic/
│   ├── env.py                   # Alembic environment configuration
│   └── versions/                # Database migration files
│
├── tests/
│   └── __init__.py              # Unit and integration tests
│
├── .env                         # Environment variables (secrets)
├── .env.example                 # Template for .env
├── .gitignore                   # Git ignore (includes .env, venv/)
├── .dockerignore                # Docker ignore
├── requirements.txt             # Python dependencies
├── alembic.ini                  # Alembic configuration
├── docker-compose.yml           # Docker setup (optional)
├── Dockerfile                   # Docker image definition
├── setup.sh                     # Linux/Mac setup script
├── setup.ps1                    # Windows PowerShell setup script
├── README.md                    # User-facing documentation
└── CLAUDE.md                    # 👈 This file (developer documentation)
```

---

## Environment Variables

Located in `.env` file (DO NOT commit to Git):

```bash
# Database Configuration (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:<YOUR_PASSWORD>@<YOUR_SUPABASE_HOST>:5432/postgres

# Gemini AI API Key
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>

# JWT Authentication (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=<YOUR_SECRET_KEY_64_CHARS>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# Application Settings
APP_NAME=Clinote Backend API
APP_VERSION=1.0.0
DEBUG=True
```

**Configuration Notes:**
- Database is hosted on **Supabase** (PostgreSQL cloud service)
- CORS allows both Vite dev server (5173) and CRA dev server (3000)
- JWT secret is 256-bit hex string for HS256 algorithm
- DEBUG=True enables auto-reload and detailed error messages

---

## Database Schema

### Tables

#### 1. `users` - User Accounts
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL DEFAULT 'provider',  -- 'provider', 'admin', 'staff'
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

**Relationships:**
- `encounters` (one-to-many) - User can have multiple encounters
- `audit_logs` (one-to-many) - User can have multiple audit logs

#### 2. `encounters` - Patient Encounters
```sql
CREATE TABLE encounters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id),

    -- Patient Info
    patient_name VARCHAR(255) NOT NULL,
    patient_id VARCHAR(100) NOT NULL,
    visit_type VARCHAR(100) NOT NULL,
    encounter_date TIMESTAMP NOT NULL,

    -- Clinical Data
    transcript TEXT,
    record JSONB,  -- Stores entire ChiropracticRecord as JSON

    -- Document Status
    status VARCHAR(50) NOT NULL DEFAULT 'DRAFT',  -- 'DRAFT', 'SIGNED', 'EXPORTED'
    signed_by VARCHAR(255),
    signed_at TIMESTAMP,

    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_encounters_user_id ON encounters(user_id);
CREATE INDEX idx_encounters_patient_id ON encounters(patient_id);
CREATE INDEX idx_encounters_created_at ON encounters(created_at DESC);
```

**Key Fields:**
- `record` (JSONB) - Stores the entire 80+ field ChiropracticRecord structure
- `status` - DRAFT (editable) → SIGNED (locked) → EXPORTED (finalized)
- `transcript` - Original conversation text from speech-to-text

#### 3. `audit_logs` - Compliance Audit Trail
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encounter_id UUID REFERENCES encounters(id),
    user_id UUID NOT NULL REFERENCES users(id),

    action VARCHAR(100) NOT NULL,  -- 'created', 'updated', 'signed', 'viewed', 'deleted', 'exported'
    changes JSONB,                 -- Stores what changed
    ip_address VARCHAR(45),        -- IPv4/IPv6
    user_agent VARCHAR(500),       -- Browser info

    timestamp TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_encounter_id ON audit_logs(encounter_id);
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
```

**Purpose:** HIPAA compliance - track who did what and when

---

## API Endpoints

Base URL: `http://localhost:8000`

### Health Check
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/` | No | API status & version |
| GET | `/health` | No | Detailed health check |
| GET | `/docs` | No | Swagger UI (interactive docs) |
| GET | `/redoc` | No | ReDoc (alternative docs) |

### Authentication (`/api/auth`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/auth/register` | No | Register new user |
| POST | `/api/auth/login` | No | Login & get JWT token |
| GET | `/api/auth/me` | Yes | Get current user info |

### AI Generation (`/api/ai`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/ai/generate-note` | Yes | Generate clinical note from transcript |

### Encounters (`/api/encounters`)
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/encounters/` | Yes | Create new encounter |
| GET | `/api/encounters/` | Yes | List all encounters (paginated) |
| GET | `/api/encounters/{id}` | Yes | Get specific encounter by ID |
| PUT | `/api/encounters/{id}` | Yes | Update encounter (if not signed) |
| POST | `/api/encounters/{id}/sign` | Yes | Sign clinical note (locks it) |
| DELETE | `/api/encounters/{id}` | Yes | Delete encounter (if not signed) |

---

## API Usage Examples

### 1. Register User

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@clinic.com",
    "name": "Dr. John Smith",
    "password": "SecurePass123!"
  }'
```

**Response (201):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "dr.smith@clinic.com",
  "name": "Dr. John Smith",
  "role": "provider",
  "is_active": true,
  "created_at": "2025-12-14T10:00:00Z"
}
```

### 2. Login

**Request:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "dr.smith@clinic.com",
    "password": "SecurePass123!"
  }'
```

**Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNTUwZTg0MDAtZTI5Yi00MWQ0LWE3MTYtNDQ2NjU1NDQwMDAwIiwiZW1haWwiOiJkci5zbWl0aEBjbGluaWMuY29tIiwiZXhwIjoxNzM0MTc2NDAwfQ.xyz",
  "token_type": "bearer"
}
```

### 3. Generate Clinical Note

**Request:**
```bash
curl -X POST http://localhost:8000/api/ai/generate-note \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "transcript": "Doctor: Good morning James, what brings you in today? Patient: I have been having severe lower back pain for the past week. It started after I lifted heavy boxes at work. The pain is mainly on the right side and gets worse when I sit for long periods.",
    "visitType": "Initial Consultation",
    "encounter": {
      "patientName": "James Wilson",
      "patientId": "MRN-67890",
      "visitType": "Initial Consultation",
      "date": "2025-12-14"
    }
  }'
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "occupation": "Warehouse Worker",
    "workload": "High",
    "isNewPatient": true,
    "mainProblem": "The patient reports experiencing severe lower back pain that began one week ago after lifting heavy boxes at work. The pain is primarily localized to the right lumbar region and is exacerbated by prolonged sitting.",
    "location": "Right lumbar region",
    "onset": "Acute",
    "duration": "1 week",
    "painQuality": ["Sharp", "Aching"],
    "aggravatedBy": "Prolonged sitting, bending forward",
    "relievedBy": "Rest, lying down",
    "diurnalVariation": ["Worse in evening"],
    "radiation": "None reported",
    "numbness": false,
    "weakness": false,
    "similarProblems": false,
    "historyDetails": "Patient has no previous history of back pain or injuries. This is the first episode.",
    "previousTrauma": "Heavy lifting at work",
    "conditions": "None",
    "surgeries": "None",
    "medications": "Over-the-counter ibuprofen",
    "allergies": "None",
    "sickLeave": false,
    "redFlags": [],
    "redFlagsComments": "",
    "activity": "Moderate physical activity at work",
    "sleepQuality": "Fair",
    "stressLevel": "Moderate",
    "workStress": true,
    "inspection": "Normal posture, slight antalgic gait favoring right side",
    "palpation": "Tenderness over right lumbar paraspinal muscles",
    "tenderness": "Right L4-L5 region",
    "jointRestrictions": "Restricted lumbar extension",
    "rom": "Flexion 60°, Extension 15° (limited), Lateral flexion WNL",
    "neuro": "Intact, no neurological deficits",
    "orthoPositive": "Straight leg raise positive at 45° on right",
    "orthoNegative": "Patrick's test negative",
    "diagnosis": "Acute mechanical low back pain, likely due to muscular strain from occupational lifting. Right lumbar facet joint dysfunction cannot be ruled out.",
    "differential": "Lumbar disc herniation (less likely given negative neurological signs), Sacroiliac joint dysfunction",
    "prognosis": "Good, expected resolution with conservative care in 2-4 weeks",
    "plannedTreatment": ["Spinal manipulation", "Soft tissue therapy", "Therapeutic exercises", "Ergonomic counseling"],
    "frequency": "3x per week for 2 weeks, then reassess",
    "goals": "Reduce pain by 50% in 1 week, restore full ROM in 2 weeks, return to work without restrictions in 4 weeks",
    "treatedArea": "Lumbar spine (L3-L5), right sacroiliac joint",
    "techniques": "HVLA manipulation to L4-L5, myofascial release to right quadratus lumborum",
    "response": "Patient tolerated treatment well, reported immediate 30% reduction in pain",
    "exercises": "Cat-cow stretches, pelvic tilts, gentle lumbar extension exercises",
    "advice": "Apply ice for 15 minutes every 2-3 hours for first 48 hours. Avoid prolonged sitting. Use proper lifting technique. Return to clinic in 2 days.",
    "nextAppointment": "December 16, 2025"
  }
}
```

### 4. Create Encounter (Save to Database)

**Request:**
```bash
curl -X POST http://localhost:8000/api/encounters/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "encounter": {
      "patientName": "James Wilson",
      "patientId": "MRN-67890",
      "visitType": "Initial Consultation",
      "date": "2025-12-14"
    },
    "transcript": "Doctor: Good morning James...",
    "record": { /* Full ChiropracticRecord object */ },
    "status": "DRAFT"
  }'
```

**Response (201):**
```json
{
  "success": true,
  "encounter_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "created_at": "2025-12-14T10:30:00Z"
}
```

### 5. Sign Note

**Request:**
```bash
curl -X POST http://localhost:8000/api/encounters/a1b2c3d4-e5f6-7890-abcd-ef1234567890/sign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "signedBy": "Dr. John Smith, DC"
  }'
```

**Response (200):**
```json
{
  "success": true,
  "signed_at": "2025-12-14T10:45:00Z",
  "status": "SIGNED"
}
```

---

## Data Models

### ChiropracticRecord (80+ Fields)

Complete structured clinical record matching frontend TypeScript interface:

```python
class ChiropracticRecord(BaseModel):
    # Patient Info (3 fields)
    occupation: str
    workload: str  # 'Low', 'Moderate', 'High', 'Unknown'
    isNewPatient: bool

    # Chief Complaint (5 fields)
    mainProblem: str
    location: str
    onset: str  # 'Acute', 'Gradual', 'Unknown'
    duration: str
    painQuality: List[str]

    # Pain Analysis (7 fields)
    aggravatedBy: str
    relievedBy: str
    diurnalVariation: List[str]
    radiation: str
    numbness: bool
    weakness: bool

    # History (3 fields)
    similarProblems: bool
    historyDetails: str
    previousTrauma: str

    # Medical History (5 fields)
    conditions: str
    surgeries: str
    medications: str
    allergies: str
    sickLeave: bool

    # Red Flags (2 fields)
    redFlags: List[str]
    redFlagsComments: str

    # Lifestyle (4 fields)
    activity: str
    sleepQuality: str  # 'Good', 'Fair', 'Poor', 'Unknown'
    stressLevel: str  # 'Low', 'Moderate', 'High', 'Unknown'
    workStress: bool

    # Clinical Exam (8 fields)
    inspection: str
    palpation: str
    tenderness: str
    jointRestrictions: str
    rom: str
    neuro: str
    orthoPositive: str
    orthoNegative: str

    # Assessment (3 fields)
    diagnosis: str
    differential: str
    prognosis: str

    # Treatment Plan (3 fields)
    plannedTreatment: List[str]
    frequency: str
    goals: str

    # Treatment Today (3 fields)
    treatedArea: str
    techniques: str
    response: str

    # Advice (2 fields)
    exercises: str
    advice: str

    # Follow-up (1 field)
    nextAppointment: str
```

---

## Development Workflow

### 1. Setup (First Time)

```bash
# Navigate to backend directory
cd D:\YH\Repository\InfiNetCode\clinoteBE

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify .env file exists with correct values
# (Database, Gemini API key, JWT secret)

# Initialize database (if not already done)
alembic upgrade head

# OR create tables directly
python -c "from app.database import init_db; init_db()"
```

### 2. Run Development Server

```bash
# Ensure virtual environment is activated
# Windows:
venv\Scripts\activate

# Start server with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Server will be available at:
# - API: http://localhost:8000
# - Swagger UI: http://localhost:8000/docs
# - ReDoc: http://localhost:8000/redoc
```

**Expected Output:**
```
🚀 Starting Clinote Backend API...
📊 Database: localhost:5432/postgres
✅ Database initialized
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using StatReload
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 3. Test API

```bash
# Health check
curl http://localhost:8000/health

# Register user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","name":"Test User","password":"password123"}'

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# Use Swagger UI for interactive testing
# Open: http://localhost:8000/docs
```

### 4. Database Migrations

```bash
# Create new migration after model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback last migration
alembic downgrade -1

# View migration history
alembic history
```

---

## Frontend Integration

### Update Frontend to Use Backend

The frontend needs to call the backend API instead of Gemini directly.

#### Step 1: Create API Service (Frontend)

Create `src/services/apiService.ts`:

```typescript
// src/services/apiService.ts
import { ChiropracticRecord, PatientEncounter, VisitType } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Helper to get auth token
const getAuthToken = (): string | null => {
  return localStorage.getItem('authToken');
};

// Helper for API calls
async function apiCall(endpoint: string, options: RequestInit = {}) {
  const token = getAuthToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// Generate clinical note from transcript
export const generateChiropracticDraft = async (
  transcript: string,
  visitType: VisitType,
  encounter: PatientEncounter
): Promise<ChiropracticRecord> => {
  const data = await apiCall('/ai/generate-note', {
    method: 'POST',
    body: JSON.stringify({ transcript, visitType, encounter }),
  });

  return data.data; // Extract ChiropracticRecord from response
};

// Authentication
export const register = async (email: string, name: string, password: string) => {
  return apiCall('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, name, password }),
  });
};

export const login = async (email: string, password: string): Promise<string> => {
  const data = await apiCall('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });

  const token = data.access_token;
  localStorage.setItem('authToken', token);
  return token;
};

export const getCurrentUser = async () => {
  return apiCall('/auth/me');
};

// Encounter management
export const createEncounter = async (
  encounter: PatientEncounter,
  transcript: string,
  record: ChiropracticRecord,
  status: 'DRAFT' | 'SIGNED' | 'EXPORTED' = 'DRAFT'
) => {
  return apiCall('/encounters/', {
    method: 'POST',
    body: JSON.stringify({ encounter, transcript, record, status }),
  });
};

export const getEncounter = async (id: string) => {
  return apiCall(`/encounters/${id}`);
};

export const updateEncounter = async (
  id: string,
  record: ChiropracticRecord,
  status?: 'DRAFT' | 'SIGNED' | 'EXPORTED'
) => {
  return apiCall(`/encounters/${id}`, {
    method: 'PUT',
    body: JSON.stringify({ record, status }),
  });
};

export const signNote = async (id: string, signedBy: string) => {
  return apiCall(`/encounters/${id}/sign`, {
    method: 'POST',
    body: JSON.stringify({ signedBy }),
  });
};
```

#### Step 2: Update App.tsx (Frontend)

Replace the import:

```typescript
// OLD:
import { generateChiropracticDraft } from './services/geminiService';

// NEW:
import { generateChiropracticDraft } from './services/apiService';

// No other changes needed! The function signature is identical.
```

#### Step 3: Add Environment Variable (Frontend)

Create/update `clinote/.env.local`:

```bash
# Backend API URL
VITE_API_BASE_URL=http://localhost:8000/api

# Keep Gemini key for now (can remove after testing backend)
GEMINI_API_KEY=your_key_here
```

#### Step 4: Add Authentication Flow (Frontend)

Update `App.tsx` to handle authentication:

```typescript
import { useState, useEffect } from 'react';
import { login, register, getCurrentUser } from './services/apiService';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Check if user is already logged in
    const token = localStorage.getItem('authToken');
    if (token) {
      getCurrentUser()
        .then(setUser)
        .then(() => setIsAuthenticated(true))
        .catch(() => {
          localStorage.removeItem('authToken');
          setIsAuthenticated(false);
        });
    }
  }, []);

  if (!isAuthenticated) {
    return <LoginPage onLogin={() => setIsAuthenticated(true)} />;
  }

  // Rest of your existing App.tsx code...
  return (
    <div>
      {/* Existing multi-step workflow */}
    </div>
  );
}
```

---

## Security Features

### 1. Authentication
- **JWT Tokens**: 30-minute expiration (configurable)
- **Password Hashing**: bcrypt with automatic salt generation
- **Token Storage**: Bearer token in Authorization header

### 2. Authorization
- **Route Protection**: All sensitive endpoints require valid JWT
- **Ownership Verification**: Users can only access their own encounters
- **Role-Based Access**: User roles (provider, admin, staff) for future features

### 3. Data Protection
- **API Key Security**: Gemini API key stored server-side only
- **Database Credentials**: Environment variables (not in code)
- **CORS Configuration**: Only specified origins allowed
- **SQL Injection**: Protected via SQLAlchemy ORM

### 4. Compliance
- **Audit Logging**: Every action logged with timestamp, user, and changes
- **Signed Note Locking**: Cannot edit/delete signed encounters
- **Data Retention**: All changes tracked in audit_logs table

---

## Testing

### Manual Testing with Swagger UI

1. Open http://localhost:8000/docs
2. Click "Authorize" button (top right)
3. Register user → Login → Copy access token
4. Paste token in authorization dialog
5. Test all endpoints interactively

### Automated Testing

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

---

## Deployment

### Option 1: Docker

```bash
# Build image
docker build -t clinote-backend .

# Run container
docker run -p 8000:8000 --env-file .env clinote-backend
```

### Option 2: Docker Compose

```bash
# Start all services (backend + database)
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 3: Cloud Platforms

**Recommended for Production:**
- **Backend**: Railway, Render, Fly.io, AWS Elastic Beanstalk, Google Cloud Run
- **Database**: Supabase (current), AWS RDS, Google Cloud SQL
- **Environment Variables**: Use platform's secret management

**Deployment Checklist:**
- [ ] Set `DEBUG=False` in production
- [ ] Use strong JWT secret (64+ characters)
- [ ] Enable HTTPS/TLS
- [ ] Configure proper CORS origins (no wildcards)
- [ ] Set up database backups
- [ ] Configure monitoring/logging (Sentry, CloudWatch)
- [ ] Set up CI/CD pipeline

---

## Troubleshooting

### Issue: Database Connection Error

```bash
# Check PostgreSQL is running
psql -U postgres -d postgres -h <YOUR_SUPABASE_HOST> -p 5432

# Test connection with Python
python -c "from app.database import engine; print(engine.connect())"
```

**Solution:** Verify `DATABASE_URL` in `.env` file is correct.

### Issue: Gemini API Error

**Symptoms:** 500 error when generating notes, "Failed to generate clinical note"

**Solutions:**
1. Verify API key: https://aistudio.google.com/app/apikey
2. Check quota limits in Google AI Studio
3. Ensure model name is `gemini-2.0-flash-exp`
4. Check logs: `tail -f logs/app.log`

### Issue: JWT Token Invalid

**Symptoms:** 401 Unauthorized on protected routes

**Solutions:**
1. Check token expiration (default 30 minutes)
2. Verify JWT_SECRET_KEY matches between sessions
3. Ensure Authorization header format: `Bearer <token>`

### Issue: CORS Error in Browser

**Symptoms:** Frontend can't connect, "CORS policy blocked"

**Solution:**
```python
# In app/config.py
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,https://your-frontend.vercel.app
```

---

## File Locations Reference

| File | Location | Purpose |
|------|----------|---------|
| **Main App** | `app/main.py` | FastAPI app, CORS, routes |
| **Routes** | `app/routes/ai.py` | AI generation endpoint |
| | `app/routes/auth.py` | Authentication endpoints |
| | `app/routes/encounters.py` | Encounter CRUD |
| **Services** | `app/services/gemini_service.py` | Gemini AI integration |
| | `app/services/auth_service.py` | JWT & password handling |
| **Models** | `app/models.py` | Database ORM models |
| **Schemas** | `app/schemas.py` | Pydantic validation |
| **Config** | `app/config.py` | Settings & env vars |
| **Database** | `app/database.py` | SQLAlchemy setup |
| **Middleware** | `app/middleware/auth.py` | JWT auth dependency |
| **Migrations** | `alembic/versions/` | Database migrations |
| **Environment** | `.env` | Secret configuration |

---

## Key Implementation Details

### 1. Gemini Integration

**File:** `app/services/gemini_service.py`

```python
# Uses gemini-2.0-flash-exp model
# Structured output via JSON schema
# Temperature 0.1 for consistent results
# Matches frontend schema exactly (80+ fields)
```

### 2. JWT Authentication

**File:** `app/services/auth_service.py`

```python
# HS256 algorithm
# 30-minute expiration
# Payload: { user_id, email, exp }
# Verified in middleware/auth.py
```

### 3. Database Sessions

**File:** `app/database.py`

```python
# Dependency injection: Depends(get_db)
# Auto-commit/rollback
# Session per request
# Connection pooling
```

### 4. Audit Logging

**File:** `app/routes/encounters.py`

```python
# Every create/update/delete/view/sign action logged
# Stores changes as JSONB
# Can add IP address and user agent
# Cannot be deleted (compliance)
```

---

## Next Steps

### Immediate (To Make Frontend Work)
1. ✅ Backend is already complete and functional
2. ⚠️ Frontend needs `apiService.ts` to call backend
3. ⚠️ Frontend needs authentication UI (login/register)
4. ⚠️ Update `App.tsx` imports to use `apiService` instead of `geminiService`

### Short Term (2-4 weeks)
- [ ] Add frontend authentication flow
- [ ] Add encounter history/list view
- [ ] Add search/filter for encounters
- [ ] Add user profile page
- [ ] Deploy backend to Railway/Render
- [ ] Deploy frontend to Vercel/Netlify

### Long Term (1-3 months)
- [ ] Multi-tenant support (clinics with multiple providers)
- [ ] PDF generation service (replace browser print)
- [ ] Real-time collaboration (WebSocket)
- [ ] Advanced analytics dashboard
- [ ] Mobile app (React Native)
- [ ] HL7/FHIR integration

---

## Session Restart Checklist

When starting a new Claude Code session:

1. ✅ Read this CLAUDE.md file
2. ✅ Check backend is running: `curl http://localhost:8000/health`
3. ✅ Check database connection: `psql -U postgres -h <YOUR_SUPABASE_HOST>`
4. ✅ Verify `.env` file has all required variables
5. ✅ Check frontend CLAUDE.md at `../clinote/CLAUDE.md`
6. ✅ Understand current task from user

**Quick Reference:**
- Backend URL: http://localhost:8000
- Frontend URL: http://localhost:5173
- Swagger UI: http://localhost:8000/docs
- Database: Supabase PostgreSQL (see .env)
- AI Model: gemini-2.0-flash-exp

---

**Last Updated:** 2025-12-14
**Version:** 1.0.0
**Status:** ✅ Production-Ready (Backend Complete)
**Next Phase:** Frontend Integration & Authentication UI

---

## Quick Commands Reference

```bash
# Start backend
cd D:\YH\Repository\InfiNetCode\clinoteBE
venv\Scripts\activate
uvicorn app.main:app --reload

# Start frontend
cd D:\YH\Repository\InfiNetCode\clinote
npm run dev

# Test backend health
curl http://localhost:8000/health

# View API docs
start http://localhost:8000/docs

# Database migrations
alembic upgrade head

# Run tests
pytest
```
