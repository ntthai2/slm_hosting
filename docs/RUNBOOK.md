# RUNBOOK — SLM Hosting Challenge 1

## Avoidance Table: 8/8 Common Mistakes

| # | Mistake | How this project avoids it |
|---|---------|---------------------------|
| 1 🟢 | Download model inside Dockerfile | `scripts/download_model.sh` downloads once to `./models/`. Docker Compose mounts `-v ./models:/models`. Container never pulls from HuggingFace. |
| 2 🟢 | Expose vLLM port directly | vLLM uses `expose: "8000"` (internal only). Nginx on port 80 is the only public entrypoint. |
| 3 🟢 | No `--max-model-len` | Set `--max-model-len 2048`. Prevents KV cache OOM on GPU. |
| 4 🟡 | No quantization on weak GPU | Using `Qwen2.5-1.5B-Instruct-AWQ` with `--quantization awq --dtype half`. ~60% less VRAM. |
| 5 🟡 | Health check doesn't verify model loaded | `GET /v1/health` calls vLLM's `/health` endpoint which only returns 200 when model is fully loaded. `depends_on: condition: service_healthy` chains startup correctly. |
| 6 🟡 | Sync endpoint blocks threads | All endpoints use `async def`. `VllmClient` uses `httpx.AsyncClient`. Zero thread blocking. |
| 7 🔴 | `--gpu-memory-utilization` defaults to 0.9 | Set to `0.75` — leaves 25% headroom for OS, monitoring, peak spikes. |
| 8 🔴 | No timeout + no `max_tokens` cap | `httpx.AsyncClient(timeout=30.0)`. Every request capped at `max_tokens=512` in `vllm_client.py`. |

---

## Quick Start

### GPU setup
```bash
# 1. Download model once
bash scripts/download_model.sh

# 2. Copy env file
cp .env.example .env

# 3. Start stack
docker compose -f docker/docker-compose.yml up --build -d

# 4. Check health
curl http://localhost/v1/health
```

### CPU setup (no GPU)
```bash
cp .env.example .env
docker compose -f docker/docker-compose-cpu.yml up --build -d

# Pull model into Ollama (first time only)
docker exec -it ollama ollama pull qwen2.5:1.5b

curl http://localhost/v1/health
```

---

## Test Requests

### Chat completion
```bash
curl -X POST http://localhost/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer secret-key-change-me" \
  -d '{
    "messages": [{"role": "user", "content": "Xin chào! Bạn là ai?"}],
    "max_tokens": 128
  }'
```

### Health check
```bash
curl http://localhost/v1/health
# {"status":"ok","model_loaded":true,"vllm_url":"http://vllm:8000"}
```

### Test rate limit (Nginx returns 429 after burst)
```bash
for i in {1..30}; do curl -s -o /dev/null -w "%{http_code}\n" http://localhost/v1/health; done
```

---

## Data Flow

```
Client
  │
  │ POST /v1/chat/completions
  ▼
Nginx (:80)
  │ rate limit 10r/s, burst=20
  │ reverse proxy
  ▼
FastAPI API Wrapper (:8080)
  │ auth check (API key)
  │ validate request (Pydantic)
  │ enforce max_tokens cap
  │ structured JSON log
  │ async HTTP (httpx)
  ▼
vLLM (:8000) — internal only
  │ Qwen2.5-1.5B-AWQ inference
  ▼
FastAPI (response)
  │ log latency + token usage
  ▼
Client
```

---

## Incident Response

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| `curl /v1/health` → `degraded` | vLLM still loading | Wait 60s, check `docker logs vllm-qwen` |
| 429 Too Many Requests | Nginx rate limit triggered | Normal — reduce request rate |
| 504 Gateway Timeout | Prompt too long or GPU busy | Reduce `max_tokens`, check `nvidia-smi` |
| 503 Service Unavailable | vLLM container crashed | `docker compose restart vllm` |
| OOM on GPU | `gpu-memory-utilization` too high | Lower to `0.6`, restart vLLM |
