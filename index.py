import datetime
from functools import reduce
import sys, collections, re, json
from io import TextIOWrapper
from morphological_lists import book_index, generous_name, book_abbreviation
from bottle import Bottle, hook, route, get, post, request, response, redirect, run, template, static_file
import paste.gzipper
from itertools import chain

from loadParallelText import getPTextFromRefPairArray

from tf.fabric import Fabric

### set up app - we're going to use it for gzip middleware ###

app = Bottle()

### load up TF ###


TF = Fabric(locations='../text-fabric-data', modules='hebrew/etcbc4c')
api = TF.load('''
	book chapter verse
	sp nu gn ps vt vs st
	otype
	det
	g_word_utf8 trailer_utf8
	lex_utf8 lex voc_utf8
	g_prs_utf8 g_uvf_utf8
	prs_gn prs_nu prs_ps g_cons_utf8
	gloss sdbh lxxlexeme
	accent accent_quality
	tab typ
''')
api.makeAvailableIn(globals())



### WORD API ###

def remove_na_and_empty_and_unknown(list_to_reduce):
	templist = list_to_reduce
	keys_to_remove = set()
	for key, value in templist.items():
		if value == "NA" or value == "" or value == "unknown" or value is None:
			keys_to_remove.add(key)
	for key in keys_to_remove:
		del templist[key]
	return templist

def word_data(node):
	r = {
		"tricons": F.lex_utf8.v(node).replace('=', '').replace('/','').replace('[',''),
		"sdbh": F.sdbh.v(node),
		"lex": F.lex.v(node),
		"voc_utf8": F.voc_utf8.v(L.u(node, otype='lex')[0]),
		"lxxlexeme": F.lxxlexeme.v(node),
		"sp": F.sp.v(node),
		"ps": F.ps.v(node),
		"nu": F.nu.v(node),
		"gn": F.gn.v(node),
		"vt": F.vt.v(node), # vt = verbal tense
		"vs": F.vs.v(node), # vs = verbal stem
		"st": F.st.v(node), # construct/absolute/emphatic
		# "type": F.typ.v(L.u(node, otype='phrase')[0]),
		"is_definite": F.det.v(L.u(node, otype='phrase_atom')[0]),
		"g_prs_utf8": F.g_prs_utf8.v(node),
		"g_uvf_utf8": F.g_uvf_utf8.v(node),
		"g_cons_utf8": F.g_cons_utf8.v(node),
		"prs_nu": F.prs_nu.v(node),
		"prs_gn": F.prs_gn.v(node),
		"prs_ps": F.prs_ps.v(node),
		"accent": F.accent.v(node),
		"accent_quality": F.accent_quality.v(node),
		"has_suffix": "Yes" if F.g_prs_utf8.v(node) != "" else "No",
		"gloss": F.gloss.v(L.u(node, otype='lex')[0]),
	}
	return remove_na_and_empty_and_unknown(r);

@app.post('/api/word_data')
def api_word_data():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	node = int(json_response["word_id"])
	wdata = word_data(node)
	response.content_type = 'application/json'
	return json.dumps(wdata)



### SEARCH API ###

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
	"voc_utf8": lambda node, value : F.voc_utf8.v(L.u(node, otype='lex')[0]) == value,
	"lxxlexeme": lambda node, value : F.lxxlexeme.v(node) == value,
	"prs_nu": lambda node, value : F.prs_nu.v(node) == value,
	"prs_gn": lambda node, value : F.prs_gn.v(node) == value,
	"prs_ps": lambda node, value : F.prs_ps.v(node) == value,
	"g_prs_utf8": lambda node, value : F.g_prs_utf8.v(node) == value,
	"g_uvf_utf8": lambda node, value : F.g_uvf_utf8.v(node) == value,
	"g_cons_utf8": lambda node, value : F.g_cons_utf8.v(node) == value,
	"accent": lambda node, value : F.accent.v(node) == value,
	"accent_quality": lambda node, value : F.accent_quality.v(node) == value,
	# "type": lambda node, value : F.typ.v(L.u(node, otype='phrase')[0]) == value,
	"is_definite": lambda node, value : F.det.v(L.u(node, otype='phrase_atom')[0]) == value,
	"has_suffix": lambda node, value : (F.g_prs_utf8.v(node) == "") is (value == "No"),
	"tricons": lambda node, value : F.lex_utf8.v(node).replace('=','').replace('/','').replace('[','') == value,
	 # note that this is not the other "root"
	"rootregex": lambda node, value : re.match(value, F.lex_utf8.v(node)) != None or re.match(value, F.lex.v(node)) != None,
	# "root": lambda node, value : F.g_lex_utf8.v(node) == value,
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

