Configuration

Variáveis de Ambiente
- IQOPTIONAPI_INSECURE_SSL: `true|false` (padrão: false)
  - Quando `true`, desativa verificação de certificados TLS no HTTP/WS. Use somente em desenvolvimento.
- IQOPTIONAPI_TRUST_ENV: `true|false` (padrão: false)
  - Quando `true`, a sessão `requests` usa variáveis de ambiente do sistema para proxies.
- IQOPTIONAPI_DEFAULT_TIMEOUT: número em segundos (padrão: 10)
  - Tempo máximo de espera para operações bloqueantes em alto nível (ex.: candles, posições, fechamento de posição).
- IQOPTIONAPI_SEND_QUEUE_MAX: inteiro (padrão: 1000)
  - Tamanho máximo da fila de envio do WebSocket antes de aplicar backpressure.

Logging
- A biblioteca usa `logging` do Python. Configure o nível/handler no aplicativo que consome a lib.
  ```python
  import logging
  logging.basicConfig(level=logging.INFO)
  ```
- Logs WS:
  - Envio WS gera linhas `ws_send name=<evento> req_id=<id>` para correlação simples.

Notas de Segurança
- A verificação TLS é habilitada por padrão para proteger credenciais e tráfego.
- Não habilite `INSECURE_SSL` em produção.

Reconexão automática
- IQOPTIONAPI_AUTO_RECONNECT: `true|false` (padrão: true)
  - Habilita o monitor de reconexão automática no nível alto (`IQ_Option`).
- IQOPTIONAPI_RECONNECT_MAX_BACKOFF: segundos (padrão: 60)
  - Tempo máximo do backoff exponencial entre tentativas de reconexão.
