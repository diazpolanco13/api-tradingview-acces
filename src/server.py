from flask import Flask, request, render_template, jsonify
from .tradingview import tradingview
from replit import db
import json
import os
from datetime import datetime
from functools import wraps
#from threading import Thread
app = Flask('')

# Security: Admin authentication
def require_admin_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Only accept token in secure header, never in query params
        admin_token = request.headers.get('X-Admin-Token')
        expected_token = os.getenv('ADMIN_TOKEN')
        
        # Require ADMIN_TOKEN to be set
        if not expected_token:
            return jsonify({'error': 'Server misconfigured - ADMIN_TOKEN not set'}), 500
        
        if not admin_token or admin_token != expected_token:
            return jsonify({'error': 'Unauthorized - Valid X-Admin-Token header required'}), 401
        
        return f(*args, **kwargs)
    return decorated_function


@app.route('/validate/<username>', methods=['GET'])
def validate(username):
  try:
    print(username)
    tv = tradingview()
    response = tv.validate_username(username)
    return json.dumps(response), 200, {
      'Content-Type': 'application/json; charset=utf-8'
    }
  except Exception as e:
    print("[X] Exception Occured : ", e)
    failureResponse = {'errorMessage': 'Unknown Exception Occurred'}
    return json.dumps(failureResponse), 500, {
      'Content-Type': 'application/json; charset=utf-8'
    }


@app.route('/access/<username>', methods=['GET', 'POST', 'DELETE'])
@require_admin_token
def access(username):
  try:
    # Solo leer JSON en métodos que tienen body
    if request.method in ['POST', 'DELETE']:
      jsonPayload = request.json or {}
      print(f"Payload received: {jsonPayload}")
    else:
      jsonPayload = {}
      
    # Nuevo formato para compatibilidad con pruebas
    if 'indicator_id' in jsonPayload or request.method == 'GET':
      # Formato de pruebas: indicator_id + days
      indicator_id = jsonPayload.get('indicator_id')
      days = jsonPayload.get('days')
      
      if request.method == 'GET':
        # Verificar acceso real al indicador si se proporciona indicator_id en query params
        indicator_id_param = request.args.get('indicator_id')
        if indicator_id_param:
          try:
            tv = tradingview()
            access = tv.get_access_details(username, indicator_id_param)
            print(f"Access details response: {access}")
            # Usar el campo correcto 'hasAccess' en lugar de 'results'
            has_access = access.get('hasAccess', False) if isinstance(access, dict) else False
            response = {
              'username': username,
              'has_access': has_access,
              'status': 'checked',
              'indicator_id': indicator_id_param,
              'expiration': access.get('currentExpiration') if has_access else None,
              'no_expiration': access.get('noExpiration', False) if has_access else False
            }
            return jsonify(response), 200
          except Exception as e:
            print(f"Error checking access: {e}")
            response = {
              'username': username,
              'has_access': False,
              'status': 'error',
              'error': str(e)
            }
            return jsonify(response), 200
        else:
          # Respuesta simple sin indicador específico
          response = {
            'username': username,
            'has_access': False,
            'status': 'checked'
          }
          return jsonify(response), 200
      
      elif request.method == 'POST' and indicator_id and days:
        # Otorgar acceso
        try:
          tv = tradingview()
          access = tv.get_access_details(username, indicator_id)
          tv.add_access(access, 'd', days)  # 'd' = días
          return jsonify({'success': True, 'message': f'Access granted for {days} days'}), 200
        except Exception as e:
          print(f"Error granting access: {e}")
          return jsonify({'success': False, 'error': str(e)}), 200
      
      elif request.method == 'DELETE' and indicator_id:
        # Revocar acceso
        try:
          tv = tradingview()
          access = tv.get_access_details(username, indicator_id)
          tv.remove_access(access)
          return jsonify({'success': True, 'message': 'Access revoked'}), 200
        except Exception as e:
          print(f"Error revoking access: {e}")
          return jsonify({'success': False, 'error': str(e)}), 200
    
    # Formato original para retrocompatibilidad: pine_ids + duration
    else:
      tv = tradingview()
      pine_ids = jsonPayload.get('pine_ids') or []
      print(f"Pine IDs: {pine_ids}")
      accessList = []
      for pine_id in pine_ids:
        access = tv.get_access_details(username, pine_id)
        accessList = accessList + [access]

      if request.method == 'POST':
        duration = jsonPayload.get('duration')
        if duration:
          dNumber = int(duration[:-1])
          dType = duration[-1:]
          for access in accessList:
            tv.add_access(access, dType, dNumber)

      if request.method == 'DELETE':
        for access in accessList:
          tv.remove_access(access)
      
      return json.dumps(accessList), 200, {
        'Content-Type': 'application/json; charset=utf-8'
      }

    return jsonify({'error': 'Invalid request format'}), 400

  except Exception as e:
    print("[X] Exception Occured : ", e)
    failureResponse = {'errorMessage': 'Unknown Exception Occurred'}
    return json.dumps(failureResponse), 500, {
      'Content-Type': 'application/json; charset=utf-8'
    }


