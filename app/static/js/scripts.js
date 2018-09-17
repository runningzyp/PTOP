
jQuery(document).ready(function() {
	
    /*
        Fullscreen background
    */
    $.backstretch("static/img/backgrounds/background.png");
    
    /*
	    Modals
	*/
	$('.launch-modal').on('click', function(e){
		
/* 		e.preventDefault();防止默认行为  默认打开链接 可有可无*/	
	$( '#' + $(this).data('modal-id') ).modal();
	
	});

	$('#modal-login').on('shown.bs.modal', function () {		
		$('#one').focus();
	});
	$('#modal-login').on('hide.bs.modal', function () {		
		$('#form')[0].reset()
	})
		


	/* 自动补全表单和提交功能 */
	
		var inputLength = $('input').length;
		//$('input').keyup(function(){})
		//使用jQuery事件代理的事件绑定方式，不需要对每个input进行事件绑定，有利于性能优化
		$('#form').delegate('input', 'keyup', function() {
			var _this = $(this),
				valLength = _this.val().length,
				index = _this.index();
			if (valLength > 0) {
				if ((index + 1) > inputLength) return false; //输入完成时进行操作
				_this.attr('data-in', 'true').next().focus().select();
			} else if (valLength == 0 && _this.attr('data-in') == 'true') {
				
				if (index == 0) return false; //删除所有时进行操作				
				_this.attr('data-in', 'false').prev().focus().select();
				
			}
		});

		/* $('input').change(function(){
				var f=$('#form');
				var str =f.one.value+f.two.value+f.three.value+
								 f.four.value+f.five.value+f.six.value;   
				if(str.length==6){
					$('#ID').value = str;
					  f.submit();
					  alert('hello');
				}
		}); */

		
         


	
   
    /*
        Form validation
    */
    $('.registration-form input[type="text"], .registration-form textarea').on('focus', function() {
    	$(this).removeClass('input-error');
    });
    
    $('.registration-form').on('submit', function(e) {
    	
    	$(this).find('input[type="text"], textarea').each(function(){
    		if( $(this).val() == "" ) {
    			e.preventDefault();
    			$(this).addClass('input-error');
    		}
    		else {
    			$(this).removeClass('input-error');
    		}
    	});
    });
    
    
});
