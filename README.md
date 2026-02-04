# 🏨 Monitor de Vagas SESC Roraima

Monitor automático de disponibilidade de hospedagem no SESC Roraima (Hotel Tepequém). Receba notificações no Telegram quando houver vagas disponíveis!

## ✨ Funcionalidades

- 🔍 Verifica automaticamente a disponibilidade de vagas
- 📱 Notificações instantâneas via Telegram
- ⏰ Execução contínua com intervalo configurável
- 🔄 Gerenciamento automático de sessão
- 🛡️ Headers realistas para evitar bloqueios

## 📋 Pré-requisitos

- Python 3.8+
- Conta no Telegram
- Bot do Telegram (criado via [@BotFather](https://t.me/BotFather))

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/monitor-sesc-vagas.git
cd monitor-sesc-vagas
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
TELEGRAM_TOKEN=seu_token_do_bot
TELEGRAM_CHAT_ID=seu_chat_id
```

## 🔑 Como obter as credenciais do Telegram

### Token do Bot
1. Abra o Telegram e procure por [@BotFather](https://t.me/BotFather)
2. Envie `/newbot` e siga as instruções
3. Copie o token fornecido (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Chat ID
1. Procure por [@userinfobot](https://t.me/userinfobot) no Telegram
2. Envie `/start`
3. O bot responderá com seu Chat ID

## ▶️ Uso

```bash
python monitor_sesc_curl.py
```

O monitor irá:
1. Iniciar uma sessão com o site do SESC
2. Verificar disponibilidade para os próximos 60 dias
3. Enviar notificação no Telegram se encontrar vagas
4. Aguardar o intervalo configurado e repetir

## ⚙️ Configurações

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `TELEGRAM_TOKEN` | Token do bot do Telegram | - |
| `TELEGRAM_CHAT_ID` | ID do chat para notificações | - |
| `DIAS_PARA_VERIFICAR` | Quantos dias à frente verificar | 60 |
| `MINUTOS_INTERVALO` | Intervalo entre verificações (min) | 480 |
| `UNIDADE_HOTEL` | Código da unidade do hotel | 51 |

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer um Fork do projeto
2. Criar uma branch para sua feature (`git checkout -b feature/NovaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/NovaFeature`)
5. Abrir um Pull Request

## ⚠️ Aviso Legal

Este projeto é apenas para fins educacionais. Use com responsabilidade e respeite os termos de uso do site do SESC. O autor não se responsabiliza pelo uso indevido desta ferramenta.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
