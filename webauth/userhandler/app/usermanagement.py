import os
import secrets

from common.models import UserRole as Role, User, db
from common.userlogin import _hostname

from sqlalchemy.exc import IntegrityError
from flask import Blueprint, session, request, jsonify
from webauthn.helpers.structs import AuthenticatorSelectionCriteria, ResidentKeyRequirement, UserVerificationRequirement
from flask_login import login_required

import webauthn

usermanagement = Blueprint('usermanagement', __name__)

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

@usermanagement.route('/setup-user', methods=['POST'])
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


@usermanagement.route('/verify-setup-user', methods=['POST'])
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


@usermanagement.route('/register-user', methods=['POST'])
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


@usermanagement.route('/verify-save-credentials', methods=['POST'])
@login_required
def verify_save_credentials():
    data = request.json
    user_id = data.get('user_id')
    return _verify_save_credentials(user_id, data.get('credential'))


@usermanagement.route('/delete-user/<id>', methods=['DELETE'])
@login_required
def delete_user(id):
    user = User.query.get(id)
    if not user:
        return {'status': 'error', 'message': 'Utente non trovato'}, 404
    db.session.delete(user)
    db.session.commit()
    return {'status': 'ok'}, 200