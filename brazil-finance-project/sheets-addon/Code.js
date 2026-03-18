/**
 * BrazilFinance Sheets - Custom Functions para Google Sheets
 * 
 * Fórmulas disponíveis:
 * =BCB("selic") - Taxa Selic atual
 * =FOCUS("IPCA", 2026) - Expectativa IPCA 2026
 * =B3("PETR4") - Cotação PETR4
 * =TESOURO("IPCA+ 2035", "taxa") - Taxa título IPCA+ 2035
 */

// ============================================================
// CONFIGURAÇÕES
// ============================================================

var API_BASE_URL = "https://api.brazilfinance.com.br/v1";

/**
 * Salva API key do usuário nas propriedades.
 */
function setUserApiKey(apiKey) {
  var props = PropertiesService.getUserProperties();
  props.setProperty("BRAZILFINANCE_API_KEY", apiKey);
}

/**
 * Remove API key do usuário.
 */
function clearUserApiKey() {
  var props = PropertiesService.getUserProperties();
  props.deleteProperty("BRAZILFINANCE_API_KEY");
}

// ============================================================
// BLOCO 1: INDICADORES MACRO (BCB)
// ============================================================

/**
 * Busca indicador do Banco Central do Brasil.
 *
 * @param {string} indicador - Nome do indicador: "selic", "ipca", "cdi", "dolar", "igpm", "ibc_br", etc.
 * @param {string} [periodo="ultimo"] - "ultimo" (padrão), "12m", ou "DD/MM/YYYY:DD/MM/YYYY"
 * @return {number} Valor do indicador
 * @customfunction
 */
function BCB(indicador, periodo) {
  if (!indicador) return "❌ Uso: =BCB(\"selic\") ou =BCB(\"ipca\", \"12m\")";
  
  periodo = periodo || "ultimo";
  
  var url = API_BASE_URL + "/bcb/" + encodeURIComponent(indicador) + 
            "?period=" + encodeURIComponent(periodo);
  
  try {
    var response = apiRequest(url, "bcb_sgs");
    
    if (response.erro) {
      return "❌ ERRO: " + response.erro;
    }
    
    return response.valor;
    
  } catch(e) {
    return "❌ ERRO: " + e.message;
  }
}

/**
 * Busca expectativas Focus do Banco Central.
 *
 * @param {string} indicador - "IPCA", "Selic", "PIB Total", "Taxa de câmbio", "IGP-M"
 * @param {number|string} ano - Ano de referência (ex: 2025, 2026)
 * @param {string} [metrica="mediana"] - "mediana", "media", "minimo", "maximo"
 * @return {number} Valor da expectativa
 * @customfunction
 */
function FOCUS(indicador, ano, metrica) {
  if (!indicador) return "❌ Uso: =FOCUS(\"IPCA\", 2026) ou =FOCUS(\"Selic\", 2026, \"media\")";
  
  metrica = metrica || "mediana";
  
  var url = API_BASE_URL + "/focus/" + encodeURIComponent(indicador);
  url += "?metric=" + encodeURIComponent(metrica);
  if (ano) url += "&year=" + ano;
  
  try {
    var response = apiRequest(url, "bcb_focus");
    
    if (response.erro) {
      return "❌ ERRO: " + response.erro;
    }
    
    return response.valor;
    
  } catch(e) {
    return "❌ ERRO: " + e.message;
  }
}

// ============================================================
// BLOCO 2: COTAÇÕES B3 (Ações, FIIs, ETFs)
// ============================================================

/**
 * Busca cotação de ação, FII ou ETF da B3.
 *
 * @param {string} ticker - Código do ativo (ex: "PETR4", "VALE3", "HGLG11")
 * @param {string} [campo="preco"] - "preco", "variacao", "fechamento_anterior", "volume"
 * @return {number} Valor do campo
 * @customfunction
 */
