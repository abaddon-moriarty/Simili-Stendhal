import mysql.connector
import spacy

nlp_fr = spacy.load('fr_core_news_sm')

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="jdm_cleaned"
)

cur = db.cursor()

# On créé une liste tabName avec toute la colonne name de la bdd
sql = "SELECT name FROM node;"
cur.execute(sql)
# remplacer fetchmany(size) par fetchall() pour charger l'intégralité
res = cur.fetchmany(50000)
tabName = []

for line in res:
    for char in "(),'":
        line = str(line).replace(char, '')
    if line not in tabName:
        tabName.append(line)

# On va trouvé tout les mots grammaticaux de la liste et les supprimer de la bdd
docs = nlp_fr.pipe(tabName)
with open("resultatDel.txt", "w") as f:
    for doc in docs:
        for tok in doc:
            if tok.pos_ == "DET" or tok.pos_ == "PRON" or tok.pos_ == "CCONJ":
                sql = "DELETE FROM node WHERE name = '"+str(tok)+"';"
                print(tok)
                f.write(str(tok)+"\n")

                # A utiliser en cas d'exécution de la requete de manière définitive
                """cur.execute(sql)
                db.commit()"""

sql = "DELETE FROM node WHERE name LIKE '%>%';"
"""cur.execute(sql)
db.commit()"""
