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
import json

"""
*****************************************************************************************************************************
* Cette fonction permet de se connecter à la base de donnée                                  							    *
* elle prend en entrée, le nom d'utilisateur, le mot de passe et le nom de la base de donnée          				        *
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
***************************************************************************************************************
* fonction qui créé la base de donnée et la table "textes" et "token" si elles n'existent pas déjà.           *
* elle prend en entrée les variables conn, mycursor, tableName, la liste des colonnes pour vérifier           * 
* que la table corresponde si elle existe ainsi que la query sql pour créer la table                          *
* elle retourne un booleen True s'il n'y a pas eu de problèmes, cela permet de continuer sur le reste du code *
***************************************************************************************************************
Le code est répété 2 fois car nous n'avons pas réussi à utiliser les placeholder sur les query mycursor.
Ce n'est pas le plus optimal mais cela fonctionne.
"""

def create(conn, mycursor, tableName, listecol, sqlQuery): 
	mycursor.execute("CREATE DATABASE IF NOT EXISTS simili_stendhal")
	# met à jour la connection en ajoutant le nom de la database
	conn, mycursor = connection("root", "", "simili_stendhal")

	#vérifie la liste des tables
	mycursor.execute("SHOW TABLES")
	tables = mycursor.fetchall()
	

	if tableName == 'textes':
		if ('textes',) in tables:
			# Si la table textes existe déjà il récupère le nom des colonnes
			mycursor.execute("SELECT * from textes")
			cols = mycursor.fetchall()
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
		else: 
			# si elle n'existe pas on exécute alors la query pour créer la table
			mycursor.execute(sqlQuery)
			return True

	elif tableName == 'tokens':
		if ('tokens',) in tables:
			# Si la table textes existe déjà il récupère le nom des colonnes
			mycursor.execute("SELECT * from tokens")
			cols = mycursor.fetchall()
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
		else: 
			# si elle n'existe pas on exécute alors la query pour créer la table
			mycursor.execute(sqlQuery)
			return True


"""
***********************************************************************************************
* Cette fonction ajoute des avant chaque apostrophe ou guillemet d'un texte donné.            *
* Nous en avons besoin pour mettre à jour les textes sur la base de donnée                    *
* Elle prend en entrée, le texte(chaine) et un boolTitre(bolléen)                             *
* Elle retourne le texte(chaine) modifié.                                                     *
***********************************************************************************************
"""
def backslashs(texte, boolTitre):
	# compte le nombre de guillemets et apostrophes, pour l'ajouter à la longeur du texte
	# sans quoi la boucle se fini prématurément.
	a = texte.count("'")
	b = texte.count('"')
	c = a + b
	sub = texte[-c:]


	
	# on regarde s'il y a un appostrophe dans la longeur ajoutée par le nombre de guillemets et d'apostrophes
	# si cette distinction n'est pas faite, tous les textes ne peuvent pas être mis à jour
	# boolTitre permet d'exclure les titres de la première boucle
	if "'" in sub or '"' in sub and not boolTitre:
		a = texte.count("'")
		b = texte.count('"')
		longeur = len(texte) + a + b
		for i in range(0, longeur):
			if texte[i] == "'" or texte[i] == '"':
				j = i-1
				if texte[j] != "\\":
					texte = texte[:i] + "\\" + texte[i:]
	elif "'" not in sub or '"' not in sub:
		for i in range(0, len(texte)):
			if texte[i] == "'" or texte[i] == '"':
				j = i-1
				if texte[j] != "\\":
					texte = texte[:i] + "\\" + texte[i:]
	return texte


"""
Elle prend en entrée le nom du fichier à analyser
Elle retourne statement, le dictionnaire contenant les informations extraites des textes
"""


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


"""
*************************************************************************************************
* Cette fonction parcours la liste des fichiers créés par scriptCut.py	 						*
* Elle prend en entrée handle, le chemin d'accès vers le dossier contenant tous les textes		*
* Elle appelle automatiquement la fonction identification pour chaque élément dans le dossier	*
* ainsi que la fonction uploadBdd pour mettre à jour la base de donnée avec les informations 	*
* extraites par identification()																*
* Elle ne retourne rien																			*
*************************************************************************************************
"""
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


"""
*********************************************************************************************************
* Cette fonction met à jour la base de donnée à partir des informations de la fonction identification()	*	
* Elle prend en entrée statement qui est un dictionnaire contenant les informations sur le texte et 	*	
* table une chaine qui contient le nom de la table à modifier.											*
* Elle retourne une chaine indiquant le nombre de lignes insérées s'il n'y a eu aucune erreur.			*
*********************************************************************************************************
"""
def uploadBdd(statement, table):

	######################################################################################################
	######## essaie de vérifier avant d'insérer mais je n'arrive pas à faire rentrer une variable #########
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



