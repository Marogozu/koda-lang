import os
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for

# Importa tu Lexer/Parser reales
from src.lexer import Lexer
from src.parser import Parser

app = Flask(__name__)

WORKSPACE = Path("workspace")
WORKSPACE.mkdir(exist_ok=True)

def safe_kd_name(name: str) -> str:
    # evita ../ y fuerza extensión .kd
    name = (name or "").strip()
    name = os.path.basename(name)
    if not name.endswith(".kd"):
        name += ".kd"
    return name

def list_kd_files():
    return sorted([p.name for p in WORKSPACE.glob("*.kd")])

def read_file(filename: str) -> str:
    path = WORKSPACE / filename
    return path.read_text(encoding="utf-8")

def write_file(filename: str, content: str):
    path = WORKSPACE / filename
    path.write_text(content, encoding="utf-8")

@app.get("/")
def index():
    files = list_kd_files()
    return render_template("index.html", files=files, current_file="", content="", result=None)

@app.post("/new")
def new_file():
    # solo limpia el editor
    return redirect(url_for("index"))

@app.get("/open")
def open_file():
    filename = request.args.get("filename", "")
    files = list_kd_files()
    if not filename:
        return render_template("index.html", files=files, error="Selecciona un archivo para abrir.", current_file="", content="", result=None)
    filename = safe_kd_name(filename)
    path = WORKSPACE / filename
    if not path.exists():
        return render_template("index.html", files=files, error="Ese archivo no existe.", current_file="", content="", result=None)
    content = read_file(filename)
    return render_template("index.html", files=files, current_file=filename, content=content, result=None, message=f"Abierto: {filename}")

@app.post("/save")
def save_file():
    files = list_kd_files()
    filename = safe_kd_name(request.form.get("filename", "main.kd"))
    content = request.form.get("content", "")

    write_file(filename, content)
    files = list_kd_files()
    return render_template("index.html", files=files, current_file=filename, content=content, result=None, message=f"Guardado: {filename}")

@app.post("/upload")
def upload_file():
    files = list_kd_files()
    f = request.files.get("codeFile")
    if not f or f.filename == "":
        return render_template("index.html", files=files, error="No se subió ningún archivo.", current_file="", content="", result=None)
    filename = safe_kd_name(f.filename)
    content = f.read().decode("utf-8", errors="replace")
    write_file(filename, content)
    files = list_kd_files()
    return render_template("index.html", files=files, current_file=filename, content=content, result=None, message=f"Subido: {filename}")

@app.post("/compile")
def compile_code():
    files = list_kd_files()
    filename = request.form.get("filename", "")
    content = request.form.get("content", "")

    # Compila desde el editor siempre
    try:
        tokens = Lexer(content)
        parser = Parser(tokens)
        ast = parser.parse()

        # salida simple: tokens + repr(ast)
        out = ["TOKENS:"]
        out.extend([repr(t) for t in tokens])
        out.append("\nAST:")
        out.append(repr(ast))
        return render_template("index.html", files=files, current_file=filename, content=content, result=out)
    except Exception as e:
        return render_template("index.html", files=files, current_file=filename, content=content, error=str(e), result=None)

if __name__ == "__main__":
    app.run(debug=True)