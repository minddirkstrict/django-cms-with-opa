# CMS Authorization Policy with Django Groups Support
# Groups: viewer, editor, publisher

package cms.authz

import future.keywords.if
import future.keywords.in

# Default deny
default allow := false
default permissions := []

# Helper functions for group checking
has_group(user, group_name) if {
    group_name in user.groups
}

is_owner(user, resource_data) if {
    resource_data.owner_id == user.id
}

# ============= VIEWER GROUP PERMISSIONS =============
# Viewers can see all entries (published and unpublished) but cannot edit or publish

# Allow viewers to list all entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "viewer")
    input.action == "list"
    input.resource == "entries"
}

# Allow viewers to view individual entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "viewer")
    input.action == "view"
    input.resource == "entry"
}

# ============= EDITOR GROUP PERMISSIONS =============
# Editors can view all entries, create, edit, and delete them (but NOT publish)

# Allow editors to list entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "editor")
    input.action == "list"
    input.resource == "entries"
}

# Allow editors to view individual entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "editor")
    input.action == "view"
    input.resource == "entry"
}

# Allow editors to create entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "editor")
    input.action == "create"
    input.resource == "entry"
}

# Allow editors to edit any entry
allow if {
    input.user.is_authenticated
    has_group(input.user, "editor")
    input.action == "edit"
    input.resource == "entry"
}

# Allow editors to delete any entry
allow if {
    input.user.is_authenticated
    has_group(input.user, "editor")
    input.action == "delete"
    input.resource == "entry"
}

# ============= PUBLISHER GROUP PERMISSIONS =============
# Publishers can ONLY publish/unpublish entries (inherit all editor permissions)

# Allow publishers to list entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
    input.action == "list"
    input.resource == "entries"
}

# Allow publishers to view individual entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
    input.action == "view"
    input.resource == "entry"
}

# ONLY publishers can publish/unpublish any entry
allow if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
    input.action == "publish"
    input.resource == "entry"
}

# ============= PUBLIC ACCESS =============
# Allow everyone to view published entries
allow if {
    input.action == "view"
    input.resource == "published_entries"
}

# ============= STAFF OVERRIDE =============
# Staff users can do everything (Django admin access)
allow if {
    input.user.is_staff
    input.action in ["list", "create", "edit", "delete", "publish", "moderate"]
    input.resource in ["entry", "entries", "published_entries"]
}

# ============= PERMISSIONS FOR UI =============
# Return user permissions for template customization
permissions := user_permissions if {
    input.action == "get_permissions"
    input.resource == "user_permissions"
}

# Viewer permissions
user_permissions := ["view_all", "list"] if {
    input.user.is_authenticated
    has_group(input.user, "viewer")
    not has_group(input.user, "editor")
    not has_group(input.user, "publisher")
}

# Editor permissions (includes viewer permissions)
user_permissions := ["view_all", "list", "create", "edit_all", "delete_all"] if {
    input.user.is_authenticated
    has_group(input.user, "editor")
    not has_group(input.user, "publisher")
}

# Publisher permissions (includes all editor permissions)
user_permissions := ["view_all", "list", "publish_all"] if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
}

# Staff permissions (everything)
user_permissions := ["view_all", "list", "create", "edit_all", "delete_all", "publish_all", "moderate", "admin"] if {
    input.user.is_staff
}

# Anonymous user permissions
user_permissions := ["view_published"] if {
    not input.user.is_authenticated
}
