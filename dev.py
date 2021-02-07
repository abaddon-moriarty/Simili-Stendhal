# coding: utf8
import nltk
import mysql.connector
import bs4 as bs
import csv
import urllib.request
import os
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import re
import string


"""
*****************************************************************************************************************************
* fonction qui permet de se connecter à la base de donnée                                  								    *
* elle prend en entrée, le nom d'utilisateur(str), le mot de passe(str) et le nom de la base de donnée(str)                 *
* elle retourne le nom de les variables conn et mycursor pour pouvoir faire des requêtes à la base de donnée                *
* le champ mot de passe peut être vide (notamment en localhost où il n'est pas nécéssaire)                                  *
* le nom de la base de donnée peut lui aussi être vide, nous utilisons d'ailleurs cet aspect, pour créer la base de donnée. *
*****************************************************************************************************************************
"""

def connection(username, password, database):
	conn = mysql.connector.connect(
	host = "localhost",
	user = username,
	password = password,
	database = database
	)
	mycursor = conn.cursor()

	return conn, mycursor

#changer ici les données de connection
#username, password, databasename
conn, mycursor = connection("root", "", "")



"""
************************************************************************************
* fonction qui créé la base de donnée et la table si elles n'existent pas déjà.    *
* elle prend en entrée les variables conn, mycursor, et tableName (str)            *
* elle retourne True(bool) or False(bool) ce qui active(?) ou non le reste du code *
************************************************************************************
"""

def create(conn, mycursor, tableName, listecol, sqlQuery): 
	mycursor.execute("CREATE DATABASE IF NOT EXISTS simili_stendhal")
	# met à jour la connection en ajoutant le nom de la database
	conn, mycursor = connection("root", "", "simili_stendhal")

	#vérifie la liste des tables
	mycursor.execute("SHOW TABLES")
	exx = mycursor.fetchall()
	# print(exx)
	if tableName == 'textes':
		if ('textes',) in exx:
			# Si la table textes existe déjà il récupère le nom des colonnes
			mycursor.execute("SELECT * from textes")
			exx = mycursor.fetchall()
			num_fields = len(mycursor.description)
			field_names = [i[0] for i in mycursor.description]

			# on la compare à la liste des colonnes que l'on utilise pour éviter toute erreur
			if listecol == field_names:
				# print('all is right in the coding world again')
				return True
			else: 
				print('Vous avez déjà une table du nom de', tableName, 'avec des colonnes différentes, vérifiez ces informations et changez le nom de la table')
				# print('AAAAAH COME ON /§§§§§§§§§§§§§§§§v DYTYUYFRSJYUFRTSSRTFGHYUI')
				return False

		# si la table n'existe pas alors on la créé
		else: 
			# print('table does not exists')
			mycursor.execute(sqlQuery)
			return True
	elif tableName == 'tokens':
		if ('tokens',) in exx:
			# Si la table textes existe déjà il récupère le nom des colonnes
			mycursor.execute("SELECT * from tokens")
			exx = mycursor.fetchall()
			num_fields = len(mycursor.description)
			field_names = [i[0] for i in mycursor.description]

			# on la compare à la liste des colonnes que l'on utilise pour éviter toute erreur
			if listecol == field_names:
				# print('all is right in the coding world again')
				return True
			else: 
				print('Vous avez déjà une table du nom de', tableName, 'avec des colonnes différentes, vérifiez ces informations et changez le nom de la table')
				# print('AAAAAH COME ON /§§§§§§§§§§§§§§§§v DYTYUYFRSJYUFRTSSRTFGHYUI')
				return False

		# si la table n'existe pas alors on la créé
		else: 
			# print('table does not exists')
			mycursor.execute(sqlQuery)
			return True



