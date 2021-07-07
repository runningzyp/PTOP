 
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
                    url: $SCRIPT_ROOT+"/admin/upload-blog-image",
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

ClassicEditor
.create(document.querySelector('#editor'),{
    
    toolbar: {
        viewportTopOffset : 50,    
        items: ["heading",  "|", "bold", "italic", "underline", "strikethrough", "highlight", "|", "alignment", "|", "numberedList", "bulletedList", "|", "link","pre","code", "blockquote", "imageUpload", "insertTable", "mediaEmbed", "|", "undo", "redo"]
    },
    image: {
    // You need to configure the image toolbar, too, so it uses the new style buttons.
    toolbar: [ 'imageTextAlternative' ],
    styles: [
        // This option is equal to a situation where no style is applied.
        'full',

            // This represents an image aligned to the left.
            'alignLeft',

            // This represents an image aligned to the right.
            'alignRight'
        ]
 },

 language: 'zh-cn',

})
.then( editor => {
    
      const toolbarContainer = document.querySelector('#ck-toolbar');

         toolbarContainer.appendChild(editor.ui.view.toolbar.element);
                // 加载了适配器
        editor.plugins.get('FileRepository').createUploadAdapter = (loader)=>{
            return new MyUploadAdapter (loader);
        };
    
   

    window.editor = editor;
} )


