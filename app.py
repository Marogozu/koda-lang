from flask import Flask, request, render_template, jsonify
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
    """Compila el codigo Koda y devuelve JSON con el codigo generado y los datos de cada fase."""
    try:
        src = request.json.get("content", "")

        if not src.strip():
            return jsonify({"error": "No se envió código para compilar."})

        # Fase 1: Lexer
        tokens = Lexer(src)

        # Fase 2: Parser
        parser = Parser(tokens)
        ast = parser.parse()

        # Fase 3: Análisis semántico
        analyzer = SemanticAnalyzer()
        semantic = analyzer.analyze(ast)

        # Fase 4: Generación de código
        generator = CodeGenerator()
        generated_code = generator.generate(ast)

        return jsonify({
            "generated_code": generated_code,
            "tokens":         str(tokens),
            "ast":            str(ast),
            "semantic":       semantic,
        })

    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/run", methods=["POST"])
def run_code():
    """Ejecuta el codigo Python generado con los valores de stdin provistos y devuelve el output."""
    try:
        data           = request.json
        generated_code = data.get("generated_code", "")
        stdin_values   = data.get("stdin", [])   # lista de strings, uno por input()

        stdin_iter = iter(stdin_values)

        def fake_input(prompt=""):
            try:
                return next(stdin_iter)
            except StopIteration:
                return ""

        stdout_capture = io.StringIO()
        namespace = {"__builtins__": __builtins__, "input": fake_input}

        with contextlib.redirect_stdout(stdout_capture):
            exec(generated_code, namespace)

        output = stdout_capture.getvalue()
        return jsonify({"output": output if output else "(El programa no produjo salida)"})

    except Exception as e:
        return jsonify({"output": f"[ERROR DE EJECUCION] {e}"})


if __name__ == "__main__":
    app.run(debug=True)