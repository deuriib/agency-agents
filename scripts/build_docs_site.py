#!/usr/bin/env python3
"""Build documentation site for Agency Agents using MkDocs Material.

Generates the docs directory from repository markdown sources and agent catalog:
- English docs in site-docs/docs/en/
- Spanish docs in site-docs/docs/es/ (22 core translated pages: home, installation,
  contributing, security, and 18 division landing pages)
- 18 division landing pages and 300 agent persona pages generated deterministically.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
SITE_DOCS_ROOT = REPO_ROOT / "site-docs"
DOCS_DIR = SITE_DOCS_ROOT / "docs"

# 18 divisions in canonical order
DIVISIONS = [
    "academic",
    "design",
    "engineering",
    "finance",
    "game-development",
    "gis",
    "healthcare",
    "marketing",
    "paid-media",
    "product",
    "project-management",
    "research",
    "sales",
    "security",
    "spatial-computing",
    "specialized",
    "support",
    "testing",
]

DIVISION_META = {
    "academic": {"name": "Academic", "name_es": "Académica", "emoji": "📚"},
    "design": {"name": "Design", "name_es": "Diseño", "emoji": "🎨"},
    "engineering": {"name": "Engineering", "name_es": "Ingeniería", "emoji": "💻"},
    "finance": {"name": "Finance", "name_es": "Finanzas", "emoji": "💵"},
    "game-development": {"name": "Game Development", "name_es": "Desarrollo de Videojuegos", "emoji": "🎮"},
    "gis": {"name": "GIS", "name_es": "SIG / GIS", "emoji": "🌍"},
    "healthcare": {"name": "Healthcare", "name_es": "Salud", "emoji": "🏥"},
    "marketing": {"name": "Marketing", "name_es": "Marketing", "emoji": "📢"},
    "paid-media": {"name": "Paid Media", "name_es": "Medios Pagados", "emoji": "💰"},
    "product": {"name": "Product", "name_es": "Producto", "emoji": "📊"},
    "project-management": {"name": "Project Management", "name_es": "Gestión de Proyectos", "emoji": "🎬"},
    "research": {"name": "Research", "name_es": "Investigación", "emoji": "🔍"},
    "sales": {"name": "Sales", "name_es": "Ventas", "emoji": "💼"},
    "security": {"name": "Security", "name_es": "Seguridad", "emoji": "🔒"},
    "spatial-computing": {"name": "Spatial Computing", "name_es": "Computación Espacial", "emoji": "🥽"},
    "specialized": {"name": "Specialized", "name_es": "Especializada", "emoji": "🎯"},
    "support": {"name": "Support", "name_es": "Soporte", "emoji": "🛟"},
    "testing": {"name": "Testing", "name_es": "Testing y Calidad", "emoji": "🧪"},
}


def parse_agent_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    meta: dict[str, Any] = {}
    body = text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try:
                meta = yaml.safe_load(parts[1]) or {}
            except Exception as e:
                print(f"Error parsing YAML from {path}: {e}", file=sys.stderr)
            body = parts[2].strip()

    name = meta.get("name", path.stem.replace("-", " ").title())
    emoji = meta.get("emoji", "🤖")
    description = meta.get("description", "")
    color = meta.get("color", "blue")
    vibe = meta.get("vibe", "")

    return {
        "slug": path.stem,
        "name": name,
        "emoji": emoji,
        "description": description,
        "color": color,
        "vibe": vibe,
        "body": body,
        "source_path": path,
    }


def clean_and_prepare_dirs() -> None:
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    (DOCS_DIR / "en").mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "es").mkdir(parents=True, exist_ok=True)



def fix_contributing_links(text: str) -> str:
    repo_url = "https://github.com/deuriib/agency-agents/blob/main/"
    text = text.replace("](docs/dx/", f"]({repo_url}docs/dx/")
    text = text.replace("](docs/dx/", f"]({repo_url}docs/dx/")
    text = text.replace("](divisions.json)", f"]({repo_url}divisions.json)")
    text = text.replace("](README.md)", "](index.md)")
    text = text.replace("](engineering/engineering-frontend-developer.md)", "](divisions/engineering/engineering-frontend-developer.md)")
    text = text.replace("](marketing/marketing-reddit-community-builder.md)", "](divisions/marketing/marketing-reddit-community-builder.md)")
    text = text.replace("](design/design-whimsy-injector.md)", "](divisions/design/design-whimsy-injector.md)")
    return text

def build_core_guides() -> None:
    readme_text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    contributing_text = fix_contributing_links((REPO_ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8"))
    security_text = (REPO_ROOT / "SECURITY.md").read_text(encoding="utf-8")

    # English core guides
    (DOCS_DIR / "en" / "index.md").write_text(build_en_home(readme_text), encoding="utf-8")
    (DOCS_DIR / "en" / "installation.md").write_text(build_en_installation(readme_text), encoding="utf-8")
    (DOCS_DIR / "en" / "contributing.md").write_text(contributing_text, encoding="utf-8")
    (DOCS_DIR / "en" / "security.md").write_text(security_text, encoding="utf-8")

    # Spanish core guides
    (DOCS_DIR / "es" / "index.md").write_text(build_es_home(), encoding="utf-8")
    (DOCS_DIR / "es" / "installation.md").write_text(build_es_installation(), encoding="utf-8")
    (DOCS_DIR / "es" / "contributing.md").write_text(build_es_contributing(), encoding="utf-8")
    (DOCS_DIR / "es" / "security.md").write_text(build_es_security(), encoding="utf-8")


def build_en_home(readme_text: str) -> str:
    # Extract overview and features from README
    return """# 🎭 The Agency

