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

# ============= EDITOR GROUP PERMISSIONS =============
# Editors can view all entries and edit them

# Allow editors to list entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "editor")
    input.action == "list"
    input.resource == "entries"
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
# Publishers can publish and unpublish entries (includes all editor permissions)

# Allow publishers to list entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
    input.action == "list"
    input.resource == "entries"
}

# Allow publishers to create entries
allow if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
    input.action == "create"
    input.resource == "entry"
}

# Allow publishers to edit any entry
allow if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
    input.action == "edit"
    input.resource == "entry"
}

# Allow publishers to delete any entry
allow if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
    input.action == "delete"
    input.resource == "entry"
}

# Allow publishers to publish/unpublish any entry
allow if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
    input.action == "publish"
    input.resource == "entry"
}

# ============= BASIC USER PERMISSIONS =============
# Authenticated users without specific groups can manage their own entries

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

# Allow users to edit their own entries (if not in viewer group)
allow if {
    input.user.is_authenticated
    not has_group(input.user, "viewer")
    input.action == "edit"
    input.resource == "entry"
    is_owner(input.user, input.resource_data)
}

# Allow users to delete their own entries (if not in viewer group)
allow if {
    input.user.is_authenticated
    not has_group(input.user, "viewer")
    input.action == "delete"
    input.resource == "entry"
    is_owner(input.user, input.resource_data)
}

# Allow users to publish their own entries (if not in viewer group)
allow if {
    input.user.is_authenticated
    not has_group(input.user, "viewer")
    input.action == "publish"
    input.resource == "entry"
    is_owner(input.user, input.resource_data)
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
user_permissions := ["view_all", "list", "create", "edit_all", "delete_all", "publish_all"] if {
    input.user.is_authenticated
    has_group(input.user, "publisher")
}

# Basic authenticated user permissions (own entries only)
user_permissions := ["list", "create", "edit_own", "delete_own", "publish_own"] if {
    input.user.is_authenticated
    not has_group(input.user, "viewer")
    not has_group(input.user, "editor") 
    not has_group(input.user, "publisher")
    not input.user.is_staff
}

# Staff permissions (everything)
user_permissions := ["view_all", "list", "create", "edit_all", "delete_all", "publish_all", "moderate", "admin"] if {
    input.user.is_staff
}

# Anonymous user permissions
user_permissions := ["view_published"] if {
    not input.user.is_authenticated
}
