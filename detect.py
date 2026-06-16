"""
Framework detection engine.

Detects programming language, framework, build system, and package manager
from a project directory — no dependencies beyond Python stdlib.
"""

import json
import os
from typing import Optional

# ── Framework definitions ─────────────────────────────────────────────────────

FRAMEWORK_PATTERNS = {
    # Node.js static sites
    "vite":          {"file": "package.json", "dep": "vite",            "type": "node-static",  "build": "npm run build",  "out": "dist",          "port": 3000},
    "react-scripts": {"file": "package.json", "dep": "react-scripts",   "type": "node-static",  "build": "npm run build",  "out": "build",         "port": 3000},
    "gatsby":        {"file": "package.json", "dep": "gatsby",          "type": "node-static",  "build": "gatsby build",   "out": "public",        "port": 3000},
    "astro":         {"file": "package.json", "dep": "astro",           "type": "node-static",  "build": "npm run build",  "out": "dist",          "port": 3000},
    "svelte-kit":    {"file": "package.json", "dep": "@sveltejs/kit",   "type": "node-static",  "build": "npm run build",  "out": "build",         "port": 3000},
    "vue-cli":       {"file": "package.json", "dep": "@vue/cli-service","type": "node-static",  "build": "npm run build",  "out": "dist",          "port": 3000},
    # Node.js SSR apps
    "nuxt":          {"file": "package.json", "dep": "nuxt",            "type": "node-ssr",     "build": "npm run build",  "out": ".output",       "port": 3000},
    "nextjs":        {"file": "package.json", "dep": "next",            "type": "node-ssr",     "build": "npm run build",  "out": ".next",         "port": 3000},
    "remix":         {"file": "package.json", "dep": "@remix-run/react","type": "node-ssr",     "build": "npm run build",  "out": "build",         "port": 3000},
    # Node.js servers
    "express":       {"file": "package.json", "dep": "express",         "type": "node-server",  "build": None,             "out": None,            "port": 3000},
    "nestjs":        {"file": "package.json", "dep": "@nestjs/core",    "type": "node-server",  "build": "npm run build",  "out": "dist",          "port": 3000},
    # Python
    "django":        {"file": "requirements.txt", "dep": "django",      "type": "python",       "build": None,             "out": None,            "port": 8000},
    "flask":         {"file": "requirements.txt", "dep": "flask",       "type": "python",       "build": None,             "out": None,            "port": 5000},
    "fastapi":       {"file": "requirements.txt", "dep": "fastapi",     "type": "python",       "build": None,             "out": None,            "port": 8000},
    "streamlit":     {"file": "requirements.txt", "dep": "streamlit",   "type": "python",       "build": None,             "out": None,            "port": 8501},
    # Go
    "go":            {"file": "go.mod",           "dep": None,          "type": "go",           "build": None,             "out": None,            "port": 8080},
    # Ruby
    "rails":         {"file": "Gemfile",          "dep": "rails",       "type": "ruby",         "build": None,             "out": None,            "port": 3000},
    "sinatra":       {"file": "Gemfile",          "dep": "sinatra",     "type": "ruby",         "build": None,             "out": None,            "port": 4567},
    # PHP
    "laravel":       {"file": "composer.json",    "dep": "laravel",     "type": "php",          "build": None,             "out": None,            "port": 8000},
    "php":           {"file": "composer.json",    "dep": None,          "type": "php",          "build": None,             "out": None,            "port": 8080},
    # Rust
    "rust":          {"file": "Cargo.toml",       "dep": None,          "type": "rust",         "build": None,             "out": None,            "port": 8080},
    # Static HTML
    "static":        {"file": "index.html",       "dep": None,          "type": "static",       "build": None,             "out": ".",             "port": 80},
}

# ── Package manager detection ────────────────────────────────────────────────

def detect_package_manager(build_context: str) -> str:
    """
    Detect which Node.js package manager a project uses by checking lock files.

    Returns ``"pnpm"``, ``"yarn"``, or ``"npm"``.
    """
    if os.path.exists(os.path.join(build_context, "pnpm-lock.yaml")):
        return "pnpm"
    if os.path.exists(os.path.join(build_context, "yarn.lock")):
        return "yarn"
    return "npm"


# ── Dependency checking ───────────────────────────────────────────────────────

