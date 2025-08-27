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

2. **Setup CMS Groups:**
   ```bash
   # Create the CMS groups (viewer, editor, publisher)
   python manage.py setup_cms_groups
   
   # List existing groups
   python manage.py setup_cms_groups --list
   ```

3. **Create Users with Groups:**
   ```bash
   # Create a viewer (can see all entries but not edit)
   python manage.py create_cms_user_with_group alice password123 --group viewer
   
   # Create an editor (can edit all entries but not publish)
   python manage.py create_cms_user_with_group bob password123 --group editor
   
   # Create a publisher (can publish entries)
   python manage.py create_cms_user_with_group carol password123 --group publisher
   
   # Create a staff user (admin access)
   python manage.py create_cms_user_with_group admin password123 --staff
   
   # Create a regular user (can only manage own entries)
   python manage.py create_cms_user_with_group dave password123
   ```

4. **Configure Django Settings:**
   The following settings are already added to `mysite/settings.py`:
   ```python
   OPA_URL = "http://localhost:8181"
   OPA_POLICY_PATH = "cms/authz"
   OPA_CACHE_TIMEOUT = 300  # 5 minutes
   OPA_TIMEOUT = 5.0  # HTTP timeout in seconds
   ```

5. **Run Migrations (if needed):**
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

#### **Group-Based Permissions:**

| Group | View All Entries | Create | Edit All | Delete All | Publish |
|-------|------------------|---------|----------|------------|---------|
| **Viewer** | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Editor** | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Publisher** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Regular User** | Own only | ✅ | Own only | Own only | Own only |
| **Staff** | ✅ | ✅ | ✅ | ✅ | ✅ |

#### **Default Policies:**
- **Anonymous users:** Can view published entries only
- **Authenticated users:** Can create, list, and manage their own entries
- **Viewer group:** Can see all entries but cannot edit or publish
- **Editor group:** Can view and edit all entries but cannot publish
- **Publisher group:** Can view, edit, and publish all entries
- **Staff users:** Can moderate and manage all entries (admin access)

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
# Test if viewer can see entries but not edit
curl -X POST http://localhost:8181/v1/data/cms/authz \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "user": {
        "id": 1,
        "username": "alice",
        "is_authenticated": true,
        "is_staff": false,
        "groups": ["viewer"]
      },
      "action": "list",
      "resource": "entries"
    }
  }'

# Test if editor can edit any entry
curl -X POST http://localhost:8181/v1/data/cms/authz \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "user": {
        "id": 2,
        "username": "bob",
        "is_authenticated": true,
        "is_staff": false,
        "groups": ["editor"]
      },
      "action": "edit",
      "resource": "entry",
      "resource_data": {
        "entry_id": 1,
        "owner_id": 3
      }
    }
  }'

# Test if publisher can publish any entry
curl -X POST http://localhost:8181/v1/data/cms/authz \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "user": {
        "id": 3,
        "username": "carol",
        "is_authenticated": true,
        "is_staff": false,
        "groups": ["publisher"]
      },
      "action": "publish",
      "resource": "entry",
      "resource_data": {
        "entry_id": 1,
        "owner_id": 4
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
