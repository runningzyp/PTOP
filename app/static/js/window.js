$(document).ready(function () {
    $('.window-show').scrollTop( $('.window-show')[0].scrollHeight );
    $(".foot-second").click(function () {
        $(".window-hidden").css("display", "block");
        $(".move").animate({
            bottom: '150px'
        });
    });

    $(".window-show").click(function (e) {
        var target = $(e.target);
        if (!target.is('.foot-second')) {
            $(".move").animate({
                bottom: '0px'
            });
        }
    })
});


$(document).ready(function () {
    get_token();
});
function get_token() {
        $.ajax({
        url: $SCRIPT_ROOT+"/get-token",
        type: "POST",
        dataType: "json", //json 还是jsonp看情况
        timeout: 2000,
        async: true,
        cache: false,
        contentType: "false",
        processData: false,
        success:function(returndata){
            ajaxToken= returndata;
          
        }
    });
}

$('#text-submit').click(function() {  // 等于按钮
    if ($('#text').val()==''){
        alert('none');
    }else{
    $.getJSON($SCRIPT_ROOT + '/_sendmessage', {
    text: $('#text').val(),
    device_type: 'web'
    }, function(data) {
        alert(data.result);
        $("input[name='text']").val("").focus();
        $(".window-show").append($add_text);
        $(".window-hide-line").show(1000);
        $('.window-show').scrollTop( $('.window-show')[0].scrollHeight );
    });
    }
    $add_text ='<div class="window-hide-line">'+
            '<div class="row clearfix">'+
                '<div class="col-md-1 col-xs-2 column" style="padding-left:15px;padding-right: 0;">'+
                    "<a href='{{url_for('.user',username=current_user.username)}}'>"+
                        "<img class='profile-thumbnail img-responsive' src='{{ url_for('static', filename='ico/web.png') }}'>"+
                    '</a>'+
                '</div>'+

                '<div class="col-md-7 col-xs-8 column" style="padding-left:0px;">'+

                    '<div class="window-show-data">'+
                            '<div>' + $('#text').val() +'</div>'+
                    '</div>'+

                '</div>'+
                '<div class="col-md-3 column">'+
                '</div>'+
                '<div class="col-md-1 column">'+
                '</div>'+
            '</div>'+
        '</div>';

});


$('#file-submit').click(function () {

    var file = document.getElementById("file");
    var current_time = Date.parse(new Date()); //获取当前时间
    current_time /= 1000; // gmt 时间精确到秒即可

    if (current_time > ajaxToken["expire"]) {
        get_token()
    }
    var dir = ajaxToken['dir']
    var formData = new FormData();
    formData.append('OSSAccessKeyId', ajaxToken['accessid']);
    formData.append('policy', ajaxToken['policy']);
    formData.append('Signature', ajaxToken['signature']);
    formData.append('key', dir + '/' + '[' + current_time + ']' + file.files[0].name); //文件名保存为当前时间戳+文件名
    formData.append('success_action_status', 200); // 指定返回的状态码
    // formData.append('callback', ajaxToken['callback']);
    formData.append("file", file.files[0]); //file 必须是最后一个域
    $.ajax({
        url: ajaxToken['url_prefix'],
        type: 'POST',
        data: formData,
        dataType: "json",

        cache: false,
        processData: false, //不需要进行序列化处理
        async: false, //发送同步请求
        contentType: false,
        success: function (result) {
            add_files(result)
        },
        error: function (result) {
            alert(result)
            alert(result.data)
            alert("上传超时");
        }
    });
});


function add_files(data) {
    var $file_url= data.url;
    var $file_name= data.filename;
    var $add_file ='<div class="window-hide-line">'+
            '<div class="row clearfix">'+
                "<div class='col-md-1 col-xs-2 column' style='padding-left:15px;padding-right: 0;'>"+
                    "<a href='{{url_for('.user',username=current_user.username)}}'>"+
                        "<img class='profile-thumbnail img-responsive' src='{{ url_for('static', filename='ico/web.png') }}'>"+
                    '</a>'+
                '</div>'+

                '<div class="col-md-7 col-xs-8 column" style="padding-left:0px;">'+

                    '<div class="window-show-data">'+
                    '<a href =\"'+  $file_url+  '\"'+ 'target='+'\"'+'_blank'+'\"'+ '>'+ $file_name +'<\/a>'+
                    '</div>'+

                '</div>'+
                '<div class="col-md-3 column">'+
                '</div>'+
                '<div class="col-md-1 column">'+
                '</div>'+
            '</div>'+
        '</div>';

    $(".window-show").append($add_file);
    $(".window-hide-line").show(1000);
    $('.window-show').scrollTop( $('.window-show')[0].scrollHeight );
}
