from flask import Flask, render_template, request, redirect, url_for
import pymysql

db_connection = {
    "host" : "127.0.0.1",
    "user" : "eric" ,
    "password" : "123456" ,
    "db" : "f1",
    "charset" : "utf8"
}

db = pymysql.connect(**db_connection)
cursor = db.cursor()

app = Flask(__name__)

# some variabls
currUserName = ""
currUserPassword = ""
login = False


@app.route("/")
def root():
    return redirect(url_for("home"))


@app.route("/home", methods = ["GET", "POST"])
def home():
    if request.method == "GET":
        login = False
        currUserName = ""
        currUserPassword = ""

    elif request.method == "POST":
        userName = request.form["username"]
        password = request.form["password"]

        cursor.execute("select userName, passwd from users")
        result = cursor.fetchall()
        if ((userName, password) not in result):
            cursor.execute("insert into users (userName, passwd, admin) values ('%s', '%s', false)" % (userName, password))
            db.commit()
        else:
            return render_template("signup.html", errormessage = "user already exists!") # temporary solution
    
    return render_template("home.html")


@app.route("/login", methods = ["GET", "POST"])
def login():
    return render_template("login.html", errormessage = "")


@app.route("/signup", methods = ["GET", "POST"])
def signup():
    return render_template("signup.html", errormessage = "")


@app.route("/afterlogin", methods = ["GET", "POST"])
def afterlogin():
    if request.method == "POST":
        currUserName = request.form["username"]
        currUserPassword = request.form["password"]
        cursor.execute("select userName, passwd from users")
        result = cursor.fetchall()
        if ((currUserName, currUserPassword) in result):
            login = True
            return render_template("afterlogin.html", username = currUserName)
        else:
            currUserName = ""
            currUserPassword = ""
            return render_template("login.html", errormessage = "invalid user name or password!")
            

@app.route("/manage", methods = ["GET", "POST"])
def manage():
    return render_template("manage.html")

@app.route("/circuit_anal", methods = ["GET", "POST"])
def circuit_anal():
    cursor.execute("select circuitId,circuitRef,name,location,country,url from circuits")
    data = cursor.fetchall()
    return render_template("circuit_anal.html",  data = data)

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
