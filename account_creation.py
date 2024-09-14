# account_creation.py

# imports
from asyncio.windows_events import NULL
import email
from tkinter import *
from tkinter import messagebox
from PIL import Image, ImageTk
import re
from database import cursor, connection
import psycopg2
import hashlib


class Account_Creation():
    """A class for the user to be able to create an account"""

    def __init__(self):
        """Initialise the account creation system"""

        # Create and configure the GUI
        self.signup = Tk()
        self.signup.title("Sign Up")
        self.signup.geometry("1280x720")
        self.signup.resizable(False, False)
        self.signup.configure(background = "DodgerBlue4")
        self.signup.iconphoto(False, PhotoImage(file ="logo.png"))

        # Create background
        self.background_image = PhotoImage(file ="MainMenuBack1.png")
        self.background = Label(self.signup, image = self.background_image)
        self.background.place(x = 0, y = 0, relwidth = 1, relheight = 1)

        # Create frames
        self.frame_headings = Frame(self.signup)
        self.frame_headings.place(relx = 0.5, rely = 0.17, anchor=CENTER)

        self.frame_fields = Frame(self.signup)
        self.frame_fields.place(relx = 0.5, rely = 0.66, anchor=CENTER)

        # Create logo image
        self.logo_img = PhotoImage(file ="logo.png")      
        self.logo = Label(self.frame_headings, image = self.logo_img)
        self.logo.grid(row = 0, column = 0)
        
        # Create Game title Label
        self.game_title = Label(self.frame_headings, text = "Dungeon Dash", bg = "LightSteelBlue1", font = ("default", 18)) ######
        self.game_title.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Create interface title label
        self.interface_title = Label(self.frame_fields, text = "Create an account", font = ("default", 18)) ##### bg = "slate gray"
        self.interface_title.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 5)

        # Create entry fields
        self.email_field = Entry(self.frame_fields, width = 65, bg = "white", font = ("default", 10))
        self.email_field.grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 5, ipady = 8)

        self.username_field = Entry(self.frame_fields, width = 65, bg = "white", font = ("default", 10))
        self.username_field.grid(row = 5, column = 0, columnspan = 2, padx = 10, pady = 5, ipady = 8)

        self.password_field = Entry(self.frame_fields, width = 65, bg = "white", font = ("default", 10), show = '*')
        self.password_field.grid(row = 7, column = 0, columnspan = 2, padx = 10, pady = 5, ipady = 8)

        self.confirmation_password_field = Entry(self.frame_fields, width = 65, bg = "white", font = ("default", 10), show = '*')
        self.confirmation_password_field.grid(row = 9, column = 0, columnspan = 2, padx = 10, pady = 5, ipady = 8)

        # Create labels
        self.label1 = Label(self.frame_fields, text = "Email")
        self.label1.grid(row = 1, column = 0, columnspan = 2, sticky="w", padx = 10)

        self.label1 = Label(self.frame_fields, text = "example: dungeon@mail.com", font = ("default", 8), fg = "grey39")
        self.label1.grid(row = 3, column = 0, columnspan = 2, sticky="w", padx = 10)

        self.label2 = Label(self.frame_fields, text = "Username")
        self.label2.grid(row = 4, column = 0, columnspan = 2, sticky="w", padx = 10)

        self.label3 = Label(self.frame_fields, text = "Password")
        self.label3.grid(row = 6, column = 0, columnspan = 2, sticky="w", padx = 10)

        self.label4 = Label(self.frame_fields, text = "Confirmation Password")
        self.label4.grid(row = 8, column = 0, columnspan = 2, sticky="w", padx = 10)

        self.label6 = Label(self.frame_fields, text = ". Password must contain valid characters only.")
        self.label6.grid(row = 10, column = 0, columnspan = 2, sticky="w", padx = 10)

        self.label7 = Label(self.frame_fields, text = ". Password must contain at least 8 characters.")
        self.label7.grid(row = 11, column = 0, columnspan = 2, sticky="w", padx = 10)

        self.label8 = Label(self.frame_fields, text = ". Password must contain at least one uppercase letter.")
        self.label8.grid(row = 12, column = 0, columnspan = 2, sticky="w", padx = 10)

        self.label9 = Label(self.frame_fields, text = ". Password must contain at least one number")
        self.label9.grid(row = 13, column = 0, columnspan = 2, sticky="w", padx = 10)

        # Create buttons
        self.signup_button = Button(self.frame_fields, text = "Sign Up", width = 25, bg = "green2", command = self.create_account)
        self.signup_button.grid(row = 14, column = 0, padx = 10, pady = 10)

        self.login_button = Button(self.frame_fields, text = "Already have an account? Login", width = 25, bg = "cyan2", command = self.go_to_login_interface)
        self.login_button.grid(row = 14, column = 1, padx = 10, pady = 10)

        self.signup.mainloop()

    def create_account(self):
        """A function which runs when the user presses 'sign up' """

        # Retrieves the user's inputted credentials from entry fields
        self.email = self.email_field.get() 
        self.username = self.username_field.get() 
        self.password = self.password_field.get() 
        self.confirmation_password = self.confirmation_password_field.get() 

        # Pass the entry field inputs into validation functions 
        email_valid = self.check_email(self.email)
        username_valid = self.check_username(self.username)
        password_valid = self.check_password(self.password, self.confirmation_password)
        self.validate_signup(self.email, self.username, self.password, email_valid, username_valid, password_valid)

    def check_email(self, email):
        """A function to check a user's email"""
        format = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")
        if re.fullmatch(format, email):
            print("Valid Email Input")
            cursor.execute("SELECT email FROM player WHERE email=(%s)", (email,))
            email_exist = cursor.fetchone()
            if email_exist: # If email exists in database
                messagebox.showinfo(title = "Email in use", message = "Email already in use, please enter a different email or login")
                return False
            else:
                return True
        else:
            messagebox.showinfo(title = "Invalid Email", message = "The email you entered is invalid")
            return False
    
    def check_username(self, username):
        """A function to check a user's username"""
        username_valid = False
        while username_valid == False:
            for index in range (len(username)):            
                if ord(username[index]) in range (33,127): # Are all characters valid?
                    username_valid = True
                    if username_valid:
                        print("Valid Username Input")
                        cursor.execute("SELECT username FROM player WHERE username=(%s)", (username,))
                        username_exist = cursor.fetchone()
                        if username_exist:
                            messagebox.showinfo(title = "Username taken", message = "Username already taken, enter a different username")
                            return False
                        else:
                            return True
                    else:
                        messagebox.showinfo(title = "Invalid Username", message = "The username you entered is invalid")
                        return False
                else:
                    messagebox.showinfo(title = "Invalid Username", message = "The username you entered has invalid characters")
                    return False
                
    def check_password(self, password, confirmation_password):
        """A function to check a user's password and confirmation password"""
        if password == confirmation_password:
            print("Password matches confirmation password")
            for index in range (len(password)):
                if ord(password[index]) in range (33, 127): # Are all characters valid?
                    print("Valid password characters")
                    uppercase = re.compile(r"([A-Z]+)")
                    if re.search(uppercase, password): # At least one uppercase letter
                        print("Uppercase letter exists")
                        if re.search("[a-zA-Z]*\d[a-zA-Z0-9]*", password): # At least one number
                            print("Digit exists")
                            if len(password) >= 8:
                                print("Password is at least 8 characters")
                                return True
                            else:
                                messagebox.showinfo(title = "Password Error", message = "Password must contain at least 8 characters.")
                                return False 
                        else:
                            messagebox.showinfo(title = "Password Error", message = "Password must contain at least one number.")
                            return False        
                    else:
                        messagebox.showinfo(title = "Password Error", message = "Password must contain at least one uppercase letter.")
                        return False
                else:
                    messagebox.showinfo(title = "Password Error", message = "Password must contain valid characters only.")
                    return False
        else:
            messagebox.showinfo(title = "Password Error", message = "Password doesn't match Confirmation Password")
            return False
    
    def validate_signup(self, email, username, password, isemailvalid, isusernamevalid, ispasswordvalid):
        """A function to hash a user's password and insert credentials into database"""
        if isemailvalid and isusernamevalid and ispasswordvalid: # If validations are successful
            print("All inputs are valid")
            print("The password to be hashed is: ", password)
            hashed_password = hashlib.sha256(password.encode()).hexdigest() # Hash 'password' using the SHA-256 Algorithm
            print(hashed_password)
            cursor.execute("INSERT INTO player (email, username, hashed_password, high_score) VALUES(%s, %s, %s, %s)", (email, username, hashed_password, NULL))
            connection.commit()
            print("1 Record inserted successfully")
            self.go_to_login_interface()
        else:
                if isemailvalid == False:
                    self.email_field.delete(0, END)
                if isusernamevalid == False:
                    self.username_field.delete(0, END)
                if ispasswordvalid == False:
                    self.password_field.delete(0, END)
                    self.confirmation_password_field.delete(0, END)
    
    def go_to_login_interface(self): # Function if the 'Login' button is pressed
        print("Transition to login interface")
        self.signup.destroy()
        from login import Login
        Login()

if __name__ == "__main__":
    Account_Creation()
