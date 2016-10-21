var WordBit = React.createClass({
	onClickHandler: function(e) {
		this.props.updateSelectedWordBit(this.props.wordbit.wid)
	},
	render: function() {
		var trailer_to_use = this.props.wordbit.trailer.replace("\n", "  ");
		return (
			<span>
				<span className="word_bit" onClick={this.onClickHandler}>
					{this.props.wordbit.bit}
				</span>
				<span className="word_trailer">
					{trailer_to_use}
				</span>
			</span>
		);
	}
});
var WholeWord = React.createClass({
	render: function() {
		var wordBitElements = this.props.word_bits.map(function(bit, i) {
			if (bit.wid === "verse")
			{
				return <span key={i} className="verse_number">{bit.verse}</span>;
			}
			else
			{
				return <WordBit key={i} wordbit={bit} updateSelectedWordBit={this.props.updateSelectedWordBit} />;
			}
		}, this);
		return (
			<span className="whole_word">
				{wordBitElements}
			</span>
		);
	}
});
var BibleText = React.createClass({
	handleWordBitSelected: function(wid) {
		this.props.updateSelectedWordBit(wid)
	},
	render: function() {
		var lastVerse = 0;
		var words = this.props.data.reduce(function(previousValue, currentValue, i) {
			// intersperse words with verse references
			var toReturn = previousValue;
			if (currentValue.verse !== lastVerse)
			{
				// the last element should be empty
				toReturn[toReturn.length-1].push({"wid": "verse", "verse": currentValue.verse});
				lastVerse = currentValue.verse;
			}

			toReturn[toReturn.length-1].push(currentValue);
			if (currentValue.trailer.includes(" ") || currentValue.trailer.includes("\n"))
			{
				toReturn.push([]);
			}
			return toReturn;
		}, [[]]).filter(function(el){return el.length > 0});
		var wordElements = words.map(function(word, i) {
			return <WholeWord key={i} word_bits={word} updateSelectedWordBit={this.handleWordBitSelected} />;
		}, this);
		return (
			<div className={this.props.isLoading ? "bible_text is_loading" : "bible_text"}>
				{wordElements}
			</div>
		);
	}
});


var AbstractSelector = React.createClass({
	render: function() {
		var columns = Math.round(Math.sqrt(this.props.list.length));
		var grid = this.props.list.reduce(function(previousValue, currentValue, i){
			var returnValue = previousValue;
			if (i % columns === 0)
				returnValue.push([]);
			returnValue[returnValue.length-1].push(currentValue);
			return returnValue;
		}, []);
		return (
			<div className="abstract_selector">
				{grid.map(function(item, i){
					return (
						<div key={i} className="table_row">
							{item.map(function(item_i, j){
								return <div key={j} className="table_cell" onClick={() => this.props.onSelection(item_i)}>{item_i}</div>;
							}, this)}
						</div>
					)
				}, this)}
			</div>
		);
	}
});
var ChapterSelector = React.createClass({
	render: function() {
		return (
			<AbstractSelector list={[...Array(this.props.chapters).keys()].map((i) => i+1)}
				onSelection={this.props.onSelection} />
		);
	}
});
var BookSelector = React.createClass({
	render: function() {
		return (
			<AbstractSelector list={this.props.books}
				onSelection={this.props.onSelection} />
		);
	}
});

var BibleReference = React.createClass({
	render: function() {
		return (
			<div className="bible_reference">
				<div className="chapter_nav" onClick={() => this.props.moveChapterHandler(-1)}>«</div>
				<div className="book_nav" onClick={this.props.referenceSelectionHandler}>{this.props.reference}</div>
				<div className="chapter_nav" onClick={() => this.props.moveChapterHandler(+1)}>»</div>
			</div>
		);
	}
});

