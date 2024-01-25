from kavenegar import *

from majorselection1402.settings import Kavenegar_API


def send_otp(mobile, otp):
    mobile = [mobile]
    try:
        api = KavenegarAPI(Kavenegar_API)
        params = {
            # 'sender': '1000080008880',
            'receptor': mobile,
            'template': 'verify1',
            # 'message': 'میزترید \n کد تایید شماره تلفن شما: \n {}'.format(otp),
            'token': otp,
            'type': 'sms'
        }
        response = api.verify_lookup(params)
        print(response)
        # print('OTP: ', otp)
        # print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)

