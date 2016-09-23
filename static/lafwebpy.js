term_to_english = {
	"categories": {
		"lex_utf8": "Lexeme",
		"sp": "Part of Speech",
		"ps": "Person",
		"nu": "Number",
		"gn": "Gender",
		"vt": "Tense",
		"vs": "Stem",
		"st": "State",
		"gloss": "Gloss"
	},
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
};

function objToTable(obj) {
	$table = $("<table>").addClass("properties");
	Object.keys(obj).forEach(function(key){
		var $tr = $("<tr>");
		k = term_to_english.categories[key];
		v = term_to_english.hasOwnProperty(key) ? term_to_english[key][obj[key]] : obj[key];
		$tr.append($("<td>").append(k));
		$tr.append($("<td>").append(v));
		$tr.data("key", key);
		$tr.data("value", obj[key]);
		$table.append($tr);
	});
	return $table;
}
function searchResultsToTable(results) {
	$table = $("<table>");
	results.forEach(function(v){
		var $tr = $("<tr>");
		var h_text = v.hebrew.replace(v.clause, "<span class='highlight_clause'>" + v.clause + "</span>");
		$tr.append($("<td>").append(v.passage));
		$tr.append($("<td>").addClass("hebrew").append(h_text));
		$tr.append($("<td>").append(v.english));
		$table.append($tr);
	});
	return $("<table>").append($table);
}

var searchTerms = [];
$(document).ready(function(){
}).on("click", "span", function(){
	$.get("/api/word_data/" + $(this).data("node"), function(data){
		$(".footer div").html(objToTable(data));
		$(".footer div").append($("<a class='addTerm' href='#'>").text("add search term"));
	});
}).on("click", ".properties tr", function(){
	$(this).toggleClass("selected");
}).on("click", ".addTerm", function(){
	var $li = $("<li>");
	var li_data = {};
	$(".selected").each(function(){
		li_data[$(this).data("key")] = $(this).data("value");
		$li.append($("<span>").append($(this).data("value")));
		$(this).removeClass("selected");
	});
	searchTerms.push(li_data);

	$(".termList").append($li);
	return false;
}).on("click", ".termList li", function(){
	searchTerms.splice($(this).index(), 1);
	$(this).addClass("hidden");
	var $that = $(this);
	setTimeout(function(){
		$that.remove();
	}, 1000);
}).on("click", ".doSearch", function(){
	$.ajax({
		method: "POST",
		url: "/api/search",
		data: JSON.stringify({"query": searchTerms})
	})
	.done(function( msg ) {
		$result_div = $("<div>").addClass("results");
		$result_div.append(searchResultsToTable(msg)).appendTo("body");
	});
}).on("click", ".results", function(){
	$(this).remove();
});
