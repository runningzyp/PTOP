layui.use('element', function () {
    var element = layui.element;

});


function createTime(v){
    var date = new Date(v);
    var y = date.getFullYear();
    var m = date.getMonth()+1;
    m = m<10?'0'+m:m;
    var d = date.getDate();
    d = d<10?("0"+d):d;
    var h = date.getHours();
    h = h<10?("0"+h):h;
    var M = date.getMinutes();
    M = M<10?("0"+M):M;
    var str = y+"-"+m+"-"+d+" "+h+":"+M;
    return str;
}



layui.use('table', function(){
    var table = layui.table;
   
    
    //第一个实例
    table.render({
        elem: '#demo'
        // ,height: 312
        ,url: $SCRIPT_ROOT+'admin/get-blogs'//数据接口
        ,method: 'post'
        ,contentType: 'application/json'
        ,page: true //开启分页
        ,toolbar: true
        ,loading:true //加载条
        ,id:'testReload'
        ,even: true //开启隔行背景
        ,toolbar: '#barDemo'
        ,cols: [[ //表头
            {type:'checkbox'}
            // ,{field:'zizeng', width:80, title: '序号',sort:true,templet:'#zizeng'}
            ,{field:'zizeng', width:80, title: '序号',type:'numbers'}
            ,{field: 'id', title: '文章序号', hide: true,width:80}
            ,{field: 'title', title: '标题',}
            ,{field: 'finish_time', title: '完成时间', width:'20%',
                    templet :function (row){
                        return createTime(row.finish_time);
                        }}
            ,{field: 'last_change_time', title: '修改时间', width:'20%',
                    templet :function (row){
                            return createTime(row.last_change_time);
                        }}
            // ,{field: 'type_id', title: '类型号', width:80}
            ,{field: 'type_name', title: '类型', width:140}
            ,{field:'right', title: '操作', width:177,toolbar: '#barDemo'}
            ]]
        ,request: {
        pageName: 'page' //页码的参数名称，默认：page
        ,limitName: 'limit' //每页数据量的参数名，默认：limit
        }
        ,response: {
            statusName: 'status' //数据状态的字段名称，默认：code
            ,statusCode: 200 //成功的状态码，默认：0
            ,msgName: 'msg' //状态信息的字段名称，默认：msg
            ,countName: 'count' //数据总数的字段名称，默认：count
            ,dataName: 'data' //数据列表的字段名称，默认：data
        }

        ,parseData: function(res){ //res 即为原始返回的数据
            return {
            "status": res.status, //解析接口状态
            "msg": res.message, //解析提示文本
            "count": res.count, //解析数据长度
            "data": res.data //解析数据列表
            };
        }
        });
         /* 第一个实例结束 */

         
            //监听工具条
            table.on('tool(test)', function(obj){ //注：tool是工具条事件名，test是table原始容器的属性 lay-filter="对应的值"
            var data = obj.data; //获得当前行数据
            var layEvent = obj.event; //获得 lay-event 对应的值（也可以是表头的 event 参数对应的值）
            var tr = obj.tr; //获得当前行 tr 的DOM对象

                if(layEvent === 'del'){ //删除
                    layer.confirm('真的删除行么', function(index){
                        //向服务端发送删除指令
                        $.ajax({
                            type: "POST",
                            url: $SCRIPT_ROOT+'admin/delete-blog',
                            data: JSON.stringify({
                                "id":data['id'],
                            }),
                            dataType: "json",
                            contentType:"application/json",
                            success: function (response) {
                                if (response.status ==200){
                                     obj.del(); //删除对应行（tr）的DOM结构，并更新缓存
                                     layer.close(index);
                                     layer.msg(response.message,{time:5000})
                                }
                            }
                        });
                    });
                }else if(layEvent === 'edit'){ //编辑
                    layer.confirm('确定编辑吗?', function(index){
                        window.location.href = ("../admin/update-blog/"+data['id']);
                    });
                }
            });
      

});