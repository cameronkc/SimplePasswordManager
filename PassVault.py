import secrets
import string
import sqlite3, hashlib
from tkinter import *
from tkinter import simpledialog
from functools import partial

#Database
with sqlite3.connect("passVault.db") as db:
    cursor = db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS vault(
id INTEGER PRIMARY KEY,
website TEXT NOT NULL,
username TEXT NOT NULL,
password TEXT NOT NULL)
""")

#Create popup

def popUp(text):
    answer = simpledialog.askstring("input string", text)
    return answer


cursor.execute("""
CREATE TABLE IF NOT EXISTS masterpassword(
id INTEGER PRIMARY KEY,
password TEXT NOT NULL)
""")

#Initialize Window
window = Tk()
window.title("PassVault")


def hashPassword(input):
    hash = hashlib.md5(input)
    hash = hash.hexdigest()

    return hash


def firstScreen():

    window.geometry("500x150")
    lbl = Label(window, text= "Welcome to PassVault, please Generate a Master Password or Create Your Own")
    lbl.config(anchor=CENTER)
    lbl.pack()

    btn = Button(window, text = "Generate", command = lambda: generatePassScreen())
    btn.config(anchor=CENTER)
    btn.pack()

    btn2 = Button(window, text = "Create My Own", command = lambda : createOwnPassScreen())
    btn2.config(anchor=CENTER)
    btn2.pack(pady=10)

    def generatePassScreen():

        for widget in window.winfo_children():
            widget.destroy()
        window.geometry("500x150")
        btn = Button(window, text="Generate Master Password", command= lambda: [lbl.config(text=passwordGen(15)), window.clipboard_clear(), window.clipboard_append(lbl.cget("text"))])
        btn.config(anchor=CENTER)
        btn.pack()

        lbl = Label(window)
        lbl.pack()


        btn2 = Button(window, text="Save Password", command = lambda: [savePassword(lbl.cget("text"))])
        btn2.config(anchor=CENTER)
        btn2.pack()



    def createOwnPassScreen():

        for widget in window.winfo_children():
            widget.destroy()
        window.geometry("500x150")

        lbl = Label(window, text="Create Master Password")
        lbl.config(anchor=CENTER)
        lbl.pack()

        txt = Entry(window, width=20, show = '*')
        txt.pack()
        txt.focus()

        lbl2 = Label(window, text="Re-enter Password")
        lbl2.config(anchor=CENTER)
        lbl2.pack()

        txt1=Entry(window, width=20, show = '*')
        txt1.pack()


        def checkPassMatch():
            if txt.get() == txt1.get():
                savePassword(txt.get())
            else:
                lbl2.config(text="Passwords do not match")

        btn = Button(window, text = "Save Password", command= lambda: checkPassMatch())
        btn.pack(pady=10)


def savePassword(pwrd):
    hashedpassword = hashPassword(pwrd.encode("UTF-8"))
    insert_password = """INSERT INTO masterpassword(password)
    VALUES(?) """
    cursor.execute(insert_password, [(hashedpassword)])
    db.commit()

    passwordVault()


#counter for max login attempts
counter = 0

def loginScreen():
    window.geometry("305x150")
    lbl = Label(window, text="Enter Master Password")
    lbl.config(anchor=CENTER)
    lbl.pack()

    lbl1 = Label(window)
    lbl1.pack()

    txt = Entry(window, width=20, show="*")
    txt.pack()
    txt.focus()

    def getMasterPassword():
        checkHashedPassword = hashPassword(txt.get().encode("UTF-8"))
        cursor.execute("SELECT * FROM masterpassword WHERE id = 1 AND password = ?", [(checkHashedPassword)])
        print(checkHashedPassword)
        return cursor.fetchall()


    def checkPassword():
        global counter
        match = getMasterPassword()
        print(match)
        if counter < 3:
            if match:
                passwordVault()
            else:
                counter += 1
                txt.delete(0, 'end')
                lbl1.config(text="Wrong Password! You have made %s/3 attempts" % counter)
        else:
            lbl1.config(text="Max attempts exceeded")


    btn = Button(window, text="Enter", command=checkPassword)
    btn.pack(pady=10)

def passwordVault():
    for widget in window.winfo_children():
        widget.destroy()

    def addEntry():
        txt1 = "Website"
        txt2 = "Username"
        txt3 = "Password"

        website = popUp(txt1)
        username = popUp(txt2)
        password = popUp(txt3)

        insert_fields = """INSERT INTO vault(website, username, password)
        VALUES(?, ?, ?)
        """

        cursor.execute(insert_fields, (website, username, password))
        db.commit()

        passwordVault()

    def removeEntry(input):
        cursor.execute("DELETE FROM vault WHERE id = ?", (input,))
        db.commit()

        passwordVault()

    window.geometry("700x350")

    lbl = Label(window, text="Password Vault")
    lbl.grid(column=1)

    btn = Button(window, text="Add a password", command=addEntry)
    btn.grid(column=1, pady=10)

    lbl = Label(window, text="Website")
    lbl.grid(row=2, column=0, padx=80)
    lbl = Label(window, text="Username")
    lbl.grid(row=2, column=1, padx=80)
    lbl = Label(window, text="Password")
    lbl.grid(row=2, column=2, padx=80)

    cursor.execute("SELECT * FROM vault")
    if(cursor.fetchall() != None):
        i=0
        while True:
            cursor.execute("SELECT * FROM vault")
            array = cursor.fetchall()

            lbl1 = Label(window, text=(array[i][1]), font=("Helvetica", 12))
            lbl1.grid(column=0, row=i+3)
            lbl1 = Label(window, text=(array[i][2]), font=("Helvetica", 12))
            lbl1.grid(column=1, row=i+3)
            lbl1 = Label(window, text=(array[i][3]), font=("Helvetica", 12))
            lbl1.grid(column=2, row=i+3)

            btn = Button(window, text="Delete", command=partial(removeEntry, array[i][0]))
            btn.grid(column=3, row=i+3, pady=10)

            i= i+1

            cursor.execute("SELECT * FROM vault")
            if(len(cursor.fetchall()) <= i):
                break

def passwordGen(password_length):
    characters = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(characters) for i in range(password_length))

    return password

def copy(txt):
    window.clipboard_clear()
    window.clipboard_append(txt)

cursor.execute("SELECT * FROM masterpassword")

if cursor.fetchall():
    loginScreen()
else:
    firstScreen()

window.mainloop()