"""
Gemini AI Service for generating clinical notes
"""
import google.generativeai as genai
from typing import Dict, Any
import json

from app.config import settings
from app.schemas import ChiropracticRecord


# Configure Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)


# Schema for structured output (matches TypeScript schema from frontend)
CHIROPRACTIC_SCHEMA = {
    "type": "object",
    "properties": {
        # Patient Info
        "occupation": {"type": "string"},
        "workload": {"type": "string", "enum": ["Low", "Moderate", "High", "Unknown"]},
        "isNewPatient": {"type": "boolean"},

        # Chief Complaint
        "mainProblem": {"type": "string", "description": "Narrative description of the problem"},
        "location": {"type": "string"},
        "onset": {"type": "string", "enum": ["Acute", "Gradual", "Unknown"]},
        "duration": {"type": "string"},
        "painQuality": {"type": "array", "items": {"type": "string"}},

        # Pain Analysis
        "aggravatedBy": {"type": "string"},
        "relievedBy": {"type": "string"},
        "diurnalVariation": {"type": "array", "items": {"type": "string"}},
        "radiation": {"type": "string"},
        "numbness": {"type": "boolean"},
        "weakness": {"type": "boolean"},

        # History
        "similarProblems": {"type": "boolean"},
        "historyDetails": {"type": "string", "description": "Detailed narrative story"},
        "previousTrauma": {"type": "string"},

        # Medical History
        "conditions": {"type": "string"},
        "surgeries": {"type": "string"},
        "medications": {"type": "string"},
        "allergies": {"type": "string"},
        "sickLeave": {"type": "boolean"},

        # Red Flags
        "redFlags": {"type": "array", "items": {"type": "string"}},
        "redFlagsComments": {"type": "string"},

        # Lifestyle
        "activity": {"type": "string"},
        "sleepQuality": {"type": "string", "enum": ["Good", "Fair", "Poor", "Unknown"]},
        "stressLevel": {"type": "string", "enum": ["Low", "Moderate", "High", "Unknown"]},
        "workStress": {"type": "boolean"},

        # Clinical Exam
        "inspection": {"type": "string"},
        "palpation": {"type": "string"},
        "tenderness": {"type": "string"},
        "jointRestrictions": {"type": "string"},
        "rom": {"type": "string"},
        "neuro": {"type": "string"},
        "orthoPositive": {"type": "string"},
        "orthoNegative": {"type": "string"},

        # Assessment
        "diagnosis": {"type": "string"},
        "differential": {"type": "string"},
        "prognosis": {"type": "string"},

        # Treatment Plan
        "plannedTreatment": {"type": "array", "items": {"type": "string"}},
        "frequency": {"type": "string"},
        "goals": {"type": "string"},

        # Treatment Today
        "treatedArea": {"type": "string"},
        "techniques": {"type": "string"},
        "response": {"type": "string"},

        # Advice
        "exercises": {"type": "string"},
        "advice": {"type": "string"},

        # Follow-up
        "nextAppointment": {"type": "string"},
    },
    "required": [
        "mainProblem", "diagnosis", "occupation", "isNewPatient", "workload",
        "painQuality", "diurnalVariation", "redFlags", "plannedTreatment"
    ]
}


async def generate_chiropractic_draft(
    transcript: str,
    visit_type: str
) -> ChiropracticRecord:
    """
    Generate structured chiropractic record from transcript using Gemini AI

    Args:
        transcript: Raw conversation transcript
        visit_type: Type of clinical visit

    Returns:
        ChiropracticRecord: Structured clinical data

    Raises:
        Exception: If AI generation fails
    """
    try:
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 0.1,
                "response_mime_type": "application/json",
                "response_schema": CHIROPRACTIC_SCHEMA
            }
        )

        prompt = f"""
You are an expert medical scribe assistant for a Chiropractor.
Your task is to convert the consultation transcript into a structured CHIROPRACTIC PATIENT RECORD.

CONTEXT & INSTRUCTIONS:
1. **Speaker Identification**: Infer who is speaking (Doctor vs Patient) from context if not labeled.
2. **Extraction**: Fill the schema strictly based on the conversation.
3. **Narrative Story-Telling**: For fields 'mainProblem', 'historyDetails', and 'diagnosis', DO NOT use short phrases like "Back pain". Instead, write a cohesive, natural story.
   - Example: "The patient reports experiencing acute lower back pain that began this morning after lifting heavy boxes at work. The pain is localized to the right lumbar region."
4. **Missing Info**: Use "Denied" or "None" if explicitly denied. Leave empty if not discussed.
5. **Medical Terminology**: Convert layperson terms to medical terminology where appropriate (e.g. "pain in low back" -> "Lumbago").

Visit Type: {visit_type}

TRANSCRIPT:
\"\"\"
{transcript}
\"\"\"
"""

        response = model.generate_content(prompt)

        if not response.text:
            raise Exception("No response generated from AI")

        # Parse JSON response
        data = json.loads(response.text)

        # Validate and convert to Pydantic model
        record = ChiropracticRecord(**data)

        return record

    except Exception as error:
        print(f"Gemini API Error: {error}")
        raise Exception("Failed to generate clinical note. Please try again.")
