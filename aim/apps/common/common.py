"""
Definition of common function.
"""
from random import randint
from passlib.hash import sha256_crypt
import jwt
from aim.const import Const
import datetime
import calendar
from firebase_admin import messaging
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import pandas
import time
import ast


class Common:

    def get_row_index_by_offset_and_limit(self, offset, limit):
        """
        Getk
        :param offset:
        :param limit:
        :return:
        """
        result = " "
        if(limit is not None and limit != ""):
            result = result + "limit " + str(limit)
            if (offset is not None and offset != ""):
                result = result + " offset " + str(offset)
        return result

    def check_password_hash(self, hashed_password, user_password):
        """
        Check password hash
        :param hashed_password:
        :param user_password:
        :return:
        """
        return sha256_crypt.verify(user_password, hashed_password)

    def gen_access_token(self, phone_number):
        """
        Gen jwt token
        :param phone_number:
        :return:
        """
        jwt_hs256_secret = Const.SECRET_KEY
        access_token = jwt.encode({"phone_number": phone_number}, jwt_hs256_secret, algorithm='HS256')
        access_token = access_token.decode("utf-8")
        return access_token

    def hash_password(self, password):
        """
        Hash password
        :param password:
        :return:
        """
        password_hash = sha256_crypt.encrypt(password)
        return password_hash

    def random_with_N_digits(self, n):
        """
        Random n digit
        :return:
        """
        range_start = 10 ** (n - 1)
        range_end = (10 ** n) - 1
        return randint(range_start, range_end)

    def get_user_from_token(self, auth_token, secret_key):
        """
        Get user information from token
        :param auth_token:
        :return:
        """
        try:
            payload = jwt.decode(auth_token, secret_key)
            result = payload
        except:
            result = None
        return result


    def add_months(self, months):
        """
        Add month
        :param months:
        :return:
        """
        sourcedate = datetime.datetime.now()
        month = sourcedate.month - 1 + months
        year = sourcedate.year + month // 12
        month = month % 12 + 1
        day = min(sourcedate.day, calendar.monthrange(year, month)[1])
        return datetime.date(year, month, day)


    def add_days(self, days):
        """
        Add days
        :param days:
        :return:
        """
        result = datetime.datetime.now() + datetime.timedelta(days=days)
        return result

    def dictfetchall(self, cursor):
        "Returns all rows from a cursor as a dict"
        desc = cursor.description
        return [
            dict(zip([col[0] for col in desc], row))
            for row in cursor.fetchall()
        ]

    def send_message_to_topic(self, title, body, topic_name, data):
        """
        Send message to topic # Use to mobile
        :param topic_name:
        :param data:
        :return:
        """

        # See documentation on defining a message payload.
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(sound='default')
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(sound='default')
                )
            ),
            data=data,
            topic=topic_name
        )

        # Send a message to the devices subscribed to the provided topic.
        response = messaging.send(message)

        print(str(response))

    def calculated_bill_info(self, order):
        """
        Calculated bill info
        :return:
        """
        print("abc")
        # # Get sub total
        # sub_total = order['sub']
        #
        # let
        # totalDiscount = 0
        # // Check
        # free
        # Item
        # totalDiscount += this.calculatedFreeItem()
        #
        # // Check
        # discount
        # totalDiscount += this.calculatedDiscount()
        #
        # // Check
        # discount
        # with max value
        # totalDiscount += this.calculatedDiscountWithMaxValue()
        #
        # // Check
        # voucher
        # totalDiscount += this.calculatedVoucher()
        #
        # if (this.paymentInfo.total < 0) {
        # this.paymentInfo.total = 0
        # }
        #
        # // Calculator
        # VAT
        # this.paymentInfo.vat_value = this.calculatedVatValue(this.paymentInfo.total, this.paymentInfo.vat_value,
        #                                                      this.paymentInfo.vat_percent)
        # this.paymentInfo.total = this.paymentInfo.total + this.paymentInfo.vat_value
        #
        # // Calculated
        # service
        # fee
        # this.calculatedServiceFee()
        #
        # // Calculated
        # total
        # discount
        # amount
        # if (totalDiscount > this.paymentInfo.sub_total + this.paymentInfo.vat_value) {
        # totalDiscount = this.paymentInfo.sub_total + this.paymentInfo.vat_value
        # }
        # this.paymentInfo.discount_amount = totalDiscount
        #
        # // Set
        # money
        # type
        # this.changeDefaultMoneyType()

    def upload_image(self, myfile, path_root):
        """
        Upload menu image
        :param myfile:
        :return:
        """
        if(myfile is None):
            return None
        # Handle file name
        tt = time.time()
        name = myfile._name
        extention = name.split('.')[-1]
        real_name = name.replace(extention, "")
        templ_name = ''.join(e for e in real_name if e.isalnum())
        file_name = templ_name + "_" + str(tt) + "." + extention
        file_name = file_name.strip()

        # Plus root url
        image_path_temp = file_name.replace(" ", "")
        image_path = path_root + image_path_temp
        default_storage.save(image_path, ContentFile(myfile.read()))

        return file_name

    def get_data_frame_from_excel_file(self, import_file, sheet_name, list_column):
        """
        Get data frame from excel file
        :param import_file:
        :param sheet_name:
        :param list_column:
        :return:
        """
        try:
            filename = self.upload_image(import_file, Const.FILE_ROOT + Const.IMAGE_ROOT) #import_file.name
            # default_storage.save(Const.IMAGE_FULL_PATH + filename, ContentFile(import_file.read()))

            data_frame = pandas.read_excel(Const.IMAGE_FULL_PATH + filename, sheet_name=sheet_name)
            data_frame_columns = data_frame.columns
            for i in range(0, len(data_frame_columns) - 1):
                if str(list_column[i]).lower() != str(data_frame_columns[i]).lower():
                    data_frame = None
                    break
        except Exception as e:
            print(str(e))
            data_frame = None
        return data_frame

    def check_role_access_api(self, api_name, screens, staff_query, cursor):
        """
        Check role access api
        :param api_name:
        :param screens:
        :return:
        """
        # Get list api can be access from db
        screens = ast.literal_eval(screens)
        screens = tuple(screens)

        cursor.execute(staff_query.get_list_screen_can_be_access(), [screens])
        apis = self.dictfetchall(cursor)

        # Check exist api name
        for api in apis:
            if api['apis']:
                list_api = ast.literal_eval(api['apis'])
                if api_name in list_api:
                    return True

        return False

    def calculated_payment_info(self, cursor, staff_query, order_id, store_id):
        """
        Calculated payment info
        :return:
        """
        # Get payment info from db
        payment_info = None
        cursor.execute(staff_query.get_bill_info_by_id(), [order_id, store_id])
        payment_infos = self.dictfetchall(cursor)

        old_total = None
        if (len(payment_infos) > 0):
            payment_info = payment_infos[0]
            old_total = payment_info['total']

            payment_info['foods'] = ast.literal_eval(payment_info['foods'])

            if (payment_info['pmts'] is None or payment_info['pmts'] == ''):
                payment_info['pmts'] = []
            else:
                payment_info['pmts'] = ast.literal_eval(payment_info['pmts'])

            if (payment_info['service'] is None or payment_info['service'] == ''):
                payment_info['service'] = []
            else:
                payment_info['service'] = ast.literal_eval(payment_info['service'])

        if payment_info:
            # Tính tổng tiền món
            sub_total = 0
            if payment_info['foods']:
                for food in payment_info['foods']:
                    sub_total = sub_total + (food['price'] * food['quantity'])
            payment_info['sub_total'] = sub_total

            total = payment_info['sub_total']

            # Calculated service fee
            service_amount = 0
            for service in payment_info['service']:
                if 'percent' in service and service['percent'] != 0:
                    service['price'] = int(total * (int(service['percent']) / 100))
                service_amount += int(service['price'])
            total += service_amount

            # Calculate promotion
            total_discount = 0

            # Check free Item
            for pmt in payment_info['pmts']:
                if pmt['type'] == 'free_item':
                    for food in payment_info['foods']:
                        if int(pmt['item_free']) == int(food['foodId']):
                            food_amount = food['price'] * pmt['quantity_apply']
                            # total = total - food_amount
                            total_discount += food_amount

            # Check discount on item
            for pmt in payment_info['pmts']:
                if pmt['type'] == 'discount_on_item':
                    if "," in pmt["on_items"]:
                        pmt["on_items"] = ast.literal_eval(pmt["on_items"])
                    else:
                        pmt["on_items"] = [int(pmt["on_items"])]

                    for food in payment_info['foods']:
                        if food['foodId'] in pmt['on_items']:
                            value_discount = food['price'] * food['quantity'] * int(pmt['discount_percent']) / 100 * int(pmt['quantity_apply'])

                            if value_discount > food['price'] * food['quantity']:
                                food_amount = food['price'] * food['quantity']
                                # total = total - food_amount
                                total_discount += food_amount
                            else:
                                # total = total - value_discount
                                total_discount += value_discount

            # Check discount
            total_discount_percent = 0
            for pmt in payment_info['pmts']:
                if pmt['type'] == 'discount':
                    total_discount_percent += int(pmt['discount_percent']) * int(pmt['quantity_apply'])

            if total_discount_percent > 0:
                if total_discount_percent > 100:
                    total_discount_percent = 100

                value_discount_temp = total * total_discount_percent / 100
                total_discount += value_discount_temp
                # total = total - value_discount_temp

            # Check discount with max value
            total_discount_percent = 0
            total_discount_amount = 0

            for pmt in payment_info['pmts']:
                if pmt['type'] == 'discount_with_max_value':
                    if payment_info['sub_total'] >= int(pmt['discount_on_amount']):
                        discount_amount = payment_info['sub_total'] * int(pmt['discount_percent']) / 100
                        if discount_amount >= int(pmt['max_discount']):
                            total_discount_amount += int(pmt['max_discount']) * int(pmt['quantity_apply'])
                        else:
                            total_discount_percent += int(pmt['discount_percent']) * int(pmt['quantity_apply'])

            if total_discount_percent > 0:
                if total_discount_percent > 100:
                    total_discount_percent = 100
                discount_temp = total * total_discount_percent / 100
                # total = total - discount_temp
                total_discount += discount_temp

            if total_discount_amount > 0:
                # total = total - total_discount_amount
                total_discount += total_discount_amount

            # Check voucher
            for pmt in payment_info['pmts']:
                if pmt['type'] == 'voucher':
                    # total = total - (int(pmt['value_of_voucher']) * int(pmt['quantity_apply']))
                    total_discount += int(pmt['value_of_voucher']) * int(pmt['quantity_apply'])

            # Apply promotion
            if total_discount > total:
                total_discount = total
            payment_info['discount_amount'] = total_discount
            total = total - total_discount

            # Check total < 0
            if total < 0:
                total = 0

            # Calculator VAT
            if payment_info['vat_percent'] != 0 and payment_info['vat_percent'] != "0" and payment_info['vat_percent'] != None:
                payment_info['vat_value'] = int(int(total) * int(payment_info['vat_percent']) / 100)
                total = total + payment_info['vat_value']
            else:
                payment_info['vat_value'] = 0
                payment_info['vat_percent'] = 0

            # Set money type
            if old_total and old_total != total:
                payment_info['cash'] = total
                payment_info['credit'] = 0
                payment_info['e_money'] = 0

            # update db: total, total_discount, service, money type
            cursor.execute(staff_query.update_order_info_after_recalculate(),
                [total, sub_total, total_discount, str(payment_info['service']), service_amount, payment_info['cash'], payment_info['credit'],
                 payment_info['e_money'], payment_info['vat_value'], payment_info['vat_percent'], order_id, store_id])