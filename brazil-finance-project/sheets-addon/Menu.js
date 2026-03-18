/**
 * BrazilFinance Sheets - Menu e Interface
 * Menu personalizado e funções de interface para Google Sheets
 */

// ============================================================
// MENU PERSONALIZADO
// ============================================================

/**
 * Adiciona menu customizado ao abrir planilha.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createAddonMenu()
    .addItem("📊 Indicadores disponíveis", "showIndicators")
    .addItem("🔑 Configurar API Key", "showApiKeyDialog")
    .addItem("🔄 Atualizar dados", "refreshAllData")
    .addItem("📈 Inserir Dashboard Macro", "insertMacroDashboard")
    .addItem("💰 Inserir Portfolio Tracker", "insertPortfolioTracker")
    .addSeparator()
    .addItem("🧪 Testar conectividade", "testConnection")
    .addItem("🧹 Limpar cache", "clearCache")
    .addSeparator()
    .addItem("❓ Ajuda", "showHelp")
    .addItem("🚀 Upgrade Pro", "showUpgrade")
    .addToUi();
}

/**
 * Função chamada quando add-on é instalado.
 */
function onInstall() {
  onOpen();
}

/**
 * Função chamada quando arquivo ganha escopo.
 */
function onFileScopeGranted() {
  onOpen();
}

// ============================================================
// FUNÇÕES DE INTERFACE
// ============================================================

/**
 * Mostra sidebar com lista de indicadores.
 */
