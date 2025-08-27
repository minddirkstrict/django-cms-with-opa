# OPA Integration Setup Guide

## 🔐 Open Policy Agent (OPA) Integration

This CMS now includes Open Policy Agent integration for centralized, policy-driven authorization.

### 📋 Prerequisites

1. **Install httpx dependency:**
   ```bash
   pip install httpx>=0.25.0
   # or with uv:
   uv add httpx
   ```

2. **Install and run OPA:**
   ```bash
   # Using Docker (recommended)
   docker run -p 8181:8181 openpolicyagent/opa:latest run --server
   
   # Or install OPA binary from https://www.openpolicyagent.org/docs/latest/get-started/
   ```

### 🔧 Setup Steps

1. **Load the OPA Policy:**
   ```bash
   # Upload the policy file to OPA
   curl -X PUT \
     --data-binary @cms_authz.rego \
     http://localhost:8181/v1/policies/cms_authz
   ```

2. **Configure Django Settings:**
   The following settings are already added to `mysite/settings.py`:
   ```python
   OPA_URL = "http://localhost:8181"
   OPA_POLICY_PATH = "cms/authz"
   OPA_CACHE_TIMEOUT = 300  # 5 minutes
   OPA_TIMEOUT = 5.0  # HTTP timeout in seconds
   ```

3. **Run Migrations (if needed):**
   ```bash
   python manage.py migrate
   ```

### 🚀 Features

#### **Policy-Driven Authorization:**
- ✅ Centralized permission management
- ✅ Dynamic policy updates without code changes
- ✅ Fine-grained access control
- ✅ Caching for performance
- ✅ Fallback policies when OPA is unavailable

#### **Default Policies:**
- **Anonymous users:** Can view published entries only
- **Authenticated users:** Can create, list, and manage their own entries
- **Staff users:** Can moderate and manage all entries

#### **Permission Types:**
- `list` - View entry list
- `create` - Create new entries
- `edit` - Modify entries (own entries for users, all for staff)
- `delete` - Delete entries (own entries for users, all for staff)
- `publish` - Publish entries (own entries for users, all for staff)
- `view` - View published entries (everyone)
- `moderate` - Staff-only moderation actions

### 🔍 Testing OPA Policies

You can test policies directly against OPA:

```bash
# Test if user can edit entry
curl -X POST http://localhost:8181/v1/data/cms/authz \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "user": {
        "id": 1,
        "username": "alice",
        "is_authenticated": true,
        "is_staff": false
      },
      "action": "edit",
      "resource": "entry",
      "resource_data": {
        "entry_id": 1,
        "owner_id": 1,
        "is_published": false
      }
    }
  }'
```

### 📊 Monitoring & Debugging

Enable debug logging in Django settings to monitor OPA interactions:

```python
LOGGING = {
    'loggers': {
        'cms.opa_client': {
            'level': 'DEBUG',
        },
        'cms.mixins': {
            'level': 'DEBUG',
        },
    },
}
```

### 🔄 Fallback Behavior

When OPA is unavailable:
- All actions are denied by default
- Only "view_published" permission is granted
- Error is logged for monitoring
- System remains functional with restrictive access

### 🎯 Advanced Usage

#### **Custom Policies:**
Modify `cms_authz.rego` to implement:
- Time-based access (e.g., embargo periods)
- Role-based permissions
- Content-based restrictions
- Approval workflows

#### **Policy Testing:**
```bash
# Get user permissions
curl -X POST http://localhost:8181/v1/data/cms/authz \
  -d '{"input": {"user": {"id": 1, "is_authenticated": true}, "action": "get_permissions", "resource": "user_permissions"}}'
```

#### **Performance Tuning:**
- Adjust `OPA_CACHE_TIMEOUT` for your needs
- Monitor cache hit rates
- Use OPA bundles for policy distribution in production

### 🔒 Security Notes

- OPA policies are cached for performance
- All policy decisions are logged
- Fallback denies access when OPA is unavailable
- Resource-specific data is included in policy decisions
- User context includes authentication and staff status

This integration provides enterprise-grade authorization that can evolve with your needs while keeping authorization logic separate from application code!
