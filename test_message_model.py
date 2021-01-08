"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Likes

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    """Test model for Message"""

    def setUp(self):
        """Create test clients, test messages"""

        User.query.delete()
        Message.query.delete()
        Likes.query.delete()

        # Create 2 users to be used in tests
        user1 = User.signup(
                            email="test1@test.com",
                            username="testuser1",
                            password="password1",
                            image_url=None
        )
        u1id = 111111
        user1.id = u1id

        user2 = User.signup(
                            email="test2@test.com",
                            username="testuser2",
                            password="password2",
                            image_url=None
        )
        u2id = 222222
        user2.id = u2id

        db.session.commit()

        self.user1 = User.query.get(user1.id)
        self.user2 = User.query.get(user2.id)

        # Create 1 message for each user to start with
        msg1 = Message(text="this message is from user1", user_id=self.user1.id)
        m1id = 11111
        msg1.id = m1id
        msg2 = Message(text="message from user2 is this one", user_id=self.user2.id)
        m2id = 22222
        msg2.id = m2id

        db.session.add(msg1)
        db.session.add(msg2)
        db.session.commit()
        
        self.msg1 = msg1
        self.msg2 = msg2

        self.client = app.test_client()

    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_message_model(self):
        """Does basic model work?"""

        m = Message(text="testing message abc123", user_id=self.user1.id)

        db.session.add(m)
        db.session.commit()
        
        self.assertEqual(len(self.user1.messages), 2)
        self.assertIn(m, self.user1.messages)

    def test_repr(self):
        """Does the repr work and look like how it should?"""

        msg = Message.query.first()
        obj = f'<Message {msg.id}>'

        self.assertEqual(obj, str(msg))

    def test_likes(self):
        """Tests counter on likes on each message"""

        # Makes sure there are no likes already on each message
        msg1_likes = Likes.query.filter(Likes.message_id == self.msg1.id).all()
        msg2_likes = Likes.query.filter(Likes.message_id == self.msg2.id).all()

        self.assertEqual(len(msg1_likes), 0)
        self.assertEqual(len(msg2_likes), 0)

        # Adds 1 like to each msg
        self.user1.likes.append(self.msg2)
        self.user2.likes.append(self.msg1)

        db.session.commit()

        msg1_likes = Likes.query.filter(Likes.message_id == self.msg1.id).all()
        msg2_likes = Likes.query.filter(Likes.message_id == self.msg2.id).all()

        self.assertEqual(len(msg1_likes), 1)
        self.assertEqual(len(msg2_likes), 1)

        # Removes a like from msg1
        self.user2.likes.clear()
        db.session.commit()

        msg1_likes = Likes.query.filter(Likes.message_id == self.msg1.id).all()
        msg2_likes = Likes.query.filter(Likes.message_id == self.msg2.id).all()

        self.assertEqual(len(msg1_likes), 0)
        self.assertEqual(len(msg2_likes), 1)








