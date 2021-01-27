import nltk
from nltk.tokenize import word_tokenize, PunktSentenceTokenizer
from nltk.corpus import stopwords, state_union
from nltk.stem import PorterStemmer


example_sentence = "A la fin de l'hiver de 1803 Madame Valbelle vint habiter le village d'Auteuil près paris. Elle loua une maison de campagne au milieu des plus beaux bois du pays qui en a de charmans. C'était une femme de 40 ans, cachant une profonde ambition sous l'air le plus naturel et le plus desocupé. Elle recevait à Paris le plus grand monde particuliérement les gens en place. tout le monde était content d'elle parce qu'elle se pliait au caractére de tout le monde. la chronique scandaleuse se taisait sur son compte, on lui reprochait seulement une liaison un peu trop suivie avec M.r de Chamoucy, le jeune homme le plus élégant de la capitale, il avait beaucoup d'esprit un naturel charmant, mais sa fortune ne répondait pas à ses vœux. Il n'avait de moyen de l'augmenter que son crédit qui était trés étendu, mais pour en tirer parti il lui falait un premier fond, aussi ses ennemis publiaient ils qu'il cherchait avidement une"
stop_words = set(stopwords.words('French'))
train_sentence = "Si vous êtes discret, ne lisez pas. Si vous n'êtes pas discret, mais cependant honnête homme dans les choses essentielles, lisez et moquez vous de l'auteur, mais ne répétez pas ce que vous aurez lu. Coste, chef de bataillon. Commentaire sur la page (Cécile Meynard)"


words = word_tokenize(example_sentence)

filtered_sentence = []

for w in words:
	if w not in stop_words:
		filtered_sentence.append(w)

################# STEMMING

ps = PorterStemmer()
# for w in words:
	# print(ps.stem(w))


################ POS

custom_sent_tokenizer = PunktSentenceTokenizer(example_sentence)

tokenized = custom_sent_tokenizer.tokenize(train_sentence)
def process_content():
	try:
		for i in tokenized:
			words = nltk.word_tokenize(i)
			tagged = nltk.pos_tag(words)
			print(tagged)
	except Exception as e:
		print(str(e))
process_content()