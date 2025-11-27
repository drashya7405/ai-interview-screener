from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List
import os
from dotenv import load_dotenv
import json
import re

# Load environment variables
load_dotenv()

# Import Groq SDK
try:
    from groq import Groq
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")
    groq_client = Groq(api_key=api_key)
    _GROQ_AVAILABLE = True
except ImportError:
    groq_client = None
    _GROQ_AVAILABLE = False
    _GROQ_IMPORT_ERROR = "Groq SDK not installed. Run: pip install groq"
except Exception as exc:
    groq_client = None
    _GROQ_AVAILABLE = False
    _GROQ_IMPORT_ERROR = str(exc)

app = FastAPI(
    title="AI Interview Screener (Groq)",
    description="Backend service for evaluating candidate interview answers using Groq's free API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class AnswerRequest(BaseModel):
    candidate_says: str = Field(..., description="The candidate's answer to evaluate")
    question_context: str = Field(
        default="",
        description="Optional: The interview question for better context"
    )

class EvaluationResponse(BaseModel):
    score: int = Field(..., ge=1, le=5, description="Score from 1-5")
    summary: str = Field(..., description="One-line summary of the answer")
    improvement: str = Field(..., description="One improvement suggestion")

class CandidateAnswer(BaseModel):
    candidate_id: str = Field(..., description="Unique identifier for the candidate")
    answer: str = Field(..., description="The candidate's answer")
    question_context: str = Field(default="", description="Optional interview question")

class RankRequest(BaseModel):
    candidates: List[CandidateAnswer] = Field(..., description="List of candidate answers to rank")

class RankedCandidate(BaseModel):
    candidate_id: str
    answer: str
    score: int
    summary: str
    improvement: str
    rank: int

class RankResponse(BaseModel):
    ranked_candidates: List[RankedCandidate]


def _strip_markdown(text: str) -> str:
    """
    Remove markdown code fences and language markers from AI response.
    Handles various formats like ```json, ```, etc.
    """
    text = text.strip()
    
    # Remove code fences
    if text.startswith("```"):
        # Find the content between backticks
        pattern = r"```(?:json)?\s*(.*?)\s*```"
        match = re.search(pattern, text, re.DOTALL)
        if match:
            text = match.group(1).strip()
    
    # Remove leading 'json' keyword if present
    if text.startswith("json"):
        text = text[4:].strip()
    
    return text


def evaluate_with_groq(answer: str, question_context: str = "") -> EvaluationResponse:
    """
    Evaluate a candidate's answer using Groq's free API with Llama models.
    
    Groq offers free API access with generous limits:
    - llama-3.3-70b-versatile: Fast and capable
    - llama-3.1-70b-versatile: Alternative option
    """
    if not _GROQ_AVAILABLE:
        raise HTTPException(
            status_code=500,
            detail=f"Groq SDK not available: {_GROQ_IMPORT_ERROR}"
        )

    context_prompt = f"\nInterview Question: {question_context}\n" if question_context else ""
    
    prompt = f"""You are an expert technical interviewer evaluating candidate responses.

{context_prompt}
Candidate's Answer: {answer}

Evaluate this answer and respond with ONLY a valid JSON object (no markdown, no explanation, no code fences):
{{
  "score": <integer 1-5>,
  "summary": "<one concise sentence summarizing the answer>",
  "improvement": "<one specific, actionable suggestion for improvement>"
}}

Scoring Guide:
- 1: Poor - Incorrect, irrelevant, or demonstrates lack of understanding
- 2: Below Average - Partially correct but significant gaps in knowledge
- 3: Average - Correct but lacks depth or misses key points
- 4: Good - Solid answer with good understanding and detail
- 5: Excellent - Comprehensive, insightful, demonstrates deep expertise

Be concise but constructive. Return ONLY the JSON object."""

    try:
        # Call Groq API with Llama model
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",  # Groq's fast and free model
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert technical interviewer. You MUST respond with valid JSON only. No markdown, no explanations, just pure JSON."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=500,
            top_p=0.9
        )

        # Extract response text
        response_text = response.choices[0].message.content.strip()
        
        # Clean up any markdown formatting
        cleaned_text = _strip_markdown(response_text)
        
        # Parse JSON
        try:
            result = json.loads(cleaned_text)
        except json.JSONDecodeError:
            # Try to extract JSON from the response if it's embedded in text
            json_match = re.search(r'\{[\s\S]*\}', cleaned_text)
            if json_match:
                result = json.loads(json_match.group(0))
            else:
                raise ValueError(f"Could not parse JSON from response: {cleaned_text[:200]}")
        
        # Validate required fields
        if "score" not in result or "summary" not in result or "improvement" not in result:
            raise ValueError(f"Missing required fields in response: {result}")
        
        return EvaluationResponse(
            score=int(result["score"]),
            summary=str(result["summary"]),
            improvement=str(result["improvement"])
        )

    except json.JSONDecodeError as jde:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to parse JSON from model. Raw response: {cleaned_text[:300]}"
        )
    except ValueError as ve:
        raise HTTPException(status_code=500, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Groq API error: {str(e)}")


@app.get("/")
async def root():
    """Health check endpoint"""
    groq_status = "✅ Connected" if _GROQ_AVAILABLE else f"❌ Not Available: {_GROQ_IMPORT_ERROR}"
    
    return {
        "status": "running",
        "service": "AI Interview Screener",
        "ai_provider": "Groq (Free API)",
        "model": "llama-3.3-70b-versatile",
        "groq_status": groq_status,
        "endpoints": ["/evaluate-answer", "/rank-candidates"],
        "docs": "/docs"
    }


@app.post("/evaluate-answer", response_model=EvaluationResponse)
async def evaluate_answer(request: AnswerRequest):
    """
    Evaluate a single candidate answer using Groq's free API.
    
    Example request:
    {
        "candidate_says": "I would use React because it's component-based",
        "question_context": "Why would you choose React?"
    }
    """
    if not request.candidate_says.strip():
        raise HTTPException(status_code=400, detail="Candidate answer cannot be empty")
    
    return evaluate_with_groq(request.candidate_says, request.question_context)


@app.post("/rank-candidates", response_model=RankResponse)
async def rank_candidates(request: RankRequest):
    """
    Evaluate and rank multiple candidates using Groq's free API.
    
    Example request:
    {
        "candidates": [
            {
                "candidate_id": "C001",
                "answer": "React is component-based",
                "question_context": "Why use React?"
            },
            {
                "candidate_id": "C002",
                "answer": "React provides reusability, virtual DOM...",
                "question_context": "Why use React?"
            }
        ]
    }
    """
    if not request.candidates:
        raise HTTPException(status_code=400, detail="Candidates list cannot be empty")
    
    evaluated_candidates = []
    
    for candidate in request.candidates:
        try:
            evaluation = evaluate_with_groq(candidate.answer, candidate.question_context)
            evaluated_candidates.append({
                "candidate_id": candidate.candidate_id,
                "answer": candidate.answer,
                "score": evaluation.score,
                "summary": evaluation.summary,
                "improvement": evaluation.improvement
            })
        except Exception as e:
            # Continue with other candidates if one fails
            evaluated_candidates.append({
                "candidate_id": candidate.candidate_id,
                "answer": candidate.answer,
                "score": 0,
                "summary": f"Evaluation failed: {str(e)}",
                "improvement": "Please retry evaluation"
            })
    
    # Sort by score (descending) - highest scores first
    evaluated_candidates.sort(key=lambda x: x["score"], reverse=True)
    
    # Add ranking
    ranked = []
    for idx, candidate in enumerate(evaluated_candidates, 1):
        ranked.append(RankedCandidate(
            candidate_id=candidate["candidate_id"],
            answer=candidate["answer"],
            score=candidate["score"],
            summary=candidate["summary"],
            improvement=candidate["improvement"],
            rank=idx
        ))
    
    return RankResponse(ranked_candidates=ranked)


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting AI Interview Screener with Groq API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/")
    uvicorn.run(app, host="0.0.0.0", port=8000)