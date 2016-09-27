<!DOCTYPE html>
<html>
<head>
	<meta charset="utf-8" />
	<title>lafwebpy</title>
	<script src="/static/jquery-3.1.0.js"></script>
	<script src="/static/lafwebpy.js"></script>
	<link rel="stylesheet" type="text/css" href="/static/style.css" />
</head>
<body>
	<section class="searchBuilder"><!--
	 --><ul class="termList">
		</ul><!--
	 --><a href="#" class="doSearch" title="search"></a>
		<div class="search_type_combo">
			<div class="selected_search_type">
				clause
			</div>
			<div class="options">
				<a href="#" data-search-type="phrase">phrase</a>
				<a href="#" data-search-type="clause">clause</a>
				<a href="#" data-search-type="sentence">sentence</a>
				<a href="#" data-search-type="verse">verse</a>
				<a href="#" data-search-type="paragraph">paragraph</a>
			</div>
		</div>
	</section>
	<nav class="ref_selector">
		<div class="chapter" data-url="{{content["prev_chapter"]}}">«</div>
		<div class="main_ref">{{content["reference"]}}</div>
		<div class="chapter" data-url="{{content["next_chapter"]}}">»</div>
	</nav>
	<section class="main">
		{{!content["chapter_text"]}}
	</section>
	<section class="footer">
		<div></div>
	</section>
</body>
</html>
