import json
import time
import re
from typing import Type
from openai import OpenAI, RateLimitError, APIConnectionError
from pydantic import BaseModel, ValidationError
import json_repair
import Orquest.config as config

_client = OpenAI(
    api_key=config.DEEPSEEK_API_KEY, 
    base_url=config.BASE_URL,
    default_headers={"Host": "127.0.0.1:7250"}
)

def ask_structured(system: str, user: str, schema: Type[BaseModel],
                   model: str | None = None, max_retries: int = 3, temperature: float = 0.2) -> BaseModel:
    model = model or config.MODEL
    
    json_schema = json.dumps(schema.model_json_schema(), indent=2)
    
    # PROMPT LIMPO: Sem comandos de override que fazem a IA da web surtar
    enhanced_system = (
        f"{system}\n\n"
        f"CRITICAL RULES:\n"
        f"- Respond ONLY with a valid JSON object.\n"
        f"- DO NOT write any conversational text before or after the JSON.\n"
        f"- The JSON must strictly follow this schema:\n{json_schema}"
    )

    last_err = None
    for attempt in range(max_retries):
        try:
            response = _client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": enhanced_system},
                    {"role": "user", "content": user},
                ],
                temperature=temperature,
                max_tokens=16384,
                stream=True,
                timeout=120
            )
            
            content = ""
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content

            if not content.strip():
                raise ValueError("Resposta vazia do modelo.")
                
            if "approaching_limit" in content or "Mensagens muito frequentes" in content:
                print("\n    [🛑 RATE LIMIT ATINGIDO!] Aguardando 60s...")
                time.sleep(60)
                raise ValueError("Rate limit atingido.")

            # A MÁGICA: Ignora toda a conversa fiada e pega só o JSON do começo ao fim
            match = re.search(r'\{.*\}', content, re.DOTALL)
            if match:
                content = match.group(0)
            else:
                raise ValueError("Nenhum JSON encontrado na resposta.")

            parsed_args = json_repair.loads(content)
            if not parsed_args:
                raise ValueError("json_repair falhou.")

            return schema.model_validate(parsed_args)
            
        except (RateLimitError, APIConnectionError) as e:
            last_err = e
            print(f"    [⚠️ Erro de API] {e}. Tentando novamente...")
            if attempt < max_retries - 1:
                time.sleep(15)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_err = e
            print(f"    [⚠️ Erro de Formato] {e}. Tentando novamente...")
            if attempt < max_retries - 1:
                time.sleep(10)
        except Exception as e:
            raise RuntimeError(f"Erro ao obter saída estruturada ({schema.__name__}): {e}") from e

    raise RuntimeError(f"Falha após {max_retries} tentativas. Último erro: {last_err}")