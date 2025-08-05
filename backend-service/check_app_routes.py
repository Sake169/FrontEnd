from app.main import app

print('Available routes:')
for route in app.routes:
    methods = getattr(route, 'methods', 'N/A')
    print(f'  {route.path} - {methods}')

print('\nAuth router routes:')
from app.api import auth
for route in auth.router.routes:
    methods = getattr(route, 'methods', 'N/A')
    print(f'  {route.path} - {methods}')