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

@app.route("/circuit_analysis", methods = ["GET", "POST"])
def circuit_analysis():
    cursor.execute("select circuitId,name,location,country from circuits")
    data = cursor.fetchall()
    return render_template("circuit_analysis.html",  data = data)

@app.route("/circuit_analysis_display", methods = ["GET",'POST'])
def circuit_analysis_display():
    circuitId=request.args.get('circuitId','')
    selected_year=request.args.get('year','')
    
    query_check = """
        SELECT COUNT(*) 
        FROM (SELECT circuitId FROM circuits WHERE circuitId LIKE %s OR %s = '') as circuits
        , (SELECT circuitId FROM races WHERE year = %s) as races
        WHERE circuits.circuitId = races.circuitId
    """
    #circuit name, loc, country, 
    query = """
        WITH maxLapSpeed as (SELECT races.raceId as raceId, MAX(results.fastestLapSpeed) as maxSpeed
        FROM (SELECT circuitId FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT raceId, circuitId FROM races WHERE year = %s) as races
        , (SELECT raceId, fastestLapSpeed FROM results) as results
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        GROUP BY races.raceId)
        ,
        base as (SELECT races.raceId as raceId, circuits.name as circuitName, circuits.location as location, circuits.country as country, 
        results.fastestLapSpeed as lapSpeed, CONCAT(drivers.forename,' ',drivers.surname) as driver
        FROM (SELECT circuitId, name, location, country FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT raceId, circuitId FROM races WHERE year = %s) as races
        , (SELECT resultId, raceId, driverId, constructorId, fastestLapSpeed, points FROM results) as results
        , (SELECT driverId, forename, surname, nationality FROM drivers) as drivers
        , (SELECT constructorId, name, nationality FROM constructors) as constructors
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        AND results.driverId = drivers.driverId
        AND results.constructorId = constructors.constructorId)
        ,
        winTeam as (SELECT Race.raceId as raceId, Race.constructorId as constructorId, Race.totalPoints as points
        FROM (SELECT raceId, MAX(totalPoints) as maxPoints
        FROM (SELECT races.raceId as raceId, SUM(results.points) as totalPoints
        FROM (SELECT raceId FROM races WHERE year = %s) as races
        , (SELECT raceId, constructorId, points FROM results) as results
        , (SELECT constructorId FROM constructors) as constructors
        WHERE races.raceId = results.raceId
        AND results.constructorId = constructors.constructorId
        GROUP BY races.raceId, constructors.constructorId) as T
        GROUP BY raceId) as maxPoints
        ,(SELECT results.raceId as raceId, results.constructorId as constructorId, SUM(results.points) as totalPoints
        FROM (SELECT raceId, constructorId, points FROM results) as results
        GROUP BY results.raceId, results.constructorId) as Race
        WHERE Race.raceId = maxPoints.raceId
        AND Race.totalPoints = maxPoints.maxPoints)
        ,
        podium1 as (SELECT races.raceId as raceId, drivers.name as driver
        FROM (SELECT circuitId FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT raceId, circuitId FROM races WHERE year = %s) as races
        , (SELECT resultId, driverId, raceId FROM results WHERE position = '1') as results
        , (SELECT driverId, CONCAT(forename, ' ', surname) as name FROM drivers) as drivers
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        AND results.driverId = drivers.driverId)
        ,
        podium2 as (SELECT races.raceId as raceId, drivers.name as driver
        FROM (SELECT circuitId FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT raceId, circuitId FROM races WHERE year = %s) as races
        , (SELECT resultId, driverId, raceId FROM results WHERE position = '2') as results
        , (SELECT driverId, CONCAT(forename, ' ', surname) as name FROM drivers) as drivers
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        AND results.driverId = drivers.driverId)
        ,
        podium3 as (SELECT races.raceId as raceId, drivers.name as driver
        FROM (SELECT circuitId FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT raceId, circuitId FROM races WHERE year = %s) as races
        , (SELECT resultId, driverId, raceId FROM results WHERE position = '3') as results
        , (SELECT driverId, CONCAT(forename, ' ', surname) as name FROM drivers) as drivers
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        AND results.driverId = drivers.driverId)

        SELECT M.circuitName, M.location, M.country, M.lapSpeed, M.driver, PW.winTeam, first, second, third
        FROM (SELECT P.raceId as raceId, W.winTeam as winTeam, first, second, third
        FROM (SELECT podium1.raceId as raceId, podium1.driver as first, podium2.driver as second, podium3.driver as third
        FROM podium1, podium2, podium3
        WHERE podium1.raceId = podium2.raceId
        AND podium1.raceId = podium3.raceId) as P
        ,
        (SELECT winTeam.raceId, name as winTeam
        FROM winTeam, (SELECT constructorId, name FROM constructors) as constructors
        WHERE winTeam.constructorId = constructors.constructorId) as W
        WHERE P.raceId = W.raceId) as PW
        ,
        (SELECT base.raceId, base.circuitName, base.location, base.country, 
        base.lapSpeed, base.driver
        FROM base, maxLapSpeed
        WHERE maxLapSpeed.maxSpeed = base.lapSpeed
        AND base.raceId = maxLapSpeed.raceId) as M
        WHERE PW.raceId = M.raceId
        ORDER BY M.circuitName
    """

    try:
        cursor.execute(query_check, (circuitId,circuitId,selected_year,))
        count = cursor.fetchone()[0]

        if count == 0:
            error_message = f"No races in {circuitId} found for the year {selected_year}."
            return render_template('circuit_analysis.html', error_message=error_message, selected_year=selected_year, selected_circuit=circuitId)

        if(circuitId == '' or circuitId == '0' or circuitId[0] == '-'):
            cursor.execute(query, ('-1', '', selected_year,'-1', '', selected_year, selected_year,'-1', '', selected_year,'-1', '', selected_year,'-1', '', selected_year))
        else:
            cursor.execute(query, (circuitId, circuitId, selected_year,circuitId, circuitId, selected_year, selected_year,circuitId, circuitId, selected_year,circuitId, circuitId, selected_year,circuitId, circuitId, selected_year))
        data = cursor.fetchall()
        if not data:
            error_message=f"No data found with the circuit '{circuitId}' and year '{selected_year}'.\n Please search the name again!"
            return render_template('circuit_analysis.html', error_message=error_message, selected_year=selected_year, selected_circuit=circuitId)

        return render_template('circuit_analysis.html', data = data, selected_year=selected_year, selected_circuit=circuitId)

    except Exception as e:
        print(f"Error: {str(e)}")
        return "An error occurred. Please check the server logs for details."

