from flask import Flask, render_template, request, redirect, url_for
import pymysql

db_connection = {
    "host" : "127.0.0.1",
    "user" : "root" ,
    "password" : "" ,
    "db" : "f1",
    "charset" : "utf8"
}

db = pymysql.connect(**db_connection)
cursor = db.cursor()

app = Flask(__name__)


@app.route("/")
def root():
    return redirect(url_for("home"))


@app.route("/home", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html", errormessage="")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    return render_template("signup.html", errormessage="")


@app.route("/signup_check", methods=["GET", "POST"])
def signup_check():
    if request.method == "POST":
        userName = request.form["username"]
        password = request.form["password"]
        cursor.execute("select userName from users")
        result = cursor.fetchall()

        if ((userName,) not in result):
            query = "insert into users (userName, passwd, admin) values (%s, %s, false)"
            cursor.execute(query, (userName, password))
            db.commit()
            return redirect(url_for("home"))
        else:
            return render_template("signup.html", errormessage="user already exists!")


@app.route("/afterlogin", methods=["GET", "POST"])
def afterlogin():
    if request.method == "POST":
        currUserName = request.form["username"]
        currUserPassword = request.form["password"]
        cursor.execute("select userName, passwd, admin from users")
        result = cursor.fetchall()

        if ((currUserName, currUserPassword, 1) in result):
            isadmin = True
            cursor.execute(f"select userId from users where userName='{currUserName}'")
            userId = cursor.fetchall()[0][0]
            return render_template("afterlogin.html", userId=userId, username=currUserName, admin=isadmin)
        elif ((currUserName, currUserPassword, 0) in result):
            isadmin = False
            cursor.execute(f"select userId from users where userName='{currUserName}'")
            userId = cursor.fetchall()[0][0]
            return render_template("afterlogin.html", userId=userId, username=currUserName, admin=isadmin)
        else:
            return render_template("login.html", errormessage="invalid user name or password!")


@app.route("/my_driver_constructor", methods=["GET", "POST"])
def my_driver_constructor():
    userId = request.args.get('userId', "")

    query = f"""select d.driverId, d.driverRef, d.number, d.code, d.forename, d.surname, d.dob, d.nationality, d.url
                from custom_content as cc
                inner join drivers as d
                on cc.customcontentId = d.driverId
                where cc.userId={userId} and cc.customType=1"""

    cursor.execute(query)
    myDriver = cursor.fetchall()

    query = f"""select c.constructorId, c.constructorRef, c.name, c.nationality, c.url
                from custom_content as cc
                inner join constructors as c
                on cc.customcontentId = c.constructorId
                where cc.userId={userId} and cc.customType=2"""

    cursor.execute(query)
    myConstructor = cursor.fetchall()

    return render_template("my_driver_constructor.html", userId=userId, myDriver=myDriver, myConstructor=myConstructor)


@app.route("/my_driver_add", methods=["GET", "POST"])
def my_driver_add():
    userId = request.args.get('userId', "")
    return render_template("my_driver_add.html", userId=userId)


@app.route("/my_driver_save", methods=["GET", "POST"])
def my_driver_save():
    userId = request.args.get('userId', "")
    driverRef = request.args.get("driverRef", "")
    number = request.args.get("number", "")
    code = request.args.get("code", "")
    forename = request.args.get("forename", "")
    surname = request.args.get("surname", "")
    dob = request.args.get("dob", "")
    nationality = request.args.get("nationality", "")
    url = request.args.get("url", "")

    query = f'''insert into drivers (driverRef,number,code,forename,surname,dob,nationality,url)
                values ('{driverRef}', {number}, '{code}', '{forename}', '{surname}', '{dob}', '{nationality}', '{url}')'''

    cursor.execute(query)
    db.commit()

    query = f'''select driverId from drivers where driverRef='{driverRef}' and
                number={number} and code='{code}' and forename='{forename}' and 
                surname='{surname}' and dob='{dob}' and nationality='{nationality}'
                and url='{url}'
                '''

    cursor.execute(query)
    driverId = cursor.fetchall()[0][0]

    query = f'''insert into custom_content (userId,customType,customcontentId)
                values ({userId}, 1, {driverId})'''

    cursor.execute(query)
    db.commit()

    return redirect(url_for("my_driver_constructor", userId=userId))


@app.route("/my_driver_delete", methods=["GET", "POST"])
def my_driver_delete():
    driverId = request.args.get('driverId', "")
    userId = request.args.get('userId', "")

    query = f"delete from drivers where driverId = {driverId}"
    cursor.execute(query)
    db.commit()

    query = f"delete from custom_content where customcontentId = {driverId} and userId = {userId} and customType = 1"
    cursor.execute(query)
    db.commit()

    return redirect(url_for("my_driver_constructor", userId=userId))


@app.route("/my_driver_edit", methods=["GET", "POST"])
def my_driver_edit():
    driverId = request.args.get('driverId', "")
    userId = request.args.get('userId', "")

    query = f"select * from drivers where driverId = {driverId}"
    cursor.execute(query)
    data = cursor.fetchall()

    return render_template("my_driver_edit.html", data=data[0], userId=userId)


@app.route("/my_driver_update", methods=["GET", "POST"])
def my_driver_update():
    userId = request.args.get('userId', "")
    driverId = request.args.get('driverId', "")
    driverRef = request.args.get("driverRef", "")
    number = request.args.get("number", "")
    code = request.args.get("code", "")
    forename = request.args.get("forename", "")
    surname = request.args.get("surname", "")
    dob = request.args.get("dob", "")
    nationality = request.args.get("nationality", "")
    url = request.args.get("url", "")

    query = f'''update drivers set driverRef='{driverRef}',
                number={number}, code='{code}', forename='{forename}',
                surname='{surname}', dob='{dob}', nationality='{nationality}', url='{url}'
                where driverId={driverId}'''

    cursor.execute(query)
    db.commit()

    return redirect(url_for("my_driver_constructor", userId=userId))


@app.route("/my_constructor_add", methods=["GET", "POST"])
def my_constructor_add():
    userId = request.args.get('userId', "")
    return render_template("my_constructor_add.html", userId=userId)


@app.route("/my_constructor_save", methods=["GET", "POST"])
def my_constructor_save():
    userId = request.args.get('userId', "")
    constructorRef = request.args.get('constructorRef', "")
    name = request.args.get('name', "")
    nationality = request.args.get('nationality', "")
    url = request.args.get('url', "")

    query = f'''insert into constructors (constructorRef,name,nationality,url)
                values ('{constructorRef}', '{name}', '{nationality}', '{url}')'''

    cursor.execute(query)
    db.commit()

    query = f'''select constructorId from constructors where constructorRef='{constructorRef}' and
                name='{name}' and nationality='{nationality}' and url='{url}'
            '''

    cursor.execute(query)
    constructorId = cursor.fetchall()[0][0]
    
    query = f'''insert into custom_content (userId,customType,customcontentId)
                values ({userId}, 2, {constructorId})'''

    cursor.execute(query)
    db.commit()

    return redirect(url_for("my_driver_constructor", userId=userId))


@app.route("/my_constructor_edit", methods=["GET", "POST"])
def my_constructor_edit():
    constructorId = request.args.get('constructorId', "")
    userId = request.args.get('userId', "")

    query = f"select * from constructors where constructorId = {constructorId}"
    cursor.execute(query)
    data = cursor.fetchall()

    return render_template("my_constructor_edit.html", data=data[0], userId=userId)


@app.route("/my_constructor_delete", methods=["GET", "POST"])
def my_constructor_delete():
    constructorId = request.args.get('constructorId', "")
    userId = request.args.get('userId', "")

    query = f"delete from constructors where constructorId = {constructorId}"
    cursor.execute(query)
    db.commit()

    query = f"delete from custom_content where customcontentId = {constructorId} and userId = {userId} and customType = 2"
    cursor.execute(query)
    db.commit()

    return redirect(url_for("my_driver_constructor", userId=userId))


@app.route("/my_constructor_update", methods=["GET", "POST"])
def my_constructor_update():
    userId = request.args.get('userId', "")
    constructorId = request.args.get('constructorId', "")
    constructorRef = request.args.get("constructorRef", "")
    name = request.args.get("name", "")
    nationality = request.args.get("nationality", "")
    url = request.args.get("url", "")

    query = f'''update constructors set constructorRef='{constructorRef}',
                name='{name}', nationality='{nationality}', url='{url}'
                where constructorId={constructorId}'''

    cursor.execute(query)
    db.commit()

    return redirect(url_for("my_driver_constructor", userId=userId))


@app.route("/user_management", methods=["GET", "POST"])
def user_management():
    cursor.execute("select * from users")
    user_list = cursor.fetchall()
    return render_template("user_management.html", data=user_list)


@app.route("/user_update", methods=["GET", "POST"])
def user_update():
    update_user_id = request.args.get('user_id', '')
    cursor.execute("select * from users where userId = %s" % (update_user_id))
    user_list = cursor.fetchall()

    query = "update users set admin = %s where userId = %s"

    if (user_list[0][3] == 1 and (user_list[0][0] != 1)):
        cursor.execute(query, ("0", update_user_id))
    elif (user_list[0][3] == 0 and (user_list[0][0] != 1)):
        cursor.execute(query, ("1", update_user_id))
    db.commit()

    return redirect(url_for("user_management"))


@app.route("/user_remove", methods=["GET", "POST"])
def user_remove():
    remove_user_id = request.args.get('user_id', '')

    query = "delete from users where userId = %s"

    if (remove_user_id != 1):
        cursor.execute(query, (remove_user_id))
        db.commit()

    return redirect(url_for("user_management"))


@app.route("/data_management", methods=["GET", "POST"])
def data_management():
    cursor.execute("show tables")
    tables = cursor.fetchall()
    return render_template("data_management.html", data=tables)


@app.route("/edit_table", methods=["GET", "POST"])
def edit_table():
    edit_table_name = request.args.get('table', '')
    cursor.execute(f"select * from {edit_table_name} limit 10")
    data = cursor.fetchall()

    cursor.execute(f"select count(*) from {edit_table_name}")
    count = cursor.fetchall()[0][0]

    return render_template("edit_table.html", tableName=edit_table_name, data=data, count=count, limit=10, currPage=1)


@app.route("/edit_table_display", methods=["GET", "POST"])
def edit_table_display():
    edit_table_name = request.args.get('tableName', '')
    limit = request.args.get('limit', '')
    count = request.args.get('count', '')
    page = request.args.get('currPage', '')

    query = f"select * from {edit_table_name} limit {limit} OFFSET {(int(page) - 1) * int(limit)}"
    cursor.execute(query)
    data = cursor.fetchall()

    return render_template("edit_table.html", tableName=edit_table_name, data=data, count=count, limit=limit, currPage=page)


primaryKeys = {"circuits": "circuitId",
               "constructors": "constructorId",
               "drivers": "driverId",
               "races": "raceId",
               "constructor_results": "constructorResultsId",
               "constructor_standings": "constructorStandingsId",
               "driver_standings": "driverStandingsId",
               "lap_times": ("raceId", "driverId", "lap"),
               "pit_stops": ("raceId", "driverId", "stop"),
               "qualifying": "qualifyId",
               "results": "resultId",
               "seasons": "year",
               "sprint_results": "resultId",
               "status": "Id",
               "users": "userId",
               "custom_content": "customDataId"}

columns = {"circuits": "circuitId,circuitRef,name,location,country,lat,lng,alt,url",
           "constructors": "constructorId,constructorRef,name,nationality,url",
           "drivers": "driverId,driverRef,number,code,forename,surname,dob,nationality,url",
           "races": "raceId,year,round,circuitId,name,date,time,url,fp1_date,fp1_time,fp2_date,fp2_time,fp3_date,fp3_time,quali_date,quali_time,sprint_date,sprint_time",
           "constructor_results": "constructorResultsId,raceId,constructorId,points,status",
           "constructor_standings": "constructorStandingsId,raceId,constructorId,points,position,positionText,wins",
           "driver_standings": "driverStandingsId,raceId,driverId,points,position,positionText,wins",
           "lap_times": "raceId,driverId,lap,position,time,milliseconds",
           "pit_stops": "raceId,driverId,stop,lap,time,duration,milliseconds",
           "qualifying": "qualifyId,raceId,driverId,constructorId,number,position,q1,q2,q3",
           "results": "resultId,raceId,driverId,constructorId,number,grid,position,positionText,positionOrder,points,laps,time,milliseconds,fastestLap,rank,fastestLapTime,fastestLapSpeed,statusId",
           "seasons": "year,url",
           "sprint_results": "resultId,raceId,driverId,constructorId,number,grid,position,positionText,positionOrder,points,laps,time,milliseconds,fastestLap,fastestLapTime,statusId",
           "status": "Id,status",
           "users": "userId,userName,passwd,admin",
           "custom_content": "customDataId,userId,customType,customcontentId"}


@app.route("/edit_row", methods=["GET", "POST"])
def edit_row():
    edit_table_name = request.args.get('tableName1', '')
    key = request.args.get('key', '')
    limit = request.args.get("limit1", "")
    currPage = request.args.get("currPage1", "")

    query = f"select * from {edit_table_name} where {primaryKeys[edit_table_name]} = {key}"
    cursor.execute(query)
    data = cursor.fetchall()

    return render_template("edit_row.html", data=data, tableName=edit_table_name, limit=limit, currPage=currPage)


@app.route("/save_row", methods=["POST"])
def save_row():
    edit_table_name = request.form.get('tableName')
    values = request.form.getlist('values')
    key = values[0]
    limit = request.form.get("limit", "")
    page = request.form.get("currPage", "")

    cols = columns[edit_table_name].split(',')
    placeholders = ', '.join([f"{col}=%s" for col in cols[1:] if values[cols.index(col)] != 'None'])
    filtered_values = [val for val in values[1:] if val != 'None']

    query = f"UPDATE {edit_table_name} SET {placeholders} WHERE {primaryKeys[edit_table_name]} = %s"

    cursor.execute(query, filtered_values + [key])
    db.commit()

    query = f"select count(*) from {edit_table_name}"
    cursor.execute(query)
    count = cursor.fetchall()[0][0]

    return redirect(url_for("edit_table_display", limit=limit, currPage=page, tableName=edit_table_name, count=count))


@app.route("/delete_row", methods=["GET", "POST"])
def delete_row():
    edit_table_name = request.args.get('tableName1', '')
    key = request.args.get('key', '')
    limit1 = request.args.get('limit1', '')
    page1 = request.args.get('currPage1', '')

    query = f"delete from {edit_table_name} where {primaryKeys[edit_table_name]} = {key}"
    cursor.execute(query)
    db.commit()

    query = f"select count(*) from {edit_table_name}"
    cursor.execute(query)
    count1 = cursor.fetchall()[0][0]

    return redirect(url_for("edit_table_display", limit=limit1, currPage=page1, tableName=edit_table_name, count=count1))


@app.route("/driver_analysis", methods=["GET", "POST"])
def driver_analysis():
    cursor.execute("select driverId,CONCAT(forename, ' ', surname) as name from drivers")
    driver = cursor.fetchall()
    return render_template("driver_analysis.html",  driver=driver)


@app.route("/driver_analysis_display", methods=["GET", "POST"])
def driver_analysis_display():
    selected_year = request.args.get('year', '')
    selected_type = request.args.get('type', '')
    driver_surname = request.args.get('driver_surname', '')
    driver_forename = request.args.get('driver_forename', '')

    cursor.execute("SELECT MAX(round)/2 FROM races")
    halfRound = cursor.fetchall()

    race = """
        SELECT races.year, drivers.name, constructors.name, AVG(results.position), MAX(fastestLapSpeed) 
        FROM (SELECT driverId, CONCAT(forename, ' ', surname) as name FROM drivers WHERE (forename = %s OR %s = '') AND (surname = %s OR %s = '')) as drivers, (SELECT constructorId, name FROM constructors) as constructors
        , (SELECT raceId, year FROM races) as races, (SELECT raceId, driverId, constructorId, fastestLapSpeed, position FROM results) as results
        WHERE races.raceId = results.raceId
        AND drivers.driverId = results.driverId
        AND constructors.constructorId = results.constructorId
        GROUP BY races.year, drivers.driverId, constructors.constructorId
        ORDER BY races.year DESC, drivers.name
    """

    season = """ WITH first as( 
    SELECT races.year, drivers.driverId, drivers.name, SUM(results.points) as totalPoints
    FROM (SELECT raceId, driverId, points FROM results) as results
    , (SELECT year, raceId FROM races WHERE round < %s) as races
    , (SELECT driverId, CONCAT(forename, ' ', surname) as name FROM drivers WHERE (forename LIKE %s OR %s = '') AND (surname LIKE %s OR %s = '')) as drivers
    WHERE drivers.driverId = results.driverId
    AND races.raceId = results.raceId
    GROUP BY races.year, drivers.driverId
    ORDER BY year DESC, totalPoints DESC),

    last as (SELECT races.year, drivers.driverId, drivers.name, SUM(results.points) as totalPoints
    FROM (SELECT raceId, driverId, points FROM results) as results
    , (SELECT year, raceId FROM races WHERE round >= %s) as races
    , (SELECT driverId, CONCAT(forename, ' ', surname) as name FROM drivers WHERE (forename LIKE %s OR %s = '') AND (surname LIKE %s OR %s = '')) as drivers
    WHERE drivers.driverId = results.driverId
    AND races.raceId = results.raceId
    GROUP BY races.year, drivers.driverId
    ORDER BY year DESC, totalPoints DESC)

    SELECT first.year, first.name, first.totalPoints + last.totalPoints as wholePoints, first.totalPoints, last.totalPoints
    FROM first, last
    WHERE first.driverId = last.driverId
    AND first.year = last.year
    ORDER BY first.year DESC, wholePoints DESC, first.totalPoints DESC, last.totalPoints DESC
    """

    if(selected_type == 'season'):
        cursor.execute(season, (halfRound, driver_forename, driver_forename, driver_surname, driver_surname,
                                halfRound, driver_forename, driver_forename, driver_surname, driver_surname))
    elif(selected_type == 'race'):
        cursor.execute(race, (driver_forename, driver_forename, driver_surname, driver_surname))
    else:
        cursor.execute("select driverId,CONCAT(forename, ' ', surname) as name from drivers")
    driver = cursor.fetchall()

    return render_template("driver_analysis.html",  driver=driver, selected_year=selected_year, selected_type=selected_type)

@app.route("/constructor_analysis", methods=["GET", "POST"])
def constructor_analysis():
    cursor.execute("select constructorId, name from constructors")
    constructor = cursor.fetchall()
    return render_template("constructor_analysis.html",  constructor_data=constructor)

@app.route("/constructor_analysis_display", methods=["GET", "POST"])
def constructor_analysis_display():
    constructor_name = request.args.get('constructor_name', '')
    cursor.execute("SELECT constructorId FROM constructors WHERE name = %s", (constructor_name,))
    constructor_data = cursor.fetchone()

    if constructor_data:
        constructor_id = constructor_data[0]
        cursor.execute("SELECT raceId, points, position FROM constructor_standings WHERE constructorId = %s", (constructor_id,))
        constructor_standing_data = cursor.fetchall()
        race_data = []
        for row in constructor_standing_data:
            cursor.execute("SELECT year, round FROM races WHERE raceId = %s", (row[0],))
            race_info = cursor.fetchone()
            if race_info:
                race_data.append((race_info[0], race_info[1], row[1], row[2]))

            race_data = sorted(race_data, key=lambda x: (x[0], x[1]), reverse=True)
        return render_template("constructor_analysis.html", constructor_data=constructor_data, constructor_name=constructor_name, data=race_data)
    else:
        cursor.execute("select constructorId, name from constructors")
        constructor = cursor.fetchall()
        return render_template("constructor_analysis.html",  constructor_data=constructor)
        
@app.route("/circuit_analysis", methods=["GET", "POST"])
def circuit_analysis():
    cursor.execute("select circuitId,name,location,country from circuits")
    data = cursor.fetchall()
    return render_template("circuit_analysis.html",  data=data)


@app.route("/circuit_analysis_display", methods=["GET", 'POST'])
def circuit_analysis_display():
    circuitId = request.args.get('circuitId', '')
    selected_type = request.args.get('type', '')

    query_check = """
        SELECT COUNT(*) 
        FROM (SELECT circuitId FROM circuits WHERE circuitId LIKE %s OR %s = '') as circuits
        , (SELECT circuitId FROM races) as races
        WHERE circuits.circuitId = races.circuitId
    """
    # circuit name, loc, country,
    winTeamAndPodium = """
        WITH base as (SELECT races.year, races.raceId as raceId, races.round as round, circuits.circuitId, circuits.name as circuitName, circuits.location as location, circuits.country as country
        FROM (SELECT circuitId, name, location, country FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT year, raceId, circuitId, round FROM races) as races
        WHERE circuits.circuitId = races.circuitId)
        ,
        winTeam as (SELECT Race.raceId as raceId, Race.constructorId as constructorId, Race.totalPoints as points
        FROM (SELECT raceId, MAX(totalPoints) as maxPoints
        FROM (SELECT races.raceId as raceId, SUM(results.points) as totalPoints
        FROM (SELECT raceId FROM races) as races
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
        , (SELECT raceId, circuitId FROM races) as races
        , (SELECT resultId, driverId, raceId FROM results WHERE position = '1') as results
        , (SELECT driverId, CONCAT(forename, ' ', surname) as name FROM drivers) as drivers
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        AND results.driverId = drivers.driverId)
        ,
        podium2 as (SELECT races.raceId as raceId, drivers.name as driver
        FROM (SELECT circuitId FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT raceId, circuitId FROM races) as races
        , (SELECT resultId, driverId, raceId FROM results WHERE position = '2') as results
        , (SELECT driverId, CONCAT(forename, ' ', surname) as name FROM drivers) as drivers
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        AND results.driverId = drivers.driverId)
        ,
        podium3 as (SELECT races.raceId as raceId, drivers.name as driver
        FROM (SELECT circuitId FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT raceId, circuitId FROM races) as races
        , (SELECT resultId, driverId, raceId FROM results WHERE position = '3') as results
        , (SELECT driverId, CONCAT(forename, ' ', surname) as name FROM drivers) as drivers
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        AND results.driverId = drivers.driverId)

        SELECT base.year, base.round, base.circuitId, base.circuitName, base.location, base.country, W.winTeam as winTeam, W.points, first, second, third
        FROM (SELECT podium1.raceId as raceId, podium1.driver as first, podium2.driver as second, podium3.driver as third
        FROM podium1, podium2, podium3
        WHERE podium1.raceId = podium2.raceId
        AND podium1.raceId = podium3.raceId) as P
        ,
        (SELECT winTeam.raceId as raceId, name as winTeam, winTeam.points as points
        FROM winTeam, (SELECT constructorId, name FROM constructors) as constructors
        WHERE winTeam.constructorId = constructors.constructorId) as W, base
        WHERE P.raceId = W.raceId
        AND base.raceId = P.raceId
        ORDER BY year DESC, round DESC
    """

    maxLapSpeed = """
        WITH maxLapSpeed as (SELECT races.raceId as raceId, MAX(results.fastestLapSpeed) as maxSpeed
        FROM (SELECT circuitId FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT raceId, circuitId FROM races) as races
        , (SELECT raceId, fastestLapSpeed FROM results) as results
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        GROUP BY races.raceId)
        ,
        base as (SELECT races.year, races.raceId as raceId, races.round, circuits.circuitId as circuitId,circuits.name as circuitName, circuits.location as location, circuits.country as country, 
        results.fastestLapSpeed as lapSpeed, CONCAT(drivers.forename,' ',drivers.surname) as driver
        FROM (SELECT circuitId, name, location, country FROM circuits WHERE (circuitId LIKE %s OR %s = '')) as circuits
        , (SELECT year, raceId, circuitId, round FROM races) as races
        , (SELECT resultId, raceId, driverId, constructorId, fastestLapSpeed, points FROM results) as results
        , (SELECT driverId, forename, surname, nationality FROM drivers) as drivers
        , (SELECT constructorId, name, nationality FROM constructors) as constructors
        WHERE circuits.circuitId = races.circuitId
        AND races.raceId = results.raceId
        AND results.driverId = drivers.driverId
        AND results.constructorId = constructors.constructorId)

        SELECT base.year, base.round, base.circuitId, base.circuitName, base.location, base.country, base.lapSpeed, base.driver
        FROM base, maxLapSpeed
        WHERE maxLapSpeed.maxSpeed = base.lapSpeed
        AND base.raceId = maxLapSpeed.raceId
        ORDER BY base.year DESC, base.round DESC
    """

    try:
        cursor.execute(query_check, (circuitId, circuitId))
        count = cursor.fetchone()[0]

        if count == 0:
            error_message = f"No races in {circuitId} found"
            return render_template('circuit_analysis.html', error_message=error_message)

        if(selected_type == 'B'):
            if(circuitId == '' or circuitId == '0' or circuitId[0] == '-'):
                cursor.execute(maxLapSpeed, ('-1', '', '-1', ''))
            else:
                cursor.execute(maxLapSpeed, (circuitId, circuitId, circuitId, circuitId))
        else:
            if(circuitId == '' or circuitId == '0' or circuitId[0] == '-'):
                cursor.execute(winTeamAndPodium, ('-1', '', '-1', '', '-1', '', '-1', ''))
            else:
                cursor.execute(winTeamAndPodium, (circuitId, circuitId, circuitId, circuitId, circuitId, circuitId, circuitId, circuitId))

        data = cursor.fetchall()

        if not data:
            error_message = f"No data found with the circuit '{circuitId}'.\n Please search the name again!"
            return render_template('circuit_analysis.html', error_message=error_message)

        return render_template('circuit_analysis.html', selected_type=selected_type, data=data)

    except Exception as e:
        print(f"Error: {str(e)}")
        return "An error occurred. Please check the server logs for details."


@app.route('/race_analysis')
def race_analysis():
    return render_template('race_analysis.html')


@app.route("/race_analysis_display", methods = ["GET",'POST'])
def race_analysis_display():
    
    try:
        query_fastest_lap="""
            WITH TMP as (SELECT races.raceId, MIN(fastestLapTime) as minLapTime
            FROM results,drivers,constructors,races
            WHERE results.driverId=drivers.driverId 
                  AND races.year=%s
                  AND races.round = %s
                  AND results.constructorId=constructors.constructorId
                  AND results.raceId=races.raceId
            GROUP BY races.raceId)
            SELECT races.name,races.year,races.date,races.time,races.round,CONCAT(drivers.forename, ' ', drivers.surname) as driver_name, constructors.name,fastestLap, fastestLapTime
            FROM results,drivers,constructors,races,TMP
            WHERE results.driverId=drivers.driverId 
                  AND races.year=%s
                  AND races.round = %s
                  AND results.constructorId=constructors.constructorId
                  AND results.raceId=races.raceId
                  AND TMP.raceId = races.raceId
                  AND results.fastestLapTime = minLapTime
        """
        query_qualifying="""
        select races.name,races.quali_date,races.quali_time,circuits.name,CONCAT(drivers.forename, ' ', drivers.surname) as driver_name,
               constructors.name,qualifying.position,qualifying.q1,qualifying.q2,qualifying.q3
        from(select raceId,year,round,circuitId,name,quali_date,quali_time from races where year=%s and round=%s) as races
        ,(select qualifyId,raceId,driverId,constructorId,position,q1,q2,q3 from qualifying) as qualifying
        ,(select driverId,forename,surname from drivers) as drivers
        ,(select circuitId,name from circuits) as circuits
        ,(select constructorId,name from constructors) as constructors
        where races.raceId=qualifying.raceId
              and circuits.circuitId=races.circuitId
              and drivers.driverId=qualifying.driverId
              and constructors.constructorId=qualifying.constructorId

        """

        query_basic_data = """
        SELECT races.name,races.date, races.time,circuits.name,CONCAT(drivers.forename, ' ', drivers.surname) as driver_name, 
               constructors.name,results.position,results.points,results.time,results.fastestLap,results.fastestLapTime,status.status
        FROM (SELECT name,year,raceId,circuitId, date, time, round FROM races WHERE year = %s AND (round = %s OR %s = '')) as races
        , (SELECT name, constructorId FROM constructors) as constructors
        , (SELECT raceId,driverId,constructorId,position,points,time,fastestLap,fastestLapTime,statusId FROM results) as results
        , (SELECT driverId, forename, surname FROM drivers) as drivers
        , (SELECT circuitId,name from circuits) as circuits
        , status
        WHERE results.raceId = races.raceId
              AND results.driverId = drivers.driverId
              AND results.constructorId = constructors.constructorId
              AND status.statusId=results.statusId
              AND races.circuitId=circuits.circuitId
        """
        #max_lap=6
        query_pit_stops="""
        select CONCAT(drivers.forename, ' ', drivers.surname) as driver_name,temp.lap,temp.duration 
        from((select races.raceId,races.name,pit_stops.driverId,pit_stops.lap,pit_stops.duration
            from (select raceId, name from races where year=%s and (round = %s OR %s = '')) as races
            ,(select raceId,driverId,lap,duration from pit_stops) as pit_stops
            where races.raceId=pit_stops.raceId)) as temp,drivers
        where temp.driverId=drivers.driverId

        """


        selected_year=request.args.get('year','')
        race_round=request.args.get('round','')
        selected_type=request.args.get('type','')

        query_check="""
            select count(*)
            from races 
            where year=%s and round=%s
        """

        if(race_round[0]=='-' or race_round=='0'):
            error_message=f"Please enter the positive round"
            return render_template('race_analysis.html',error_message=error_message)

        cursor.execute(query_check,(selected_year,race_round))
        correctness=cursor.fetchone()[0]

        if (correctness == 0):
            error_message = f"No races found for round {race_round} in the year {selected_year}."
            return render_template('race_analysis.html', error_message=error_message)



        if(selected_type=='lapper'):
            cursor.execute(query_fastest_lap,(selected_year, race_round, selected_year, race_round))
            lapper_data=cursor.fetchall()
            return render_template('race_analysis.html',lapper_data=lapper_data,selected_year=selected_year,race_round=race_round)
        elif(selected_type=='qualifying'):
            cursor.execute(query_qualifying,(selected_year, race_round))
            qualify_data=cursor.fetchall()
            return render_template('race_analysis.html',qualify_data=qualify_data,selected_year=selected_year,race_round=race_round)
        elif (selected_type=='basic'):
            cursor.execute(query_basic_data,(selected_year, race_round, race_round))
            basic_data=cursor.fetchall()
            return render_template('race_analysis.html',basic_data=basic_data,selected_year=selected_year,race_round=race_round)
        elif (selected_type=='pit_stops'):
            cursor.execute("select name from races where races.year=%s and races.round=%s",(selected_year,race_round))
            race_name=cursor.fetchone()[0]
            cursor.execute(query_pit_stops,(selected_year, race_round, race_round))
            pit_stops_data=cursor.fetchall()
            return render_template('race_analysis.html',pit_stops_data=pit_stops_data,selected_year=selected_year,race_round=race_round,race_name=race_name)
        

    except Exception as e:
        print(f"Error: {str(e)}")
        return "An error occurred. Please check the server logs for details."


@app.route('/rank')
def rank():
    return render_template('rank.html')

@app.route('/rank_display')
def rank_display():
    try:
        query_lap_rank = """
        SELECT distinct lap_times.position, CONCAT(drivers.forename, ' ', drivers.surname) as driver_name
        FROM (SELECT name,year,raceId, date, time, round FROM races WHERE year = %s AND (round = %s OR %s = '')) as races
        , (SELECT name, constructorId FROM constructors) as constructors
        , (SELECT raceId,driverId,constructorId FROM results) as results
        , (SELECT driverId, forename, surname FROM drivers) as drivers
        , (SELECT raceId,driverId,lap,position,time FROM lap_times WHERE lap=%s) as lap_times
        WHERE lap_times.raceId=races.raceId
              AND lap_times.driverId=drivers.driverId
              AND results.raceId=races.raceId
              AND results.constructorId=constructors.constructorId
        ORDER BY lap_times.position
        """

        selected_year=request.args.get('year','')
        race_round=request.args.get('round','')
        lap_number=request.args.get('lap_number', '')
        
        query_check="""
            select count(*) 
            from 
            (select raceId from lap_times where lap=%s) as lap_times
            ,(select raceId,year,round from races where year=%s and round=%s) as races
            where lap_times.raceId=races.raceId
        """
        
        if(race_round[0]=='-' or race_round=='0'):
            error_message = f"Please enter the positive round"
            return render_template('rank.html', error_message=error_message)

        if(lap_number[0]=='-' or lap_number=='0'):
            error_message = f"Please enter the positive lap number"
            return render_template('rank.html', error_message=error_message)

        cursor.execute(query_check,(lap_number,selected_year,race_round))
        correctness=cursor.fetchone()[0]

        if(correctness==0):
            error_message=f"No race found for lap {lap_number} in round {race_round} in the year {selected_year}"
            return render_template('rank.html',error_message=error_message)

        cursor.execute(query_lap_rank,(selected_year, race_round, race_round,lap_number))
        
        data = cursor.fetchall()

        cursor.execute("select name from races where year=%s and round=%s",(selected_year,race_round))
        race_name=cursor.fetchone()[0]

        return render_template('rank.html', data=data, selected_year=selected_year,race_round=race_round,lap_number=lap_number,race_name=race_name)

    except Exception as e:
        print(f"Error: {str(e)}")
        return "An error occurred. Please check the server logs for details."

if __name__ == "__main__":
    app.run("0.0.0.0", debug=True)