function B3(ticker, campo) {
  if (!ticker) return "❌ Uso: =B3(\"PETR4\") ou =B3(\"VALE3\", \"variacao\")";
  
  campo = campo || "preco";
  
  var url = API_BASE_URL + "/b3/" + encodeURIComponent(ticker.toUpperCase()) + 
            "?field=" + encodeURIComponent(campo);
  
  try {
    var response = apiRequest(url, "b3_quote");
    
    if (response.erro) {
      return "❌ ERRO: " + response.erro;
    }
    
    return response.valor;
    
  } catch(e) {
    return "❌ ERRO: " + e.message;
  }
}

// ============================================================
// BLOCO 3: TESOURO DIRETO
// ============================================================

/**
 * Busca dados de título do Tesouro Direto.
 *
 * @param {string} titulo - Nome do título (ex: "IPCA+ 2035", "Prefixado 2029", "Selic 2029")
 * @param {string} [campo="taxa"] - "taxa", "taxa_venda", "preco", "preco_venda"
 * @return {number} Valor do campo
 * @customfunction
 */
function TESOURO(titulo, campo) {
  if (!titulo) return "❌ Uso: =TESOURO(\"IPCA+ 2035\") ou =TESOURO(\"Prefixado 2029\", \"preco\")";
  
  campo = campo || "taxa";
  
  var url = API_BASE_URL + "/tesouro/" + encodeURIComponent(titulo) + 
            "?field=" + encodeURIComponent(campo);
  
  try {
    var response = apiRequest(url, "tesouro");
    
    if (response.erro) {
      return "❌ ERRO: " + response.erro;
    }
    
    return response.valor;
    
  } catch(e) {
    return "❌ ERRO: " + e.message;
  }
}

// ============================================================
// FUNÇÕES AUXILIARES AVANÇADAS
// ============================================================

/**
 * Busca múltiplas cotações de uma vez.
 *
 * @param {string} tickers - Tickers separados por vírgula (ex: "PETR4,VALE3,ITUB4")
 * @param {string} [campo="preco"] - Campo desejado
 * @return {Array} Array com as cotações
 * @customfunction
 */
function B3_MULTIPLOS(tickers, campo) {
  if (!tickers) return "❌ Uso: =B3_MULTIPLOS(\"PETR4,VALE3,ITUB4\")";
  
  var tickerList = tickers.split(',');
  var results = [];
  
  for (var i = 0; i < tickerList.length; i++) {
    var ticker = tickerList[i].trim();
    if (ticker) {
      try {
        var value = B3(ticker, campo);
        results.push([ticker, value]);
      } catch(e) {
        results.push([ticker, "ERRO: " + e.message]);
      }
    }
  }
  
  return results;
}

/**
 * Cria resumo das principais expectativas econômicas.
 *
 * @param {number} [ano] - Ano de referência (padrão: próximo ano)
 * @return {Array} Array com resumo das expectativas
 * @customfunction
 */
function FOCUS_RESUMO(ano) {
  if (!ano) {
    ano = new Date().getFullYear() + 1;
  }
  
  var indicadores = ["IPCA", "Selic", "PIB Total", "Taxa de câmbio"];
  var results = [["Indicador", "Expectativa " + ano]];
  
  for (var i = 0; i < indicadores.length; i++) {
    try {
      var valor = FOCUS(indicadores[i], ano);
      results.push([indicadores[i], valor]);
    } catch(e) {
      results.push([indicadores[i], "ERRO"]);
    }
  }
  
  return results;
}

/**
 * Busca curva de juros do Tesouro por tipo.
 *
 * @param {string} [tipo="IPCA+"] - Tipo do título ("IPCA+", "Prefixado", "Selic")
 * @return {Array} Array com curva de taxas
 * @customfunction
 */
