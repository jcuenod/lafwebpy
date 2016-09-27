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
		<select class="search_type_combo">
			<option value="phrase">phrase</option>
			<option value="clause">clause</option>
			<option value="sentence">sentence</option>
			<option value="verse">verse</option>
			<option value="paragraph">paragraph</option>
		</select>
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
