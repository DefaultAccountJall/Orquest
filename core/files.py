import os
import re
import unicodedata
from pathlib import Path
import Orquest.config as config
from Orquest.core.schemas import FileWrite

CURRENT_PROJECT_DIR = ""

def set_project_dir(name: str) -> str:
    global CURRENT_PROJECT_DIR
    # Limpa o nome do projeto para virar uma URL amigável
    nfkd = unicodedata.normalize('NFKD', name)
    clean_name = u"".join([c for c in nfkd if not unicodedata.combining(c)])
    clean_name = re.sub(r'[^a-zA-Z0-9]', '-', clean_name).lower()
    clean_name = re.sub(r'-+', '-', clean_name).strip('-')
    
    if not clean_name:
        clean_name = "projeto"
        
    CURRENT_PROJECT_DIR = clean_name
    full_path = config.WORKSPACE_DIR / clean_name
    full_path.mkdir(parents=True, exist_ok=True)
    return clean_name

def get_project_dir_name() -> str:
    return CURRENT_PROJECT_DIR

def get_current_workspace_path() -> Path:
    if CURRENT_PROJECT_DIR:
        return config.WORKSPACE_DIR / CURRENT_PROJECT_DIR
    return config.WORKSPACE_DIR

def safe_path(rel: str) -> Path:
    base = get_current_workspace_path()
    p = (base / rel).resolve()
    if not str(p).startswith(str(base.resolve())):
        raise ValueError(f"Tentativa de escrita fora do workspace bloqueada: {rel}")
    return p

def write_files(files: list[FileWrite]) -> list[str]:
    written = []
    for f in files:
        if not f.path or not f.content: continue
        path = safe_path(f.path)
        path.parent.mkdir(parents=True, exist_ok=True)
        try:
            path.write_text(f.content, encoding="utf-8")
            written.append(str(path.relative_to(get_current_workspace_path())))
            print(f"    [💾 Salvo] {f.path}")
        except Exception as e:
            print(f"    [❌ Erro ao salvar] {f.path}: {e}")
    return written

def read_workspace() -> dict[str, str]:
    out = {}
    base = get_current_workspace_path()
    if not base.exists(): return out
    for p in base.rglob("*"):
        if p.is_file() and not p.name.startswith(".") and p.name != ".gitkeep":
            try:
                out[str(p.relative_to(base))] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
    return out