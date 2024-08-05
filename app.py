from fastapi import FastAPI, HTTPException, Response, Form
from pydantic import BaseModel
from transformers import AutoModelForSeq2SeqLM, NllbTokenizer
import json
import os

os.environ["Transformers_CACHE"] = "/app/cache"

# Initialize FastAPI app
app = FastAPI()

# Load model and tokenizer
translation_model_name = 'sarahai/nllb-uzbek-cyrillic-to-russian'
translation_model = AutoModelForSeq2SeqLM.from_pretrained(translation_model_name)
translation_tokenizer = NllbTokenizer.from_pretrained(translation_model_name)


def split_into_chunks(text, tokenizer, max_length=150):
    tokens = tokenizer.tokenize(text)
    chunks = []
    current_chunk = []
    current_length = 0
    for token in tokens:
        current_chunk.append(token)
        current_length += 1
        if current_length >= max_length:
            chunks.append(tokenizer.convert_tokens_to_string(current_chunk))
            current_chunk = []
            current_length = 0
    if current_chunk:
        chunks.append(tokenizer.convert_tokens_to_string(current_chunk))
    return chunks

def translate(text, model, tokenizer, src_lang='uzb_Cyrl', tgt_lang='rus_Cyrl'):
    tokenizer.src_lang = src_lang
    tokenizer.tgt_lang = tgt_lang
    chunks = split_into_chunks(text, tokenizer)
    translated_chunks = []
    for chunk in chunks:
        inputs = tokenizer(chunk, return_tensors='pt', padding=True, truncation=True, max_length=128)
        outputs = model.generate(inputs['input_ids'])
        translated_chunks.append(tokenizer.decode(outputs[0], skip_special_tokens=True))
    return ' '.join(translated_chunks)

class RequestModel(BaseModel):
    source: str
    
def response_template(status_code: int, message: str, data: dict=None):
    if status_code == 200:
        return Response(
            content=json.dumps({
            "success": {
                "result": data,
            },
            "error": {},
        }),
            media_type="application/json",
            status_code=status_code
        )
    elif status_code in (400, 500):
        return Response(
            content=json.dumps({
            "success": {},
            "error": {
                "description": message 
            },
        }),
            media_type="application/json",
            status_code=status_code
            )

@app.post("/translate")
async def translate_text(request: RequestModel):
    text = request.source
    if not text:
        return response_template(400, "No text provided for translation.")
    try:        
        translated_text = translate(text, translation_model, translation_tokenizer)
    except Exception as e:
        return response_template(500, f"Translation failed: {e}")
    
    return response_template(200, "Success",translated_text)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=6050)