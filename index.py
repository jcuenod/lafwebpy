import sqlite3, sys, collections, re, xml.etree.ElementTree, json
from io import TextIOWrapper
from morphological_lists import book_index, generous_name
from bottle import route, get, post, request, response, redirect, run, template, static_file
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

db = sqlite3.connect("parallel_texts.sqlite")
# query = "select b_eng.* from bibles as b_wlc, bibles as b_eng where b_wlc.parallel=b_eng.parallel and b_wlc.book_number={bk} and b_wlc.chapter={ch} and b_wlc.verse={vs} and b_eng.bibletext_id=1"
query = "select text from p_text where book_number={bk} and heb_chapter={ch} and heb_verse={vs}"

def remove_tags(text):
	return ' '.join(xml.etree.ElementTree.fromstring(text).itertext())

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
		"lex_utf8": F.lex_utf8.v(node),
		"sp": F.sp.v(node),
		"ps": F.ps.v(node),
		"nu": F.nu.v(node),
		"gn": F.gn.v(node),
		"vt": F.vt.v(node), # vt = verbal tense
		"vs": F.vs.v(node), # vs = verbal stem
		"st": F.st.v(node), # construct/absolute/emphatic
		# "Suffix": F.g_prs_utf8.v(node),
		"gloss": F.gloss.v(node)
	}
	r = remove_na(r);
	# return template('json', json=r)
	response.content_type = 'application/json'
	return json.dumps(r)

@route('/static/<filename>')
def static(filename):
	return static_file(filename, root='static')


@post('/<book>/<chapter>')
def index(book, chapter):
	book = generous_name(book)
	for n in NN():
		if F.otype.v(n) == 'chapter' and F.chapter.v(n) == chapter and F.book.v(n) == book:
			book_chapter_node = n
			break
	# to_p = ''.join('<span data-node="{}">{}</span>{}'.format(w, F.g_word_utf8.v(w), F.trailer_utf8.v(w)) for w in L.d("word", book_chapter_node))
	ret = []
	for w in L.d("word", book_chapter_node):
		ret.append({ "verse": F.verse.v(L.u("verse", w)), "wid": w, "bit": F.g_word_utf8.v(w), "trailer": F.trailer_utf8.v(w) })

	# c = {
	# 	"reference": book + " " + str(chapter),
	# 	"chapter_text": to_p,
	# 	"prev_chapter": "/" + book + "/" + str(int(chapter) - 1),
	# 	"next_chapter": "/" + book + "/" + str(int(chapter) + 1)
	# }
	# return template('main', content=c)
	response.content_type = 'application/json'
	return json.dumps(ret)

def key_from_passage(a):
	passage_tuple = re.findall(r"(\S+) (\d+):(\d+)", a["passage"])[0]
	bindex = book_index(passage_tuple[0])
	r = bindex * 1000000 + int(passage_tuple[1]) * 1000 + int(passage_tuple[2])
	return r

functions = {
	"sp": lambda node, value : F.sp.v(node) == value,
	"nu": lambda node, value : F.nu.v(node) == value,
	"gn": lambda node, value : F.gn.v(node) == value,
	"ps": lambda node, value : F.ps.v(node) == value,
	"vt": lambda node, value : F.vt.v(node) == value,
	"vs": lambda node, value : F.vs.v(node) == value,
	"st": lambda node, value : F.st.v(node) == value,
	"lex_utf8": lambda node, value : F.lex_utf8.v(node).replace('=','') == value.replace('=', ''),
	"lex": lambda node, value : F.lex_utf8.v(node) == value,
	"root": lambda node, value : F.g_lex_utf8.v(node) == value
}
def test_node_with_query(query, node):
	ret = True
	for key in query:
		ret &= functions[key](node, query[key])
	return ret

def get_p_text(passage):
	cursor = db.cursor()
	bk = book_index(passage[0])
	ch = int(passage[1])
	vs = int(passage[2])
	new_query=query.format(bk=bk,ch=ch,vs=vs)
	cursor.execute(new_query)
	query_success = cursor.fetchone()
	if query_success:
		translated_verse = query_success[0]
	else:
		return ""
	return remove_tags(translated_verse)

@post('/api/search')
def search():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	query = json_response["query"]
	search_types = ["clause", "sentence", "paragraph", "verse", "phrase"]
	search_type = json_response["search_type"]
	if search_type not in search_types:
		search_type = "clause"
	arr = [[] for i in range(len(query))]
	for n in NN():
		if F.otype.v(n) == 'word':
			q_index = 0
			word_added = False
			for q in query:
				if not word_added and test_node_with_query(q, n):
					arr[q_index].append(L.u(search_type, n))
					break
				q_index += 1

	intersection = list(set.intersection(*map(set, arr)))

	retval = []
	for r in intersection:
		clause_words = L.d('word', r)
		clause_text = T.words(clause_words, fmt='ha').replace('\n','')
		passage = T.passage(r)

		# We'll traverse more carefully in the future, this is just temporary
		verse_node = r
		if F.otype.v(verse_node) != 'verse':
			verse_node = L.u('verse', r)

		if verse_node is not None:
			verse_words = L.d('word', verse_node)
			heb_verse_text = T.words(verse_words, fmt='ha').replace('\n','')
			passage_tuple = re.findall(r"(\S+) (\d+):(\d+)", passage)[0]
			p_text = get_p_text(passage_tuple)
		else:
			heb_verse_text = clause_text
			p_text = ""

		if verse_node == r:
			clause_text = ""

		retval.append({
			"passage": passage,
			"clause": clause_text,
			"hebrew": heb_verse_text,
			"english": p_text
		})
	response.content_type = 'application/json'
	# retval_sorted = sorted(retval, tcmp)
	retval_sorted = sorted(retval, key=lambda x: key_from_passage(x))
	return json.dumps(retval_sorted)

@get('/<book>')
@get('/<book>/<chapter>')
@route('/')
def root_page(book="Genesis", chapter="1"):
	return static_file("/index.html", root='static')


# run(host='localhost', port=8080)
run(host='0.0.0.0', port=8080, debug=True)
