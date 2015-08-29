
import time

_ACCOUNT = 'gh_b74fddf87897'

_TEMPLATE_TEXT = '''<xml>
<ToUserName><![CDATA[{ToUserName}]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>{CreateTime}</CreateTime>
<MsgType><![CDATA[{MsgType}]]></MsgType>
<Content><![CDATA[{Content}]]></Content>
</xml>''' % _ACCOUNT

_template_map = {'text': _TEMPLATE_TEXT}

#values is a dict contains fromuser, touser, createtime and ...
def reply(**values):
    #get msgtype from dict values, let it be text if not existed
    msgtype = values.get('MsgType', 'text')
    values['CreateTime'] = int(time.time())

    tmp = _template_map.get(msgtype, '')
    try:
        tmp = tmp.format(**values)
    except:
        tmp = ''

    return tmp or None
