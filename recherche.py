"""
    Ce script a pour but de calculer le poids de la similitude entre le mot-clé choisi par l'utilisateur et les textes.
"""

import mysql.connector

# On demande un mot-clé à l'utilisateur.
mot = input("Entrez un mot-clé : ")


# Dans cette portion, on va se connecter à la bdd simili_stendhal pour stocker la table tokens dans "t"
# et la colonne permalien dans "permalien".
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

sql = "SELECT permalien FROM simili_stendhal.textes;"
cur.execute(sql)
permalien = cur.fetchall()
# Ici, on parcourt permalien pour retirer les virgules inutiles.
for i in range(0, len(permalien)):
    permalien[i] = str(permalien[i]).replace(",", "")



# Dans cette portion, on récupère uniquement les nombres de la colonne "textesList" de la table "tokens" pour
# les stocker dans un tableau "textesList" sous la forme :
# textesList = [['id du texte où le token apparait', 'nombre de fois qu'il apparait',
# 'id du texte où le token apparait', 'nombre de fois qu'il apparait'...], ['...', '...', '...', '...'...]].
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
    # On supprime tableau[0] qui est vide.
    del tableau[0]
    textesList.append(tableau)

cur.close()
db.close()




# Dans cette portion, on se connecte à la bdd jdm_cleaned pour stocker les mots proche du mot-clé ainsi que
# leur poids dans un tableau "x".
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



# Dans cette portion, on va créer un dictionnaire "dic" avec pour clé l'id du texte suivi de son permalien et
# pour valeur le poids entre le mot clé et le texte.
dic = {}
for i in range(0, len(t)):
    # Ici, on gère le cas où l'on trouve le mot-clé tel quel dans le texte,
    # si cela arrive on ajoute +1 000 au poids final (multiplié par le nombre de fois ou il apparait).
    if t[i][1] == mot:
        j = 0
        while j != len(textesList[i]):
            dic["texte "+textesList[i][j]+" "+str(permalien[int(textesList[i][j])-1])] = int(textesList[i][j+1])*1000
            j+=2

    # Ici, on va gérer le cas où on trouve un mot dans le texte proche du mot-clé,
    # dans ce cas-là on ajoute le poids du mot au poids final (généralement entre 1 et 500).
    for k in range(0, len(x)):
        if t[i][1] == x[k][0]:
            m = 0
            while m != len(textesList[i]):
                if "texte "+textesList[i][m]+" "+str(permalien[int(textesList[i][m])-1]) in dic.keys():
                    dic["texte " + textesList[i][m]+" "+str(permalien[int(textesList[i][m])-1])] += int(textesList[i][m + 1]) * x[k][1]
                else:
                    dic["texte " + textesList[i][m]+" "+str(permalien[int(textesList[i][m])-1])] = int(textesList[i][m + 1]) * x[k][1]
                m+=2




# Ici, on va renvoyer les textes qui ont un poids final supérieur à
# 100 (possibilité de changer selon le degré de proximité que l'on souhaite) dans l'ordre décroissant.
dic = sorted(dic.items(), key=lambda z: z[1], reverse=True)
for i in dic:
    if i[1] >= 100:
        print(i[0], ":", i[1])