def get_highlighted_words_nodes_of_verse_range_from_node(node, found_words):
	words = []
	p = passage_tuple(node)
	found_word_group = L.d(node, otype='word')

	# broad_node = T.nodeFromSection(T.sectionFromNode(node))
	verse = node
	if F.otype.v(node) == "verse":
		verse = [node]
	else:
		verse = L.u(node, otype='verse')
		if len(verse) == 0:
			verse = []
			for v in range(p["verse_lower"], p["verse_upper"] + 1):
				verse.append(T.nodeFromSection((p["book"], p["chapter"], v)))

	if len(verse) == 1:
		words = L.d(verse[0], otype='word')
	else:
		for n in verse:
			words += L.d(n, otype='word')

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

def get_filtered_search_range(filterToUse):
	search_range_filtered = F.otype.s('word')
	if len(filterToUse) > 0:
		temp_search_range_filtered = []
		for sfilter in filterToUse:
			filter_node = T.nodeFromSection((generous_name(sfilter),))
			if filter_node is not None:
				temp_search_range_filtered = list(chain(temp_search_range_filtered, L.d(filter_node, otype='word')))
			else:
				print("Dropped a filter category: ", sfilter)
		if len(temp_search_range_filtered) > 0:
			search_range_filtered = temp_search_range_filtered
	return search_range_filtered



@app.post('/api/search')
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

	search_range_filtered = get_filtered_search_range(json_response["search_filter"] if "search_filter" in json_response else [])

	word_groups_to_exclude = []
	word_group_with_match = [[] for i in range(len(query))]
	found_words = []

	for n in search_range_filtered:
		inverted_search_done = False
		regular_search_done = False
		for q_index, q in enumerate(query):
			query_inverted = "invert" in q
			if (inverted_search_done and query_inverted) or (regular_search_done and not query_inverted):
				continue
			if test_node_with_query(n, q):
				search_range_node = L.u(n, otype=search_range)[0]
				word_group_with_match[q_index].append(search_range_node)
				found_words.append({
					"search_range_node": search_range_node,
					"word_node": n
				})
				if query_inverted:
					inverted_search_done = True
				else:
					regular_search_done = True
				if regular_search_done and inverted_search_done:
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
	truncated = False
	if len(intersection) > 1000:
		intersection = intersection[:500]
		print ("Abbreviating to just 500 elements")
		truncated = True


	retval = []
	for r in intersection:
		found_word_nodes = list(map(lambda x : x["word_node"], filter(lambda x : x["search_range_node"] == r, found_words)))
		clause_text = get_highlighted_words_nodes_of_verse_range_from_node(r, found_word_nodes)
		retval.append({
			"passage": passage_abbreviation(r),
			"node": r,
			"clause": clause_text,
		})

	# Grab parallel text
	parallel_text = getPTextFromRefPairArray(list(map(lambda x: (T.sectionFromNode(x["node"]), T.sectionFromNode(x["node"], lastSlot=True)), retval)))
	if len(parallel_text) != len(retval):
		print("how can we have different values?!?")
		exit(1)
	for i in range(len(parallel_text)):
		retval[i]["english"] = parallel_text[i]
	retval_sorted = sorted(retval, key=lambda r: sortKey(r["node"]))

	response.content_type = 'application/json'
	return json.dumps({
		"truncated": truncated,
		"search_results": retval_sorted
	})


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

@app.post('/api/collocations')
def api_collocations():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	search_range = json_response["search_range"]
	search_ranges = ["clause", "sentence", "paragraph", "verse", "phrase"]
	if search_range not in search_ranges:
		search_range = "clause"
	search_query = list(filter(lambda x: len(list(x.keys())) > 0, json_response["query"]))

	search_range_filtered = get_filtered_search_range(json_response["search_filter"] if "search_filter" in json_response else [])

	word_group_with_match = [[] for i in range(len(search_query))]
	for n in search_range_filtered:
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
	return json.dumps({
		"truncated": False,
		"search_results": word_tally_list_sorted
	})

@app.post('/api/word_study')
def api_word_study():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	query = list(filter(lambda x: len(list(x.keys())) > 0, json_response["query"]))

	search_range_filtered = get_filtered_search_range(json_response["search_filter"] if "search_filter" in json_response else [])

	column_list = []
	results = []
	for word in search_range_filtered:
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

	response.content_type = 'application/json'
	return json.dumps({
		"truncated": False,
		"search_results": {
			"columns": column_list,
			"rows": results
		}
	})

