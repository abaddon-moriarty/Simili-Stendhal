# chose à faire : gérer les tok présent plusieurs fois, ajouter hyperlien

import mysql.connector
import spacy
import time

start_time = time.time()

"""
    Cette fonction va calculer le poids du lien qui lie deux fichiers en fonction de la proximité des mots 
    entre les deux textes.
    Elle va donc retourner le poids "p" de type int.
"""
def poids(texte1, texte2):
    # Dans cette portion, on va se connecter à la bdd simili_stendhal pour stocker la table tokens dans "t".
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



    # Dans cette portion, on va se connecter à la bdd jdm_cleaned pour stocker les tokens du premier texte
    # dans tabT1 et les tokens du deuxième texte dans tabT2.
    db = mysql.connector.connect(
            host="localhost",
            user="root",
            # Insérez votre mot de passe dans password.
            password="",
            database="jdm_cleaned"
        )

    cur = db.cursor()
    tabT1 = []
    tabT2 = []
    for i in range(0, len(t)):
        j = 0
        while j != len(textesList[i]):
            if textesList[i][j] == str(texte1):
                for k in range(0, int(textesList[i][j+1])):
                    tabT1.append(t[i][1])
            elif textesList[i][j] == str(texte2):
                for k in range(0, int(textesList[i][j+1])):
                    tabT2.append(t[i][1])

            j+=2


    # On initialise la variable de poids.
    p = 0

    # Pour chaque mot du texte, on va sortir grâce à la requete sql,
    # un tableau x qui regroupe les mots les plus proches ainsi que leur poids.
    for i in tabT1:
        sql = 'SELECT N2.name, R.weight, R.rtid FROM node N1 INNER JOIN relation R ON N1.eid = R.eid1 INNER JOIN node N2 ON R.eid2 = N2.eid WHERE N1.name = "'+i+'" ORDER BY R.weight DESC'
        cur.execute(sql)
        x = cur.fetchall()

        # On parcourt chaque mot du texte 2 pour voir si il est dans le texte 1 ou dans le tableau x,
        # si oui alors on incrémente le poids (+1 000 pour un mot identique et +le poids du mot pour un mot proche).
        for line in tabT2:
            for j in range(len(x)):
                # cas mot proche.
                if line in x[j]:
                    p+=x[j][1]
                # Cas mot identique.
                if i == line:
                    p+=1000


    # On fait la même chose mais à l'inverse cette fois,
    # du texte 2 au texte 1 (sauf pour les mots identiques car ils seront juste compté deux fois ce qui est inutile).
    for i in tabT2:
        sql = 'SELECT N2.name, R.weight, R.rtid FROM node N1 INNER JOIN relation R ON N1.eid = R.eid1 INNER JOIN node N2 ON R.eid2 = N2.eid WHERE N1.name = "'+i+'" ORDER BY R.weight DESC'
        cur.execute(sql)
        x = cur.fetchall()

        for line in tabT1:
            for j in range(len(x)):
                if line in x[j]:
                    p+=x[j][1]
    cur.close()
    db.close()

    return p

# On se connecte à la bdd simili_stendhal pour récupérer les permaliens.
db = mysql.connector.connect(
            host="localhost",
            user="root",
            # Insérez votre mot de passe dans password.
            password="",
            database="simili_stendhal"
        )
cur = db.cursor()
sql = "SELECT permalien FROM simili_stendhal.textes;"
cur.execute(sql)
permalien = cur.fetchall()
# Ici, on parcourt permalien pour retirer les virgules inutiles.
for h in range(0, len(permalien)):
    permalien[h] = str(permalien[h]).replace(",", "")


tabPair = []
# On applique la fonction à chaque pair de fichier et on
# stock les résultats dans un fichier csv à la forme (texte 1, permalien 1, texte 2, permalien 2, poids)
with open("recapitulatifPoids.csv", "w") as f:
    # Changer les ranges en fonction du nombre de fichier
    for i in range(1, 20):
        for j in range(1, 20):
            # Condition pour ne pas calculer les doublons et donc gagner du temps de traitement
            if i != j and (str(i)+str(j) not in tabPair or str(j)+str(i) not in tabPair):
                p = poids(str(i), str(j))
                f.write("Texte "+str(i)+","+permalien[i-1]+",Texte "+str(j)+","+permalien[j-1]+","+str(p)+"\n")
                print(i, permalien[i-1], j, permalien[j-1], p)

            tabPair.append(str(i) + str(j))
            tabPair.append(str(j) + str(i))

print("--- %s seconds ---" % (time.time() - start_time))
