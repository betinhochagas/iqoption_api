Errors

Exceções tipadas
- ApiError: base para todas as exceções da biblioteca.
- NetworkError: falhas de rede/requests (DNS, conexão, timeout HTTP, etc.).
- HttpError: erro HTTP genérico (status 4xx/5xx), inclui `status_code`, `url`, `body`.
- AuthError: 401/403.
- NotFoundError: 404.
- RateLimitError: 429.
- ServerError: 5xx.
- TimeoutError: tempo de espera excedido em operações bloqueantes de alto nível.

Notas
- Métodos HTTP agora propagam exceções tipadas; capture conforme necessidade:
```python
from iqoptionapi.errors import ApiError, AuthError, RateLimitError

try:
    resp = api.login("email", "senha")
except AuthError as e:
    print("Falha de autenticação:", e)
except RateLimitError:
    time.sleep(1)
except ApiError as e:
    print("Erro de API:", e)
```

