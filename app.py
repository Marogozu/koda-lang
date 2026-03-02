from flask import Flask, request, render_template
from src import Lexer, Parser

def compile(src: str):
    tokensFromSrc = Lexer(src=src)
    #astFromTokens = Parser(tokensFromSrc)
    
    return tokensFromSrc




app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route('/handle_data', methods=['POST'])
def handle_data():
    if request.method != "POST":
        return render_template("index.html", error="Expected POST request.")

    if "codeFile" not in request.files: #el name del input debe ser codeFile
        return render_template("index.html", error="No file part found in request. (Did you uploaded a file?)")

    file = request.files["codeFile"]

    if file.filename == "": #Al no tener nombre sospechamos que es un envio vacio
        return render_template("index.html", error="No file selected. (Or no name found)")

    #(operaciones no seguras)
    try:
        # Leer archivo a memoria 
        file_content = file.read()
        
        # decodificar como texto
        text_data = file_content.decode('utf-8', errors='replace')
        codeGen = compile(src=text_data)

        return render_template("index.html", result=codeGen)
    
    except Exception as e:
    
        return render_template("index.html", error=f"Error processing file: {e}")
    


# Permite hacer hot-reload y tener el servidor en modo debugging
if __name__ == '__main__':
    app.run(debug=True)
