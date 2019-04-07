var Books = (function () {

	var $books = $('#bk-list > li > div.bk-book'),
		booksCount = $books.length;

	function init() {

		$books.each(function () {

			var $book = $(this),
				$other = $books.not($book),
				$parent = $book.parent(),
				$page = $book.children('div.bk-page'),
				$bookview = $parent.find('button.bk-bookview'),
				$content = $page.children('div.bk-content'),
				current = 0;

			$parent.find('button.bk-bookback').on('click', function () {

				$bookview.removeClass('bk-active');

				if ($book.data('flip')) {

					$book.data({
						opened: false,
						flip: false
					}).removeClass('bk-viewback').addClass('bk-bookdefault');

				} else {

					$book.data({
						opened: false,
						flip: true
					}).removeClass('bk-viewinside bk-bookdefault').addClass('bk-viewback');

				}

			});

			$bookview.on('click', function () {

				var $this = $(this);

				$other.data('opened', false).removeClass('bk-viewinside').parent().css('z-index', 0).find('button.bk-bookview').removeClass('bk-active');
				if (!$other.hasClass('bk-viewback')) {
					$other.addClass('bk-bookdefault');
				}

				if ($book.data('opened')) {
					$this.removeClass('bk-active');
					$book.data({
						opened: false,
						flip: false
					}).removeClass('bk-viewinside').addClass('bk-bookdefault');
				} else {
					$this.addClass('bk-active');
					$book.data({
						opened: true,
						flip: false
					}).removeClass('bk-viewback bk-bookdefault').addClass('bk-viewinside');
					$parent.css('z-index', booksCount);
					current = 0;
					$content.removeClass('bk-content-current').eq(current).addClass('bk-content-current');
				}

			});

			if (1) {

				var $navPrev = $('<span class="bk-page-prev">上一页</span>'),
					$navNext = $('<span class="bk-page-next">下一页</span>');
					
				$page.append($('<nav></nav>').append($navPrev, $navNext));
				
				
				// alert($("#"+article_type).html())
				// alert($("#"+article_type).children().children().html())
				$navPrev.on('click', function () {
					
					 var $this = $(this);
					 var article_type = $this.parent().prev().attr("id");
					 var page = gl_current_page[article_type];
					//  alert(page);
					 var title = $this.parent().prev(".bk-content").find(".title")
					 var content = $this.parent().prev(".bk-content").find(".content")
					 var data={"page":page-1, "article_type":article_type};
					if (page >1) {
						gl_current_page[article_type]--;
						$.ajax({
							url: $SCRIPT_ROOT + '/blogs',
							type: "POST",
							data: JSON.stringify({
								"page":page-1,
								"article_type": article_type,
							}),
							async: true,
							cache: false,
							contentType:"application/json",
							dataType: "json",
							// processData:false,
							success:function (data) {
                                var str="/blog/"+data.article.id;
                                title.find("a").attr('href', str);
								title.find("p").text(data.article.title);
								content.html(data.article.body_html);
						　　}, 
						　　error: function (data) { 
							　　　　　alert('error');
						　　}							
						});
						//post 方法已经弃用
						// $.post(
						// 	$SCRIPT_ROOT + '/blogs', {
						// 		page: page-1, 
						// 		article_type: article_type
						// 	},
						// 	function (data, status) {
						// 		if (status == 'success') {
						// 			title.text(data.article.id);
						// 			content.text(data.article.title)
						// 		} else {
						// 			alert('error');
						// 		}
						// 	});
					} else {
						alert('第一页')
					}

					return false;
				});

				$navNext.on('click', function () {
					var $this = $(this);
					var article_type = $this.parent().prev().attr("id");
					var total_page = gl_total_page[article_type];
				
				
					var page = gl_current_page[article_type];
					var title = $this.parent().prev(".bk-content").find(".title")
					var content = $this.parent().prev(".bk-content").find(".content")
					if (page < total_page) {
						gl_current_page[article_type]++;

						$.ajax({
							url: $SCRIPT_ROOT + '/blogs',
							type: "POST",
							data: JSON.stringify({
								"page":page+1,
								"article_type": article_type,
							}),
							async: true,
							cache: false,
							contentType:"application/json",
							dataType: "json",
							// processData:false,
							success:function (data) {
                                var str="/blog/"+data.article.id;
                                title.find("a").attr('href', str);
								title.find("p").text(data.article.title);
                                content.html(data.article.body_html)
                                alert(data.article.body_html)
						　　}, 
						　　error: function (data) { 
							　　　　　alert('error');
						　　}							
						});

						// post 方法已经弃用
						// $.post(
						// 	$SCRIPT_ROOT + '/blogs', {
						// 		page: page+1,
						// 		article_type: article_type
						// 	},
						// 	function (data, status) {
						// 		if (status == 'success') {
						// 			title.text(data.article.id);
						// 			content.text(data.article.title)
						// 		} else {
						// 			alert('error');
						// 		}
						// 	});
					} else {
						alert('最后一页')
					}
					return false;
				});

			
			
			}

		});

	}

	return {
		init: init
	};

})();