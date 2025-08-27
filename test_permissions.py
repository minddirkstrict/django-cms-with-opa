#!/usr/bin/env python3
"""
Quick test script to verify OPA permissions are working correctly
"""

import os
import sys
import django
from cms.opa_client import query_policy

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()


def test_permissions():
    """Test the permission system with different user types"""
    
    print("🧪 Testing CMS Permissions\n")
    
    # Test data
    test_cases = [
        {
            'name': 'User without groups',
            'groups': [],
            'actions': ['list', 'view', 'create', 'edit', 'delete', 'publish']
        },
        {
            'name': 'Viewer',
            'groups': ['viewer'],
            'actions': ['list', 'view', 'create', 'edit', 'delete', 'publish']
        },
        {
            'name': 'Editor', 
            'groups': ['editor'],
            'actions': ['list', 'view', 'create', 'edit', 'delete', 'publish']
        },
        {
            'name': 'Publisher',
            'groups': ['publisher'], 
            'actions': ['list', 'view', 'create', 'edit', 'delete', 'publish']
        }
    ]
    
    for test_case in test_cases:
        print(f"👤 {test_case['name']}:")
        
        # Create mock user data
        user_data = {
            'id': 1,
            'username': 'testuser',
            'is_authenticated': True,
            'is_staff': False,
            'groups': test_case['groups']
        }
        
        for action in test_case['actions']:
            resource = "entry" if action in ['view', 'create', 'edit', 'delete', 'publish'] else "entries"
            
            input_data = {
                'user': user_data,
                'action': action,
                'resource': resource,
                'resource_data': {'owner_id': 1}
            }
            
            try:
                result = query_policy(input_data)
                allowed = result.get('allow', False)
                status = "✅" if allowed else "❌"
                print(f"  {status} {action}")
            except Exception as e:
                print(f"  ❌ {action} (Error: {e})")
        
        print()

if __name__ == '__main__':
    try:
        test_permissions()
    except Exception as e:
        print(f"Error running tests: {e}")
        sys.exit(1)
