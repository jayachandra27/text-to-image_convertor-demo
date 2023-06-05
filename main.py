from fastapi import FastAPI, status, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.responses import HTMLResponse
import requests
import io
from PIL import Image
import os
import configparser

parser = configparser.ConfigParser()

parser.read('conf.ini')


API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"
API_TOKEN=parser.get('CREDS','token')
headers = {"Authorization": f"Bearer {API_TOKEN}"}
path = "static\images"

templates = Jinja2Templates(directory="templates")

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

def generate_image(specification):
    payload = {"inputs": specification,}
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.content

@app.post("/generate", status_code=status.HTTP_201_CREATED)
def generate(request: Request, specification: str = Form(...)):
    image_bytes = generate_image(specification)
    image = Image.open(io.BytesIO(image_bytes))
    name = specification + '.png'
    file_path = os.path.join(path, name)
    print(file_path)
    image.save(file_path)
    return templates.TemplateResponse('output.html', {"request": request, "file_path": file_path})


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    resp = templates.TemplateResponse("home.html", {"request": request, "title":"Text-to-Image-Generator"})
    return resp