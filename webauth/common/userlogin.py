from flask import Blueprint, request, jsonify, session, redirect, current_app
from flask_login import login_user, logout_user

from urllib.parse import urlparse
from webauthn.helpers.structs import UserVerificationRequirement

import webauthn

from common.models import User


userlogin = Blueprint('userlogin', __name__)

def _hostname():
    return str(urlparse(request.host_url).hostname)

@userlogin.route('/autentication-options', methods=['POST'])
def authenticate():
    username = request.json.get('username')
    user = User.query.filter(User.username == username).first()
    if not user:
        return jsonify({'error': "utente non trovato"}), 500
    options = webauthn.generate_authentication_options(rp_id=_hostname(),
                                                       user_verification=UserVerificationRequirement.PREFERRED)
    session[f"challenge_{user.id}"] = options.challenge
    jsonOptions = webauthn.options_to_json(options)
    return jsonify(jsonOptions)


@userlogin.route('/login-verify', methods=['POST'])
def login_verify():
    try:
        data = request.json

        credential = data.get('credential')
        if not credential:
            return jsonify({'error': "credential non presente"}), 500

        username = data.get('username')
        user = User.query.filter(User.username == username).first()
        if not user:
            return jsonify({'error': "utente non trovato"}), 500

        challenge = session.get(f"challenge_{user.id}")
        if not challenge:
            return jsonify({'error': "challenge non presente"}), 500
        
        host = request.headers.get("Origin", request.host)
        result = webauthn.verify_authentication_response(
            credential=credential,
            expected_origin=f"{host}",
            expected_rp_id=_hostname(),
            expected_challenge=session.get(f"challenge_{user.id}"),
            credential_current_sign_count=user.current_sign_count,
            credential_public_key=user.credential_public_key,
            require_user_verification=True
        )

        login_user(user)
        return jsonify({'success': True, 'user': user.id}), 200
    except Exception as e:
        return jsonify({'error': f'Errore durante la verifica delle credenziali. {e}'}), 500

@userlogin.route('/logout')
def logout():
    logout_user()
    return redirect('/')