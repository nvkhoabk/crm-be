from zalo.sdk.app import ZaloAppInfo, Zalo3rdAppClient

app_id = '2252452034861651725'
secret_key = 'mNC5uCK6TN6kBgD5oqU6'
callback_url = 'https://crm.ity.vn/api/zalo/login/callback'

zalo_info = ZaloAppInfo(app_id, secret_key, callback_url)
zalo = Zalo3rdAppClient(zalo_info)

login_url = zalo.get_login_url()
print (login_url)

code = 'dEhm-nL7o6Iur9ILC6kAAglule9LTvXLwllFX5jIr2hYml-0Sr2YTlxklwbZVOq4aFQkrYvv-W7_qU6eGqZC3DtLclbQRhv6nlIukXHAc6opmDUM5M7fEwZuYuSKGACfqANOsY8GwsZKYjB4F5BQSDcOkOTh4EXrjz3Xb2bCwIlrXS_l4mxkKQk0qBmJ1O5Jwi7yc2S6qZ3jfV2SIH757xcB_BLuPD0ZnU6irISib0xgwfgWVKRELvopfQvrE8H_xQtLYqWm_2BlgTQ9Pr_IBhYXh14SEwkjfu2AJWu_whcksl0c5LBXkxtpf7b3SxFkyEwsO04bnQ6EdgGrAfRcggC-_XTQsypreNE9JsQtrlNr9uuyCxM_j-97Z6rFlR6bNbacsBToQWb1u6G'
access_token = zalo.get_access_token(code)
print (access_token)
profile = zalo.get('/me', access_token['access_token'], {'fields': 'id, name'})
print (profile)