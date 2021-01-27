# coding: utf8

import pymysql
import bs4 as bs
import csv
import urllib.request
import os
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords


## connection à la base de donnée pour uploader les données
conn = pymysql.connect(
	host = "localhost",
	user = "root",
	password = "",
	database = "simili_stendhal")

mycursor = conn.cursor()



training = []
def identification(fileName):
	sauce = open(fileName, encoding='utf-8')
	soup = bs.BeautifulSoup(sauce, 'lxml', from_encoding="utf-8")

	################### RECUPERER IDENTIFICATION #################
	statement = {'cote': '', 
	'ordre': '', 
	'page': '', 
	'volume': '', 
	'RV': '', 
	'titre': '',
	'lien': '', 
	'text': ''}

	for line in soup.find_all('biblscope'):
		if line.get('unit') == 'cote':
			statement['cote'] = line.text
		elif line.get('unit') == 'numero_ordre_dans_registre':
			statement['ordre'] = line.text
		elif line.get('unit') == 'numero_page':
			statement['page'] = line.text
		elif line.get('unit') == 'volume':
			statement['volume'] = line.text
	statement['RV'] = soup.msdesc.get('type')

	lien = soup.ref
	permalien = lien.get('target')

	#vérification au cas où il y ait plusieurs lie ns
	handle = "http://manuscrits-de-stendhal.org/permalien.php"
	if handle in permalien:
		statement['lien'] = permalien

	# text = soup.surface
	for paragraph in soup.find_all('surface'):
		statement['text'] = paragraph.text 
		#on retrouve les \n quand on print(statement)
		#mais ils disparaissent quand on vise statement['text']
		#donc tout va bien
		training.append(paragraph.text)


	for line in soup.find_all('textdesc'):
		if line.get('n') == 'document':
			statement['titre'] = line.text
	return statement


#fonction qui met à jour la base de donnée avec les informations récupérées par beautiful soup
def update(statement):  
	cote = statement['cote']
	ordre = statement['ordre']
	volume = statement['volume']
	page = statement['page']
	titre = statement['titre']
	lien = statement['lien']
	texte = statement['text']
	mycursor.execute(""" INSERT INTO textes(cote, nb_ordre, volume, page, titre, permalien, texte) VALUES (cote, ordre, volume, page, titre, lien, texte);
	""")

	conn.commit()
	return none



#récupère tous les document ".xml" dans le dossier
############ changer le handle pour adapter à l'ordinateur ###########
handle = "C:\\Users\\munau\\OneDrive\\Documents\\SimiliStendhal\\export"
fileList = []

# r=>root, d=>directories, f=>files
for r, d, f, in os.walk(handle):
	for item in f:
		if '.xml' in item:
			fileList.append(os.path.join(r, item))


# NE FONCTIONNE PAS
#parcours chaque fichier xml de la dir et applique la fonction identification()
# for i in range(0, len(fileList)):
# 	temp = identification(fileList[i])
# 	update(temp)




# superHash = {'link': '', 'statement': ''}


# for i in range(0, len(fileList)):
# 	superHash['link'].append(fileList[i].text)
# 	superHash['statement'].append(identification(fileList[i]))

# for value in superHash.items():
# 	print(value)


word = []
filterList = []
test = identification("C:\\Users\\munau\\OneDrive\\Documents\\SimiliStendhal\\export\\Stendhal100.xml")
stop_words = set(stopwords.words("french"))
temp = update(test)

surface = test['text']
tokenText = word_tokenize(surface)
word.append(tokenText)
# print(surface)
# print(word)
for w in word:
	if w not in stop_words:
		filterList.append(w)
# print(filterList)



# for i in range(0, 200):
# 	print(surfaces)
# 	print("\n\n")


conn.close()