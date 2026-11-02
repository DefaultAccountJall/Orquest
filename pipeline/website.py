import json
import re
import time
import Orquest.config as config
from Orquest.agents.researcher import Researcher
from Orquest.agents.ui_planner import UIPlanner
from Orquest.agents.redesign_planner import RedesignPlanner
from Orquest.agents.brand_extractor import BrandExtractor
from Orquest.agents.logic_planner import LogicPlanner
from Orquest.agents.frontend_coder import FrontendCoder
from Orquest.agents.logic_coder import LogicCoder
from Orquest.agents.reviewer import Reviewer
from Orquest.core import files as fs
from Orquest.core.schemas import Plan, CodeOutput, ReviewResult, FileWrite

def build(brief: str, status_callback=None, plan_callback=None):
    def update_status(msg):
        if status_callback:
            status_callback(msg)
        print(msg)

    frontend_coder = FrontendCoder()
    logic_planner = LogicPlanner()
    logic_coder = LogicCoder()
    reviewer = Reviewer()
    
    brand_images = []

    # --- ETAPA 0 e 1: INGESTÃO E PLANEJAMENTO ---
    url_pattern = re.compile(r'https?://[^\s]+')
    url_match = url_pattern.search(brief)
    
    if url_match:
        url = url_match.group(0)
        update_status(f"[0/5] Extraindo dados de: {url}")
        extractor = BrandExtractor(url)
        brand_data = extractor.extract()
        
        if "error" in brand_data:
            update_status(f"❌ Erro ao extrair site: {brand_data['error']}")
            return None

        brand_images = brand_data.get("images_found", [])
        update_status(f"✔ Dados extraídos | {len(brand_images)} imagens encontradas.")
        
        update_status("[1/5] Redesign Planner analisando a marca...")
        planner = RedesignPlanner()
        plan_ui: Plan = planner.run(brief=brief, brand_data=json.dumps(brand_data, ensure_ascii=False))
        
    else:
        update_status("[1/5] Iniciando Pesquisa de Mercado...")
        premium_brief = f"Awwwards winning website design and features for: {brief}. Focus on premium animations and layout."
        research = Researcher().run(brief=premium_brief)
        update_status("✔ Pesquisa concluída.")
        
        update_status("[2/5] Arquiteto Suíço planejando o Ecossistema e Design System...")
        plan_ui: Plan = UIPlanner().run(brief=brief, research=research.model_dump_json(indent=2))

    if plan_callback:
        plan_callback(plan_ui)
        print("📊 Plano de Design e Jornada enviados para a interface!")

    # --- NOVO: CRIA A PASTA DO PROJETO AQUI ---
    project_folder = fs.set_project_dir(plan_ui.site_name)
    update_status(f"📂 Projeto isolado na pasta: workspace/{project_folder}")

    # --- GUIA DE TESTE ---
    ds = plan_ui.design_system
    guia_html = f"""<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8"><title>Guia - {plan_ui.site_name}</title><script src="https://cdn.tailwindcss.com"></script><style>body {{ background-color: {ds.background_color}; color: {ds.text_color}; }}</style></head><body class="p-8 md:p-24 max-w-5xl mx-auto"><h1 class="text-5xl font-bold mb-4">Guia de Teste</h1><p>Projeto: {plan_ui.site_name} | Engine: {ds.layout_engine}</p><a href="index.html" class="text-blue-500 underline">Voltar para Home</a></body></html>"""
    fs.write_files([fs.FileWrite(path="guia.html", content=guia_html)])
    
    # --- ETAPA 3: FRONTEND (MÚLTIPLAS PÁGINAS) ---
    update_status("[3/5] Construindo Ecossistema Frontend (HTML e CSS)...")
    ui_files = [f for f in plan_ui.files_to_create if f.endswith(('.html', '.css'))]
    if not ui_files: ui_files = ["index.html"]
    
    all_pages_str = ", ".join(ui_files)
    
    for path in ui_files:
        update_status(f" -> Criando {path}...")
        
        # Avisa o coder se existem imagens locais ou se deve usar Unsplash
        if brand_images:
            brand_images_str = "\n".join(brand_images)
        else:
            brand_images_str = "(Nenhuma imagem fornecida. Verifique se existem imagens na pasta 'img/' local e use caminhos como './img/foto1.jpg'. Caso contrário, use Unsplash.)"
        
        code = frontend_coder.run(
            plan=plan_ui.model_dump_json(indent=2),
            design_system=ds.model_dump_json(indent=2),
            brand_images=brand_images_str,
            all_pages=all_pages_str,
            target_file=path,
            feedback="(nenhum)"
        )
        fs.write_files(code.files)
        
        # PAUSA DE SEGURANÇA DO CLAUDE
        update_status("⏳ Aguardando 5s para evitar Rate Limit...")
        time.sleep(5)

    # --- INJEÇÃO DE SEGURANÇA DO JS ---
    update_status("🔧 Injetando script de animações nas páginas...")
    current_files = fs.read_workspace()
    for file_path, content in current_files.items():
        if file_path.endswith(".html") and file_path != "guia.html":
            if "js/main.js" not in content:
                content = content.replace("</body>", '  <script src="js/main.js"></script>\n</body>')
                fs.write_files([FileWrite(path=file_path, content=content)])

    # --- LOOP DE VALIDAÇÃO (QA) ROBUSTO ---
    update_status("🔍 QA Frontend: Iniciando auditoria do ecossistema...")
    for loop in range(1, config.MAX_REVIEW_LOOPS + 1):
        workspace_content = fs.read_workspace()
        pages_to_review = {k: v for k, v in workspace_content.items() if k != "guia.html"}
        
        review = reviewer.run(plan=plan_ui.model_dump_json(indent=2), files=pages_to_review)
        
        if review.approved:
            update_status("✔ Ecossistema APROVADO.")
            break
        else:
            update_status(f"⚠️ Auditoria encontrou problemas (Loop {loop}/{config.MAX_REVIEW_LOOPS}). Corrigindo...")
            issues_by_file = {}
            for issue in review.issues:
                if issue.severity in ("error", "warning"):
                    issues_by_file.setdefault(issue.file, []).append(issue)
            
            if issues_by_file:
                target_file = max(issues_by_file, key=lambda k: len(issues_by_file[k]))
                target_issues = issues_by_file[target_file]
                feedback = "\n".join(f"- [{i.severity}] {i.description}" for i in target_issues)
                
                update_status(f" -> Corrigindo {target_file}...")
                code = frontend_coder.run(
                    plan=plan_ui.model_dump_json(indent=2),
                    design_system=ds.model_dump_json(indent=2),
                    all_pages=all_pages_str,
                    brand_images=brand_images_str,
                    target_file=target_file,
                    feedback=feedback
                )
                fs.write_files(code.files)
                
                # PAUSA DE SEGURANÇA DO CLAUDE
                update_status("⏳ Aguardando 5s para evitar Rate Limit...")
                time.sleep(5)
            else:
                update_status("⚠️ Nenhum erro explícito encontrado, mas não aprovado. Pulando correção.")
                break

    # --- ETAPAS 4 e 5: LÓGICA E ANIMAÇÕES ---
    update_status("[4/5] Planejando Mecânicas e Animações Globais...")
    logic_plan = logic_planner.run(
        ui_plan=plan_ui.model_dump_json(indent=2),
        design_system=ds.model_dump_json(indent=2),
        current_files=json.dumps(list(pages_to_review.keys()))
    )
    js_files = [f for f in logic_plan.scripts_to_create if f.endswith('.js')]
    if not js_files: js_files = ["js/main.js"]

    update_status("[5/5] Implementando Animações Frontend...")
    for path in js_files:
        update_status(f" -> Criando {path}...")
        code = logic_coder.run(
            logic_plan=logic_plan.model_dump_json(indent=2),
            design_system=ds.model_dump_json(indent=2),
            current_files=fs.read_workspace(),
            target_file=path,
            feedback="(nenhum)"
        )
        fs.write_files(code.files)
        
        # PAUSA DE SEGURANÇA DO CLAUDE
        update_status("⏳ Aguardando 5s para evitar Rate Limit do Claude...")
        time.sleep(5)

    update_status("✅ Concluído! O ecossistema está pronto.")
    
    return plan_ui