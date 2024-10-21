import os
import sqlalchemy as sqla
from datetime import datetime
from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import click
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

# Definindo a classe base para o SQLAlchemy
class Base(DeclarativeBase):
    pass

# Instanciando o SQLAlchemy e vinculando à classe base
db = SQLAlchemy(model_class=Base)
migrate = Migrate()  # Inicializa o gerenciador de migrações
jwt = JWTManager()   # Inicializa o gerenciador de JWT

class Role(db.Model):
    id: Mapped[int] = mapped_column(sqla.Integer, primary_key=True)
    name: Mapped[str] = mapped_column(sqla.String, nullable=False)
    user: Mapped[list["User"]] = relationship(back_populates='role')

class User(db.Model):
    # Define o modelo User com campos para ID, nome de usuário e status ativo
    id: Mapped[int] = mapped_column(sqla.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(sqla.String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(sqla.String, nullable=False)
    role_id: Mapped[int] = mapped_column(sqla.ForeignKey("role.id"))
    role: Mapped["Role"] = relationship(back_populates='user')
    
    def __repr__(self):
        return f"User(id={self.id!r}, username={self.username!r}, active={self.active!r})"

class Post(db.Model):
    # Define o modelo Post com campos para ID, título, corpo, data de criação e autor
    id: Mapped[int] = mapped_column(sqla.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(sqla.String, nullable=False)
    body: Mapped[str] = mapped_column(sqla.String, nullable=False)
    created: Mapped[datetime] = mapped_column(sqla.DateTime, default=sqla.func.now())
    author_id: Mapped[int] = mapped_column(sqla.ForeignKey('user.id'))
    
    def __repr__(self):
        return f"Post(id={self.id!r}, title={self.title!r}, author_id={self.author_id!r})"

# Comando do Flask CLI para inicializar o banco de dados
@click.command('init-db')
def init_db_command():
    """Limpa os dados existentes e cria novas tabelas."""
    with current_app.app_context():  # Garante que estamos no contexto da aplicação Flask
        db.create_all()  # Cria as tabelas definidas nos modelos
    click.echo('Banco de dados inicializado.')  # Exibe a mensagem no terminal após a criação

# Função para criar e configurar a aplicação Flask
def create_app(test_config=None):
    # Inicializa a aplicação Flask
    app = Flask(__name__, instance_relative_config=True)
    
    # Configurações das aplicações
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI=os.environ["DATABASE_URL"],
        JWT_SECRET_KEY='super-secret',
    )

    if test_config is None:
        # Carrega a configuração da instância 'config.py', se existir
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Carrega a configuração de teste, se fornecida
        app.config.from_mapping(test_config)

    # Registrar o comando CLI para inicializar o banco de dados
    app.cli.add_command(init_db_command)
    
    # Inicializa as extensões
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    
    # Registro blueprints
    from src.controllers import user, post
    from src.controllers import auth, role
    
    app.register_blueprint(user.app)
    app.register_blueprint(post.app)
    app.register_blueprint(auth.app)
    app.register_blueprint(role.app)
    
    return app  # Retorna a aplicação configurada
