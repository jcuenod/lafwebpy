from sys import getsizeof
from functools import reduce
import sqlite3, sys, collections, re, json
from collections import defaultdict
from io import TextIOWrapper
from morphological_lists import book_index, generous_name, book_abbreviation
from bottle import hook, route, get, post, request, response, redirect, run, template, static_file
from lxml import etree

from tf.fabric import Fabric

TF = Fabric(locations='../text-fabric-data', modules='hebrew/etcbc4c')
api = TF.load('''
	sp nu gn ps vt vs st
	otype
	 lex_utf8
	language gloss
	chapter verse
	g_prs_utf8 g_uvf_utf8
	det book chapter verse sdbh lxxlexeme

	trailer_utf8 g_word_utf8 lex
	prs_gn prs_nu prs_ps
''')
api.makeAvailableIn(globals())



# PRECOMPUTE SOME USEFUL DATA
verse_node_index = defaultdict(lambda : defaultdict(dict))
# word_node_list = []

# print (" -- precomputing node data --")
# for n in F.otype.s('verse'):
# 	verse_node_index[F.book.v(n)][int(F.chapter.v(n))][int(F.verse.v(n))] = n
# print (" -- done precomputing --")

db = sqlite3.connect("parallel_texts.sqlite", check_same_thread=False)
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

def word_data(node):
	r = {
		"tricons": F.lex_utf8.v(node).replace('=', '').replace('/','').replace('[',''),
		"sdbh": F.sdbh.v(node),
		"lex": F.lex.v(node),
		"lxxlexeme": F.lxxlexeme.v(node),
		"sp": F.sp.v(node),
		"ps": F.ps.v(node),
		"nu": F.nu.v(node),
		"gn": F.gn.v(node),
		"vt": F.vt.v(node), # vt = verbal tense
		"vs": F.vs.v(node), # vs = verbal stem
		"st": F.st.v(node), # construct/absolute/emphatic
		"is_definite": F.det.v(L.u(node, otype='phrase_atom')[0]),
		"g_prs_utf8": F.g_prs_utf8.v(node),
		"g_uvf_utf8": F.g_uvf_utf8.v(node),
		"prs_nu": F.prs_nu.v(node),
		"prs_gn": F.prs_gn.v(node),
		"prs_ps": F.prs_ps.v(node),
		"has_suffix": "Yes" if F.g_prs_utf8.v(node) != "" else "No",
		"gloss": F.gloss.v(L.u(node, otype='lex')[0]),
		"invert": "t",
	}
	return remove_na_and_empty_and_unknown(r);

@post('/api/word_data')
def api_word_data():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	node = int(json_response["word_id"])
	wdata = word_data(node)
	response.content_type = 'application/json'
	return json.dumps(wdata)



### SEARCH API ###

def key_from_passage(ptup):
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
	"sdbh": lambda node, value : F.sdbh.v(node) == value,
	"lex": lambda node, value : F.lex.v(node) == value,
	"lxxlexeme": lambda node, value : F.lxxlexeme.v(node) == value,
	"prs_nu": lambda node, value : F.prs_nu.v(node) == value,
	"prs_gn": lambda node, value : F.prs_gn.v(node) == value,
	"prs_ps": lambda node, value : F.prs_ps.v(node) == value,
	"g_prs_utf8": lambda node, value : F.g_prs_utf8.v(node) == value,
	"g_uvf_utf8": lambda node, value : F.g_uvf_utf8.v(node) == value,
	"is_definite": lambda node, value : F.det.v(L.u("phrase", node)) == value,
	"has_suffix": lambda node, value : (F.g_prs_utf8.v(node) == "") is (value == "No"),
	"tricons": lambda node, value : F.lex_utf8.v(node).replace('=','').replace('/','').replace('[','') == value,
	"root": lambda node, value : F.g_lex_utf8.v(node) == value,
	"gloss": lambda node, value : value in F.gloss.v(L.u(node, otype='lex')[0]),
	"invert": lambda node, value : True
}
def test_node_with_query(node, query):
	ret = True
	for key in query:
		ret &= functions[key](node, query[key])
		if not ret:
			return False
	return True

