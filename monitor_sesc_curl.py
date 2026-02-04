import os
import requests
import time
import sys
import urllib3
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# ================= CONFIGURAÇÕES =================
# Carregadas do arquivo .env (crie um baseado no .env.example)
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

# Configurações de Busca (podem ser sobrescritas via .env)
DIAS_PARA_VERIFICAR = int(os.getenv('DIAS_PARA_VERIFICAR', '60'))
MINUTOS_INTERVALO = int(os.getenv('MINUTOS_INTERVALO', '480'))
UNIDADE_HOTEL = os.getenv('UNIDADE_HOTEL', '51')  # 51 = Tepequém
# =================================================

# Desabilita avisos de SSL inseguro (já que o site tem problemas de cert)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SescMonitor:
    def __init__(self):
        self.base_url = "https://snh.sescrr.com.br"
        self.session = requests.Session()
        # Headers idênticos ao seu CURL para passar despercebido
        self.headers = {
            'Accept': 'text/plain, */*; q=0.01',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://snh.sescrr.com.br',
            'Referer': 'https://snh.sescrr.com.br/ReservaOnline/',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"'
        }

    def iniciar_sessao(self):
        """
        Acessa a página inicial para pegar o Cookie 'ASP.NET_SessionId' 
        e o '__RequestVerificationToken'.
        """
        try:
            print("🔄 Inicializando sessão...")
            resp = self.session.get(f"{self.base_url}/ReservaOnline/", headers=self.headers, verify=False)
            
            if resp.status_code == 200:
                # Tenta extrair a unidade automaticamente caso mude, senão usa a config
                soup = BeautifulSoup(resp.text, 'html.parser')
                select_unidade = soup.find('select', {'id': 'codMeioHospedagem'})
                if select_unidade:
                    opcao = select_unidade.find('option', selected=True)
                    if opcao:
                        global UNIDADE_HOTEL
                        UNIDADE_HOTEL = opcao['value']
                        print(f"🏨 Unidade detectada: {UNIDADE_HOTEL}")
                
                print("✅ Sessão (Cookies) obtida com sucesso.")
                return True
            else:
                print(f"❌ Erro ao acessar site: {resp.status_code}")
                return False
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False

    def verificar_disponibilidade(self, data_entrada, data_saida):
        """
        Faz a requisição exatamente igual ao CURL fornecido.
        """
        url = f"{self.base_url}/ReservaOnline/Reserva/VerificarBloqueio"
        
        # Payload extraído do seu CURL: codMeioHospedagem=51&dataInicial=...
        payload = {
            'codMeioHospedagem': UNIDADE_HOTEL,
            'dataInicial': data_entrada,
            'dataFinal': data_saida
        }

        try:
            response = self.session.post(
                url, 
                headers=self.headers, 
                data=payload, 
                verify=False, 
                timeout=10
            )

            if response.status_code == 200:
                # O site retorna texto puro: "false" (Disponível) ou "true" (Bloqueado)
                resposta_texto = response.text.strip().lower()
                
                if resposta_texto == 'false':
                    return True  # NÃO está bloqueado = DISPONÍVEL
                elif resposta_texto == 'true':
                    return False # ESTÁ bloqueado = INDISPONÍVEL
                else:
                    # Se vier HTML de erro ou outra coisa, assume indisponível
                    return False
            return False
        except Exception as e:
            print(f" [Erro Req] {e}")
            return False

    def enviar_telegram(self, mensagem):
        if not TELEGRAM_TOKEN:
            print("⚠️ Token do Telegram não configurado!")
            return
        
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {"chat_id": TELEGRAM_CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
        try:
            requests.post(url, json=data)
        except:
            print("❌ Falha ao enviar Telegram")

    def rodar(self):
        print("🚀 Monitor SESC Roraima (Modo CURL) Iniciado")
        self.enviar_telegram("🤖 Monitor iniciado! Buscando vagas...")

        while True:
            if not self.iniciar_sessao():
                time.sleep(60)
                continue

            vagas_encontradas = []
            hoje = datetime.now()

            print(f"\n🔎 Verificando {DIAS_PARA_VERIFICAR} dias a partir de {hoje.strftime('%d/%m')}...")

            # Loop pelos dias
            for i in range(1, DIAS_PARA_VERIFICAR + 1):
                data_obj = hoje + timedelta(days=i)
                
                # Regra de negócio: Sesc geralmente libera finais de semana ou dias específicos.
                # Se quiser filtrar apenas Sexta/Sábado, descomente abaixo:
                # if data_obj.weekday() not in [4, 5, 6]: continue 

                dt_entrada = data_obj.strftime('%d/%m/%Y')
                dt_saida = (data_obj + timedelta(days=1)).strftime('%d/%m/%Y')

                disponivel = self.verificar_disponibilidade(dt_entrada, dt_saida)

                # Log visual no terminal
                status_icon = "✅" if disponivel else "❌"
                sys.stdout.write(f"\r{dt_entrada}: {status_icon}   ")
                sys.stdout.flush()

                if disponivel:
                    vagas_encontradas.append(f"{dt_entrada} a {dt_saida}")

                # Pequeno delay para não flodar o servidor (importante!)
                time.sleep(0.3)

            print("") # Quebra de linha após o loop

            if vagas_encontradas:
                print("\n🎉 VAGAS ENCONTRADAS!")
                msg = f"🚨 **VAGAS DISPONÍVEIS SESC RR** 🚨\nUnidade: {UNIDADE_HOTEL}\n\n"
                msg += "\n".join([f"✅ {v}" for v in vagas_encontradas])
                msg += f"\n\n🔗 [Reservar Agora]({self.base_url}/ReservaOnline/)"
                
                self.enviar_telegram(msg)
            else:
                print("😴 Nenhuma vaga encontrada.")

            print(f"⏳ Aguardando {MINUTOS_INTERVALO} minutos para próxima busca...")
            time.sleep(MINUTOS_INTERVALO * 60)

if __name__ == "__main__":
    monitor = SescMonitor()
    monitor.rodar()
