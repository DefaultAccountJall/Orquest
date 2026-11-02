from pydantic import BaseModel, Field, model_validator
from typing import Any

# --- SCHEMAS DE PESQUISA ---
class ResearchOutput(BaseModel):
    design_trends: str = Field(default="")
    requirements: list[str] = Field(default=[])
    references: list[str] = Field(default=[])

# --- SCHEMAS DE PLANEJAMENTO VISUAL (UI) ---
class DesignSystem(BaseModel):
    primary_color: str = Field(default="#000000")
    background_color: str = Field(default="#ffffff")
    text_color: str = Field(default="#333333")
    font_heading: str = Field(default="Playfair Display")
    font_body: str = Field(default="Inter")
    visual_style: str = Field(default="Editorial, Premium")
    layout_engine: str = Field(default="Swiss Design", description="Engine: 'Neo-Brutalism', 'Glassmorphism', 'Swiss Design', 'Cyberpunk'")
    animations: list[str] = Field(default_factory=list)

class PageSpec(BaseModel):
    path: str = Field(default="")
    title: str = Field(default="")
    purpose: str = Field(default="")

    @model_validator(mode='before')
    @classmethod
    def fix_purpose(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("path"): data["path"] = data.get("file", "index.html")
            if not data.get("title"): data["title"] = data.get("name", "Página")
            if not data.get("purpose"):
                for k, v in data.items():
                    if k not in ["path", "title", "file", "url", "name"]:
                        if isinstance(v, list): data["purpose"] = ", ".join(str(x) for x in v)
                        elif isinstance(v, str): data["purpose"] = v
                        break
                else:
                    data["purpose"] = "Propósito não especificado."
        return data

# Procure a classe Plan no seu core/schemas.py e deixe assim:
class Plan(BaseModel):
    site_name: str = "Meu Site"
    summary: str = ""
    pages: list[PageSpec] = []
    files_to_create: list[str] = Field(default=[])
    design_system: DesignSystem = Field(default_factory=DesignSystem)
    # NOVO CAMPO ABAIXO:
    user_journey: list[str] = Field(default=[], description="Lista de caminhos/fluxos que o usuário pode fazer no site")

# --- SCHEMAS DE PLANEJAMENTO DE LÓGICA (FRONTEND ONLY) ---
class LogicPlan(BaseModel):
    scripts_to_create: list[str] = Field(default=[], description="Arquivos JS a criar (ex: 'js/main.js')")
    interactions: list[str] = Field(default=[], description="Mecânicas frontend (ex: 'validação', 'lightbox')")
    notes: str = ""

# --- SCHEMAS DE CÓDIGO ---
class FileWrite(BaseModel):
    path: str = ""
    content: str = ""

# Atualize a classe DesignSystem no seu core/schemas.py:
class DesignSystem(BaseModel):
    primary_color: str = Field(default="#000000")
    background_color: str = Field(default="#ffffff")
    text_color: str = Field(default="#333333")
    font_heading: str = Field(default="Playfair Display")
    font_body: str = Field(default="Inter")
    visual_style: str = Field(default="Editorial, Premium")
    layout_engine: str = Field(default="Swiss Design", description="Engine de layout: 'Neo-Brutalism', 'Glassmorphism', 'Swiss Design', 'Cyberpunk'")
    animations: list[str] = Field(default_factory=list)

class CodeOutput(BaseModel):
    files: list[FileWrite] = []
    notes: str = ""

# --- SCHEMAS DE REVISÃO ---
class Issue(BaseModel):
    file: str = Field(default="geral")
    severity: str = Field(default="error")
    description: str = Field(default="")

    @model_validator(mode='before')
    @classmethod
    def map_alternative_keys(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if not data.get("file"): data["file"] = data.get("path", "geral")
            if not data.get("severity"): data["severity"] = data.get("type", "error")
            if not data.get("description"):
                for k, v in data.items():
                    if k not in ["file", "severity", "path", "type"]:
                        if isinstance(v, str): data["description"] = v
                        break
                else:
                    data["description"] = "Problema detectado."
        return data

class ReviewResult(BaseModel):
    approved: bool = False
    issues: list[Issue] = []
    summary: str = ""