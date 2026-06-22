@ gateway/breaker.py
import time
from datetime import timedelta
from aiobreaker import CircuitBreaker, CircuitBreakerListener

db_breaker = CircuitBreaker(fail_max=3, timeout_duration=timedelta(seconds=10))

class ProductionStyleListener(CircuitBreakerListener):
    def state_change(self, breaker, old_state, new_state):
        if old_state.state != new_state.state:
            print(f"\n🚨 [🚨 SYSTEM ALERT] 斷路器狀態切換: {old_state.state.name} ➡ {new_state.state.name} (Time: {time.strftime('%X')})")

db_breaker.add_listener(ProductionStyleListener())