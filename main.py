from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from database.weaviate_client import WeaviateClient
from database.memoria import Memoria
import openai
import os
from jinja2 import Environment, FileSystemLoader
from server.gunicorn_server import GunicornServer

app = FastAPI(
    title="Via Chat",
    version="0.1",
    description="Agente Professor de Violão é um assistente virtual que funciona como um professor(a) de violão.",
)

app.mount("/assets", StaticFiles(directory="assets"), name="assets")

openai_key = os.getenv('OPENAI_API_KEY')
weaviate_client = WeaviateClient("http://localhost:8080", openai.api_key)

env = Environment(loader=FileSystemLoader('templates'))

class Question(BaseModel):
    question: str
    session_id: str

@app.get("/", response_class=HTMLResponse)
async def get_chat(request: Request):
    template = env.get_template('via_chat.html')
    return template.render(request=request)

@app.post("/ask")
async def ask_question(question: Question):
    session_id = question.session_id
    question_text = question.question

    if not question_text or not session_id:
        raise HTTPException(status_code=400, detail="Missing 'question' or 'session_id' in request body")


    memoria = Memoria(session_id)


    historico = memoria.obter_historico_formatado()

    vector = weaviate_client.generate_embedding(question_text)
        

    similar_texts = weaviate_client.search_similar(vector)
    print(f"Similar texts: {similar_texts}")
    

    context = "\n".join([text for text, _ in similar_texts])


    prompt = (
        f"Use o seguinte contexto para responder a pergunta: {context}\n\n"
        f"Histórico da conversa:\n{historico}\n\n"
        f"Pergunta atual: {question_text}\n\n"
        "Instrução: Responda à pergunta atual com base no contexto e no histórico da conversa."
    )
    print("Texto enviado para OpenAI:", prompt)
    
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente virtual que funciona como um professor(a) de violão."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=600
    )

    answer = response.choices[0].message['content'].strip()

    memoria.salvar_historico(question_text, answer)

    return {"answer": answer}
  
if __name__ == '__main__':
  options = {
      'bind': '{}:{}'.format('0.0.0.0', '8000'),
      'workers': 1,
      'worker_class': 'uvicorn.workers.UvicornWorker',
      'timeout': 600
  }
  GunicornServer(app, options).run()