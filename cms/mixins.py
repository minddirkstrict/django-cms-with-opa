from django.core.exceptions import PermissionDenied
from .opa_client import opa_client
import logging

logger = logging.getLogger(__name__)

class OPAPermissionMixin:
    """Mixin to check OPA permissions for views"""
    required_permission = None
    resource_type = None
    
    def dispatch(self, request, *args, **kwargs):
        if not self.check_opa_permission(request):
            logger.warning(
                f"OPA permission denied for user {request.user.username if request.user.is_authenticated else 'anonymous'} "
                f"on {self.required_permission}:{self.resource_type}"
            )
            raise PermissionDenied("Access denied by policy")
        return super().dispatch(request, *args, **kwargs)
    
    def check_opa_permission(self, request):
        if not self.required_permission or not self.resource_type:
            return True  # No permission check required
        
        resource_data = self.get_resource_data(request)
        
        return opa_client.check_permission(
            user=request.user,
            action=self.required_permission,
            resource=self.resource_type,
            resource_data=resource_data
        )
    
    def get_resource_data(self, request):
        """Override in subclasses to provide resource-specific data"""
        return {}

class OPAEntryPermissionMixin(OPAPermissionMixin):
    """Mixin for entry-specific permission checks"""
    
    def get_resource_data(self, request):
        # For entry views, include entry data if available
        if hasattr(self, 'get_object'):
            try:
                entry = self.get_object()
                return {
                    "entry_id": entry.id,
                    "owner_id": entry.owner.id,
                    "is_published": entry.is_published(),
                    "created_at": entry.created_at.isoformat(),
                }
            except Exception as e:
                logger.debug(f"Could not get entry resource data: {e}")
                pass
        return {}
