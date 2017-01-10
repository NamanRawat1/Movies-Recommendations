# Movies-Recommendations
Database and Machine learning in Python

The aim is to create a database from the 3 .csv files (containing informations about movies and users rating movies), define a related graphic interface with some specific requests, and build a movies recommendation system for new users.

Files :
- PythonProject.py : python code
- movie.csv : contains movie id, movie name, release year, director, budget, review rate
- users.csv : contains user id, anonym name
- ratings.csv : contains user id, movie id, rate (given by a user to a movie)
- RelationalDiagram.jpg : relational diagram of the final database

Method :
- Database creation with "sqlite3"
- Files import and data treatment with "pandas" (+ "currencyconverter" to convert movie budgets in a same currency and "name" to define random names to the anonym users)
- Data import into database ("sqlite3")
- Definition of SQL requests and functions used in the graphic interface
- Creation of the graphic environnemement with "tkinter"
- Creation of the recommendations system (use of personnalized algorithms of k-means and NNS with adapted similarity)

To use the code, download the 3 .csv files in a folder and write the folder path at the indicated location (l. 37), then run the source.
openmanager() to open the graphic interface
randomv() to create preferences of a random user
NNSRecommendations(user) to return 10 best recommendations per genre to the user 
(put preferences of the user in paramater, such as randomv() returns, ex: NNSRecommendation(randomv()))


N.B. : In each part some functions may seem long (in script) ; as the program is iterating a large number of actions, i tried as much as possible not to use general and predefined procedures (with a minimum number of actions) when a shorter way was clearly identifiable.
However, i did not merge all parts together in order to understand and modify (if necessary) easily the code
