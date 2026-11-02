from ddgs import DDGS

def search_web(query: str, max_results: int = 5) -> str:
    """Pesquisa na web e retorna um resumo dos resultados para o Researcher."""
    try:
        # O DDGS agora é importado da biblioteca 'ddgs'
        results = list(DDGS().text(query, max_results=max_results))
        
        if not results:
            return "Nenhum resultado encontrado na web. Use o conhecimento interno."
        
        resumo = ""
        for i, r in enumerate(results, 1):
            title = r.get('title', 'Sem título')
            body = r.get('body', 'Sem descrição')
            href = r.get('href', '#')
            
            resumo += f"[{i}] Fonte: {href}\nTítulo: {title}\nResumo: {body}\n\n"
            
        return resumo.strip()
    except Exception as e:
        return f"Erro na pesquisa web: {e}. O Researcher deve seguir com o conhecimento interno."