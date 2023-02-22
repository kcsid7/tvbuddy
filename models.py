# Setup Models

from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


db = SQLAlchemy()
bcrypt = Bcrypt()


def connect_db(app):
    db.app = app
    db.init_app(app)


#############################################################

# User's favorite shows

class UserShow(db.Model):
    """ User's favorite Shows """

    __tablename__ = "users_shows"

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    show_id = db.Column(db.Integer, primary_key=True)
    show_name = db.Column(db.Text)
    show_img = db.Column(db.Text)

#############################################################

class UserActor(db.Model):
    """ User's favorite Actors """
    
    __tablename__ = "users_actors"

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"), primary_key=True)
    actor_id = db.Column(db.Integer, primary_key=True)
    actor_name = db.Column(db.Text)
    actor_image = db.Column(db.Text)



#############################################################


class User(db.Model):
    """ User Model """

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    first_name = db.Column(db.String(40), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    image_url = db.Column(db.Text)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    fav_shows = db.relationship('UserShow', backref="users", cascade="all, delete") # Displays the fav shows for user 
    fav_actors = db.relationship('UserActor', backref="users", cascade="all, delete") # Displays the fav actors for user



    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @classmethod
    def register(cls, first_name, last_name, email, username, password):
        """ Registger User (Signup): Returns new user class 
            Hash user provided password and then create new user class
        """
        hashed_pw = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf8) string
        hashed_pw_utf = hashed_pw.decode("utf8")

        new_user = cls(
            first_name = first_name,
            last_name = last_name,
            email = email,
            username = username,
            password = hashed_pw_utf
        )
        return new_user

    @classmethod
    def authenticate(cls, username, password):
        """ Authenticate User (Login): User.authenticate('ursname', 'pwd') 
            Checks for user and if user password matches hashed password returns user
            Otherwise returns false
        """
        
        user = cls.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False


#############################################################

# class Show(db.Model):
#     """ Show Model """

#     __tablename__ = "shows"

#     show_id = db.Column(db.Integer, primary_key=True)
#     show_name = db.Column(db.Text, nullable=False)
#     show_status = db.Column(db.Text)
#     show_image = db.Column(db.Text)
#     show_runtime = db.Column(db.Text)
#     show_length = db.Column(db.Text)

    # user_fav = db.relationship('UserShow', backref="show") # Displays which users have selected show




#############################################################

# class Actor(db.Model):
#     """ Actor Model """

#     __tablename__ = "actors"

#     actor_id = db.Column(db.Integer, primary_key=True)
#     actor_first_name = db.Column(db.Text, nullable=False)
#     actor_last_name = db.Column(db.Text, nullable=False)










