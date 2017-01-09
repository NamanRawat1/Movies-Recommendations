"""
Created on Thu Jan  5 22:23:21 2017

@author: Roman Gambelin

"""

#########################################
### Python databases project : Cinema ###
#########################################


"""
    SUMMARY :
    - 56  : Database Creation
    - 135 : Data Import and Treatment
    - 346 : Data Import into Database
    - 402 : Definition of SQL Requests
    - 673 : Creation of Graphic Interface
    - 732 : Recommendations
"""


## Modules import
print("\nImporting modules\n")
import sqlite3 as sql3
import pandas as pd
import numpy as np
import tkinter as tk
import random as rdm
## !! These modules are not included in Anaconda basic distribution, to be installed !!
import currency_converter as CC
import names


## Stock .csv files folder (Please enter your path)
Folder="C:\\Users\\Isa\\Desktop\\M1 Courses\\Projet Python S1\\"
moviesfname="movie.csv"
ratingsfname="rating.csv"
usersfname="users_anonym.csv"


"""
    FUNCTIONS & PROCEDURES TO BE USED :
    - openmanager()    : open the graphic interface to search the basic requests
    - randomv(p=1/5)   : return a random rates list over a film selection
        * p      : probability for the user to rate each movie
    - NNSRecommendation(vector, k=15, mode='', nmovie=3)     : return 10 recommendations per genre
        * vector : random rates list of the user to be recommended
        * k      : number of neighbours used for the k-means method
        * mode   : use cosinus similarity when = to 'cos', special (or basic) similarity otherwise (see code)
        * nmovie : minimum number of movies that users and its neighbours both have rated when using the basic similarity
"""


### DATABASE CREATION ###

## Connect to cinema database (or create it if doesn't exist)
print("\nConnecting to DB\n")
conn = sql3.connect(':memory:')

cursor = conn.cursor()

print("\nCreating tables in DB\n")

## Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Users(
     U_Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     U_Name TEXT
)
""")

## Create film directors table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Directors(
     D_Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     D_Surname TEXT,
     D_Firstname TEXT
)
""")

## Create movies table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Movies(
     M_Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     M_Name TEXT,
     M_Year INTEGER VARCHAR(4),
     M_Budget REAL,
     M_Genre TEXT,
     M_Rate REAL
)
""")

## Create movie marks table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Marks(
     Mark REAL,
     U_Id INTEGER,
     M_Id INTEGER,
     FOREIGN KEY (U_Id) REFERENCES Users(U_Id),
     FOREIGN KEY (M_Id) REFERENCES Movies(M_Id)
)
""")

## Create movie makings table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Makings(
     D_Id INTEGER,
     M_Id INTEGER,
     FOREIGN KEY (D_Id) REFERENCES Users(D_Id),
     FOREIGN KEY (M_Id) REFERENCES Movies(M_Id)
)
""")

## Create genres table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Genres(
     G_Id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
     G_Name TEXT
)
""")

