import logging
import sys
import time
import base64
import gzip
import datetime
import requests
import simplejson as json
from decimal import Decimal as D
from cStringIO import StringIO
from xml.etree import cElementTree as eTree
import persistence
from bustoken import TK_FISCALWRAPPER_GET_FISCAL_XML
from mwapp.components import AuditEventConsumer
from msgbus import TK_STORECFG_GET, FM_PARAM, TK_SYS_ACK
from systools import sys_log_error, sys_log_exception, sys_log_info, sys_log_warning
from syserrors import SE_SUCCESS, SE_NOTFOUND, SE_CFGLOAD, SE_BADXML, SE_BADRESPONSE, SE_CONNECT, SE_USERCANCEL


logger = logging.getLogger("BohPump")

__all__ = ()
_SERVICE_NAME = 'BohPump'
_SERVICE_TYPE = 'DataPump'
_CFG_GROUP = _SERVICE_NAME
_AUDITLOG_SUBJECT = 'AUDITLOGGER'
_EXPORTED_SERVICES = '%s:%s' % (_SERVICE_NAME, _SERVICE_TYPE)
_REQUIRED_SERVICES = 'AuditLogger|StoreWideConfig'
_VIEWS = {
    'OPERATORLOGOUT': 'pump/sale/close-drawer',
    'USER_PUNCH': 'pump/hr/time-entry-pos',
    'BUSINESSBEGIN': 'pump/cash/pos-status',
    'BUSINESSEND': 'pump/cash/pos-status',
    'PAID': 'pump/sale/order-picture',
    'VOID_ORDER': 'pump/sale/order-picture',
    'PRODUCTION_ORDER_TIMES': 'pump/sale/production-history'
}


def add_not_empty(event, field_name, xml, attribute):
    value = xml.get(attribute)
    if value not in (None, ''):
        event[field_name] = value
    return None


mbcontext = None
config = None


