#!/usr/bin/env python3
"""
🤖 MUJU COMPLETO - Versão Render.com
• PIN: 302010
• API própria: Não pega IP
• DeepSeek: Puxa dados online
• Tudo em um só código!
"""

import os
import sys
import requests
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime

# ============================================
# CONFIGURAÇÕES DO SISTEMA
# ============================================

class MUJUConfig:
    """Configurações principais do MUJU"""
    def __init__(self):
        self.PIN_CORRETO = "302010"
        self.API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
        self.VERSAO = "3.0"
        self.DESENVOLVEDOR = "M.27"

# ============================================
# SISTEMA DE SEGURANÇA COM PIN
# ============================================

class SistemaSeguranca:
    """Sistema de PIN para proteger acesso"""
    
    def __init__(self):
        self.arquivo_log = "acessos_muju.json"
        self.max_tentativas = 5
        self.bloqueio_minutos = 15
    
    def verificar_pin(self, pin_digitado: str) -> dict:
        """Verifica PIN e registra acesso"""
        resultado = {
            "acesso_permitido": False,
            "mensagem": "",
            "tentativas_restantes": 0
        }
        
        # Carrega histórico
        historico = self.carregar_historico()
        
        # Verifica se está bloqueado
        if self.esta_bloqueado(historico):
            resultado["mensagem"] = "🔒 Sistema temporariamente bloqueado. Aguarde 15 minutos."
            return resultado
        
        # Verifica PIN
        if pin_digitado == MUJUConfig().PIN_CORRETO:
            self.registrar_acesso(historico, True)
            resultado["acesso_permitido"] = True
            resultado["mensagem"] = "✅ Acesso permitido!"
        else:
            historico["tentativas_falhas"].append(datetime.now().isoformat())
            self.salvar_historico(historico)
            
            falhas_recentes = len(historico["tentativas_falhas"])
            restantes = self.max_tentativas - falhas_recentes
            
            if restantes > 0:
                resultado["mensagem"] = f"❌ PIN incorreto. Tentativas restantes: {restantes}"
                resultado["tentativas_restantes"] = restantes
            else:
                resultado["mensagem"] = "🔒 Muitas tentativas falhas. Sistema bloqueado."
        
        return resultado
    
    def carregar_historico(self) -> dict:
        """Carrega histórico de acessos"""
        if os.path.exists(self.arquivo_log):
            try:
                with open(self.arquivo_log, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        return {
            "primeiro_acesso": datetime.now().isoformat(),
            "acessos_sucesso": [],
            "tentativas_falhas": [],
            "total_scripts": 0
        }
    
    def salvar_historico(self, historico: dict):
        """Salva histórico"""
        with open(self.arquivo_log, 'w') as f:
            json.dump(historico, f, indent=2)
    
    def registrar_acesso(self, historico: dict, sucesso: bool):
        """Registra novo acesso"""
        if sucesso:
            historico["acessos_sucesso"].append(datetime.now().isoformat())
        else:
            historico["tentativas_falhas"].append(datetime.now().isoformat())
        self.salvar_historico(historico)
    
    def esta_bloqueado(self, historico: dict) -> bool:
        """Verifica se sistema está bloqueado"""
        falhas = historico.get("tentativas_falhas", [])
        if len(falhas) >= self.max_tentativas:
            ultima_falha = datetime.fromisoformat(falhas[-1])
            tempo_passado = (datetime.now() - ultima_falha).seconds / 60
            return tempo_passado < self.bloqueio_minutos
        return False

# ============================================
# API DEEPSEEK - SEM PEGAR IP DO USUÁRIO
# ============================================

class MUJUDeepSeekAPI:
    """Integração com DeepSeek sem expor IP"""
    
    def __init__(self):
        self.api_url = "https://api.deepseek.com/chat/completions"
        self.api_key = MUJUConfig().API_KEY
        
        # Headers que não identificam o usuário final
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "Muju-Server/1.0",
            "X-Forwarded-For": "server-ip",  # IP do servidor, não do usuário
            "X-Real-IP": "server-ip"
        }
    
    def gerar_script(self, prompt: str) -> dict:
        """Gera script Lua usando DeepSeek (IP do servidor)"""
        
        # Sistema de prompts inteligentes
        prompt_otimizado = self.otimizar_prompt(prompt)
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": """Você é MUJU, especialista em Lua e Roblox Studio.
                    Gere código Lua funcional para executores como Synapse X, KRNL, Xeno.
                    Inclua:
                    1. Sistema de ativação por tecla
                    2. Comentários em português
                    3. Mensagens de debug (print)
                    4. Código otimizado
                    
                    Retorne APENAS código Lua, sem markdown, sem explicações."""
                },
                {
                    "role": "user",
                    "content": prompt_otimizado
                }
            ],
            "max_tokens": 1500,
            "temperature": 0.7,
            "stream": False
        }
        
        try:
            # Requisição feita pelo SERVIDOR (não pelo usuário)
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                codigo = data["choices"][0]["message"]["content"]
                
                # Limpeza do código
                codigo = self.limpar_codigo(codigo)
                
                return {
                    "sucesso": True,
                    "codigo": codigo,
                    "modelo": "deepseek-chat",
                    "tokens": data.get("usage", {}).get("total_tokens", 0)
                }
            else:
                return {
                    "sucesso": False,
                    "erro": f"Erro API: {response.status_code}",
                    "fallback": self.gerar_fallback(prompt)
                }
                
        except Exception as e:
            return {
                "sucesso": False,
                "erro": str(e),
                "fallback": self.gerar_fallback(prompt)
            }
    
    def otimizar_prompt(self, prompt: str) -> str:
        """Otimiza o prompt para melhor resultado"""
        prompt = prompt.lower()
        
        # Detecta tipo de script
        if any(word in prompt for word in ['fly', 'voar', 'voo']):
            return f"Crie um script de Fly (voar) para Roblox com: {prompt}. Use BodyVelocity e controles WASD + Espaço/Shift."
        elif any(word in prompt for word in ['esp', 'highlight', 'ver jogador']):
            return f"Crie um script ESP (ver jogadores) para Roblox com: {prompt}. Use Highlight e diferencie por time."
        elif any(word in prompt for word in ['noclip', 'fantasma', 'atraves']):
            return f"Crie um script Noclip (atravessar paredes) para Roblox com: {prompt}. Use CanCollide=false."
        elif any(word in prompt for word in ['speed', 'velocidade', 'rapido']):
            return f"Crie um script Speed (aumentar velocidade) para Roblox com: {prompt}. Modifique WalkSpeed."
        elif any(word in prompt for word in ['aimbot', 'mira', 'auto aim']):
            return f"Crie um script Aimbot (mira automática) para Roblox com: {prompt}. Use CFrame e suavização."
        else:
            return f"Crie um script Lua funcional para Roblox com estas características: {prompt}"
    
    def limpar_codigo(self, codigo: str) -> str:
        """Limpa e formata o código gerado"""
        # Remove markdown
        codigo = codigo.replace("```lua", "").replace("```", "")
        
        # Adiciona cabeçalho padrão
        cabecalho = f"""-- 🤖 MUJU - Script Gerado Automaticamente
