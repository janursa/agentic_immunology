#!/usr/bin/env bash
# Sets up pi (https://github.com/earendil-works/pi) as a Claude-Code-style
# subagent runtime for this repo: installs pi, installs the subagent
# delegation extension, and regenerates .pi/agents/*.md + .pi/SYSTEM.md from
# agents/*.md + ciim_agentic.md, translating tools/model per agents/models.yaml
# (Claude Code keeps reading agents/*.md directly; nothing there is touched).
set -euo pipefail
cd "$(dirname "$0")"
REPO_ROOT="$(pwd)"
MODELS_YAML="$REPO_ROOT/agents/models.yaml"

# 1. Install pi if missing
if ! command -v pi >/dev/null 2>&1; then
  if ! command -v npm >/dev/null 2>&1; then
    echo "error: npm not found. Load a Node.js module first, e.g.:" >&2
    echo "  module load nodejs   # or: conda install -n base nodejs" >&2
    exit 1
  fi
  echo "Installing pi..."
  npm install -g @earendil-works/pi-coding-agent
fi

# 2. Install the subagent delegation tool (user-level, idempotent)
PI_PKG="$(npm root -g)/@earendil-works/pi-coding-agent"
mkdir -p ~/.pi/agent/extensions/subagent
ln -sf "$PI_PKG/examples/extensions/subagent/index.ts"  ~/.pi/agent/extensions/subagent/index.ts
ln -sf "$PI_PKG/examples/extensions/subagent/agents.ts" ~/.pi/agent/extensions/subagent/agents.ts

# 2b. Register the GWDG academic-cloud endpoint as a pi provider (idempotent
#     upsert into pi's own config, ~/.pi/agent/models.json). Needs GWDG_API_KEY
#     in .env (gitignored) or the environment; skipped otherwise.
[ -f "$REPO_ROOT/.env" ] && set -a && source "$REPO_ROOT/.env" && set +a
if [ -n "${GWDG_API_KEY:-}" ]; then
  python3 - "$GWDG_API_KEY" <<'PYEOF'
import json, os, sys

path = os.path.expanduser("~/.pi/agent/models.json")
key = sys.argv[1]
# (id, display name, reasoning) — full catalog from https://chat-ai.academiccloud.de/v1/models,
# so any id can be picked later in agents/models.yaml without touching this script.
models = [
    ("apertus-70b-instruct-2509", "Apertus 70B Instruct 2509", False),
    ("qwen3.5-122b-a10b", "Qwen 3.5 122B A10B", True),
    ("glm-4.7", "GLM-4.7", False),
    ("devstral-2-123b-instruct-2512", "Devstral 2 123B Instruct", False),
    ("qwen3-omni-30b-a3b-instruct", "Qwen 3 Omni 30B A3B Instruct", False),
    ("qwen3-coder-next", "Qwen 3 Coder Next", False),
    ("qwen3.6-35b-a3b", "Qwen 3.6 35B A3B", False),
    ("qwen3.6-27b", "Qwen 3.6 27B", False),
    ("gemma-4-31b-it", "Gemma 4 31B Instruct", False),
    ("mistral-large-3-675b-instruct-2512", "Mistral Large 3 675B Instruct", False),
    ("qwen3.5-397b-a17b", "Qwen 3.5 397B A17B", True),
    ("meta-llama-3.1-8b-instruct", "Meta Llama 3.1 8B Instruct", False),
    ("openai-gpt-oss-120b", "OpenAI GPT-OSS 120B", False),
    ("qwen3-30b-a3b-instruct-2507", "Qwen 3 30B A3B Instruct 2507", False),
    ("medgemma-27b-it", "MedGemma 27B Instruct", False),
]

try:
    with open(path) as f:
        cfg = json.load(f)
except FileNotFoundError:
    cfg = {}
