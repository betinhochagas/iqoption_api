Roadmap (sanitizado)

Fases e Entregaveis
- Fase 1 — Estabilidade e Seguranca: Concluida 2025-09-06
  - TLS por padrao; raise_for_status; sleeps minimos; mapeamento de erros; timeouts
- Fase 2 — Eventos (request_id): Concluida 2025-09-06
  - Pending/resolve/wait; canais com request_id; alto nivel usando Events
- Fase 3 — Estado e Concorrencia: Concluida 2025-09-06
  - `state` por instancia; fila de envio WS com backpressure
- Fase 4 — Observabilidade e Reconnect: Concluida 2025-09-06
  - Logs `ws_send`; auto reconnect com backoff; re-subscribe deterministico
- Fase 5 — Tipagem e Modelos: Concluida 2025-09-06
  - `types.py`; type hints em modulos centrais; mypy.ini
- Fase 6 — Dinamica de Ativos: Planejada
  - Atualizar ACTIVES dinamicamente via init/instruments; fallback estatico
- Fase 7 — Testes e CI/CD: Planejada
  - CI (lint+mypy+tests) e testes unitarios/mocks/smoke; publicacao

Cronograma
- Sprint 1: 2025-09-08 → 2025-09-21 — Concluida antecipadamente (2025-09-06)
  - Excecoes + timeouts + inicio de Events (digital)
- Sprint 2: 2025-09-22 → 2025-10-05 — Concluida (2025-09-06)
  - Events generalizados + reconexao/backoff + re-subscribe deterministico
- Sprint 3: 2025-10-06 → 2025-10-19 — Concluida (2025-09-06)
  - Estado por instancia; locks; fila de envio WS
- Sprint 4: 2025-10-20 → 2025-11-02 — Concluida (2025-09-06)
  - Observabilidade (logs) + Auto reconnect
- Sprint 5: 2025-11-03 → 2025-11-30 — Concluida antecipadamente (2025-09-06)
  - Tipagem/modelos (escopo ajustado); CI fica no Sprint 7
- Buffer: 2025-12-01 → 2025-12-07
- Sprint 6: 2025-12-08 → 2025-12-21
  - Dinamica de ACTIVES (init/instruments) e migracao suave
- Sprint 7: 2025-12-22 → 2026-01-05
  - CI (lint+mypy+tests), testes unitarios/mocks/smoke, pipeline publicacao

Observacoes
- Datas podem ajustar-se a feriados/localidade; sprints mantem duracao de 2 semanas quando possivel.