function showIndicators() {
  var html = HtmlService.createHtmlOutput(`
    <style>
      body { font-family: Arial, sans-serif; margin: 10px; }
      .indicator-group { margin-bottom: 15px; }
      .indicator-title { font-weight: bold; color: #1a73e8; margin-bottom: 5px; }
      .indicator-item { margin: 2px 0; font-size: 12px; }
      .formula { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
      .divider { border-top: 1px solid #e0e0e0; margin: 15px 0; }
    </style>
    
    <h2>📊 BrazilFinance - Indicadores</h2>
    
    <div class="indicator-group">
      <div class="indicator-title">Macro Economia (BCB)</div>
      <div class="indicator-item"><span class="formula">=BCB("selic")</span> - Taxa Selic</div>
      <div class="indicator-item"><span class="formula">=BCB("ipca")</span> - IPCA mensal</div>
      <div class="indicator-item"><span class="formula">=BCB("cdi")</span> - CDI</div>
      <div class="indicator-item"><span class="formula">=BCB("dolar")</span> - USD/BRL</div>
      <div class="indicator-item"><span class="formula">=BCB("igpm")</span> - IGP-M</div>
      <div class="indicator-item"><span class="formula">=BCB("desemprego")</span> - Taxa desemprego</div>
    </div>
    
    <div class="divider"></div>
    
    <div class="indicator-group">
      <div class="indicator-title">Expectativas Focus</div>
      <div class="indicator-item"><span class="formula">=FOCUS("IPCA", 2026)</span> - Expectativa IPCA</div>
      <div class="indicator-item"><span class="formula">=FOCUS("Selic", 2026)</span> - Expectativa Selic</div>
      <div class="indicator-item"><span class="formula">=FOCUS("PIB Total", 2026)</span> - Expectativa PIB</div>
      <div class="indicator-item"><span class="formula">=FOCUS("Taxa de câmbio", 2026)</span> - Expectativa Dólar</div>
    </div>
    
    <div class="divider"></div>
    
    <div class="indicator-group">
      <div class="indicator-title">Mercado B3</div>
      <div class="indicator-item"><span class="formula">=B3("PETR4")</span> - Cotação PETR4</div>
      <div class="indicator-item"><span class="formula">=B3("VALE3", "variacao")</span> - Variação VALE3</div>
      <div class="indicator-item"><span class="formula">=B3("HGLG11")</span> - FII HGLG11</div>
      <div class="indicator-item"><span class="formula">=B3("BOVA11", "volume")</span> - Volume BOVA11</div>
    </div>
    
    <div class="divider"></div>
    
    <div class="indicator-group">
      <div class="indicator-title">Tesouro Direto</div>
      <div class="indicator-item"><span class="formula">=TESOURO("IPCA+ 2035")</span> - Taxa IPCA+ 2035</div>
      <div class="indicator-item"><span class="formula">=TESOURO("Prefixado 2029", "preco")</span> - Preço Prefixado</div>
      <div class="indicator-item"><span class="formula">=TESOURO("Selic 2029")</span> - Taxa Selic 2029</div>
    </div>
    
    <div class="divider"></div>
    
    <div class="indicator-group">
      <div class="indicator-title">Funções Auxiliares</div>
      <div class="indicator-item"><span class="formula">=MACRO_RESUMO(2026)</span> - Dashboard macro</div>
      <div class="indicator-item"><span class="formula">=B3_COMPARAR("PETR4,VALE3")</span> - Comparar ativos</div>
      <div class="indicator-item"><span class="formula">=BCB_LISTA()</span> - Lista indicadores</div>
      <div class="indicator-item"><span class="formula">=BCB_DATA("selic")</span> - Data atualização</div>
    </div>
    
    <div class="divider"></div>
    
    <p style="font-size: 11px; color: #666;">
      <strong>Dica:</strong> Clique duas vezes em qualquer fórmula para copiá-la.
    </p>
    
    <p style="text-align: center; margin-top: 20px;">
      <a href="https://brazilfinance.com.br/docs" target="_blank" 
         style="color: #1a73e8; text-decoration: none; font-weight: bold;">
        📖 Documentação Completa
      </a>
    </p>
  `)
    .setTitle("BrazilFinance - Indicadores")
    .setWidth(320);
    
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * Dialog para configurar API Key.
 */
function showApiKeyDialog() {
  var ui = SpreadsheetApp.getUi();
  
  var currentKey = getUserApiKey();
  var promptText = currentKey ? 
    "API Key atual: " + currentKey.substring(0, 8) + "...\nCole uma nova API Key ou deixe em branco para manter:" :
    "Cole sua API Key do BrazilFinance.\nObtenha grátis em: brazilfinance.com.br";
    
  var result = ui.prompt(
    "🔑 Configurar API Key",
    promptText,
    ui.ButtonSet.OK_CANCEL
  );
  
  if (result.getSelectedButton() == ui.Button.OK) {
    var newKey = result.getResponseText().trim();
    if (newKey) {
      setUserApiKey(newKey);
      ui.alert("✅ API Key salva com sucesso!");
    } else if (currentKey) {
      ui.alert("API Key mantida: " + currentKey.substring(0, 8) + "...");
    } else {
      ui.alert("❌ Nenhuma API Key fornecida.");
    }
  }
}

/**
 * Força atualização de todos os dados.
 */
function refreshAllData() {
  var ui = SpreadsheetApp.getUi();
  
  try {
    // Limpar cache local
    var cache = CacheService.getScriptCache();
    cache.removeAll(cache.getKeys());
    
    // Forçar recálculo
    SpreadsheetApp.flush();
    
    ui.alert("🔄 Dados atualizados!", "As fórmulas serão recalculadas automaticamente.", ui.ButtonSet.OK);
  } catch(e) {
    ui.alert("❌ Erro ao atualizar", "Erro: " + e.message, ui.ButtonSet.OK);
  }
}

/**
 * Testa conectividade com a API.
 */
function testConnection() {
  var ui = SpreadsheetApp.getUi();
  
  try {
    var result = testarConectividade();
    ui.alert("🧪 Teste de Conectividade", result, ui.ButtonSet.OK);
  } catch(e) {
    ui.alert("❌ Erro no teste", "Erro: " + e.message, ui.ButtonSet.OK);
  }
}

/**
 * Limpa cache do usuário.
 */
function clearCache() {
  var ui = SpreadsheetApp.getUi();
  
  try {
    var result = limparCache();
    ui.alert("🧹 Cache", result, ui.ButtonSet.OK);
  } catch(e) {
    ui.alert("❌ Erro", "Não foi possível limpar o cache: " + e.message, ui.ButtonSet.OK);
  }
}

// ============================================================
// TEMPLATES AUTOMÁTICOS
// ============================================================

/**
 * Insere dashboard macro na planilha atual.
 */
function insertMacroDashboard() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var ui = SpreadsheetApp.getUi();
  
  var result = ui.alert(
    "📈 Inserir Dashboard Macro",
    "Isso criará um dashboard com indicadores macro na planilha atual. Continuar?",
    ui.ButtonSet.YES_NO
  );
  
  if (result == ui.Button.YES) {
    try {
      // Headers
      sheet.getRange("A1").setValue("DASHBOARD MACRO BRASIL");
      sheet.getRange("A1").setFontSize(14).setFontWeight("bold");
      
      sheet.getRange("A3").setValue("Indicador");
      sheet.getRange("B3").setValue("Atual");
      sheet.getRange("C3").setValue("Expectativa 2026");
      sheet.getRange("A3:C3").setFontWeight("bold").setBackground("#e8f0fe");
      
      // Data
      var data = [
        ["Selic (%)", "=BCB(\"selic\")", "=FOCUS(\"Selic\", 2026)"],
        ["IPCA (% mês)", "=BCB(\"ipca\")", "=FOCUS(\"IPCA\", 2026)"],
        ["PIB (%)", "=BCB(\"ibc_br\")", "=FOCUS(\"PIB Total\", 2026)"],
        ["Dólar (R$)", "=BCB(\"dolar\")", "=FOCUS(\"Taxa de câmbio\", 2026)"],
        ["CDI (%)", "=BCB(\"cdi\")", ""],
        ["IGP-M (% mês)", "=BCB(\"igpm\")", ""],
        ["Desemprego (%)", "=BCB(\"desemprego\")", ""]
      ];
      
      sheet.getRange(4, 1, data.length, 3).setValues(data);
      sheet.getRange(4, 2, data.length, 2).setNumberFormat("0.00");
      
      // Styling
      sheet.autoResizeColumns(1, 3);
      sheet.getRange("A1:C" + (3 + data.length)).setBorder(true, true, true, true, true, true);
      
      ui.alert("✅ Sucesso!", "Dashboard macro inserido com sucesso!", ui.ButtonSet.OK);
    } catch(e) {
      ui.alert("❌ Erro", "Erro ao inserir dashboard: " + e.message, ui.ButtonSet.OK);
    }
  }
}

