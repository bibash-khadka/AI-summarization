
from pathlib import Path
import re
import torch

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from transformers import T5ForConditionalGeneration, T5Tokenizer


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="Text Summarizer App",
    description="Text Summarization using T5",
    version="1.0",
)

# Configure static files
app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

# Load model and tokenizer
MODEL_NAME = "bibashkhadka/text-summarizer-t5"

tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME)

model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME)

# Select device
if torch.backends.mps.is_available():
    device = torch.device("mps")
elif torch.cuda.is_available():
    device = torch.device("cuda")
else:
    device = torch.device("cpu")

model.to(device)
model.eval()

# Configure templates
templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


class DialogueInput(BaseModel):
    dialogue: str


def clean_data(text: str) -> str:
    text = re.sub(r"\r\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"<.*?>", " ", text)
    return text.strip().lower()


def summarize_dialogue(dialogue: str) -> str:

    cleaned = clean_data(dialogue)

    inputs = tokenizer(
        cleaned,
        padding="max_length",
        max_length=512,
        truncation=True,
        return_tensors="pt",
    ).to(device)

    with torch.no_grad():

        targets = model.generate(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_length=150,
            num_beams=4,
            early_stopping=True,
        )

    return tokenizer.decode(
        targets[0],
        skip_special_tokens=True
    )


@app.post("/summarize/")
def summarize(dialogue_input: DialogueInput):

    summary = summarize_dialogue(dialogue_input.dialogue)

    return {"summary": summary}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )
