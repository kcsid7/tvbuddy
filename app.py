import requests

from flask import Flask, render_template, request, flash, redirect, session, make_response
from flask_debugtoolbar import DebugToolbarExtension
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

from models import db, connect_db, User, UserShow, UserActor
from forms import UserSignupForm, UserSigninForm, UserEditForm


app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///tvbuddy'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = "tv*BU_dS3c_Re_T_Key__"

toolbar = DebugToolbarExtension(app)

connect_db(app)


API_URL = 'https://api.tvmaze.com/'

def create_db_func():
    with app.app_context():
        db.create_all()


@app.route("/")
def root_route():
    """ Root Route """

    # return render_template("home.html", users=all_users)
    return redirect("/tvbuddy")



# USER ROUTES

@app.route("/users")
def users_route():
    """ Shows Route """

    if "username" not in session:
        flash(f"Unauthorized Access! Please Login", "warning")
        return redirect(f"/user/login")

    users = User.query.all()
    return render_template("/user/all.html", users=users)

@app.route("/user/signup", methods=["GET", "POST"])
def user_signup_form():
    """ Get User Signup Form"""

    if "username" in session:
        flash(f"{session['username']} is logged in! Please logout to register new user!", "warning")
        return redirect(f"/users/{session['username']}")

    form = UserSignupForm()

    try:
        if form.validate_on_submit():
            new_user = User.register(
                form.first_name.data,
                form.last_name.data,
                form.email.data,
                form.username.data,
                form.password.data
            )

            db.session.add(new_user)
            db.session.commit()
            session["username"] = new_user.username
            session["userid"] = new_user.user_id

            flash(f"Added {new_user.first_name} as {new_user.username}", "success")
            resp = make_response(redirect("/"))
            resp.set_cookie("user_login", "true")
            return resp
        else:
            return render_template("/user/signup.html", form=form)

    except IntegrityError as e:
        msg = e._message()
        err_msg = msg[(msg.find('DETAIL') + 13):]
        db.session.rollback()

        flash(f"User already exists! {err_msg}", "warning")
        return render_template("/user/signup.html", form=form)




@app.route("/user/login", methods=["GET", "POST"])
def user_login_form():
    """ Login User 
        Add user to session if user successfully authenticates
    """
    if "username" in session:
        flash(f"{session['username']} is already logged in!", "warning")
        return redirect(f"/users/{session['username']}")

    form = UserSigninForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            session["username"] = user.username
            session["userid"] = user.user_id
            flash(f"Hello {user.username}! Welcome Back!", "success")

            resp = make_response(redirect(f"/"))
            resp.set_cookie("user_login", "true")
            return resp
        else:
            flash(f"Invalid username and password combination! Try again!", "danger")
            return redirect("/user/login")
    else:
        return render_template("/user/login.html", form=form)


@app.route("/users/<username>/logout", methods=["POST"])
def logout_user(username):
    """ Logout User 
    """
    if "username" not in session:
        flash(f"Unauthorized Access! Please Login", "warning")
        return redirect(f"/user/login")

    if session["username"] != username:
        flash(f"Unauthorized Access! Please Login", "warning")
        return redirect(f"/")

    session.pop("username")
    session.pop("userid")
    
    flash(f"Logged Out", "primary")

    resp = make_response(redirect("/"))
    resp.set_cookie("user_login", "", expires=0)

    return resp


@app.route("/user/<username>")
def user_profile(username):
    """ User Profile Page """

    if "username" not in session:
        flash(f"Unauthorized Access! Please Login", "warning")
        return redirect(f"/user/login")

    if session["username"] != username:
        flash(f"Unauthorized Access!", "warning")
        return redirect(f"/")

    user = User.query.get(session['userid'])

    return render_template("/user/profile.html", user=user)


@app.route("/user/<username>/edit", methods=["GET", "POST"])
def edit_user(username):
    
    if "username" not in session:
        flash(f"Unauthorized Access! Please Login", "warning")
        return redirect(f"/user/login")

    if session["username"] != username:
        flash(f"Unauthorized Access!", "warning")
        return redirect(f"/")

    form = UserEditForm()
    user = User.query.get(session['userid'])

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data
        user.image_url = form.image_url.data

        db.session.add(user)
        db.session.commit()

        flash(f"{user.username} updated!", "success")
        return redirect(f"/user/{user.username}")

    form.first_name.data = user.first_name
    form.last_name.data = user.last_name
    form.email.data = user.email
    form.image_url.data = user.image_url

    return render_template("/user/edit.html", form=form, user=user)


