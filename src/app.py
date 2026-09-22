"""
Aplicação Web da Lis 💳 (Python Standard Library - Sem dependências externas)
Servidor HTTP Multi-thread de alta performance com suporte completo a Ctrl+C no Windows.
Uso: python src/app.py
"""

import http.server
import socketserver
import json
import urllib.parse
import sys
import os
import signal
from pathlib import Path
from data_loader import DataLoader
from agente import AgenteLis

PORT = 8501

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lis 💳 | Especialista em Cartões Bradesco</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0a0d14;
            --bg-card: rgba(255, 255, 255, 0.04);
            --border-card: rgba(255, 255, 255, 0.08);
            --red-bradesco: #cc092f;
            --red-hover: #e6173a;
            --text-main: #f0f6fc;
            --text-muted: #8b949e;
            --accent-blue: #38bdf8;
            --accent-green: #34d399;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
        body { background: var(--bg-base); color: var(--text-main); display: flex; height: 100vh; overflow: hidden; }
        
        .brand { display: flex; align-items: center; gap: 12px; }
        .badge { background: var(--red-bradesco); padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; font-weight: 600; }

        /* Main Chat Area */
        main {
            flex: 1;
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            background: radial-gradient(circle at 50% 10%, rgba(204, 9, 47, 0.08), transparent 70%), var(--bg-base);
        }
        header {
            padding: 16px 32px;
            border-bottom: 1px solid var(--border-card);
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: rgba(15, 20, 32, 0.6);
            backdrop-filter: blur(12px);
        }
        .chat-container {
            flex: 1;
            padding: 24px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            gap: 16px;
            max-width: 960px;
            width: 100%;
            margin: 0 auto;
        }
        .msg {
            max-width: 82%;
            padding: 16px 20px;
            border-radius: 14px;
            line-height: 1.6;
            font-size: 0.95rem;
            animation: fadeIn 0.2s ease-in;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .msg-lis {
            align-self: flex-start;
            background: #18121a;
            border: 1px solid rgba(230, 23, 58, 0.2);
            border-left: 4px solid var(--red-bradesco);
        }
        .msg-user {
            align-self: flex-end;
            background: #1b263b;
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-right: 4px solid var(--accent-blue);
        }
        .quick-actions-wrapper {
            max-width: 960px;
            width: 100%;
            margin: 0 auto;
            padding: 0 24px;
        }
        .quick-actions {
            display: flex;
            gap: 10px;
            padding: 8px 0;
            overflow-x: auto;
        }
        .quick-btn {
            background: var(--bg-card);
            border: 1px solid var(--border-card);
            color: var(--text-main);
            padding: 8px 14px;
            border-radius: 20px;
            font-size: 0.85rem;
            cursor: pointer;
            white-space: nowrap;
            transition: all 0.2s;
        }
        .quick-btn:hover {
            border-color: var(--red-bradesco);
            background: rgba(204, 9, 47, 0.15);
        }
        .quick-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .input-wrapper {
            max-width: 960px;
            width: 100%;
            margin: 0 auto;
            padding: 16px 24px 24px 24px;
        }
        .input-bar {
            border: 1px solid var(--border-card);
            border-radius: 12px;
            display: flex;
            gap: 10px;
            padding: 6px 8px 6px 16px;
            background: #141a29;
            box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        }
        .input-bar:focus-within {
            border-color: var(--red-bradesco);
        }
        .input-bar input {
            flex: 1;
            background: transparent;
            border: none;
            color: #fff;
            font-size: 0.95rem;
            outline: none;
            padding: 8px 0;
        }
        .input-bar input:disabled { opacity: 0.6; }
        .send-btn {
            background: var(--red-bradesco);
            color: #fff;
            border: none;
            border-radius: 8px;
            padding: 0 20px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .send-btn:hover { background: var(--red-hover); }
        .send-btn:disabled { opacity: 0.5; cursor: not-allowed; }
    </style>
</head>
<body>
    <main>
        <header>
            <div class="brand">
                <span style="font-size: 1.7rem;">💳</span>
                <div>
                    <div style="font-size: 1.15rem; font-weight: 700;">Lis Consultiva</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); font-weight: 400;">Bradesco Cartões • IA Generativa com Gemma 4 (Docker)</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 14px;">
                <span style="font-size: 0.8rem; color: var(--accent-green);">● Conectado ao Gemma 4</span>
                <div class="badge">Crédito Consciente</div>
            </div>
        </header>

        <div class="chat-container" id="chat">
            <div id="emptyState" style="text-align: center; color: var(--text-muted); margin: auto; padding: 40px 20px;">
                <div style="font-size: 3.2rem; margin-bottom: 12px;">💳</div>
                <h3 style="color: var(--text-main); font-weight: 600; font-size: 1.3rem;">Como posso te ajudar hoje, João?</h3>
                <p style="font-size: 0.9rem; margin-top: 8px; color: var(--text-muted); max-width: 480px; line-height: 1.5; margin-left: auto; margin-right: auto;">
                    Estou pronta para analisar seus gastos, eliminar tarifas de anuidade e te indicar os melhores cartões e benefícios do Bradesco.
                </p>
                <p style="font-size: 0.8rem; margin-top: 14px; color: var(--accent-blue);">
                    💡 Dica: Digite uma pergunta abaixo ou escolha um dos atalhos rápidos.
                </p>
            </div>
        </div>

        <div class="quick-actions-wrapper">
            <div class="quick-actions">
                <button class="quick-btn" onclick="perguntar('Estou pagando anuidade no cartão Classic e quero viajar para a Europa. O que recomenda?')">✈️ Viagem para Europa sem anuidade</button>
                <button class="quick-btn" onclick="perguntar('Gasto R$ 4.500/mês. Compensa mais Cashback no Like Visa ou Milhas no Amex Gold?')">💰 Comparar Cashback vs Milhas</button>
                <button class="quick-btn" onclick="perguntar('Minha renda é R$ 8.000. Posso pedir o The Platinum Card direto?')">👑 Posso pedir o The Platinum Card?</button>
            </div>
        </div>

        <div class="input-wrapper">
            <div class="input-bar">
                <input type="text" id="userInput" placeholder="Digite sua dúvida (ex: anuidade, seguro viagem, milhas, débito para crédito)..." onkeydown="handleKeyDown(event)">
                <button class="send-btn" id="sendBtn" onclick="enviar()">Enviar</button>
            </div>
        </div>
    </main>

    <script>
        const chat = document.getElementById('chat');
        const input = document.getElementById('userInput');
        const sendBtn = document.getElementById('sendBtn');
        const quickBtns = document.querySelectorAll('.quick-btn');

        const historicoConversa = [];

        function formatMarkdown(text) {
            if (!text) return '';
            return text
                .replace(/\\*\\*(.*?)\\*\\*/g, '<b>$1</b>')
                .replace(/\\*(.*?)\\*/g, '<i>$1</i>')
                .replace(/\\n/g, '<br>');
        }

        function setEnviando(estado) {
            input.disabled = estado;
            sendBtn.disabled = estado;
            quickBtns.forEach(btn => btn.disabled = estado);
            sendBtn.innerText = estado ? 'Enviando...' : 'Enviar';
            if (!estado) {
                input.focus();
            }
        }

        function handleKeyDown(event) {
            if (event.key === 'Enter') {
                event.preventDefault();
                enviar();
            }
        }

        function enviar() {
            const msg = input.value.trim();
            if (!msg) return;
            perguntar(msg);
            input.value = '';
        }

        async function perguntar(msg) {
            const emptyState = document.getElementById('emptyState');
            if (emptyState) {
                emptyState.remove();
            }

            chat.innerHTML += `<div class="msg msg-user"><b>Você:</b><br>${formatMarkdown(msg)}</div>`;
            chat.scrollTop = chat.scrollHeight;

            const loadingId = 'loading-' + Date.now();
            chat.innerHTML += `<div class="msg msg-lis" id="${loadingId}"><i>Lis está analisando seus dados e consultando a base oficial...</i></div>`;
            chat.scrollTop = chat.scrollHeight;

            setEnviando(true);

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ mensagem: msg, historico: historicoConversa })
                });

                if (!res.ok) {
                    throw new Error('Status ' + res.status);
                }

                const data = await res.json();
                const respostaTexto = data.resposta || 'Não foi possível obter resposta no momento.';
                const loadingElem = document.getElementById(loadingId);
                if (loadingElem) {
                    loadingElem.innerHTML = `<b>Lis 💳:</b><br>${formatMarkdown(respostaTexto)}`;
                }

                historicoConversa.push({ role: 'user', content: msg });
                historicoConversa.push({ role: 'assistant', content: respostaTexto });
            } catch(err) {
                console.error('Erro na requisição:', err);
                const loadingElem = document.getElementById(loadingId);
                if (loadingElem) {
                    loadingElem.innerHTML = `<b>Lis 💳:</b><br>Ocorreu uma instabilidade momentânea na conexão com o motor de IA. Por favor, tente novamente.`;
                }
            } finally {
                setEnviando(false);
                chat.scrollTop = chat.scrollHeight;
            }
        }
    </script>
