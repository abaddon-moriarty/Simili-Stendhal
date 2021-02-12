"""
    ... a pour but de calculer le poids de la similitude entre le mot-clé choisi par l'utilisateur et les textes.
"""

import mysql.connector

mot = input("Entrez un mot-clé : ")

db = mysql.connector.connect(
            host="localhost",
            user="root",
            # Insérez votre mot de passe dans password.
            password="",
            database="simili_stendhal"
        )

cur = db.cursor()
sql = "SELECT * FROM simili_stendhal.tokens;"
cur.execute(sql)
t = cur.fetchall()

textesList = []

for j in range(0, len(t)):
    nb = ""
    tableau = []
    transi = str(t[j][2]) + "  ("

    for i in range(0, len(transi)):
        if transi[i] == "0" or transi[i] == "1" or transi[i] == "2" or transi[i] == "3" or transi[i] == "4" or transi[i] == "5" or transi[i] == "6" or transi[i] == "7" or transi[i] == "8" or transi[i] == "9":
            nb = nb + transi[i]
        try:
            if transi[i]+transi[i+1]+transi[i+2] == "', " or transi[i] == "(":
                tableau.append(nb)
                nb = ""
        except IndexError:
            if transi[i] == " ":
                tableau.append(nb)
                nb = ""

    del tableau[0]
    textesList.append(tableau)

cur.close()
db.close()

db = mysql.connector.connect(
            host="localhost",
            user="root",
            # Insérez votre mot de passe dans password.
            password="",
            database="jdm_cleaned"
        )

cur = db.cursor()

sql = 'SELECT N2.name, R.weight, R.rtid FROM node N1 INNER JOIN relation R ON N1.eid = R.eid1 INNER JOIN node N2 ON R.eid2 = N2.eid WHERE N1.name = "'+mot+'" ORDER BY R.weight DESC'
cur.execute(sql)
x = cur.fetchall()

dic = {}
for i in range(0, len(t)):
    if t[i][1] == mot:
        j = 0
        while j != len(textesList[i]):
            dic["texte "+textesList[i][j]] = int(textesList[i][j+1])*1000
            #print(textesList[i][j],":", textesList[i][j+1])
            j+=2

    for k in range(0, len(x)):
        if t[i][1] == x[k][0]:
            m = 0
            while m != len(textesList[i]):
                if "texte "+textesList[i][m] in dic.keys():
                    dic["texte " + textesList[i][m]] += int(textesList[i][m + 1]) * x[k][1]
                else:
                    dic["texte " + textesList[i][m]] = int(textesList[i][m + 1]) * x[k][1]
                m+=2




dic = sorted(dic.items(), key=lambda z: z[1], reverse=True)
for i in dic:
    print(i[0], ":", i[1])