@app.route("/user/<username>/delete", methods=["POST"])
def delete_user(username):
    """ Delete Selected User """

    if "username" not in session:
        flash(f"Unauthorized Access! Please Login", "warning")
        return redirect(f"/user/login")

    if session["username"] != username:
        flash(f"Unauthorized Access!", "warning")
        return redirect(f"/")

    user = User.query.get(session['userid'])

    db.session.delete(user)
    db.session.commit()

    session.pop("username")
    session.pop("userid")

    flash(f"{user.username} deleted!", "danger")
    resp = make_response(redirect("/"))
    resp.set_cookie("user_login", "", expires=0)
    return resp


# TV Buddy App

@app.route("/tvbuddy")
def tv_buddy():

    """ Serve the tvBuddy File 
        When user is not logged in, it displays the tvBuddy form where the unsigned user can browse but not save any information
        When the user is logged in, the interface allows the user to store favorite shows
    """

    return render_template("/tvBuddy/index.html")


@app.route("/tvbuddy/shows/<int:show_id>")
@app.route("/tvbuddy/shows/<int:show_id>/<castlist>")
def get_tv_episodes(show_id, castlist=None):
    """ Gets the list of shows """

    if "username" not in session:
        flash(f"Unauthorized Access! Please Login", "warning")
        return redirect(f"/user/login")

    user = User.query.get(session['userid'])

    favShow = False

    if user.fav_shows:
        for show in user.fav_shows:
            if show.show_id == show_id:
                favShow = True

    if castlist:
        redirect_cast = True
    else:
        redirect_cast = False

    user_fav_actors = [ actor.actor_id for actor in user.fav_actors ]
    
    
    res = requests.get(f"https://api.tvmaze.com/shows/{show_id}")
    data = res.json()

    cast_info = requests.get(f"https://api.tvmaze.com/shows/{show_id}/cast")
    cast_data = cast_info.json()


    return render_template("/tvBuddy/episodes.html", data=data, favShow=favShow, cast_data=cast_data, redirect_cast=redirect_cast, user_fav_actors=user_fav_actors)


@app.route("/tvbuddy/shows/<int:show_id>/save", methods=["POST"])
def save_user_fav_show(show_id):
    """ Save User's Fav Show """

    if "username" not in session:
        flash(f"Unauthorized Access! Please Login", "warning")
        return redirect(f"/user/login")

    user = User.query.get(session['userid'])

    # Remove show from favorites if it's already there
    if user.fav_shows:
        for show in user.fav_shows:
            if show.show_id == show_id:
                usershow = UserShow.query.get((session['userid'], show_id))

                db.session.delete(usershow)
                db.session.commit()
                return redirect(f"/tvbuddy/shows/{show_id}")
            
    new_usershow = UserShow(
        user_id = user.user_id,
        show_id = show_id,
        show_name = request.form['showname'],
        show_img = request.form['showimage']
    )
    db.session.add(new_usershow)
    db.session.commit()

    return redirect(f"/tvbuddy/shows/{show_id}")


@app.route("/users/actors/<int:actorid>/save", methods=["POST"])
def save_user_fav_actor(actorid):
    """ Save User's Fav Actor """

    showid = request.form['showid']

    if "username" not in session:
        flash(f"Unauthorized Access! Please Login", "warning")
        return redirect(f"/user/login")

    user = User.query.get(session['userid'])

    # Remove actor from favorites if already in the list
    if user.fav_actors:
        for actor in user.fav_actors:
            if actor.actor_id == actorid:
                useractor = UserActor.query.get((session['userid'], actorid))

                db.session.delete(useractor)
                db.session.commit()
                return redirect(f"/tvbuddy/shows/{showid}/cast")

    new_useractor = UserActor(
        user_id = user.user_id,
        actor_id = actorid,
        actor_name = request.form['actorname'],
        actor_image = request.form['actorimg']
    )

    db.session.add(new_useractor)
    db.session.commit()

    return redirect(f"/tvbuddy/shows/{showid}/cast")


@app.route("/user/<int:user_id>/<int:resource_id>/delete/", methods=["POST"])
@app.route("/user/<int:user_id>/<int:resource_id>/delete/<actor>", methods=["POST"])
def delete_user_favs(user_id, resource_id, actor=None):
    """ Remove User's Fav Resources """

    if (actor):
        useractor = UserActor.query.get_or_404((user_id, resource_id))
        db.session.delete(useractor)
        db.session.commit()
        return redirect(f"/user/{session['username']}")
    
    usershow = UserShow.query.get_or_404((user_id, resource_id))
    db.session.delete(usershow)
    db.session.commit()
    return redirect(f"/user/{session['username']}")


@app.route("/<path:u_path>")
def catch_all(u_path):
    """ Catch all Route """

    return render_template("/notfound.html")

















