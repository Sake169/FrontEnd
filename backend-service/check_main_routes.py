from app.main import app

print('App created successfully')
print('Routes:')
for route in app.routes:
    methods = getattr(route, 'methods', 'N/A')
    print(f'  {route.path} - {methods}')

print('\nAuth routes specifically:')
for route in app.routes:
    if hasattr(route, 'path') and 'auth' in route.path:
        methods = getattr(route, 'methods', 'N/A')
        print(f'  {route.path} - {methods}')