@app.route('/race_analysis')
def race_analysis():
    return render_template('race_analysis.html')

@app.route("/race_analysis_display", methods = ["GET",'POST'])
def race_analysis_display():
    driver_surname=request.args.get('driver_surname','')
    driver_forename=request.args.get('driver_forename','')
    selected_year=request.args.get('year','')
    race_round=request.args.get('round','')
    
    query_check_year="SELECT COUNT(*) FROM races WHERE year = %s"
    query_check_round = "SELECT COUNT(*) FROM races WHERE year = %s AND (round = %s OR %s = '')"

    query = """
        SELECT races.date, races.time, races.round, drivers.forename, drivers.surname, constructors.name
        FROM (SELECT raceId, date, time, round FROM races WHERE year = %s AND (round = %s OR %s = '')) as races
        , (SELECT name, constructorId FROM constructors) as constructors
        , (SELECT raceId,driverId,constructorId FROM results) as results
        , (SELECT driverId, forename, surname FROM drivers WHERE (drivers.forename LIKE %s OR %s ='') AND (drivers.surname LIKE %s OR %s = '')) as drivers
        WHERE results.raceId = races.raceId
              AND results.driverId = drivers.driverId
              AND results.constructorId = constructors.constructorId
    """

    try:
        cursor.execute(query_check_year, (selected_year,))
        year_count = cursor.fetchone()[0]

        if year_count == 0:
            error_message = f"No races found for the year {selected_year}."
            return render_template('race_analysis.html', error_message=error_message, selected_year=selected_year)

        if (race_round != '0' and race_round[0] != '-'):
            cursor.execute(query_check_round, (selected_year, race_round, race_round))
        else:
            cursor.execute(query_check_round, (selected_year, race_round,''))
        round_count = cursor.fetchone()[0]

        if round_count == 0:
            error_message = f"No races found for round {race_round} in the year {selected_year}."
            return render_template('race_analysis.html', error_message=error_message, selected_year=selected_year)

        if (driver_surname or driver_forename) and (race_round != '0' and race_round[0] != '-'):
            cursor.execute(query, (selected_year, race_round, race_round, f'%{driver_forename}%', driver_forename, f'%{driver_surname}%', driver_surname))
        else :
            if (driver_surname or driver_forename) and (race_round == '0' or race_round[0] == '-'):
                cursor.execute(query, (selected_year, '-1', '', f'%{driver_forename}%', driver_forename, f'%{driver_surname}%', driver_surname))
            else:
                if race_round == '0' or race_round[0] == '-':
                    cursor.execute(query, (selected_year, '-1', '', '%', '', '%', ''))
                else :
                    cursor.execute(query, (selected_year, race_round, race_round, '%', '', '%', ''))

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
