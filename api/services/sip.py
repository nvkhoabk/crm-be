import json

import requests

from api.const import CALL_DIRECTION
from api.models.call_center import SipServiceInfo
from api.services.exceptions import (SipCredentialError, SipAPIError)

BASE_URL = 'https://cms.siptrunk.vn:1443/'


class SipService:
    def url(self, uri):
        return BASE_URL + uri

    def login(self, user, password, company_id):
        data = {
            "email": user,
            "password": password
        }
        response = requests.post(self.url('api/v2/login'), json=data)
        if response.status_code != 200:
            raise SipCredentialError()

        access_token = json.loads(response.content)['access_token']
        sip_company_id = json.loads(response.content)['company_id']

        try:
            sip_service_info = SipServiceInfo.objects.get(company_id=company_id)
            sip_service_info.token = access_token
            sip_service_info.sip_company_id = sip_company_id
            sip_service_info.save()
        except SipServiceInfo.DoesNotExist:
            sip_service_info = SipServiceInfo.objects.create(company_id=company_id, token=access_token,
                                                             sip_company_id=sip_company_id)
        return sip_service_info

    def get_agent_list(self, company_id):
        limit = 5
        page = 1
        agent_list = []

        try:
            access_token = SipServiceInfo.objects.get(company_id=company_id).token
        except SipServiceInfo.DoesNotExist:
            raise SipCredentialError

        while True:
            res = requests.get(self.url('api/v2/extension?limit={}&order=+id&page={}'.format(limit, page)),
                               headers={'Authorization': 'Bearer ' + access_token})

            if res.status_code != 200:
                raise SipAPIError()

            response_object = res.json()
            for ext in response_object['data']:
                agent_list.append({
                    'ext': 'ext' + str(ext['company']['id']) + str(ext['extension']),
                    'secret': ext['secret'],
                    'sip_id': ext['id']
                })

            page += 1
            total = response_object['meta']['total']
            if total == 0:
                break

        return agent_list

    def filter_call_history(self, company_id, limit, page, month, from_date, to_date, sip_id=None):
        call_history = []

        page += 1
        try:
            sip_service_info = SipServiceInfo.objects.get(company_id=company_id)
            access_token = sip_service_info.token
            sip_company_id = sip_service_info.sip_company_id
        except SipServiceInfo.DoesNotExist:
            raise SipCredentialError

        uri = 'api/v2/pbx/loadCdr?order=-calldate&company={}&month={}&limit={}&page={}'.format(sip_company_id, month,
                                                                                               limit, page)

        if sip_id:
            uri += '&user={}'.format(sip_id)

        if from_date and to_date:
            uri += '&filters={{"initDate":"{}", "endDate":"{}"}}'.format(from_date, to_date)

        res = requests.get(self.url(uri), headers={'Authorization': 'Bearer ' + access_token})

        if res.status_code != 200:
            raise SipAPIError()

        response_object = res.json()
        for cdr in response_object['data']:
            if cdr['direction'] == CALL_DIRECTION.INCOMING:
                call_history.append({
                    'dest_number': cdr['callerid'],
                    'calldate': cdr['calldate'],
                    'src_extension': cdr['dst_extension'],
                    'record_url': self.get_record_url(cdr),
                    'direction': cdr['direction'],
                    'duration': cdr['duration'],
                    'ext': 'ext' + cdr['dst_company'] + cdr['dst_extension']
                })

            if cdr['direction'] == CALL_DIRECTION.OUTGOING:
                call_history.append({
                    'dest_number': cdr['destination'],
                    'calldate': cdr['calldate'],
                    'src_extension': cdr['src_extension'],
                    'record_url': self.get_record_url(cdr),
                    'direction': cdr['direction'],
                    'duration': cdr['duration'],
                    'ext': 'ext' + cdr['src_company'] + cdr['src_extension']
                })

        return call_history

    def get_record_url(self, cdr):
        return BASE_URL + cdr['record_file'] if cdr['record_file'] else None
