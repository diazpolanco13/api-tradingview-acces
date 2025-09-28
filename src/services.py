"""
Business logic services for PineScript Control Access
"""
from typing import Dict, List, Any, Optional
from .models import Indicador, Cliente, Acceso
from .tradingview import tradingview

class IndicadorService:
    """Service for managing indicators"""
    
    @staticmethod
    def create_indicator(nombre: str, pub_id: str, version: str = "1.0", descripcion: str = "") -> int:
        """Create a new indicator"""
        return Indicador.create(
            nombre=nombre,
            pub_id=pub_id,
            version=version,
            descripcion=descripcion
        )
    
    @staticmethod
    def get_all_indicators() -> List[Dict[str, Any]]:
        """Get all indicators"""
        return Indicador.get_all()
    
    @staticmethod
    def get_active_indicators() -> List[Dict[str, Any]]:
        """Get only active indicators"""
        return Indicador.get_active()
    
    @staticmethod
    def search_indicators(term: str) -> List[Dict[str, Any]]:
        """Search indicators by name or description"""
        return Indicador.search(term)
    
    @staticmethod
    def update_indicator(indicator_id: int, **kwargs) -> bool:
        """Update an indicator"""
        return Indicador.update(indicator_id, **kwargs)
    
    @staticmethod
    def delete_indicator(indicator_id: int) -> bool:
        """Delete an indicator (soft delete by setting estado to 'inactivo')"""
        return Indicador.update(indicator_id, estado='inactivo')
    
    @staticmethod
    def get_indicator_stats(indicator_id: int) -> Dict[str, Any]:
        """Get statistics for a specific indicator"""
        indicator = Indicador.get_by_id(indicator_id)
        if not indicator:
            return {}
        
        accesses = Acceso.get_indicator_accesses(indicator_id)
        active_accesses = [a for a in accesses if a['estado'] == 'activo']
        
        return {
            'indicator': indicator,
            'total_accesses': len(accesses),
            'active_accesses': len(active_accesses),
            'expired_accesses': len([a for a in accesses if a['estado'] == 'expirado']),
            'revoked_accesses': len([a for a in accesses if a['estado'] == 'revocado']),
            'recent_accesses': accesses[:10]  # Last 10
        }

class ClienteService:
    """Service for managing clients"""
    
    @staticmethod
    def create_client(username_tradingview: str, email: str = "", nombre_completo: str = "") -> Dict[str, Any]:
        """Create a new client with TradingView validation"""
        result = {'success': False, 'message': '', 'client_id': None}
        
        # Check if client already exists
        existing = Cliente.get_by_username(username_tradingview)
        if existing:
            result['message'] = 'Cliente ya existe con ese username de TradingView'
            return result
        
        # Validate username with TradingView API
        try:
            tv = tradingview()
            validation = tv.validate_username(username_tradingview)
            
            if not validation.get('validuser', False):
                result['message'] = 'Username no válido en TradingView'
                return result
                
        except Exception as e:
            result['message'] = f'Error validating username: {str(e)}'
            return result
        
        # Create client
        try:
            client_id = Cliente.create(
                username_tradingview=username_tradingview,
                email=email,
                nombre_completo=nombre_completo
            )
            
            result['success'] = True
            result['client_id'] = client_id
            result['message'] = 'Cliente creado exitosamente'
            
        except Exception as e:
            result['message'] = f'Error creating client: {str(e)}'
        
        return result
    
    @staticmethod
    def get_all_clients() -> List[Dict[str, Any]]:
        """Get all clients with access count"""
        return Cliente.get_with_access_count()
    
    @staticmethod
    def get_active_clients() -> List[Dict[str, Any]]:
        """Get only active clients"""
        return Cliente.get_active()
    
    @staticmethod
    def search_clients(term: str) -> List[Dict[str, Any]]:
        """Search clients"""
        return Cliente.search(term)
    
    @staticmethod
    def get_client_profile(client_id: int) -> Dict[str, Any]:
        """Get complete client profile with access history"""
        client = Cliente.get_by_id(client_id)
        if not client:
            return {}
        
        accesses = Acceso.get_client_accesses(client_id)
        active_accesses = [a for a in accesses if a['estado'] == 'activo']
        
        return {
            'client': client,
            'accesses': accesses,
            'active_accesses': active_accesses,
            'total_accesses': len(accesses),
            'indicators_count': len(set(a['indicador_id'] for a in active_accesses))
        }
    
    @staticmethod
    def update_client(client_id: int, **kwargs) -> bool:
        """Update a client"""
        return Cliente.update(client_id, **kwargs)
    
    @staticmethod
    def deactivate_client(client_id: int) -> bool:
        """Deactivate a client (soft delete)"""
        return Cliente.update(client_id, estado='inactivo')

