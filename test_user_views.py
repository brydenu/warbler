"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewsTestCase(TestCase):
    """Test views for user"""

    def setUp(self):
        
        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

        self.user1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="password1",
                                    image_url=None
                                    )

        self.user1_id = 111111
        self.user1.id = self.user1_id

        self.user2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="password2",
                                    image_url=None
                                    )

        self.user2_id = 222222
        self.user2.id = self.user2_id

        self.user3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="password3",
                                    image_url=None
                                    )

        self.user3_id = 333333
        self.user3.id = self.user3_id

        db.session.commit()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_list_users(self):
        """Does view return page showing all users?"""
        with self.client as c:

            resp = c.get("/users")

            html = resp.get_data(as_text=True)

            self.assertIn("@testuser1", html)
            self.assertIn("@testuser2", html)
            self.assertIn("@testuser3", html)

    def test_users_show(self):
        """Does the view show a specific user profile?"""

        # Create a message from user1 to make sure messages show up
        msg = Message(text="message abcdefg", user_id=self.user1.id)
        db.session.add(msg)
        db.session.commit()

        with self.client as c:

            resp = c.get("/users/111111")
            html = resp.get_data(as_text=True)

            self.assertIn("@testuser1", html)
            self.assertIn('message abcdefg', html)
        
    def test_show_following(self):
        """Can you see who a user follows?"""

        # user2 will follow user1 and user3 to be checked
        usr2 = self.user2
        usr2.following.append(self.user1)
        usr2.following.append(self.user3)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            resp = c.get("/users/222222/following")
            html = resp.get_data(as_text=True)

            # Check if other two users added earlier are in user2's following
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", html)
            self.assertIn("@testuser3", html)

    def test_logged_out_following(self):
        """Are you prevented from seeing who someone follows if you aren't logged on?"""
        with self.client as c:
            
            resp = c.get("/users/222222/following")
            
            # Should redirect
            self.assertEqual(resp.status_code, 302)

    def test_show_followers(self):
        """Can you see who is following a user?"""

        # User2 will be followed by user1 and user3 to be checked
        self.user1.following.append(self.user2)
        self.user3.following.append(self.user2)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            resp = c.get("/users/222222/followers")
            html = resp.get_data(as_text=True)

            # Check if user2 has 2 followers and they show up on their followers page
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", html)
            self.assertIn("@testuser2", html)

    def test_logged_out_followers(self):
        """Are you prevented from seeing someone's followers if you aren't logged on?"""
        with self.client as c:
            
            resp = c.get("/users/222222/followers")
            
            # Should redirect
            self.assertEqual(resp.status_code, 302)

        


        

            
    





        