/**
 * Insere template de portfolio tracker.
 */
function insertPortfolioTracker() {
  var sheet = SpreadsheetApp.getActiveSheet();
  var ui = SpreadsheetApp.getUi();
  
  var result = ui.alert(
    "💰 Inserir Portfolio Tracker", 
    "Isso criará um tracker de portfolio na planilha atual. Continuar?",
    ui.ButtonSet.YES_NO
  );
  
  if (result == ui.Button.YES) {
    try {
      // Headers
      sheet.getRange("A1").setValue("PORTFOLIO TRACKER");
      sheet.getRange("A1").setFontSize(14).setFontWeight("bold");
      
      var headers = ["Ticker", "Quantidade", "Preço Atual", "Total", "Variação %", "Última Atualização"];
      sheet.getRange("A3:F3").setValues([headers]);
      sheet.getRange("A3:F3").setFontWeight("bold").setBackground("#e8f0fe");
      
      // Sample data
      var sampleData = [
        ["PETR4", 100, "=B4*B3(\"PETR4\")", "=B4*C4", "=B3(\"PETR4\",\"variacao\")", "=NOW()"],
        ["VALE3", 50, "=B3(\"VALE3\")", "=B5*C5", "=B3(\"VALE3\",\"variacao\")", "=NOW()"],
        ["HGLG11", 200, "=B3(\"HGLG11\")", "=B6*C6", "=B3(\"HGLG11\",\"variacao\")", "=NOW()"]
      ];
      
      sheet.getRange(4, 1, sampleData.length, 6).setValues(sampleData);
      
      // Formatting
      sheet.getRange("C4:D6").setNumberFormat("R$ 0.00");
      sheet.getRange("E4:E6").setNumberFormat("0.00%");
      sheet.getRange("F4:F6").setNumberFormat("dd/mm/yyyy hh:mm");
      
      // Total row
      sheet.getRange("A8").setValue("TOTAL PORTFOLIO:");
      sheet.getRange("A8").setFontWeight("bold");
      sheet.getRange("D8").setFormula("=SUM(D4:D6)");
      sheet.getRange("D8").setNumberFormat("R$ #,##0.00").setFontWeight("bold");
      
      sheet.autoResizeColumns(1, 6);
      sheet.getRange("A1:F8").setBorder(true, true, true, true, true, true);
      
      ui.alert("✅ Sucesso!", "Portfolio tracker inserido! Edite as quantidades na coluna B.", ui.ButtonSet.OK);
    } catch(e) {
      ui.alert("❌ Erro", "Erro ao inserir portfolio: " + e.message, ui.ButtonSet.OK);
    }
  }
}

/**
 * Mostra ajuda completa.
 */