var SearchTerm = React.createClass({
	render: function() {
		var lexeme = this.props.data.hasOwnProperty("lex_utf8") ? this.props.data.lex_utf8.replace(/[\/\[=]/g,"") :
			(this.props.data.hasOwnProperty("tricons") ? this.props.data.tricons : "ANY");
		var png_prop = {
			"nu": {
				"sg": "s",
				"du": "d",
				"pl": "p",
				"unknown": "-",
				"NA": "-"
			},
			"gn": {
				"m": "m",
				"f": "f",
				"unknown": "-",
				"NA": "-"
			},
			"ps": {
				"p1": "1",
				"p2": "2",
				"p3": "3",
				"unknown": "-",
				"NA": "-"
			}
		}
		var png = typeof this.props.data.ps !== "undefined" ? (png_prop.ps[this.props.data.ps]) : "-";
		png = png + (typeof this.props.data.gn !== "undefined" ? (png_prop.gn[this.props.data.gn]) : "-");
		png = png + (typeof this.props.data.nu !== "undefined" ? (png_prop.nu[this.props.data.nu]) : "-");

		var stem = this.props.data.hasOwnProperty("vs") ?
			<span className="stem">{this.props.data.vs}</span> : "";
		var tense = this.props.data.hasOwnProperty("vt") ?
			<span className="stem">{this.props.data.vt}</span> : "";
		png = png !== "---" ?
			<span className="png">{png}</span> : "";

		return (
				<div className="search_term" onClick={() => this.props.onClickHandler(this.props.index)}>
					<heading>
						{lexeme}
					</heading>
					<p>
						{stem}{tense}{png}
					</p>
				</div>
		);
	}
});
var SettingsListItem = React.createClass({
	render: function() {
		return (
			<li onClick={() => this.props.onClickHandler(this.props.value)} className={this.props.isSelected ? "active" : ""}>
				{this.props.value}
			</li>
		);
	}
});
var SearchSettingsMenu = React.createClass({
	render: function() {
		var optionElements = this.props.data.option_list.map(function(value, i){
			return (
				<SettingsListItem key={i} isSelected={value == this.props.data.selected_value} value={value} onClickHandler={this.props.onClickHandler} />
			)
		}, this);
		return (
			<ul className="search_settings_menu">
				{optionElements}
			</ul>
		);
	}
});
var SearchSettings = React.createClass({
	render: function() {
		return (
			<div className="search_settings">
				<div className="search_settings_button">
					<SearchSettingsMenu data={this.props.menu_settings} onClickHandler={this.props.setSearchType} />
				</div>
			</div>
		);
	}
});
var SearchBuilder = React.createClass({
	render: function() {
		var searchTermElements = this.props.data.map(function(value, i){
			return <SearchTerm key={i} data={value} index={i} onClickHandler={this.props.searchTermClickHandler} />;
		}, this);
		return (
			<div className="search_builder">
				{searchTermElements}
				<div className={this.props.menu_settings.in_progress ? "do_search in-progress" : "do_search"} onClick={this.props.performSearch}></div>
				<SearchSettings setSearchType={this.props.setSearchType} menu_settings={this.props.menu_settings} />
				<BibleReference referenceSelectionHandler={this.props.referenceSelectionHandler} reference={this.props.currentReference} moveChapterHandler={this.props.moveChapterHandler} />
				<div className="spacer"></div>
			</div>
		);
	}
});


var MorphDisplay = React.createClass({
	addSearchTermClickHandler: function(e) {
		var term = this.props.data.reduce(function(previousValue, currentValue) {
			if (currentValue.selected)
				previousValue[currentValue.k] = currentValue.v;
			return previousValue;
		}, {});
		this.props.addSearchTerm(term);
	},
	render: function() {
		var term_to_english = {
			"categories": {
				"lex_utf8": "Sense Lexeme",
				"tricons": "Consonantal Root",
				"g_prs_utf8": "Pronominal Suffix",
				"is_definite": "Definite",
				"has_suffix": "Has Pron. Suffix",
				"g_uvf_utf8": "Univalent Final",
				"sp": "Part of Speech",
				"ps": "Person",
				"nu": "Number",
				"gn": "Gender",
				"vt": "Tense",
				"vs": "Stem",
				"st": "State",
				"gloss": "Gloss"
			},
			"is_definite": {
				"det": "Yes",
				"und": "No"
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
		return (
			<div className="morph_displayer">
				<table>
					<tbody>
						{this.props.data.map(function(morph, i){
							var kv_key = term_to_english["categories"][morph.k];
							var kv_value = term_to_english.hasOwnProperty(morph.k) ? term_to_english[morph.k][morph.v] : morph.v;
							return <tr key={i} className={morph.selected ? "active" : ""} onClick={() => this.props.onClickHandler(morph.k)}><td>{kv_key}</td><td>{kv_value}</td></tr>;
						}, this)}
					</tbody>
				</table>
				{this.props.data.reduce(function(p, c) { return p |= c.selected }, false) ?
					<div className="add_search_term" onClick={this.addSearchTermClickHandler}>add search term</div> : ""}
			</div>
		);
	}
});

var Modal = React.createClass({
	render: function() {
		return (
			<div className={this.props.isVisible ? "modal" : "modal hidden"} onClick={this.props.onClickHandler}>
				{this.props.children}
			</div>
		);
	}
});
var TabulatedResults = React.createClass({
	render: function() {
		return (
			<div>
				<div className="results_tally">{this.props.data.length} results</div>
				<table className="results_table">
					<tbody>
						{this.props.data.map(function(row, i){
							// var h_text = row.hebrew.replace(row.clause, "<span class='highlight_clause'>" + row.clause + "</span>");
							var url = row.passage.replace(/(.*)\ (\d+):\d+/, "/$1/$2");
							return (
								<tr key={i}>
									<td className="reference"><a href={url}>{row.passage}</a></td>
									<td className="hebrew">{row.clause.map((words, i) => {
											return (
												<span key={i} className={words.significance}>{words.text}</span>
											);
										})}</td>
									<td className="english" dangerouslySetInnerHTML={{__html: row.english}} />
								</tr>
							)
						}, this)}
					</tbody>
				</table>
			</div>
		);
	}
});


var App = React.createClass({
	getInitialState: function() {
		var ref = "/Genesis/1";
		if (localStorage.getItem('reference'))
			ref = localStorage.getItem('reference');
		if (location.pathname.replace("/", "").length > 0)
			ref = location.pathname;
		var ref_array = ref.replace(/^\//, "").split("/");
		var ref_obj = {
			"book": ref_array[0],
			"chapter": Number.isInteger(+ref_array[1]) ? +ref_array[1] : 1
		};

		return {
			"maindata": [],
			"isLoading": false,
			"morphData": [],
			"searchTerms": [],
			"searchResults": [],
			"menuSettings": {
				"in_progress": false,
				"selected_value": "clause",
				"option_list": ["phrase","clause","sentence","verse"]
			},
			"bookSelectionMode": false,
			"chapterSelectionMode": false,
			"bookNames": this.getOTBooksDetails().map(function(x) {return x.name;}),
			"bookSelection": "Genesis",
			"reference": ref_obj
		};
	},
	getOTBooksDetails: function() {
		return [
			{"name": "Genesis", "chapters": 50, "abbreviation": "Gen"},
			{"name": "Exodus", "chapters": 40, "abbreviation": "Ex"},
			{"name": "Leviticus", "chapters": 27, "abbreviation": "Lev"},
			{"name": "Numbers", "chapters": 36, "abbreviation": "Num"},
			{"name": "Deuteronomy", "chapters": 34, "abbreviation": "Deut"},
			{"name": "Joshua", "chapters": 24, "abbreviation": "Josh"},
			{"name": "Judges", "chapters": 21, "abbreviation": "Judg"},
			{"name": "Ruth", "chapters": 4, "abbreviation": "Ruth"},
			{"name": "1 Samuel", "chapters": 31, "abbreviation": "1 Sam"},
			{"name": "2 Samuel", "chapters": 24, "abbreviation": "2 Sam"},
			{"name": "1 Kings", "chapters": 22, "abbreviation": "1 Kgs"},
			{"name": "2 Kings", "chapters": 25, "abbreviation": "2 Kgs"},
			{"name": "1 Chronicles", "chapters": 29, "abbreviation": "1 Chron"},
			{"name": "2 Chronicles", "chapters": 36, "abbreviation": "2 Chron"},
			{"name": "Ezra", "chapters": 10, "abbreviation": "Ezra"},
			{"name": "Nehemiah", "chapters": 13, "abbreviation": "Neh"},
			{"name": "Esther", "chapters": 10, "abbreviation": "Est"},
			{"name": "Job", "chapters": 42, "abbreviation": "Job"},
			{"name": "Psalms", "chapters": 150, "abbreviation": "Ps"},
			{"name": "Proverbs", "chapters": 31, "abbreviation": "Prov"},
			{"name": "Ecclesiastes", "chapters": 12, "abbreviation": "Eccl"},
			{"name": "Song of Solomon", "chapters": 8, "abbreviation": "Songs"},
			{"name": "Isaiah", "chapters": 66, "abbreviation": "Isa"},
			{"name": "Jeremiah", "chapters": 52, "abbreviation": "Jer"},
			{"name": "Lamentations", "chapters": 5, "abbreviation": "Lam"},
			{"name": "Ezekiel", "chapters": 48, "abbreviation": "Ez"},
			{"name": "Daniel", "chapters": 12, "abbreviation": "Dan"},
			{"name": "Hosea", "chapters": 14, "abbreviation": "Hos"},
			{"name": "Joel", "chapters": 3, "abbreviation": "Joel"},
			{"name": "Amos", "chapters": 9, "abbreviation": "Amos"},
			{"name": "Obadiah", "chapters": 1, "abbreviation": "Ob"},
			{"name": "Jonah", "chapters": 4, "abbreviation": "Jon"},
			{"name": "Micah", "chapters": 7, "abbreviation": "Mic"},
			{"name": "Nahum", "chapters": 3, "abbreviation": "Nah"},
			{"name": "Habakkuk", "chapters": 3, "abbreviation": "Hab"},
			{"name": "Zephaniah", "chapters": 3, "abbreviation": "Zeph"},
			{"name": "Haggai", "chapters": 2, "abbreviation": "Hag"},
			{"name": "Zechariah", "chapters": 14, "abbreviation": "Zech"},
			{"name": "Malachi", "chapters": 4, "abbreviation": "Mal"}
		];
	},
	componentDidMount: function() {
		var source_url = "/" + this.state.reference.book + "/" + this.state.reference.chapter;
		this.loadChapter(source_url);
	},
	componentWillUpdate: function(nextProps, nextState){
		if (nextState.reference.book == this.state.reference.book &&
			nextState.reference.chapter == this.state.reference.chapter)
			return;
		var source_url = "/" + nextState.reference.book + "/" + nextState.reference.chapter;
		this.loadChapter(source_url);
	},
	loadChapter: function(source_url) {
		localStorage.setItem("reference", source_url);
		this.setState({"isLoading": true});
		this.serverRequest = $.post(source_url, function (result) {
			this.setState({"maindata": result});
			this.setState({"isLoading": false});
		}.bind(this));
	},
	updateMorphData: function(wid) {
		this.serverRequest = $.get(this.props.morph_api_url + "/" + wid, function (result) {
			var morph_data = Object.keys(result).map(function(key, i){
				return {
					"selected": false,
					"k": key,
					"v": result[key]
				};
			});
			this.setState({
				"morphData": morph_data
			});
		}.bind(this));
	},
	toggleMorphSelection: function(key) {
		var morph_state = this.state.morphData;
		var index = morph_state.map(function(md) {return md.k; }).indexOf(key);
		morph_state[index].selected = !morph_state[index].selected;
		this.setState({"morphData": morph_state});
	},
	addSearchTerm: function(term) {
		var search_terms = this.state.searchTerms;
		search_terms.push(term);
		this.setState(search_terms);
		Object.keys(term).forEach(function(tkey){
			this.toggleMorphSelection(tkey);
		}, this);
	},
	removeSearchTerm: function(index) {
		var newSearchTerms = this.state.searchTerms.slice();
		newSearchTerms.splice(index, 1);
		this.setState({"searchTerms": newSearchTerms});
	},
	setSearchType: function(newType) {
		var menu_settings = jQuery.extend(true, {}, this.state.menuSettings);
		menu_settings.selected_value = newType;
		this.setState({"menuSettings": menu_settings});
	},
	setSearchInProgress: function(inProgress) {
		var menu_settings = jQuery.extend(true, {}, this.state.menuSettings);
		menu_settings.in_progress = inProgress;
		this.setState({"menuSettings": menu_settings});
	},
	performSearch: function() {
		if (this.state.searchTerms.length === 0)
		{
			alert("You cannot search without any search terms. Try clicking on a word and then selecting morphological data to create a search term.");
			return;
		}
		this.setSearchInProgress(true);
		var dataToSend = {
			"query": this.state.searchTerms,
			"search_type": this.state.menuSettings.selected_value
		};
		var context = this;
		$.ajax({
			method: "POST",
			url: this.props.search_url,
			data: JSON.stringify(dataToSend)
		})
		.done(function(data) {
			if (data.length === 0)
			{
				alert("Your search did not yield any results");
			}
			else
			{
				context.setState({"searchResults": data})
			}
			context.setSearchInProgress(false);
		})
		.fail(function(msg){
			alert("Hmm, something went wrong with that search. Sorry about that... Try refreshing the page.");
			context.setSearchInProgress(false);
		});
	},
	clearResults: function() {
		this.setState({"searchResults": []});
	},
	changeMode: function(mode_type, is_on) {
		var newState = {};
		newState[mode_type] = is_on;
		this.setState(newState);
	},
	referenceSelectionHandler: function() {
		this.changeMode("bookSelectionMode", true)
	},
	moveChapterHandler: function(direction) {
		var referenceArray = this.getOTBooksDetails().reduce(function(previousValue, currentValue){
			var newReferences = [...Array(currentValue.chapters).keys()].map((i) => ({ "book": currentValue.name, "chapter": i+1}));
			return previousValue.concat(newReferences)
		},[]);
		var curr_ref = this.state.reference;
		var index = referenceArray.findIndex((item) => item.chapter == curr_ref.chapter && item.book == curr_ref.book);
		var newIndex = index + direction;
		newIndex = newIndex >= 0 ? newIndex : referenceArray.length - 1;
		newIndex = newIndex < referenceArray.length ? newIndex : 0;
		this.setState({"reference": referenceArray[newIndex]});
	},
	bookSelectionHandler: function(book) {
		var index = this.getOTBooksDetails().map(function(obj) { return obj.name; }).indexOf(book);
		var chapter_count = this.getOTBooksDetails()[index].chapters;
		this.setState({"bookSelection": book});
		this.setState({"chapterSelection": chapter_count})
		this.changeMode("chapterSelectionMode", true);
		this.changeMode("bookSelectionMode", false);
	},
	chapterSelectionHandler: function(chapter) {
		this.setState({"reference": {
			"book": this.state.bookSelection,
			"chapter": chapter
		}});
		this.changeMode("chapterSelectionMode", false);
	},
	render: function() {
		return (
			<div>
				<SearchBuilder data={this.state.searchTerms}
					searchTermClickHandler={this.removeSearchTerm}
					setSearchType={this.setSearchType}
					menu_settings={this.state.menuSettings}
					performSearch={this.performSearch}
					moveChapterHandler={this.moveChapterHandler}
					referenceSelectionHandler={this.referenceSelectionHandler}
					currentReference={this.state.reference.book + " " + this.state.reference.chapter} />

				<div className="bible_text_container">
					<BibleText data={this.state.maindata}
						updateSelectedWordBit={this.updateMorphData}
						isLoading={this.state.isLoading} />
				</div>

				 <MorphDisplay data={this.state.morphData}
					onClickHandler={this.toggleMorphSelection}
					addSearchTerm={this.addSearchTerm} />

				<Modal isVisible={this.state.searchResults.length > 0}
					onClickHandler={this.clearResults}>
					<TabulatedResults data={this.state.searchResults} />
				</Modal>

				<Modal isVisible={this.state.bookSelectionMode}
					onClickHandler={() => this.changeMode("bookSelectionMode", false)}>
					<BookSelector onSelection={this.bookSelectionHandler}
						books={this.state.bookNames} />
				</Modal>

				<Modal isVisible={this.state.chapterSelectionMode}
					onClickHandler={() => this.changeMode("chapterSelectionMode", false)}>
					<ChapterSelector onSelection={this.chapterSelectionHandler}
						chapters={this.state.chapterSelection} />
				</Modal>
			</div>
		);
	}
});

ReactDOM.render(
	<App root_url="http://localhost:8080/" morph_api_url="/api/word_data" search_url="/api/search" />,
	document.getElementById('app')
);
