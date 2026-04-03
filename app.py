from flask import Flask, request, render_template
from src import Lexer, Parser, SemanticAnalyzer, CodeGenerator

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
        analyzer = SemanticAnalyzer()
        semantic = analyzer.analyze(ast)

        # ----- Fase 4: Code Generation -----
        generator = CodeGenerator()
        output = generator.generate(ast)

        # salida que se mostrará en los paneles
        # tokens = str(tokens)
        # tokens = "\n".join(tokens)
        ast = str(ast)

        return render_template(
            "index.html",
            output=output,
            tokens=tokens,
            ast=ast,
            semantic=semantic,
            content=src
        )

    except Exception as e:

        return render_template(
            "index.html",
            output=str(e),
            # error=str(e),
            content=src
        )


if __name__ == "__main__":
    app.run(debug=True)