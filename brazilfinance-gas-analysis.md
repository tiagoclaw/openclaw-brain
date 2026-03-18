# Brazil Finance API - Google Apps Script Analysis

## Código Analisado - 2026-03-18

### Estrutura Atual
- **Linguagem:** JavaScript (Google Apps Script)
- **Target:** Google Sheets Custom Functions
- **API:** brazilfinance.com.br/v1
- **Endpoints:** BCB, Focus, B3, Tesouro Direto

## Análise do Código

### ✅ Pontos Fortes

**1. Arquitetura Limpa:**
- Separação clara por domínios (macro, ações, tesouro)
- Custom functions bem documentadas com JSDoc
- Error handling básico implementado

**2. Funcionalidades Core:**
- **BCB()** - Indicadores macro (Selic, IPCA, CDI, Dólar)
- **FOCUS()** - Expectativas de mercado BCB
- **B3()** - Cotações B3 (ações, FIIs, ETFs)
- **TESOURO()** - Títulos do Tesouro Direto

**3. UX Google Sheets:**
- Parâmetros opcionais com defaults sensatos
- Mensagens de erro claras
- Sintaxe intuitiva: `=BCB("selic")`, `=B3("PETR4")`

### 🔧 Oportunidades de Melhoria

**1. Completar função TESOURO:**
```javascript
function TESOURO(titulo, campo) {
  if (!titulo) return "Uso: =TESOURO(\"IPCA+ 2035\") ou =TESOURO(\"Prefixado 2029\", \"preco\")";
  campo = campo || "taxa";
  
  var url = API_URL + "/tesouro/" + encodeURIComponent(titulo) + "?field=" + encodeURIComponent(campo);
  
  try {
    var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    var data = JSON.parse(response.getContentText());
    
    if (data.erro) return "ERRO: " + data.erro;
    return data.valor;
  } catch(e) {
    return "ERRO: " + e.message;
  }
}
```

**2. Adicionar Rate Limiting:**
```javascript
// Evitar spam de requests
var lastRequestTime = {};

function rateLimitCheck(funcName) {
  var now = new Date().getTime();
  var key = funcName;
  if (lastRequestTime[key] && (now - lastRequestTime[key]) < 1000) {
    return false; // Rate limited
  }
  lastRequestTime[key] = now;
  return true;
}
```

**3. Cache para Performance:**
```javascript
// Cache results temporário (limitação: custom functions não suportam CacheService)
var memCache = {};

function getCachedOrFetch(url, cacheKey, ttlMinutes) {
  var now = new Date().getTime();
  var cached = memCache[cacheKey];
  
  if (cached && (now - cached.timestamp) < (ttlMinutes * 60 * 1000)) {
    return cached.data;
  }
  
  // Fetch fresh data
  var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
  var data = JSON.parse(response.getContentText());
  
  memCache[cacheKey] = {
    data: data,
    timestamp: now
  };
  
  return data;
}
```

### 🚀 Funcionalidades Adicionais Sugeridas

**1. Função CRYPTO:**
```javascript
/**
 * Busca cotação de criptomoedas.
 *
 * @param {string} crypto - "BTC", "ETH", "ADA", etc.
 * @param {string} [moeda="BRL"] - "BRL", "USD"
 * @return {number} Preço em BRL
 * @customfunction
 */
function CRYPTO(crypto, moeda) {
  // Implementation
}
```

**2. Função COMMODITIES:**
```javascript
/**
 * Busca preços de commodities.
 *
 * @param {string} commodity - "petroleo", "ouro", "cafe", "soja"
 * @param {string} [unidade="BRL"] - "BRL", "USD"
 * @return {number} Preço
 * @customfunction
 */
function COMMODITIES(commodity, unidade) {
  // Implementation
}
```

**3. Função FUNDOS:**
```javascript
/**
 * Busca dados de fundos de investimento.
 *
 * @param {string} cnpj - CNPJ do fundo
 * @param {string} [campo="cota"] - "cota", "patrimonio", "rentabilidade"
 * @return {number} Valor do campo
 * @customfunction
 */
function FUNDOS(cnpj, campo) {
  // Implementation
}
```

## Uso Prático - Exemplos

### Dashboard Macro Brasil
```
| Indicador | Atual | Expectativa 2026 |
|-----------|-------|------------------|
| Selic     | =BCB("selic")     | =FOCUS("Selic", 2026) |
| IPCA      | =BCB("ipca")      | =FOCUS("IPCA", 2026) |
| PIB       | =BCB("pib")       | =FOCUS("PIB Total", 2026) |
| Dólar     | =BCB("dolar")     | =FOCUS("Taxa de câmbio", 2026) |
```

### Portfolio Tracking
```
| Ticker | Preço | Variação |
|--------|-------|----------|
| PETR4  | =B3("PETR4") | =B3("PETR4", "variacao") |
| VALE3  | =B3("VALE3") | =B3("VALE3", "variacao") |
| HGLG11 | =B3("HGLG11") | =B3("HGLG11", "variacao") |
```

### Tesouro Direto
```
| Título | Taxa | Preço |
|--------|------|-------|
| IPCA+ 2035 | =TESOURO("IPCA+ 2035") | =TESOURO("IPCA+ 2035", "preco") |
| Prefixado 2029 | =TESOURO("Prefixado 2029") | =TESOURO("Prefixado 2029", "preco") |
```

## Arquitetura API Recomendada

### Endpoints Core
- `GET /v1/bcb/{indicator}` - Indicadores BCB
- `GET /v1/focus/{indicator}` - Expectativas Focus  
- `GET /v1/b3/{ticker}` - Cotações B3
- `GET /v1/tesouro/{title}` - Tesouro Direto
- `GET /v1/crypto/{symbol}` - Criptomoedas
- `GET /v1/commodities/{name}` - Commodities
- `GET /v1/fundos/{cnpj}` - Fundos

### Response Format
```json
{
  "valor": 10.75,
  "data_atualizacao": "2026-03-18T04:41:00Z",
  "fonte": "BCB",
  "metadados": {
    "periodo": "ultimo",
    "unidade": "%"
  }
}
```

## Próximos Passos

1. **Completar função TESOURO**
2. **Implementar rate limiting**
3. **Adicionar crypto/commodities**
4. **Criar documentação para usuários finais**
5. **Testes com diferentes cenários de erro**
6. **Deploy e monitoring da API**

## Avaliação Final

**🎯 Código sólido para MVP!**
- Base bem estruturada
- Funcionalidades essenciais cobertas
- Pronto para expansão
- UX intuitiva para usuários Google Sheets

**Score: 8.5/10** - Excelente fundação para fintech brasileira!