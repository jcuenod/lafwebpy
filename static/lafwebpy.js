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
ot_books = [
	"Genesis",
	"Exodus",
	"Leviticus",
	"Numbers",
	"Deuteronomy",
	"Joshua",
	"Judges",
	"Ruth",
	"1 Samuel",
	"2 Samuel",
	"1 Kings",
	"2 Kings",
	"1 Chronicles",
	"2 Chronicles",
	"Ezra",
	"Nehemiah",
	"Esther",
	"Job",
	"Psalms",
	"Proverbs",
	"Ecclesiastes",
	"Song of Solomon",
	"Isaiah",
	"Jeremiah",
	"Lamentations",
	"Ezekiel",
	"Daniel",
	"Hosea",
	"Joel",
	"Amos",
	"Obadiah",
	"Jonah",
	"Micah",
	"Nahum",
	"Habakkuk",
	"Zephaniah",
	"Haggai",
	"Zechariah",
	"Malachi"
];
chapters_per_book = {
	"Genesis": 50,
	"Exodus": 40,
	"Leviticus": 27,
	"Numbers": 36,
	"Deuteronomy": 34,
	"Joshua": 24,
	"Judges": 21,
	"Ruth": 4,
	"1 Samuel": 31,
	"2 Samuel": 24,
	"1 Kings": 22,
	"2 Kings": 25,
	"1 Chronicles": 29,
	"2 Chronicles": 36,
	"Ezra": 10,
	"Nehemiah": 13,
	"Esther": 10,
	"Job": 42,
	"Psalms": 150,
	"Proverbs": 31,
	"Ecclesiastes": 12,
	"Song of Solomon": 8,
	"Isaiah": 66,
	"Jeremiah": 52,
	"Lamentations": 5,
	"Ezekiel": 48,
	"Daniel": 12,
	"Hosea": 14,
	"Joel": 3,
	"Amos": 9,
	"Obadiah": 1,
	"Jonah": 4,
	"Micah": 7,
	"Nahum": 3,
	"Habakkuk": 3,
	"Zephaniah": 3,
	"Haggai": 2,
	"Zechariah": 14,
	"Malachi": 4
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
		url = v.passage.replace(/(.*)\ (\d+):\d+/, "/$1/$2");
		var $a = $("<a>").attr("href", url).text(v.passage);
		$tr.append($("<td>").append($a));
		$tr.append($("<td>").addClass("hebrew").append(h_text));
		$tr.append($("<td>").append(v.english));
		$table.append($tr);
	});
	return $table;
}

var searchTerms = [];
var searchType = "clause";
$(document).ready(function(){
}).on("click", ".main span", function(){
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
	if (Object.keys(li_data).length === 0)
	{
		alert("You can't add an empty search term. Click on a morphological attribute to define a search term.");
		return false;
	}
	searchTerms.push(li_data);

	$(".termList").append($li);
	return false;
}).on("click", ".termList li", function(){
	$(this).addClass("hidden");
	var $that = $(this);
	setTimeout(function(){
		searchTerms.splice($that.index(), 1);
		$that.remove();
	}, 1000);
}).on("click", ".doSearch", function(){
	if (searchTerms.length === 0)
	{
		alert("You need search terms before you can search smarty pants...");
	}
	else
	{
		dataToSend = {
			"query": searchTerms,
			"search_type": searchType
		};
		$.ajax({
			method: "POST",
			url: "/api/search",
			data: JSON.stringify(dataToSend)
		})
		.done(function( msg ) {
			$result_div = $("<div>").addClass("results").css({"opacity": 0}).text(msg.length + " results");
			$result_div.append(searchResultsToTable(msg)).appendTo("body");
			$result_div.animate({"opacity": 1});
			$(".doSearch").removeClass("busy");
		})
		.fail(function(msg){
			alert("Hmm, something went wrong with that search. Sorry about that... Try refreshing the page.");
			$(".doSearch").removeClass("busy");
		});
		$(".doSearch").addClass("busy");
	}
}).on("click", ".results, .modal_container", function(){
	$(this).animate({"opacity": 0}, function(){
		$(this).remove();
	});
}).on("click", ".search_type_combo .options a", function(){
	searchType = $(this).text();
	$(".search_type_combo .selected_search_type").text(searchType);
}).on("click", "nav .main_ref", function(){
	var $div = $("<div>").addClass("modal_container");
	ot_books.forEach(function(bk){
		$div.append($("<a href=#>").addClass("book_link").text(bk));
	});
	$("body").append($div);
}).on("click", ".book_link", function(){
	var book_choice = $(this).text();
	var $div = $(".modal_container").empty();
	for (var i = 0; i < chapters_per_book[book_choice]; i++)
	{
		$div.append($("<a href=#>").data("url", "/" + book_choice + "/" + (i + 1)).addClass("chapter_link").text(i+1));
	}
	return false;
}).on("click", "nav .chapter, .chapter_link", function(){
	window.location.href = $(this).data("url");
});
