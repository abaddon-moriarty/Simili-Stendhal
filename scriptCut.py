from xml.dom import minidom

"""
	Ce script va donner en sortie les fichiers xml découpé à la balise <TEI>.
	Ici, on va donc avoir 2462 fichiers xml qui représente chaque page des manuscrits de Stendhal.
"""

#Découpage des feuillets à chaque balise <TEI>.
dom = minidom.parse('Stendhal.1487945865.TEI.xml')
sections = dom.getElementsByTagName('TEI')
for indice, section in enumerate(sections):
	open("Stendhal%i.xml" % indice, 'w', encoding="utf-8").write(section.toprettyxml())


	

		
