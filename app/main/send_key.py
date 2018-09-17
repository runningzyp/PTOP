# -*- coding: utf-8 -*-

import json
import os

from aliyunsdkcore import client
from aliyunsdksts.request.v20150401 import AssumeRoleRequest

import oss2


# 以下代码展示了STS的用法，包括角色扮演获取临时用户的密钥、使用临时用户的密钥访问OSS。

# STS入门教程请参看  https://yq.aliyun.com/articles/57895
# STS的官方文档请参看  https://help.aliyun.com/document_detail/28627.html

# 首先初始化AccessKeyId、AccessKeySecret、Endpoint等信息。
# 通过环境变量获取，或者把诸如“<你的AccessKeyId>”替换成真实的AccessKeyId等。
# 注意：AccessKeyId、AccessKeySecret为子用户的密钥。
# RoleArn可以在控制台的“访问控制  > 角色管理  > 管理  > 基本信息  > Arn”上查看。
#
# 以杭州区域为例，Endpoint可以是：
#   http://oss-cn-hangzhou.aliyuncs.com
#   https://oss-cn-hangzhou.aliyuncs.com
# 分别以HTTP、HTTPS协议访问。
'''
access_key_id = 'LTAInn4CiOcTMupp'
access_key_secret = 'YNHxZ7QdZ160zmMO0kmLu2QJ6MtA3A'
bucket_name = 'zhanyunpeng1995'
endpoint = 'oss-cn-shanghai.aliyuncs.com'
sts_role_arn = 'acs:ram::1158764349830607:role/oss-scaner'


# 确认上面的参数都填写正确了
for param in (access_key_id, access_key_secret, bucket_name, endpoint, sts_role_arn):
    assert '<' not in param, '请设置参数：' + param
'''


class StsToken(object):
    """AssumeRole返回的临时用户密钥
    :param str access_key_id: 临时用户的access key id
    :param str access_key_secret: 临时用户的access key secret
    :param int expiration: 过期时间，UNIX时间，自1970年1月1日UTC零点的秒数
    :param str security_token: 临时用户Token
    :param str request_id: 请求ID
    """

    def __init__(self):
        self.access_key_id = ''
        self.access_key_secret = ''
        self.expiration = 0
        self.security_token = ''
        self.request_id = ''


def fetch_sts_token(access_key_id, access_key_secret, role_arn):
    """子用户角色扮演获取临时用户的密钥
    :param access_key_id: 子用户的 access key id
    :param access_key_secret: 子用户的 access key secret
    :param role_arn: STS角色的Arn
    :return StsToken: 临时用户密钥
    你好
    """
    clt = client.AcsClient(access_key_id, access_key_secret, 'cn-hangzhou')
    req = AssumeRoleRequest.AssumeRoleRequest()

    req.set_accept_format('json')
    req.set_RoleArn(role_arn)
    req.set_RoleSessionName('oss-python-sdk-example')

    body = clt.do_action_with_exception(req)

    j = json.loads(oss2.to_unicode(body))

    token = StsToken()

    token.access_key_id = j['Credentials']['AccessKeyId']
    token.access_key_secret = j['Credentials']['AccessKeySecret']
    token.security_token = j['Credentials']['SecurityToken']
    token.request_id = j['RequestId']
    token.expiration = oss2.utils.to_unixtime(
        j['Credentials']['Expiration'], '%Y-%m-%dT%H:%M:%SZ')

    return token
