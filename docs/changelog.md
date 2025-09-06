Changelog

Data: 2025-09-06

Aplicado
- Segurança: TLS habilitado por padrão no HTTP/WS; opção `IQOPTIONAPI_INSECURE_SSL` para desativar em desenvolvimento.
- HTTP v2: `response.raise_for_status()` reativado para propagação de erros.
- Performance: inclusão de pequenas esperas em loops de espera (busy-waits) para reduzir uso de CPU.
- Correções de bugs:
  - `stable_api.py:get_candles`: chamada correta a `self.check_connect()` e espera curta no aguardo de candles.
  - `stable_api.py:start_mood_stream/stop_mood_stream`: correção de testes de pertença e remoção correta da lista.
  - `stable_api.py`: esperas curtas em diversos loops de aguardo (`get_*`, `close_*`, etc.).
  - `ws/received/position_changed.py`: ajuste de precedência lógica para roteamento consistente de mensagens.
- Documentação: adicionados `README.md` e `docs/` (overview, usage, configuration, roadmap, changelog).

Fase 1 — início
- Exceções tipadas em `iqoptionapi/errors.py` (ApiError, NetworkError, HttpError, AuthError, NotFoundError, RateLimitError, ServerError, TimeoutError).
- Wrapping dos erros HTTP/requests em `send_http_request(_v2)` para lançar exceções tipadas.
- Timeouts configuráveis via `IQOPTIONAPI_DEFAULT_TIMEOUT` para operações bloqueantes em alto nível (métodos selecionados).
- `stable_api.connect`: tratamento robusto de erros não-JSON e fluxo de 2FA preservado.

Fase 1 — concluída
- Timeouts aplicados em operações bloqueantes principais de alto nível:
  - `get_candles`, `get_balances`, `get_financial_information`, `get_leader_board`,
    `reset_practice_balance`, `get_instrument_quites_generated_data`,
    `get_realtime_strike_list`, `get_order`, `get_pending`, `get_positions`,
    `get_position`, `get_digital_position_by_position_id`, `get_digital_position`,
    `get_position_history`, `get_position_history_v2`, `get_available_leverages`,
    `cancel_order`, `close_position`, `close_position_v2`,
    `get_user_profile_client`, `request_leaderboard_userinfo_deals_client`,
    `get_users_availability`, `start_mood_stream`.
- Documentação atualizada (`docs/configuration.md`, `docs/errors.md`) para refletir novos controles e exceções.
- Conexão com timeouts: `start_websocket` e `send_ssid` agora respeitam timeouts padrão; espera por `timeSync` também limitada.

Fase 2 — concluída
- Pending requests: adicionados métodos `register_pending`, `resolve_pending`, `wait_request` em `IQOptionAPI`.
- Resolução automática por `request_id` no `ws/client.py:on_message`.
- Canais: registro de pending em `digital_option.py` (v1/v2), `buyv3.py`, `buy_place_order_temp.py`, `get_order.py`, `get_deferred_orders.py`, `get_positions.py`, `get_available_leverages.py`, `cancel_order.py`, `close_position.py`, `change_tpsl.py`, `change_auto_margin_call.py`.
- WS client: resolve pendências por `request_id` para nomes relevantes e sinaliza `result` específico do `request_id`.
- Alto nível: `buy_digital_spot`, `buy_digital`, `buy_digital_spot_v2`, `buy_order`, `get_order`, `get_pending`, `get_positions`, `get_position`, `get_digital_position(_by_position_id)`, `get_available_leverages`, `change_order`, `change_auto_margin_call`, `cancel_order`, `close_position` aguardam Events (com timeout) e fazem fallback.
- `buy` (binário/turbo): combina `option` + `result` pelo `request_id` (aguarda `option` e tenta `result` com timeout) para sinalizar sucesso/fracasso.

Compatibilidade
- Mudanças são retrocompatíveis para usuários que não dependiam de TLS desabilitado. Para reproduzir o comportamento antigo (inseguro), defina `IQOPTIONAPI_INSECURE_SSL=true`.
Fase 3 — início
- Substituído `global_value` por `state` por instância (`iqoptionapi/state.py`): flags de conexão, mutex de envio e `balance_id` agora vivem em `self.state`.
- Atualizações nos módulos: `api.py`, `ws/client.py`, `ws/received/profile.py`, canais WS que usavam `global_value` (`buyv3.py`, `buy_place_order_temp.py`, `digital_option.py`, `get_deferred_orders.py`, `get_positions.py`, `get_available_leverages.py`, `api_game_getoptions.py`, `buyv2.py`).
- `stable_api.py` atualizado para usar `self.api.state.balance_id` e flags de conexão.

Fase 3 — concluída
- Fila de envio WS com backpressure e thread dedicada implementada no `api.py` (configurável por `IQOPTIONAPI_SEND_QUEUE_MAX`).
- `send_websocket_request` agora enfileira mensagens e o worker envia de forma sequencial e resiliente.

Fase 5 — início
- Tipagem:
  - Adicionado `iqoptionapi/types.py` com tipos básicos: `InstrumentType` (Enum), `RequestId` (type alias), `WsMessage` (TypedDict) e `WsSendEnvelope` (dataclass).
  - Type hints parciais em `api.py` (HTTP/WS/pending/result), `ws/client.py` (assinatura do on_message) e assinaturas seletivas em `stable_api.py`.

Fase 4 — concluída
- Observabilidade:
  - Logs de envio WS com correlação por request_id: linhas `ws_send name=<evento> req_id=<id>`.
- Reconexão automática:
  - Monitor no `IQ_Option` com backoff exponencial; re-subscribe determinístico após reconectar.
  - Configuração: `IQOPTIONAPI_AUTO_RECONNECT` (padrão: true) e `IQOPTIONAPI_RECONNECT_MAX_BACKOFF` (padrão: 60s).
- Re-subscribe determinístico:
  - Candles (granularidade única e todas), traders mood, `top-assets-updated` e `commission-changed` preservados em reconexões.

Fase 5 — concluída
- Tipagem e modelos:
  - Adicionado `iqoptionapi/types.py` com tipos base (`InstrumentType`, `RequestId`, `WsMessage`, `WsSendEnvelope`).
  - Type hints aplicadas nos pontos centrais (`api.py`, `ws/client.py:on_message`, `ws/chanels/base.py`, assinaturas em `stable_api.py`).
  - Handlers WS tipados: `time_sync`, `balances`, `profile`, `candles`, `candle_generated_v2`, `digital_option_placed`, `order`, `result`, `order_canceled`, `position`.
- Ferramentas:
  - Incluído `mypy.ini` básico (ver CI no Sprint 7).
