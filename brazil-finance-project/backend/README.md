# BrazilFinance API - Backend

API unificada de dados financeiros brasileiros para Google Sheets.

## Features

- **BCB SGS**: Indicadores econômicos do Banco Central (Selic, IPCA, CDI, etc.)
- **BCB Focus**: Expectativas de mercado Focus
- **B3**: Cotações de ações, FIIs e ETFs via Yahoo Finance
- **Tesouro Direto**: Taxas e preços dos títulos públicos
- **Cache inteligente**: TTL otimizado por tipo de dado
- **Rate limiting**: Controle por tier (free/pro)
- **FastAPI**: Documentação automática e performance

## Quick Start

### Desenvolvimento Local

```bash
# Clone o repositório
git clone <repo-url>
cd backend/

# Instalar dependências
pip install -r requirements.txt

# Copiar configurações
cp .env.example .env

# Rodar a API
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build e run
docker-compose up --build

# Ou apenas a API
docker build -t brazilfinance-api .
docker run -p 8000:8000 brazilfinance-api
```

## Endpoints

### Indicadores BCB
```http
GET /v1/bcb/{indicator}?period=ultimo
```
**Indicadores disponíveis**: selic, ipca, cdi, dolar, euro, igpm, ibc_br, desemprego, etc.

**Exemplos**:
- `/v1/bcb/selic` - Taxa Selic atual
- `/v1/bcb/ipca?period=12m` - IPCA últimos 12 meses  
- `/v1/bcb/dolar` - Cotação USD/BRL

### Expectativas Focus
```http
GET /v1/focus/{indicator}?year=2026&metric=mediana
```
**Indicadores**: IPCA, Selic, PIB Total, Taxa de câmbio, IGP-M

**Exemplos**:
- `/v1/focus/IPCA?year=2026` - Expectativa IPCA 2026
- `/v1/focus/Selic?year=2025&metric=media` - Expectativa Selic 2025 (média)

### Cotações B3
```http
GET /v1/b3/{ticker}?field=preco
```
**Campos**: preco, variacao, fechamento_anterior, volume, maxima, minima

**Exemplos**:
- `/v1/b3/PETR4` - Preço PETR4
- `/v1/b3/VALE3?field=variacao` - Variação % VALE3
- `/v1/b3/HGLG11` - Cotação FII HGLG11

### Tesouro Direto
```http
GET /v1/tesouro/{titulo}?field=taxa
```
**Campos**: taxa, taxa_venda, preco, preco_venda

**Exemplos**:
- `/v1/tesouro/IPCA+ 2035` - Taxa IPCA+ 2035
- `/v1/tesouro/Prefixado 2029?field=preco` - Preço Prefixado 2029

### Meta
- `GET /v1/health` - Health check
- `GET /v1/indicators` - Lista todos os indicadores

## Testes

```bash
# Instalar pytest
pip install pytest pytest-asyncio

# Rodar testes
pytest -v

# Testes específicos
pytest tests/test_collectors.py -v

# Com coverage
pytest --cov=app tests/
```

## Deploy

### Railway
```bash
# Conectar ao Railway
railway login
railway link

# Deploy
railway up
```

### Render/Fly.io
- Usar Dockerfile incluído
- Configurar variáveis de ambiente do .env.example

## Estrutura

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── collectors/          # Data collectors
│   │   ├── bcb_sgs.py      # BCB séries temporais
│   │   ├── bcb_focus.py    # BCB expectativas  
│   │   ├── b3_stocks.py    # Cotações B3
│   │   └── tesouro.py      # Tesouro Direto
│   └── cache/
│       └── cache_manager.py # Sistema de cache
├── tests/                   # Testes automatizados
├── requirements.txt         # Dependências Python
├── Dockerfile              # Container
└── docker-compose.yml      # Dev environment
```

## Monitoramento

### Logs
```bash
# Ver logs em produção
docker logs <container-id>

# Logs específicos de collector
grep "bcb_sgs" logs/app.log
```

### Health Checks
- `/v1/health` - Status da API
- Cache stats disponível via código

### Métricas Importantes
- **Taxa de cache hit**: > 70% ideal
- **Response time**: < 2s para dados cacheados
- **Error rate**: < 5% aceitável

## Limitações Conhecidas

1. **Yahoo Finance**: API não oficial, pode ter instabilidade
2. **Tesouro CSV**: URL pode mudar, implementar fallbacks
3. **Cache memory**: Usar Redis em produção para escala
4. **Rate limiting**: Implementação simples, melhorar para produção

## Roadmap

- [ ] **Redis cache** para produção
- [ ] **Metrics/monitoring** (Prometheus)
- [ ] **API versioning** (v2)
- [ ] **WebSocket** real-time feeds
- [ ] **Crypto endpoints**
- [ ] **CVM fundos** integration
- [ ] **Historical data** endpoints

## Contribuição

1. Fork do repositório
2. Criar feature branch
3. Implementar com testes
4. Pull request com descrição

## Licença

MIT License - Ver arquivo LICENSE