function showHelp() {
  var html = HtmlService.createHtmlOutput(`
    <style>
      body { font-family: Arial, sans-serif; margin: 10px; line-height: 1.4; }
      h2 { color: #1a73e8; margin-bottom: 10px; }
      h3 { color: #333; margin-top: 15px; margin-bottom: 5px; }
      .formula { background: #f8f9fa; padding: 2px 4px; border-radius: 3px; font-family: monospace; }
      .example { background: #f0f8ff; padding: 8px; border-radius: 4px; margin: 5px 0; }
      .warning { background: #fff3cd; padding: 8px; border-radius: 4px; margin: 10px 0; border-left: 4px solid #ffc107; }
      .tip { background: #d1ecf1; padding: 8px; border-radius: 4px; margin: 10px 0; border-left: 4px solid #17a2b8; }
      a { color: #1a73e8; text-decoration: none; }
      a:hover { text-decoration: underline; }
    </style>
    
    <h2>🚀 BrazilFinance - Guia Completo</h2>
    
    <h3>📊 Fórmulas Principais</h3>
    <div class="example">
      <strong>Macro (BCB):</strong><br>
      <span class="formula">=BCB("selic")</span> — Taxa Selic atual<br>
      <span class="formula">=BCB("ipca")</span> — IPCA mensal<br>
      <span class="formula">=BCB("dolar")</span> — Cotação USD/BRL
    </div>
    
    <div class="example">
      <strong>Expectativas (Focus):</strong><br>
      <span class="formula">=FOCUS("IPCA", 2026)</span> — Expectativa IPCA 2026<br>
      <span class="formula">=FOCUS("Selic", 2026, "media")</span> — Selic 2026 (média)
    </div>
    
    <div class="example">
      <strong>Mercado (B3):</strong><br>
      <span class="formula">=B3("PETR4")</span> — Preço PETR4<br>
      <span class="formula">=B3("HGLG11", "variacao")</span> — Variação FII<br>
      <span class="formula">=B3("BOVA11", "volume")</span> — Volume ETF
    </div>
    
    <div class="example">
      <strong>Tesouro:</strong><br>
      <span class="formula">=TESOURO("IPCA+ 2035")</span> — Taxa IPCA+ 2035<br>
      <span class="formula">=TESOURO("Prefixado 2029", "preco")</span> — Preço unitário
    </div>
    
    <h3>🔧 Funções Auxiliares</h3>
    <div class="example">
      <span class="formula">=MACRO_RESUMO(2026)</span> — Dashboard macro automático<br>
      <span class="formula">=B3_COMPARAR("PETR4,VALE3,ITUB4")</span> — Comparar múltiplos ativos<br>
      <span class="formula">=BCB_LISTA()</span> — Lista todos indicadores disponíveis
    </div>
    
    <div class="tip">
      <strong>💡 Dica:</strong> Use o menu <strong>BrazilFinance</strong> para inserir dashboards prontos automaticamente!
    </div>
    
    <h3>⚙️ Configuração</h3>
    <p><strong>API Key (Opcional):</strong> Para mais requests, obtenha uma chave gratuita em brazilfinance.com.br e configure no menu.</p>
    
    <div class="warning">
      <strong>⚠️ Limites:</strong><br>
      • Free: 500 requests/dia<br>
      • Pro: 10.000 requests/dia (R$ 39/mês)<br>
      • Team: 50.000 requests/dia (R$ 149/mês)
    </div>
    
    <h3>🆘 Problemas Comuns</h3>
    <p><strong>❌ "Limite atingido":</strong> Aguarde reset diário ou faça upgrade</p>
    <p><strong>❌ "Ticker não encontrado":</strong> Verifique se está correto (ex: PETR4, não PETR)</p>
    <p><strong>❌ "Erro de conexão":</strong> Tente atualizar os dados pelo menu</p>
    
    <h3>🔗 Links Úteis</h3>
    <p>
      <a href="https://brazilfinance.com.br" target="_blank">🏠 Site oficial</a><br>
      <a href="https://brazilfinance.com.br/docs" target="_blank">📖 Documentação</a><br>
      <a href="mailto:suporte@brazilfinance.com.br">📧 Suporte</a>
    </p>
    
    <div style="text-align: center; margin-top: 20px; padding: 10px; background: #f8f9fa; border-radius: 5px;">
      <strong>Versão:</strong> 1.0.0 | <strong>Última atualização:</strong> Março 2026
    </div>
  `)
    .setTitle("BrazilFinance - Ajuda")
    .setWidth(400);
    
  SpreadsheetApp.getUi().showSidebar(html);
}

/**
 * Mostra informações sobre upgrade.
 */
function showUpgrade() {
  var ui = SpreadsheetApp.getUi();
  
  var message = "🚀 UPGRADE BRAZILFINANCE PRO\n\n" +
    "BENEFÍCIOS:\n" +
    "✅ 10.000 requests/dia (vs 500 free)\n" +
    "✅ Todos os indicadores BCB + Focus + Tesouro\n" +
    "✅ Cache otimizado (atualizações mais rápidas)\n" +
    "✅ Suporte prioritário\n" +
    "✅ Novos recursos primeiro\n\n" +
    "PREÇO: Apenas R$ 39/mês\n\n" +
    "Clique OK para visitar o site e fazer upgrade.";
    
  var result = ui.alert("💎 BrazilFinance Pro", message, ui.ButtonSet.OK_CANCEL);
  
  if (result == ui.Button.OK) {
    var html = HtmlService.createHtmlOutput(`
      <script>
        window.open('https://brazilfinance.com.br/pricing', '_blank');
        google.script.host.close();
      </script>
    `);
    
    SpreadsheetApp.getUi().showModelessDialog(html, "Redirecionando...");
  }
}