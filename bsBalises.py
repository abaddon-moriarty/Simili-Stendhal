# coding: utf8


import bs4 as bs
import urllib.request
import os

def identification(sauce):
	soup = bs.BeautifulSoup(open(sauce), 'lxml', from_encoding="ISO-8859-1"
		)

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

	#vérification au cas où il y ait plusieurs liens
	handle = "http://manuscrits-de-stendhal.org/permalien.php"
	if handle in permalien:
		statement['lien'] = permalien

	# text = soup.surface
	for paragraph in soup.find_all('surface'):
		statement['text'] = paragraph.text 
		#on retrouve les \n quand on print(statement)
		#mais ils disparaissent quand on vise statement['text']
		#donc tout va bien

	for line in soup.find_all('textdesc'):
		if line.get('n') == 'document':
			statement['titre'] = line.text
	return statement


#récupère tous les document ".xml" dans le dossier
############ changer le handle pour adapter à l'ordinateur ###########
handle = "C:\\Users\\munau\\OneDrive\\Documents\\SimiliStendhal\\export"
fileList = []

# r=>root, d=>directories, f=>files
for r, d, f, in os.walk(handle):
	for item in f:
		if '.xml' in item:
			fileList.append(os.path.join(r, item))


for item in fileList:
	info = identification(item)

