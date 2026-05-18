import time
import logging
from enum import Enum
from functools import wraps

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = State.CLOSED

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if self.state == State.OPEN:
                if time.time() - self.last_failure_time > self.recovery_timeout:
                    self.state = State.HALF_OPEN
                    logging.info("Circuit breaker HALF_OPEN")
                else:
                    logging.warning("Circuit breaker OPEN, fast failing")
                    raise Exception("Circuit breaker is OPEN")

            try:
                result = func(*args, **kwargs)
                if self.state == State.HALF_OPEN:
                    self.state = State.CLOSED
                    self.failure_count = 0
                    logging.info("Circuit breaker CLOSED")
                return result
            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()
                logging.error(f"Function call failed ({self.failure_count}/{self.failure_threshold}): {e}")
                
                if self.failure_count >= self.failure_threshold:
                    self.state = State.OPEN
                    logging.error("Circuit breaker OPEN")
                
                raise e
        return wrapper

# Global instance for Ollama calls
ollama_circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=60)
