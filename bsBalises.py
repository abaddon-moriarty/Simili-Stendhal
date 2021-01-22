import bs4 as bs
import urllib.request

# def cookingBalise(url, fileName, mode)
sauce = urllib.request.urlopen("http://stendhal.demarre-shs.fr/catalogue_TEI/5896-21-019.tei.xml").read()
soup = bs.BeautifulSoup(sauce, 'lxml')


################### RECUPERER TEXTE #################

 


#### AJOUTER TEXTE A LA BDD ####




################### RECUPERER IDENTIFICATION #################
statement = {'cote': '', 'ordre': '', 'page': '', 'volume': '', 'RV': '', 'lien': '', 'text': ''}

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

#vérification au cas ou il y ait plusieurs liens
handle = "http://manuscrits-de-stendhal.org/permalien.php"
if handle in permalien:
	statement['lien'] = permalien

# text = soup.surface
for paragraph in soup.find_all('surface'):
	statement['text'] = paragraph.text 
	#on retrouve les \n quand on print(statement)
	#mais ils disparaissent quand on vise statement['text']
	#donc tout va bien

print(statement)
print(statement['text'])


########## AJOUTER LA BDD ############


