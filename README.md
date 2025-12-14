# Clinote Backend API

AI-powered medical documentation assistant backend built with FastAPI, PostgreSQL, and Google Gemini AI.

## Features

- **AI-Powered Documentation**: Generate structured clinical notes from transcripts using Gemini 2.0 Flash
- **RESTful API**: Complete CRUD operations for patient encounters
- **JWT Authentication**: Secure user authentication and authorization
- **PostgreSQL Database**: Robust data persistence with JSONB support
- **Audit Logging**: Complete audit trail for compliance
- **Auto Documentation**: Interactive API docs (Swagger UI & ReDoc)

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI**: Google Gemini AI (2.0 Flash Exp)
- **Authentication**: JWT with python-jose
- **Validation**: Pydantic v2
- **Migration**: Alembic

## Project Structure

```
clinoteBE/
├── app/
│   ├── main.py              # FastAPI app & routes
│   ├── config.py            # Settings & environment
│   ├── database.py          # Database connection
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── routes/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── ai.py            # AI generation endpoints
│   │   └── encounters.py    # Encounter CRUD
│   ├── services/
│   │   ├── gemini_service.py # Gemini AI integration
│   │   └── auth_service.py   # JWT & auth logic
│   └── middleware/
│       └── auth.py          # Auth middleware
├── alembic/                 # Database migrations
├── tests/                   # Unit & integration tests
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
└── README.md
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Gemini API Key

### 1. Clone Repository

```bash
cd clinoteBE
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database

```bash
# Create database
createdb clinote_db

# Or using psql
psql -U postgres
CREATE DATABASE clinote_db;
\q
```

### 5. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/clinote_db

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# JWT (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# App
APP_NAME=Clinote Backend API
DEBUG=True
```

### 6. Initialize Database

```bash
# Run migrations
alembic upgrade head

# Or create tables directly
python -c "from app.database import init_db; init_db()"
```

### 7. Run Development Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/register` | Register new user | No |
| POST | `/api/auth/login` | Login & get JWT token | No |
| GET | `/api/auth/me` | Get current user | Yes |

### AI Generation

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/ai/generate-note` | Generate clinical note from transcript | Yes |

### Encounters

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/encounters/` | Create new encounter | Yes |
| GET | `/api/encounters/` | List all encounters | Yes |
| GET | `/api/encounters/{id}` | Get specific encounter | Yes |
| PUT | `/api/encounters/{id}` | Update encounter | Yes |
| POST | `/api/encounters/{id}/sign` | Sign clinical note | Yes |
| DELETE | `/api/encounters/{id}` | Delete encounter | Yes |

## API Usage Examples

### 1. Register User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "name": "Dr. John Smith",
    "password": "securepassword123"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "doctor@example.com",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### 3. Generate Clinical Note

```bash
curl -X POST "http://localhost:8000/api/ai/generate-note" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "transcript": "Doctor: Good morning, James...",
    "visitType": "Initial Consultation",
    "encounter": {
      "patientName": "James Smith",
      "patientId": "MRN-12345",
      "visitType": "Initial Consultation",
      "date": "2025-12-14"
    }
  }'
```

### 4. Create Encounter

```bash
curl -X POST "http://localhost:8000/api/encounters/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "encounter": {
      "patientName": "James Smith",
      "patientId": "MRN-12345",
      "visitType": "Initial Consultation",
      "date": "2025-12-14"
    },
    "transcript": "Doctor: Good morning...",
    "record": { ... },
    "status": "DRAFT"
  }'
```

## Database Schema

### Users Table
```sql
- id: UUID (primary key)
- email: VARCHAR(255) UNIQUE
- name: VARCHAR(255)
- hashed_password: VARCHAR(255)
- role: ENUM (provider, admin, staff)
- is_active: BOOLEAN
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### Encounters Table
```sql
- id: UUID (primary key)
- user_id: UUID (foreign key)
- patient_name: VARCHAR(255)
- patient_id: VARCHAR(100)
- visit_type: VARCHAR(100)
- encounter_date: TIMESTAMP
- transcript: TEXT
- record: JSONB
- status: ENUM (DRAFT, SIGNED, EXPORTED)
- signed_by: VARCHAR(255)
- signed_at: TIMESTAMP
- created_at: TIMESTAMP
- updated_at: TIMESTAMP
```

### Audit Logs Table
```sql
- id: UUID (primary key)
- encounter_id: UUID (foreign key)
- user_id: UUID (foreign key)
- action: VARCHAR(100)
- changes: JSONB
- ip_address: VARCHAR(45)
- user_agent: VARCHAR(500)
- timestamp: TIMESTAMP
```

## Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

## Deployment

### Using Docker

```bash
# Build image
docker build -t clinote-backend .

# Run container
docker run -p 8000:8000 --env-file .env clinote-backend
```

### Using Docker Compose

```bash
docker-compose up -d
```

## Frontend Integration

Update your frontend `apiService.ts`:

```typescript
const API_BASE_URL = 'http://localhost:8000/api';

export const generateChiropracticDraft = async (
  transcript: string,
  visitType: string,
  encounter: PatientEncounter
) => {
  const token = localStorage.getItem('authToken');

  const response = await fetch(`${API_BASE_URL}/ai/generate-note`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({ transcript, visitType, encounter })
  });

  const data = await response.json();
  return data.data; // Returns ChiropracticRecord
};
```

## Security Considerations

- JWT tokens stored securely (httpOnly cookies recommended)
- Password hashing with bcrypt
- CORS configured for frontend origin
- Database credentials in environment variables
- Audit logging for all operations
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy ORM

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/db` |
| `GEMINI_API_KEY` | Google Gemini API key | `AIza...` |
| `JWT_SECRET_KEY` | JWT signing secret | `openssl rand -hex 32` |
| `JWT_ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration | `30` |
| `CORS_ORIGINS` | Allowed origins (comma-separated) | `http://localhost:3000` |
| `DEBUG` | Debug mode | `True` or `False` |

## Troubleshooting

### Database Connection Error

```bash
# Check PostgreSQL is running
pg_ctl status

# Test connection
psql -U username -d clinote_db
```

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Gemini API Error

- Verify API key in `.env`
- Check quota: https://aistudio.google.com/app/apikey
- Ensure model name is correct: `gemini-2.0-flash-exp`

## Development

### Database Migrations

```bash
# Create migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Add New Endpoint

1. Define Pydantic schema in `schemas.py`
2. Create route handler in `routes/`
3. Include router in `main.py`
4. Test with Swagger UI

## Contributing

1. Create feature branch
2. Make changes
3. Write tests
4. Submit pull request

## License

MIT License

## Support

For issues and questions:
- GitHub Issues: [Create Issue]
- Documentation: http://localhost:8000/docs

---

**Version**: 1.0.0
**Last Updated**: 2025-12-14
