#!/bin/bash
# UAT Test Codebases Download Script
# Downloads 10 opensource projects (polyglot: Python, TypeScript, Go)

set -e

UAT_DIR="${1:-$HOME/Projects/shannon-insight/uat/codebases}"
mkdir -p "$UAT_DIR"
cd "$UAT_DIR"

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Downloading 10 UAT Test Codebases                               ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

# ─────────────────────────────────────────────────────────────────────────
# LARGE POLYGLOT PROJECTS (Frontend + Backend)
# ─────────────────────────────────────────────────────────────────────────

echo ""
echo "▶ [1/10] Sentry (Python + TypeScript/React) - Error tracking platform"
if [ ! -d "sentry" ]; then
    git clone --depth 1 https://github.com/getsentry/sentry.git
else
    echo "  Already exists, skipping..."
fi

echo ""
echo "▶ [2/10] Grafana (Go + TypeScript/React) - Observability platform"
if [ ! -d "grafana" ]; then
    git clone --depth 1 https://github.com/grafana/grafana.git
else
    echo "  Already exists, skipping..."
fi

echo ""
echo "▶ [3/10] Mattermost Server (Go) - Team collaboration"
if [ ! -d "mattermost" ]; then
    git clone --depth 1 https://github.com/mattermost/mattermost.git
else
    echo "  Already exists, skipping..."
fi

echo ""
echo "▶ [4/10] Cal.com (TypeScript fullstack) - Scheduling platform"
if [ ! -d "cal.com" ]; then
    git clone --depth 1 https://github.com/calcom/cal.com.git
else
    echo "  Already exists, skipping..."
fi

echo ""
echo "▶ [5/10] Supabase (TypeScript + Go + PostgreSQL) - Firebase alternative"
if [ ! -d "supabase" ]; then
    git clone --depth 1 https://github.com/supabase/supabase.git
else
    echo "  Already exists, skipping..."
fi

# ─────────────────────────────────────────────────────────────────────────
# MEDIUM PYTHON PROJECTS (well-typed)
# ─────────────────────────────────────────────────────────────────────────

echo ""
echo "▶ [6/10] FastAPI (Python) - Modern web framework"
if [ ! -d "fastapi" ]; then
    git clone --depth 1 https://github.com/tiangolo/fastapi.git
else
    echo "  Already exists, skipping..."
fi

echo ""
echo "▶ [7/10] httpx (Python) - Async HTTP client"
if [ ! -d "httpx" ]; then
    git clone --depth 1 https://github.com/encode/httpx.git
else
    echo "  Already exists, skipping..."
fi

echo ""
echo "▶ [8/10] Pydantic (Python) - Data validation"
if [ ! -d "pydantic" ]; then
    git clone --depth 1 https://github.com/pydantic/pydantic.git
else
    echo "  Already exists, skipping..."
fi

# ─────────────────────────────────────────────────────────────────────────
# SMALL PROJECTS
# ─────────────────────────────────────────────────────────────────────────

echo ""
echo "▶ [9/10] Rich (Python) - Terminal formatting"
if [ ! -d "rich" ]; then
    git clone --depth 1 https://github.com/Textualize/rich.git
else
    echo "  Already exists, skipping..."
fi

echo ""
echo "▶ [10/10] Typer (Python) - CLI framework"
if [ ! -d "typer" ]; then
    git clone --depth 1 https://github.com/tiangolo/typer.git
else
    echo "  Already exists, skipping..."
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║  Download Complete!                                              ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "Codebases saved to: $UAT_DIR"
echo ""
du -sh "$UAT_DIR"/* 2>/dev/null | sort -h
