# Example OPA policy file (cms_authz.rego)
# Save this to your OPA server or policy bundle

package cms.authz

import future.keywords.if
import future.keywords.in

# Default deny
default allow := false
default permissions := []

# Allow authenticated users to list entries
allow if {
    input.user.is_authenticated
    input.action == "list"
    input.resource == "entries"
}

# Allow authenticated users to create entries
allow if {
    input.user.is_authenticated
    input.action == "create"
    input.resource == "entry"
}

# Allow users to edit their own entries
allow if {
    input.user.is_authenticated
    input.action == "edit"
    input.resource == "entry"
    input.resource_data.owner_id == input.user.id
}

# Allow users to delete their own entries
allow if {
    input.user.is_authenticated
    input.action == "delete"
    input.resource == "entry"
    input.resource_data.owner_id == input.user.id
}

# Allow users to publish their own entries
allow if {
    input.user.is_authenticated
    input.action == "publish"
    input.resource == "entry"
    input.resource_data.owner_id == input.user.id
}

# Allow everyone to view published entries
allow if {
    input.action == "view"
    input.resource == "published_entries"
}

# Staff users can edit any entry
allow if {
    input.user.is_staff
    input.action in ["edit", "delete", "publish"]
    input.resource == "entry"
}

# Staff users can moderate (additional permission for staff)
allow if {
    input.user.is_staff
    input.action == "moderate"
    input.resource in ["entry", "entries", "published_entries"]
}

# Return user permissions for UI customization
permissions := user_permissions if {
    input.action == "get_permissions"
    input.resource == "user_permissions"
}

user_permissions := ["create", "list", "view_published"] if {
    input.user.is_authenticated
    not input.user.is_staff
}

user_permissions := ["create", "list", "view_published", "moderate", "admin"] if {
    input.user.is_staff
}

user_permissions := ["view_published"] if {
    not input.user.is_authenticated
}
