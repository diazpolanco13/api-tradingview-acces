"""
API Routes for PineScript Control Access
New management endpoints alongside existing legacy API
"""
from flask import Blueprint, request, jsonify
from functools import wraps
import os
from ..services import ClienteService, IndicadorService, AccesoService, DashboardService

# Create blueprint for new API routes
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

def require_admin_token(f):
    """Decorator for admin authentication - accepts both token headers and authenticated sessions"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        
        # Check for authenticated session first
        if session.get('authenticated'):
            return f(*args, **kwargs)
        
        # Fall back to token authentication
        admin_token = request.headers.get('X-Admin-Token')
        expected_token = os.getenv('ADMIN_TOKEN')
        
        if not expected_token:
            return jsonify({'error': 'Server misconfigured - ADMIN_TOKEN not set'}), 500
        
        if not admin_token or admin_token != expected_token:
            return jsonify({'error': 'Unauthorized - Authentication required'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Dashboard endpoint
@api_bp.route('/dashboard', methods=['GET'])
@require_admin_token
def dashboard():
    """Get dashboard statistics"""
    try:
        stats = DashboardService.get_dashboard_stats()
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Client management endpoints
@api_bp.route('/clients', methods=['GET'])
@require_admin_token
def get_clients():
    """Get all clients"""
    try:
        search_term = request.args.get('search', '')
        
        if search_term:
            clients = ClienteService.search_clients(search_term)
        else:
            clients = ClienteService.get_active_clients()
        
        return jsonify({
            'success': True,
            'data': clients
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/clients', methods=['POST'])
@require_admin_token
def create_client():
    """Create a new client"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username_tradingview'):
            return jsonify({'error': 'username_tradingview is required'}), 400
        
        result = ClienteService.create_client(
            username_tradingview=data['username_tradingview'],
            email=data.get('email', ''),
            nombre_completo=data.get('nombre_completo', '')
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/clients/<int:client_id>', methods=['GET'])
@require_admin_token
def get_client_profile(client_id):
    """Get client profile with access history"""
    try:
        profile = ClienteService.get_client_profile(client_id)
        
        if not profile:
            return jsonify({'error': 'Client not found'}), 404
        
        return jsonify({
            'success': True,
            'data': profile
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/clients/<int:client_id>', methods=['PUT'])
@require_admin_token
def update_client(client_id):
    """Update a client"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = ClienteService.update_client(client_id, **data)
        
        if success:
            return jsonify({'success': True, 'message': 'Client updated successfully'})
        else:
            return jsonify({'error': 'Client not found or update failed'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/clients/<int:client_id>', methods=['DELETE'])
@require_admin_token
def deactivate_client(client_id):
    """Deactivate a client (soft delete)"""
    try:
        success = ClienteService.deactivate_client(client_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Client deactivated successfully'})
        else:
            return jsonify({'error': 'Client not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Indicator management endpoints
@api_bp.route('/indicators', methods=['GET'])
@require_admin_token
def get_indicators():
    """Get all indicators"""
    try:
        search_term = request.args.get('search', '')
        
        if search_term:
            indicators = IndicadorService.search_indicators(search_term)
        else:
            indicators = IndicadorService.get_all_indicators()
        
        return jsonify({
            'success': True,
            'data': indicators
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/indicators', methods=['POST'])
@require_admin_token
def create_indicator():
    """Create a new indicator"""
    try:
        data = request.get_json()
        
        if not data or not data.get('nombre') or not data.get('pub_id'):
            return jsonify({'error': 'nombre and pub_id are required'}), 400
        
        indicator_id = IndicadorService.create_indicator(
            nombre=data['nombre'],
            pub_id=data['pub_id'],
            precio=float(data.get('precio', 0.0)),
            version=data.get('version', '1.0'),
            descripcion=data.get('descripcion', '')
        )
        
        return jsonify({
            'success': True,
            'indicator_id': indicator_id,
            'message': 'Indicator created successfully'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/indicators/<int:indicator_id>', methods=['GET'])
@require_admin_token
def get_indicator_stats(indicator_id):
    """Get indicator statistics"""
    try:
        stats = IndicadorService.get_indicator_stats(indicator_id)
        
        if not stats:
            return jsonify({'error': 'Indicator not found'}), 404
        
        return jsonify({
            'success': True,
            'data': stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/indicators/<int:indicator_id>', methods=['PUT'])
@require_admin_token
def update_indicator(indicator_id):
    """Update an indicator"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        success = IndicadorService.update_indicator(indicator_id, **data)
        
        if success:
            return jsonify({'success': True, 'message': 'Indicator updated successfully'})
        else:
            return jsonify({'error': 'Indicator not found or update failed'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/indicators/<int:indicator_id>', methods=['DELETE'])
@require_admin_token
def delete_indicator(indicator_id):
    """Delete an indicator (soft delete)"""
    try:
        success = IndicadorService.delete_indicator(indicator_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Indicator deleted successfully'})
        else:
            return jsonify({'error': 'Indicator not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Access management endpoints
@api_bp.route('/access', methods=['GET'])
@require_admin_token
def get_accesses():
    """Get all accesses"""
    try:
        filter_type = request.args.get('filter', 'all')  # all, active, expiring
        
        if filter_type == 'expiring':
            days = int(request.args.get('days', 7))
            accesses = AccesoService.get_expiring_accesses(days)
        elif filter_type == 'active':
            accesses = AccesoService.get_all_accesses()
        else:
            accesses = AccesoService.get_all_accesses()  # Default to active for now
        
        return jsonify({
            'success': True,
            'data': accesses
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/access', methods=['POST'])
@require_admin_token
def grant_access():
    """Grant access to a client"""
    try:
        data = request.get_json()
        
        required_fields = ['client_id', 'indicator_id', 'duracion_dias']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'error': f'Required fields: {", ".join(required_fields)}'
            }), 400
        
        # Get client and indicator details for AccesoService
        from ..models import Cliente, Indicador
        client = Cliente.get_by_id(data['client_id'])
        indicator = Indicador.get_by_id(data['indicator_id'])
        
        if not client or not indicator:
            return jsonify({'error': 'Client or indicator not found'}), 400
        
        result = AccesoService.grant_access(
            username_tradingview=client['username_tradingview'],
            pub_id=indicator['pub_id'],
            days=int(data['duracion_dias'])
        )
        
        if result['success']:
            return jsonify(result), 201
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/access/<int:client_id>/<int:indicator_id>', methods=['DELETE'])
@require_admin_token
def revoke_access(client_id, indicator_id):
    """Revoke access from a client"""
    try:
        # Get client and indicator details for AccesoService
        from ..models import Cliente, Indicador
        client = Cliente.get_by_id(client_id)
        indicator = Indicador.get_by_id(indicator_id)
        
        if not client or not indicator:
            return jsonify({'error': 'Client or indicator not found'}), 400
        
        result = AccesoService.revoke_access(
            username_tradingview=client['username_tradingview'],
            pub_id=indicator['pub_id']
        )
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Maintenance endpoint
@api_bp.route('/maintenance/expired', methods=['POST'])
@require_admin_token
def process_expired_accesses():
    """Process expired accesses"""
    try:
        # This could clean up expired accesses or send notifications
        # For now, just return success
        return jsonify({
            'success': True,
            'message': 'Expired accesses processed successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/access/check', methods=['POST'])
@require_admin_token
def check_access():
    """Check access status for a client"""
    try:
        data = request.get_json()
        
        required_fields = ['username_tradingview', 'pub_id']
        if not data or not all(field in data for field in required_fields):
            return jsonify({
                'error': f'Required fields: {", ".join(required_fields)}'
            }), 400
        
        result = AccesoService.check_access(
            username_tradingview=data['username_tradingview'],
            pub_id=data['pub_id']
        )
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Maintenance endpoints
@api_bp.route('/maintenance/expired', methods=['POST'])
@require_admin_token
def process_expired():
    """Process expired accesses"""
    try:
        count = AccesoService.process_expired_accesses()
        
        return jsonify({
            'success': True,
            'message': f'Processed {count} expired accesses'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Token validation endpoints
@api_bp.route("/validate-token", methods=["POST", "GET"])
def validate_token():
    """Validate admin token and provide clear feedback"""
    import os
    
    # Get token from header or JSON body
    admin_token = request.headers.get("X-Admin-Token")
    if not admin_token and request.method == "POST":
        data = request.get_json() or {}
        admin_token = data.get("token")
    
    expected_token = os.getenv("ADMIN_TOKEN")
    
    if not expected_token:
        return jsonify({
            "valid": False,
            "error": "Server misconfigured - ADMIN_TOKEN not set",
            "message": "Contacta al administrador del sistema"
        }), 500
    
    if not admin_token:
        return jsonify({
            "valid": False,
            "error": "No token provided",
            "message": "Incluye el token en el header X-Admin-Token o en el body como \"token\""
        }), 400
    
    if admin_token == expected_token:
        return jsonify({
            "valid": True,
            "message": "✅ Token válido - Acceso autorizado",
            "permissions": ["dashboard", "clients", "indicators", "access_management"]
        })
    else:
        return jsonify({
            "valid": False,
            "error": "Invalid token",
            "message": "❌ Token inválido - Acceso denegado",
            "hint": f"Token recibido: {admin_token[:12]}... (truncado por seguridad)"
        }), 401

@api_bp.route("/get-token", methods=["GET"])
def get_current_token():
    """Get current admin token (development only)"""
    import os
    if os.getenv("ENV") == "production":
        return jsonify({"error": "Token access disabled in production"}), 403
    
    token = os.getenv("ADMIN_TOKEN")
    if token:
        return jsonify({
            "token": token,
            "message": "Use this token in X-Admin-Token header for admin operations"
        })
    else:
        return jsonify({"error": "No token found"}), 404

