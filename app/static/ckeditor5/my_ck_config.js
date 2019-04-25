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

DecoupledEditor
.create(document.querySelector('#editor'),{
    
    viewportTopOffset : 50,  

     ckfinder: {
        // Upload the images to the server using the CKFinder QuickUpload command.
        uploadUrl: "http://127.0.0.1:5000/admin/img"
    },  

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


})
.then( editor => {
    
      const toolbarContainer = document.querySelector('#toolbar-container');

                toolbarContainer.appendChild(editor.ui.view.toolbar.element);

                // 加载了适配器
    editor.plugins.get('FileRepository').createUploadAdapter = (loader)=>{
        return new MyUploadAdapter (loader);
    };

    window.editor = editor;
    // const toolbarContainer = document.querySelector( 'layui-footer' );

    // toolbarContainer.appendChild( editor.ui.view.toolbar.element );
} )


