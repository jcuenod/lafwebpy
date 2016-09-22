import sys, collections, re
from bottle import route, run, template, static_file
from laf.fabric import LafFabric
from etcbc.preprocess import prepare

fabric = LafFabric()
source='etcbc'
version='4b'
API=fabric.load(source+version, 'lexicon', 'workshop', {
    "xmlids": {"node": False, "edge": False},
    "features": ('''
        sp nu gn ps vt vs st
        otype
        g_word lex_utf8
        language gloss
        chapter verse
    ''','mother'),
    "prepare": prepare,
    "primary": False,
}, verbose='DETAIL')
exec(fabric.localnames.format(var='fabric'))


sp_list = {
	"art": "Article",
	"verb": "Verb",
	"subs": "Noun",
	"nmpr": "Proper noun",
	"advb": "Adverb",
	"prep": "Preposition",
	"conj": "Conjunction",
	"prps": "Pers. pronoun",
	"prde": "Demons. pron.",
	"prin": "Interr. pronoun",
	"intj": "Interjection",
	"nega": "Negative",
	"inrg": "Interrogative",
	"adjv": "Adjective"
}
nu_list = {
	"sg": "Singular",
	"du": "Dual",
	"pl": "Plural",
	"unknown": "Unknown",
	"NA": "NA"
}
gn_list = {
	"m": "Masculine",
	"f": "Feminine",
	"unknown": "Unknown",
	"NA": "NA"
}
ps_list = {
	"p1": "First",
	"p2": "Second",
	"p3": "Third",
	"unknown": "Unknown",
	"NA": "NA"
}
vt_list = {
	"perf": "Perfect",
	"impf": "Imperfect",
	"wayq": "Wayyiqtol",
	"impv": "Imperative",
	"infa": "Infinitive (Absolute)",
	"infc": "Infinitive (Construct)",
	"ptca": "Participle",
	"ptcp": "Participle (Passive)",
	"NA": "NA"
}
vs_list = {
	"afel": "Af‘el",
	"etpa": "Etpa“al",
	"etpe": "Etpe‘el",
	"haf": "Haf‘el",
	"hif": "Hif‘il",
	"hit": "Hitpa“el",
	"hof": "Hof‘al",
	"hop": "Hotpa“al",
	"hsht": "Hishtaf‘al",
	"htpa": "Hitpa“al",
	"htpe": "Hitpe‘el",
	"nif": "Nif‘al",
	"nit": "Nitpa“el",
	"pael": "Pa“el",
	"pasq": "Passiveqal",
	"peal": "Pe‘al",
	"peil": "Pe‘il",
	"piel": "Pi“el",
	"pual": "Pu“al",
	"qal": "Qal",
	"shaf": "Shaf‘el",
	"tif": "Tif‘al",
	"NA": "NA"
}
st_list = {
	"a": "Absolute",
	"c": "Construct",
	"e": "Emphatic",
	"NA": "NA"
}

def remove_na(list_to_reduce):
	templist = list_to_reduce
	keys_to_remove = set()
	for key, value in templist.items():
		if value == "NA":
			keys_to_remove.add(key)
	print(keys_to_remove)
	for key in keys_to_remove:
		del templist[key]
	return templist


@route('/api/word_data/<node:int>')
def api(node):
	r = {
		"Lexeme": F.g_lex_utf8.v(node),
		"Part of Speech": sp_list[F.sp.v(node)],
		"Person": ps_list[F.ps.v(node)],
		"Number": nu_list[F.nu.v(node)],
		"Gender": gn_list[F.gn.v(node)],
		"Tense": vt_list[F.vt.v(node)], # vt = verbal tense
		"Stem": vs_list[F.vs.v(node)], # vs = verbal stem
		"State": st_list[F.st.v(node)], # construct/absolute/emphatic
		# "Suffix": F.g_prs_utf8.v(node),
		"Gloss": F.gloss.v(node)
	}
	r = remove_na(r);
	return template('json', json=r)

@route('/static/<filename>')
def static(filename):
	return static_file(filename, root='static')


@route('/<book>/<chapter>')
def index(book, chapter):
	for n in NN():
		if F.otype.v(n) == 'chapter' and F.chapter.v(n) == chapter and F.book.v(n) == book:
			book_chapter_node = n
	to_p = ''.join('<span data-node="{}">{}</span>{}'.format(w, F.g_word_utf8.v(w), F.trailer_utf8.v(w)) for w in L.d("word", book_chapter_node))
	return template('main', content=to_p)

run(host='localhost', port=8080)