## Create movie relations to genre table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Relations(
     M_Id INTEGER,
     G_Id INTEGER,
     FOREIGN KEY (M_Id) REFERENCES Movies(M_Id),
     FOREIGN KEY (G_Id) REFERENCES Genres(G_Id)
)
""")


### DATA IMPORT AND TREATMENT ###

## Convert .csv files in dataframes
print("\nFiles conversion to dataframe\n")
movies=pd.read_csv(Folder+moviesfname,sep=";")
ratings=pd.read_csv(Folder+ratingsfname,sep=";")
users=pd.read_csv(Folder+usersfname,sep=";")

## Stocks file sizes
nm=len(movies)
nr=len(ratings)
nu=len(users)

print("\nIdentifying Directors' informations\n")
## Creating directors dataframe and completing movies frame with directors surnames, firstnames and ID
directors=[]
nd=len(directors)
## Initializing list of the directors' surnames for each movie
msn=[""]*nm
## Initializing list of the directors' firstnames for each movie
mfn=[""]*nm
## Initializing list of the directors' Id for each movie
mdid=[""]*nm
## Initializing directors' surnames list
dsn=[]
## Initializing directors' firstnames list
dfn=[]
## Initializing directors' Id list
did=[]
## Initializing directors' Id
Id=1
## Initializing movies' df Index
i=0
## For the director d of each movie
for d in movies.director:
    ## If there director there is
    if d!=" ":
        l=0
        ## Capturing length of the director's name
        n=len(d)
        ## Capturing firstname (or surname in the case there is no barspace in the name)
        while d[l]!=" " and l<(n-1):
            l+=1
        ## Surname case
        if l==(n-1):
            msn[i]=d
        ## Firstname case
        else:
            mfn[i]=d[0:l]
            msn[i]=d[(l+1)::]
        ## Looking if the director is already registered
        index=0
        ## Case where there is no director registered yet
        if nd==0:
            directors.append(d)
            dsn.append(msn[i])
            dfn.append(mfn[i])
            did.append(Id)
            mdid[i]=Id
            nd+=1
            Id+=1
        ## Otherwise we compare director d to all directors in directors list
        else:
            while d!=directors[index] and index<(nd-1):
                index+=1
            ## And add it to it if we don't find it
            if index==(nd-1) and directors[index]!=d:
                directors.append(d)
                dsn.append(msn[i])
                dfn.append(mfn[i])
                did.append(Id)
                mdid[i]=Id
                nd+=1
                Id+=1
            ## Otherwise we just add its already existing Id to movies df
            else:
                mdid[i]=index+1
    i+=1
    
## Stocking final number of directors
nd=len(directors)
## Adding new directors' informations to movies df
movies["did"]=mdid
movies["dfirstname"]=mfn
movies["dsurname"]=msn
## Creating directors df
directors=pd.DataFrame({"id":did,"firstname":dfn,"surname":dsn})
               
## Function for genres identification (assign list of genres id to each movie and create a genres df, as previously)
def genreidentifying(data):
    genres=[]
    gindex=[]
    ng=len(genres)
    gi=1
    N=len(data)
    moviegenresid=[[]]*N
    i=0
    ## For the list of genres g of each movie
    for g in data.genre:
        ## If there is a genre
        if g!=' ':
            n=len(g)
            ## Create a local list for genres id of the movie
            localgenresid=[]
            ## Initializing character index
            l=1
            ## While it is not the end of the genres list
            a=0
            while l<(n-1):
                #print("a")
                #print(a)
                ## Stocking specific character index
                p=l
                ## While we're still on the same genre (no "," or ")" to separate or finish)
                b=0
                while g[l]!="," and l<(n-1):
                    #print("b")
                    #print(b)
                    l+=1
                    b+=1
                ## Stocking genre
                genre=g[p:l]
                ## Looking if the genre is already registered (same system than directors ident.)
                if ng==0:
                    genres.append(genre)
                    gindex.append(gi)
                    localgenresid.append(gi)
                    gi+=1
                    ng+=1
                else:
                    index=0
                    c=0
                    while genre!=genres[index] and index<(ng-1):
                        #print("c")
                        #print(c)
                        index+=1
                        c+=1
                    if index==(ng-1) and genres[index]!=genre:
                        localgenresid.append(gindex[index])
                        genres.append(genre)
                        gindex.append(gi)
                        localgenresid.append(gi)
                        gi+=1
                        ng+=1
                    else:
                        localgenresid.append(gindex[index])
                    if l<(n-1):
                        l+=1
                a+=1
            moviegenresid[i]=localgenresid
        i+=1
    data["moviegenresid"]=moviegenresid
    genres=pd.DataFrame({'genre':genres,'id':gindex})
    return(genres)

## Genres identification
print("\nIdentifying genres\n")
genres=genreidentifying(movies)       
## Stocking number of genres 
ng=len(genres)

## Function for currencies conversion
cc=CC.CurrencyConverter()
def currencyconversion(array):
    ## Creation of the list of the 10 first naturel integers in string type
    intlist=[]
    for i in list(range(10)):
        intlist+=[str(i)]
    ## For every budget b in list
    index=0
    for b in array:
        ## If there is a budget
        b=str(b)
        if b!=' ':
            ## Cleaning amount informaton (if something is written after the money amount it removes it)
            n=len(b)
            if b[n-1] not in intlist:
                n+=-1
                while b[n-1] not in intlist:
                    n+=-1
                array[index]=b[0:n]
            ## And if the budget is not in dollar
            if b[0] not in intlist:
                i=1
                ## Get currency
                while b[i] not in intlist+[' ']:
                    i+=1
                currency=b[0:i]
                if b[i]==[' ']:
                    i+=1
                ## Special character cases
                if currency=="€":
                    currency="EUR"
                elif currency=="£":
                    currency="GBP"
                elif currency=="¥":
                    currency="JPY"
                ## Convert and assign new budget in dollar
                array[index]=cc.convert(array[index][i::],currency,'USD')
        index+=1
        
## Convert all movie budgets in USD
print("\nConverting movie budgets in USD\n")
currencyconversion(movies.budget)

## Asign randomly a full name (surname + firstname) to each user
print("\nAssigning random names to users\n")
for i in range(nu):
    users.username[i]=names.get_full_name()
    

### DATA IMPORT INTO DATABASE ###
    
print("\n Fill DB with dataframes values :")

## Fill directors table with directors dataframe
print("- Directors")
for (Id, FName, SName) in directors[['id','firstname','surname']].values:
        cursor.execute("""
                   INSERT INTO Directors(D_Id,D_Surname,D_Firstname) VALUES(?, ?, ?)
                   """,
                   (Id, SName, FName))

## Fill genres table with genres dataframe
print("- Genres")
for (Id,Genre) in genres[['id','genre']].values:
    cursor.execute("""
                   INSERT INTO Genres(G_Id,G_Name) VALUES(?, ?)
                   """,
                   (Id,Genre))       
        
## Fill movies, makings and relations table with movies dataframe
print("- Movies, Makings & Relations")
for (MId, Name, Year, Genre, Budget, Rate, DId, MGId) in movies[['movieid','moviename','year','genre','budget','rate','did','moviegenresid']].values:
    cursor.execute("""
                   INSERT INTO Movies(M_Id,M_Name,M_Year,M_Budget,M_Genre,M_rate) VALUES(?, ?, ?, ?, ?, ?)
                   """,
                   (MId, Name, Year, Budget, Genre, Rate))
    if DId!='':
        cursor.execute("""
                       INSERT INTO Makings(D_Id,M_Id) VALUES(?, ?)
                       """,
                       (DId,MId))
    if MGId!=[]:
        for gid in MGId:
            cursor.execute("""
                           INSERT INTO Relations(M_Id,G_Id) VALUES(?, ?)
                           """,
                           (MId, gid))

## Fill users table with users dataframe
print("- Users")
for (Id, Name) in users[['userid','username']].values:
    cursor.execute("""
                   INSERT INTO Users(U_Id,U_Name) VALUES(?, ?)
                   """,
                   (Id, Name))
    
## Fill ratings table with ratings dataframe
print("- Ratings")
for (Mark, UId, MId) in ratings[['rating','userid','movieid']].values:
    cursor.execute("""
                   INSERT INTO Marks(Mark,U_Id,M_Id) VALUES(?, ?, ?)
                   """,
                   (Mark, UId, MId))
    

### DEFINITION OF SQL REQUESTS AND ASSOCIATED FUNCTIONS ###

print("\nDefining SQL Requests :")

## By year :
print("- By year")
    
#1 TOP 5 Movies (using users marks) in the given year  
r1="""
   SELECT M_Name, AVG(Mark) AS Rate
   FROM Marks
   INNER JOIN Movies
       ON Marks.M_Id = Movies.M_Id
   WHERE M_Year = ?
   GROUP BY Marks.M_Id
   ORDER BY Rate DESC
   LIMIT 5
   """
def dr1(parameter):
    cursor.execute(r1,(parameter,))
    output=cursor.fetchall()
    if output!=[]:
        label="Top 5 movies in "+str(parameter)+" :\n\n"
        for m in output:
            label+="- "+str(m[0])+" : "+str(m[1])+"\n"
    else:
        label="No movie found this year"
    return(label)  
    
#2 Movie with the hight budget in the given year
r2="""
   SELECT M_Name, M_Budget
   FROM Movies
   WHERE M_Year = ? AND M_Budget!=' '
   ORDER BY M_Budget DESC
   LIMIT 1
   """
def dr2(parameter):
    cursor.execute(r2,(parameter,))
    output=cursor.fetchall()
    if output!=[]:
        label="Movie with the hight budget in "+str(parameter)+" :\n\n- "+str(output[0][0])+" : "+str(output[0][1])+"$"
    else:
        label="No movie found this year"
    return(label)

#3 Best movies by genre in a given year
r3="""
   SELECT G_Name, M_Name, AVG(Mark) AS Rate
   FROM Marks
   INNER JOIN Movies
       ON Marks.M_Id = Movies.M_Id
   INNER JOIN Relations
       ON Marks.M_Id = Relations.M_Id
   INNER JOIN Genres
       ON Relations.G_Id = Genres.G_Id
   WHERE M_Year = ?
   GROUP BY Genres.G_Id
   ORDER BY Rate DESC
   """ 
def dr3(parameter):
    cursor.execute(r3,(parameter,))
    output=cursor.fetchall()
    if output!=[]:
        label="Best movies by genre in "+str(parameter)+" :\n\n"
        for m in output:
            label+="- "+str(m[0])+' : "'+str(m[1])+"'\n"
    else:
        label="No movie found this year"
    return(label)
   
#4 User who rated the highest number of films in the given year
r4="""
   SELECT U_Name, COUNT(Marks.M_Id) AS Nb
   FROM Marks
   INNER JOIN Users, Movies
       ON Marks.U_Id = Users.U_Id AND Marks.M_Id = Movies.M_Id
   WHERE M_Year = ?
   GROUP BY Marks.U_Id
   ORDER BY Nb DESC
   LIMIT 1
   """
def dr4(parameter):
    cursor.execute(r4,(parameter,))
    output=cursor.fetchall()
    if output!=[]:
        label="User who rated the highest number of films in "+str(parameter)+" :\n\n"
        label+='- "'+str(output[0][0])+'" with '+str(output[0][1])+" rates"
    else:
        "No user found this year"
    return(label)
   
## By movie :
print("- By movie")

#5 Film's description
r5="""
   SELECT *
   FROM Movies
   WHERE M_Name = ?
   """
def dr5(parameter):
   cursor.execute(r5,(parameter,))
   output=cursor.fetchall()
   if output!=[]:
       label='Informations about "'+str(parameter)+'" :\n\n'
       label+="- Movie Id : "+str(output[0][0])+"\n- Year : "+str(output[0][2])+"\n- Budget : "+str(output[0][3])+"$\n- Genres : "+str(output[0][4])+"\n- Review rate : "+str(output[0][5])
   else:
       label="Movie not found"
   return(label)

#6 Rates mean and standard error for the given movie
r6="""
   SELECT AVG(Mark), AVG(Mark*Mark)-AVG(Mark)*AVG(Mark)
   FROM Marks
   INNER JOIN Movies
       ON Marks.M_Id = Movies.M_Id
   WHERE M_Name = ?
   """
def dr6(parameter):
    cursor.execute(r6,(parameter,))
    output=cursor.fetchall()
    if output!=[]:
        label='Statistical distribution of "'+str(parameter)+'"s rates :\n\n'
        label+="- Mean : "+str(output[0][0])+"\n- Standard Deviation : "+str(pow(output[0][1],1/2))
    else:
        label="Movie not found or no rate available"
    return(label)

#7 Film's global rank and year rank
r70="""
    SELECT M_Id, M_Year
    FROM Movies
    WHERE M_Name = ?
    """
r71="""
   SELECT Marks.M_Id
   FROM Movies
   INNER JOIN Marks
       ON Movies.M_Id = Marks.M_Id
   GROUP BY Marks.M_Id
   ORDER BY AVG(Mark) DESC
   """
r72="""
   SELECT Marks.M_Id
   FROM Movies
   INNER JOIN Marks
       ON Movies.M_Id = Marks.M_Id
   WHERE M_Year = ?
   GROUP BY Marks.M_Id
   ORDER BY AVG(Mark) DESC
   """
def dr7(parameter):
    cursor.execute(r70,(parameter,))
    output=cursor.fetchall()
    if output!=[]:
        MId=output[0][0]
        MYear=output[0][1]
        cursor.execute(r71)
        output=cursor.fetchall()
        globalrank=0
        n=len(output)
        while output[globalrank][0]!=MId and globalrank<(n-1):
            globalrank+=1
        if globalrank==(n-1) and MId!=output[globalrank][0]:
            label="No rate for this movie"
            return(label)
        else:
            globalrank+=1
        cursor.execute(r72,(MYear,))
        output=cursor.fetchall()
        yearrank=0
        n=len(output)
        while output[yearrank][0]!=MId and yearrank<(n-1):
            yearrank+=1
        yearrank+=1
        label='"'+str(parameter)+'"'+"'s rank :\n\n"
        label+="- Global : "+str(globalrank)+"\n- Year ("+str(MYear)+") : "+str(yearrank)
        return(label)
    else:
        label="Movie not found"
        return(label)
    
#8 Movie's best mark
r8="""
   SELECT MAX(Mark)
   FROM Marks
   INNER JOIN Movies
       ON Marks.M_Id = Movies.M_Id
   WHERE M_Name = ?
   """   
def dr8(parameter):
    cursor.execute(r8,(parameter,))
    output=cursor.fetchall() 
    if output!=[]:
        label='"'+str(parameter)+'" best user mark : '+str(output[0][0])
    else:
        label="Movie not found or no rate available"
    return(label)
    
#9 Movie's worst mark  
r9="""
   SELECT MIN(Mark)
   FROM Marks
   INNER JOIN Movies
       ON Marks.M_Id = Movies.M_Id
   WHERE M_Name = ?
   """   
def dr9(parameter):
    cursor.execute(r9,(parameter,))
    output=cursor.fetchall() 
    if output!=[]:
        label='"'+str(parameter)+'" worse user mark : '+str(output[0][0])
    else:
        label="Movie not found or no rate available"
    return(label)    
    
#10 Movie's realisator mean rate
r10="""
    SELECT AVG(Mark)
    FROM Marks
    INNER JOIN Makings
        ON Marks.M_Id = Makings.M_Id
    WHERE D_Id = (SELECT Directors.D_Id
                  FROM Directors
                  INNER JOIN Makings
                      ON Directors.D_Id = Makings.D_Id
                  INNER JOIN Movies
                      ON Makings.M_Id = Movies.M_Id
                  WHERE M_Name = ?)
    """    
def dr10(parameter):
    cursor.execute(r10,(parameter,))
    output=cursor.fetchall()
    if output!=[]:
        label='"'+str(parameter)+'"'+"'s realisator mean rate : "+str(output[0][0])
    else:
        label="Movie not found or no rate available"
    return(label)

## Global function (show the result in a pop up window)
def click(r, parameter1, parameter2):
    window=tk.Tk()
    window.title("Research Result")
    frame=tk.Frame(window, borderwidth=2)
    frame.pack(padx=30, pady=5)
    if r==1:
        text=dr1(parameter1)
    elif r==2:
        text=dr2(parameter1)
    elif r==3:
        text=dr3(parameter1)
    elif r==4:
        text=dr4(parameter1)
    elif r==5:
        text=dr5(parameter2)
    elif r==6:
        text=dr6(parameter2)
    elif r==7:
        text=dr7(parameter2)
    elif r==8:
        text=dr8(parameter2)
    elif r==9:
        text=dr9(parameter2)
    else:
        text=dr10(parameter2)
    label=tk.Label(frame,text=text)
    label.pack()
    window.mainloop()
    

### CREATION OF GRAPHIC INTERFACE ###

## Environnement
print("\nCreation of graphic envrionnement\n")

def openmanager():
    window=tk.Tk()
    window.title("Film Manager")

    Frame1 = tk.Frame(window, borderwidth=2)
    Frame1.pack(padx=30, pady=5)
    yearlabel = tk.Label(Frame1,text="Enter year :")
    yearlabel.pack()
    yearvalue = tk.StringVar()
    yearvalue.set("")
    yearentry = tk.Entry(Frame1, textvariable=yearvalue, width=30)
    yearentry.pack()
    movielabel = tk.Label(Frame1,text="Enter movie name :")
    movielabel.pack()
    movievalue = tk.StringVar()
    movievalue.set("")
    movieentry = tk.Entry(Frame1, textvariable=movievalue, width=30)
    movieentry.pack()
    
    Frame2 = tk.Frame(window, borderwidth=2)
    Frame2.pack(padx=30, pady=10)
    actionlabel = tk.Label(Frame2, text="Select an action :")
    actionlabel.pack()
    mode = tk.StringVar() 
    mode.set(1)
    button1 = tk.Radiobutton(window, text="Year's TOP 5 movies", variable=mode, value=1)
    button1.pack()
    button2 = tk.Radiobutton(window, text="Year's movie with the highest budget", variable=mode, value=2)
    button2.pack()
    button3 = tk.Radiobutton(window, text="Year's best movies by genre", variable=mode, value=3)
    button3.pack()
    button4 = tk.Radiobutton(window, text="Year's user who gave the highest number of rates", variable=mode, value=4)
    button4.pack()
    button5 = tk.Radiobutton(window, text="Movie's description", variable=mode, value=5)
    button5.pack()
    button6 = tk.Radiobutton(window, text="Movie's mean rate and standard error", variable=mode, value=6)
    button6.pack()
    button7 = tk.Radiobutton(window, text="Movie's rank (total and on the year)", variable=mode, value=7)
    button7.pack()
    button8 = tk.Radiobutton(window, text="Movie's best user mark", variable=mode, value=8)
    button8.pack()
    button9 = tk.Radiobutton(window, text="Movie's worst user mark", variable=mode, value=9)
    button9.pack()
    button10 = tk.Radiobutton(window, text="Movie's director's rates mean", variable=mode, value=10)
    button10.pack()
    
    Frame3 = tk.Frame(window, borderwidth=2)
    Frame3.pack(padx=10, pady=10)
    actionbutton=tk.Button(Frame3, text="Search", command=lambda cursor=cursor:click(int(mode.get()),int(yearvalue.get()),str(movievalue.get())))
    actionbutton.pack()
    
    window.mainloop()


### RECOMMENDATIONS ###
print("\nComputing recommendations :")

## Find the list of the 20 most rated movies by genre
print("- Identifying 20 most rated movies by genre")
movieidlist=[]
movienamelist=[]
for gid in range(28):
    cursor.execute("""
                   SELECT Marks.M_Id, M_Name
                   FROM Movies
                   INNER JOIN Marks
                       ON Movies.M_Id = Marks.M_Id
                   INNER JOIN Relations
                       ON Movies.M_Id = Relations.M_Id
                   WHERE G_Id = ?
                   GROUP BY Marks.M_Id
                   ORDER BY COUNT(Marks.U_Id)
                   LIMIT 20
                   """,
                   (gid, ))
    output=cursor.fetchall()
    for m in output:
        if m[0] not in movieidlist:
            movieidlist.append(m[0])
            movienamelist.append(m[1])
nml=len(movieidlist)

## Find the n most popular genres
def topgenres(n):
    cursor.execute("""
                   SELECT Relations.G_Id, G_Name
                   FROM Genres
                   INNER JOIN Relations
                       ON Genres.G_Id = Relations.G_Id
                   GROUP BY Relations.G_Id
                   ORDER BY COUNT(Relations.M_Id) DESC
                   LIMIT ?
                   """,
                   (n, ))
    output=cursor.fetchall()
    gid=[0]*n
    name=[""]*n
    for i in range(n):
        gid[i]=output[i][0]
        name[i]=output[i][1]
    df=pd.DataFrame({"id":gid,"name":name})
    return(df)
TOPgenres=topgenres(10)
ntg=len(TOPgenres)

## Define a random user rates vector with probability p to like uniformly between 0 and 6
def randomv(p=(1/5)):
    vect=[-1]*nml
    for i in range(nml):
        if rdm.random()<p:
            vect[i]=np.floor(rdm.random()*7)
    return(vect)

## Creation of a dictionary with the user's list of rate corresponding to the previous list of films for each user
print("- Defining associated vector for all users")
## Initializing
drusers={}
## Number of ratings per user
dnusers={}
for i in users.userid:
    drusers[i]=[-1]*nml
    dnusers[i]=0
for r in range(nr):
    m=0
    uid=ratings.userid[r]
    mid=ratings.movieid[r]
    while mid!=movieidlist[m] and m<(nml-1):
        m+=1
    if mid==movieidlist[m]:
        drusers[uid][m]=ratings.rating[uid]
        dnusers[uid]+=1

print("- Defining Cos and Special similarities")

## Define cosinus similarity
def cosd(v1,v2):
    n=len(v1)
    scal=0
    nv1=0
    nv2=0
    for i in range(n):
        if v1[i]!=-1 and v2[i]!=-1:
            scal+=v1[i]*v2[i]
            nv1+=pow(v1[i],2)
            nv2+=pow(v2[i],2)
    if nv1==0 or nv2==0:
        sim=0
    else:
        sim=scal/(nv1*nv2)
    return(sim)

## Define a special similarity taking in account rates equal to 0 and opposite opposite tastes
## It also only movies that both users have rated and return 0 (independant) if both users have not rated at least a minimum number of common films
## It goes from -3 to 3 (rates go from 0 to 6)
def ratedist(rate1,rate2):
    if rate1==-1 or rate2==-1:
        return(0)
    else:
        d=abs(rate1-rate2)
        d=3-d
    return(d)
## nmovie is the minimum number of common movies that 2 users must have rated
def vectdist(v1,v2,nmovie=1):
    n=len(v1)
    scal=0
    div=0
    for i in range(n):
        scal+=ratedist(v1[i],v2[i])
        if v1[i]!=-1 and v2[i]!=-1:
            div+=1
    if div<nmovie:
        return(0)
    else:
        sim=scal/(div*3)
    return(sim) 

## Recommand films using k closest users, cos similarity if mode='cos', special one otherwise
print("- Defining NNS Recommendations function")
def NNSRecommendation(vector, k=15, mode='', nmovie=3):
## Find the k closest neighbours
    neighbours=[0]*k
    dneighbours=[-1]*k
    for uid,urates in drusers.items():
        if mode=='cos':
            sim=cosd(vector,urates)
        else:
            sim=vectdist(vector,urates,nmovie)
        if sim>dneighbours[(k-1)]:
            rank=(k-1)
            while sim>dneighbours[rank-1] and (rank-1)!=0:
                    rank+=-1
            if rank==1 and dneighbours[0]<sim:
                rank+=-1
            dneighbours=dneighbours[0:rank]+[sim]+dneighbours[(rank+1)::]
            neighbours=neighbours[0:rank]+[uid]+neighbours[(rank+1)::]
## Remove neighbours non positively correlated with the user
    i=0
    nl=[]
    dnl=[]
    for i in range(k):
        if dneighbours[i]>0:
            nl.append(neighbours[i])
            dnl.append(dneighbours[i])
    n=len(nl)
## Calibrate neighbours depending on their similarity with the user
    T=sum(dnl)
    for i in range(n):
        dnl[i]=dnl[i]/T
## Fill missing movie rates in the user global (on all movies) vector
    # Creating global vectors (copying the answers of the user in all movies rates vector)
    glob=[-1]*nm
    ## Doing a modificable copy of glob
    copy=[-1]*nm
    for i in range(nml):
        if vector[i]!=-1:
            glob[movieidlist[i]-1]=vector[i]
            copy[movieidlist[i]-1]=vector[i]
    # Looking at each rating
    for (uid,mid,r) in ratings[["userid","movieid","rating"]].values:
        # Checking the user id belongs to the neighbours
        nbrid=0
        while uid!=nl[nbrid] and nbrid<(n-1):
            nbrid+=1
        # If it is the case
        if uid==nl[nbrid]:
            # If user didn't rate this movie
            if glob[int(mid-1)]==-1:
    # Its rate take a calibrated value, we consider that a rate > 3 is good, < 3 is bad
                copy[int(mid-1)]=(r-3)*dnl[nbrid]
## Identify the 10 best movies by genre
    # Create a dictionary containing for each genre, a sub-dictionary which contains the list of movie names and the list of movie rates
    # Initializing
    dg={}
    for gid in TOPgenres.id:
        dg[gid]={'name':[],'rate':[]}
    # For each movie m
    for m in range(nm):
        # If we have a relevant rate about
        rate=copy[m]
        if rate!=-1:
            # If user didn't rate m
            if glob[m]==-1:
                # For every genre in the top genres
                for gid in TOPgenres.id:
                    # If the movie belongs to one of the top genres
                    if gid in movies.moviegenresid[m]:
                        dg[gid]['name']+=[movies.moviename[m]]
                        dg[gid]['rate']+=[rate]
    # Finding top 10 movies and creating list of tuples (pairs of genre name and movie names list) to return
    a=[("",[])]*ntg
    aindex=0
    for k,v in dg.items():
        # Convertion of dictionary value to dataframe
        dg[k]=pd.DataFrame(v)
        # Finding top 10 movies of the genre
        localtop=[""]*10
        rlocaltop=[0]*10
        for (mn,mr) in dg[k][['name','rate']].values:
            rank=9
            if mr>rlocaltop[rank]:
                while mr>rlocaltop[(rank-1)] and rank>0:
                    rank+=-1
                localtop=localtop[0:rank]+[mn]+localtop[(rank+1)::]
                rlocaltop=rlocaltop[0:rank]+[mr]+rlocaltop[(rank+1)::]
        a[aindex]=(TOPgenres.name[TOPgenres[TOPgenres.id==k].name.index.get_values()[0]],localtop) 
        aindex+=1
    return(a)
                
        
    








        