Overview

Arquitetura
- HTTP: `requests.Session` compartilhada para endpoints de autenticação, perfil, appinit e eventos.
- WebSocket: `websocket.WebSocketApp` com callbacks (`on_open`, `on_message`, `on_error`, `on_close`).
- Estado: objeto `api` mantém atributos atualizados pelos handlers em `ws/received/*` (candles, perfil, posições, ordens, etc.).
- Alto nível: `IQ_Option` (em `stable_api.py`) fornece operações de conveniência e sincronização simples.

Módulos principais
- `iqoptionapi/api.py`: constrói URLs HTTP, executa requisições, gerencia a sessão (TLS, proxies), abre WS e envia mensagens.
- `iqoptionapi/stable_api.py`: oferece métodos de alto nível (connect, candles RT, buy/sell binário e digital, CFDs/forex, histórico, payout, leaderboard, etc.).
- `iqoptionapi/ws/client.py`: loop do WebSocket; roteia mensagens para `iqoptionapi/ws/received/*`.
- `iqoptionapi/ws/chanels/*`: geradores de mensagens WS (subscribe/unsubscribe, buy, portfolio, digital-options, price-splitter...).
- `iqoptionapi/ws/received/*`: tratadores para cada `message.name` (ex.: `candles`, `candle-generated`, `position-changed`, `order`, `result`, etc.).
- `iqoptionapi/http/*`: recursos HTTP (login v2, 2FA: send_sms/verify, logout, auth, appinit, billing, events, getprofile...).
- `iqoptionapi/constants.py`: mapeamento estático parcial de ativos.
- `iqoptionapi/global_value.py`: flags globais para coordenação mínima (conexão WS, mutex de envio, SSID, balance_id).

Fluxos importantes
- Autenticação:
  - `login`/`login2fa` em `auth.iqoption.com` (v2), `send_sms` e `verify` para 2FA.
  - Cookie `ssid` usado para autenticar no WS; persistido na sessão HTTP.
- Conexão WS:
  - `api.connect()` abre WS, aguarda `timeSync`, injeta `ssid` e confirma `profile` e `balances`.
- Market data:
  - `subscribe`/`candles-generated`, `candle-generated` para candles.
  - `price-splitter.client-price-generated` (payout digital), `instrument-quotes-generated` (lista de strikes/profit digital).
- Trading:
  - Binário/Turbo: `binary-options.open-option` (via `buyv3`).
  - Digital: `digital-options.place-digital-option` (v1/v2), `digital-options.close-position`.
  - CFDs/Forex/Crypto: `place-order-temp`, `cancel-order`, `get-positions`, `get-position`, `portfolio.get-history-positions`.
- Portfolio/ordens:
  - Subscrições `portfolio.position-changed` e `portfolio.order-changed` por tipo de instrumento.

Canais WS (exemplos)
- Dados: `candles`, `candle-generated`, `candles-generated`, `top-assets-updated`, `commission-changed`, `price-splitter.client-price-generated`, `instrument-quotes-generated`.
- Trading: `binary-options.open-option`, `digital-options.place-digital-option`, `digital-options.close-position`.
- Portfolio: `get-positions`, `get-position`, `portfolio.get-history-positions`.
- Conta: `profile`, `balances`, `balance-changed`.
- Infra: `timeSync`, `heartbeat`.

Sincronização e estado
- Handlers em `ws/received/*` atualizam atributos de `api` (ex.: `api.candles.candles_data`, `api.position`, `api.result`, etc.).
- A camada `stable_api` aguarda as alterações com loops curtos (com pequena espera) e timeouts quando aplicável.

Riscos e limitações conhecidas
- Dependência de mudanças do protocolo/servidor.
- Tabela de `ACTIVES` estática (pode ficar desatualizada; API já possui meios para preencher via init v2 e instruments).

