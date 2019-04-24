class MyUploadAdapter {
    constructor( loader ) {
      // Save Loader instance to update upload progress.
      this.loader = loader;
    }
    upload() {
        return this.loader.file
            .then( uploadedFile => {
                return new Promise( ( resolve, reject ) => {
                const data = new FormData();
                data.append( 'image', uploadedFile );
                data.append('type','image')
    
                axios( {
                    url: $SCRIPT_ROOT+"admin/upload-blog-image",
                    method: 'post',
                    data,
                    headers: {
                        'Content-Type': 'multipart/form-data;'
                    },
                    // withCredentials: false   
                } ).then( response => {
                    if ( response.data.status == '200' ) {
                        alert(response.data.url)
                        resolve( {
                            "default": response.data.url
                        } );
                    } else {
                        reject( response.data.message );
                    }
                } ).catch( response => {
                    reject( 'Upload failed' );
                } );
    
            } );
        } );
    }
    
  
    abort() {
      // Reject promise returned from upload() method.
    }
  }
//   $SCRIPT_ROOT+"admin/upload-blog-image"

     ClassicEditor.create( document.querySelector( '#editor' ), {
            
            placeholder: 'Type the content here!',
            fontFamily: {
                options: [
                    'default',
                    'Ubuntu, Arial, sans-serif',
                    'Ubuntu Mono, Courier New, Courier, monospace'
                ]
            },
            toolbar: {
                viewportTopOffset : 50, 
                items: [
                    'heading',
                    '|',
                    'alignment',                                                 // <--- ADDED
                    'bold',
                    'italic',
                    'underline',
                    'strikethrough',
                    'blockQuote',
                    '|',
                    'fontSize',  
                    'fontColor', 
                    'fontBackgroundColor',
                    'highlight',
                    '|',
                    'code',
                    'subscript',
                    'superscript',
                    '|',
                    'link',
                    'bulletedList',
                    'numberedList',
                    'insertTable',
                    'imageUpload',
                    'mediaEmbed',
                    'undo',
                    'redo',
                    // 'removeFormat', 删除格式 未安装
                   
                ]
             },

            //自定义版本不需要      

            //  ckfinder: {
            //     // Upload the images to the server using the CKFinder QuickUpload command.
            //     uploadUrl: $SCRIPT_ROOT+"admin/upload-blog-image"
            // },           
            image: {
                // You need to configure the image toolbar, too, so it uses the new style buttons.
                toolbar: [   'imageStyle:alignLeft', 'imageStyle:full', 'imageStyle:alignRight','|','imageTextAlternative' ],
                styles: [
                    // This option is equal to a situation where no style is applied.
                    'full',
    
                    // This represents an image aligned to the left.
                    'alignLeft',
    
                    // This represents an image aligned to the right.
                    'alignRight'
                ]
            },
            fontSize: {
                options: [8, 9, 10, 11, 12, 'default', 14, 16, 18, 20, 22, 24, 26, 28, 36, 44, 48, 72],
              },
            heading: {
                options: [
                    { model: 'paragraph', title: 'Paragraph', class: 'ck-heading_paragraph' },
                    { model: 'heading1', view: 'h1', title: 'Heading 1', class: 'ck-heading_heading1' },
                    { model: 'heading2', view: 'h2', title: 'Heading 2', class: 'ck-heading_heading2' },
                    { model: 'heading3', view: 'h3', title: 'Heading 3', class: 'ck-heading_heading3' },
                ]
            },
            
            language: 'zh-cn',
    })
.then( editor => {
    // 加载了适配器
    editor.plugins.get('FileRepository').createUploadAdapter = (loader)=>{
        return new MyUploadAdapter (loader);
    };

    window.editor = editor;
    // const toolbarContainer = document.querySelector( 'layui-footer' );

    // toolbarContainer.appendChild( editor.ui.view.toolbar.element );
} )


