import mysql.connector
import spacy
import time

start_time = time.time()

"""
    Cette fonction va calculer le poids du lien qui lie deux fichiers en fonction de la proximité des mots 
    entre les deux textes.
    Elle va donc retourner le poids "p" de type int et un tableau associatif avec en clé le mot proche et en valeur son poids.
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


    # On initialise la variable de poids et le dictionnaire qui contiendra les mots les plus proches.
    p = 0
    dic = {}
    # Pour chaque mot du texte, on va sortir grâce à la requete sql,
    # un tableau x qui regroupe les mots les plus proches ainsi que leur poids.
    for i in tabT1:
        sql = 'SELECT N2.name, R.weight, R.rtid FROM node N1 INNER JOIN relation R ON N1.eid = R.eid1 INNER JOIN node N2 ON R.eid2 = N2.eid WHERE N1.name = "'+i+'" ORDER BY R.weight DESC'
        cur.execute(sql)
        x = cur.fetchall()

        # On parcourt chaque mot du texte 2 pour voir si il est dans le texte 1 ou dans le tableau x,
        # si oui alors on incrémente le poids (+1 000 pour un mot identique et +le poids du mot pour un mot proche)
        # et on stock les mots et les poids dans un tableau associatif dic.
        for line in tabT2:
            for j in range(len(x)):
                # cas mot proche.
                if line in x[j]:
                    if line in dic.keys():
                        dic[line]+=x[j][1]
                    else:
                        dic[line] = x[j][1]
                    p+=x[j][1]
                # Cas mot identique.
                if i == line:
                    if line in dic.keys():
                        dic[line]+=1000
                    else:
                        dic[line] = 1000
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
                    if line in dic.keys():
                        dic[line]+=x[j][1]
                    else:
                        dic[line] = x[j][1]
                    p+=x[j][1]
    cur.close()
    db.close()

    return p, dic

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
    permalien[h] = str(permalien[h]).replace("_", "/")


tabPair = []
# On applique la fonction à chaque pair de fichier et on
# stock les résultats dans un fichier json qui nous servira pour la représentation graphique. On le met en forme
# avec les différents noeuds et les différents liens.
with open("recapitulatifPoids.json", "w") as f:
    f.write('{"nodes": [\n')
    for i in range(1, 21):
        if i != 20:
            f.write('\t{"id": "Texte '+str(i)+'", "permalien": "'+permalien[i-1]+'"},\n')
        else:
            f.write('\t{"id": "Texte ' + str(i) + '", "permalien": "' + permalien[i - 1] + '"}\n')
    f.write('],\n')
    f.write('"links": [\n')
    # Changer les ranges i et j en fonction du nombre de fichier.
    for i in range(1, 21):
        for j in range(1, 21):
            # Condition pour ne pas calculer les doublons et donc gagner du temps de traitement.
            if i != j and (str(i)+str(j) not in tabPair or str(j)+str(i) not in tabPair):
                p, dic = poids(str(i), str(j))
                # On tri les valeurs de dic par ordre décroisant et on garde les 3 premières.
                dic = sorted(dic.items(), key=lambda z: z[1], reverse=True)[:3]
                # On enlève l'apostrophe qui provoque une erreur pour le réseau graphique.
                dic = str(dic).replace("qu'", "qu ")

                if p != 0:
                    if i == 19 and j == 20:
                        phrase = '\t{"source": "Texte ' + str(i) + '", "target": "Texte ' + str(j) + '", "weight": ' + str(p) + ', "tokens": '+str(dic)+'}\n'
                        phrase = phrase.replace("[", '"')
                        phrase = phrase.replace("]", '"')
                        f.write(phrase)
                    else:
                        phrase = '\t{"source": "Texte ' + str(i) + '", "target": "Texte ' + str(j) + '", "weight": ' + str(p) + ', "tokens": '+str(dic)+'},\n'
                        phrase = phrase.replace("[", '"')
                        phrase = phrase.replace("]", '"')
                        f.write(phrase)
                print(i, permalien[i-1], j, permalien[j-1], p)
                print(dic)

            tabPair.append(str(i) + str(j))
            tabPair.append(str(j) + str(i))
    f.write(']}')
print("--- %s seconds ---" % (time.time() - start_time))