# Dungeon-Dash-Project
Dungeon Crawler 2D Platformer Project made in Python.

Includes an account creation and login system connected with a PostgreSQL Database which stores account information and highscore data (note: The password is hashed before being appended to the database) 

The database.py file requires database information to be supplied before the program can work (currently it's all just asterisks ***). 

Run the main.py file to run the program, if error arises that assets are missing then an absolute path/directory must be hardcoded for each instance of loading an image 

e.g. 
"logo.png" must be converted to r"PATH\logo.png"

The leaderboard.py is a standalone program that displays highscores and may produce an error if there are not at least 5 accounts registered in the database due to the index threshold not being met.

