from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import threading
import os
from Orquest.pipeline.website import build
from Orquest.core import files as fs # IMPORTANTE: Importar para pegar o nome da pasta

app = Flask(__name__)
CORS(app)

# Variáveis de estado global
is_generating = False
current_status = "Aguardando início..."
current_plan = None

# Pega o caminho absoluto da pasta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.join(BASE_DIR, 'workspace')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/status', methods=['GET'])
def get_status():
    # Pega o nome da pasta do projeto atual (se existir)
    project_folder = fs.get_project_dir_name() if current_plan else ""
    
    return jsonify({
        "is_generating": is_generating,
        "status": current_status,
        "plan": current_plan.model_dump() if current_plan else None,
        "project_folder": project_folder # <-- Envia o nome da pasta para o frontend
    })

@app.route('/workspace/<path:filename>')
def serve_workspace(filename):
    print(f"📂 [FLASK] Tentando servir o arquivo: {filename}")
    try:
        # O filename já vem com a pasta do projeto (ex: aura-atelier/index.html)
        return send_from_directory(WORKSPACE_DIR, filename)
    except FileNotFoundError:
        print(f"❌ ERRO: '{filename}' não achado em {WORKSPACE_DIR}")
        return "Arquivo não encontrado.", 404

@app.route('/generate', methods=['POST'])
def generate():
    global is_generating, current_status, current_plan
    if is_generating:
        return jsonify({"status": "error", "message": "Já existe uma geração em andamento."}), 400

    data = request.json
    brief = data.get('brief')
    engine = data.get('engine')

    if not brief or not engine:
        return jsonify({"status": "error", "message": "Prompt e Motor são obrigatórios."}), 400

    def run_pipeline():
        global is_generating, current_status, current_plan
        is_generating = True
        current_status = "Iniciando orquestração..."
        current_plan = None
        
        try:
            # Injeta o motor escolhido no prompt final
            forced_brief = f"{brief}. IMPORTANTE: Use OBRIGATORIAMENTE o motor de layout '{engine}'."
            print(f"\n🚀 Iniciando geração: {engine}")
            
            def update_status(msg):
                global current_status
                current_status = msg

            def update_plan(plan_obj):
                global current_plan
                current_plan = plan_obj

            # Executa o pipeline
            build(forced_brief, status_callback=update_status, plan_callback=update_plan)
            
            current_status = "✅ Concluído! O site está pronto."
            print("✅ Geração concluída com sucesso!")
            
        except Exception as e:
            current_status = f"❌ Erro: {e}"
            print(f"❌ Erro na geração: {e}")
        finally:
            is_generating = False

    thread = threading.Thread(target=run_pipeline)
    thread.start()

    return jsonify({"status": "success", "message": "Geração iniciada!"})

if __name__ == '__main__':
    if not os.path.exists(WORKSPACE_DIR):
        os.makedirs(WORKSPACE_DIR)
    # O SEGREDO ESTÁ AQUI: use_reloader=False impede que o Flask rode tudo duas vezes!
    app.run(debug=True, port=5050, use_reloader=False)