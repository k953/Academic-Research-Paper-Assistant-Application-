from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering
from typing import Optional

# Initialize the FastAPI app
app = FastAPI()

# Load models for Summarization and Question Answering
try:
    # Summarization pipeline using the `distilbart-cnn-12-6` model
    summarizer = pipeline(
        "summarization",
        model="sshleifer/distilbart-cnn-12-6",
        framework="pt",
        device=0  # Set to 0 to use GPU; use -1 for CPU
    )

    # Question Answering model and tokenizer using `distilbert-base-uncased-distilled-squad`
    tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-distilled-squad")
    qa_model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-uncased-distilled-squad")

except Exception as e:
    raise RuntimeError("Error loading model(s): " + str(e))


# Define request body structure for summarization
class SummarizeRequest(BaseModel):
    content: str  # Content to summarize

# Define request body structure for question answering
class QuestionRequest(BaseModel):
    context: str  # Context for question answering
    question: str  # User's question

### Endpoint: Summarization ###
@app.post("/summarize/")
async def summarize_paper(request: SummarizeRequest):
    """
    Summarize the provided content.
    """
    content = request.content
    
    try:
        # Perform summarization on the provided content
        summary = summarizer(content, max_length=150, min_length=30, do_sample=False)
        return {"summary": summary[0]['summary_text']}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Summarization failed: " + str(e))

### Endpoint: Question Answering ###
@app.post("/answer_question/")
async def answer_question(request: QuestionRequest):
    """
    Answer a question based on the provided context.
    """
    context = request.context
    question = request.question

    try:
        # Prepare inputs for the Q&A model
        inputs = tokenizer(question, context, return_tensors="pt", truncation=True)
        outputs = qa_model(**inputs)

        # Identify the answer span with highest confidence
        answer_start = outputs.start_logits.argmax()
        answer_end = outputs.end_logits.argmax()
        answer = tokenizer.convert_tokens_to_string(
            tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start: answer_end + 1])
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Question answering failed: " + str(e))
