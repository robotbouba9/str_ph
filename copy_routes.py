#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نسخ المسارات من ملف app.py إلى app_fixed.py
"""

import inspect
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.abspath('.'))

# Import the original app
from app import app as original_app

# Import the fixed app
from app_fixed import app as fixed_app, login_required

# Get all the routes from the original app
original_routes = {}
for rule in original_app.url_map.iter_rules():
    endpoint = rule.endpoint
    if endpoint != 'static' and endpoint not in ['login', 'logout', 'index']:
        view_func = original_app.view_functions[endpoint]
        original_routes[endpoint] = (rule, view_func)

# Copy the routes to the fixed app
for endpoint, (rule, view_func) in original_routes.items():
    # Check if the route already exists in the fixed app
    if endpoint not in fixed_app.view_functions:
        # Get the route path and methods
        path = str(rule)
        methods = list(rule.methods)
        
        # Register the route in the fixed app
        fixed_app.add_url_rule(path, endpoint, view_func, methods=methods)

# Save the updated app to a new file
with open('app_complete.py', 'w', encoding='utf-8') as f:
    f.write('''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
تطبيق Flask لإدارة مخزون محل الهواتف - نسخة كاملة ومصححة
"""

from app_fixed import app

if __name__ == '__main__':
    print("🚀 بدء تشغيل تطبيق الويب (النسخة المصححة الكاملة)...")
    print("🌐 يمكنك الوصول للتطبيق على: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
''')

print("✅ تم نسخ المسارات بنجاح!")