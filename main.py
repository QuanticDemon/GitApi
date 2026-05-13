from flask import *
import json
from pathlib import Path
app = Flask(__name__)
app.secret_key = "IZN"
#logica de web

@app.route('/home')
def home():
    username = session.get("user_logged")

    if not username:
        return redirect(url_for("login"))
    

    return render_template("home.html", username = username)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=["GET","POST"])
def register():
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        userNew = Users(username, password)
        
        usuarios_registrados = db.load()

        if any(user['username']==userNew.username for user in usuarios_registrados):
            return redirect(url_for("login"))         

        db.save(userNew)
        session["user_logged"] = userNew.username
        return redirect(url_for("home"))

    return render_template("register.html")

@app.route('/logout')
def logout():
    return redirect(url_for("index"))


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username == "Izanadmin" and password =="lol":
            session["user_logged"] = username
            return redirect(url_for("home"))
        else:
            session["user_logged"] = username
            return redirect(url_for("home"))
            
    return render_template("login.html")

#logica db
class Users:
    def __init__(self, username, passw):
        self.username = username 
        self.passw = passw

def serializator(objt):
    if hasattr(objt, "__dict__"):
        return objt.__dict__
    raise TypeError(f"No se pudo serializar")


class JsonManager:
    def __init__(self, file):
        self.file = file
        Path(self.file).parent.mkdir(parents=True, exist_ok=True)
        if not Path(self.file).exists() or Path(self.file).stat().st_size==0:
            
            with open(self.file, "w", encoding="utf-8") as f:
                json.dump([], f)

    def load(self):
        try: 
            if Path(self.file).exists():
                with open(self.file, "r", encoding="utf-8") as f:
                    json.load(f)
                    return []
        except (json.JSONDecodeError, FileNotFoundError):
            return []

            
    def save(self, data_user):
        usuarios = self.load()
        usuarios.append(data_user)
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data_user, f, indent=4, default=serializator)
            print(f"Guardado en '{self.file}'")
#Logica de funcionamiento
base_dir = Path(__file__).resolve().parent

base_dirDB = base_dir / "data" / "data.json"

db = JsonManager(base_dirDB)

if __name__ == "__main__":
    app.run(debug=True)
    