def check_dependency(file_path: str, dep_name: str) -> bool:
    """Check whether a dependency exists in a project file."""
    try:
        if file_path.endswith("package.json"):
            with open(file_path) as f:
                pkg = json.load(f)
            all_deps = {}
            all_deps.update(pkg.get("dependencies", {}))
            all_deps.update(pkg.get("devDependencies", {}))
            return dep_name in all_deps
        elif file_path.endswith("requirements.txt"):
            with open(file_path) as f:
                content = f.read().lower()
            return dep_name.lower() in content
        elif file_path.endswith("Gemfile"):
            with open(file_path) as f:
                content = f.read().lower()
            return dep_name.lower() in content
        elif file_path.endswith("composer.json"):
            with open(file_path) as f:
                pkg = json.load(f)
            all_deps = {}
            all_deps.update(pkg.get("require", {}))
            all_deps.update(pkg.get("require-dev", {}))
            return dep_name in all_deps
        elif file_path.endswith("Cargo.toml") or file_path.endswith("go.mod"):
            return True
        return False
    except Exception:
        return False

# ── Enrich detection ────────────────────────────────────────────────────────── 

def enrich_detection(result: dict, build_context: str) -> None: 
    """ 
    Fill in language, install/build/start commands and port info based on 
    the detected framework type. 
    """ 
    type_map = { 
        "node-static": "node", 
        "node-ssr": "node", 
        "node-server": "node", 
        "python": "python", 
        "go": "go", 
        "ruby": "ruby", 
        "php": "php", 
        "rust": "rust", 
        "static": "static", 
    } 
    result["language"] = type_map.get(result["type"], "unknown") 
 
    # ── Install commands ───────────────────────────────────────────────── 
    if result["language"] == "node": 
        pm = detect_package_manager(build_context) 
        result["package_manager"] = pm 
        if pm == "pnpm": 
            result["install_command"] = "npm install -g pnpm && pnpm install --frozen-lockfile" 
        elif pm == "yarn": 
            result["install_command"] = "yarn install --frozen-lockfile" 
        else: 
            result["install_command"] = "npm ci" 
    elif result["language"] == "python": 
        result["install_command"] = "pip install -r requirements.txt" 
    elif result["language"] == "go": 
        result["install_command"] = "go mod download" 
        if not result["build_command"]: 
            result["build_command"] = "go build -o app ." 
    elif result["language"] == "ruby": 
        result["install_command"] = "bundle install" 
    elif result["language"] == "php": 
        result["install_command"] = "composer install --no-dev" 
    elif result["language"] == "rust": 
        result["install_command"] = "cargo build --release" 
 
    # ── Start commands ─────────────────────────────────────────────────── 
    if result["type"] == "node-server": 
        pkg_json = os.path.join(build_context, "package.json") 
        try: 
            with open(pkg_json) as f: 
                pkg = json.load(f) 
            result["start_command"] = pkg.get("scripts", {}).get("start", "node index.js") 
        except Exception: 
            result["start_command"] = "node index.js" 
    elif result["type"] == "node-ssr": 
        if result["framework"] == "nextjs": 
            result["start_command"] = "npx next start" 
        elif result["framework"] == "nuxt": 
            result["start_command"] = "npx nuxt start" 
        elif result["framework"] == "remix": 
            result["start_command"] = "npx remix-serve build/index.js" 
        else: 
            result["start_command"] = "npm start" 
    elif result["type"] == "python": 
        manage = os.path.join(build_context, "manage.py") 
        asgi_f = os.path.join(build_context, "asgi.py") 
        wsgi_f = os.path.join(build_context, "wsgi.py") 
        main_py = os.path.join(build_context, "main.py") 
        app_py = os.path.join(build_context, "app.py") 
        if os.path.exists(manage): 
            result["start_command"] = "python manage.py runserver 0.0.0.0:8000" 
        elif os.path.exists(asgi_f): 
            result["start_command"] = "uvicorn asgi:application --host 0.0.0.0 --port 8000" 
        elif os.path.exists(wsgi_f): 
            result["start_command"] = "gunicorn wsgi:application --bind 0.0.0.0:8000" 
        elif os.path.exists(main_py): 
            result["start_command"] = "python main.py" 
        elif os.path.exists(app_py): 
            result["start_command"] = "python app.py" 
        else: 
            result["start_command"] = f"uvicorn app.main:app --host 0.0.0.0 --port {result['port']}" 
        if result["framework"] == "fastapi": 
            result["start_command"] = "uvicorn main:app --host 0.0.0.0 --port 8000" 
        elif result["framework"] == "flask": 
            result["start_command"] = "gunicorn app:app --bind 0.0.0.0:5000" 
        elif result["framework"] == "streamlit": 
            result["start_command"] = "streamlit run main.py --server.port 8501" 
    elif result["type"] == "go": 
        result["start_command"] = "./app" 
    elif result["type"] == "ruby": 
        result["start_command"] = "rails server -b 0.0.0.0 -p 3000" if result["framework"] == "rails" else "ruby app.rb" 
    elif result["type"] == "php": 
        result["start_command"] = "php artisan serve --host 0.0.0.0 --port 8000" if result["framework"] == "laravel" else "php -S 0.0.0.0:8080 -t public" 
    elif result["type"] == "rust": 
        result["start_command"] = "./target/release/app" 

