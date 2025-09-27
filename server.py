from flask import Flask, request, render_template, jsonify
from tradingview import tradingview
from replit import db
import json
from datetime import datetime
#from threading import Thread
app = Flask('')


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
def access(username):
  try:
    jsonPayload = request.json or {}
    pine_ids = jsonPayload.get('pine_ids') or []
    print(jsonPayload)
    print(pine_ids)
    tv = tradingview()
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
  return render_template('admin.html')


@app.route('/admin/cookies/status', methods=['GET'])
def check_cookies_status():
  try:
    # Crear instancia de tradingview para verificar el estado
    tv = tradingview()
    
    # Si llegamos aquí sin errores, las cookies son válidas
    current_time = datetime.now().isoformat()
    
    # Obtener información de la cuenta si está disponible
    balance = getattr(tv, 'account_balance', '0.00')
    
    return jsonify({
      'valid': True,
      'lastCheck': current_time,
      'balance': balance,
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
    db['tv_sessionid'] = sessionid
    db['tv_sessionid_sign'] = sessionid_sign
    db['cookies_updated_at'] = datetime.now().isoformat()
    
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
