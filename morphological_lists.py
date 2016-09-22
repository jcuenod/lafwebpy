fancy_translations = {
	"sp": {
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
	},
	"nu": {
		"sg": "Singular",
		"du": "Dual",
		"pl": "Plural",
		"unknown": "Unknown",
		"NA": "NA"
	},
	"gn": {
		"m": "Masculine",
		"f": "Feminine",
		"unknown": "Unknown",
		"NA": "NA"
	},
	"ps": {
		"p1": "First",
		"p2": "Second",
		"p3": "Third",
		"unknown": "Unknown",
		"NA": "NA"
	},
	"vt": {
		"perf": "Perfect",
		"impf": "Imperfect",
		"wayq": "Wayyiqtol",
		"impv": "Imperative",
		"infa": "Infinitive (Absolute)",
		"infc": "Infinitive (Construct)",
		"ptca": "Participle",
		"ptcp": "Participle (Passive)",
		"NA": "NA"
	},
	"vs": {
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
	},
	"st": {
		"a": "Absolute",
		"c": "Construct",
		"e": "Emphatic",
		"NA": "NA"
	}
}

def fancifier(morph_type, morph_type_key):
	return fancy_translations[morph_type][morph_type_key]