function TESOURO_CURVA(tipo) {
  tipo = tipo || "IPCA+";
  
  var titulos = [
    tipo + " 2026", tipo + " 2029", tipo + " 2032", 
    tipo + " 2035", tipo + " 2040", tipo + " 2045"
  ];
  
  var results = [["Vencimento", "Taxa"]];
  
  for (var i = 0; i < titulos.length; i++) {
    try {
      var taxa = TESOURO(titulos[i], "taxa");
      if (typeof taxa === 'number') {
        results.push([titulos[i], taxa]);
      }
    } catch(e) {
      // Ignorar títulos que não existem
    }
  }
  
  return results;
}

// ============================================================
// BLOCO BÔNUS: HELPER FUNCTIONS
// ============================================================

/**
 * Lista todos os indicadores BCB disponíveis.
 *
 * @return {string} Lista de indicadores
 * @customfunction
 */
function BCB_LISTA() {
  try {
    var response = apiRequest(API_BASE_URL + "/v1/indicators", "default");
    if (response.erro) return "❌ ERRO: " + response.erro;
    
    return response.bcb_sgs ? response.bcb_sgs.indicators.join(", ") : "Indicadores não disponíveis";
  } catch(e) {
    return "❌ ERRO: " + e.message;
  }
}

/**
 * Retorna a data da última atualização de um indicador.
 *
 * @param {string} indicador - Nome do indicador BCB
 * @return {string} Data da última atualização
 * @customfunction
 */
function BCB_DATA(indicador) {
  if (!indicador) return "❌ Uso: =BCB_DATA(\"selic\")";
  
  var url = API_BASE_URL + "/v1/bcb/" + encodeURIComponent(indicador) + "?period=ultimo";
  
  try {
    var response = apiRequest(url, "bcb_sgs");
    if (response.erro) return "❌ ERRO: " + response.erro;
    
    return response.data || "Data não disponível";
  } catch(e) {
    return "❌ ERRO: " + e.message;
  }
}

/**
 * Retorna resumo de múltiplos indicadores macro.
 *
 * @param {number} [ano] - Ano para expectativas (padrão: próximo ano)
 * @return {Array} Array com resumo macro
 * @customfunction
 */
function MACRO_RESUMO(ano) {
  if (!ano) {
    ano = new Date().getFullYear() + 1;
  }
  
  var results = [["Indicador", "Atual", "Expectativa " + ano]];
  
  var indicadores = [
    {nome: "Selic", atual: "selic", focus: "Selic"},
    {nome: "IPCA", atual: "ipca", focus: "IPCA"}, 
    {nome: "PIB", atual: "ibc_br", focus: "PIB Total"},
    {nome: "Dólar", atual: "dolar", focus: "Taxa de câmbio"}
  ];
  
  for (var i = 0; i < indicadores.length; i++) {
    try {
      var atual = BCB(indicadores[i].atual);
      var expectativa = FOCUS(indicadores[i].focus, ano);
      results.push([indicadores[i].nome, atual, expectativa]);
    } catch(e) {
      results.push([indicadores[i].nome, "ERRO", "ERRO"]);
    }
  }
  
  return results;
}

/**
 * Compara performance de múltiplos ativos.
 *
 * @param {string} tickers - Tickers separados por vírgula
 * @return {Array} Array com comparação
 * @customfunction
 */
function B3_COMPARAR(tickers) {
  if (!tickers) return "❌ Uso: =B3_COMPARAR(\"PETR4,VALE3,ITUB4\")";
  
  var tickerList = tickers.split(',');
  var results = [["Ticker", "Preço", "Variação %"]];
  
  for (var i = 0; i < tickerList.length && i < 10; i++) {
    var ticker = tickerList[i].trim();
    if (ticker) {
      try {
        var preco = B3(ticker, "preco");
        var variacao = B3(ticker, "variacao");
        results.push([ticker.toUpperCase(), preco, variacao]);
      } catch(e) {
        results.push([ticker.toUpperCase(), "ERRO", "ERRO"]);
      }
    }
  }
  
  return results;
}