#Fonction qui ajoute un backslash avant chaque apostrophe ou guillemet pour aider à l'upload
#boolTitre est un boolean, s'il ce qui passe dans la fonction est un titre ou un le texte
def backslashs(texte, boolTitre):
	a = texte.count("'")
	b = texte.count('"')
	c = a + b
	sub = texte[-c:]


	#vérifie s'il y a un appostrophe ou un guillemet que si c'est le texte
	if "'" in sub or '"' in sub and not boolTitre:
		# print(sub, '\n', "il y a un truc")
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
		# print(texte)
	elif "'" not in sub or '"' not in sub:
		# print("il n'y a rien")
		for i in range(0, len(texte)):
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

	#compte le nombre de balises surfaces
	surfCount = len(soup.find_all('surface'))
	if surfCount > 0: #s'il en trouve alors ajoute les balises au texte
		for paragraph in soup.find_all('surface'):
			statement['texte'] += paragraph.text

		# 690 pages n'ont pas de balises surface, le texte est contenu dans les balises body
		#S'il n'y a pas de balises surface alors on cherche les balises body
	else : #sinon on compte les balises body contenant du texte
		for paragraph in soup.find_all('text'):
			statement['texte'] += paragraph.text


	#on retrouve les \n quand on print(statement)
	#mais ils disparaissent quand on vise statement['text']
	#donc tout va bien

	#permet d'enlever toutes les tabulations retours à la ligne et espace inutiles.
	statement['texte'] = statement['texte'].replace('\n', '')
	statement['texte'] = statement['texte'].replace('\t', '')
	statement['texte'] = statement['texte'].replace('#', '')
	statement['texte'] = statement['texte'].lower()

	# print(statement['texte'])
	while "  " in statement['texte']:
		statement['texte'] = statement['texte'].replace("  ", " ")

	statement['texte'] = backslashs(statement['texte'], False)
	# for item in statement['texte']:
		# print(item, '\n')

	for line in soup.find_all('textdesc'):
		if line.get('n') == 'corpus':
			statement['titre'] += line.text
			statement['titre'] += " "

	for line in soup.find_all('textdesc'):
		if line.get('n') == 'document':
			statement['titre'] += line.text
	statement['titre'] = backslashs(statement['titre'], True)
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
		# print(temp['texte'], '\n')
		xml = name[name.rindex('Stendhal'): name.index('.xml')+4]
		temp['nomxml'] = xml
		uploadBdd(temp, 'simili_stendhal.textes')
		# exportTxt(temp, name)
	return

# fonction qui upload les informatios récupérées par identification() à la base de donnée
def uploadBdd(statement, table):

	######################################################################################################
	######## essaie de vérifier avant d'isérer mais je n'arrive pas à faire rentrer une variable #########
	## lienxml = statement['nomxml'] 	                                                                ##
	## sql = """INSERT INTO tokens (%s) SELECT * FROM (SELECT %s) as temp WHERE NOT EXISTS 			    ##
	## (SELECT nomxml FROM tokens WHERE nomxml = " +  lienxml + ") LIMIT 1;""" % (columns, values)      ##
	######################################################################################################
	
	columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in statement.keys())
	values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in statement.values())
	sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % (table, columns, values)
	mycursor.execute(sql)
	conn.commit()
	for row in mycursor.fetchall():
		print(row)

	retour = mycursor.rowcount, "record inserted"
	return retour

def exportTxt(statement, handle):
		name = handle[handle.rindex('Stendhal'): handle.index('.xml')]
		name = 'C:\\Users\\munau\\OneDrive\\Documents\\SimiliStendhal\\try2\\'+ name +'.txt'
		outfile = open(name, 'w', encoding='utf-8')
		outfile.write(statement['texte'])
		outfile.close()

french_stopwords = set(stopwords.words('french'))

def stopwords(nltkList, handle):
	with open(handle, 'r', encoding='utf-8') as f:
		stopWords = f.readlines()
		for i in range(0, len(stopWords)):
			stopWords[i] = stopWords[i].strip('\n')
			for j in range(0,len(nltkList)):
				if stopWords[i] not in nltkList:
					nltkList.add(stopWords[i])
		f.close()

	return nltkList


# fonction qui vérifie que l'eNtrée ne fasse pas déjà partie de la base de donnée
# def verifDoublons(statement):
# 	sql = "SELECT * FROM `textes` WHERE `cote` = %s AND `nb_ordre` = %s AND `volume` = %s AND `type` = %s AND `page` = %s AND `titre` = %s AND `texte` = %s;" % (statement['cote'], statement['nb_ordre'], statement['page'], statement['volume'], statement['type'], statement['titre'], statement['texte'])
# 	mycursor.execute(sql)
# 	titleList = mycursor.fetchall() #fetchall will select the last excecuted query
# 	if mycursor.rowcount == 0: #vérifie qu'il n'y a pas d'entrée avec les mêmes infos
# 		uploadBdd(statement) #appelle la fonction upload, pour mettre à jour la bdd
# 	else:
# 		print('il y a déjà', mycursor.rowcount, 'entrée(s) avec les mêmes informations')
# 	return




textCol = ['id', 'nomxml', 'cote', 'nb_ordre', 'page', 'volume', 'type', 'titre', 'permalien', 'texte']
sql = """CREATE TABLE textes 
			(id int PRIMARY KEY NOT NULL AUTO_INCREMENT, 
			nomxml varchar(255),
			cote varchar(255),
			nb_ordre varchar(255),
			page varchar(255),
			volume varchar(255),
			type varchar(255),
			titre varchar(255),
			permalien varchar(255),
			texte text)"""
aOk = create(conn, mycursor, 'textes', textCol, sql)

