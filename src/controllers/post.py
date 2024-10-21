from flask import Blueprint, request  
from src.app import Post, db  
from http import HTTPStatus
from datetime import datetime

# Registro do Blueprint para agrupar rotas de posts com o prefixo '/posts'.
app = Blueprint('post', __name__, url_prefix='/posts')

# Cria um novo post no banco de dados.
def _create_post():
    data = request.json
    
    if not data:
        return {'message': 'Request body must be JSON'}, HTTPStatus.BAD_REQUEST

    created = data.get('created')
    
    if created:
        try:
            created = datetime.fromisoformat(created)  # Converte a data para o formato datetime
        except ValueError:
            return {'message': 'Invalid datetime format. Use ISO format.'}, HTTPStatus.BAD_REQUEST
    else:
        created = datetime.utcnow()  # Usa a data atual se não for fornecida
    
    post = Post(
        title=data['title'],
        body=data['body'],
        author_id=data['author_id']
    )
    db.session.add(post)  # Adiciona o novo post à sessão do banco de dados
    db.session.commit()  # Confirma a transação no banco de dados

# Lista todos os posts registrados no banco de dados.
def _list_posts():
    query = db.select(Post)
    posts = db.session.execute(query).scalars()
    return [
        {
            "id": post.id,
            "title": post.title,
            "body": post.body,
            "created": post.created,
            "author_id": post.author_id,
        }
        for post in posts
    ]

# Rota para criar um post ou listar todos os posts, dependendo do método da requisição.
@app.route("/", methods=["POST", "GET"])
def list_get_or_create_post():
    if request.method == 'POST':
        _create_post()
        return {'message': 'Post created successfully!'}, HTTPStatus.CREATED
    else:
        return {'posts': _list_posts()}

# Rota para obter os detalhes de um post específico pelo ID.
@app.route('/<int:post_id>')
def get_post(post_id):
    post = db.get_or_404(Post, post_id)
    return {
        "id": post.id,
        "title": post.title,
        "body": post.body,
        "created": post.created,
        "author_id": post.author_id
    }
    
# Rota para atualizar um post específico, se fornecidos novos dados.
@app.route('/<int:post_id>', methods=['PATCH'])
def update_post(post_id):
    post = db.get_or_404(Post, post_id)
    data = request.json
    
    if "title" in data:
        post.title = data['title']
    
    if "body" in data:
        post.body = data['body']
    
    if "created" in data:
        post.created = data['created']
        
    if "author_id" in data:
        post.author_id = data['author_id']

    db.session.commit()  # Confirma a atualização no banco de dados
    
    return {'message': 'Post updated successfully!'}, HTTPStatus.OK

# Rota para deletar um post específico pelo ID.
@app.route('/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    post = db.get_or_404(Post, post_id)
    db.session.delete(post)  # Deleta o post do banco de dados
    db.session.commit()  # Confirma a exclusão no banco de dados
    return "", HTTPStatus.NO_CONTENT  # Retorna status 204 (Sem Conteúdo) após a exclusão bem-sucedida
