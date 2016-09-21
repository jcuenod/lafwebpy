$(document).on("click", "span", function(){
	$.get("/api/word_data/" + $(this).data("node"), function(data){
		$(".footer div").html(data);
	});
});
