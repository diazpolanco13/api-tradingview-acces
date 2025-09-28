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
        print("🔐 Admin token generado para esta sesión:")
        
        # Solo mostrar el token completo en desarrollo (no en producción/Docker)
        if os.getenv('ENV') == 'production':
            print("   Token: [HIDDEN - available in environment variables]")
            print("   ⚠️  Para seguridad en producción, el token no se muestra en logs")
        else:
            print(f"   {admin_token}")
            print("   ⚠️  Token completo mostrado arriba")
            print("   Para producción, configure ADMIN_TOKEN en variables de entorno")
    else:
        print("✅ Admin panel secured with configured token")
    
    server.start_server()