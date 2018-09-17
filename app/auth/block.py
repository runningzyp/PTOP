def random_str(randomlength=6):
    str = ''
    chars = '0123456789'
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


    while (True):
            userkey = random_str(6)
            user = User.query.filter_by(userkey=userkey).first()
            if user is None:
                break