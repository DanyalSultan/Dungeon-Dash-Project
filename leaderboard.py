# leaderboard.py

# imports
from tkinter import *
from PIL import Image, ImageTk
from database import cursor, connection
import psycopg2

class Leaderboard():
    """A class for the leaderboard"""

    def __init__(self):
        """Initialise the leaderboard system"""

        cursor.execute("SELECT high_score, username FROM player")
        self.highscores = cursor.fetchall()
        print(self.highscores)
        n = len(self.highscores)
        for i in range(1, n):
            current = self.highscores[i]
            index2 = i
            while index2 > 0 and self.highscores[index2 - 1] < current:
                self.highscores[index2] = self.highscores[index2 - 1]
                index2 -= 1
            
            self.highscores[index2] = current
            print(self.highscores)

        self.first = str(self.highscores[0])
        self.second = str(self.highscores[1])
        self.third = str(self.highscores[2])
        self.fourth = str(self.highscores[3])
        self.fifth = str(self.highscores[4])

        self.first = self.first.replace("[", "")
        self.first = self.first.replace("]", "")
        self.first = self.first.replace("(", "")
        self.first = self.first.replace(")", "")
        self.first = self.first.replace(",", "")

        self.second = self.second.replace("[", "")
        self.second = self.second.replace("]", "")
        self.second = self.second.replace("(", "")
        self.second = self.second.replace(")", "")
        self.second = self.second.replace(",", "")

        self.third = self.third.replace("[", "")
        self.third = self.third.replace("]", "")
        self.third = self.third.replace("(", "")
        self.third = self.third.replace(")", "")
        self.third = self.third.replace(",", "")

        self.fourth = self.fourth.replace("[", "")
        self.fourth = self.fourth.replace("]", "")
        self.fourth = self.fourth.replace("(", "")
        self.fourth = self.fourth.replace(")", "")
        self.fourth = self.fourth.replace(",", "")

        self.fifth = self.fifth.replace("[", "")
        self.fifth = self.fifth.replace("]", "")
        self.fifth = self.fifth.replace("(", "")
        self.fifth = self.fifth.replace(")", "")
        self.fifth = self.fifth.replace(",", "")

        self.create_gui()

    def create_gui(self):
        # Create and configure the GUI
        self.leaderboard = Tk()
        self.leaderboard.title("Leaderboard")
        self.leaderboard.geometry("640x720")
        self.leaderboard.resizable(False, False)
        self.leaderboard.configure(background = "DodgerBlue4")
        self.leaderboard.iconphoto(False, PhotoImage(file = "logo.png"))

        # Create background
        self.background_image = PhotoImage(file = "MainMenuBack2.png")
        self.background = Label(self.leaderboard, image = self.background_image)
        self.background.place(x = 0, y = 0, relwidth = 1, relheight = 1)

        # Create frames
        self.frame_headings = Frame(self.leaderboard)
        self.frame_headings.place(relx = 0.5, rely = 0.2, anchor=CENTER)

        self.frame_fields = Frame(self.leaderboard)
        self.frame_fields.place(relx = 0.5, rely = 0.6, anchor=CENTER)

        # Create logo image
        self.logo_img = PhotoImage(file = "logo.png")      
        self.logo = Label(self.frame_headings, image = self.logo_img)
        self.logo.grid(row = 0, column = 0)
        
        # Create game title label
        self.game_title = Label(self.frame_headings, text = "Dungeon Dash", bg = "LightSteelBlue1", font = ("default", 18))
        self.game_title.grid(row = 1, column = 0, padx = 10, pady = 10)

        # Create interface title label
        self.interface_title = Label(self.frame_fields, text = "Leaderboard", font = ("default", 18))
        self.interface_title.grid(row = 0, column = 0, columnspan = 2,padx = 10, pady = 5)

        # Create labels
        self.label1 = Label(self.frame_fields, text = "1st: " + str(self.first), bg = "gold4")
        self.label1.grid(row = 1, column = 0, columnspan = 2, sticky="w", padx = 10, ipady = 10)

        self.label2 = Label(self.frame_fields, text = "2nd: " + str(self.second), bg = "grey50")
        self.label2.grid(row = 2, column = 0, columnspan = 2, sticky="w", padx = 10, ipady = 10)

        self.label3 = Label(self.frame_fields, text = "3rd: " + str(self.third), bg = "saddle brown")
        self.label3.grid(row = 3, column = 0, columnspan = 2, sticky="w", padx = 10, ipady = 10)

        self.label4 = Label(self.frame_fields, text = "4th: " + str(self.fourth))
        self.label4.grid(row = 4, column = 0, columnspan = 2, sticky="w", padx = 10, ipady = 10)

        self.label5 = Label(self.frame_fields, text = "5th: " + str(self.fifth))
        self.label5.grid(row = 5, column = 0, columnspan = 2, sticky="w", padx = 10, ipady = 10)

        self.leaderboard.mainloop()


leaderboard = Leaderboard()