def passage_tuple(node):
	reference = T.sectionFromNode(node)
	last_reference = T.sectionFromNode(node, lastSlot=True)
	# p_tuple = re.search('(.*)\ (\d+):(\d+)(-(\d+))?', reference)
	return {
		"book": reference[0], #p_tuple.group(1),
		"chapter": reference[1],  # p_tuple.group(2)),
		"verse_lower": reference[2],  # p_tuple.group(3)),
		# "verse_upper": int(p_tuple.group(3) if p_tuple.group(5) is None else p_tuple.group(5))
		"verse_upper": last_reference[2] if reference[2] != last_reference[2] else reference[2]
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

# def get_words_from_verse_node_index(book_name, chapter, verse):
# 	try:
# 		return L.d('word', verse_node_index[book_name][chapter][verse])
# 	except:
# 		print(book_name, chapter, verse)
# 		return []

def get_parallel_text_from_node(node):
	p_ret = ""
	p = passage_tuple(node)
	for verse in range(p["verse_lower"], p["verse_upper"] + 1):
		p_ret += get_p_text(p["book"], p["chapter"], verse)
	return p_ret

# def get_words_nodes_of_verse_range_from_node(node):
# 	words = []
# 	p = passage_tuple(node)
# 	for vs in range(p["verse_lower"], p["verse_upper"] + 1):
# 		words += get_words_from_verse_node_index(generous_name(p["book"]), p["chapter"], vs)
# 	return T.words(words, fmt='ha').replace('\n','')

def get_highlighted_words_nodes_of_verse_range_from_node(node, found_words):
	words = []
	p = passage_tuple(node)
	found_word_group = L.d(node, otype='word')

	# broad_node = T.nodeFromSection(T.sectionFromNode(node))
	verse = L.u(node, otype='verse')
	if len(verse) == 1:
		words = L.d(verse[0], otype='word')
	else:
		for vs in L.d(node, otype='verse'):
			words += L.d(vs, otype='word')


	# for vs in L.u(node, otype='verse'):
	# 	words += L.d(vs, otype='word')

	# for vs in range(p["verse_lower"], p["verse_upper"] + 1):
		# words += get_words_from_verse_node_index(generous_name(p["book"]), p["chapter"], vs)
		# words += T.

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
				ret_array[-1]["text"] = T.text(ret_array[-1]["text"]).replace('\n','')
			ret_array.append({
				"significance": word_significance,
				"text": []
			})
		ret_array[-1]["text"].append(w)
	if len(ret_array) > 0:
		ret_array[-1]["text"] = T.text(ret_array[-1]["text"]).replace('\n','')
	return ret_array

def passage_abbreviation(node):
	first_node = T.sectionFromNode(node, lang='sbl')
	last_node = T.sectionFromNode(node, lastSlot=True, lang='sbl')
	suffix = "‑" + str(last_node[2]) if first_node[2] != last_node[2] else ""
	return "{0} {1:d}:{2:d}".format(*first_node) + suffix

# def passage_abbreviation(reference):
# 	# p_tuple = re.search('(.*)\ (\d+):(\d+)(-(\d+))?', reference)
# 	# ret = book_abbreviation(p_tuple.group(1)) + " " + p_tuple.group(2) + ":" + p_tuple.group(3)
# 	# if p_tuple.group(5) is not None:
# 	# 	ret += "-" + p_tuple.group(5)
# 	ret = str(reference)
# 	return ret

@post('/api/search')
def api_search():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	query = list(filter(lambda x: len(list(x.keys())) > 0, json_response["query"]))
	if len(query) == 0:
		response.content_type = 'application/json'
		return json.dumps([])
	search_ranges = ["clause", "sentence", "paragraph", "verse", "phrase"]
	search_range = json_response["search_range"]
	if search_range not in search_ranges:
		search_range = "clause"

	word_groups_to_exclude = []
	word_group_with_match = [[] for i in range(len(query))]
	found_words = []
	for n in F.otype.s('word'):
		for q_index, q in enumerate(query):
			if test_node_with_query(n, q):
				search_range_node = L.u(n, otype=search_range)[0]
				word_group_with_match[q_index].append(search_range_node)
				found_words.append({
					"search_range_node": search_range_node,
					"word_node": n
				})
				break

	words_groups_to_intersect = []
	words_groups_to_filter = []
	for q_index, q in enumerate(query):
		if "invert" in q and q["invert"] == "t":
			words_groups_to_filter += word_group_with_match[q_index]
		else:
			words_groups_to_intersect.append(word_group_with_match[q_index])


	intersection_to_filter = list(set.intersection(*map(set, words_groups_to_intersect)))
	intersection = list(filter(lambda x: x not in words_groups_to_filter, intersection_to_filter))
	print (str(len(intersection)) + " results")

	# Truncate array if too long
	if len(intersection) > 200:
		intersection = intersection[:100]
		print ("Abbreviating to just 100 elements")

	retval = []
	for r in intersection:
		# full_verse_search_text = get_words_nodes_of_verse_range_from_node(r)
		found_word_nodes = list(map(lambda x : x["word_node"], filter(lambda x : x["search_range_node"] == r, found_words)))
		clause_text = get_highlighted_words_nodes_of_verse_range_from_node(r, found_word_nodes)
		# heb_verse_text = full_verse_search_text
		p_text = get_parallel_text_from_node(r)

		retval.append({
			"passage": passage_abbreviation(r),
			"node": r,

			# "passage": passage_abbreviation(str(T.sectionFromNode(r))),
			"clause": clause_text,
			# "hebrew": heb_verse_text, # This is unnecessary - the clause prop has highlighted hebrew...
			"english": p_text
		})
	# retval_sorted = sorted(retval, key=lambda x: key_from_passage(x["passage"]))
	retval_sorted = sorted(retval, key=lambda r: sortKey(r["node"]))

	response.content_type = 'application/json'
	return json.dumps(retval_sorted)


def appended_formatted_list(original_dict, node):
	new_dict = original_dict.copy()
	reference = node
	p_tuple = passage_tuple(reference)
	abbreviated_book_name = book_abbreviation(p_tuple["book"])
	if abbreviated_book_name not in original_dict:
		new_dict[abbreviated_book_name] = {}
	if p_tuple["chapter"] not in new_dict[abbreviated_book_name]:
		new_dict[abbreviated_book_name][p_tuple["chapter"]] = []
	verse_range = p_tuple["verse_lower"]
	if p_tuple["verse_lower"] is not p_tuple["verse_upper"]:
		verse_range += "-" + p_tuple["verse_upper"]
	if verse_range not in new_dict[abbreviated_book_name][p_tuple["chapter"]]:
		new_dict[abbreviated_book_name][p_tuple["chapter"]].append(verse_range)
	return new_dict

@post('/api/collocations')
def api_collocations():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	search_range = json_response["search_range"]
	search_ranges = ["clause", "sentence", "paragraph", "verse", "phrase"]
	if search_range not in search_ranges:
		search_range = "clause"
	search_query = json_response["query"]

	word_group_with_match = [[] for i in range(len(search_query))]
	for n in F.otype.s('word'):
		for q_index, q in enumerate(search_query):
			if test_node_with_query(n, q):
				search_range_node = L.u(n, otype=search_range)[0]
				word_group_with_match[q_index].append(search_range_node)
				break

	intersection = list(set.intersection(*map(set, word_group_with_match)))
	word_list = []
	for n in intersection:
		word_list += L.d(n, otype='word')

	word_tally = {}
	for word in word_list:
		w = F.lex_utf8.v(word)
		if w in word_tally:
			word_tally[w]["count"] += 1
			word_tally[w]["references"] = appended_formatted_list(word_tally[w]["references"], word)
		else:
			word_tally[w] = {
				"count": 1,
				"references": appended_formatted_list({}, word)
			}

	word_tally_list = []
	for key in word_tally:
		word_tally_list.append({
			"lexeme": key,
			"count": word_tally[key]["count"],
			"references": word_tally[key]["references"]
		})

	word_tally_list_sorted = sorted(word_tally_list, key=lambda w: -w["count"])

	response.content_type = 'application/json'
	return json.dumps(word_tally_list_sorted)

@post('/api/word_study')
def api_word_study():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	query = json_response["query"]

	column_list = []
	results = []
	for word in F.otype.s('word'):
		if not reduce(lambda x, y: x and test_node_with_query(word, y), query, True):
			continue
		wd = word_data(word)
		ref = T.sectionFromNode(word, lang='sbl')
		wd["book"] = ref[0]
		wd["ch"] = ref[1]
		wd["v"] = ref[2]
		results.append(wd)
		keys_to_add = list(wd.keys())
		if len(column_list) > 0:
			keys_to_add = set(keys_to_add) - set(map(lambda x: x["header"],column_list))
		for k in keys_to_add:
			column_list.append({
				"header": k,
				"accessor": k,
			})

	r = {
		"truncated": False,
		"search_results": {
			"columns": column_list,
			"rows": results
		}
	}
	response.content_type = 'application/json'
	return json.dumps(r)

@post('/api/book_chapter')
def api_book_chapter():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	book = generous_name(json_response["book"])
	chapter = int(json_response["chapter"]) # This needs to be a string for the if...
	book_chapter_node = T.nodeFromSection((book, chapter))
	chapter_data = []
	for v in L.d(book_chapter_node, otype='verse'):
		verse = F.verse.v(v)
		for w in L.d(v, otype='word'):
			chapter_data.append({ "verse": verse, "wid": w, "bit": F.g_word_utf8.v(w), "trailer": F.trailer_utf8.v(w) })
	response.content_type = 'application/json'
	ret = {
		"reference": { "book": book, "chapter": chapter },
		"chapter_data": chapter_data
	}
	return json.dumps(ret)


### BARE ESSENTIAL FUNCTIONS ###

@get('/<filename:re:.*\.js>')
@get('/<filename:re:.*\.css>')
@get('/<filename:re:.*\.svg>')
@get('/<filename:re:.*\.png>')
@get('/<filename:re:.*\.map>')
@route('/static/<filename>')
def static(filename):
	return static_file(filename, root='../react-lafwebpy-client/build')

@get('/<book>')
@get('/<book>/<chapter>')
@route('/')
def root_page(book="Genesis", chapter="1"):
	return static_file("/index.html", root='../react-lafwebpy-client/build')

@hook('after_request')
def enable_cors():
	response.headers['Access-Control-Allow-Origin'] = '*'

port_to_host_on = 80
if len(sys.argv) > 1:
	if sys.argv[1].isdigit():
		port_to_host_on = int(sys.argv[1])
run(host='0.0.0.0', port=port_to_host_on, server='paste', debug=True)
