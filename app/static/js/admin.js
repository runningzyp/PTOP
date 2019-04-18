$(document).ready(function () {
    article_total_page = 0;
    $article_current_page = 1;
    user_total_page = 0;
    $user_current_page = 1;
    __init__(); // 初始化函数


    function __init__() {
        getblog(1); // 初始化第一页博客
        getuser(1); // 初始化第一页用户
    }

    // 获取博客
    function getblog(current_page) {
        $.ajax({
            url: $SCRIPT_ROOT + '/admin/get-blog',
            type: "POST",
            data: JSON.stringify({
                "page": current_page,
                // "article_type": article_type,
            }),
            async: true,
            cache: false,
            contentType: "application/json",
            dataType: "json",
            // processData:false,
            success: function (data) {
                article_total_page = data.pages;
                $("#tbarticle").empty();
                for (var i = 0; i < data.article.length; i++) {
                    var txt = "<tr>" +
                        "<td class = 'id'>" + data.article[i].id + "</td>" +
                        "<td>" + data.article[i].title + "</td>" +
                        "<td>" + moment(data.article[i].timestamp).locale('zh-cn').utcOffset(8).format('lll') + "</td>" +
                        "<td>" + data.article[i].article_type + "</td>" +
                        "<td><button type='button' class='btn-my btn-primary'><span class='glyphicon glyphicon-pencil'> 修改</span></button>"+
                        "<button type='button' style='margin-left:10px' class='btn-my btn-danger delete-article'><span class='glyphicon glyphicon-trash'> 删除</span></button></td>"+
                        "</tr>"

                    $("#tbarticle").append(txt);

                }
            },
            error: function (data) {
                alert('error');
            }
        });
    }
    // 删除博客
    $("tbody").on('click',".delete-article",function(){

        var $id = $(this).parents('tr').find('.id').text()
        var $ret =$(this).parents('tr')
       
        $.ajax({
            url: $SCRIPT_ROOT + '/admin/delete-blog',
            type: "POST",
            data: JSON.stringify({
                "id":$id
            }),
            async: true,
            cache: false,
            contentType: "application/json",
            dataType: "json",
            // processData:false,
            success: function (data) {
                if (data.status =='200'){
                    alert(data.message)
                    $ret.remove()
                }
            }
        });
         
    })
    // 获取用户列表
    function getuser(current_page) {
        $.ajax({
            url: $SCRIPT_ROOT + '/admin/get-user',
            type: "POST",
            data: JSON.stringify({
                "page": current_page,
                // "article_type": article_type,
            }),
            async: true,
            cache: false,
            contentType: "application/json",
            dataType: "json",
            // processData:false,
            success: function (data) {
                user_total_page = data.pages;
                $("#tbuser").empty();
                for (var i = 0; i < data.user.length; i++) {
                    var txt = "<tr>" +
                        "<td>" + data.user[i].id + "</td>" +
                        "<td>" + data.user[i].username + "</td>" +
                        "<td>" + data.user[i].userkey + "</td>" +
                        "<td>" + data.user[i].role + "</td>" +
                        "<td><button type='button' style='margin-left:10px' class='btn-my center-block btn-danger'>删除用户</button></td>"+
                        "</tr>"

                    $("#tbuser").append(txt);

                }
            },
            error: function (data) {
                alert('error');
            }
        });
    }


    // 分页显示博客
    $(".pagination-my li").click(function () {
        var $this = $(this);
        if ($this.attr('class') == "prev-page" && $article_current_page > 1) {
            $article_current_page--;
            getblog($article_current_page);
        } else if ($this.attr('class') == "next-page" && $article_current_page < article_total_page) {
            $article_current_page++;
            getblog($article_current_page);
        } else if (!isNaN($this.attr('class'))) {
            $article_current_page = $this.attr('class');
            getblog($article_current_page);
        } else {
            return
        }
    });

    // 分页显示用户
    $(".pagination-my li").click(function () {
        var $this = $(this);
        if ($this.attr('class') == "prev-page" && $user_current_page > 1) {
            $user_current_page--;
            getblog($user_current_page);
        } else if ($this.attr('class') == "next-page" && $user_current_page < user_total_page) {
            $user_current_page++;
            getblog($user_current_page);
        } else if (!isNaN($this.attr('class'))) {
            $user_current_page = $this.attr('class');
            getblog($user_current_page);
        } else {
            return
        }
    });


    // 切换侧边栏功能
    $(".nav-sidebar li").click(function () {
        var $this = $(this);
        var $name = $this.attr('id');
        $(".nav-sidebar li").removeClass('active');
        $this.addClass('active');
        $(".block").removeClass("show");
        $(".block").addClass("hidden");
        $("." + $name).removeClass("hidden");
        $("." + $name).addClass("show");

    });

    //博客编辑器
    $("#write-article").click(function () {

        var BlogEditor;
        $(function () {
            BlogEditor = editormd("blog-editormd", {
                width: $(".write-article").width,
                height: $(".write-article").height,
                syncScrolling: "single",
                emoji: true,
                placeholder: "Enjoy Markdown! coding now...",
                path: "../../static/editormd/lib/",
                //启动本地图片上传功能
                imageUpload: true,
                imageFormats: ["jpg", "jpeg", "gif", "png", "bmp", "webp"],
                imageUploadURL: $SCRIPT_ROOT + "/admin/upload_blog_img",
                onload: function () {
                    //console.log('onload', this);
                    //this.fullscreen();
                    //this.unwatch();
                    //this.watch().fullscreen();
                    //this.width("100%");
                    //this.height(480);
                    //this.resize("100%", 640);
                },
            });
        });
    });



});