</body>
</html>
"""

loader = DataLoader()
agente = AgenteLis(data_loader=loader)


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    """Servidor HTTP multi-thread que não bloqueia requisições simultâneas."""
    daemon_threads = True
    allow_reuse_address = True


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, format, *args):
        # Log simplificado e limpo no console
        print(f"[HTTP] {self.command} {self.path} - {args[0]}")

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/?"):
            body = HTML_TEMPLATE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Connection", "close")
            self.end_headers()
        elif self.path == "/api/status":
            body = json.dumps({"status": "online", "cliente": loader.obter_resumo_financeiro()}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404, "Not Found")

    def do_POST(self):
        if self.path == "/api/chat":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length).decode("utf-8")
                body = json.loads(post_data) if post_data else {}
                msg = body.get("mensagem", "")
                historico = body.get("historico", [])
                
                print(f"[Lis] Processando pergunta: '{msg}'")
                resposta = agente.responder(msg, historico_conversa=historico)
                
                payload = json.dumps({"resposta": resposta}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(payload)
                print(f"[Lis] Resposta enviada com sucesso!")
            except Exception as e:
                print(f"[ERRO] Falha no processamento POST: {e}")
                err_payload = json.dumps({"resposta": "Desculpe, ocorreu um erro interno ao processar a consulta."}).encode("utf-8")
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(err_payload)))
                self.send_header("Connection", "close")
                self.end_headers()
                self.wfile.write(err_payload)
        else:
            self.send_error(404, "Not Found")


def main():
    if sys.stdout and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    
    server_address = ("", PORT)
    httpd = ThreadedHTTPServer(server_address, CustomHandler)
    # Timeout curto para permitir interrupção imediata via Ctrl+C no Windows
    httpd.timeout = 0.5

    print(f"=" * 60)
    print(f"  Lis 💳 - Assistente de Cartões Bradesco")
    print(f"  Servidor HTTP Multi-thread Ativo na porta {PORT}")
    print(f"  Conectado ao Gemma 4 (Llama-Server Docker)")
    print(f"  Acesse no seu navegador: http://localhost:{PORT}")
    print(f"  Pressione Ctrl+C para encerrar o servidor a qualquer momento.")
    print(f"=" * 60)

    try:
        while True:
            httpd.handle_request()
    except KeyboardInterrupt:
        print("\n[INFO] Sinal de interrupção (Ctrl+C) recebido.")
    finally:
        httpd.server_close()
        print("[INFO] Servidor finalizado com sucesso.")


if __name__ == "__main__":
    main()
