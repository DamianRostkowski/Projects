from flask import redirect, render_template, session
from functools import wraps
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as p
import os

def allowed_file(filename):
    return filename.rsplit('.', 1)[1].lower()

#Make graph based on user's donates and asks for money
def makeGraph(donated, received):
    #configure graph and overwrite last one
    sizes = []
    if donated == 0 and received == 0:
        sizes = [50, 50]
    else:
        total= donated + received
        donated = donated/total*100
        received = received/total*100
        sizes = [donated, received]
    p.pie(sizes, autopct='%1.1f%%', labels=["donated", "received"], startangle=140, colors=["orange", "skyblue"])  # autopct dodaje procenty, startangle ustawia kąt początkowy
    p.axis('equal')  # Ustawienie osi na równą, aby wykres wyglądał jak koło
    p.title('Your balance')
    img_path = 'static/photos/webSite/graph.png'
    if os.path.exists(img_path):
        os.remove(img_path)
    p.tight_layout()
    p.savefig(img_path, transparent=True)
    p.close()

#
def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

#shows propositions to user relying on his input in searching people



