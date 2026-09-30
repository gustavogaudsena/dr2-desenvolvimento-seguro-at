# API de agendamento de consultas

## Requisitos

- Python 3.13 ou superior
- Docker (apenas para usar o ZAP)

## Executar a aplicação

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

O `.env.example` usa SQLite. A API fica em `http://localhost:8080` e o Swagger em `http://localhost:8080/docs`.

## Testes

```bash
pytest
```

## Scan passivo com ZAP

Com a API em execução e dados fictícios, inicie o ZAP:

```bash
docker compose -f compose.zap.yaml up -d
```

A interface fica em `http://localhost:8081/zap/` e o proxy em `http://127.0.0.1:8090`. Nos arquivos [`rest/`](rest/), deixe ativa uma única linha `@apiUrl` no topo: use `localhost` para acesso direto ou `host.docker.internal` ao passar pelo proxy do ZAP (HTTP ou HTTPS, conforme a API estiver rodando). Configure o cliente HTTP para usar o proxy, envie as requisições e gere o relatório pela interface do ZAP. O scan é passivo.

Para encerrar:

```bash
docker compose -f compose.zap.yaml down
```
