from flask import Blueprint, request
from src.app import Role, db
from http import HTTPStatus
from flask_jwt_extended import jwt_required, get_jwt_identity

# Registro do Blueprint para agrupar rotas de usuários com o prefixo '/users'.

app = Blueprint('role', __name__, url_prefix='/roles')

@app.route("/", methods=["POST"])
def create_role():
    
    data = request.json
    role = Role(name=data['name'])
    db.session.add(role)
    db.session.commit()
    
    return {'message': 'Role created!'}, HTTPStatus.CREATED
   