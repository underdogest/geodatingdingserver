from flask import Flask, request, json, send_file
import json
from mydb import userbase
from passlib.hash import pbkdf2_sha256
import datetime

app = Flask(__name__)

def successMessageJSON(Data):
    d = {
        'Ok': True, 
        'Data': Data
        }
    return json.dumps(d)

def errorMessageJSON(Data):
    d = {
        'Ok': False,
        'Data': Data
        }
    return json.dumps(d)

def checkAuthentification(db, sessionId):
    return True

def connectDatabase():
    db = userbase.Userbase()
    db.connect("test.db")
    return db

@app.route('/')    
def index():
    return "Hello, World!"

@app.route('/users/all', methods=['GET'])
def getAllUsers():    
    try:
        db = connectDatabase()
        ret = db.getAllEntries()
        return json.dumps(ret)
    except Exception as e:
        return errorMessageJSON({'Operation':'list users', 'Cause':'database error'})
    finally:
        db.disconnect()

@app.route('/users/<int:Id>', methods=['GET'])
def getUserinfo(Id):
    try:
        db = connectDatabase()
        ret = db.getEntry(Id)
        return json.dumps(ret)
    except Exception as e:
        return errorMessageJSON({'Operation':'get userinfo', 'Cause':'database error'})
    finally:
        db.disconnect()

@app.route('/users/profile/<int:Id>', methods=['GET'])
def getUserprofile(Id):
    try:
        db = connectDatabase()
        ret = db.getProfileData(Id)
        return json.dumps(ret)
    except Exception as e:
        return errorMessageJSON({'Operation':'get userprofile', 'Cause':'database error'})
    finally:
        db.disconnect()

@app.route('/users/image/<int:Id>', methods=['GET'])
def getUserpicture(Id):
    filename = "%d.jpg" % Id
    return send_file(filename, mimetype='image/jpeg');

@app.route('/users/login', methods=['POST'])
def checkLogin():
    jsonPayload = request.json

    try:
        db = connectDatabase()
        if "Password" in jsonPayload and "Username" in jsonPayload:
            ret = db.checkLogin(jsonPayload['Username'])
            if ret and pbkdf2_sha256.verify(jsonPayload['Password'], ret['Password']):
                return successMessageJSON({'Operation':'login user', 'Cookie':'supergeheim'})
            else:
                return errorMessageJSON({'Operation':'login user', 'Cause':'wrong username/password'})
    except Exception as e:
        return errorMessageJSON({'Operation':'login user', 'Cause':'database error'})
    finally:
        db.disconnect()

@app.route('/users/find/<int:PLZ>', methods=['GET'])
def findNearbyPeople(PLZ):    
    try:
        db = connectDatabase()

        if not checkAuthentification(db, request.cookies.get('session')):
            return errorMessageJSON({'Operation':'find users by PLZ', 'Cause':'not authentified'})

        ret = db.findPeopleByZIP(PLZ)
        return json.dumps(ret)
    except Exception as e:
        return errorMessageJSON({'Operation':'find users by PLZ', 'Cause':'database error'})
    finally:
        db.disconnect()

@app.route('/users/updateposition', methods=['POST'])
def updatePosition():
    jsonPayload = request.json

    try:
        db = connectDatabase()
        if not checkAuthentification(db, request.cookies.get('session')):
            return errorMessageJSON({'Operation':'update position', 'Cause':'not authentified'})

        if not ("Username" in jsonPayload and "CurrentLocationZIP" in jsonPayload and "CurrentLocationLAT" in jsonPayload and "CurrentLocationLNG" in jsonPayload):
            return errorMessageJSON({'Operation':'update position', 'Cause':'invalid input'})

        db.setPosition(jsonPayload['Username'], jsonPayload['CurrentLocationZIP'], jsonPayload['CurrentLocationLAT'], jsonPayload['CurrentLocationLNG'])
        return successMessageJSON({'Operation':'update position'})
    except Exception as e:
        return errorMessageJSON({'Operation':'update position', 'Cause':'database error', 'e':e.message})
    finally:
        db.disconnect()

@app.route('/users/updateprofile', methods=['POST'])
def updateProfile():
    jsonPayload = request.json

    try:
        db = connectDatabase()
        if not checkAuthentification(db, request.cookies.get('session')):
            return errorMessageJSON({'Operation':'update profile', 'Cause':'not authentified'})

        if not ("Username" in jsonPayload and "FirstName" in jsonPayload and "LastName" in jsonPayload):
            return errorMessageJSON({'Operation':'update profile', 'Cause':'invalid input'})

        db.setProfileData(jsonPayload['Username'], jsonPayload['FirstName'], jsonPayload['LastName'])
        return successMessageJSON({'Operation':'update profile'})
    except Exception as e:
        return errorMessageJSON({'Operation':'update profile', 'Cause':'database error', 'e':e.message})
    finally:
        db.disconnect()

@app.route('/users/updateprofileextra', methods=['POST'])
def updateProfileExtra():
    jsonPayload = request.json

    try:
        db = connectDatabase()
        if not checkAuthentification(db, request.cookies.get('session')):
            return errorMessageJSON({'Operation':'update profile extra', 'Cause':'not authentified'})

        if not ("Username" in jsonPayload):
            return errorMessageJSON({'Operation':'update profile extra', 'Cause':'invalid input'})
        

        d = {
        'Age': jsonPayload['Age'], 
        'Male': jsonPayload['Male'],
        'LookingFor': jsonPayload['LookingFor'],
        'Interests': jsonPayload['Interests']
        }

        db.setProfileExtra(jsonPayload['Username'], json.dumps(d))
        return successMessageJSON({'Operation':'update profile extra'})
    except Exception as e:
        return errorMessageJSON({'Operation':'update profile extra', 'Cause':'database error', 'e':e.message})
    finally:
        db.disconnect()


@app.route('/users/findabletill', methods=['POST'])
def setFindableTill():
    jsonPayload = request.json

    try:
        db = connectDatabase()
        if not checkAuthentification(db, request.cookies.get('session')):
            return errorMessageJSON({'Operation':'set findable till', 'Cause':'not authentified'})

        if not ("Username" in jsonPayload and "Time" in jsonPayload):
            return errorMessageJSON({'Operation':'set findable till', 'Cause':'invalid input'})

        #+seconds
        newTime = datetime.datetime.utcnow() + datetime.timedelta(0, int(jsonPayload['Time']))
        db.setFindableTill(jsonPayload['Username'], newTime)
        return successMessageJSON({'Operation':'set findable till', 'FindableTill':newTime.__str__()})
    except Exception as e:
        return errorMessageJSON({'Operation':'set findable till', 'Cause':'database error', 'e':e.message})
    finally:
        db.disconnect()

@app.route('/users/register', methods=['POST'])
def registerUser():
    jsonPayload = request.json

    try:
        db = connectDatabase()

        if not ("Password" in jsonPayload and "Username" in jsonPayload and "Email" in jsonPayload):
            return errorMessageJSON({'Operation':'register user', 'Cause':'invalid input'})

        passwordHash = pbkdf2_sha256.encrypt(jsonPayload['Password'], rounds=200000, salt_size=16)
        ret = db.addUser(jsonPayload['Username'], passwordHash, jsonPayload['Email'])
        if ret:
            return successMessageJSON({'Operation':'register user', 'UserId':ret})
        else:
            return errorMessageJSON({'Operation':'register user', 'Cause':'database error'})
    except Exception as e:
        return errorMessageJSON({'Operation':'register user', 'Cause':'database error', 'e':e.message})
    finally:
        db.disconnect()
    
app.run(host='0.0.0.0', port=8080, debug=True)
