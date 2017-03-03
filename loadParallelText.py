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
	"Song_of_Songs": 22,
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

def passageToIndex(passage):
	if passage[0] not in book_to_index:
		raise IndexError("Didn't find book in index, that's bad...")
	return book_to_index[passage[0]] * 100000 + int(passage[1]) * 1000 + int(passage[2])

db = sqlite3.connect("parallel_texts.sqlite", check_same_thread=False)
# query = "select text from p_text where book_number={bk} and heb_chapter={ch} and heb_verse={vs}"
query = "select text from IndexedText where normalisedHebrewIndex={nhi}"

def getPTextFromRef(ref_tuple):
	cursor = db.cursor()
	new_query=query.format(nhi=passageToIndex(ref_tuple))
	cursor.execute(new_query)
	query_success = cursor.fetchone()
	if query_success:
		return query_success[0]
	else:
		return ""

def getPTextFromRefArray(ref_tuple_array):
	toret = {}
	index_list = list(map(lambda x: str(passageToIndex(x)), ref_tuple_array))
	query_array = "select * from IndexedText where normalisedHebrewIndex in ({index_list})".format(index_list=",".join(index_list))
	cursor = db.cursor()
	cursor.execute(query_array)
	for row in cursor:
		tuple_key = index_list.index(str(row[0]))
		toret[ref_tuple_array[tuple_key]] = row[1]

	return toret
