# Notification Service

Email, SMS, and Push Notification Service with provider abstraction.

## Features

- **Multi-channel**: Email, SMS, and Push notifications
- **Provider abstraction**: Mock provider for testing, extensible for real providers (Twilio, SendGrid, etc.)
- **Priority levels**: 4-tier priority system (low, normal, high, urgent)
- **Input validation**: E.164 phone format, EmailStr validation, Pydantic models
- **Template support**: Notification templates endpoint

## Environment Variables

```bash
# No specific env vars required for mock provider
# Real providers would require:
# SENDGRID_API_KEY=your_key_here
# TWILIO_SID=your_sid_here
# TWILIO_AUTH_TOKEN=your_token_here
```

## API Endpoints

### Health & Info

- `GET /` - Root endpoint
- `GET /health` - Health check with provider status
- `GET /api/v1/provider` - Get active provider info

### Notifications

- `POST /api/v1/notify/email` - Send email notification
- `POST /api/v1/notify/sms` - Send SMS notification (E.164 phone format)
- `POST /api/v1/notify/push` - Send push notification

### Templates

- `GET /api/v1/notify/templates` - List available templates

## Quick Start

### Run Service

```bash
cd services/notification-service
uvicorn main:app --port 8011 --reload
```

### Run Tests

```bash
# All tests (in-process via ASGITransport)
pytest services/notification-service/tests/test_notification_service.py -v

# Specific test class
pytest services/notification-service/tests/test_notification_service.py::TestEmailNotifications -v

# Quick mode
pytest services/notification-service/tests/test_notification_service.py -q
```

## Example Payloads

### Email Notification

```json
{
  "to": "user@example.com",
  "subject": "Interview Invitation",
  "html": "<h1>You are invited</h1>",
  "text": "You are invited to an interview",
  "priority": "high"
}
```

### SMS Notification (E.164 Format)

```json
{
  "to": "+14155552671",
  "text": "Your interview is scheduled for tomorrow",
  "priority": "urgent"
}
```

### Push Notification

```json
{
  "to": "device_token_abc123",
  "title": "Interview Scheduled",
  "body": "Your interview is confirmed for Dec 16",
  "data": {"interview_id": "123", "candidate_id": "456"},
  "priority": "normal"
}
```

## Priority Levels

- `low` - Non-urgent informational notifications
- `normal` - Standard notifications (default)
- `high` - Important notifications requiring attention
- `urgent` - Critical time-sensitive notifications

## Phone Number Validation

SMS notifications require E.164 international format:

- Must start with optional `+`
- Must start with digit 1-9 (no leading zeros)
- 2-15 digits total
- Examples: `+14155552671`, `442071234567`, `+61412345678`

## Testing Notes

- All tests run in-process via ASGITransport (no external server needed)
- Mock provider returns success for all operations
- 26 tests covering email/SMS/push, validation, error handling, integration

## Architecture

```
notification-service/
├── main.py              # FastAPI app with endpoints
├── schemas.py           # Pydantic models + NotificationPriority enum
├── providers/           # Provider implementations
│   └── __init__.py      # get_provider() + MockProvider
└── tests/
    └── test_notification_service.py  # 26 tests (ASGITransport)
```
