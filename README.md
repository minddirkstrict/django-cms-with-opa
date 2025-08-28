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
   
   # Create a publisher (can ONLY publish entries)
   python manage.py create_cms_user_with_group carol password123 --group publisher
   
   # Create a staff user (admin access)
   python manage.py create_cms_user_with_group admin password123 --staff
   
   # Create a regular user (no group-based permissions)
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

| Group | View Published | View All | List All | Create | Edit All | Delete All | Publish/Unpublish |
|-------|----------------|----------|----------|--------|----------|------------|-------------------|
| **Anonymous** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Authenticated (no group)** | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **Viewer** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| **Editor** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **Publisher** | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | ✅ |
| **Staff** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

#### **Permission Model Overview:**

**🔍 Viewer Group:**
- **Read-only access** to all entries (published and unpublished)
- Can list and view individual entries
- **Cannot** create, edit, delete, or publish

**✏️ Editor Group:**
- **Full editing access** to all entries
- Can create new entries, edit and delete any entry
- **Cannot** publish or unpublish entries (content creation only)

**📢 Publisher Group:**
- **Publication control only**
- Can list and view all entries
- **Cannot** create, edit, or delete entries
- **Can only** publish and unpublish entries

**👤 Staff Users:**
- **Full administrative access**
- Can perform all actions: create, edit, delete, publish, moderate
- Override all group restrictions

**🌐 Public Access:**
- **Anonymous users** can only view published entries
- No other permissions without authentication

#### **Action Types:**
- `view` - View individual entries (published entries for public)
- `list` - List all entries (requires viewer+ group)
- `create` - Create new entries (editors only)
- `edit` - Modify entries (editors only)
- `delete` - Delete entries (editors only)
- `publish` - Publish entries (publishers only)
- `unpublish` - Unpublish entries (publishers only)
- `moderate` - Staff-only moderation actions

#### **Resource Types:**
- `entry` - Individual entry operations
- `entries` - Bulk entry operations (listing)
- `published_entries` - Public view of published content

### 🔍 Testing OPA Policies

You can test policies directly against OPA:

```bash
# Test anonymous user viewing published entries
curl -X POST http://localhost:8181/v1/data/cms/authz \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "user": {
        "id": null,
        "username": null,
        "is_authenticated": false,
        "is_staff": false,
        "groups": []
      },
      "action": "view",
      "resource": "published_entries"
    }
  }'

# Test viewer can see all entries but not edit
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

# Test editor can edit any entry but not publish
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

# Test publisher can publish any entry
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

# Test publisher cannot edit entries
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
      "action": "edit",
      "resource": "entry",
      "resource_data": {
        "entry_id": 1,
        "owner_id": 4
      }
    }
  }'

# Get user permissions for UI customization
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
      "action": "get_permissions",
      "resource": "user_permissions"
    }
  }'
```

### 📊 Monitoring & Debugging

Enable debug logging in Django settings to monitor OPA interactions:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'cms.opa_client': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'cms.mixins': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

### 🔄 Fallback Behavior

When OPA is unavailable:
- System denies all actions by default for security
- Only published content viewing remains available
- All policy decisions are logged for monitoring
- System remains functional with minimal access

### 🎯 Workflow Design

This permission model supports a **separation of concerns** workflow:

1. **Content Creation Phase** (Editors):
   - Editors create and refine content
   - They can edit and delete any entry
   - Cannot publish content (ensures review process)

2. **Publication Phase** (Publishers):
   - Publishers review and approve content for publication
   - They can publish/unpublish any entry
   - Cannot modify content (ensures editorial integrity)

3. **Review Phase** (Viewers):
   - Viewers can see all content for review purposes
   - Read-only access prevents accidental modifications
   - Can provide feedback through other channels

4. **Administration** (Staff):
   - Full access for system administration
   - Can override all restrictions when needed

### 🔧 Advanced Usage

#### **Custom Policies:**
Modify `cms_authz.rego` to implement:
- Time-based access (e.g., embargo periods)
- Content category-based restrictions
- Multi-stage approval workflows
- Resource-specific permissions

#### **UI Permission Tokens:**
The policy returns specific permission sets for UI customization:
- `view_published` - Anonymous users
- `["view_all", "list"]` - Viewers
- `["view_all", "list", "create", "edit_all", "delete_all"]` - Editors
- `["view_all", "list", "publish_all"]` - Publishers
- `["view_all", "list", "create", "edit_all", "delete_all", "publish_all", "moderate", "admin"]` - Staff

#### **Performance Tuning:**
- Adjust `OPA_CACHE_TIMEOUT` based on policy change frequency
- Monitor cache hit rates in Django logs
- Use OPA bundles for policy distribution in production
- Consider OPA clustering for high availability

### 🔒 Security Notes

- **Default deny policy** - All actions denied unless explicitly allowed
- **Group-based access control** with clear separation of duties
- **Staff override** for administrative access
- **Public access** limited to published content only
- **Resource ownership** validation where applicable
- **Comprehensive logging** of all policy decisions
- **Graceful degradation** when OPA is unavailable

### 🔧 Troubleshooting

**Common Issues:**

1. **OPA not responding:**
   ```bash
   # Check OPA health
   curl http://localhost:8181/health
   ```

2. **Policy not loaded:**
   ```bash
   # List all policies
   curl http://localhost:8181/v1/policies
   
   # View specific policy
   curl http://localhost:8181/v1/policies/cms_authz
   ```

3. **Unexpected permission denials:**
   - Verify user groups: `python manage.py setup_cms_groups --list`
   - Test policy directly with curl commands above
   - Enable debug logging to trace decision flow
   - Check user authentication status

4. **Publisher cannot edit content:**
   - This is by design - publishers only control publication
   - Use editor group for content creation/modification
   - Staff users have full access if admin override needed

This authorization model provides **enterprise-grade security** with clear separation of duties, making it ideal for content management workflows that require editorial oversight
