IQ Option API (Python) — Cliente HTTP/WS

Este repositório contém uma biblioteca Python para integração com a plataforma IQ Option utilizando HTTP e WebSocket. Ele oferece uma API de baixo nível (requests + websocket-client) e uma fachada de alto nível para uso em automações de trading.

Seções principais:
- Visão geral da arquitetura
- Guia rápido de uso
- Configuração e segurança (TLS e proxies)
- Estrutura do projeto
- Links para documentação detalhada

Documentação detalhada: veja os arquivos em `docs/`.

Guia Rápido
- Instancie `IQ_Option(email, password)` e chame `connect()`.
- Para candles em tempo real, use `start_candles_stream` e `get_realtime_candles`.
- Para comprar binário/turbo use `buy` ou `buy_by_raw_expirations`.
- Para digital use `buy_digital_spot_v2` ou `buy_digital`.
- Para CFDs/Forex use `buy_order` e consulte `get_order`, `get_positions`.

Exemplo mínimo
```python
from iqoptionapi.stable_api import IQ_Option

I_want_money = IQ_Option("email@example.com", "password")
ok, reason = I_want_money.connect()
if not ok:
    print("Falha ao conectar:", reason)
    raise SystemExit(1)

I_want_money.start_candles_stream("EURUSD", 60, 50)
print(I_want_money.get_realtime_candles("EURUSD", 60))
```

Configuração e Segurança
- Por padrão, a verificação de certificado TLS está ATIVADA.
- Defina `IQOPTIONAPI_INSECURE_SSL=true` apenas em desenvolvimento para desativar verificação TLS (HTTP/WS).
- Para permitir que a sessão honre variáveis de proxy do sistema, defina `IQOPTIONAPI_TRUST_ENV=true`.

Estrutura do Projeto
- `iqoptionapi/api.py`: núcleo HTTP/WS de baixo nível.
- `iqoptionapi/stable_api.py`: camada de alto nível (conveniência).
- `iqoptionapi/ws/chanels/*`: comandos/canais WebSocket (subscribe, buy, portfolio etc.).
- `iqoptionapi/ws/received/*`: handlers de mensagens WS que atualizam o estado.
- `iqoptionapi/http/*`: recursos HTTP (login, 2FA, profile, eventos etc.).
- `iqoptionapi/constants.py`: mapa ACTIVES (ativos → id).
- `iqoptionapi/global_value.py`: flags globais de sincronização.

Mais informações
- docs/overview.md — arquitetura detalhada e fluxos.
- docs/usage.md — exemplos práticos.
- docs/configuration.md — variáveis de ambiente e logging.
- docs/errors.md — classes de exceções e mapeamentos de erro.
- docs/roadmap.md — plano de evolução.
- docs/changelog.md — mudanças aplicadas.