class _BohPumpImpl(AuditEventConsumer):
    """private - class used just to keep private functions on a single namespace"""

    def __init__(self):
        super(self.__class__, self).__init__(_SERVICE_NAME, _SERVICE_TYPE, self.process, _CFG_GROUP, _REQUIRED_SERVICES)
        self.serverURL = None
        self.throttle = None
        self.storeId = None
        self.countryCode = None
        self.apiKey = None
        self.msgBusTerm = False
        self.responseLog = False
        self.queueFolder = None
        self.queueMaxSize = 1000
        self.processDisabled = False
        self.alwaysEncode = True
        self.persistence_service = None
        self._cache = {}
        self.get_cache()
        self.read_config()

    def read_config(self):
        """private - reads the configuration file"""
        try:
            msg = self.mbcontext.MB_EasySendMessage('StoreWideConfig', TK_STORECFG_GET, format=FM_PARAM, data='Store.Id')
            self.storeId = msg.data.split('\x00')[0]
            msg = self.mbcontext.MB_EasySendMessage('StoreWideConfig', TK_STORECFG_GET, format=FM_PARAM, data='Store.Country')
            self.countryCode = msg.data.split('\x00')[0]
            msg = self.mbcontext.MB_EasySendMessage('StoreWideConfig', TK_STORECFG_GET, format=FM_PARAM, data='BackOffice.ApiKey')
            self.apiKey = msg.data
            msg = self.mbcontext.MB_EasySendMessage('StoreWideConfig', TK_STORECFG_GET, format=FM_PARAM, data='BackOffice.ServerURL')
            self.serverURL = msg.data
            if self.serverURL is None:
                logger.error('[%s] Configuration error: BohPump.serverURL is undefined.' % _SERVICE_NAME)
                sys.exit(SE_NOTFOUND)

            if not self.serverURL.endswith('/'):
                self.serverURL += '/'

            self.throttle = int(self.config.find_value('BohPump.throttle', '100'))
            self.retryWait = int(self.config.find_value('BohPump.retryWait', '10000'))
            self.initialPeriod = int(self.config.find_value('BohPump.initialPeriod', '0'))
            self.responseLog = self.config.find_value('BohPump.responseLog', 'false').lower() == 'true'
            self.alwaysEncode = self.config.find_value('BohPump.alwaysEncode', 'true').lower() == 'true'
            self.persistence_service = self.config.find_value('BohPump.persistenceService', 'Persistence').encode('utf-8')
        except:
            logger.exception('[%s] Error reading configuration file.' % _SERVICE_NAME)
            sys.exit(SE_CFGLOAD)

    def get_cache(self):
        self._cache['BKPLU'] = {}
        self._cache['Categories'] = {}
        self._cache['SubCategories'] = {}
        self._cache['Operators'] = {}
        conn = persistence.Driver().open(self.mbcontext, service_name=self.persistence_service)
        cursor = conn.select("\n            SELECT ProductCode, CustomParamId, CustomParamValue\n            FROM (\n                SELECT\n                    ProductCode,\n                    substr(Tag,1,instr(Tag,'=')-1) AS CustomParamId,\n                    substr(Tag,instr(Tag,'=')+1) AS CustomParamValue\n                FROM ProductTags\n            ) Tags\n            WHERE Tags.CustomParamId IN ('Categories', 'SubCategories')\n        ")
        for row in cursor:
            if row.get_entry('CustomParamId') == 'Categories':
                self._cache['Categories'][row.get_entry('ProductCode')] = row.get_entry('CustomParamValue')
            if row.get_entry('CustomParamId') == 'SubCategories':
                self._cache['SubCategories'][row.get_entry('ProductCode')] = row.get_entry('CustomParamValue')

        check_cat_subcat_from_custom_params = len(self._cache['Categories']) == 0
        cursor = conn.select('SELECT * FROM productdb.ProductCustomParams;')
        for row in cursor:
            if row.get_entry('CustomParamId') == 'BKPLU':
                self._cache['BKPLU'][row.get_entry('ProductCode')] = row.get_entry('CustomParamValue')
            if check_cat_subcat_from_custom_params:
                if row.get_entry('CustomParamId') == 'Categories':
                    self._cache['Categories'][row.get_entry('ProductCode')] = row.get_entry('CustomParamValue')
                if row.get_entry('CustomParamId') == 'SubCategories':
                    self._cache['SubCategories'][row.get_entry('ProductCode')] = row.get_entry('CustomParamValue')

    def send_request(self, view, payload):
        try:
            headers = {
                'Accept': 'application/json',
                'Content-type': 'application/json',
                'x-api-key': self.apiKey
            }
            url = '{}{}'.format(self.serverURL, view)
            
            logger.info('[{0}] Sending event to: {1}, payload:\n{2}'.format(_SERVICE_NAME, url, payload))

            response = requests.post(url,
                                     headers=headers,
                                     data=payload,
                                     timeout=30,
                                     verify=False)
            if response.status_code != 200:
                logger.info('[{}] Error sending event to server, status: {}; description: {}'.format(_SERVICE_NAME, response.status_code, response.content))
                time.sleep(self.retryWait / 1000.0)
                return SE_BADRESPONSE
            logger.info('[%s] Success sending event to server.' % _SERVICE_NAME)
            return SE_SUCCESS
        except Exception as _:
            logger.exception('[%s] Communication error sending event to server.' % _SERVICE_NAME)
            return SE_CONNECT

    def process(self, conn, evt_list):
        evtdata = None
        for evt in evt_list:
            try:
                xml, type = evt[0], evt[1]
                event = eTree.XML(xml)
                auditlog = event.find('AuditLog')
                evttime = auditlog.get('evtTime') or ''
                createdat = auditlog.get('createdAt') or ''
                evtdata = auditlog.text.encode('UTF-8')
                data = eTree.fromstring(gzip.GzipFile(fileobj=StringIO(base64.b64decode(evtdata))).read())
            except:
                logger.exception('[%s] Auditlog Event parser error. Exiting to force resynchronization.' % _SERVICE_NAME)
                return SE_BADXML

            try:
                if type == 'BUSINESSBEGIN' or type == 'BUSINESSEND':
                    payload = {}
                    payload['store-code'] = str(self.storeId)
                    period = data.get('period')
                    period = datetime.datetime.strptime(period, '%Y%m%d')
                    payload['business-dt'] = period.strftime('%Y-%m-%d')
                    payload['pos-code'] = data.get('posid')
                    if type == 'BUSINESSBEGIN':
                        status = 'OPENED'
                    else:
                        status = 'CLOSED'
                    payload['status'] = status
                    payload['event-dttm'] = evttime or datetime.datetime.today().strftime('%Y-%m-%dT%H:%M:%S.000')
                    status = self.send_request(_VIEWS.get(type), json.dumps(payload))
                    if status != SE_SUCCESS:
                        return status

                if type == 'PAID' or type == 'VOID_ORDER':
                    payload = {}
                    payload['store-code'] = str(self.storeId)
                    payload['order-code'] = data.get('orderId')

                    msg = self.mbcontext.MB_EasySendMessage('FiscalWrapper', TK_FISCALWRAPPER_GET_FISCAL_XML, FM_PARAM,
                                                            str(data.get('orderId')))
                    if msg.token == TK_SYS_ACK:
                        fiscal_base64 = msg.data
                        payload['xml-data'] = fiscal_base64

                    session_id = data.get('sessionId')
                    for session_data in session_id.split(','):
                        key_data = session_data.split('=')
                        if key_data[0] == 'user':
                            payload['pos-user-id'] = key_data[1]

                    if data.get('exemptionCode'):
                        payload['exemption'] = int(data.get('exemptionCode'))
                    if data.get('posId'):
                        payload['pos-code'] = data.get('posId')
                    else:
                        for session_data in session_id.split(','):
                            key_data = session_data.split('=')
                            if key_data[0] == 'pos':
                                payload['pos-code'] = key_data[1]

                    order_picture_custom_order_properties = {}
                    if data.find('CustomOrderProperties'):
                        custom_properties = data.find('CustomOrderProperties')
                        for custom_property in custom_properties:
                            order_picture_custom_order_properties[custom_property.get('key')] = custom_property.get('value')

                    payload['order-picture-custom-order-properties'] = order_picture_custom_order_properties

                    period = data.get('businessPeriod')
                    period = datetime.datetime.strptime(period, '%Y%m%d')
                    payload['business-dt'] = period.strftime('%Y-%m-%d')
                    payload['session'] = session_id
                    payload['originator-code'] = data.get('originatorId')
                    payload['pod-type'] = data.get('podType')
                    payload['state-id'] = int(data.get('stateId'))
                    payload['type-id'] = int(data.get('typeId'))
                    payload['sale-type-id'] = int(data.get('saleType'))
                    payload['price-list'] = data.get('priceList')
                    payload['price-basis'] = data.get('priceBasis')
                    payload['total-amount'] = float(data.get('totalAmount') or 0)
                    payload['total-after-discount'] = float(data.get('totalAfterDiscount') or 0)
                    payload['total-gross'] = float(data.get('totalGross') or 0)
                    payload['total-tender'] = float(data.get('totalTender') or 0)
                    payload['total-gift'] = float(0)
                    payload['change'] = float(data.get('change') or 0)
                    payload['due-amount'] = float(data.get('dueAmount') or 0)
                    payload['tax-total'] = float(data.get('taxTotal') or 0)
                    payload['discount-amount'] = float(data.get('discountAmount') or 0)
                    payload['order-discount-amount'] = float(data.get('orderDiscountAmount') or 0)
                    payload['tip'] = float(data.get('tip') or 0)
                    payload['tax-applied'] = float(data.get('taxTotal') or 0)
                    payload['discount-applied'] = data.get('discountsApplied')
                    payload['creation-dttm'] = data.get('createdAtGMT') + "Z"
                    payload['order-picture-sale-lines'] = []
                    payload['order-picture-tenders'] = []
                    for sale_line in data.findall('SaleLine'):
                        sale_line_payload = {}
                        sale_line_payload['order-picture-id'] = int(data.get('orderId'))
                        sale_line_payload['line-number'] = int(sale_line.get('lineNumber'))
                        sale_line_payload['level'] = int(sale_line.get('level'))
                        sale_line_payload['plu'] = sale_line.get('partCode')
                        sale_line_payload['menu-item-code'] = sale_line.get('itemId')
                        sale_line_payload['item-type'] = sale_line.get('itemType')
                        sale_line_payload['part-code'] = self._cache['BKPLU'].get(sale_line.get('partCode'))
                        sale_line_payload['product'] = sale_line.get('productName')
                        sale_line_payload['multiplied-qty'] = D(sale_line.get('multipliedQty'))
                        sale_line_payload['qty'] = D(sale_line.get('qty'))
                        sale_line_payload['inc-qty'] = D(sale_line.get('incQty'))
                        sale_line_payload['dec-qty'] = D(sale_line.get('decQty'))
                        if sale_line.get('defaultQty'):
                            sale_line_payload['default-qty'] = D(sale_line.get('defaultQty'))
                        if sale_line.get('addedQty'):
                            sale_line_payload['added-qty'] = D(sale_line.get('addedQty'))
                        if sale_line.get('subQty'):
                            sale_line_payload['sub-qty'] = D(sale_line.get('subQty'))
                        if sale_line.get('chosenQty'):
                            sale_line_payload['chosen-qty'] = D(sale_line.get('chosenQty'))
                        sale_line_payload['comment'] = []
                        for comment in sale_line.findall('Comment'):
                            sale_line_payload['comment'].append(comment.get('comment'))

                        sale_line_payload['category-description'] = self._cache['Categories'].get(sale_line.get('partCode'))
                        sale_line_payload['sub-category-description'] = self._cache['SubCategories'].get(sale_line.get('partCode'))
                        sale_line_payload['item-price'] = float(sale_line.get('itemPrice') or 0)
                        sale_line_payload['unit-price'] = float(sale_line.get('unitPrice') or 0)
                        sale_line_payload['added-unit-price'] = float(sale_line.get('addedUnitPrice') or 0)
                        sale_line_payload['sub-unit-price'] = float(sale_line.get('subUnitPrice') or 0)
                        sale_line_payload['price-key'] = sale_line.get('priceKey')
                        sale_line_payload['item-discount'] = float(sale_line.get('itemDiscount') or 0)
                        sale_line_payload['item-discount-applied'] = sale_line.get('discountsApplied')
                        payload['order-picture-sale-lines'].append(sale_line_payload)

                    for tender_line in data.findall('TenderHistory/Tender'):
                        tender_payload = {}
                        tender_payload['order-picture-id'] = int(data.get('orderId'))
                        tender_payload['tender-type'] = tender_line.get('tenderType')
                        if tender_line.get('tenderDetail'):
                            tender_payload['tender-detail'] = tender_line.get('tenderDetail')
                        tender_payload['tender-amount'] = float(tender_line.get('tenderAmount') or 0)
                        tender_payload['reference-amount'] = float(tender_line.get('tenderAmount') or 0)
                        tender_payload['change-amount'] = float(tender_line.get('change') or 0)
                        if tender_line.get('tip'):
                            tender_payload['tip'] = float(tender_line.get('tip'))
                        payload['order-picture-tenders'].append(tender_payload)

                    status = self.send_request(_VIEWS.get(type), json.dumps(payload, use_decimal=True))
                    if status != SE_SUCCESS:
                        return status
                if type == 'USER_PUNCH':
                    operator_id = int(data.get('operatorId'))
                    period = data.get('businessPeriod')
                    punch_time = data.get('dateTime')
                    evt_punch_type = data.get('type')
                    punch_type = evt_punch_type == '0'
                    punch_time = datetime.datetime.strptime(punch_time, '%Y-%m-%dT%H:%M:%S')
                    punch_time += datetime.datetime.utcnow() - datetime.datetime.now()
                    period = datetime.datetime.strptime(period, '%Y%m%d')
                    payload = {
                        'store-code': str(self.storeId),
                        'business-dt': period.strftime('%Y-%m-%d'),
                        'entry-dttm': evttime or punch_time.strftime('%Y-%m-%dT%H:%M:%S.000'),
                        'pos-user-id': operator_id,
                        'in': punch_type
                    }
                    status = self.send_request(_VIEWS.get(type), json.dumps(payload))
                    if status != SE_SUCCESS:
                        return status

                if type == 'OPERATORLOGOUT':
                    period = data.get('period')
                    payload_period = datetime.datetime.strptime(period, '%Y%m%d')
                    session_id = data.get('sessionid')
                    pos_id = data.get('posid')
                    operator_id = int(data.get('operatorid'))
                    initial_float = data.get('initialfloat')
                    conn = None
                    trans = False
                    if not session_id:
                        logger.warning("** ATTENTION: Undefined 'sessionid' in the 'OPERATORLOGOUT' event. Dismissing it. **")
                        continue
                    try:
                        conn = persistence.Driver().open(self.mbcontext, service_name=self.persistence_service)
                        conn.set_dbname(str(pos_id))
                        conn.transaction_start()
                        trans = True
                        op_open = None
                        op_close = None
                        sql = "\n                            SELECT strftime('%%Y-%%m-%%dT%%H:%%M:%%f', OpenTime) AS OpenTime,\n                                   strftime('%%Y-%%m-%%dT%%H:%%M:%%f', CloseTime) AS CloseTime\n                              FROM UserSession\n                             WHERE SessionId = '%s';\n                        " % session_id
                        cursor = conn.select(sql)
                        for row in cursor:
                            op_open = row.get_entry('OpenTime')
                            op_close = row.get_entry('CloseTime')

                        payload = {
                            'store-code': str(self.storeId),
                            'business-dt': payload_period.strftime('%Y-%m-%d'),
                            'pos-code': pos_id,
                            'pos-user-id': operator_id,
                            'session': session_id,
                            'opened-at-dttm': op_open,
                            'closed-at-dttm': op_close,
                            'closed-drawer-detail': []
                        }
                        drawer_count = {}
                        conn.query('DELETE FROM temp.ReportsPeriod')
                        conn.query('INSERT INTO temp.ReportsPeriod(StartPeriod,EndPeriod) VALUES(%s,%s)' % (period, period))
                        sql = "SELECT * from temp.CASHView WHERE SessionId='%s';" % session_id
                        cursor = conn.select(sql)
                        transfer_in_amount = float(0)
                        transfer_out_amount = float(0)
                        transfer_skim_amount = float(0)
                        drawer_count = {
                            0: {
                                'tender-type-code': '0',
                                'computed-amount': 0.0,
                                'tip-amount': 0.0,
                                'transaction-count': 0,
                                'paid-in-amount': 0.0,
                                'paid-out-amount': 0.0,
                                'skim-amount': 0.0,
                                'counted-amount': None,
                                'initial-float-amount': 0.0
                            }
                        }
                        for row in cursor:
                            if row.get_entry('TransferInAmount'):
                                transfer_in_amount = transfer_in_amount + float(row.get_entry('TransferInAmount'))
                            if row.get_entry('TransferOutAmount'):
                                transfer_out_amount = transfer_out_amount + float(row.get_entry('TransferOutAmount'))
                            if row.get_entry('SkimAmount'):
                                transfer_skim_amount = transfer_skim_amount + float(row.get_entry('SkimAmount'))
                            if row.get_entry('TenderSessionInfo'):
                                sales = eval(row.get_entry('TenderSessionInfo'))
                                for sale in sales:
                                    tender_id = sale['TenderId']
                                    if tender_id in drawer_count:
                                        drawer_count[tender_id]['computed-amount'] += float(sale['TenderTotal'])
                                        drawer_count[tender_id]['tip-amount'] += float(sale['TipAmount'])
                                        drawer_count[tender_id]['transaction-count'] += int(sale['PaidQty'])
                                    else:
                                        drawer_count[tender_id] = {}
                                        drawer_count[tender_id]['tender-type-code'] = str(tender_id)
                                        drawer_count[tender_id]['computed-amount'] = float(sale.get('TenderTotal') or 0)
                                        drawer_count[tender_id]['tip-amount'] = float(sale.get('TipAmount') or 0)
                                        drawer_count[tender_id]['transaction-count'] = int(sale.get('PaidQty') or 0)
                                        drawer_count[tender_id]['paid-in-amount'] = 0
                                        drawer_count[tender_id]['paid-out-amount'] = 0
                                        drawer_count[tender_id]['skim-amount'] = 0
                                        drawer_count[tender_id]['counted-amount'] = None
                                        drawer_count[tender_id]['initial-float-amount'] = 0

                        try:
                            sql = "SELECT TenderId, tdsum(Amount) from Transfer WHERE SessionId='%s' AND Type=6 GROUP BY TenderId;" % session_id
                            cursor = conn.select(sql)
                            declared_amounts = dict([ (int(row.get_entry(0)), float(row.get_entry(1) or 0)) for row in cursor ])
                        except Exception as e:
                            logger.error('Failed to query for declared amounts: %s' % str(e))
                            declared_amounts = {}

                        for tender_infos in drawer_count:
                            if tender_infos == 0:
                                drawer_count[tender_infos]['paid-in-amount'] = transfer_in_amount
                                drawer_count[tender_infos]['paid-out-amount'] = transfer_out_amount
                                drawer_count[tender_infos]['skim-amount'] = transfer_skim_amount
                                drawer_count[tender_infos]['initial-float-amount'] = float(initial_float)
                            if tender_infos in declared_amounts:
                                drawer_count[tender_infos]['counted-amount'] = declared_amounts[tender_infos]
                            payload['closed-drawer-detail'].append(drawer_count[tender_infos])

                        status = self.send_request(_VIEWS.get(type), json.dumps(payload))
                        if status != SE_SUCCESS:
                            return status
                    finally:
                        if conn is not None:
                            if trans:
                                conn.transaction_end()
                                trans = False
                            conn.close()
                            conn = None

                if type == 'PRODUCTION_ORDER_TIMES':
                    logger.info('[BohPump] processing order times')
                    result = list()
                    for order_xml in data.findall('Order'):
                        order = dict()
                        result.append(order)
                        order['creation-dttm'] = order_xml.get('created_at')
                        order['order-code'] = order_xml.get('orderId')
                        order['business-dt'] = order_xml.get('period')
                        events = list()
                        order['events'] = events
                        events_xml = order_xml.findall('Event')
                        for event_xml in events_xml:
                            event = dict()
                            events.append(event)
                            event['type'] = event_xml.get('type')
                            event['event-dttm'] = event_xml.get('timestamp')
                            event['production-line'] = event_xml.get('box')
                            add_not_empty(event, 'production-queue', event_xml, 'queue')
                            add_not_empty(event, 'production-status', event_xml, 'prod_state')
                            add_not_empty(event, 'automatic', event_xml, 'automatic')
                            add_not_empty(event, 'order-line-code', event_xml, 'line_id')
                            add_not_empty(event, 'order-item-tag', event_xml, 'item_tag')

                    status = self.send_request(_VIEWS.get(type), json.dumps(result))
                    if status != SE_SUCCESS:
                        return status
            except:
                logger.exception('[%s] Unable to process event.' % _SERVICE_NAME)
                return SE_BADRESPONSE

        return SE_SUCCESS


def main():
    """ main()
    Main entry point of the component
    """
    try:
        logger.info('Starting Boh Pump Client component ...')
        bohimpl = _BohPumpImpl()
        logger.info('Boh Pump Client component was started with success. Running ...')
        bohimpl.start()
        logger.info('Boh Pump Client component finished.')
    except KeyboardInterrupt:
        sys.exit(SE_USERCANCEL)
