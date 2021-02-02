# coding: utf8

import mysql.connector
import bs4 as bs
import csv
import urllib.request
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import re


## connection à la base de donnée pour uploader les données
conn = mysql.connector.connect(
	host = "localhost",
	user = "root",
	password = "",
	database = "simili_stendhal")

mycursor = conn.cursor()

#Fonction qui ajoute un backslash avant chaque apostrophe ou guillemet pour aider à l'upload
def backslashs(texte):

	'''compte le nombre d'occurence d'appostrophes et de guillemet, pour ajouter à la longeur de la boucle
	autrement la boucle s'arrête avant la fin réelle du texte auquel on aura ajouté des \''''
	a = texte.count("'")
	b = texte.count('"')
	longeur = len(texte) + a + b
	for i in range(0, longeur):
		if texte[i] == "'" or texte[i] == '"':
			j = i-1
			if texte[j] != "\\":
				texte = texte[:i] + "\\" + texte[i:]
	return texte



def identification(fileName):
	sauce = open(fileName, encoding='utf-8')
	soup = bs.BeautifulSoup(sauce, 'lxml', from_encoding="utf-8")

	################### RECUPERER IDENTIFICATION #################
	statement = {'nomxml': '',
	'cote': '', 
	'nb_ordre': '', 
	'page': '', 
	'volume': '', 
	'type': '', 
	'titre': '',
	'permalien': '', 
	'texte': ''}

	for line in soup.find_all('biblscope'):
		if line.get('unit') == 'cote':
			statement['cote'] = line.text
		elif line.get('unit') == 'numero_ordre_dans_registre':
			statement['nb_ordre'] = line.text
		elif line.get('unit') == 'numero_page':
			statement['page'] = line.text
		elif line.get('unit') == 'volume':
			statement['volume'] = line.text
	statement['type'] = soup.msdesc.get('type')

	lien = soup.ref
	permalien = lien.get('target')

	#vérification au cas où il y ait plusieurs lie ns
	handle = "http://manuscrits-de-stendhal.org/permalien.php"
	if handle in permalien:
		statement['permalien'] = permalien

	# text = soup.surface
	for paragraph in soup.find_all('surface'):
		statement['texte'] += paragraph.text
		#on retrouve les \n quand on print(statement)
		#mais ils disparaissent quand on vise statement['text']
		#donc tout va bien

		#permet d'enlever toutes les tabulations retours à la ligne et espace inutiles.
		statement['texte'] = statement['texte'].replace('\n', '')
		statement['texte'] = statement['texte'].replace('\t', '')
		while "  " in statement['texte']:
			statement['texte'] = statement['texte'].replace("  ", " ")
		statement['texte'] = backslashs(statement['texte'])

	for line in soup.find_all('textdesc'):
		if line.get('n') == 'corpus':
			statement['titre'] += line.text
			statement['titre'] += " "

	for line in soup.find_all('textdesc'):
		if line.get('n') == 'document':
			statement['titre'] += line.text
	statement['titre'] = backslashs(statement['titre'])
	return statement




#parcours chaque fichier xml de la dir et applique la fonction identification()
def parcoursXml(handle):
	fileList = []
	# r=>root, d=>directories, f=>files
	# récupère tous les fichier d'une dir et ls met dans une liste fileList
	for r, d, f, in os.walk(handle):
		for item in f:
			if '.xml' in item:
				fileList.append(os.path.join(r, item))

	# boucle qui parcours la liste des fichier, leur applique la fonction identification à fileList et upload les informations à la base de donnée
	for name in fileList:
		temp = identification(name)
		xml = name[name.rindex('Stendhal'): name.index('.xml')+4]
		temp['nomxml'] = xml
		uploadBdd(temp)
	return

# fonction qui upload les informatios récupérées par identification() à la base de donnée
def uploadBdd(statement):
	columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in statement.keys())
	values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in statement.values())
	sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % ('simili_stendhal.textes', columns, values)
	mycursor.execute(sql)
	conn.commit()
	for row in mycursor.fetchall():
		print(row)

	retour = mycursor.rowcount, "record inserted"
	return retour



# fonction qui vérifie que l'etrée ne fasse pas déjà partie de la base de donnée
# def verifDoublons(statement):
# 	sql = "SELECT * FROM `textes` WHERE `cote` = %s AND `nb_ordre` = %s AND `volume` = %s AND `type` = %s AND `page` = %s AND `titre` = %s AND `texte` = %s;" % (statement['cote'], statement['nb_ordre'], statement['page'], statement['volume'], statement['type'], statement['titre'], statement['texte'])
# 	mycursor.execute(sql)
# 	titleList = mycursor.fetchall() #fetchall will select the last excecuted query
# 	if mycursor.rowcount == 0: #vérifie qu'il n'y a pas d'entrée avec les mêmes infos
# 		uploadBdd(statement) #appelle la fonction upload, pour mettre à jour la bdd
# 	else:
# 		print('il y a déjà', mycursor.rowcount, 'entrée(s) avec les mêmes informations')
# 	return





#récupère tous les document ".xml" dans le dossier
############ changer le handle pour adapter à l'ordinateur ###########
handle = "C:\\Users\\munau\\OneDrive\\Documents\\SimiliStendhal\\try"#\\Stendhal2211.xml"
parcoursXml(handle)
# prob = identification(handle)
# print(prob)

# <>

# word = []
# filterList = []
# stop_words = set(stopwords.words("french"))
# # temp = update(test)

# surface = test['text']
# tokenText = word_tokenize(surface)
# word.append(tokenText)
# print(surface)
# print(word)
# for w in word:
# 	if w not in stop_words:
# 		filterList.append(w)
# print(filterList)



conn.close()