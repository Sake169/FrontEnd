from app.main import app

print('Main app loaded successfully')
print('All routes:')
for route in app.routes:
    if hasattr(route, 'path'):
        print(f'  {route.path} - {getattr(route, "methods", "N/A")}')