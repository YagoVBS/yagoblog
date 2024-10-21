import pytest
from src.app import create_app, db, User, Role

@pytest.fixture()
def app():
    app = create_app(
        {
        "SECRET_KEY":"test",
        "SQLALCHEMY_DATABASE_URI" : "sqlite://",
        "JWT_SECRET_KEY" : "test",
        }
    )
    with app.app_context():
        db.create_all()
        yield app



@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def access_token(client):
    role = Role(name='admin')
    db.session.add(role)
    db.session.commit()
    
    user = User(username='joe', password='test', role_id=role.id)
    db.session.add(user)
    db.session.commit()

    response = client.post("/auth/login", json={"username":user.username, "password": user.password})
    
    return response.json["access_token"]

