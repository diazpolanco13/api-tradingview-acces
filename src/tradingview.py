import os
from replit import db
from . import config
import requests
import platform
from urllib3 import encode_multipart_formdata
from datetime import datetime, timezone
from . import helper


class tradingview:

  def get_profile_info(self):
    """Get detailed profile information"""
    try:
      # Try different endpoints for user data
      headers = {'cookie': self.cookies}
      endpoints_to_try = [
        f"https://www.tradingview.com/pine_perm/get_author_data/?username={self.username}",
        f"https://www.tradingview.com/u/{self.username}/",
        "https://www.tradingview.com/accounts/me/",
        "https://www.tradingview.com/social/user/",
      ]
      
      for endpoint in endpoints_to_try:
        try:
          response = requests.get(endpoint, headers=headers)
          print(f'Endpoint {endpoint} status: {response.status_code}')
          
          if response.status_code == 200:
            # Try to parse as JSON first
            try:
              data = response.json()
              if data and isinstance(data, dict) and len(data) > 0:
                print(f'Profile data from {endpoint}: {data}')
                return data
            except:
              # If not JSON, check if HTML contains useful data
              content = response.text
              if 'userpic' in content or 'avatar' in content:
                print(f'Found profile page with potential image data: {endpoint}')
                # Extract image URL from HTML if possible
                import re
                img_pattern = r'https://s3\.tradingview\.com/userpics/[^"\']*'
                matches = re.findall(img_pattern, content)
                if matches:
                  profile_image = matches[0]
                  print(f'Found profile image: {profile_image}')
                  return {'profile_image': profile_image, 'username': self.username}
        except Exception as e:
          print(f'Error with endpoint {endpoint}: {e}')
          continue
          
    except Exception as e:
      print(f'Error getting profile info: {e}')
      return None
    
  def __init__(self):
    print('Loading cookies from database')
    
    # Try to get cookies from database first
    self.sessionid = db.get('tv_sessionid', '')
    self.sessionid_sign = db.get('tv_sessionid_sign', '')
    
    if self.sessionid and self.sessionid_sign:
      print('Using cookies from database')
      self.cookies = f'sessionid={self.sessionid}; sessionid_sign={self.sessionid_sign}'
      
      # Test if cookies are valid
      headers = {'cookie': self.cookies}
      test = requests.request("GET", config.urls["tvcoins"], headers=headers)
      print(f'Cookie test response status: {test.status_code}')
      
      if test.status_code == 200:
        print('Database cookies are valid')
        try:
          account_data = test.json()
          self.account_balance = account_data.get('partner_fiat_balance', 0)
          self.username = account_data.get('link', '')
          self.partner_status = account_data.get('partner_status', 0)
          self.aff_id = account_data.get('aff_id', 0)
          print(f'Account balance: ${self.account_balance}')
          print(f'Username: {self.username}')
          print(f'Full account data: {account_data}')
          
          # Try to get additional profile info
          profile_info = self.get_profile_info()
          if profile_info:
            self.profile_info = profile_info
        except:
          self.account_balance = 0
        return
      else:
        print('Database cookies are invalid, need manual update')
        
    # If no valid cookies, raise an error that requires manual intervention
    print('No valid cookies found - please update through admin panel')
    raise Exception('Invalid or expired TradingView session. Please update cookies through /admin panel.')

  def validate_username(self, username):
    users = requests.get(config.urls["username_hint"] + "?s=" + username)
    usersList = users.json()
    validUser = False
    verifiedUserName = ''
    for user in usersList:
      if user['username'].lower() == username.lower():
        validUser = True
        verifiedUserName = user['username']
    return {"validuser": validUser, "verifiedUserName": verifiedUserName}

  def get_access_details(self, username, pine_id):
    user_payload = {'pine_id': pine_id, 'username': username}

    user_headers = {
      'origin': 'https://www.tradingview.com',
      'Content-Type': 'application/x-www-form-urlencoded',
      'Cookie': self.cookies
    }
    print(user_payload)
    usersResponse = requests.post(config.urls['list_users'] +
                                  '?limit=10&order_by=-created',
                                  headers=user_headers,
                                  data=user_payload)
    userResponseJson = usersResponse.json()
    print(userResponseJson)
    users = userResponseJson['results']

    access_details = user_payload
    hasAccess = False
    noExpiration = False
    expiration = str(datetime.now(timezone.utc))
    for user in users:
      if user['username'].lower() == username.lower():
        hasAccess = True
        strExpiration = user.get("expiration")
        if strExpiration is not None:
          expiration = user['expiration']
        else:
          noExpiration = True

    access_details['hasAccess'] = hasAccess
    access_details['noExpiration'] = noExpiration
    access_details['currentExpiration'] = expiration
    return access_details

  def add_access(self, access_details, extension_type, extension_length):
    noExpiration = access_details['noExpiration']
    access_details['expiration'] = access_details['currentExpiration']
    access_details['status'] = 'Not Applied'
    if not noExpiration:
      payload = {
        'pine_id': access_details['pine_id'],
        'username_recip': access_details['username']
      }
      if extension_type != 'L':
        expiration = helper.get_access_extension(
          access_details['currentExpiration'], extension_type,
          extension_length)
        payload['expiration'] = expiration
        access_details['expiration'] = expiration
      else:
        access_details['noExpiration'] = True
      enpoint_type = 'modify_access' if access_details[
        'hasAccess'] else 'add_access'

      body, contentType = encode_multipart_formdata(payload)

      headers = {
        'origin': 'https://www.tradingview.com',
        'Content-Type': contentType,
        'cookie': self.cookies
      }
      add_access_response = requests.post(config.urls[enpoint_type],
                                          data=body,
                                          headers=headers)
      access_details['status'] = 'Success' if (
        add_access_response.status_code == 200
        or add_access_response.status_code == 201) else 'Failure'
    return access_details

  def remove_access(self, access_details):
    payload = {
      'pine_id': access_details['pine_id'],
      'username_recip': access_details['username']
    }
    body, contentType = encode_multipart_formdata(payload)

    headers = {
      'origin': 'https://www.tradingview.com',
      'Content-Type': contentType,
      'cookie': self.cookies
    }
    remove_access_response = requests.post(config.urls['remove_access'],
                                           data=body,
                                           headers=headers)
    access_details['status'] = 'Success' if (remove_access_response.status_code
                                             == 200) else 'Failure'
