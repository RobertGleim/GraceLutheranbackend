from app import create_app
from app.models import User, PastorMessage, db
import unittest
from werkzeug.security import generate_password_hash
from app.utils.auth import encode_token


class TestPastorMessages(unittest.TestCase):

    def setUp(self):
        self.app = create_app('TestingConfig')
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            
            # Create admin user
            self.admin_user = User(
                username="admin",
                email="admin@email.com",
                password=generate_password_hash('admin123'),
                role="admin"
            )
            db.session.add(self.admin_user)
            
            # Create regular user
            self.regular_user = User(
                username="user",
                email="user@email.com",
                password=generate_password_hash('user123'),
                role="user"
            )
            db.session.add(self.regular_user)
            db.session.commit()
            
            self.admin_token = encode_token(self.admin_user.id, "admin")
            self.user_token = encode_token(self.regular_user.id, "user")

    def test_create_pastor_message_as_admin(self):
        """Test that admin can create a pastor message"""
        message_payload = {
            "title": "Welcome Message",
            "message": "Welcome to our church!",
            "is_active": True
        }
        headers = {"Authorization": "Bearer " + self.admin_token}
        response = self.client.post('/pastor-messages', json=message_payload, headers=headers)
        
        self.assertEqual(response.status_code, 201)
        self.assertIn('data', response.json)
        self.assertEqual(response.json['data']['title'], "Welcome Message")
        self.assertEqual(response.json['data']['message'], "Welcome to our church!")
        self.assertTrue(response.json['data']['is_active'])

    def test_create_pastor_message_as_non_admin(self):
        """Test that non-admin cannot create a pastor message"""
        message_payload = {
            "title": "Unauthorized Message",
            "message": "This should fail",
            "is_active": True
        }
        headers = {"Authorization": "Bearer " + self.user_token}
        response = self.client.post('/pastor-messages', json=message_payload, headers=headers)
        
        self.assertEqual(response.status_code, 403)

    def test_get_all_messages_as_admin(self):
        """Test that admin can get all pastor messages"""
        with self.app.app_context():
            msg1 = PastorMessage(title="Message 1", message="Content 1", is_active=True)
            msg2 = PastorMessage(title="Message 2", message="Content 2", is_active=False)
            db.session.add(msg1)
            db.session.add(msg2)
            db.session.commit()
        
        headers = {"Authorization": "Bearer " + self.admin_token}
        response = self.client.get('/pastor-messages', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 2)

    def test_get_active_message_public(self):
        """Test that anyone can get the active pastor message"""
        with self.app.app_context():
            msg = PastorMessage(title="Active Message", message="This is active", is_active=True)
            db.session.add(msg)
            db.session.commit()
        
        response = self.client.get('/pastor-messages/active')
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['title'], "Active Message")
        self.assertTrue(response.json['is_active'])

    def test_get_active_message_when_none_active(self):
        """Test getting active message when none exists"""
        response = self.client.get('/pastor-messages/active')
        
        self.assertEqual(response.status_code, 404)
        self.assertIn('message', response.json)

    def test_update_pastor_message_as_admin(self):
        """Test that admin can update a pastor message"""
        with self.app.app_context():
            msg = PastorMessage(title="Old Title", message="Old message", is_active=False)
            db.session.add(msg)
            db.session.commit()
            msg_id = msg.id
        
        update_payload = {
            "title": "Updated Title",
            "message": "Updated message",
            "is_active": True
        }
        headers = {"Authorization": "Bearer " + self.admin_token}
        response = self.client.put(f'/pastor-messages/{msg_id}', json=update_payload, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['data']['title'], "Updated Title")
        self.assertEqual(response.json['data']['message'], "Updated message")

    def test_update_nonexistent_message(self):
        """Test updating a message that doesn't exist"""
        update_payload = {
            "title": "Updated Title",
            "message": "Updated message"
        }
        headers = {"Authorization": "Bearer " + self.admin_token}
        response = self.client.put('/pastor-messages/999', json=update_payload, headers=headers)
        
        self.assertEqual(response.status_code, 404)

    def test_delete_pastor_message_as_admin(self):
        """Test that admin can delete a pastor message"""
        with self.app.app_context():
            msg = PastorMessage(title="To Delete", message="Delete me", is_active=False)
            db.session.add(msg)
            db.session.commit()
            msg_id = msg.id
        
        headers = {"Authorization": "Bearer " + self.admin_token}
        response = self.client.delete(f'/pastor-messages/{msg_id}', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('deleted', response.json['message'].lower())

    def test_delete_pastor_message_as_non_admin(self):
        """Test that non-admin cannot delete a pastor message"""
        with self.app.app_context():
            msg = PastorMessage(title="Protected", message="Can't delete", is_active=False)
            db.session.add(msg)
            db.session.commit()
            msg_id = msg.id
        
        headers = {"Authorization": "Bearer " + self.user_token}
        response = self.client.delete(f'/pastor-messages/{msg_id}', headers=headers)
        
        self.assertEqual(response.status_code, 403)

    def test_activate_pastor_message(self):
        """Test activating a specific pastor message"""
        with self.app.app_context():
            msg1 = PastorMessage(title="Message 1", message="Content 1", is_active=True)
            msg2 = PastorMessage(title="Message 2", message="Content 2", is_active=False)
            db.session.add(msg1)
            db.session.add(msg2)
            db.session.commit()
            msg2_id = msg2.id
        
        headers = {"Authorization": "Bearer " + self.admin_token}
        response = self.client.patch(f'/pastor-messages/{msg2_id}/activate', headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json['data']['is_active'])
        
        # Verify only one message is active
        with self.app.app_context():
            active_messages = db.session.query(PastorMessage).filter_by(is_active=True).all()
            self.assertEqual(len(active_messages), 1)
            self.assertEqual(active_messages[0].id, msg2_id)

    def test_create_active_message_deactivates_others(self):
        """Test that creating an active message deactivates all others"""
        with self.app.app_context():
            msg1 = PastorMessage(title="Message 1", message="Content 1", is_active=True)
            db.session.add(msg1)
            db.session.commit()
        
        message_payload = {
            "title": "New Active Message",
            "message": "This should be the only active one",
            "is_active": True
        }
        headers = {"Authorization": "Bearer " + self.admin_token}
        response = self.client.post('/pastor-messages', json=message_payload, headers=headers)
        
        self.assertEqual(response.status_code, 201)
        
        # Verify only one message is active
        with self.app.app_context():
            active_messages = db.session.query(PastorMessage).filter_by(is_active=True).all()
            self.assertEqual(len(active_messages), 1)
            self.assertEqual(active_messages[0].title, "New Active Message")


if __name__ == "__main__":
    unittest.main()
