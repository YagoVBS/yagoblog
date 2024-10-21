from http import HTTPStatus
from src.app import User, Role , db


def test_get_user_sucess(client):
    #Given
    role = Role(name='admin')
    db.session.add(role)
    db.session.commit()
    
    user = User(username='joe', password='test', role_id=role.id)
    db.session.add(user)
    db.session.commit()
    
    #When
    response = client.get(f"/users/{user.id}")
    
    #Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {"id":user.id, "username": user.username}
    
    
def test_get_user_not_found(client):
    #Given
    role = Role(name='admin')
    db.session.add(role)
    db.session.commit()
    
    user_id = 1
    
    #When
    response = client.get(f"/users/{user_id}")
    
    #Then
    assert response.status_code == HTTPStatus.NOT_FOUND
    # assert response.json == {}

def test_create_user(client, access_token):
    #Given
    role_id = db.session.execute(db.select(Role.id).where(Role.name == "admin")).scalar()
    
    payload = {
	"username": "user2",
	"password": "user2",
	"role_id": role_id
    }
    
    #When
    response = client.post("/users/", json=payload, headers={"Authorization": f"Bearer {access_token}"})

    #Then
    assert response.status_code == HTTPStatus.CREATED
    assert response.json == {"message": "User created!"}
    # assert db.session.execute(db.select(User).count()).scalar() == 2
    
def test_list_users(client, access_token):
    #Given
    user = db.session.execute(db.select(User).where(User.username == "joe")).scalar()
    response = client.post("/auth/login", json={"username":user.username, "password": user.password})
    access_token = response.json["access_token"]
    
    #When
    response = client.get("/users/", headers={"Authorization" : f"Bearer {access_token}"})
    
    #Then
    assert response.status_code == HTTPStatus.OK
    assert response.json == {
        "users": [
            {"id":user.id,
             "username": user.username,
             "role": {
                 "id": user.role.id,
                 "name": user.role.name,   
                },
            }  
        ]
    }
    

    