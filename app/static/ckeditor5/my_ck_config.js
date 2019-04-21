      
      ClassicEditor
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
             ckfinder: {
                // Upload the images to the server using the CKFinder QuickUpload command.
                uploadUrl: $SCRIPT_ROOT+"admin/upload-blog-image"
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
            fontSize: {
                options: [
                    'tiny',
                    'small',
                    'big',
                    'huge'
                ]
            },
            
            language: 'zh-cn',
    })
.then( editor => {
    window.editor = editor;
} )


