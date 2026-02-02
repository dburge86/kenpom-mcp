# ADR 003: Custom Exception Hierarchy for Retry Logic

**Status:** Accepted
**Date:** January 30, 2026 (Task 7 of polish plan)
**Decision Maker:** David Burgess
**Context:** Adding network resilience to scraper login

---

## Context

The scraper's `login()` method makes HTTP requests to KenPom.com that can fail for two distinct reasons:

1. **Authentication Failures:** Invalid credentials, expired subscription, account issues
   - **Permanent failures** that won't resolve by retrying
   - Should fail immediately with clear error message
   - Example: "KENPOM_EMAIL required" or "Invalid credentials"

2. **Network Failures:** Timeouts, DNS errors, connection resets, 5xx server errors
   - **Transient failures** that may resolve on retry
   - Should retry with exponential backoff
   - Example: "Connection timeout" or "503 Service Unavailable"

**Problem:** Python's built-in exceptions don't distinguish between these failure types. Using generic `Exception` or `httpx.RequestError` would force retry logic to apply uniformly to both cases, wasting retries on permanent auth failures.

---

## Decision

Create a **custom exception hierarchy** that distinguishes permanent failures from transient failures:

```python
class KenPomError(Exception):
    """Base exception for all KenPom errors"""
    pass

class AuthenticationError(KenPomError):
    """Permanent auth failure - do not retry"""
    pass

class NetworkError(KenPomError):
    """Transient network failure - retry with backoff"""
    pass
```

Apply retry logic **only to NetworkError** using the tenacity library:

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    retry=retry_if_exception_type(NetworkError),  # Only retry NetworkError
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    before_sleep=before_sleep_log(logger, logging.WARNING),
)
async def login(self) -> bool:
    try:
        # HTTP request logic
        ...
    except httpx.TimeoutException as e:
        raise NetworkError(f"Login timeout: {e}") from e
    except httpx.ConnectError as e:
        raise NetworkError(f"Connection failed: {e}") from e
    except Exception as e:
        if "Logged in as" not in response.text:
            raise AuthenticationError("Invalid credentials") from e
        raise NetworkError(f"Unknown error: {e}") from e
```

---

## Consequences

### Positive

✅ **Smart Retries:** Only retries failures that might succeed on retry
✅ **Fast Failures:** Auth errors fail immediately without wasting time
✅ **Clear Error Messages:** Users know if it's auth or network issue
✅ **Production Ready:** Handles transient network failures gracefully
✅ **Logging:** Retry attempts logged at WARNING level for debugging
✅ **Exponential Backoff:** 2s → 4s → 8s prevents hammering server

### Negative

⚠️ **Exception Wrapping:** All `httpx` exceptions must be caught and wrapped
⚠️ **Testing Complexity:** Must test both exception types and retry behavior
⚠️ **Tenacity Quirk:** When retries exhausted, raises `RetryError` not `NetworkError`

### Mitigations

- **Comprehensive Tests:** Added 3 tests covering retry behavior (see test_scraper.py:114-159)
- **Clear Docstrings:** Exception classes document when to use each
- **Logging:** `before_sleep_log` makes retry attempts visible

---

## Alternatives Considered

### 1. Generic Retry for All Exceptions
**Pros:** Simpler, no custom exceptions
**Cons:** Wastes retries on permanent auth failures (6-20 seconds delay)
**Rejected:** Poor user experience for common error (bad credentials)

### 2. HTTP Status Code Filtering
**Pros:** Could retry on 5xx but not 4xx
**Cons:** Auth failures don't always return clean HTTP status codes
**Rejected:** KenPom responses not always RESTful (302 redirects, HTML errors)

### 3. Multiple Exception Types per Failure
**Pros:** Could distinguish timeout vs connection vs DNS errors
**Cons:** Too granular, all benefit from same retry strategy
**Rejected:** Two-tier hierarchy (auth vs network) is sufficient

### 4. Built-in httpx Retry
**Pros:** httpx supports Transport with retry logic
**Cons:** Can't customize based on response content (e.g., "Logged in as" text)
**Rejected:** Need response inspection for auth validation

---

## Implementation Details

### Exception Hierarchy
```python
# scraper.py
class KenPomError(Exception):
    """Base exception for KenPom scraper"""