cfg.setdefault("providers", {})["gwdg"] = {
    "baseUrl": "https://chat-ai.academiccloud.de/v1",
    "api": "openai-completions",
    "apiKey": key,
    "compat": {"supportsDeveloperRole": False, "supportsReasoningEffort": False},
    "models": [
        {
            "id": mid, "name": name, "reasoning": reasoning,
            "contextWindow": 131072,  # ponytail: placeholder, GWDG doesn't publish this; raise if truncation is observed
            "cost": {"input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0},
        }
        for mid, name, reasoning in models
    ],
}
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w") as f:
    json.dump(cfg, f, indent=2)
print(f"registered gwdg provider ({len(models)} models) in {path}")
PYEOF
else
  echo "GWDG_API_KEY not set (add it to .env) - skipping gwdg provider registration" >&2
fi

# 3. Translate Claude tool names -> pi built-in tool names (WebSearch/WebFetch/Agent
#    dropped: pi has no equivalent yet)
map_tools() {
  local out=""
  IFS=',' read -ra parts <<< "$1"
  for t in "${parts[@]}"; do
    t="$(echo "$t" | xargs)"
    case "$t" in
      Read)  out+="read, " ;;
      Write) out+="write, " ;;
      Edit)  out+="edit, " ;;
      Bash)  out+="bash, " ;;
      Grep)  out+="grep, " ;;
      Glob)  out+="find, " ;;
    esac
  done
  echo "${out%, }"
}

pi_model_for() {  # $1 = agent name, reads agents/models.yaml
  grep "^$1:" "$MODELS_YAML" | sed -E 's/.*pi:\s*([^, }]+).*/\1/'
}

yaml_quote() {  # pi's frontmatter parser is strict YAML; quote values that may contain ": "
  printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'
}

body_of() {  # strip YAML frontmatter, print the rest
  awk '/^---$/{c++; next} c>=2' "$1"
}

# 4/5. Regenerate project-level pi agents + system prompt from agents/*.md.
#      This is a shared repo checkout: only whoever owns .pi/ (or has ACL
#      write) can rebuild it. Others just use what's already there.
write_check_dir="$REPO_ROOT/.pi"
[ -d "$write_check_dir" ] || write_check_dir="$REPO_ROOT"

if [ ! -w "$write_check_dir" ]; then
  echo "no write access to $write_check_dir - skipping .pi/agents and .pi/SYSTEM.md regeneration (using existing files as-is)" >&2
else
  # 4. Regenerate project-level pi agents from agents/*.md
  rm -rf "$REPO_ROOT/.pi/agents"
  mkdir -p "$REPO_ROOT/.pi/agents"

  for f in "$REPO_ROOT"/agents/*.md; do
    base="$(basename "$f" .md)"
    [ "$base" = "list" ] && continue

    name=$(grep "^name:"        "$f" | head -1 | sed 's/name: *//')
    desc=$(grep "^description:" "$f" | head -1 | sed 's/description: *//')
    tools_line=$(grep "^tools:" "$f" | head -1 | sed 's/tools: *//')
    model=$(pi_model_for "$name")
    pi_tools=$(map_tools "$tools_line")

    out="$REPO_ROOT/.pi/agents/$base.md"
    {
      echo "---"
      echo "name: \"$(yaml_quote "$name")\""
      echo "description: \"$(yaml_quote "$desc")\""
      echo "tools: $pi_tools"
      echo "model: $model"
      echo "---"
      echo
      body_of "$f"
    } > "$out"
    echo "generated: .pi/agents/$base.md (model=$model, tools=$pi_tools)"
  done

  # 5. Main instructor -> pi's project system prompt (replaces default prompt)
  #    The agentScope reminder goes FIRST: the subagent tool defaults to
  #    agentScope "user" and ignores project agents unless told otherwise on
  #    every call, so this must not be missed on the first tool call.
  {
    echo "CRITICAL: this project's subagents (study_designer_agent, data_analyst_agent,"
    echo "etc.) are registered at PROJECT scope in .pi/agents, not user scope. The"
    echo "\`subagent\` tool defaults to agentScope \"user\" and will report agents as"
    echo "unknown unless you pass \`agentScope: \"both\"\` on EVERY call."
    echo
    echo "---"
    echo
    body_of "$REPO_ROOT/ciim_agentic.md"
  } > "$REPO_ROOT/.pi/SYSTEM.md"
  echo "generated: .pi/SYSTEM.md"
fi

echo
echo "Done. Launch with:"
echo "  cd $REPO_ROOT && pi --model $(pi_model_for ciim_agentic)"
echo "(model is provider-qualified, e.g. gwdg/qwen3-coder-next or openai/gpt-4o; the openai provider"
echo " reads OPENAI_API_KEY from the environment, gwdg's key is already registered in models.json)"
