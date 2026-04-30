# OGUser Monitor

Monitor em Python para verificar alertas e mensagens privadas no OGUser e enviar notificações via Telegram.

## Requisitos

- Python 3.10+
- Conta no Telegram
- Bot do Telegram criado via BotFather
- Cookie `ogumybbuser` válido da sessão OGUser

## Instalação

Clone o repositório e instale as dependências:

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Configuração

Edite as constantes no arquivo `OGUser-Monitor.py`:

```python
OGUSER_TOKEN = "YOUR_OGUMYBBUSER_COOKIE"
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
POLL_SECONDS = 3
```

Campos:

- `OGUSER_TOKEN`: valor do cookie `ogumybbuser` da sua sessão autenticada.
- `TELEGRAM_BOT_TOKEN`: token do bot Telegram.
- `TELEGRAM_CHAT_ID`: ID do chat, grupo ou usuário que receberá as notificações.
- `POLL_SECONDS`: intervalo entre verificações.

## Execução

```bash
python OGUser-Monitor.py
```

O script cria automaticamente o arquivo `oguser_seen.json` para registrar eventos já enviados. Esse arquivo é estado local de execução e não deve ser enviado ao GitHub.

## Arquivos recomendados no repositório

```text
OGUser-Monitor.py
README.md
requirements.txt
.gitignore
```

## Segurança

Não envie tokens, cookies, arquivos `.env` ou `oguser_seen.json` para o GitHub. O cookie `ogumybbuser` equivale a uma sessão autenticada e deve ser tratado como segredo.

## Observações técnicas

- O script usa `tls-client` para criar uma sessão HTTP com fingerprint semelhante ao Chrome.
- O parser HTML depende da estrutura atual das páginas do OGUser. Mudanças no site podem exigir ajustes nos seletores CSS.
- Se receber erro `403`, `Cloudflare challenge retornado` ou redirecionamento para login, valide o cookie e a sessão.
