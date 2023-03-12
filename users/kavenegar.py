from kavenegar import *

from majorselection1402.settings import Kavenegar_API


def send_otp(mobile, otp):
    mobile = [mobile]
    try:
        api = KavenegarAPI(Kavenegar_API)
        params = {
            'sender': '10008663',
            'receptor': mobile,
            'message': 'Your otp is {}'.format(otp),
        }
        response = api.sms_send(params)
        print('OTP: ', otp)
        print(response)
    except APIException as e:
        print(e)
    except HTTPException as e:
        print(e)

