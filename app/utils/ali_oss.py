# -*- coding:utf-8 -*-

import base64
import oss2
import time
import datetime
import json
import hmac

from hashlib import sha1 as sha


def get_bucket():
    from app.models import AliConfig
    config = AliConfig.query.first()
    auth = oss2.Auth(config.access_key_id, config.access_key_secret)
    bucket = oss2.Bucket(auth, config.host, config.bucket)
    return bucket


def get_iso_8601(expire):
    gmt = datetime.datetime.utcfromtimestamp(expire).isoformat()
    gmt += "Z"
    return gmt


# def get_token(upload_dir, expire_time, access_key_id, access_key_secret,
#               callback_url, host='http://oss-cn-shanghai.aliyuncs.com',):
def get_token(aliconfig, upload_dir):
    now = int(time.time())  # 返回当前时间的时间戳（1970纪元后经过的浮点秒数）。
    expire_syncpoint = now + aliconfig.expire_time  # 设置过期时间

    expire = get_iso_8601(expire_syncpoint)  # 转化为gmt时间

    condition_array = []
    array_item = []
    array_item.append("starts-with")
    array_item.append("$key")
    array_item.append(upload_dir)
    condition_array.append(array_item)

    # 构建police
    policy_dict = {}
    policy_dict["expiration"] = expire
    policy_dict["conditions"] = condition_array
    policy = json.dumps(policy_dict).strip().encode("utf-8")
    policy_encode = base64.b64encode(policy)
    h = hmac.new(
        aliconfig.access_key_secret.encode("utf-8"), policy_encode, sha
    )
    sign_result = base64.encodebytes(h.digest()).strip().decode("utf-8")

    # 构建callback
    callback_dict = {}
    callback_dict["callbackUrl"] = aliconfig.callback_url
    callback_dict[
        "callbackBody"
    ] = "bucket=${bucket}&filename=${object}&size=${size}&mimeType=${mimeType}&height=${imageInfo.height}&width=${imageInfo.width}"
    callback_dict["callbackBodyType"] = "application/x-www-form-urlencoded"
    callback_param = json.dumps(callback_dict).strip().encode("utf-8")
    base64_callback_body = base64.b64encode(callback_param).decode("utf-8")

    # 构建token
    token_dict = {}
    token_dict["accessid"] = aliconfig.access_key_id
    token_dict["url_prefix"] = aliconfig.url_prefix
    token_dict["policy"] = policy_encode.decode("utf-8")
    token_dict["signature"] = sign_result
    token_dict["expire"] = expire_syncpoint
    token_dict["dir"] = upload_dir
    token_dict["callback"] = base64_callback_body

    result = json.dumps(token_dict)
    return result
