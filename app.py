from flask import Flask, request, render_template
from src import Lexer, Parser, SemanticAnalyzer, CodeGenerator
import io
import sys
import contextlib

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
        generated_code = generator.generate(ast)

        # ----- Fase 5: Execution -----
        # Capturar el stdout del codigo generado
        stdout_capture = io.StringIO()
        try:
            # El namespace compartido permite que funciones y variables
            # declaradas antes sean visibles en todo el programa.
            # __builtins__ es necesario para que print, input, int, etc. funcionen.
            namespace = {"__builtins__": __builtins__}
            with contextlib.redirect_stdout(stdout_capture):
                exec(generated_code, namespace)
            output = stdout_capture.getvalue()
            if not output:
                output = "(El programa no produjo salida)"
        except Exception as exec_error:
            output = f"[ERROR DE EJECUCION] {exec_error}"

        # salida que se mostrará en los paneles
        ast_str = str(ast)

        return render_template(
            "index.html",
            output=output,
            tokens=tokens,
            ast=ast_str,
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