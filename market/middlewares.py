from datetime import timedelta

from flask_http_middleware import  BaseHTTPMiddleware
import time

from jose import jwt

from market import app
from flask import render_template , redirect , url_for , flash , request , make_response

from market.routes import SECRET_KEY_JWT, ALGORITHM, create_access_token


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self):
        super().__init__()

    def dispatch(self, request, call_next):
        t0 = time.time()
        response = call_next(request)
        response_time = time.time()-t0
        response.headers.add("response_time", response_time)
        return response


@app.before_request
def jwt_middleware():

    try:
        token = request.cookies.get('access_token')
        if token == None and request.endpoint == 'login_page':
            return None
        if token == None and request.endpoint != 'login_page':
            return redirect(url_for('login_page'))
        payload = jwt.decode(token, SECRET_KEY_JWT,algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError:

        if request.endpoint == 'login_page':
            return None
        flash('Sorry ! token expired', category='info')

        # check refresh token expiry if not yet expired then use refresh token to generate new tokens
        try:
            refresh_token = request.cookies.get('refresh_token')
            payload = jwt.decode(refresh_token, SECRET_KEY_JWT, algorithms=[ALGORITHM])
            response = make_response(redirect(request.path))

            token_expires = timedelta(minutes=1)
            token = create_access_token(payload["sub"], expires_delta=token_expires)
            response.set_cookie(key="access_token", value=token)

            flash('Great ! access token refreshed using refresh token', category='info')
            return response
        except jwt.ExpiredSignatureError:
            flash('Sorry ! refresh token expired', category='info')

        if request.endpoint != 'login_page':
            return redirect(url_for('login_page'))

    except jwt.JWTError:
        flash('Sorry ! token error', category='info')
        if request.endpoint != 'login_page':
            return redirect(url_for('login_page'))

    return None




