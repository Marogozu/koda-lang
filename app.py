from flask import Flask, request, render_template
from src import Lexer, Parser

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/compile", methods=["POST"])
def compile_code():

    try:
        # código enviado desde el editor
        src = request.form.get("content", "")

        if not src.strip():
            return render_template(
                "index.html",
                error="No se envió código para compilar."
            )

        # ----- Fase 1: Lexer -----
        tokens = Lexer(src)

        # ----- Fase 2: Parser -----
        parser = Parser(tokens)
        ast = parser.parse()

        # salida que se mostrará en el panel derecho
        result = []

        result.append("TOKENS:")
        for t in tokens:
            result.append(str(t))

        result.append("\nAST:")
        result.append(str(ast))

        return render_template(
            "index.html",
            result=result,
            content=src
        )

    except Exception as e:

        return render_template(
            "index.html",
            error=str(e),
            content=src
        )


# ---------------------------------
# Ejecutar servidor
# ---------------------------------
if __name__ == "__main__":
    app.run(debug=True)