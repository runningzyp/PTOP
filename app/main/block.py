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









  $(".window-show").append(
        <div class="window-show-line">
                               <div class="row clearfix">
                                       <div class="col-md-1 col-xs-2 column" style="padding-left:15px;padding-right: 0;">
                                               <a href="{{url_for('.user',username=current_user.username)}}">
                                                   <img class="profile-thumbnail img-responsive" src="{{ url_for('static', filename='ico/web.png') }}">
                                               </a>                                                            
                                       </div>
                                      
                                       <div class="col-md-7 col-xs-8 column" style="padding-left:0px;" >
                                           
                                           <div class="window-show-data">                            
                                          
                                           </div>
                                        
                                       </div>
                                       <div class="col-md-3 column">
                                       </div>
                                       <div class="col-md-1 column">
                                       </div>
                               </div>
                            </div>
            