@app.post('/api/book_chapter')
def api_book_chapter():
	json_response = json.load(TextIOWrapper(request.body))
	print(json_response)
	reference = json_response["reference"]
	book = generous_name(reference["book"])
	chapter = int(reference["chapter"]) # This needs to be a string for the if...
	book_chapter_node = T.nodeFromSection((book, chapter))

	if "display_by" not in json_response:
		json_response["display_by"] = "verse"
	display_setting_options = ["verse", "clause"]
	display_setting = json_response["display_by"] if json_response["display_by"] in display_setting_options else "verse"

	highlights = {}
	if "highlights" in json_response:
		highlights = json_response["highlights"]

	chapter_data = []
	if display_setting == "clause":
		for c in L.d(book_chapter_node, otype='clause_atom'):
			clause_atom_words = []
			accent_unit_chunk = []
			previous_trailer = " "
			for w in L.d(c, otype='word'):
				highlightMatches = [k for k, c in highlights.items() if test_node_with_query(w, c)]
				if previous_trailer not in {'', '־'}:
					if len(accent_unit_chunk) > 0:
						clause_atom_words.append(accent_unit_chunk)
						accent_unit_chunk = []
				accent_unit_chunk.append({
					"wid": w,
					"bit": F.g_word_utf8.v(w),
					"trailer": F.trailer_utf8.v(w),
					"highlights": highlightMatches,
				})
				previous_trailer = F.trailer_utf8.v(w)
			if len(accent_unit_chunk) > 0:
				clause_atom_words.append(accent_unit_chunk)

			chapter_data.append({
				"verse": T.sectionFromNode(c)[2],
				"tab": F.tab.v(c),
				"type": F.typ.v(c),
				"clause_words": clause_atom_words,
			})

	elif display_setting == "verse":
		for v in L.d(book_chapter_node, otype='verse'):
			verse_words = []
			accent_unit_chunk = []
			previous_trailer = " "
			for w in L.d(v, otype='word'):
				highlightMatches = [k for k, v in highlights.items() if test_node_with_query(w, v)]
				if previous_trailer not in {'', '־'}:
					if len(accent_unit_chunk) > 0:
						verse_words.append(accent_unit_chunk)
					accent_unit_chunk = []
				accent_unit_chunk.append({
					"wid": w,
					"bit": F.g_word_utf8.v(w),
					"trailer": F.trailer_utf8.v(w),
					"highlights": highlightMatches,
				})
				previous_trailer = F.trailer_utf8.v(w)
			if len(accent_unit_chunk) > 0:
				verse_words.append(accent_unit_chunk)

			chapter_data.append({
				"verse": F.verse.v(v),
				"verse_words": verse_words
			})


	response.content_type = 'application/json'
	ret = {
		"reference": { "book": book, "chapter": chapter },
		"display_by": display_setting,
		"chapter_data": chapter_data
	}
	return json.dumps(ret)

	# This is a good way of getting the range of word nodes given an arbitrary starting and ending verse
	####
	# startingReference = ("Isaiah", 52, 13)
	# endingReference = ("Isaiah", 53, 12)
	# firstNode = L.d(T.nodeFromSection(startingReference), otype="word")[0]
	# lastNode = L.d(T.nodeFromSection(endingReference), otype="word")[-1]
	# nodeRange = range(firstNode, lastNode+1)
	# wordNodeRange = filter(lambda x: F.otype.v(x) == "word", nodeRange)


### BARE ESSENTIAL FUNCTIONS ###

@app.get('/<filename:re:.*\.js>')
@app.get('/<filename:re:.*\.css>')
@app.get('/<filename:re:.*\.svg>')
@app.get('/<filename:re:.*\.png>')
@app.get('/<filename:re:.*\.map>')
@app.route('/static/<filename>')
def static(filename):
	response = static_file(filename, root='../react-lafwebpy-client/build')
	response.set_header('Cache-Control', 'public, max-age=0')
	return response

@app.get('/<book>')
@app.get('/<book>/<chapter>')
@app.route('/')
def root_page(book="Genesis", chapter="1"):
	response = static_file("/index.html", root='../react-lafwebpy-client/build')
	response.set_header('Cache-Control', 'public, max-age=0')
	return response

@app.hook('after_request')
def enable_cors():
	response.headers['Access-Control-Allow-Origin'] = '*'

@app.hook('before_request')
def log_the_request():
	client_ip = request.environ.get('REMOTE_ADDR')
	client_path = request.path
	client_payload = str(vars(request.POST))
	with open('log/clients.log', mode='a', encoding='utf-8') as out:
		out.write(client_ip + "\t" + str(datetime.datetime.now()) +  "\t" + client_path + "\t" + client_payload + "\n")


port_to_host_on = 80
if len(sys.argv) > 1:
	if sys.argv[1].isdigit():
		port_to_host_on = int(sys.argv[1])


app = paste.gzipper.middleware(app)
run(app, host='0.0.0.0', port=port_to_host_on, server='paste', debug=True)
