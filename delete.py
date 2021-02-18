import mysql.connector
import spacy

"""
    ***Attention*** Le script met très longtemps à s'executer, il est préférable de ne pas l'executer et de prendre 
    directement la base de données nettoyé ***Attention***
    
    Ce script a pour but de supprimer les mots grammaticaux et les mots avec un ">" de la base de données jdm_cleaned.
"""


nlp_fr = spacy.load('fr_core_news_sm')

db = mysql.connector.connect(
    host="localhost",
    user="root",
    # Insérez votre mot de passe dans password.
    password="",
    database="jdm_cleaned"
)

cur = db.cursor()

# On créé une liste tabName avec toute la colonne name de la base de données.
sql = "SELECT name FROM node;"
cur.execute(sql)
res = cur.fetchall()
tabName = []

# On supprime quelques caractères inutiles.
for line in res:
    for char in "(),'":
        line = str(line).replace(char, '')
    if line not in tabName:
        tabName.append(line)

# On va trouver tout les mots grammaticaux de la liste grâce à spacy et les supprimer de la base de données.
docs = nlp_fr.pipe(tabName)
for doc in docs:
    for tok in doc:
        if tok.pos_ == "DET" or tok.pos_ == "PRON" or tok.pos_ == "CCONJ":
            sql = "DELETE FROM node WHERE name = '"+str(tok)+"';"
            print(tok)
            cur.execute(sql)
            db.commit()

# On va supprimer les lignes avec des chevronnes ouverts qui sont inutiles pour notre traitement.
sql = "DELETE FROM node WHERE name LIKE '%>%';"
cur.execute(sql)
db.commit()

cur.close()
db.close()