> **A complete AI agency at your fingertips** — 300 specialized AI agent personas ready to install across Claude Code, Cursor, Codex, Gemini CLI, OpenCode, Qwen, Windsurf, Aider, and more.

## Overview

The Agency gives your AI coding harness full-stack agency capabilities. Each persona is built with:
- Deep domain workflows, checklists, and identity memory
- Native compatibility with top AI development environments
- Quality gates, testing discipline, and evidence-driven handoffs

## Quick Links

- [Installation & Quick Start](installation.md)
- [Divisions & Agents Catalog](divisions/index.md)
- [Contributing Guide](contributing.md)
- [Security Policy](security.md)

---
*Upstream project: [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)*
"""


def build_en_installation(readme_text: str) -> str:
    return """# ⚡ Installation & Quick Start

## Option 1: Desktop App (Recommended)

The fastest way in — no clone, no terminal. [**Agency Agents**](https://agencyagents.app) is a native desktop app for macOS, Linux, and Windows that browses the whole roster and installs agents with one click.

- **[Download latest release](https://github.com/deuriib/agency-agents-app/releases/latest)**
- On macOS via Homebrew:
```bash
brew install --cask msitarzewski/agency-agents/agency-agents
```

## Option 2: CLI via PyPI (No clone required)

The Python CLI bundles the full catalog and installs into your active coding harness:

```bash
pip install py-agency-agents
# or run directly with uvx:
uvx py-agency-agents install --tool claude-code
```

## Option 3: Local Clone & Development

If contributing or modifying agents locally:

```bash
git clone https://github.com/deuriib/agency-agents.git
cd agency-agents
./scripts/bootstrap.sh
./scripts/gate.sh
uv run agency-agents install --tool claude-code
```

## Supported Tools

| Tool | Format | Notes |
|---|---|---|
| **Claude Code** | Native persona prompts | Installs directly to Claude config |
| **Cursor** | `.cursorrules` / rules | Auto-converted rules per agent |
| **OpenCode** | Agent instructions | Multi-agent catalog support |
| **Gemini CLI** | Extension JSON | Rich tool calling integration |
| **Antigravity** | Workspace rules | Compiled skill packages |
| **Aider** | CONVENTIONS / prompts | System instructions |
| **Windsurf** | `.windsurfrules` | Memory & workflow rules |
"""


def build_es_home() -> str:
    return """# 🎭 The Agency

> **Una agencia completa de IA al alcance de tus dedos** — 300 agentes especializados listos para instalarse en Claude Code, Cursor, Codex, Gemini CLI, OpenCode, Qwen, Windsurf, Aider y más.

## Descripción General

The Agency equipa tu entorno de desarrollo asistido por IA con capacidades operativas de nivel profesional. Cada persona incluye:
- Flujos de trabajo profundos, listas de verificación y memoria de identidad
- Compatibilidad nativa con los principales arneses de codificación con IA
- Puertas de calidad, disciplina de pruebas y traspasos basados en evidencia

## Enlaces Rápidos

- [Instalación y Guía Rápida](installation.md)
- [Divisiones y Catálogo de Agentes](divisions/index.md)
- [Guía de Contribución](contributing.md)
- [Política de Seguridad](security.md)

---
*Proyecto original: [msitarzewski/agency-agents](https://github.com/msitarzewski/agency-agents)*
"""


def build_es_installation() -> str:
    return """# ⚡ Instalación y Guía Rápida

## Opción 1: Aplicación de Escritorio (Recomendado)

La forma más rápida — sin clonar repositorios ni usar terminal. [**Agency Agents**](https://agencyagents.app) es una aplicación nativa para macOS, Linux y Windows que permite explorar todo el catálogo e instalar agentes con un solo clic.

- **[Descargar última versión](https://github.com/deuriib/agency-agents-app/releases/latest)**
- En macOS vía Homebrew:
```bash
brew install --cask msitarzewski/agency-agents/agency-agents
```

## Opción 2: CLI desde PyPI (Sin clonar)

La CLI de Python incluye todo el catálogo empaquetado y se instala directamente en tu entorno:

```bash
pip install py-agency-agents
# o ejecutar directamente con uvx:
uvx py-agency-agents install --tool claude-code
```

## Opción 3: Clon Local y Desarrollo

Para colaborar o modificar agentes localmente:

```bash
git clone https://github.com/deuriib/agency-agents.git
cd agency-agents
./scripts/bootstrap.sh
./scripts/gate.sh
uv run agency-agents install --tool claude-code
```

## Herramientas Compatibles

| Herramienta | Formato | Notas |
|---|---|---|
| **Claude Code** | Prompts nativos de persona | Instalación directa en configuración de Claude |
| **Cursor** | `.cursorrules` / reglas | Reglas optimizadas por cada persona |
| **OpenCode** | Instrucciones de agente | Compatibilidad multi-agente |
| **Gemini CLI** | Extensión JSON | Integración con llamadas de herramientas |
| **Antigravity** | Reglas de espacio de trabajo | Paquetes de habilidades compilados |
| **Aider** | CONVENTIONS / prompts | Instrucciones de sistema |
| **Windsurf** | `.windsurfrules` | Reglas y contexto de flujo de trabajo |
"""


def build_es_contributing() -> str:
    return """# 🤝 Contribuir a The Agency

¡Muchas gracias por considerar contribuir a The Agency! Personas como tú hacen que este catálogo de agentes de IA sea cada día mejor para todos.

## 📋 Código de Conducta

Este proyecto y todos los participantes se rigen por nuestro Código de Conducta. Al participar, te comprometes a mantener un ambiente respetuoso, constructivo e inclusivo.

## 🎯 ¿Cómo contribuir?

1. **Nuevos Agentes**: Diseña personas altamente especializadas que resuelvan problemas específicos con personalidad, flujos claros y criterios de aceptación.
2. **Mejoras a Agentes Existentes**: Refina prompts, añade memoria de contexto y optimiza las instrucciones de entrega.
3. **Herramientas e Integraciones**: Aporta mejoras al generador, los arneses de instalación o los scripts de automatización.

## 🔄 Proceso de Pull Request

- Abre una rama descriptiva (`feat/nombre-agente` o `fix/problema`).
- Ejecuta las verificaciones locales con `./scripts/gate.sh` o `mise run check`.
- Asegúrate de que las pruebas y linters pasen al 100%.
- Documenta claramente los cambios en la descripción del PR.
"""


def build_es_security() -> str:
    return """# 🔒 Política de Seguridad

Nos tomamos la seguridad de The Agency con la máxima seriedad y agradecemos los informes responsables sobre cualquier vulnerabilidad.

## Reporte de Vulnerabilidades

**Por favor, NO abras issues públicos para reportar vulnerabilidades de seguridad.**

En su lugar, envía un reporte confidencial a través de los canales privados del repositorio en GitHub o por correo electrónico a `deuriib@gmail.com`.

## Compromiso de Respuesta

- **Acuse de recibo**: En un plazo máximo de 48 horas tras recibir el reporte.
- **Evaluación y remediación**: Priorización inmediata según la severidad del hallazgo.
- **Divulgación coordinada**: Publicación del parche de seguridad antes de cualquier divulgación pública.
"""


def build_divisions_and_agents() -> None:
    en_div_index = ["# 🏛️ Divisions Overview\n\nThe Agency is structured into 18 specialized divisions, organizing 300 expert AI agents:\n\n| Division | Agents | Description |\n|---|---|---|"]
    es_div_index = ["# 🏛️ Resumen de Divisiones\n\nThe Agency está organizada en 18 divisiones especializadas con 300 agentes de IA expertos:\n\n| División | Agentes | Descripción |\n|---|---|---|"]

    nav_divisions_en = []
    nav_divisions_es = []

    for div_slug in DIVISIONS:
        meta = DIVISION_META[div_slug]
        div_path = REPO_ROOT / div_slug

        # Find all agent files in this division
        agent_files = []
        for root, _, files in os.walk(div_path):
            for f in sorted(files):
                if f.endswith(".md"):
                    agent_files.append(Path(root) / f)

        agent_files.sort(key=lambda p: p.stem)
        agent_count = len(agent_files)

        # Division dirs
        (DOCS_DIR / "en" / "divisions" / div_slug).mkdir(parents=True, exist_ok=True)
        (DOCS_DIR / "es" / "divisions" / div_slug).mkdir(parents=True, exist_ok=True)

        en_div_index.append(f"| [{meta['emoji']} {meta['name']}]({div_slug}/index.md) | {agent_count} | Specialized in {meta['name'].lower()} workflows |")
        es_div_index.append(f"| [{meta['emoji']} {meta['name_es']}]({div_slug}/index.md) | {agent_count} | Especialistas en flujos de {meta['name_es'].lower()} |")

        # English division landing page
        en_div_content = [
            f"# {meta['emoji']} {meta['name']} Division",
            f"\nWelcome to the **{meta['name']}** division. This division contains **{agent_count}** specialized agents.",
            "\n## Agents Roster\n",
            "| Agent | Focus / Description |",
            "|---|---|",
        ]

        # Spanish division landing page
        es_div_content = [
            f"# {meta['emoji']} División de {meta['name_es']}",
            f"\nBienvenido a la división de **{meta['name_es']}**. Esta división agrupa a **{agent_count}** agentes especializados.",
            "\n## Catálogo de Agentes\n",
            "| Agente | Especialidad / Descripción |",
            "|---|---|",
        ]

        agent_nav_items_en = []
        agent_nav_items_es = []

        for apath in agent_files:
            agent_data = parse_agent_file(apath)
            rel_slug = agent_data["slug"]

            en_div_content.append(f"| [{agent_data['emoji']} {agent_data['name']}]({rel_slug}.md) | {agent_data['description']} |")
            es_div_content.append(f"| [{agent_data['emoji']} {agent_data['name']}]({rel_slug}.md) | {agent_data['description']} |")

            # Agent page content
            agent_page_content = f"""# {agent_data['emoji']} {agent_data['name']}

> {agent_data['description']}

{agent_data['body']}
"""
            # Write agent markdown in English (Spanish will fall back to English per specification)
            (DOCS_DIR / "en" / "divisions" / div_slug / f"{rel_slug}.md").write_text(agent_page_content, encoding="utf-8")

            agent_nav_items_en.append({f"{agent_data['emoji']} {agent_data['name']}": f"divisions/{div_slug}/{rel_slug}.md"})
            agent_nav_items_es.append({f"{agent_data['emoji']} {agent_data['name']}": f"divisions/{div_slug}/{rel_slug}.md"})

        # Write division landing pages
        (DOCS_DIR / "en" / "divisions" / div_slug / "index.md").write_text("\n".join(en_div_content) + "\n", encoding="utf-8")
        (DOCS_DIR / "es" / "divisions" / div_slug / "index.md").write_text("\n".join(es_div_content) + "\n", encoding="utf-8")

        div_nav_en = [{f"Overview": f"divisions/{div_slug}/index.md"}] + agent_nav_items_en
        div_nav_es = [{f"Resumen": f"divisions/{div_slug}/index.md"}] + agent_nav_items_es

        nav_divisions_en.append({f"{meta['emoji']} {meta['name']}": div_nav_en})
        nav_divisions_es.append({f"{meta['emoji']} {meta['name_es']}": div_nav_es})

    # Write division master index
    (DOCS_DIR / "en" / "divisions" / "index.md").write_text("\n".join(en_div_index) + "\n", encoding="utf-8")
    (DOCS_DIR / "es" / "divisions" / "index.md").write_text("\n".join(es_div_index) + "\n", encoding="utf-8")


def write_mkdocs_config() -> None:
    mkdocs_config = {
        "site_name": "The Agency",
        "site_description": "300 specialized AI agents for development, design, and operations",
        "site_url": "https://deuriib.github.io/agency-agents/",
        "repo_name": "deuriib/agency-agents",
        "repo_url": "https://github.com/deuriib/agency-agents",
        "docs_dir": "site-docs/docs",
        "site_dir": "site",
        "theme": {
            "name": "material",
            "language": "en",
            "palette": [
                {
                    "scheme": "default",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {
                        "icon": "material/brightness-7",
                        "name": "Switch to dark mode",
                    },
                },
                {
                    "scheme": "slate",
                    "primary": "indigo",
                    "accent": "indigo",
                    "toggle": {
                        "icon": "material/brightness-4",
                        "name": "Switch to light mode",
                    },
                },
            ],
            "features": [
                "navigation.tabs",
                "navigation.sections",
                "navigation.expand",
                "navigation.top",
                "search.suggest",
                "search.highlight",
                "content.code.copy",
            ],
        },
        "extra": {
            "alternate": [
                {"name": "English", "link": "/agency-agents/", "lang": "en"},
                {"name": "Español", "link": "/agency-agents/es/", "lang": "es"},
            ],
            "social": [
                {
                    "icon": "fontawesome/brands/github",
                    "link": "https://github.com/deuriib/agency-agents",
                }
            ],
            "attribution": "Based on the upstream project msitarzewski/agency-agents",
        },
        "plugins": [
            "search",
            {
                "i18n": {
                    "docs_structure": "folder",
                    "fallback_to_default": True,
                    "languages": [
                        {
                            "locale": "en",
                            "name": "English",
                            "default": True,
                            "build": True,
                        },
                        {
                            "locale": "es",
                            "name": "Español",
                            "build": True,
                        },
                    ],
                }
            },
        ],
        "markdown_extensions": [
            "admonition",
            "pymdownx.details",
            "pymdownx.superfences",
            "pymdownx.highlight",
            "pymdownx.inlinehilite",
            "tables",
            "attr_list",
            "toc",
        ],
    }

    with open(REPO_ROOT / "mkdocs.yml", "w", encoding="utf-8") as f:
        yaml.dump(mkdocs_config, f, sort_keys=False, allow_unicode=True)


def main() -> None:
    print("Preparing docs directories in site-docs/...")
    clean_and_prepare_dirs()

    print("Building core guides (en & es)...")
    build_core_guides()

    print("Building divisions and agent pages...")
    build_divisions_and_agents()

    print("Writing mkdocs.yml...")
    write_mkdocs_config()

    print("Docs site content generated successfully!")


if __name__ == "__main__":
    main()