// ============================================================
// SISTEMA DE COMUNICAÇÃO COM API
// ============================================================

/**
 * Faz request para a API backend com cache automático.
 *
 * @param {string} url - URL completa da API
 * @param {string} cacheType - Tipo para TTL do cache
 * @return {Object} Resposta da API
 */
function apiRequest(url, cacheType) {
  // Cache key baseado na URL
  var cache = CacheService.getScriptCache();
  var cacheKey = "bf_" + Utilities.base64Encode(url);
  
  // Verificar cache primeiro
  var cached = cache.get(cacheKey);
  if (cached) {
    try {
      return JSON.parse(cached);
    } catch(e) {
      // Cache corrompido, continuar com request
    }
  }
  
  // Configurar request
  var options = {
    method: "get",
    headers: {
      "X-API-Key": getUserApiKey() || "",
      "User-Agent": "BrazilFinance-Sheets/1.0",
      "Accept": "application/json"
    },
    muteHttpExceptions: true
  };
  
  // Fazer request
  var response = UrlFetchApp.fetch(url, options);
  var code = response.getResponseCode();
  var responseText = response.getContentText();
  
  // Tratar códigos de erro específicos
  if (code === 429) {
    return { 
      erro: "Limite de requests atingido. Upgrade em brazilfinance.com.br ou aguarde." 
    };
  }
  
  if (code === 401) {
    return { 
      erro: "API key inválida. Configure com setUserApiKey() ou upgrade em brazilfinance.com.br" 
    };
  }
  
  if (code !== 200) {
    return { 
      erro: "Erro HTTP " + code + " da API. Tente novamente em alguns minutos." 
    };
  }
  
  // Parse da resposta
  var data;
  try {
    data = JSON.parse(responseText);
  } catch(e) {
    return { erro: "Erro ao processar resposta da API" };
  }
  
  // Cachear resposta válida
  if (!data.erro) {
    var ttl = getCacheTTL(cacheType);
    try {
      cache.put(cacheKey, JSON.stringify(data), ttl);
    } catch(e) {
      // Cache put pode falhar se data muito grande, ignorar
    }
  }
  
  return data;
}

/**
 * Recupera API key do usuário.
 */
function getUserApiKey() {
  var props = PropertiesService.getUserProperties();
  return props.getProperty("BRAZILFINANCE_API_KEY") || "";
}

/**
 * Define TTL do cache baseado no tipo de dados.
 */
function getCacheTTL(cacheType) {
  var ttls = {
    "bcb_sgs": 3600,      // 1 hora
    "bcb_focus": 7200,    // 2 horas  
    "b3_quote": 300,      // 5 minutos
    "tesouro": 3600,      // 1 hora
    "default": 1800       // 30 minutos
  };
  
  return ttls[cacheType] || ttls["default"];
}

// ============================================================
// FUNÇÕES DE SETUP E DIAGNÓSTICO
// ============================================================

/**
 * Testa conectividade com a API.
 */
function testarConectividade() {
  var url = API_BASE_URL + "/health";
  
  try {
    var response = UrlFetchApp.fetch(url, { muteHttpExceptions: true });
    var data = JSON.parse(response.getContentText());
    
    console.log("✅ API online:", data);
    return "✅ Conectado à API BrazilFinance";
    
  } catch(e) {
    console.log("❌ Erro de conectividade:", e.message);
    return "❌ Erro: " + e.message;
  }
}

/**
 * Lista todos os indicadores disponíveis.
 */
function listarIndicadores() {
  var url = API_BASE_URL + "/indicators";
  
  try {
    var response = apiRequest(url, "default");
    console.log("📊 Indicadores disponíveis:", response);
    return response;
    
  } catch(e) {
    return { erro: e.message };
  }
}

/**
 * Limpa cache do usuário.
 */
function limparCache() {
  var cache = CacheService.getScriptCache();
  cache.removeAll(cache.getKeys());
  return "🧹 Cache limpo";
}