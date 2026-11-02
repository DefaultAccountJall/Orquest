import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

class BrandExtractor:
    def __init__(self, url: str):
        self.url = url

    def extract(self) -> dict:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(self.url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. Texto
            for script in soup(["script", "style", "noscript"]):
                script.decompose()
            text_content = re.sub(r'\s+', ' ', soup.get_text(separator=' ', strip=True))

            title = soup.title.string if soup.title else "Sem título"
            meta_desc = ""
            meta_tag = soup.find("meta", attrs={"name": "description"})
            if meta_tag:
                meta_desc = meta_tag.get("content", "")

            # 2. Cores
            colors = set(re.findall(r'#[0-9a-fA-F]{3,6}', response.text))

            # 3. Imagens (NOVO)
            images = []
            for img in soup.find_all('img'):
                # Pega o src, data-src (lazy load) ou srcset
                src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                if src and not src.startswith('data:'):
                    # Resolve URLs relativas para absolutas
                    full_url = urljoin(self.url, src)
                    # Filtra apenas imagens (ignora ícones pequenos se possível)
                    if any(ext in full_url.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                        images.append(full_url)
            
            # Remove duplicatas e limita a 15 imagens
            images = list(set(images))[:15]

            return {
                "url": self.url,
                "title": title,
                "meta_description": meta_desc,
                "text_content": text_content[:5000],
                "colors_found": list(colors)[:20],
                "images_found": images
            }
        except Exception as e:
            return {"error": str(e), "url": self.url}