import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
from functions import login_required, apology, allowed_file, makeGraph
from werkzeug.utils import secure_filename
# Configure application
app = Flask(__name__)

# Select folder and types of photos which will be send by users.
UPLOAD_FOLDER = 'static/photos/users'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#join database
db = SQL("sqlite:///database.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


#Main site
@app.route("/", methods=["GET","POST"])
@login_required
def index():
    if request.method=="GET":
        checkboxes=["Normal", "Donate","Help"]
        users_help = db.execute("SELECT name, photo, posts.id FROM users JOIN posts ON posts.user_help_id = users.id;")
        comments = db.execute("SELECT user_id, post_id, content, date, users.photo as photo, users.name as name FROM comments JOIN users ON users.id = user_id ORDER BY date DESC;")
        rows = db.execute("SELECT posts.id, posts.topic, posts.description, posts.type, posts.request_money, posts.received_money, posts.user_help_id, posts.date, users.name as user_name, users.id as user_id, users.photo as photo, CASE WHEN (SELECT isPositive FROM likes WHERE post_id = posts.id AND user_id = ? LIMIT 1) = 1 THEN 1 WHEN (SELECT isPositive FROM likes WHERE post_id = posts.id AND user_id = ? LIMIT 1) = 0 THEN 0 ELSE 2 END AS isLiked, SUM(CASE WHEN likes.isPositive = 1 THEN 1 ELSE 0 END) AS likes, SUM(CASE WHEN likes.isPositive = 0 THEN 1 ELSE 0 END) AS dislikes FROM posts JOIN users on posts.user_id = users.id LEFT JOIN likes on posts.id = likes.post_id GROUP BY posts.id ORDER BY date DESC", session["user_id"], session["user_id"])
        messageBox = session.pop('messageBox', None)
        if messageBox == None:
            messageBox = ''
        return render_template("index.html", posts = rows, comments = comments, users_help = users_help, checkboxes = checkboxes, messageBox = messageBox)
    elif request.method == "POST":
        comments = db.execute("SELECT user_id, post_id, content, date, users.photo as photo, users.name as name FROM comments JOIN users ON users.id = user_id ORDER BY date DESC;")
        userName = ""
        users_help = db.execute("SELECT name, photo, posts.id FROM users JOIN posts ON posts.user_help_id = users.id;")

        #make custom question based on chosen options
        sortOrder = "posts.date DESC"
        if request.form.get("SortBy") == "likes":
            sortOrder = "like_count DESC"
        if request.form.get("searchPersonList") != "showAll":
            userName = "WHERE users.name = '" + request.form.get("searchPersonList") + "'"
        checkboxes = []
        if request.form.get("normal"):
            checkboxes.append("Normal")
        if request.form.get("donate"):
            checkboxes.append("Donate")
        if request.form.get("help"):
            checkboxes.append("Help")
        if not checkboxes:
            checkboxes=["Normal", "Donate","Help"]

        question = "SELECT posts.id, posts.topic, posts.description, posts.type, posts.request_money, posts.received_money, posts.user_help_id, posts.date, users.name as user_name, users.id as user_id, users.photo as photo, CASE WHEN (SELECT isPositive FROM likes WHERE post_id = posts.id AND user_id = " + str(session["user_id"]) + " LIMIT 1) = 1 THEN 1 WHEN (SELECT isPositive FROM likes WHERE post_id = posts.id AND user_id = " + str(session["user_id"]) + " LIMIT 1) = 0 THEN 0 ELSE 2 END AS isLiked, SUM(CASE WHEN likes.isPositive = 1 THEN 1 ELSE 0 END) - SUM(CASE WHEN likes.isPositive = 0 THEN 1 ELSE 0 END) AS like_count, SUM(CASE WHEN likes.isPositive = 1 THEN 1 ELSE 0 END) AS likes, SUM(CASE WHEN likes.isPositive = 0 THEN 1 ELSE 0 END) AS dislikes FROM posts JOIN users on posts.user_id = users.id LEFT JOIN likes on posts.id = likes.post_id "+userName+" GROUP BY posts.id ORDER BY " +sortOrder
        rows = db.execute(question)
        return render_template("index.html", posts = rows, comments=comments, users_help = users_help, checkboxes = checkboxes)

#adding comment to post
@app.route("/addComment", methods=["POST"])
@login_required
def addComment():
    text = request.form.get("commentArea")
    postId = request.form.get("commentedPostId")
    if text == "":
        return apology("Comment can't be empty")
    db.execute("INSERT INTO comments (user_id, post_id, content, date) values(?, ?, ?, ?)", session["user_id"], postId, text, datetime.now())
    session['messageBox'] = "Comment has been written."
    return redirect("/")

#declare help for post
@app.route("/help", methods=["POST"])
@login_required
def help():
    post_id = request.form.get("help_post_id")
    db.execute("UPDATE posts SET user_help_id = ? WHERE posts.id = ?", session["user_id"], post_id)
    session['messageBox'] = "The declaration of help has been sent"
    return redirect("/")

#send donate for donate post
@app.route("/sendDonate", methods=["POST"])
@login_required
def sendDonate():
    post_id = request.form.get("donatePostId")
    try:
        donate = int(request.form.get("donateAmmount"))
    except ValueError as e:
        return apology("Your donate must be a positive number")
    if donate < 1:
        return apology("Your donate must be a positive number")

    #change users balance
    rows = db.execute("SELECT balance from money WHERE user_id = ?", session["user_id"])
    if rows[0]["balance"] < donate:
        return apology("Your balance is too low")
    else:
        db.execute("UPDATE posts SET received_money = received_money + ? WHERE id = ?", donate, post_id)
        db.execute("UPDATE money SET donated = donated + ?, balance = balance - ? WHERE user_id = ?", donate, donate, session["user_id"])
        db.execute("UPDATE money SET received = received + ?, balance = balance + ? WHERE user_id = (SELECT user_id FROM posts WHERE id=? )", donate, donate, post_id)
        session['messageBox'] = "Donate has been sent"
        return redirect("/")

#live searching users by typing text
@app.route("/livesearch", methods=["POST"])
def livesearch():
    searchbox = request.form.get("text")
    rows = db.execute("SELECT name FROM users WHERE name LIKE ? ORDER BY name LIMIT 3", (searchbox + '%'))
    result = [{'name': row["name"]} for row in rows]
    return jsonify(result)


@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")
#changing user's balance
@app.route("/manageMoney", methods=["GET","POST"])
@login_required
def manageMoney():
    rows = db.execute("SELECT balance FROM money WHERE user_id = ?", session["user_id"]);
    actualBalance = int(rows[0]["balance"])
    if request.method == "GET":
        return render_template("manageMoney.html", actualBalance = actualBalance)
    else:
        try:
            moneyToManage = int(request.form.get("moneyToManage"))
        except ValueError as e:
            return apology("Money to manage must be a positive number")
        if moneyToManage < 1:
            return apology("Money to manage must be a positive number")
        if request.form.get("moneyBtn") == "deposit":
            db.execute("UPDATE money SET balance = balance + ? WHERE user_id = ?", moneyToManage, session["user_id"])
        elif request.form.get("moneyBtn") == "withdraw":
            if actualBalance < moneyToManage:
                return apology("You don't have that ammount of money")
            else:
                db.execute("UPDATE money SET balance = balance - ? WHERE user_id = ?", moneyToManage, session["user_id"])
        rows = db.execute("SELECT balance FROM money WHERE user_id = ?", session["user_id"]);
        actualBalance = int(rows[0]["balance"])
        messageBox = "Your balance has been updated"
        return render_template("manageMoney.html", messageBox=messageBox, actualBalance = actualBalance)

#edit user's data
@app.route("/editProfile", methods=["GET","POST"])
@login_required
def editProfile():
    money = db.execute("SELECT donated, received FROM money WHERE user_id=?", session["user_id"])
    donated = int(money[0]["donated"])
    received = int(money[0]["received"])
    makeGraph(donated, received)
    if request.method=="GET":
        rows = db.execute("SELECT id, topic, description, date FROM posts WHERE user_id = ?", session["user_id"])
        messageBox = session.pop('messageBox', None)
        if messageBox == None:
            messageBox = ''
        return render_template("editProfile.html", messageBox = messageBox, posts=rows, received = received, donated=donated)
    if request.method=="POST":
        name = request.form.get("name")
        if name != session['name'] and name:
            data = db.execute("SELECT name FROM users WHERE name=?;", name)
            if len(data) == 1:
                return apology("The user with this name already exists.")
            db.execute("UPDATE users SET name = ? WHERE id = ?", name, session["user_id"])
            session["name"] = name
            imageRows = db.execute("SELECT photo FROM users WHERE id=?", session["user_id"])
            image = imageRows[0]["photo"]
            if image != "basic.jpg":
                extansion = image.split('.')
                fileName = name + '.' + extansion[1]
                os.rename(os.path.join('static/photos/users', image), os.path.join('static/photos/users', fileName))
                db.execute("UPDATE users SET photo = ? WHERE id = ?", fileName, session["user_id"])
                session["photo"] = fileName
        currentPassword = request.form.get("currentPassword")
        newPassword = request.form.get("newPassword")
        if currentPassword != '' or newPassword != '':
            password = db.execute("SELECT password FROM users WHERE id=?", session["user_id"])
            if not check_password_hash(password[0]["password"], currentPassword):
                return apology("The current password is wrong.")
            if newPassword == '':
                return apology("New password can't be empty.")
            db.execute("UPDATE users SET password = ? WHERE id = ?", generate_password_hash(newPassword), session["user_id"])
        image = request.files["imgInput"]
        if image:
            if allowed_file(image.filename) in ALLOWED_EXTENSIONS:
                os.remove("static/photos/users" + session["photo"])
                image.filename = session["name"] + "." + allowed_file(image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
                image.save(filepath)
                session["photo"] = image.filename
                db.execute("UPDATE users SET photo = ? WHERE id = ?", image.filename, session["user_id"])
            else:
                return apology("Wrong type of file.")
        rows = db.execute("SELECT id, topic, description, date FROM posts WHERE user_id = ?", session["user_id"])
        messageBox = "Your profile has been updated"
        return render_template("editProfile.html", posts=rows, messageBox=messageBox, received = received, donated=donated)

#Like and dislike system under every post
@app.route("/likeDislike", methods=["POST"])
def likeDislike():
    post_id = request.form.get("post_id")
    rows = db.execute("SELECT * FROM likes WHERE post_id = ? AND user_id = ?", post_id, session["user_id"])
    #logic to don't let user to send more than one
    if request.form.get("like") == "true":
        if len(rows) == 0:
            db.execute("INSERT INTO likes (user_id, post_id, isPositive) values (?, ?, 1)",session["user_id"], post_id)
            return "like"
        elif rows[0]["isPositive"] == 0:
            db.execute("DELETE FROM likes WHERE user_id == ? AND post_id == ?",session["user_id"], post_id)
            db.execute("INSERT INTO likes (user_id, post_id, isPositive) values (?, ?, 1)",session["user_id"], post_id)
            return "dislikeToLike"
        else:
            db.execute("DELETE FROM likes WHERE user_id == ? AND post_id == ?",session["user_id"], post_id)
            return "unLike"
    else:
        if len(rows) == 0:
            db.execute("INSERT INTO likes (user_id, post_id, isPositive) values (?, ?, 0)",session["user_id"], post_id)
            return "dislike"
        elif rows[0]["isPositive"] == 1:
            db.execute("DELETE FROM likes WHERE user_id == ? AND post_id == ?",session["user_id"], post_id)
            db.execute("INSERT INTO likes (user_id, post_id, isPositive) values (?, ?, 0)",session["user_id"], post_id)
            return "likeToDislike"
        else:
            db.execute("DELETE FROM likes WHERE user_id == ? AND post_id == ?",session["user_id"], post_id)
            return "unDislike"

#Making 3 different type of posts
@app.route("/addPost", methods=["GET","POST"])
@login_required
def addPost():
    postTypes = {"Donate", "Normal", "Help"}
    if request.method=="GET":
        return render_template("addPost.html", postTypes = postTypes)
    elif request.method == "POST":
        if not request.form.get("title"):
            return apology("must provide title")
        if not request.form.get("description"):
            return apology("must provide description")
        if not request.form.get("postTypes") in postTypes:
            return apology("Incorrect type of post")
        if request.form.get("postTypes") == "Donate":
            try:
                donate = int(request.form.get("goal"))
            except ValueError as e:
                return apology("Goal is not a number")
        if request.form.get("postTypes") == "Donate" and int(request.form.get("goal")) < 1:
           return apology("Value of goal must be higher than 1$")
        session['messageBox'] = "Your post has been sent"
        if request.form.get("postTypes") == "Donate":
            db.execute("INSERT INTO posts (user_id, topic, description, type, request_money, received_money, date) values (?, ?, ?, ?, ?, ?, ?)", session["user_id"], request.form.get("title"), request.form.get("description"), request.form.get("postTypes"), request.form.get("goal"), 0, datetime.now())
            return redirect("/")
        if request.form.get("postTypes") == "Normal":
            db.execute("INSERT INTO posts (user_id, topic, description, type, date) values (?, ?, ?, ?, ?)", session["user_id"], request.form.get("title"), request.form.get("description"), request.form.get("postTypes"), datetime.now())
            return redirect("/")
        if request.form.get("postTypes") == "Help":
            db.execute("INSERT INTO posts (user_id, topic, description, type, date) values (?, ?, ?, ?, ?)", session["user_id"], request.form.get("title"), request.form.get("description"), request.form.get("postTypes"), datetime.now())
            return redirect("/")

#edit title and description of your post from editProfile
@app.route("/editPost", methods=["POST"])
@login_required
def editPost():
    if request.form.get("submit") == "editBtn":
        post_id = request.form.get("post_id")
        rows = db.execute("SELECT topic, description FROM posts WHERE id = ?", post_id)
        title = rows[0]["topic"]
        description = rows[0]["description"]
        return render_template("editPost.html", title= title, description = description, id=post_id)
    elif request.form.get("submit") == "saveBtn":
        if not request.form.get("title"):
            return apology("must provide title")
        if not request.form.get("description"):
            return apology("must provide description")
        post_id = request.form.get("post_id")
        title = request.form.get("title")
        description = request.form.get("description")
        rows = db.execute("SELECT id FROM posts WHERE user_id = ?", session["user_id"])
        for row in rows:
            if int(row["id"]) == int(post_id):
                db.execute("UPDATE posts set topic=?, description = ? WHERE id = ?", title, description, post_id)
                session['messageBox'] = "Your post has been edited"
                return redirect("/editProfile")
        return apology("You don't have permission for this post, hacker")
    else:
        return apology("Wrong method to enter the site")

#Delete your post from editPost
@app.route("/deletePost", methods=["POST"])
@login_required
def deletePost():
    post_id = request.form.get("post_id")
    rows = db.execute("SELECT id FROM posts WHERE user_id = ?", session["user_id"])
    for row in rows:
        if int(row["id"]) == int(post_id):
            db.execute("DELETE FROM comments WHERE post_id = ?;", post_id)
            db.execute("DELETE FROM likes WHERE post_id = ?;", post_id)
            db.execute("DELETE FROM posts WHERE id = ?;", post_id)
            session['messageBox'] = "Your post has been deleted"
            return redirect("/editProfile")
    return apology("You don't have permission for this post, hacker")

#Login when there is no user or clicked logout
@app.route("/login", methods=["GET","POST"])
def login():
    messageBox = session.get('messageBox', '')
    session.clear()
    if request.method=="GET":
        return render_template("login.html", messageBox = messageBox)
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("must provide username")
        elif not request.form.get("password"):
            return apology("must provide password")
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("name"))
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password")
        #set session data
        session["user_id"] = rows[0]["id"]
        session["name"] = rows[0]["name"]
        session["photo"] = rows[0]["photo"]
        session['messageBox'] = "You've just log-in!"
        return redirect("/")

#simple logout
@app.route("/logout")
def logout():
    session.clear()
    session['messageBox'] = "You've just log-out!"
    return redirect("/")

#Add new user with optional photo
@app.route("/register", methods=["GET","POST"])
def register():
    session.clear()
    if request.method=="GET":
        return render_template("register.html")
    if request.method == "POST":
        if not request.form.get("name"):
            return apology("must provide name")
        elif not request.form.get("password"):
            return apology("must provide password")
        elif not request.form.get("confirmPassword"):
            return apology("must confirm password")
        elif not request.form.get("birthday"):
            return apology("must select your birthday")
        if not request.form.get("password") == request.form.get("confirmPassword"):
            return apology("Passwords in both files must be the same")
        rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("name"))
        if len(rows) == 1:
            return apology("The user with this name already exists.")
        #Adding user to database according to file
        photofile = request.files['file']
        if not photofile:
            db.execute("INSERT INTO users (name, password, photo, birthday) values (?, ?, ?, ?)", request.form.get("name"), generate_password_hash(request.form.get("password")), "basic.jpg", request.form.get("birthday"))
            rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("name"))
            session["user_id"] = rows[0]["id"]
            session["name"] = rows[0]["name"]
            session["photo"] = "basic.jpg"
            db.execute("INSERT INTO money (user_id, donated, received, balance) values (?, 0, 0, 0)", rows[0]["id"])
            session['messageBox'] = "You've just registered! Welcome"
            return redirect("/")
        if photofile:
            #logic that allow us to upload the photo
            if allowed_file(photofile.filename) in ALLOWED_EXTENSIONS:
                photofile.filename = request.form.get("name") + "." + allowed_file(photofile.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], photofile.filename)
                photofile.save(filepath)
                db.execute("INSERT INTO users (name, password, photo, birthday) values (?, ?, ?, ?)", request.form.get("name"), generate_password_hash(request.form.get("password")), photofile.filename, request.form.get("birthday"))
                rows = db.execute("SELECT * FROM users WHERE name = ?", request.form.get("name"))
                db.execute("INSERT INTO money (user_id, donated, received, balance) values (?, 0, 0, 0)", rows[0]["id"])
                session["user_id"] = rows[0]["id"]
                session["name"] = rows[0]["name"]
                session["photo"] = rows[0]["photo"]
                session['messageBox'] = "You've just registered! Welcome"
                return redirect("/")