# Movies-Recommendations
Database and Machine learning in Python

The aim is to create a database from the 3 .csv files (containing informations about movies and users rating movies), define a related graphic interface with some specific requests, and build a movies recommendation system for new users.

Method :
- Database creation with "sqlite3"
- Files import and data treatment with "pandas" (+ "currencyconverter" to convert movie budgets a same currency and "name" to define random names to the anonym users)
- Data import into database ("sqlite3")
- Definition of SQL requests and functions used in the graphic interface
- Creation of the graphic environnemement with "tkinter"
- Creation of the recommendations system (use of personnalized algorithms of k-means and NNS with adapted similarity)

To use the code, download the 3 .csv files in a folder and write the folder path at the indicated location (l. 37), then run the source.
openmanager() to open the graphic interface
randomv() to define preferences of a random user
NNSRecommendations(user) to return 10 best recommendations per genre to the user 
(put preferences of the user in paramater, such as randomv() returns)
