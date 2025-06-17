from flask import Flask, Response
from dotenv import load_dotenv
import json
import os

app = Flask(__name__)
load_dotenv()

@app.route("/deploy_quiz.html")
def serve_html():
    try:
        # Carrega HTML base
        with open("deploy_quiz.html", "r", encoding="utf-8") as f:
            html = f.read()

        # Carrega bytecode do .env
        bytecode = os.getenv("BYTECODE", "")
        if not bytecode:
            return "❌ BYTECODE não definido no .env", 500

        # Carrega ABI do JSON
        with open("EduQuiz_ABI.json", "r", encoding="utf-8") as f:
            abi = json.load(f)
        abi_str = json.dumps(abi, ensure_ascii=False, separators=(",", ":"))

        # Substituição no HTML
        html = html.replace("{{BYTECODE}}", bytecode)
        html = html.replace("{{ABI}}", abi_str)

        return Response(html, mimetype="text/html")
    except Exception as e:
        return f"❌ Erro ao gerar HTML: {e}", 500

@app.route("/<path:path>")
def serve_static(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return Response(f.read(), mimetype="text/html")
    return "Arquivo não encontrado", 404

if __name__ == "__main__":
    app.run(port=3000)