class AccesoService:
    """Service for managing access permissions"""
    
    @staticmethod
    def grant_access(username_tradingview: str, pub_id: str, days: int) -> Dict[str, Any]:
        """Grant access to a client for a specific indicator"""
        result = {'success': False, 'message': '', 'access_id': None}
        
        try:
            # Get or create client
            client = Cliente.get_by_username(username_tradingview)
            if not client:
                # Try to create client automatically
                client_result = ClienteService.create_client(username_tradingview)
                if not client_result['success']:
                    result['message'] = f"Cliente no encontrado y no se pudo crear: {client_result['message']}"
                    return result
                client = Cliente.get_by_id(client_result['client_id'])
            
            # Get indicator
            indicator = Indicador.get_by_pub_id(pub_id)
            if not indicator:
                result['message'] = f"Indicador no encontrado con PUB ID: {pub_id}"
                return result
            
            # Grant access
            access_id = Acceso.grant_access(
                cliente_id=client['id'],
                indicador_id=indicator['id'],
                days=days
            )
            
            # Sync with TradingView API
            try:
                tv = tradingview()
                tv_access = tv.get_access_details(username_tradingview, pub_id)
                
                if days == 30:
                    tv.add_access(tv_access, 'M', 1)  # 1 month
                else:
                    tv.add_access(tv_access, 'd', days)
                    
            except Exception as tv_error:
                result['message'] = f"Acceso creado en DB pero error en TradingView: {str(tv_error)}"
                return result
            
            result['success'] = True
            result['access_id'] = access_id
            result['message'] = f"Acceso otorgado por {days} días"
            
        except Exception as e:
            result['message'] = f"Error granting access: {str(e)}"
        
        return result
    
    @staticmethod
    def revoke_access(username_tradingview: str, pub_id: str) -> Dict[str, Any]:
        """Revoke access for a client to specific indicator"""
        result = {'success': False, 'message': ''}
        
        try:
            # Get client and indicator
            client = Cliente.get_by_username(username_tradingview)
            indicator = Indicador.get_by_pub_id(pub_id)
            
            if not client:
                result['message'] = "Cliente no encontrado"
                return result
                
            if not indicator:
                result['message'] = "Indicador no encontrado"
                return result
            
            # Revoke in database
            revoked = Acceso.revoke_access(client['id'], indicator['id'])
            if not revoked:
                result['message'] = "No se encontró acceso activo para revocar"
                return result
            
            # Sync with TradingView API
            try:
                tv = tradingview()
                tv_access = tv.get_access_details(username_tradingview, pub_id)
                tv.remove_access(tv_access)
            except Exception as tv_error:
                result['message'] = f"Acceso revocado en DB pero error en TradingView: {str(tv_error)}"
                return result
            
            result['success'] = True
            result['message'] = "Acceso revocado exitosamente"
            
        except Exception as e:
            result['message'] = f"Error revoking access: {str(e)}"
        
        return result
    
    @staticmethod
    def check_access(username_tradingview: str, pub_id: str) -> Dict[str, Any]:
        """Check if a client has access to a specific indicator"""
        result = {
            'has_access': False,
            'access_details': None,
            'tradingview_status': None
        }
        
        try:
            # Check in database
            client = Cliente.get_by_username(username_tradingview)
            indicator = Indicador.get_by_pub_id(pub_id)
            
            if client and indicator:
                access = Acceso.get_by_client_and_indicator(client['id'], indicator['id'])
                if access:
                    result['has_access'] = access['estado'] == 'activo'
                    result['access_details'] = access
            
            # Check in TradingView
            try:
                tv = tradingview()
                tv_access = tv.get_access_details(username_tradingview, pub_id)
                result['tradingview_status'] = tv_access
            except Exception:
                pass  # TradingView check is optional
                
        except Exception:
            pass  # Errors are handled by returning default result
        
        return result
    
    @staticmethod
    def get_all_accesses() -> List[Dict[str, Any]]:
        """Get all active accesses"""
        return Acceso.get_active_accesses()
    
    @staticmethod
    def get_expiring_accesses(days: int = 7) -> List[Dict[str, Any]]:
        """Get accesses expiring in the next N days"""
        return Acceso.get_expiring_soon(days)
    
    @staticmethod
    def process_expired_accesses() -> int:
        """Process expired accesses and return count"""
        return Acceso.mark_expired()

class DashboardService:
    """Service for dashboard statistics and overview"""
    
    @staticmethod
    def get_dashboard_stats() -> Dict[str, Any]:
        """Get complete dashboard statistics"""
        from .database import db
        
        stats = db.get_stats()
        
        # Get expiring soon
        expiring_accesses = AccesoService.get_expiring_accesses(7)
        
        # Get recent activity (last 10 accesses created)
        recent_accesses = Acceso.get_all("", ())[:10]
        
        # Top indicators by usage
        top_indicators_query = """
            SELECT i.nombre, i.pub_id, COUNT(a.id) as access_count
            FROM indicadores i
            LEFT JOIN accesos a ON i.id = a.indicador_id AND a.estado = 'activo'
            WHERE i.estado = 'activo'
            GROUP BY i.id, i.nombre, i.pub_id
            ORDER BY access_count DESC
            LIMIT 5
        """
        top_indicators = db.execute_query(top_indicators_query)
        
        return {
            'basic_stats': stats,
            'expiring_accesses': expiring_accesses,
            'recent_accesses': recent_accesses,
            'top_indicators': top_indicators,
            'alerts': {
                'expiring_count': len(expiring_accesses),
                'expired_count': stats.get('total_accesos', 0) - stats.get('accesos_activos', 0)
            }
        }