# login.py

# imports
from tkinter import *
from tkinter import messagebox
from tkinter.font import ITALIC
from PIL import Image, ImageTk
import re
from database import cursor, connection
import psycopg2
from psycopg2 import Error
import hashlib


class Login():
    """A class for the user to be able to login"""

    def __init__(self):
        """Initialise the login system"""

        # Create and configure the GUI
        self.login = Tk()
        self.login.title("Login")
        self.login.geometry("640x720")
        self.login.resizable(False, False)
        self.login.configure(background = "DodgerBlue4")
        self.login.iconphoto(False, PhotoImage(file="logo.png"))

        # Create background
        self.background_image = PhotoImage(file ="MainMenuBack2.png")
        self.background = Label(self.login, image = self.background_image)
        self.background.place(x = 0, y = 0, relwidth = 1, relheight = 1)

        # Create frames
        self.frame_headings = Frame(self.login)
        self.frame_headings.place(relx = 0.5, rely = 0.2, anchor=CENTER)

        self.frame_fields = Frame(self.login)
        self.frame_fields.place(relx = 0.5, rely = 0.6, anchor=CENTER)

        # Create logo image
        self.logo_img = PhotoImage(file ="logo.png")      
        self.logo = Label(self.frame_headings, image = self.logo_img)
        self.logo.grid(row = 0, column = 0)
        
        # Create game title label
        self.game_title = Label(self.frame_headings, text = "Dungeon Dash", bg = "LightSteelBlue1", font = ("default", 18))
        self.game_title.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Create interface title label
        self.interface_title = Label(self.frame_fields, text = "Login", font = ("default", 18))
        self.interface_title.grid(row = 0, column = 0, columnspan = 2,padx = 10, pady = 5)

        # Create entry fields
        self.username_field = Entry(self.frame_fields, width = 65, bg = "white", font = ("default", 10))
        self.username_field.grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 5, ipady = 8)

        self.password_field = Entry(self.frame_fields, width = 65, bg = "white", font = ("default", 10), show = '*')
        self.password_field.grid(row = 4, column = 0, columnspan = 2, padx = 10, pady = 5, ipady = 8)

        # Create labels
        self.label2 = Label(self.frame_fields, text = "Username")
        self.label2.grid(row = 1, column = 0, columnspan = 2, sticky="w", padx = 10)

        self.label3 = Label(self.frame_fields, text = "Password")
        self.label3.grid(row = 3, column = 0, columnspan = 2, sticky="w", padx = 10)

        # Create buttons
        self.login_button = Button(self.frame_fields, text = "Login", width = 65, bg = "green2", command = self.login_button)
        self.login_button.grid(row = 5, column = 0, columnspan = 2, padx = 10, pady = 10, ipady = 10)

        self.signup_button = Button(self.frame_fields, text = "Don't have an account? Sign Up", width = 25, bg = "cyan2", command = self.go_to_signup)
        self.signup_button.grid(row = 6, column = 0,  columnspan = 2, padx = 10, pady = 10, ipady = 10)

        self.login.mainloop()


    def login_button(self):
        """A function which runs when the user presses 'login' """

        # Retrieves the user's inputted credentials from entry fields
        self.username = self.username_field.get() 
        self.password = self.password_field.get()
        self.hashed_password = hashlib.sha256(self.password.encode()).hexdigest() # Hash 'password' using the SHA-256 Algorithm

        # Get email
        global useremail  
        useremail = self.get_email(self.username)

        # Pass the entry field inputs into validation functions 
        username_valid = self.validate_username(self.username)
        self.validate_password(self.username, self.hashed_password, username_valid)
    
    def validate_username(self, username):
        """A function which checks the inputted username"""
        cursor.execute("SELECT username FROM player WHERE username=(%s)", (username,))
        username_exist = cursor.fetchone()
        if username_exist:
            return True
        else:
            messagebox.showinfo(title = "Username doesn't exist", message = "The username you have entered doesn't exist.")
            self.username_field.delete(0, END)
            return False

    def validate_password(self, username, hashed_password, username_correct):
        """A function which checks the inputted password"""
        if username_correct:
            cursor.execute("SELECT hashed_password FROM player WHERE username=(%s)", (username,))
            password_in_database = cursor.fetchone()
            hashed_password = "('" + hashed_password + "',)"
            if str(password_in_database) == str(hashed_password):
                self.authorise_login()
            else:
                messagebox.showinfo(title = "Incorrect Password", message = "The password you have entered is incorrect.")
                self.password_field.delete(0, END)
    
    def get_email(self, username):
        cursor.execute("SELECT email FROM player WHERE username=(%s)", (username,))
        email = cursor.fetchone()
        return email

    def authorise_login(self): #Logs into the game
        print("Transition to Game")
        self.login.destroy()
        from dungeon_dash import Game
    
    def go_to_signup(self): # Function if the 'Sign Up' button is pressed
        print("Transition to Signup")
        self.login.destroy()
        from account_creation import Account_Creation
        Account_Creation()

if __name__ == "__main__":
    Login()