# ── Main detection entry point ───────────────────────────────────────────────

def detect_framework(
    build_context: str,
    user_framework: Optional[str] = None,
) -> dict:
    """
    Scan *build_context* (a directory path) and return a dict describing the
    detected framework, language, package manager, and all commands needed to
    build and run the project.

    If *user_framework* is set to a known framework name (e.g. ``"nextjs"``)
    it will be used directly instead of auto-detecting.  Pass ``"auto"`` to
    force auto-detection.
    """
    result = {
        "framework": user_framework or "unknown",
        "type": "unknown",
        "language": "unknown",
        "build_command": None,
        "install_command": None,
        "start_command": None,
        "output_dir": None,
        "port": 3000,
        "package_manager": "npm",
    }

    # ── User-specified framework (skip auto-detect) ────────────────────
    if user_framework and user_framework != "auto":
        normalized = (
            user_framework.lower().replace(" ", "-").replace("_", "-")
        )
        if normalized in FRAMEWORK_PATTERNS:
            pattern = FRAMEWORK_PATTERNS[normalized]
            result["framework"] = normalized
            result["type"] = pattern["type"]
            result["build_command"] = pattern["build"]
            result["output_dir"] = pattern["out"]
            result["port"] = pattern["port"]
            enrich_detection(result, build_context)
            return result

    # ── Auto-detect: match against known frameworks ────────────────────
    for fw_name, pattern in FRAMEWORK_PATTERNS.items():
        file_path = os.path.join(build_context, pattern["file"])
        if not os.path.exists(file_path):
            continue
        if pattern["dep"]:
            matched = check_dependency(file_path, pattern["dep"])
            if not matched:
                continue
        result["framework"] = fw_name
        result["type"] = pattern["type"]
        result["build_command"] = pattern["build"]
        result["output_dir"] = pattern["out"]
        result["port"] = pattern["port"]
        enrich_detection(result, build_context)
        return result

    # ── Fallback: generic Node.js (package.json) ───────────────────────
    pkg_json = os.path.join(build_context, "package.json")
    if os.path.exists(pkg_json):
        result["framework"] = "node"
        result["type"] = "node-server"
        result["language"] = "node"
        result["package_manager"] = detect_package_manager(build_context)
        result["install_command"] = f"{result['package_manager']} install"
        try:
            with open(pkg_json) as f:
                pkg = json.load(f)
            if "scripts" in pkg:
                scripts = pkg["scripts"]
                if "start" in scripts:
                    result["start_command"] = scripts["start"]
                elif "dev" in scripts:
                    result["start_command"] = scripts["dev"]
        except Exception:
            pass
        return result

    # ── Fallback: Python (requirements.txt) ────────────────────────────
    req_txt = os.path.join(build_context, "requirements.txt")
    if os.path.exists(req_txt):
        result["framework"] = "python"
        result["type"] = "python"
        result["language"] = "python"
        result["install_command"] = "pip install -r requirements.txt"
        return result

    # ── Fallback: Static HTML ──────────────────────────────────────────
    index_html = os.path.join(build_context, "index.html")
    if os.path.exists(index_html):
        result["framework"] = "static"
        result["type"] = "static"
        result["language"] = "static"
        result["port"] = 80
        return result

    return result
