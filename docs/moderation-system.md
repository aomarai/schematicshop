# User Moderation System

This document describes the user moderation system implemented in SchematicShop.

## Overview

The moderation system provides comprehensive tools for managing user behavior and maintaining platform security. It includes warnings, temporary and permanent bans, account disabling, and a complete audit trail of all moderation actions.

## Features

### 1. Warnings
Moderators can issue warnings to users for inappropriate behavior or violations of community guidelines.

- **Model**: `Warning`
- **Fields**:
  - `user`: The user receiving the warning
  - `issued_by`: The moderator who issued the warning
  - `reason`: Explanation for the warning
  - `is_acknowledged`: Whether the user has acknowledged the warning
  - `created_at`: Timestamp of when the warning was issued

### 2. Bans
Support for both temporary (timeout) and permanent bans.

- **Model**: `Ban`
- **Types**:
  - **Temporary Ban**: Expires after a specified time period
  - **Permanent Ban**: Never expires, completely deactivates the account
- **Fields**:
  - `user`: The user being banned
  - `issued_by`: The moderator who issued the ban
  - `ban_type`: 'temporary' or 'permanent'
  - `reason`: Explanation for the ban
  - `expires_at`: When the ban expires (only for temporary bans)
  - `is_active`: Whether the ban is currently active

**Behavior**:
- Permanent bans set `user.is_active = False`
- Temporary bans set `user.ban_expires_at` to the expiration time
- When a ban is created, it automatically updates the user's status
- Bans can be revoked through the API

### 3. Account Disabling
Soft deactivation that retains user data for review.

- Disables the user account (`is_active = False`)
- Retains all user data, schematics, and history
- Can be re-enabled by moderators
- Different from permanent bans (which are logged separately)

### 4. Moderation Audit Log
Complete audit trail of all moderation actions.

- **Model**: `ModerationAction`
- **Action Types**:
  - `warning`: Warning issued
  - `ban`: Ban issued
  - `unban`: Ban removed
  - `disable`: Account disabled
  - `enable`: Account enabled
- **Fields**:
  - `user`: The user affected
  - `moderator`: The moderator who took the action
  - `action_type`: Type of action taken
  - `reason`: Explanation for the action
  - `details`: Additional JSON data (e.g., ban duration)
  - `ip_address`: IP address of the moderator
  - `created_at`: Timestamp

### 5. Ban Check Middleware
Middleware that automatically blocks banned users from accessing the API.

- **Middleware**: `BanCheckMiddleware`
- **Behavior**:
  - Checks if authenticated users are banned before allowing API access
  - Allows access to authentication endpoints so users can check their status
  - Returns HTTP 403 with ban details if user is banned
  - Checks both permanent bans (`is_active = False`) and temporary bans (`ban_expires_at`)

## API Endpoints

### Warnings

**List Warnings**
```
GET /api/auth/warnings/
```
- Moderators: See all warnings
- Regular users: See only their own warnings

**Create Warning**
```
POST /api/auth/warnings/
```
**Permissions**: Staff only
**Body**:
```json
{
  "user": 123,
  "reason": "Inappropriate behavior in comments"
}
```

**Get Warning Details**
```
GET /api/auth/warnings/{id}/
```

**Update Warning**
```
PUT/PATCH /api/auth/warnings/{id}/
```

**Delete Warning**
```
DELETE /api/auth/warnings/{id}/
```

### Bans

**List Bans**
```
GET /api/auth/bans/
```
**Permissions**: Staff only

**Create Permanent Ban**
```
POST /api/auth/bans/
```
**Permissions**: Staff only
**Body**:
```json
{
  "user": 123,
  "ban_type": "permanent",
  "reason": "Repeated violations of community guidelines"
}
```

**Create Temporary Ban**
```
POST /api/auth/bans/
```
**Permissions**: Staff only
**Body**:
```json
{
  "user": 123,
  "ban_type": "temporary",
  "reason": "Minor policy violation",
  "expires_at": "2026-01-23T12:00:00Z"
}
```

**Revoke Ban**
```
POST /api/auth/bans/{id}/revoke/
```
**Permissions**: Staff only

**Get Ban Details**
```
GET /api/auth/bans/{id}/
```

### Account Disable/Enable

**Disable Account**
```
POST /api/auth/users/{username}/disable/
```
**Permissions**: Staff only
**Body**:
```json
{
  "reason": "Account under investigation"
}
```

**Enable Account**
```
POST /api/auth/users/{username}/enable/
```
**Permissions**: Staff only
**Body**:
```json
{
  "reason": "Investigation complete"
}
```

