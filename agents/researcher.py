from Orquest.agents.base import Agent
from Orquest.core.schemas import ResearchOutput

# Tenta importar o ddgs (DuckDuckGo Search)
try:
    from ddgs import DDGS
    HAS_DDGS = True
except ImportError:
    HAS_DDGS = False

def search_web(query: str, max_results: int = 3) -> str:
    """Pesquisa na web usando DuckDuckGo de forma segura."""
    if not HAS_DDGS:
        return "Pesquisa indisponível. Biblioteca 'ddgs' não instalada. Use seu conhecimento interno."

    try:
        results = list(DDGS().text(query, max_results=max_results))
        if not results:
            return "Nenhum resultado encontrado. Use seu conhecimento interno."

        resumo = "Resultados da Pesquisa Web:\n"
        for i, r in enumerate(results, 1):
            title = r.get('title', 'Sem título')
            body = r.get('body', 'Sem descrição')
            resumo += f"[{i}] {title}\n{body}\n\n"
        return resumo.strip()
    except Exception as e:
        return f"Erro na pesquisa web: {e}. O Researcher deve seguir com o conhecimento interno."

class Researcher(Agent):
    name = "researcher"
    system_prompt = (
        "Você é um Analista de Tendências de Design Digital de Elite. "
        "Sua missão é analisar o briefing e os resultados de busca fornecidos, "
        "extraindo os padrões de design, layout e animação usados nos sites mais premiados.\n\n"
        "DIRETRIZES DE EXTRAÇÃO:\n"
        "1. TENDÊNCIAS DE DESIGN: Identifique estilos visuais fortes.\n"
        "2. REQUISITOS TÉCNICOS: Extraia bibliotecas e técnicas (GSAP, Lenis, Tailwind).\n"
        "3. REFERÊNCIAS: Liste estúdios ou sites premiados que serviram de inspiração.\n\n"
        "Seja extremamente específico. Crie um plano digno de prêmio."
    )
    output_schema = ResearchOutput

    def run(self, brief: str) -> ResearchOutput:
        print(f"  [🔍 Pesquisando referências na web para: {brief[:30]}...]")
        
        # 1. Faz a busca real no DuckDuckGo
        query = f"Awwwards winning website design layout animations for {brief}"
        search_results = search_web(query, max_results=3)
        
        # 2. Monta o contexto para a IA
        context = (
            f"Briefing Original do Cliente:\n{brief}\n\n"
            f"{search_results}\n\n"
            f"INSTRUÇÃO: Analise o briefing e os resultados da web acima. Crie as diretrizes de design."
        )
        
        # 3. Envia para a IA extrair o JSON
        return super().run(context=context)