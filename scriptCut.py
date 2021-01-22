from xml.dom import minidom
from bs4 import BeautifulSoup


#Découpage des feuillets
dom = minidom.parse('Stendhal.1487945865.TEI.xml')
sections = dom.getElementsByTagName('TEI')
for indice, section in enumerate(sections):
	open("Stendhal%i.xml" % indice, 'w', encoding="utf-8").write(section.toprettyxml())

# On enlève les balises  
	tab = []
	f = open("Stendhal%i.xml" % indice, 'r', encoding="utf-8")
	try:
		for line in f:
			soup = BeautifulSoup(line)
			tab.append(soup.get_text())
	finally:
		f.close()


# On stock dans des fichiers
	f = open("Stendhal%i.txt" % indice, 'w', encoding="utf-8")
	try:
		for j in tab:
			f.write(j)
	finally:
		f.close()
	

		