-- Desenvolvido por: {MUJUConfig().DESENVOLVEDOR}
-- Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}
-- Versão: {MUJUConfig().VERSAO}
-- PIN de segurança: 302010

"""
        
        return cabecalho + codigo.strip()
    
    def gerar_fallback(self, prompt: str) -> str:
        """Gera fallback local se API falhar"""
        return f"""-- Script MUJU (Modo Local)
-- Prompt: {prompt}

print("🤖 MUJU - Script carregado!")
print("🔧 Funcionalidade: {prompt[:50]}...")

-- Adicione sua lógica Lua aqui
-- Este é um template básico"""

# ============================================
# SERVIDOR FLASK - API COMPLETA
# ============================================

app = Flask(__name__)
CORS(app)  # Permite requisições de qualquer origem

# Instâncias globais
seguranca = SistemaSeguranca()
api_muju = MUJUDeepSeekAPI()
config = MUJUConfig()

# ============================================
# ROTAS DA API
# ============================================

@app.route('/')
def home():
    """Página inicial"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>🤖 MUJU Server</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
                max-width: 800px;
                width: 100%;
                text-align: center;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .tagline {
                color: #666;
                margin-bottom: 30px;
                font-size: 1.1em;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .feature {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #667eea;
            }
            .feature h3 {
                color: #333;
                margin-bottom: 10px;
            }
            .endpoints {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: left;
            }
            code {
                background: #333;
                color: #00ff88;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: 'Courier New', monospace;
            }
            .status {
                display: inline-block;
                background: #00ff88;
                color: #000;
                padding: 5px 15px;
                border-radius: 20px;
                font-weight: bold;
                margin: 10px 0;
            }
            .warning {
                background: #fff3cd;
                color: #856404;
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #ffc107;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 MUJU Server</h1>
            <p class="tagline">Assistente Roblox com DeepSeek API</p>
            
            <div class="status">🟢 ONLINE</div>
            
            <div class="features">
                <div class="feature">
                    <h3>🔐 Segurança</h3>
                    <p>Sistema PIN protegido</p>
                </div>
                <div class="feature">
                    <h3>🌐 Privacidade</h3>
                    <p>Não coleta IP de usuários</p>
                </div>
                <div class="feature">
                    <h3>🚀 Performance</h3>
                    <p>DeepSeek AI integrado</p>
                </div>
                <div class="feature">
                    <h3>🎮 Roblox</h3>
                    <p>Scripts Lua otimizados</p>
                </div>
            </div>
            
            <div class="endpoints">
                <h3>📡 Endpoints da API:</h3>
                <p><strong>POST</strong> <code>/api/verify-pin</code> - Verificar PIN</p>
                <p><strong>POST</strong> <code>/api/generate</code> - Gerar scripts</p>
                <p><strong>GET</strong> <code>/api/status</code> - Status do servidor</p>
            </div>
            
            <div class="warning">
                <strong>⚠️ Importante:</strong> Esta API usa DeepSeek para geração de código.
                O IP dos usuários finais não é exposto para a DeepSeek.
            </div>
            
            <p style="color: #666; margin-top: 20px;">
                Desenvolvido por: M.27 | Versão: 3.0 | PIN: 302010
            </p>
        </div>
    </body>
    </html>
    '''

@app.route('/api/status', methods=['GET'])
def status():
    """Endpoint de status"""
    return jsonify({
        "status": "online",
        "service": "MUJU Server",
        "version": config.VERSAO,
        "developer": config.DESENVOLVEDOR,
        "ai_provider": "DeepSeek",
        "privacy": "no_user_ip_collection",
        "endpoints": {
            "verify_pin": "/api/verify-pin",
            "generate": "/api/generate",
            "status": "/api/status"
        }
    })

@app.route('/api/verify-pin', methods=['POST'])
def verify_pin():
    """Verifica PIN de acesso"""
    try:
        data = request.json
        if not data or 'pin' not in data:
            return jsonify({"error": "PIN não fornecido"}), 400
        
        resultado = seguranca.verificar_pin(data['pin'])
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate', methods=['POST'])
def generate():
    """Gera script Lua com DeepSeek"""
    try:
        data = request.json
        
        # Verifica PIN primeiro
        if 'pin' not in data:
            return jsonify({"error": "PIN não fornecido"}), 400
        
        pin_result = seguranca.verificar_pin(data['pin'])
        if not pin_result["acesso_permitido"]:
            return jsonify(pin_result), 403
        
        # Verifica prompt
        if 'prompt' not in data:
            return jsonify({"error": "Prompt não fornecido"}), 400
        
        prompt = data['prompt'].strip()
        if len(prompt) < 3:
            return jsonify({"error": "Prompt muito curto"}), 400
        
        # Gera script
        resultado = api_muju.gerar_script(prompt)
        
        # Atualiza estatísticas
        historico = seguranca.carregar_historico()
        historico["total_scripts"] = historico.get("total_scripts", 0) + 1
        seguranca.salvar_historico(historico)
        
        return jsonify(resultado)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# CONFIGURAÇÃO ESPECIAL PARA RENDER.COM
# ============================================

def inicializar_sistema():
    """Inicializa o sistema MUJU"""
    print("="*70)
    print("🤖 INICIANDO MUJU SERVER NO RENDER")
    print("="*70)
    print(f"Versão: {config.VERSAO}")
    print(f"Desenvolvedor: {config.DESENVOLVEDOR}")
    print(f"PIN de acesso: {config.PIN_CORRETO}")
    print(f"API DeepSeek: {'✅ Configurada' if config.API_KEY else '❌ Não configurada'}")
    print(f"Privacidade: IP dos usuários NÃO coletado")
    print("="*70)
    
    if not config.API_KEY:
        print("\n⚠️  AVISO: Configure a variável de ambiente DEEPSEEK_API_KEY no Render")
        print("💡 Dica: Vá em Environment > Add Environment Variable")

if __name__ == '__main__':
    inicializar_sistema()
    
    # Render usa a variável PORT automaticamente
    porta = int(os.environ.get('PORT', 10000))
    
    print(f"\n🚀 Servidor iniciando na porta {porta}...")
    print(f"🌐 Seu URL será: https://SEU-APP.onrender.com")
    print("📡 Aguardando requisições...")
    print("="*70)
    
    # Para produção no Render
    app.run(host='0.0.0.0', port=porta, debug=False)
