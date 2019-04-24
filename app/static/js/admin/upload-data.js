
var upload = layui.upload; //得到 upload 对象
 
//创建一个上传组件
upload.render({
  elem: '#upload'
  ,url: ''
  ,done: function(res, index, upload){ //上传后的回调
  
  } 
  //,accept: 'file' //允许上传的文件类型
  //,size: 50 //最大允许上传的文件大小
  //,……
})