from sys import getsizeof
import sqlite3, sys, collections, re, json
from collections import defaultdict
from io import TextIOWrapper
from morphological_lists import book_index, generous_name, book_abbreviation
from bottle import hook, route, get, post, request, response, redirect, run, template, static_file
from lxml import etree
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
        g_prs_utf8 g_uvf_utf8
        det
    ''','mother'),
    "prepare": prepare,
    "primary": False,
}, verbose='DETAIL')
exec(fabric.localnames.format(var='fabric'))



# PRECOMPUTE SOME USEFUL DATA
verse_node_index = defaultdict(lambda : defaultdict(dict))
word_node_list = []

print (" -- precomputing node data --")
for n in NN():
	if F.otype.v(n) == 'verse':
		verse_node_index[F.book.v(n)][int(F.chapter.v(n))][int(F.verse.v(n))] = n
	elif F.otype.v(n) == 'word':
		word_node_list.append(n)
print (" -- done precomputing --")

db = sqlite3.connect("parallel_texts.sqlite")
query = "select text from p_text where book_number={bk} and heb_chapter={ch} and heb_verse={vs}"





### WORD API ###

def remove_tags(text):
	doc = etree.XML(text)
	for br in doc.xpath("*//br"):
		br.tail = " " + br.tail if br.tail else " "
	for netNote in doc.xpath("*//br"):
		netNote.tail = " " + netNote.tail if netNote.tail else " "
	etree.strip_elements(doc, 'netNote', 'chapter', with_tail=False)
	etree.strip_tags(doc, 'bodyText', 'br')
	return etree.tostring(doc).decode("utf-8").replace("  ", " ")

def remove_na_and_empty_and_unknown(list_to_reduce):
	templist = list_to_reduce
	keys_to_remove = set()
	for key, value in templist.items():
		if value == "NA" or value == "" or value == "unknown":
			keys_to_remove.add(key)
	for key in keys_to_remove:
		del templist[key]
	return templist

@route('/api/word_data/<node:int>')
def api(node):
	r = {
		"tricons": F.lex_utf8.v(node).replace('=', '').replace('/','').replace('[',''),
		"lex_utf8": F.lex_utf8.v(node),
		"sp": F.sp.v(node),
		"ps": F.ps.v(node),
		"nu": F.nu.v(node),
		"gn": F.gn.v(node),
		"vt": F.vt.v(node), # vt = verbal tense
		"vs": F.vs.v(node), # vs = verbal stem
		"st": F.st.v(node), # construct/absolute/emphatic
		"is_definite": F.det.v(L.u("phrase_atom", node)),
		"g_prs_utf8": F.g_prs_utf8.v(node),
		"g_uvf_utf8": F.g_uvf_utf8.v(node),
		"has_suffix": "Yes" if F.g_prs_utf8.v(node) != "" else "No",
		"gloss": F.gloss.v(node)
	}
	r = remove_na_and_empty_and_unknown(r);
	response.content_type = 'application/json'
	return json.dumps(r)



### SEARCH API ###

def key_from_passage(a):
	ptup = re.findall(r"(.*) (\d+):(\d+)", a["passage"])[0]
	bindex = book_index(ptup[0])
	r = bindex * 1000000 + int(ptup[1]) * 1000 + int(ptup[2])
	return r

functions = {
	"sp": lambda node, value : F.sp.v(node) == value,
	"nu": lambda node, value : F.nu.v(node) == value,
	"gn": lambda node, value : F.gn.v(node) == value,
	"ps": lambda node, value : F.ps.v(node) == value,
	"vt": lambda node, value : F.vt.v(node) == value,
	"vs": lambda node, value : F.vs.v(node) == value,
	"st": lambda node, value : F.st.v(node) == value,
	"lex_utf8": lambda node, value : F.lex_utf8.v(node) == value,
	"g_prs_utf8": lambda node, value : F.g_prs_utf8.v(node) == value,
	"g_uvf_utf8": lambda node, value : F.g_uvf_utf8.v(node) == value,
	"is_definite": lambda node, value : F.det.v(L.u("phrase", node)) == value,
	"has_suffix": lambda node, value : (F.g_prs_utf8.v(node) == "") is (value == "No"),
	"tricons": lambda node, value : F.lex_utf8.v(node).replace('=','').replace('/','').replace('[','') == value,
	"root": lambda node, value : F.g_lex_utf8.v(node) == value,
	"gloss": lambda node, value : F.gloss.v(node) == value
}
def test_node_with_query(query, node):
	ret = True
	for key in query:
		ret &= functions[key](node, query[key])
	return ret

def passage_tuple(node):
	reference = T.passage(node)
	p_tuple = re.search('(.*)\ (\d+):(\d+)(-(\d+))?', reference)
	return {
		"book": p_tuple.group(1),
		"chapter": int(p_tuple.group(2)),
		"verse_lower": int(p_tuple.group(3)),
		"verse_upper": int(p_tuple.group(3) if p_tuple.group(5) is None else p_tuple.group(5))
	}

def get_p_text(book, chapter, verse):
	cursor = db.cursor()
	new_query=query.format(bk=book_index(book),ch=chapter,vs=verse)
	cursor.execute(new_query)
	query_success = cursor.fetchone()
	if query_success:
		translated_verse = query_success[0]
	else:
		return ""
	return remove_tags(translated_verse)

def get_words_from_verse_node_index(book_name, chapter, verse):
	try:
		return L.d('word', verse_node_index[book_name][chapter][verse])
	except:
		print(book_name)
		print(chapter)
		print(verse)
		return []

def get_parallel_text_from_node(node):
	p_ret = ""
	p = passage_tuple(node)
	for verse in range(p["verse_lower"], p["verse_upper"] + 1):
		p_ret += get_p_text(p["book"], p["chapter"], verse)
	return p_ret

def get_words_nodes_of_verse_range_from_node(node):
	words = []
	p = passage_tuple(node)
	for vs in range(p["verse_lower"], p["verse_upper"] + 1):
		words += get_words_from_verse_node_index(generous_name(p["book"]), p["chapter"], vs)
	return T.words(words, fmt='ha').replace('\n','')

def get_highlighted_words_nodes_of_verse_range_from_node(node, found_words):
	words = []
	p = passage_tuple(node)
	found_word_group = L.d('word', node)
	for vs in range(p["verse_lower"], p["verse_upper"] + 1):
		words += get_words_from_verse_node_index(generous_name(p["book"]), p["chapter"], vs)

	ret_array = []
	for w in words:
		if w in found_words:
			word_significance = "hot"
		elif w in found_word_group:
			word_significance = "warm"
		else:
			word_significance = "normal"

		if len(ret_array) == 0:
			ret_array.append({
				"significance": word_significance,
				"text": []
			})
		elif ret_array[-1]["significance"] is not word_significance:
			if len(ret_array) > 0:
				ret_array[-1]["text"] = T.words(ret_array[-1]["text"], fmt='ha').replace('\n','')
			ret_array.append({
				"significance": word_significance,
				"text": []
			})
		ret_array[-1]["text"].append(w)
	if len(ret_array) > 0:
		ret_array[-1]["text"] = T.words(ret_array[-1]["text"], fmt='ha').replace('\n','')
	return ret_array

def passage_abbreviation(reference):
	p_tuple = re.search('(.*)\ (\d+):(\d+)(-(\d+))?', reference)
	ret = book_abbreviation(p_tuple.group(1)) + " " + p_tuple.group(2) + ":" + p_tuple.group(3)
	if p_tuple.group(5) is not None:
		ret += "-" + p_tuple.group(5)
	return ret

@post('/api/search')
def search():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	query = json_response["query"]
	search_ranges = ["clause", "sentence", "paragraph", "verse", "phrase"]
	search_range = json_response["search_range"]
	if search_range not in search_ranges:
		search_range = "clause"

	word_group_with_match = [[] for i in range(len(query))]
	found_words = []
	for n in word_node_list:
		for q_index, q in enumerate(query):
			if test_node_with_query(q, n):
				search_range_node = L.u(search_range, n)
				word_group_with_match[q_index].append(search_range_node)
				found_words.append({
					"search_range_node": search_range_node,
					"word_node": n
				})
				break

	intersection = list(set.intersection(*map(set, word_group_with_match)))
	print (str(len(intersection)) + " results")
	retval = []
	for r in intersection:
		# full_verse_search_text = get_words_nodes_of_verse_range_from_node(r)
		found_word_nodes = list(map(lambda x : x["word_node"], filter(lambda x : x["search_range_node"] == r, found_words)))
		clause_text = get_highlighted_words_nodes_of_verse_range_from_node(r, found_word_nodes)
		# heb_verse_text = full_verse_search_text
		p_text = get_parallel_text_from_node(r)

		retval.append({
			"passage": passage_abbreviation(T.passage(r)),
			"clause": clause_text,
			# "hebrew": heb_verse_text, # This is unnecessary - the clause prop has highlighted hebrew...
			"english": p_text
		})
	retval_sorted = sorted(retval, key=lambda x: key_from_passage(x))

	response.content_type = 'application/json'
	return json.dumps(retval_sorted)

@post('/api/collocations')
def collocations():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	search_range = json_response["search_range"]
	search_ranges = ["clause", "sentence", "paragraph", "verse", "phrase"]
	if search_range not in search_ranges:
		search_range = "clause"
	search_query = json_response["query"]

	word_group_with_match = [[] for i in range(len(search_query))]
	for n in word_node_list:
		for q_index, q in enumerate(search_query):
			if test_node_with_query(q, n):
				search_range_node = L.u(search_range, n)
				word_group_with_match[q_index].append(search_range_node)
				# found_words.append({
				# 	"search_range_node": search_range_node,
				# 	"word_node": n
				# })
				break

	intersection = list(set.intersection(*map(set, word_group_with_match)))
	word_list = []
	for n in intersection:
		word_list += L.d("word", n)

	word_tally = {}
	for word in word_list:
		w = F.lex_utf8.v(word)
		if w in word_tally:
			word_tally[w] += 1
		else:
			word_tally[w] = 1

	word_tally_list = []
	for key in word_tally:
		word_tally_list.append({
			"lexeme": key,
			"count": word_tally[key]
		})

	word_tally_list_sorted = sorted(word_tally_list, key=lambda w: -w["count"])

	response.content_type = 'application/json'
	return json.dumps(word_tally_list_sorted)



### BARE ESSENTIAL FUNCTIONS ###

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
	ret = []
	for w in L.d("word", book_chapter_node):
		ret.append({ "verse": F.verse.v(L.u("verse", w)), "wid": w, "bit": F.g_word_utf8.v(w), "trailer": F.trailer_utf8.v(w) })
	response.content_type = 'application/json'
	return json.dumps(ret)

@get('/<book>')
@get('/<book>/<chapter>')
@route('/')
def root_page(book="Genesis", chapter="1"):
	return static_file("/index.html", root='static')

@hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

run(host='0.0.0.0', port=8080, debug=True)
