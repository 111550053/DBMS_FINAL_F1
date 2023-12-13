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

@app.route('/race_analysis')
def race_analysis():
    return render_template('race_analysis.html')

@app.route("/analysis_display", methods = ["GET",'POST'])
def analysis_display():
    driver_surname=request.args.get('driver_surname','')
    driver_forename=request.args.get('driver_forename','')
    selected_year=request.args.get('year','')
    race_round=request.args.get('round','')
    
    query_check_year="SELECT COUNT(*) FROM races WHERE year=%s"
    query_check_round = "SELECT COUNT(*) FROM races WHERE year = %s AND round = %s"

    query = """
        SELECT results.resultId,races.date, races.time,races.round, drivers.driverRef, drivers.forename, drivers.surname, 
               constructors.constructorRef, constructors.name, races.url
        FROM races, constructor_results, constructors, results, drivers
        WHERE results.raceId = races.raceId
              AND results.driverId = drivers.driverId
              AND results.constructorId = constructors.constructorId
              AND year = %s
              AND (drivers.forename LIKE %s OR %s ='')
              AND (drivers.surname LIKE %s OR %s = '')
              AND (races.round = %s OR %s = '')
        LIMIT 20
    """

    try:
        cursor.execute(query_check_year, (selected_year,))
        year_count = cursor.fetchone()[0]

        if year_count == 0:
            error_message = f"No races found for the year {selected_year}."
            return render_template('race_analysis.html', error_message=error_message, selected_year=selected_year)

        cursor.execute(query_check_round, (selected_year, race_round))
        round_count = cursor.fetchone()[0]

        if round_count == 0:
            error_message = f"No races found for round {race_round} in the year {selected_year}."
            return render_template('race_analysis.html', error_message=error_message, selected_year=selected_year)

        if driver_surname or driver_forename or race_round:
            cursor.execute(query, (selected_year, f'%{driver_forename}%', driver_forename, f'%{driver_surname}%', driver_surname, race_round, race_round))
        else:
            cursor.execute(query, (selected_year, '%', '', '%', '', '', ''))


        data = cursor.fetchall()

        if not data:
            error_message=f"No driver found with the partial name '{driver_forename + ' ' +  driver_surname}'.\n Please search the name again!"
            return render_template('race_analysis.html', error_message=error_message, selected_year=selected_year)

        return render_template('race_analysis.html', data=data, selected_year=selected_year)

    except Exception as e:
        print(f"Error: {str(e)}")
        return "An error occurred. Please check the server logs for details."

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
