import sqlite3 as lite
from datetime import datetime

class Userbase(object):
    """description of class"""
    def __init__(self):
        pass

    def dict_factory(self,  cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def rebuild(self):
        cur = self.con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS Users(
            Username TEXT UNIQUE,
            Password TEXT, 
            Email TEXT UNIQUE,

            CurrentLocationZIP INT,
            CurrentLocationLAT TEXT,
            CurrentLocationLNG TEXT,
            FindableTill DATETIME,

            FirstName TEXT, 
            LastName TEXT,
            Picture BLOB,
            ExtraProfileData TEXT
            )""")

    def connect(self,  database):
        self.con = lite.connect(database)
        with self.con:
            self.rebuild()
            self.con.row_factory = self.dict_factory
    def disconnect(self):
        self.con.close()
        


    #debugging only
    def getAllEntries(self):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT ROWID AS ID FROM Users")
            return cur.fetchall()
        return False
    
    def getEntry(self,  Id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT * FROM Users WHERE ROWID=?",  (Id, ))
            return cur.fetchone()
        return False

    #Profile stuff, public
    def findByName(self, name):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT ROWID AS Id FROM Users WHERE FirstName LIKE ? OR LastName LIKE ?", ("%" + name + "%", "%" + name + "%"))
            return cur.fetchall()
        return False

    def getProfileData(self, Id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT FirstName, LastName, CurrentLocationZIP, CurrentLocationLAT, CurrentLocationLNG, ExtraProfileData FROM Users WHERE ROWID=? AND FindableTill >= ?",  (Id, datetime.utcnow()))
            return cur.fetchone()
        return False

    def setProfileData(self, Username, FirstName, LastName):
        with self.con:
            cur = self.con.cursor()
            cur.execute("UPDATE Users SET FirstName=?, LastName=? WHERE Username=?",  (FirstName, LastName, Username))
            return cur.fetchone()
        return False

    def setProfileExtra(self, Username, Extra):
        with self.con:
            cur = self.con.cursor()
            cur.execute("UPDATE Users SET ExtraProfileData=? WHERE Username=?",  (Extra, Username))
            return cur.fetchone()
        return False

    def getProfilePicture(self, Id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT Picture FROM Users WHERE ROWID=?",  (Id, ))
            return cur.fetchone()
        return False

    def getSingleLocation(self, Id):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT CurrentLocationZIP, CurrentLocationLAT, CurrentLocationLNG FROM Users WHERE ROWID=? AND FindableTill >= ?",  (Id, datetime.utcnow()))
            return cur.fetchone()
        return False


    #Functionality stuff, public
    def findPeopleByZIP(self, ZIP):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT ROWID AS Id, FirstName, LastName, CurrentLocationZIP, CurrentLocationLAT, CurrentLocationLNG FROM Users WHERE CurrentLocationZIP=? AND FindableTill >= ?",  (ZIP, datetime.utcnow()))
            return cur.fetchall()
        return False

    #Account stuff, private. Only after authentification
    def setFindableTill(self, Username, FindableTill):
        with self.con:
            cur = self.con.cursor()
            cur.execute("UPDATE Users SET FindableTill=? WHERE Username=?", (FindableTill, Username))
            if(cur.rowcount == 1):
                return True
        return False

    def setPosition(self, Username, CurrentLocationZIP, CurrentLocationLAT, CurrentLocationLNG):
        with self.con:
            cur = self.con.cursor()
            cur.execute("UPDATE Users SET CurrentLocationZIP=?, CurrentLocationLAT=?, CurrentLocationLNG=? WHERE Username=?", (CurrentLocationZIP, CurrentLocationLAT, CurrentLocationLNG, Username))
            if(cur.rowcount == 1):
                return True
        return False

    def changePassword(self, Username, PasswordHash):
        with self.con:
            cur = self.con.cursor()
            cur.execute("UPDATE Users SET Password=? WHERE Username=?", (PasswordHash, Username))
            if(cur.rowcount == 1):
                return True
        return False

    def changeEmail(self, Username, Email):
        with self.con:
            cur = self.con.cursor()
            cur.execute("UPDATE Users SET Email=? WHERE Username=?", (Email, Username))
            if(cur.rowcount == 1):
                return True
        return False

    def checkLogin(self, Username):
        with self.con:
            cur = self.con.cursor()
            cur.execute("SELECT ROWID AS Id, Password FROM Users WHERE Username=?", (Username,))
            return cur.fetchone()
        return False

    def addUser(self, Username, PasswordHash, Email):
        with self.con:
            cur = self.con.cursor()
            cur.execute("INSERT INTO Users(Username, Password, Email) VALUES(?,?,?)", (Username, PasswordHash, Email))
            if(cur.rowcount == 1):
                return cur.lastrowid
        return False

    def deleteUser(self, Username):
        with self.con:
            cur = self.con.cursor()
            cur.execute("DELETE FROM Users WHERE Username=?", (Username,))
            if(cur.rowcount == 1):
                return True
        return False