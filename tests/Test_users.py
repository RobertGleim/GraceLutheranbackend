from app import create_app
from app.models import User, db
import unittest
from werkzeug.security import check_password_hash, generate_password_hash
from app.utils.auth import encode_token

class TestUsers(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            self.user = User(
                username="testuser",
                email="testuser@email.com",
                password=generate_password_hash('123'),
                role="customer"
            )
            db.session.add(self.user)
            db.session.commit()
            self.user_token = encode_token(self.user.id, "customer")
            self.mechanic_token = encode_token(self.user.id, "mechanic")
            self.admin_token = encode_token(self.user.id, "admin")

    def test_create_user(self):
        user_payload = {
            "username": "john_doe",
            "email": "john@email.com",
            "password": "123",
            "role": "customer"
        }
        response = self.client.post('/users', json=user_payload)
        self.assertEqual(response.status_code, 201)
        self.assertIn('user', response.json)
        self.assertEqual(response.json['user']['username'], "john_doe")
        self.assertEqual(response.json['user']['email'], "john@email.com")
        self.assertEqual(response.json['user']['role'], "customer")

    def test_invalid_create_user(self):
        user_payload = {
            "username": "jane_doe",
            "email": "invalid-email",
            "password": "123",
            "role": "customer"
        }
        response = self.client.post('/users', json=user_payload)
        self.assertIn('email', response.json)
        self.assertEqual(response.status_code, 400)

    def test_get_users_role_access(self):
        headers = {"Authorization": "Bearer " + self.mechanic_token}
        response = self.client.get('/users', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_get_all_users(self):
        with self.app.app_context():
            user2 = User(
                username="alice",
                email="alice@email.com",
                password=generate_password_hash('abc'),
                role="customer"
            )
            db.session.add(user2)
            db.session.commit()
        headers = {"Authorization": "Bearer " + self.admin_token}
        response = self.client.get('/users', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_update_user_role_access(self):
        update_payload = {
            "username": "jane_doe",
            "email": "newemail@email.com",
            "password": "123",
            "role": "customer"
        }
        headers = {"Authorization": "Bearer " + self.user_token}
        response = self.client.put(f'/users/{self.user.id}', json=update_payload, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_login_user(self):
        login_creds = {
            "email": "testuser@email.com",
            "password": "123"
        }
        response = self.client.post('/users/login', json=login_creds)
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.json)
        self.assertEqual(response.json['user']['email'], "testuser@email.com")

    def test_unauthorized_user(self):
        response = self.client.delete('/users/1')
        self.assertIn(response.status_code, (401, 405))
        # If 401, check for message; if 405, skip message check
        if response.status_code == 401:
            self.assertIn('message', response.json)

if __name__ == "__main__":
    unittest.main()

# class TestAdminUserActions(unittest.TestCase):
#     def setUp(self):
#         self.app = create_app('TestingConfig')
#         self.client = self.app.test_client()
#         with self.app.app_context():
#             db.drop_all()
#             db.create_all()
#             admin = User(
#                 username="admin",
#                 email="admin@email.com",
#                 password=generate_password_hash('adminpass'),
#                 role="admin"
#             )
#             db.session.add(admin)
#             db.session.commit()
#             self.admin_token = encode_token(admin.id, "admin")
#             other = User(
#                 username="target",
#                 email="target@email.com",
#                 password=generate_password_hash('target'),
#                 role="customer"
#             )
#             db.session.add(other)
#             db.session.commit()
#             self.other_id = other.id

    # def test_admin_update_user_by_id(self):
    #     headers = {"Authorization": "Bearer " + self.admin_token}
    #     payload = {"username": "updated", "role": "mechanic"}
    #     response = self.client.put(f"/users/{self.other_id}", json=payload, headers=headers)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertEqual(response.json['username'], 'updated')
    #     self.assertEqual(response.json['role'], 'mechanic')

    # def test_admin_delete_user_by_id(self):
    #     headers = {"Authorization": "Bearer " + self.admin_token}
    #     response = self.client.delete(f"/users/{self.other_id}", headers=headers)
    #     self.assertIn(response.status_code, (200,204))

    # def test_admin_cannot_delete_self(self):
    #     headers = {"Authorization": "Bearer " + self.admin_token}
    #     response = self.client.delete(f"/users/1", headers=headers)
    #     self.assertEqual(response.status_code, 403)