"""
************************************************************************************
* Cette fonction supprime les mots outils de la liste des mots du texte 		   *
* Elle prend en entrée nltkList qui est une liste contenant tous les mots du texte * 
* et handle qui est une chaine contenant la liste des mots outils à enlever.       *
* Elle retourne nltkList, liste contenant les mots 'filtrés'                       *
************************************************************************************
nous avons choisi de stoquer la liste des mots outils pour une facilité d'accès,
il est possible de cette manière de changer de liste entièrement au besoin
"""

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
# NE FONCTIONNE PAS
# def verifDoublons(statement):
# 	sql = "SELECT * FROM `textes` WHERE `cote` = %s AND `nb_ordre` = %s AND `volume` = %s AND `type` = %s AND `page` = %s AND `titre` = %s AND `texte` = %s;" % (statement['cote'], statement['nb_ordre'], statement['page'], statement['volume'], statement['type'], statement['titre'], statement['texte'])
# 	mycursor.execute(sql)
# 	titleList = mycursor.fetchall() #fetchall will select the last excecuted query
# 	if mycursor.rowcount == 0: #vérifie qu'il n'y a pas d'entrée avec les mêmes infos
# 		uploadBdd(statement) #appelle la fonction upload, pour mettre à jour la bdd
# 	else:
# 		print('il y a déjà', mycursor.rowcount, 'entrée(s) avec les mêmes informations')
# 	return



# Appel de la fonction create pour la table textes
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
if aOk is True :

	#récupère tous les document ".xml" dans le dossier
	############ changer le handle pour adapter à l'ordinateur ###########
	handle = "C:\\Users\\munau\\OneDrive\\Documents\\SimiliStendhal\\export"

	################################################################### ATTENTION ###################################################################
	# Si la mise à jour s'est déroulé sans erreur, mettre cette ligne en commentaire  pour ne pas télécharger deux fois les mêmes
	parcoursXml(handle)
	################################################################### ATTENTION ###################################################################


# Appel de la fonction create pour la table tokens
tokCol = ['tokenId', 'token', 'textesList', 'useTotal']
sql = """CREATE TABLE `simili_stendhal`.`tokens` 
	(`tokenId` INT NOT NULL PRIMARY KEY AUTO_INCREMENT , 
	`token` VARCHAR(250) NOT NULL , 
	`textesList` TEXT NOT NULL,
	`useTotal` INT NOT NULL)"""
bOk = create(conn, mycursor, 'tokens', tokCol, sql)

#si la table tokens à bien été créée alors on commence le travail sur les tokens
if bOk is True:

	# on récupère chaque texte de la base de donnée
	mycursor.execute("SELECT id, texte FROM simili_stendhal.textes")
	txtList = mycursor.fetchall()
	conn, mycursor = connection("root", "", "simili_stendhal")

	vocab = {}

	# parcours les textes de la requête
	for texte in txtList:
		surface = texte[1]
		surface = surface.lower()
		surface = backslashs(surface, True)

		#une fois le texte récupéré on le tokenise grâce à la librairie nltk
		words = word_tokenize(surface, language="french")

		# customStopWord est une liste de stopword à compléter au fur et à mesure des versions
		# puisque Stendhal écrit avec des abréviations ou une graphie différente 
		# ce n'est pas toujours reconnu par les analyseur, nous avons donc préféré une liste définie de termes.
		customStopWord = stopwords(french_stopwords, "C:\\Users\\munau\\OneDrive\\Documents\\GitHub\\Simili-Stendhal\\customStopWord.txt")

		#on enlève alors les stopwords et la ponctuation
		punkt = ["!", "?", ".", "…", "-", "–", "—", "—", "—", "_", ",", ";", ":", "’", "`", "{", "}", "]", "[", ")", "(", "&", "%", "+", "«", "»", "=", "*", "|", "≠", "±", "§", ]
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


		# on calcule la fréquence des mots 
		tk = FreqDist()
		# ne calcule que les mots filtrés (hors stop words)
		for word in filtre:
			tk[word] += 1
		
		# ressort un tuple contenant le mot et le nombre de fois où il apparait dans le texte
		for values in tk.items():
			mot = values[0]
			mot = backslashs(mot, False)
			mot = mot.rstrip().lstrip()
			freq = values[1]
			freK = texte[0], 'nb:', freq
			freK = backslashs(str(freK), False)
			#si le mot ne fait pas encore partie du dictionnaire on l'y ajoute
			if mot != "":
				if mot not in vocab:
					vocab[mot] = {
					'tokenId': '', 
					'token': mot,
					'useTotal': freq,
					'textesList': freK,
					}
				else : #si le mot fait déjà partie du dictionnaire on met à jour, les textes où il apparait et sa fréquence
					vocab[mot]['textesList'] = vocab[mot]['textesList'] + freK
					vocab[mot]['useTotal'] = vocab[mot]['useTotal'] + freq
	

	#transforme en chaine la liste des textes car on ne peut pas intégrer de tableau dans la base de donnée
	# met à jour la table tokens 
	for item, info in vocab.items():
		vocab[mot]['textesList'] = str(vocab[mot]['textesList'])
		uploadBdd(info, 'simili_stendhal.tokens')

else:
	print('problème avec la création de la table tokens')

# <>





conn.close()