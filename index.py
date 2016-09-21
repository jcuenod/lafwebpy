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
        sp vs vt
        otype
        g_word lex_utf8
        sp language gloss
        chapter verse
    ''','mother'),
    "prepare": prepare,
    "primary": False,
}, verbose='DETAIL')
exec(fabric.localnames.format(var='fabric'))


@route('/api/word_data/<node:int>')
def api(node):
	r = {
		"node": node,
		"sp": F.sp.v(node),
		"vt": F.vt.v(node),
		"vs": F.vs.v(node),
		"gloss": F.gloss.v(node),
		"lex": F.lex_utf8.v(node)
	}
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
