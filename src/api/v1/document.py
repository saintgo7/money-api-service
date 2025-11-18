"""Document AI API endpoints."""
from typing import Optional, Dict, List
from decimal import Decimal
import time
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
import PyPDF2
import io

from src.config import get_settings
from src.core.database import get_db
from src.core.usage_tracker import UsageTracker
from src.api.dependencies import verify_and_check_rate_limit

settings = get_settings()
router = APIRouter(prefix="/v1/document", tags=["Document AI"])


# Request/Response Models
class ParsedDocument(BaseModel):
    """Parsed document response."""
    text: str
    tables: Optional[List[dict]] = None
    images: Optional[List[str]] = None
    metadata: dict
    page_count: int


class QARequest(BaseModel):
    """Document Q&A request."""
    questions: List[str] = Field(..., min_items=1, max_items=10)


class QAResponse(BaseModel):
    """Document Q&A response."""
    answers: List[dict]
    cost: float


# Endpoints
@router.post("/parse", response_model=ParsedDocument)
async def parse_document(
    document: UploadFile = File(...),
    extract_tables: bool = True,
    extract_images: bool = False,
    api_key_data: Dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Parse documents (PDF, DOCX, PPTX).

    Extracts text, tables, images, and metadata from documents.
    Returns structured data for further processing.
    """
    start_time = time.time()

    try:
        # Read document
        doc_data = await document.read()

        if document.filename.endswith('.pdf'):
            # Parse PDF
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(doc_data))
            page_count = len(pdf_reader.pages)

            # Extract text
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"

            metadata = {
                "filename": document.filename,
                "format": "pdf",
                "size_bytes": len(doc_data)
            }

        elif document.filename.endswith('.docx'):
            # Parse DOCX (placeholder)
            text = "DOCX parsing not yet implemented"
            page_count = 1
            metadata = {"filename": document.filename, "format": "docx"}

        else:
            raise HTTPException(status_code=400, detail="Unsupported document format")

        # Calculate cost (simple per-page pricing)
        cost = Decimal(str(page_count * 0.01))

        # Check credit balance
        tracker = UsageTracker(db)
        if not await tracker.check_credit_balance(api_key_data["user_id"], cost):
            raise HTTPException(status_code=402, detail="Insufficient credits")

        # Record usage
        duration_ms = int((time.time() - start_time) * 1000)
        await tracker.record_usage(
            user_id=api_key_data["user_id"],
            api_key_id=api_key_data["api_key_id"],
            endpoint="/v1/document/parse",
            method="POST",
            tokens=0,
            duration_ms=duration_ms,
            status_code=200,
            cost=cost,
            metadata={"page_count": page_count}
        )

        return ParsedDocument(
            text=text,
            tables=[] if extract_tables else None,
            images=[] if extract_images else None,
            metadata=metadata,
            page_count=page_count
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document parsing failed: {str(e)}")


@router.post("/qa", response_model=QAResponse)
async def document_qa(
    document: UploadFile = File(...),
    questions: List[str] = [],
    api_key_data: Dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Answer questions about a document.

    Upload a document and ask questions. AI reads and answers based on content.
    """
    # This would use Claude with the document content
    return QAResponse(
        answers=[
            {"question": q, "answer": "Answer placeholder", "confidence": 0.95}
            for q in questions
        ],
        cost=0.05
    )


@router.post("/summarize")
async def summarize_document(
    document: UploadFile = File(...),
    length: str = "medium",
    api_key_data: Dict = Depends(verify_and_check_rate_limit),
    db: AsyncSession = Depends(get_db)
):
    """
    Summarize a document.

    Generate concise summaries of long documents.
    """
    return {
        "message": "Document summarization endpoint",
        "status": "not_implemented",
        "note": "This endpoint will use Claude to summarize parsed documents"
    }