#si la fonction create n'a pas eu d'erreur alors on commence le travail sur les textes
#Je n'ai pas réussis à n'upload que si la ligne n'existe pas je me donc l'appel en commentaire
if aOk is True :

	#récupère tous les document ".xml" dans le dossier
	############ changer le handle pour adapter à l'ordinateur ###########
	handle = "C:\\Users\\munau\\OneDrive\\Documents\\SimiliStendhal\\export"#\\Stendhal1014.xml"
	parcoursXml(handle)
	# prob = identification(handle)
	# print(prob)
	# print(prob):
	# # prob['texte'] = backslashs(prob['texte'])
	# print(prob['texte'])
else:
	print("nope")


tokCol = ['tokenId', 'token', 'textesList', 'useTotal']
sql = """CREATE TABLE `simili_stendhal`.`tokens` 
	(`tokenId` INT NOT NULL PRIMARY KEY AUTO_INCREMENT , 
	`token` VARCHAR(250) NOT NULL , 
	`textesList` TEXT NOT NULL,
	`useTotal` INT NOT NULL)"""
bOk = create(conn, mycursor, 'tokens', tokCol, sql)

#si la table token à bien été créée
if bOk is True:

	# on récupère chaque texte dans la base de donnée
	mycursor.execute("SELECT id, texte FROM simili_stendhal.textes") # WHERE id <= 2")
	txtList = mycursor.fetchall()
	conn, mycursor = connection("root", "", "simili_stendhal")

	vocab = {}

	for texte in txtList:
		surface = texte[1]
		surface = surface.lower()
		surface = backslashs(surface, True)
		# print(surface, '\n')

		#une fois le texte récupéré on le tokenise grâce à la librairie nltk
		words = word_tokenize(surface, language="french")
		# customStopWord est une liste de stopword à compléter au fur et à mesure des versions
		#puisque Stendhal écrit avec des abréviations ou une graphie différente 
		# ce n'est pas toujours reconnu par les analyseur, nous avons donc préféré une liste définie de termes.
		customStopWord = stopwords(french_stopwords, "C:\\Users\\munau\\OneDrive\\Documents\\GitHub\\Simili-Stendhal\\customStopWord.txt")
		# print(customStopWord)
		# print(words, '\n')

		#on enlève alors les stopwords et la ponctuation
		punkt = ["!", "?", ".", "-", '–', "_", ",", ";", ":", "’", "]", "[", ")", "(", "&", "%", "+", "«", "»", "=", ""]
		# filtre = [word for word in words if word not in customStopWord and word not in punkt]
		filtre = []

		# boucle qui vérifie, pour chaque mot, qu'il ne fasse pas partie des stopwords ou de la ponctuation
		for word in words:
			if word not in punkt and word not in customStopWord:
				# vérifie aussi qu'il n'y ai pas de ponctuation à l'intérieur du mot
				for i in range(0, len(word)):
					if word[i] in punkt:
						word = word[:i] + " " + word[i+1:]
				if word[-1:] == "\\":
					word = word.replace('\\', '')
				filtre.append(word)

		# print(filtre, '\n')

		###########################################
		#calcul la fréquence d'un mot dans la page#
		###########################################

		tk = FreqDist()
		# ne calcule que les mots filtrés (hors stop words)
		for word in filtre:
			tk[word] += 1
		
		# ressort un tuple contenant le mot et le nombre de fois où il apparait dans le texte
		for values in tk.items():
			# print(values)
			mot = values[0]
			mot = backslashs(mot, False)
			freq = values[1]
			freK = texte[0], 'nb:', freq
			freK = backslashs(str(freK), False)
			#si le mot ne fait pas encore partie du dictionnaire
			if mot not in vocab:
				vocab[mot] = {
				'tokenId': '', 
				'token': mot,
				'useTotal': freq,
				'textesList': freK,
				}
			else : #si le mot fait déjà partie du dictionnaire
				vocab[mot]['textesList'] = vocab[mot]['textesList'] + freK
				vocab[mot]['useTotal'] = vocab[mot]['useTotal'] + freq
				# print('in')
			# print(vocab[mot])

	


	# for item in vocab.items():
		vocab[mot]['textesList'] = str(vocab[mot]['textesList'])
		# vocab[mot]['textesList'] = backslashs(vocab[mot]['textesList'], False)
		# print(item['textesList'])

		# sql = "INSERT INTO `tokens`(`token`, `useTotal`) VALUES (%s,%s)" % (vocab[mot]['token'], vocab[mot]['useTotal'])
		# mycursor.execute(sql)
		# conn.commit()
		# for row in mycursor.fetchall():
		# 	print(row)
		# print(mycursor.rowcount, "record inserted")

	for item, info  in vocab.items():
		# print(info)
		uploadBdd(info, 'simili_stendhal.tokens')

else:
	print('problème avec la création de la table tokens')




# <>





conn.close()