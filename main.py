import src.server as server
import os

if __name__ == '__main__':
    # Set admin token if not already set
    if not os.getenv('ADMIN_TOKEN'):
        # For production, require ADMIN_TOKEN to be set via environment
        # For development, generate a secure token for this session
        import secrets
        admin_token = f"tvapi-{secrets.token_urlsafe(32)}"
        os.environ['ADMIN_TOKEN'] = admin_token
        print("🔐 ADMIN_TOKEN generado y configurado.")
        print("   ⚠️  Token disponible solo en variables de entorno por seguridad")
    else:
        print("✅ Admin panel secured with configured token")
    
    server.start_server()