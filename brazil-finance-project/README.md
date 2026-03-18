# BrazilFinance Sheets - Plano de Execução Completo

## Visão Geral do Projeto

**Nome:** BrazilFinance Sheets (nome provisório)  
**O que é:** Google Sheets Add-on que permite puxar dados financeiros brasileiros com fórmulas simples  
**Exemplos:** `=BCB("selic")`, `=B3("PETR4","preco")`, `=TESOURO("IPCA+ 2035","taxa")`

**Por que existe:** Economistas, analistas e assessores no Brasil gastam horas copiando dados manualmente de sites do BCB, B3, CVM, IBGE e Tesouro Nacional para planilhas. Não existe plugin que unifique dados financeiros brasileiros.

**Público-alvo:** Economistas, analistas de gestoras, assessores de investimento, pesquisadores acadêmicos, fintechs.

**Modelo de negócio:** Freemium. Tier gratuito com fórmulas básicas, Pro a R$39/mês com acesso completo.

## Arquitetura Geral

```
┌─────────────────────────┐
│ Google Sheets Add-on    │ ← Google Apps Script (JavaScript)
│ (Custom Functions)      │
└────────┬────────────────┘
         │ HTTPS (fetch)
         ▼
┌─────────────────────────┐
│ API Backend             │ ← Python (FastAPI)
│ api.brazilfinance.com   │
│                         │
│ ┌───────────────────┐   │
│ │ Cache Layer       │   │ ← Redis ou SQLite
│ │ (TTL por fonte)   │   │
│ └───────┬───────────┘   │
│         │               │
│ ┌───────▼───────────┐   │
│ │ Data Collectors   │   │ ← Módulos por fonte
│ │ ┌─────────────┐   │   │
│ │ │ BCB (SGS)   │   │   │
│ │ │ BCB (Focus) │   │   │
│ │ │ BCB (PTAX)  │   │   │
│ │ │ B3 / Yahoo  │   │   │
│ │ │ Tesouro     │   │   │
│ │ │ IBGE (SIDRA)│   │   │
│ │ │ CVM Fundos  │   │   │
│ │ └─────────────┘   │   │
│ └───────────────────┘   │
└─────────────────────────┘
```

**Deploy:** Railway, Render ou Fly.io (free tier para começar)  
**Domínio:** brazilfinance.com.br ou similar

## Cronograma

- **Fase 1:** Backend API (Semanas 1-2)
- **Fase 2:** Google Sheets Add-on (Semanas 3-4)
- **Fase 3:** Deploy e MVP (Semana 5)
- **Fase 4:** Marketing e Growth (Semana 6+)

## MVP Features

### Backend API (/v1/)
- `/bcb/{indicator}` - Indicadores BCB (Selic, IPCA, CDI, Dólar, etc.)
- `/focus/{indicator}` - Expectativas Focus BCB
- `/b3/{ticker}` - Cotações B3 (ações, FIIs, ETFs)  
- `/tesouro/{titulo}` - Títulos Tesouro Direto
- Rate limiting por tier (free/pro)
- Cache inteligente por tipo de dado

### Google Sheets Functions
- `=BCB("selic")` - Taxa Selic atual
- `=BCB("ipca", "12m")` - IPCA últimos 12 meses
- `=FOCUS("IPCA", 2026)` - Expectativa IPCA 2026
- `=B3("PETR4")` - Cotação PETR4 atual
- `=B3("VALE3", "variacao")` - Variação % VALE3
- `=TESOURO("IPCA+ 2035", "taxa")` - Taxa IPCA+ 2035

### Monetização
- **Free:** 500 requests/dia, indicadores básicos
- **Pro (R$39/mês):** 10K requests/dia, todos indicadores
- **Team (R$149/mês):** 50K requests/dia, suporte prioritário

## Roadmap Futuro (V2)
- Crypto integration (`=CRYPTO("BTC", "BRL")`)
- Commodities (`=COMMODITIES("petroleo", "USD")`)
- Fundos CVM (`=FUNDOS("00.000.000/0001-00", "cota")`)
- Historical data (`=BCB("selic", "2020-01-01:2025-12-31")`)
- Charts and visualization helpers
- Multiple currencies support
- Real-time WebSocket feeds (premium)

---

*Projeto criado em 2026-03-18*  
*Análise e implementação por OpenClaw*