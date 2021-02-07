import mysql.connector
import spacy
import time

start_time = time.time()
"""
*******************************************************************************************************
Cette fonction va calculer le poids du lien qui lie deux fichiers en fonction de la proximité des mots 
entre les deux textes.
*******************************************************************************************************
"""
def poids(handle1, handle2):
    nlp_fr = spacy.load('fr_core_news_sm')
    # On se connecte à la base de donnée de jeuxDeMots.
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        # Insérez votre mot de passe dans password.
        password="",
        database="jdm_cleaned"
    )

    cur = db.cursor()

    # On récupère le texte du fichier 1 en le nettoyant de certains caractères génants.
    with open(handle1, "r", encoding="utf-8") as f:
        res=f.readlines()
        for i in range(0, len(res)):
            res[i] = res[i].strip('\n')
            res[i] = res[i].strip('\t')
            res[i] = res[i].strip(' ')
            res[i] = res[i].strip('/')
            res[i] = res[i].replace("'", "")
            res[i] = res[i].replace('"', "")
            res[i] = res[i].replace("=", "")

        result = list(filter(None, res))
        texte=' '.join(result)
        tabT1=[]
        doc = nlp_fr(texte)

        # On enlève les mots grammaticaux qui nous serons d'aucune utilité pour l'analyse.
        for tok in doc:
            if tok.pos_ != "DET" and tok.pos_ != "PRON":
                # On a donc une liste tabT1 des tokens du texte sans les mots grammaticaux.
                tabT1.append(tok.text)


        #print(tabT1)

    # On fait pareil pour le deuxième texte
    with open(handle2, "r", encoding="utf-8") as f:
        res = f.readlines()
        for i in range(0, len(res)):
            res[i] = res[i].strip('\n')
            res[i] = res[i].strip('\t')
            res[i] = res[i].strip(' ')
            res[i] = res[i].strip('/')
            res[i] = res[i].replace("'", "")
            res[i] = res[i].replace('"', "")
            res[i] = res[i].replace("=", "")

        result = list(filter(None, res))
        texte = ' '.join(result)
        tabT2 = []
        doc = nlp_fr(texte)
        for tok in doc:
            tabT2.append(tok.text)


    # On initialise la variable de poids.
    p = 0

    # Pour chaque mot du texte, on va sortir grâce à la requete sql,
    # un tableau x qui regroupe les mots les plus proches ainsi que leur poids.
    for i in tabT1:
        sql = "SELECT N2.name, R.weight, R.rtid FROM node N1 INNER JOIN relation R ON N1.eid = R.eid1 INNER JOIN node N2 ON R.eid2 = N2.eid WHERE N1.name = '"+i+"' ORDER BY R.weight DESC"
        cur.execute(sql)
        x = cur.fetchall()
        #print(x)

        # On parcourt chaque mot du texte 2 pour voir si il est dans le texte 1 ou dans le tableau x,
        # si oui alors on incrémente le poids.
        for line in tabT2:
            for j in range(len(x)):
                if line in x[j]:
                    p+=x[j][1]
                if i == line:
                    p+=400


    # On fait la même chose mais à l'inverse cette fois,
    # du texte 2 au texte 1 (sauf pour les mots identiques car ils seront juste compté deux fois ce qui est inutile.
    for i in tabT2:
        sql = "SELECT N2.name, R.weight, R.rtid FROM node N1 INNER JOIN relation R ON N1.eid = R.eid1 INNER JOIN node N2 ON R.eid2 = N2.eid WHERE N1.name = '"+i+"' ORDER BY R.weight DESC"
        cur.execute(sql)
        x = cur.fetchall()

        for line in tabT1:
            for j in range(len(x)):
                if line in x[j]:
                    p+=x[j][1]

    return p


tabPair = []
# On applique la fonction à chaque pair de fichier et on
# stock les résultats dans un fichier csv à la forme (fichier1, fichier2, poids)
with open("recapitulatifPoids.csv", "w") as f:
    # changer les ranges en fonction du nombre de fichier
    for i in range(0, 20):
        for j in range(0, 20):
            # Condition pour ne pas calculer les doublons et donc gagner du temps de traitement
            if i != j and (str(i)+str(j) not in tabPair or str(j)+str(i) not in tabPair):
                p = poids("Stendhal"+str(i)+".txt", "Stendhal"+str(j)+".txt")
                f.write("Stendhal"+str(i)+",Stendhal"+str(j)+","+str(p)+"\n")
                print(i, j)

            tabPair.append(str(i) + str(j))
            tabPair.append(str(j) + str(i))

print("--- %s seconds ---" % (time.time() - start_time))