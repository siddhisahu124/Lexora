from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from brain import handle_memory_command
from pdf_reader import read_pdf
from rag import process_text, query_rag
from pydantic import BaseModel
import shutil
import uuid
import os
import json
from financial_detector import detect_financial_document
from financial_extractor import extract_financial_metrics
from finance_api import get_stock_price
from finance_api import analyze_portfolio
from fastapi.responses import StreamingResponse, FileResponse
from rag import query_multi_doc
from fastapi import BackgroundTasks
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/vectorstore", StaticFiles(directory="vectorstore"), name="vectorstore")

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- Paths ----------------
CHAT_PATH = "chat_memory"
os.makedirs(CHAT_PATH, exist_ok=True)

# ---------------- Health Check ----------------
@app.get("/")
def health():
    return {"status": "AETHER backend running"}


# ---------------- Upload ----------------
@app.post("/upload")
async def upload(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    doc_id = str(uuid.uuid4())

    os.makedirs(f"vectorstore/{doc_id}", exist_ok=True)

    pdf_path = f"vectorstore/{doc_id}/{doc_id}.pdf"

    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = read_pdf(pdf_path)

    if not text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in PDF"
        )

    if background_tasks:
        background_tasks.add_task(process_text, text, doc_id)
    else:
        process_text(text, doc_id)

    is_financial = detect_financial_document(text)

    if is_financial:
        metrics = extract_financial_metrics(text)

        with open(f"vectorstore/{doc_id}/financial.json", "w") as f:
            json.dump(metrics, f, indent=2)

    return {"doc_id": doc_id}


# ---------------- Chat Schema ----------------
class ChatRequest(BaseModel):
    doc_id: str = "paste-doc-id-here"
    question: str = "Ask question about document"


class MultiDocRequest(BaseModel):
    doc_ids: list[str]
    question: str


class PortfolioRequest(BaseModel):
    symbols: list[str]


# ---------------- Chat ----------------
@app.post("/chat")
def chat(req: ChatRequest):

    memory_reply = handle_memory_command(req.question)
    if memory_reply:
        return {"answer": memory_reply}

    chat_file = os.path.join(CHAT_PATH, f"{req.doc_id}.json")
    history = []

    if os.path.exists(chat_file):
        try:
            with open(chat_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append({"role": "user", "content": req.question})

    try:
        answer = query_rag(
            question=req.question,
            doc_id=req.doc_id,
            history=history
        )
    except Exception:
        answer = "⚠️ Something went wrong while answering. Please try again."

    history.append({"role": "assistant", "content": answer})

    with open(chat_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    return {"answer": answer}


# ---------------- Read Chat History ----------------
@app.get("/history/{doc_id}")
def get_history(doc_id: str):

    chat_file = os.path.join(CHAT_PATH, f"{doc_id}.json")

    if not os.path.exists(chat_file):
        return []

    try:
        with open(chat_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


# ---------------- New Chat ----------------
@app.post("/new-chat/{doc_id}")
def new_chat(doc_id: str):

    chat_file = os.path.join(CHAT_PATH, f"{doc_id}.json")

    if os.path.exists(chat_file):
        os.remove(chat_file)

    return {"status": "New chat started"}


# ---------------- Delete Document ----------------
@app.delete("/document/{doc_id}")
def delete_document(doc_id: str):

    vec_path = os.path.join("vectorstore", doc_id)
    chat_file = os.path.join(CHAT_PATH, f"{doc_id}.json")

    if os.path.exists(vec_path):
        shutil.rmtree(vec_path)

    if os.path.exists(chat_file):
        os.remove(chat_file)

    return {"status": "Document deleted"}


# ---------------- Document Status ----------------
@app.get("/document-status/{doc_id}")
def doc_status(doc_id: str):

    doc_path = os.path.join("vectorstore", doc_id)

    if not os.path.exists(doc_path):
        return {"status": "not_found"}

    if os.path.exists(os.path.join(doc_path, "processing")):
        return {"status": "processing"}

    if os.path.exists(os.path.join(doc_path, "index.faiss")):
        return {"status": "ready"}

    return {"status": "processing"}


# ---------------- Compare Documents ----------------
@app.post("/compare")
def compare_docs(req: MultiDocRequest):

    answer = query_multi_doc(
        question=req.question,
        doc_ids=req.doc_ids,
        history=[]
    )

    return {"answer": answer}


@app.get("/stock/{symbol}")
def stock(symbol: str):
    data = get_stock_price(symbol.upper())

    if not data:
        return {"error": "Stock not found"}

    return data


@app.post("/portfolio")
def portfolio(req: PortfolioRequest):
    return analyze_portfolio(req.symbols)


# ---------------- Chart ----------------
@app.get("/chart/{doc_id}")
def get_chart(doc_id: str):

    chart_path = os.path.join("vectorstore", doc_id, "revenue_chart.png")

    if not os.path.exists(chart_path):
        raise HTTPException(status_code=404, detail="Chart not found")

    return FileResponse(chart_path, media_type="image/png")