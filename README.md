# SLM Hosting

Production-ready self-hosted SLM (Small Language Model) using **vLLM + FastAPI + Nginx**.

---

## Architecture

```
Client → Nginx (rate limit) → FastAPI Wrapper (auth, log, timeout) → vLLM (inference)
```

## Stack

| Layer | Technology |
|-------|-----------|
| Inference engine | vLLM `v0.6.6` (GPU) |
| Model | `Qwen/Qwen2.5-1.5B-Instruct-AWQ` |
| API Wrapper | FastAPI + httpx (async) |
| Reverse proxy | Nginx (rate limit 10r/s) |
| Containerization | Docker Compose |

---

## Quick Start

### GPU
```bash
# Step 1: Download model once (never inside Docker!)
bash scripts/download_model.sh

# Step 2: Configure environment
cp .env.example .env

# Step 3: Start full stack
docker compose -f docker/docker-compose.yml up --build -d

# Step 4: Verify
curl http://localhost/v1/health
```

---

## API Usage

```bash
curl -X POST http://localhost/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-key-change-me" \
  -d '{
    "messages": [{"role": "user", "content": "Giải thích AI là gì?"}],
    "max_tokens": 256
  }'
```

---

## Key Design Decisions (Avoids 8/8 common mistakes)

See [`docs/RUNBOOK.md`](docs/RUNBOOK.md) for full avoidance table.

1. **Model downloaded outside container** — mounted as volume
2. **vLLM never exposed publicly** — only Nginx port 80 is open
3. **`--max-model-len 2048`** — prevents KV cache OOM
4. **AWQ quantization** — 60% less VRAM
5. **Deep health check** — waits for model to load before routing traffic
6. **Async endpoints** — `httpx.AsyncClient`, zero thread blocking
7. **`--gpu-memory-utilization 0.75`** — 25% GPU headroom
8. **Timeout + max_tokens cap** — no runaway requests

---

## Project Structure

```
slm-hosting/
├── app/               # FastAPI wrapper
│   ├── main.py
│   ├── api/v1/        # Endpoints + schemas
│   ├── domains/       # vLLM client service
│   └── core/          # Config, logging, exceptions
├── nginx/             # Reverse proxy + rate limit
├── docker/            # Dockerfile + Docker Compose (GPU & CPU)
├── scripts/           # One-time model download
└── docs/              # RUNBOOK.md + screenshots
```