class AuthenticationError(KenPomError):
    """Raised when login fails due to bad credentials"""

class NetworkError(KenPomError):
    """Raised when network request fails (transient)"""
```

### Retry Configuration
- **Max Attempts:** 3 (initial + 2 retries)
- **Backoff:** Exponential with multiplier=1
- **Wait Times:** 2s → 4s → 8s (min=2, max=10)
- **Retry Condition:** Only `NetworkError` (not `AuthenticationError`)
- **Logging:** WARNING level via `before_sleep_log`

### Error Mapping
| httpx Exception        | Maps To         | Retry? |
|------------------------|-----------------|--------|
| `TimeoutException`     | `NetworkError`  | ✅ Yes  |
| `ConnectError`         | `NetworkError`  | ✅ Yes  |
| `ConnectTimeout`       | `NetworkError`  | ✅ Yes  |
| `ReadTimeout`          | `NetworkError`  | ✅ Yes  |
| Generic + no "Logged in" | `AuthenticationError` | ❌ No |
| Other exceptions       | `NetworkError`  | ✅ Yes  |

---

## Test Coverage

### Test Cases (test_scraper.py:114-159)

1. **test_login_network_error_retries_and_succeeds**
   - Mock first two attempts to fail with `ConnectError`
   - Third attempt succeeds
   - Verifies: Retry logic works, eventually succeeds

2. **test_login_network_error_exhausts_retries**
   - Mock all attempts to fail with `TimeoutException`
   - Verifies: After 3 attempts, raises `RetryError`

3. **test_login_auth_error_no_retry**
   - Mock response with no "Logged in as" text
   - Verifies: Raises `AuthenticationError` immediately, no retries

### Key Learning: RetryError Wrapping

When tenacity exhausts retries, it raises `RetryError` wrapping the original `NetworkError`:
```python
try:
    await scraper.login()
except RetryError as e:
    assert isinstance(e.last_attempt.exception(), NetworkError)
```

Tests must catch `RetryError` and inspect `.last_attempt.exception()` to verify the underlying error type.

---

## Performance Impact

### Before (No Retry)
- Single network failure → Immediate failure
- User must manually retry

### After (With Retry)
- Single transient failure → Auto-retry after 2s
- Two transient failures → Auto-retry after 2s, 4s
- Three transient failures → Final failure after 14s total
- Auth failure → Immediate failure (0s overhead)

### Worst Case
- **Transient failures:** 14 seconds before final failure (2s + 4s + 8s)
- **Permanent failures:** 0 seconds (fail immediately)

---

## Monitoring & Debugging

### Log Output Examples

**Successful retry:**
```
WARNING: Retrying login after ConnectError (attempt 1/3)
INFO: Login successful for user@example.com
```

**Exhausted retries:**
```
WARNING: Retrying login after TimeoutException (attempt 1/3)
WARNING: Retrying login after TimeoutException (attempt 2/3)
WARNING: Retrying login after TimeoutException (attempt 3/3)
ERROR: Login failed after 3 attempts: RetryError
```

**Auth failure (no retry):**
```
ERROR: Authentication failed: Invalid credentials
```

---

## Related Decisions

- **ADR 001:** Dual Transport Architecture (both transports benefit from retry logic)

---

## References

- [Tenacity Documentation](https://tenacity.readthedocs.io/)
- [httpx Exceptions](https://www.python-httpx.org/exceptions/)
- [Python Exception Hierarchy Best Practices](https://docs.python.org/3/tutorial/errors.html#user-defined-exceptions)

---

**Last Updated:** 2026-02-02
