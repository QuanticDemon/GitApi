from flask import *
import json
from pathlib import Path
import uuid 
from abc import ABC, abstractmethod
app = Flask(__name__)
app.secret_key = "IZN"
#logica de web

@app.route('/home', methods=["GET", "POST"])
def home():
    username = session.get("user_logged")

    if not username:
        return redirect(url_for("login"))

    mode = None
    name = None
    retorno = None
    Cratename_user = None
    pass_user = None
    checkBox = []
    action = None
    checkBoxName = False
    checkBoxPass =  False
    editMode = False
    newName = None
    newPass = None
    if request.method == "POST":
        mode = request.form.get('lista')
        name = request.form.get('Searchuser')
        Cratename_user = request.form.get('name')
        pass_user = request.form.get('password')
        checkBox = request.form.getlist('check')
        action = request.form.get('action')
        editMode = request.form.get("editMode") == "True"
        
        if not name:
            name = request.form.get('username')
        if mode == 'consult':
            retorno = Consulta(name).consultar()
            
        elif mode == 'crear':
            retorno = Crear(Cratename_user, pass_user).crear()
            
        elif mode == 'delete':
            
            retorno = Deleter(name, []).consultar()
            
            if action == "delete":
                deleter = Deleter(name, checkBox)

                retorno = deleter.delete()
        elif mode == 'edit':
            retorno = Edition(name).consultar()
            if request.form.get("editMode") == "True":
                editMode = True
            checkBoxName = request.form.get('checkEditName') is not None
            checkBoxPass = request.form.get('checkEditPass') is not None

            if action == "aplicar":
                newName = request.form.get('newName')
                newPass = request.form.get('newPass')

                editor = Edition(name)

                retorno =editor.editar(
                    newName if checkBoxName else None,
                    newPass if checkBoxPass else None
                )

    return render_template("home.html", 
                           username = username, 
                           mode = mode, 
                           nameUser = name, 
                           retorno =retorno,
                           Cratename_user = Cratename_user,
                           editMode = editMode,
                           checkBoxName = checkBoxName,
                            checkBoxPass = checkBoxPass
                           )
#admin modes

class Consulta(): 
    def __init__(self, objetivo):
        self.objetivo = objetivo

    def consultar(self):
        usuario_registrados = db.load()

        users_encontrado = [u for u in usuario_registrados if u['username'] == self.objetivo]

        return users_encontrado

class Crear:
    def __init__(self, name, password):
        self.name = name
        self.password = password
    def crear(self):
        newUser = Users(self.name, self.password)
        db.save(newUser)
    
class Deleter(Consulta):
    def __init__(self, objetivo, usersChecked):
        super().__init__(objetivo)
        self.usersChecked = usersChecked
    def consultar(self):
        return super().consultar()
    def delete(self):
        usuarios_registrados = db.load()

        users_update = [users for users in usuarios_registrados if users['id'] not in self.usersChecked]

        db.update(users_update)  

        return users_update

class Edition(Consulta):
    def __init__(self, objetivo):
        super().__init__(objetivo)
        

    def consultar(self):
        return super().consultar()
    
    def editar(self, newName=None, newPass=None):
        user_registration = db.load()

        for user in user_registration:
            if user['username'] == self.objetivo:
                if newName:
                    user['username'] = newName
                if newPass:
                    user['passw'] = newPass

        db.update(user_registration)
        return user_registration
#endpoint api logica
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
        self.id = str(uuid.uuid4())

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
                    return json.load(f)
                    
        except (json.JSONDecodeError, FileNotFoundError):
            return []

            
    def save(self, data_user):
        usuarios = self.load()
        usuarios.append(data_user)
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(usuarios, f, indent=4, default=serializator)
            print(f"Guardado en '{self.file}'")

    def update(self, data_user):
        with open(self.file, "w", encoding="utf-8") as f:
            json.dump(data_user, f, indent=4, default=serializator)
#Control Panel Admin

def consultaUsuarios():
    name = request.form.get("usernameAdmin")
    usuarios_registrados = db.load()

    usuarios_encontrados = [u for u in usuarios_registrados if u['username'] == name]


    return usuarios_encontrados







#Logica de funcionamiento
base_dir = Path(__file__).resolve().parent

base_dirDB = base_dir / "data" / "data.json"

db = JsonManager(base_dirDB)

if __name__ == "__main__":
    app.run(debug=True)
    
