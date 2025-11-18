"""Resilience patterns: Circuit breaker, retry logic, timeouts."""
import asyncio
import time
import logging
from typing import Callable, Optional, Any, Dict
from enum import Enum
from functools import wraps

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by failing fast when a service is unavailable.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            expected_exception: Exception type that triggers circuit
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[float] = None
        self.state = CircuitState.CLOSED

    def __call__(self, func: Callable) -> Callable:
        """Decorator for circuit breaker."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.call(func, *args, **kwargs)
        return wrapper

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker."""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state for {func.__name__}")
            else:
                logger.warning(
                    f"Circuit breaker OPEN for {func.__name__}, "
                    f"rejecting call (failures: {self.failure_count})"
                )
                from src.core.exceptions import AIProviderUnavailable
                raise AIProviderUnavailable(provider=func.__name__)

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result

        except self.expected_exception as e:
            self._on_failure()
            logger.error(
                f"Circuit breaker recorded failure for {func.__name__}: {str(e)}"
            )
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.last_failure_time is None:
            return False
        return time.time() - self.last_failure_time >= self.recovery_timeout

    def _on_success(self):
        """Handle successful call."""
        if self.state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker recovered, closing circuit")

        self.failure_count = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        """Handle failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker opened after {self.failure_count} failures"
            )


class RetryStrategy:
    """
    Retry strategy with exponential backoff.
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        """
        Initialize retry strategy.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay in seconds
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            jitter: Add random jitter to prevent thundering herd
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter

    def __call__(self, func: Callable) -> Callable:
        """Decorator for retry."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await self.execute(func, *args, **kwargs)
        return wrapper

    async def execute(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with retry logic."""
        last_exception = None

        for attempt in range(self.max_retries + 1):
            try:
                return await func(*args, **kwargs)

            except Exception as e:
                last_exception = e

                if attempt < self.max_retries:
                    delay = self._calculate_delay(attempt)
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{self.max_retries} "
                        f"for {func.__name__} after {delay:.2f}s: {str(e)}"
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"All {self.max_retries} retry attempts failed for {func.__name__}"
                    )

        raise last_exception

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for retry attempt."""
        delay = min(
            self.initial_delay * (self.exponential_base ** attempt),
            self.max_delay
        )

        if self.jitter:
            import random
            delay = delay * (0.5 + random.random() * 0.5)

        return delay


class Timeout:
    """
    Timeout decorator for async functions.
    """

    def __init__(self, seconds: float):
        """
        Initialize timeout.

        Args:
            seconds: Timeout in seconds
        """
        self.seconds = seconds

    def __call__(self, func: Callable) -> Callable:
        """Decorator for timeout."""
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.seconds
                )
            except asyncio.TimeoutError:
                logger.error(
                    f"Function {func.__name__} timed out after {self.seconds}s"
                )
                from src.core.exceptions import AIProviderTimeout
                raise AIProviderTimeout(provider=func.__name__)
        return wrapper


# Global circuit breakers for AI providers
_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(provider: str) -> CircuitBreaker:
    """Get or create circuit breaker for provider."""
    if provider not in _circuit_breakers:
        _circuit_breakers[provider] = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
    return _circuit_breakers[provider]


def with_resilience(
    provider: str,
    max_retries: int = 3,
    timeout_seconds: float = 30.0
):
    """
    Combined decorator for resilience patterns.

    Applies: Circuit Breaker + Retry + Timeout

    Example:
        @with_resilience(provider="anthropic", max_retries=3, timeout_seconds=30)
        async def call_anthropic_api():
            # API call
            pass
    """
    circuit_breaker = get_circuit_breaker(provider)
    retry_strategy = RetryStrategy(max_retries=max_retries)
    timeout = Timeout(seconds=timeout_seconds)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Apply timeout -> retry -> circuit breaker
            @timeout
            @retry_strategy
            async def resilient_call():
                return await circuit_breaker.call(func, *args, **kwargs)

            return await resilient_call()

        return wrapper

    return decorator


# Monitoring
def get_circuit_breaker_stats() -> Dict[str, Dict[str, Any]]:
    """Get statistics for all circuit breakers."""
    return {
        provider: {
            "state": breaker.state.value,
            "failure_count": breaker.failure_count,
            "last_failure_time": breaker.last_failure_time
        }
        for provider, breaker in _circuit_breakers.items()
    }
