import os
import secrets

from flask import Blueprint, request, jsonify, session
from flask_login import login_user, login_required
from sqlalchemy.exc import IntegrityError
from urllib.parse import urlparse
import webauthn
from models import db, User, UserRole as Role
from webauthn.helpers.structs import AuthenticatorSelectionCriteria, ResidentKeyRequirement, UserVerificationRequirement
from webauthn.helpers import base64url_to_bytes

apis = Blueprint('apis', __name__)


def _hostname():
    return str(urlparse(request.host_url).hostname)


def _register_user(username, name, role=Role.USER.value):
    user = User(username=username, name=name,
                credential_public_key=b'', credential_id=b'', role=role)
    try:
        db.session.add(user)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        if "duplicate key value" in str(e.orig):
            msg = "Username già esistente"
        else:
            msg = str(e.orig)
        return {'status': 'error', 'message': msg}, 400

    public_credential_creation_options = webauthn.generate_registration_options(
        rp_id=_hostname(),
        rp_name="User Handler",
        user_name=user.username,
        authenticator_selection=AuthenticatorSelectionCriteria(
            resident_key=ResidentKeyRequirement.REQUIRED,
            user_verification=UserVerificationRequirement.PREFERRED)
    )

    session[f"challenge_{user.id}"] = public_credential_creation_options.challenge
    return public_credential_creation_options, user.id


def _verify_save_credentials(user_id, credential):
    result = webauthn.verify_registration_response(
        credential=credential,
        expected_challenge=session.get(f"challenge_{user_id}"),
        expected_origin=f"{request.scheme}://{request.host}",
        expected_rp_id=_hostname()
    )

    user = User.query.get(user_id)
    if not user:
        return {'status': 'error', 'message': 'Utente non trovato'}, 404

    user.credential_public_key = result.credential_public_key
    user.credential_id = result.credential_id
    user.current_sign_count = result.sign_count
    db.session.commit()
    return {'status': 'ok'}, 200


@apis.route('/setup-user', methods=['POST'])
def setup_user():
    if session.get("setup") != True:
        return {'status': 'error', 'message': 'Setup già completato'}, 403

    token = request.get_json().get('token')
    if token != os.getenv('ADMIN_INIT_TOKEN'):
        return jsonify({'error': 'Token di setup non valido'}), 403

    public_credential_creation_options, user_id = _register_user(
        "admin", "admin", Role.ADMIN.value)
    
    tmp_token = secrets.token_urlsafe(16)
    session["tmp_token"] = tmp_token
    return jsonify({
        'publicCredentialCreationOptions': webauthn.options_to_json(public_credential_creation_options),
        'user_id': user_id,
        'token': tmp_token
    })


@apis.route('/verify-setup-user', methods=['POST'])
def verify_setup_user():
    if session.pop("setup", None) != True:
        return {'status': 'error', 'message': 'Setup già completato'}, 403
    data = request.json
    token = data.get('token')
    user_id = data.get('user_id')
    sess_token = session.get("tmp_token")
    if token != session.pop("tmp_token", None):
        return jsonify({'error': 'Token di verifica non valido', 'token1': token, 'token2': sess_token}), 403
    return _verify_save_credentials(user_id, data.get('credential'))


@apis.route('/register-user', methods=['POST'])
@login_required
def register_user():
    data = request.get_json()
    name = data.get('name')
    username = data.get('username')

    public_credential_creation_options, user = _register_user(username, name)
    return jsonify({
        'publicCredentialCreationOptions': webauthn.options_to_json(public_credential_creation_options),
        'user_id': user
    })


@apis.route('/verify-save-credentials', methods=['POST'])
@login_required
def verify_save_credentials():
    data = request.json
    user_id = data.get('user_id')
    return _verify_save_credentials(user_id, data.get('credential'))


@apis.route('/delete-user/<id>', methods=['DELETE'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return {'status': 'error', 'message': 'Utente non trovato'}, 404
    db.session.delete(user)
    db.session.commit()
    return {'status': 'ok'}, 200


@apis.route('/autentication-options', methods=['POST'])
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


@apis.route('/login-verify', methods=['POST'])
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
        result = webauthn.verify_authentication_response(
            credential=credential,
            expected_origin=f"{request.scheme}://{request.host}",
            expected_rp_id=_hostname(),
            expected_challenge=session.get(f"challenge_{user.id}"),
            credential_current_sign_count=user.current_sign_count,
            credential_public_key=user.credential_public_key,
            require_user_verification=True
        )

        login_user(user)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': f'Errore durante la verifica delle credenziali.'}), 500
