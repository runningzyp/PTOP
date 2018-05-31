if request.method == 'POST':
        old_filename = ''
        sec_filename = ''
        dt = datetime.datetime.utcnow()
        sec_key = dt.strftime("%Y-%m-%d-%H-%M-%S")
        text = request.form.get('text')
#       if 'file' not in request.files:
#           print('yes')
        try:
            file = request.files['file']
            real_name = '['+sec_key + ']' + secure_filename(file.filename)
            old_filename = file.filename
            sec_filename = real_name
            persional_folder = UPLOAD_FOLDER
            file.save(os.path.join(persional_folder, real_name))
        except:
            file = None


$('#file-submit').click(function(), {  // 等于按钮
    $.getJSON($SCRIPT_ROOT + '/_sendfile', {
      file: $('#file').val(),
      device_type: 'web'
    }, function(data) {
        $("input[name='text']").val("").focus();
        $(".window-show").append($add_text);
        $(".window-hide-line").show(1000);
        $('.window-show').scrollTop( $('.window-show')[0].scrollHeight );
    });
  });


@main.route('/_sendfile')
@login_required
def sendfile():
    file = request.args.get('file', '')
    device_type = request.args.get('device_type', '')
    dt = datetime.datetime.utcnow()
    if file is not None:
        filename = file.filename
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        data = Data(filename=filename, device_type=device_type,
                    author=current_user._get_current_object())
        db.session.add(data)
    return jsonify(text=text)





  $('#file-submit').click(function() {  // 等于按钮
    var formData = new FormData($('#uploadForm')[0]);
    $.getJSON($SCRIPT_ROOT + '/_send', {
      file: formData
      device_type: 'web'
    }, function(data) {
        $("input[name='text']").val("").focus();
        $(".window-show").append($add_text);
        $(".window-hide-line").show(1000);
        $('.window-show').scrollTop( $('.window-show')[0].scrollHeight );
    });
})
