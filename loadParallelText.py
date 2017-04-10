import sqlite3

# tf book@en to index in sqlite file
book_to_index = {
	"Genesis": 1,
	"Exodus": 2,
	"Leviticus": 3,
	"Numbers": 4,
	"Deuteronomy": 5,
	"Joshua": 6,
	"Judges": 7,
	"Ruth": 8,
	"1_Samuel": 9,
	"2_Samuel": 10,
	"1_Kings": 11,
	"2_Kings": 12,
	"1_Chronicles": 13,
	"2_Chronicles": 14,
	"Ezra": 15,
	"Nehemiah": 16,
	"Esther": 17,
	"Job": 18,
	"Psalms": 19,
	"Proverbs": 20,
	"Ecclesiastes": 21,
	"Song_of_songs": 22,
	"Isaiah": 23,
	"Jeremiah": 24,
	"Lamentations": 25,
	"Ezekiel": 26,
	"Daniel": 27,
	"Hosea": 28,
	"Joel": 29,
	"Amos": 30,
	"Obadiah": 31,
	"Jonah": 32,
	"Micah": 33,
	"Nahum": 34,
	"Habakkuk": 35,
	"Zephaniah": 36,
	"Haggai": 37,
	"Zechariah": 38,
	"Malachi": 39,
}

def refTupleToIndex(ref_tuple):
	if ref_tuple[0] not in book_to_index:
		print(ref_tuple)
		raise IndexError("Didn't find book in index, that's bad...")
	return book_to_index[ref_tuple[0]] * 1000000 + int(ref_tuple[1]) * 1000 + int(ref_tuple[2])

db = sqlite3.connect("parallel_texts.sqlite", check_same_thread=False)

def getPTextFromRefPairArray(ref_pair_tuple_array):
	if len(ref_pair_tuple_array) == 0:
		return []

	range_array = []
	where_clause = ""
	for i, ref_pair_tuple in enumerate(ref_pair_tuple_array):
		start_index = refTupleToIndex(ref_pair_tuple[0])
		end_index   = refTupleToIndex(ref_pair_tuple[1])
		where_clause += """(normalisedHebrewIndex >= {start} AND normalisedHebrewIndex <= {end}) OR """.format(start=start_index, end=end_index)
		range_array.append({"start": start_index, "end": end_index, "i": i})
	where_clause = where_clause[:-4]

	toret = [""] * len(ref_pair_tuple_array)
	query_array = """
		SELECT normalisedHebrewIndex, text FROM IndexedText
			WHERE {wc}
			ORDER BY normalisedHebrewIndex ASC""".format(wc=where_clause)
	cursor = db.cursor()
	cursor.execute(query_array)
	for row in cursor:
		for index in filter(lambda x: x["start"] <= row[0] and x["end"] >= row[0], range_array):
			toret[index["i"]] += row[1]

	return toret
