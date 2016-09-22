import sys, collections, re
from morphological_lists import fancifier
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


def remove_na(list_to_reduce):
	templist = list_to_reduce
	keys_to_remove = set()
	for key, value in templist.items():
		if value == "NA":
			keys_to_remove.add(key)
	for key in keys_to_remove:
		del templist[key]
	return templist


@route('/api/word_data/<node:int>')
def api(node):
	r = {
		"Lexeme": F.g_lex_utf8.v(node),
		"Part of Speech": fancifier("sp", F.sp.v(node)),
		"Person": fancifier("ps", F.ps.v(node)),
		"Number": fancifier("nu", F.nu.v(node)),
		"Gender": fancifier("gn", F.gn.v(node)),
		"Tense": fancifier("vt", F.vt.v(node)), # vt = verbal tense
		"Stem": fancifier("vs", F.vs.v(node)), # vs = verbal stem
		"State": fancifier("st", F.st.v(node)), # construct/absolute/emphatic
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