@app.route('/')
def main():
  return 'Your bot is alive!'


@app.route('/admin')
def admin_panel():
  # Public access to serve the HTML - authentication happens via API calls
  return render_template('admin.html')


@app.route('/admin/cookies/status', methods=['GET'])
@require_admin_token
def check_cookies_status():
  try:
    # Crear instancia de tradingview para verificar el estado
    tv = tradingview()
    
    # Si llegamos aquí sin errores, las cookies son válidas
    current_time = datetime.now().isoformat()
    
    # Obtener información completa de la cuenta
    balance = getattr(tv, 'account_balance', '0.00')
    username = getattr(tv, 'username', '')
    partner_status = getattr(tv, 'partner_status', 0)
    aff_id = getattr(tv, 'aff_id', 0)
    profile_info = getattr(tv, 'profile_info', {})
    
    return jsonify({
      'valid': True,
      'lastCheck': current_time,
      'balance': balance,
      'username': username,
      'partner_status': partner_status,
      'aff_id': aff_id,
      'profile_info': profile_info,
      'status': 'authenticated'
    })
  except Exception as e:
    current_time = datetime.now().isoformat()
    return jsonify({
      'valid': False,
      'lastCheck': current_time,
      'error': str(e),
      'status': 'failed'
    })


@app.route('/admin/cookies/update', methods=['POST'])
@require_admin_token
def update_cookies():
  try:
    data = request.json or {}
    sessionid = data.get('sessionid', '').strip()
    sessionid_sign = data.get('sessionid_sign', '').strip()
    
    if not sessionid or not sessionid_sign:
      return jsonify({
        'success': False,
        'error': 'Both sessionid and sessionid_sign are required'
      }), 400
    
    # Guardar en la base de datos de Replit
    if db is not None:
      db['tv_sessionid'] = sessionid
      db['tv_sessionid_sign'] = sessionid_sign
      db['cookies_updated_at'] = datetime.now().isoformat()
    else:
      raise Exception("Database connection not available")
    
    # Verificar que las cookies funcionan creando una instancia
    try:
      test_tv = tradingview()
      return jsonify({
        'success': True,
        'message': 'Cookies updated and verified successfully',
        'timestamp': datetime.now().isoformat()
      })
    except Exception as test_error:
      return jsonify({
        'success': False,
        'error': f'Cookies saved but failed verification: {str(test_error)}'
      }), 400
      
  except Exception as e:
    return jsonify({
      'success': False,
      'error': f'Failed to update cookies: {str(e)}'
    }), 500


# def run():
#   app.run(host='0.0.0.0', port=5000)

# def start_server_async():
#   server = Thread(target=run)
#   server.start()


def start_server():
  app.run(host='0.0.0.0', port=5000)