### Moderation Audit Log

**List Moderation Actions**
```
GET /api/auth/moderation-actions/
```
**Permissions**: Staff only

**Get Moderation Action Details**
```
GET /api/auth/moderation-actions/{id}/
```
**Permissions**: Staff only

## User Model Additions

The `User` model has been extended with moderation-related fields:

```python
class User(AbstractUser):
    # ... existing fields ...
    
    # Moderation fields
    ban_expires_at = models.DateTimeField(null=True, blank=True)
    ban_reason = models.TextField(blank=True)
    
    @property
    def is_banned(self):
        """Check if user is currently banned"""
        if not self.is_active:
            return True
        if self.ban_expires_at and self.ban_expires_at > timezone.now():
            return True
        return False
    
    def unban(self):
        """Unban the user by clearing ban-related fields"""
        self.is_active = True
        self.ban_expires_at = None
        self.ban_reason = ''
        self.save()
```

## Permissions

Two custom permission classes are provided:

1. **IsModerator**: Requires user to be staff (`is_staff = True`)
2. **IsModeratorOrReadOnly**: Allows moderators full access, others read-only

## Django Admin Integration

The Django admin interface has been enhanced with:

- **User Admin**: Shows ban status with color-coded indicators
- **Warning Admin**: Browse and manage all warnings
- **Ban Admin**: Browse and manage all bans
- **Moderation Action Admin**: Browse the complete audit log

All admin interfaces include:
- Clickable links between related users and moderators
- Search functionality
- Filtering by date, type, and status
- Read-only fields for timestamps and audit data

## Usage Examples

### Issuing a Warning (via API)

```python
import requests

response = requests.post(
    'https://api.example.com/api/auth/warnings/',
    headers={'Authorization': 'Bearer <token>'},
    json={
        'user': 123,
        'reason': 'Posting spam content'
    }
)
```

### Creating a Temporary Ban (via API)

```python
from datetime import datetime, timedelta

expires_at = (datetime.now() + timedelta(days=7)).isoformat()

response = requests.post(
    'https://api.example.com/api/auth/bans/',
    headers={'Authorization': 'Bearer <token>'},
    json={
        'user': 123,
        'ban_type': 'temporary',
        'reason': 'Multiple warnings ignored',
        'expires_at': expires_at
    }
)
```

### Checking if a User is Banned (in code)

```python
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='example')

if user.is_banned:
    print(f"User is banned. Reason: {user.ban_reason}")
    if user.ban_expires_at:
        print(f"Ban expires at: {user.ban_expires_at}")
    else:
        print("This is a permanent ban.")
```

### Viewing Moderation History (in code)

```python
from apps.users.models import ModerationAction

# Get all actions for a specific user
actions = ModerationAction.objects.filter(user__username='example')

for action in actions:
    print(f"{action.created_at}: {action.action_type} by {action.moderator}")
    print(f"  Reason: {action.reason}")
```

## Security Considerations

1. **Permissions**: All moderation endpoints require staff permissions
2. **Audit Trail**: All moderation actions are logged with timestamp, moderator, and IP address
3. **Middleware Protection**: Banned users are automatically blocked from API access
4. **Data Retention**: Disabled accounts retain all data for potential review
5. **Self-Moderation Prevention**: Moderators cannot ban, warn, or disable themselves
6. **Staff Protection**: Only superusers can ban or disable other staff members
7. **Immutable Records**: Warnings and bans are read-only after creation to maintain audit integrity
8. **Proxy-Aware IP Logging**: IP addresses are captured correctly behind proxies using X-Forwarded-For
9. **Transaction Safety**: All moderation actions use atomic transactions to prevent inconsistent states
10. **Performance Optimization**: Database index on ban_expires_at for efficient ban status checks

## Future Enhancements

The current implementation provides a solid foundation for:

- IP blocking or rate-limiting for abusive behavior
- Automatic flagging/reporting system for user actions or content
- More granular permission levels (e.g., separate moderator roles)
- Appeal process for moderation actions
- Notification system for users receiving warnings or bans
- Escalation workflows (e.g., automatic ban after X warnings)
- Time-based moderation reports and analytics

## Testing

Comprehensive test coverage includes:

- Model tests for User, Warning, Ban, and ModerationAction
- API tests for all moderation endpoints
- Permission tests for moderator-only actions
- Middleware tests for ban checking
- Integration tests for the complete moderation workflow

Run tests with:
```bash
pytest apps/users/tests.py -v
```
