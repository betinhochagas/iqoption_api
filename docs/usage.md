Usage

Conexão básica
```python
from iqoptionapi.stable_api import IQ_Option

I = IQ_Option("email@example.com", "password")
ok, reason = I.connect()
if not ok:
    print("Falha ao conectar:", reason)
    raise SystemExit(1)

# Seleciona saldo (REAL/PRACTICE/TOURNAMENT)
I.change_balance("PRACTICE")

print("Currency:", I.get_currency())
print("Balance:", I.get_balance())
```

2FA por SMS
```python
ok, reason = I.connect()
if not ok and reason == "2FA":
    code = input("Digite o código recebido por SMS: ")
    ok, reason = I.connect_2fa(code)
```

Candles históricos e tempo real
```python
# Histórico (count candles até endtime)
end = I.get_server_timestamp()
candles = I.get_candles("EURUSD", 60, 100, end)

# Tempo real
I.start_candles_stream("EURUSD", 60, 50)
rt = I.get_realtime_candles("EURUSD", 60)
I.stop_candles_stream("EURUSD", 60)
```

Sinais e métricas
```python
# Traders mood (percentual)
I.start_mood_stream("EURUSD")
print(I.get_traders_mood("EURUSD"))
```

Binário/Turbo (buy)
```python
# direction: "call" ou "put"; expirations: minutos
ok, order_id = I.buy(1.0, "EURUSD", "call", 1)
print("Ordem:", ok, order_id)
```

Digital
```python
ok, order_id = I.buy_digital_spot_v2("EURUSD", 2.5, "call", 1)
status, pnl = I.check_win_digital_v2(order_id)
```

CFDs/Forex/Crypto
```python
ok, order_id = I.buy_order(
    instrument_type="forex", instrument_id="EURUSD",
    side="buy", amount=10, leverage=100,
    type="market"
)
print("Order:", ok, order_id)
```

Histórico e posições
```python
ok, positions = I.get_positions("forex")
ok, hist = I.get_position_history("forex")
```

Logout
```python
I.logout()
```

