import httpx
import json
from django.conf import settings
from django.core.cache import cache
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OPAClient:
    def __init__(self):
        self.opa_url = getattr(settings, 'OPA_URL', 'http://localhost:8181')
        self.policy_path = getattr(settings, 'OPA_POLICY_PATH', 'cms/authz')
        self.cache_timeout = getattr(settings, 'OPA_CACHE_TIMEOUT', 300)  # 5 minutes
        self.timeout = getattr(settings, 'OPA_TIMEOUT', 5.0)
    
    def query_policy(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Query OPA for authorization decision"""
        cache_key = f"opa_{hash(json.dumps(input_data, sort_keys=True))}"
        
        # Check cache first
        cached_result = cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"OPA cache hit for key: {cache_key}")
            return cached_result
        
        try:
            url = f"{self.opa_url}/v1/data/{self.policy_path}"
            
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    url, 
                    json={"input": input_data}
                )
                response.raise_for_status()
                
                result = response.json().get('result', {})
                
                # Cache the result
                cache.set(cache_key, result, self.cache_timeout)
                logger.debug(f"OPA policy query successful, cached result for key: {cache_key}")
                
                return result
                
        except httpx.RequestError as e:
            logger.error(f"OPA query failed - network error: {e}")
            return self._fallback_policy()
        except httpx.HTTPStatusError as e:
            logger.error(f"OPA query failed - HTTP {e.response.status_code}: {e}")
            return self._fallback_policy()
        except Exception as e:
            logger.error(f"OPA query failed - unexpected error: {e}")
            return self._fallback_policy()
    
    def _fallback_policy(self) -> Dict[str, Any]:
        """Fallback to restrictive policy when OPA is unavailable"""
        return {"allow": False, "permissions": ["view_published"]}
    
    def check_permission(self, user, action: str, resource: str, resource_data: Optional[Dict[str, Any]] = None) -> bool:
        """Check if user has permission for specific action on resource"""
        input_data = {
            "user": self._serialize_user(user),
            "action": action,
            "resource": resource,
            "resource_data": resource_data or {}
        }
        
        result = self.query_policy(input_data)
        return result.get("allow", False)
    
    def get_user_permissions(self, user) -> list:
        """Get all permissions for a user"""
        input_data = {
            "user": self._serialize_user(user),
            "action": "get_permissions",
            "resource": "user_permissions"
        }
        
        result = self.query_policy(input_data)
        return result.get("permissions", ["view_published"])
    
    def _serialize_user(self, user) -> Dict[str, Any]:
        """Serialize user data for OPA input"""
        if not user or not hasattr(user, 'is_authenticated'):
            return {
                "id": None,
                "username": "anonymous",
                "is_authenticated": False,
                "is_staff": False,
                "groups": [],
            }
        
        return {
            "id": user.id if user.is_authenticated else None,
            "username": user.username
            if user.is_authenticated
            else "anonymous",
            "is_authenticated": user.is_authenticated,
            "is_staff": user.is_staff if user.is_authenticated else False,
            "groups": self._get_user_groups(user)
            if user.is_authenticated
            else [],
        }

    def _get_user_groups(self, user) -> list:
        """Get user Django groups"""
        try:
            if hasattr(user, "groups") and user.groups.exists():
                return [group.name.lower() for group in user.groups.all()]
        except Exception as e:
            logger.debug(f"Could not get user groups: {e}")
        return []

# Global OPA client instance
opa_client = OPAClient()
