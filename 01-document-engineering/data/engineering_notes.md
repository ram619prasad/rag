# Payment Service

## Database
- Primary: PostgreSQL
- Cache: Redis

## API Endpoints
| Method | Endpoint |
|--------|----------|
| POST | /payments |
| GET | /payments/{id} |

## Configuration
```python
MAX_RETRIES = 3