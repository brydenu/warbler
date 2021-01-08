"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

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


class UserModelTestCase(TestCase):
    """Test model for User."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        # Create user to be used in other tests
        usr = User.signup(
                email="tester@test.com",
                username="setuptester",
                password="password",
                image_url=None
        )
        
        db.session.commit()

        self.set_up_user = usr

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    def test_repr(self):
        """Does the repr work and look like how it should?"""

        usr = User.query.first()
        obj = f'<User #{usr.id}: {usr.username}, {usr.email}>'

        self.assertEqual(obj, str(usr))

    def test_follows(self):
        """Does is_following detect when user1 is and isn't following user2?"""
        
        # Create a second user to interact with the setup user
        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        user1 = User.query.get(self.set_up_user.id)
        user2 = User.query.get(u.id)

        # Confirms that user1 isn't already following user2
        self.assertNotIn(user2, user1.following)
        self.assertNotIn(user1, user2.followers)
        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user2.is_followed_by(user1))

        # Make user1 follow user2
        user1.following.append(user2)
        db.session.commit()

        # Re-pull users from db to get fresh information
        user1 = User.query.get(self.set_up_user.id)
        user2 = User.query.get(u.id)

        self.assertIn(user2, user1.following)
        self.assertIn(user1, user2.followers)
        self.assertTrue(user1.is_following(user2))
        self.assertTrue(user2.is_followed_by(user1))

        # Does unfollowing work?
        user1.following.clear()
        db.session.commit()

        # Get fresh users again
        user1 = User.query.get(self.set_up_user.id)
        user2 = User.query.get(u.id)

        self.assertNotIn(user2, user1.following)
        self.assertNotIn(user1, user2.followers)
        self.assertFalse(user1.is_following(user2))
        self.assertFalse(user2.is_followed_by(user1))


    def test_user_signup(self):
        """Does User.signup work with valid credentials?"""

        # Create a valid new user
        user = User.signup("test_username", 
                            "signup@test.com", 
                            "abc123",
                            "https://cdn.pixabay.com/photo/2017/02/07/16/47/kingfisher-2046453_960_720.jpg"
                            )
        # Checks all fields to make sure user is set up correctly
        self.assertIn(user, User.query.all())
        self.assertEqual(user.username, "test_username")
        self.assertEqual(user.email, "signup@test.com")
        self.assertNotEqual(user.password, "abc123")
        self.assertTrue(user.password.startswith("$2b$"))


    def test_invalid_user_signup(self):
        """User.signup should not work with non unique
         information or non-nullable fields not filled out"""

         # Create user using same username as setup username (should be invalid)
        user = User.signup("setuptester",
                            "email@email.com",
                            "abc123",
                            "https://cdn.pixabay.com/photo/2017/02/07/16/47/kingfisher-2046453_960_720.jpg"
                            )
        
        # Should raise an error
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_authenticate(self):
        """Does User.authenticate successfully return a user 
        when given a valid username and password?"""

        # Assigns user with the authentication of a user with the setup
        # information and password
        user = User.authenticate(self.set_up_user.username, "password")

        # Verifies that the user object is what we want
        self.assertTrue(user)
        self.assertEqual(user.username, "setuptester")
        self.assertEqual(user.email, "tester@test.com")


    def test_invalid_username(self):
        """Does User.authenticate successfully deny access without good username?"""

        self.assertFalse(User.authenticate("not_a_username", "password"))


    def test_invalid_password(self):
        """Does User.authenticate successfully deny access without correct password?"""

        self.assertFalse(User.authenticate("setuptester", "blahblahblah"))

        


        


