import src.server as server
import os

if __name__ == '__main__':
    # Set admin token if not already set
    if not os.getenv('ADMIN_TOKEN'):
        # Generate a secure token for this session
        import secrets
        admin_token = f"tvapi-{secrets.token_urlsafe(32)}"
        os.environ['ADMIN_TOKEN'] = admin_token
        print("🔐 Admin token generado para esta sesión:")
        print(f"   {admin_token}")
        print("   Usa este token para acceder al panel de administración")
    else:
        print("✅ Admin panel secured with configured token")
    
    server.start_server()