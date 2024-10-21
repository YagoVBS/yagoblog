from flask import Blueprint, request
from src.app import User, db
from http import HTTPStatus
from flask_jwt_extended import jwt_required
from src.utils import requires_role


# Registro do Blueprint para agrupar rotas de usuários com o prefixo '/users'.

app = Blueprint('user', __name__, url_prefix='/users')

# Cria um novo usuário no banco de dados.
def _create_user():
    data = request.json
    user = User(
        username=data["username"],       
        password=data["password"],
        role_id=data["role_id"]           
    )
    db.session.add(user)
    db.session.commit()

# Lista todos os usuários registrados no banco de dados.
def _list_users():
    query = db.select(User)
    users = db.session.execute(query).scalars()
    return [
        
        {"id": user.id, 
         "username": user.username,
         "role":{"id":user.role_id, "name":user.role.name}
         }
        
        for user in users
    ]

# Rota para criar um usuário ou listar todos os usuários, dependendo do método da requisição.

@app.route("/", methods=["GET", "POST"])
@jwt_required()
@requires_role("admin")
def list_get_or_create_user():
    
    if request.method == 'POST':
        _create_user()
        return {'message': 'User created!'}, HTTPStatus.CREATED
    else:
        return {'users' : _list_users()}

# Rota para obter os detalhes de um usuário específico pelo ID.
@app.route('/<int:user_id>')
def get_user(user_id):
    user = db.get_or_404(User, user_id)
    return {
        "id": user.id,
        "username": user.username,
    }

# Rota para atualizar o nome de um usuário específico, se fornecido.
@app.route('/<int:user_id>', methods=['PATCH'])
def update_user(user_id):
    user = db.get_or_404(User, user_id)
    data = request.json
    
    if 'username' in data:
        user.username = data['username']
        db.session.commit()
    
    return {
        "id": user.id,
        "username": user.username,
    }

# Rota para deletar um usuário específico pelo ID.
@app.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = db.get_or_404(User, user_id)
    db.session.delete(user)
    db.session.commit()
    return " ", HTTPStatus.NO_CONTENT
