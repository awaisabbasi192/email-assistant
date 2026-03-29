# Email Assistant - API Documentation

**Version**: 2.0
**Last Updated**: March 27, 2026

---

## Base URL

```
http://localhost:5000/api
```

All requests require authentication (session cookie from login).

---

## Table of Contents

1. [Authentication](#authentication)
2. [Email Endpoints](#email-endpoints)
3. [Draft Endpoints](#draft-endpoints)
4. [Thread Endpoints](#thread-endpoints)
5. [Search Endpoints](#search-endpoints)
6. [Attachment Endpoints](#attachment-endpoints)
7. [Notification Endpoints](#notification-endpoints)
8. [Scheduler Endpoints](#scheduler-endpoints)
9. [LLM Endpoints](#llm-endpoints)
10. [Health & Status](#health--status)

---

## Authentication

### Login

**Endpoint**: `POST /login`

**Request**:
```json
{
  "username": "admin",
  "password": "your_password"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged in successfully",
  "redirect": "/dashboard"
}
```

**Response** (401 Unauthorized):
```json
{
  "success": false,
  "message": "Invalid credentials"
}
```

**Notes**:
- Sets secure session cookie
- CSRF token required for POST
- Rate limited to 5 attempts per minute
- Passwords hashed with bcrypt

### Logout

**Endpoint**: `GET /logout`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

---

## Email Endpoints

### List Emails

**Endpoint**: `GET /api/emails`

**Query Parameters**:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20)
- `status`: Filter by status (`unread`, `read`, `processed`, `draft`)
- `priority`: Filter by priority (`low`, `normal`, `high`, `urgent`)

**Response** (200 OK):
```json
{
  "success": true,
  "emails": [
    {
      "id": 1,
      "user_id": 1,
      "message_id": "abc123",
      "sender": "john@example.com",
      "subject": "Meeting Tomorrow",
      "body": "Let's discuss...",
      "priority": "high",
      "is_read": false,
      "has_attachments": true,
      "received_date": "2026-03-27T10:30:00",
      "thread_id": 5,
      "created_at": "2026-03-27T10:30:00"
    }
  ],
  "total": 150,
  "page": 1,
  "per_page": 20
}
```

### Get Email Details

**Endpoint**: `GET /api/emails/{email_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "email": {
    "id": 1,
    "sender": "john@example.com",
    "subject": "Meeting Tomorrow",
    "body": "Full email body...",
    "priority": "high",
    "is_read": true,
    "thread_id": 5,
    "attachments": [
      {
        "id": 1,
        "filename": "document.pdf",
        "mime_type": "application/pdf",
        "size_bytes": 102400
      }
    ]
  }
}
```

### Mark Email as Read

**Endpoint**: `PUT /api/emails/{email_id}/read`

**Request Body**:
```json
{
  "is_read": true
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Email marked as read"
}
```

### Delete Email

**Endpoint**: `DELETE /api/emails/{email_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Email deleted"
}
```

---

## Draft Endpoints

### List Drafts

**Endpoint**: `GET /api/drafts`

**Query Parameters**:
- `email_id`: Filter by parent email ID
- `status`: Filter by status (`draft`, `sent`, `scheduled`)

**Response** (200 OK):
```json
{
  "success": true,
  "drafts": [
    {
      "id": 1,
      "email_id": 5,
      "reply_body": "Thank you for your email...",
      "model_used": "claude",
      "confidence_score": 0.95,
      "status": "draft",
      "created_at": "2026-03-27T11:00:00"
    }
  ]
}
```

### Create Draft

**Endpoint**: `POST /api/drafts`

**Request Body**:
```json
{
  "email_id": 5,
  "reply_body": "Thank you...",
  "model_used": "claude"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "draft_id": 1,
  "message": "Draft created"
}
```

### Update Draft

**Endpoint**: `PUT /api/drafts/{draft_id}`

**Request Body**:
```json
{
  "reply_body": "Updated reply...",
  "confidence_score": 0.92
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Draft updated"
}
```

### Delete Draft

**Endpoint**: `DELETE /api/drafts/{draft_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Draft deleted"
}
```

---

## Thread Endpoints

### Get Email Thread

**Endpoint**: `GET /api/threads/{email_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "thread": {
    "thread_id": 5,
    "subject": "Project Discussion",
    "participants": ["john@example.com", "jane@example.com"],
    "message_count": 4,
    "date_range": {
      "start": "2026-03-20T09:00:00",
      "end": "2026-03-27T14:30:00"
    },
    "messages": [
      {
        "id": 1,
        "sender": "john@example.com",
        "subject": "Project Discussion",
        "body": "Let's discuss...",
        "received_date": "2026-03-20T09:00:00"
      },
      {
        "id": 2,
        "sender": "jane@example.com",
        "subject": "Re: Project Discussion",
        "body": "Great idea...",
        "received_date": "2026-03-20T10:15:00"
      }
    ]
  }
}
```

### Get Thread Summary

**Endpoint**: `GET /api/threads/{email_id}/summary`

**Response** (200 OK):
```json
{
  "success": true,
  "summary": {
    "thread_id": 5,
    "subject": "Project Discussion",
    "participants_count": 2,
    "message_count": 4,
    "date_range": {
      "start": "2026-03-20T09:00:00",
      "end": "2026-03-27T14:30:00"
    },
    "context": "Discussion about project timeline and deliverables"
  }
}
```

---

## Search Endpoints

### Full-Text Search

**Endpoint**: `GET /api/search`

**Query Parameters**:
- `q`: Search query (required)
- `limit`: Max results (default: 50)

**Example**:
```
GET /api/search?q=meeting+deadline&limit=20
```

**Response** (200 OK):
```json
{
  "success": true,
  "query": "meeting deadline",
  "results": [
    {
      "id": 1,
      "sender": "john@example.com",
      "subject": "Project Meeting - Important Deadline",
      "excerpt": "...the meeting is scheduled for Friday. The deadline...",
      "score": 0.95
    }
  ],
  "total": 3
}
```

### Advanced Search

**Endpoint**: `POST /api/search/advanced`

**Request Body**:
```json
{
  "query": "meeting",
  "filters": {
    "sender": "john@example.com",
    "priority": "high",
    "date_from": "2026-03-01",
    "date_to": "2026-03-31",
    "is_read": false,
    "has_attachment": true,
    "category": "work"
  },
  "limit": 50
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "results": [
    {
      "id": 1,
      "sender": "john@example.com",
      "subject": "Project Meeting",
      "priority": "high",
      "has_attachments": true,
      "received_date": "2026-03-20T09:00:00"
    }
  ],
  "total": 5
}
```

### Save Search

**Endpoint**: `POST /api/search/save`

**Request Body**:
```json
{
  "name": "Urgent Unread",
  "filters": {
    "priority": "urgent",
    "is_read": false
  }
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "search_id": 1,
  "message": "Search saved"
}
```

### List Saved Searches

**Endpoint**: `GET /api/search/saved`

**Response** (200 OK):
```json
{
  "success": true,
  "searches": [
    {
      "id": 1,
      "name": "Urgent Unread",
      "filters": {
        "priority": "urgent",
        "is_read": false
      },
      "created_at": "2026-03-27T10:00:00"
    }
  ]
}
```

### Execute Saved Search

**Endpoint**: `GET /api/search/saved/{search_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "search_name": "Urgent Unread",
  "results": [
    {
      "id": 1,
      "sender": "john@example.com",
      "subject": "Urgent: System Down",
      "priority": "urgent"
    }
  ],
  "total": 3
}
```

### Delete Saved Search

**Endpoint**: `DELETE /api/search/saved/{search_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Search deleted"
}
```

---

## Attachment Endpoints

### List Attachments

**Endpoint**: `GET /api/emails/{email_id}/attachments`

**Response** (200 OK):
```json
{
  "success": true,
  "attachments": [
    {
      "id": 1,
      "filename": "document.pdf",
      "mime_type": "application/pdf",
      "size_bytes": 102400,
      "is_downloaded": true,
      "attachment_id": "gmail_att_123"
    }
  ]
}
```

### Download Attachment

**Endpoint**: `GET /api/attachments/{attachment_id}/download`

**Response** (200 OK):
- Returns file binary content
- Sets `Content-Disposition: attachment` header

### Get Attachment Preview

**Endpoint**: `GET /api/attachments/{attachment_id}/preview`

**Response** (200 OK):
```json
{
  "success": true,
  "preview": {
    "type": "image",
    "data": "base64_encoded_image_data"
  }
}
```

Or for text files:
```json
{
  "success": true,
  "preview": {
    "type": "text",
    "content": "File content..."
  }
}
```

### Get Attachment Context

**Endpoint**: `GET /api/emails/{email_id}/attachments/context`

**Response** (200 OK):
```json
{
  "success": true,
  "context": "Email contains 2 attachments: document.pdf (102KB, PDF), image.jpg (256KB, JPEG image)"
}
```

### Get Attachment Statistics

**Endpoint**: `GET /api/attachments/stats`

**Response** (200 OK):
```json
{
  "success": true,
  "statistics": {
    "total_attachments": 150,
    "total_size_bytes": 52428800,
    "by_type": {
      "pdf": 45,
      "image": 60,
      "document": 30,
      "other": 15
    }
  }
}
```

---

## Notification Endpoints

### Get Notification Preferences

**Endpoint**: `GET /api/notifications/preferences`

**Response** (200 OK):
```json
{
  "success": true,
  "preferences": {
    "desktop_notifications": true,
    "notify_urgent": true,
    "notify_important": true,
    "notify_normal": false,
    "notify_low": false,
    "quiet_hours_enabled": true,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "08:00",
    "daily_digest_enabled": false,
    "daily_digest_time": "09:00"
  }
}
```

### Update Notification Preferences

**Endpoint**: `PUT /api/notifications/preferences`

**Request Body**:
```json
{
  "desktop_notifications": true,
  "notify_urgent": true,
  "notify_important": false,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00",
  "quiet_hours_end": "08:00"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Preferences updated"
}
```

### Send Test Notification

**Endpoint**: `POST /api/notifications/test`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Test notification sent"
}
```

---

## Scheduler Endpoints

### Schedule Email

**Endpoint**: `POST /api/scheduler/schedule`

**Request Body**:
```json
{
  "draft_id": 1,
  "scheduled_time": "2026-03-28T14:00:00"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "scheduled_id": 1,
  "message": "Email scheduled for 2026-03-28 at 14:00"
}
```

### Get Scheduled Emails

**Endpoint**: `GET /api/scheduler/scheduled`

**Response** (200 OK):
```json
{
  "success": true,
  "scheduled": [
    {
      "id": 1,
      "draft_id": 1,
      "scheduled_time": "2026-03-28T14:00:00",
      "status": "pending",
      "created_at": "2026-03-27T10:00:00"
    }
  ]
}
```

### Cancel Scheduled Email

**Endpoint**: `DELETE /api/scheduler/scheduled/{scheduled_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Scheduled email cancelled"
}
```

### Snooze Email

**Endpoint**: `POST /api/scheduler/snooze`

**Request Body**:
```json
{
  "email_id": 5,
  "snooze_until": "2026-03-28T14:00:00"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "snooze_id": 1,
  "message": "Email snoozed until 2026-03-28 at 14:00"
}
```

### Get Snoozed Emails

**Endpoint**: `GET /api/scheduler/snoozed`

**Response** (200 OK):
```json
{
  "success": true,
  "snoozed": [
    {
      "id": 1,
      "email_id": 5,
      "snooze_until": "2026-03-28T14:00:00",
      "snoozed_at": "2026-03-27T10:00:00"
    }
  ]
}
```

### Unsnooze Email

**Endpoint**: `DELETE /api/scheduler/snoozed/{snooze_id}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Email unsnoozed"
}
```

---

## LLM Endpoints

### Get Provider Status

**Endpoint**: `GET /api/llm/status`

**Response** (200 OK):
```json
{
  "success": true,
  "providers": {
    "claude": {
      "available": true,
      "last_error": null,
      "failure_count": 0
    },
    "ollama": {
      "available": true,
      "last_error": null,
      "failure_count": 0
    },
    "template": {
      "available": true,
      "last_error": null
    }
  },
  "active_provider": "claude"
}
```

### Generate Reply

**Endpoint**: `POST /api/llm/reply`

**Request Body**:
```json
{
  "email_id": 5,
  "custom_instructions": "Keep reply brief and professional"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "reply": "Thank you for your email. I appreciate your input...",
  "provider": "claude",
  "confidence_score": 0.92
}
```

### Regenerate Reply

**Endpoint**: `POST /api/llm/reply/regenerate`

**Request Body**:
```json
{
  "draft_id": 1,
  "force_provider": "ollama"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "reply": "Thank you for reaching out...",
  "provider": "ollama"
}
```

### Reset Circuit Breaker

**Endpoint**: `POST /api/llm/reset-breaker`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Circuit breaker reset"
}
```

---

## Health & Status

### Health Check

**Endpoint**: `GET /api/health`

**Response** (200 OK):
```json
{
  "status": "healthy",
  "timestamp": "2026-03-27T11:00:00",
  "services": {
    "database": "connected",
    "gmail": "connected",
    "llm": "operational"
  }
}
```

### Application Statistics

**Endpoint**: `GET /api/stats`

**Response** (200 OK):
```json
{
  "success": true,
  "statistics": {
    "total_emails": 450,
    "unread_emails": 23,
    "total_drafts": 127,
    "total_attachments": 156,
    "database_size_mb": 45.2,
    "last_sync": "2026-03-27T11:00:00",
    "uptime_hours": 168
  }
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "success": false,
  "error": "Invalid request parameters",
  "details": "email_id is required"
}
```

### 401 Unauthorized
```json
{
  "success": false,
  "error": "Unauthorized",
  "message": "Please log in first"
}
```

### 403 Forbidden
```json
{
  "success": false,
  "error": "Forbidden",
  "message": "You don't have permission to access this resource"
}
```

### 404 Not Found
```json
{
  "success": false,
  "error": "Not Found",
  "message": "Resource not found"
}
```

### 429 Too Many Requests
```json
{
  "success": false,
  "error": "Rate Limited",
  "message": "Too many requests. Please try again later."
}
```

### 500 Internal Server Error
```json
{
  "success": false,
  "error": "Internal Server Error",
  "message": "An unexpected error occurred"
}
```

---

## Rate Limiting

- Login endpoint: 5 requests per minute per IP
- Other endpoints: 100 requests per minute per session
- Search endpoints: 20 requests per minute per session

---

## CORS Headers

Responses include CORS headers for cross-origin requests:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, X-Requested-With
```

---

## Pagination

List endpoints support pagination:

**Query Parameters**:
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

**Response**:
```json
{
  "data": [...],
  "page": 1,
  "per_page": 20,
  "total": 450,
  "total_pages": 23
}
```

---

## Timestamps

All timestamps are in ISO 8601 format:
```
2026-03-27T11:00:00
```

---

**API Version**: 2.0
**Last Updated**: March 27, 2026
**Maintained By**: Email Assistant Team
