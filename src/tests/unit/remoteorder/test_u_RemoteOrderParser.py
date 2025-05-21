# encoding: utf-8

import unittest
from datetime import datetime, tzinfo
from dateutil import tz
from remoteorder import RemoteOrderParser, InvalidJsonException


class ParseOrderTestCase(unittest.TestCase):
    def test_InvalidJson_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        invalid_json = u"{asdf]"
        try:
            remote_order_parser.parse_order(invalid_json)
            self.fail()
        except InvalidJsonException as ex:
            pass

    def test_ValidJsonAllFields_CorrectRemoteOrderReturned(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        remote_order = remote_order_parser.parse_order(valid_json)
        self.assertEqual(remote_order.id, u"21861")
        self.assertEqual(len(remote_order.tenders), 1)
        self.assertEqual(remote_order.tenders[0].type, u"online")
        self.assertEqual(remote_order.tenders[0].value, 23.9)
        self.assertEqual(len(remote_order.items), 1)
        self.assertEqual(remote_order.items[0].part_code, u"1051")
        self.assertEqual(remote_order.items[0].quantity, 1)
        self.assertEqual(len(remote_order.items[0].parts), 2)
        self.assertEqual(remote_order.items[0].parts[0].part_code, u"6012")
        self.assertEqual(remote_order.items[0].parts[0].quantity, 1)
        self.assertEqual(remote_order.items[0].parts[1].part_code, u"9008")
        self.assertEqual(remote_order.items[0].parts[1].quantity, 1)
        self.assertEqual(len(remote_order.custom_properties), 2)
        self.assertTrue(u"customer_name" in remote_order.custom_properties, u"customer_name not present in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_name"].value, u"Eduardo")
        self.assertTrue(u"customer_document" in remote_order.custom_properties, u"customer_document not present in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_document"].value, u"32695871805")
        self.assertEqual(remote_order.pickup.time, datetime(2017, 9, 1, 18, 10, 10, 0, tz.tzutc()))
        self.assertEqual(remote_order.pickup.company, u"Logg")
        self.assertEqual(remote_order.pickup.address.formattedAddress, u"Avenida Tucunaré, 1140, AP 64M")
        self.assertEqual(remote_order.pickup.address.streetName, u"Avenida Tucunaré")
        self.assertEqual(remote_order.pickup.address.streetNumber, u"1140")
        self.assertEqual(remote_order.pickup.address.complement, u"AP 64M")
        self.assertEqual(remote_order.pickup.address.neighborhood, u"Tamboré")
        self.assertEqual(remote_order.pickup.address.reference, u"Mackenzie")
        self.assertEqual(remote_order.pickup.address.city, u"Barueri")
        self.assertEqual(remote_order.pickup.address.state, u"SP")
        self.assertEqual(remote_order.pickup.address.postalCode, u"06460020")
        self.assertEqual(remote_order.pickup.address.country, u"Brasil")
        self.assertEqual(remote_order.pickup.address.latitude, -9.824966)
        self.assertEqual(remote_order.pickup.address.longitude, -67.949965)

    def test_ValidJsonNoAddress_CorrectRemoteOrderReturned(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg"
        }
    }"""

        remote_order = remote_order_parser.parse_order(valid_json)
        self.assertEqual(remote_order.id, u"21861")
        self.assertEqual(len(remote_order.tenders), 1)
        self.assertEqual(remote_order.tenders[0].type, u"online")
        self.assertEqual(remote_order.tenders[0].value, 23.9)
        self.assertEqual(len(remote_order.items), 1)
        self.assertEqual(remote_order.items[0].part_code, u"1051")
        self.assertEqual(remote_order.items[0].quantity, 1)
        self.assertEqual(len(remote_order.items[0].parts), 2)
        self.assertEqual(remote_order.items[0].parts[0].part_code, u"6012")
        self.assertEqual(remote_order.items[0].parts[0].quantity, 1)
        self.assertEqual(remote_order.items[0].parts[1].part_code, u"9008")
        self.assertEqual(remote_order.items[0].parts[1].quantity, 1)
        self.assertEqual(len(remote_order.custom_properties), 2)
        self.assertTrue(u"customer_name" in remote_order.custom_properties, u"customer_name not in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_name"].value, u"Eduardo")
        self.assertTrue(u"customer_document" in remote_order.custom_properties, u"customer_document not in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_document"].value, u"32695871805")
        self.assertEqual(remote_order.pickup.time, datetime(2017, 9, 1, 18, 10, 10, 0, tz.tzutc()))
        self.assertEqual(remote_order.pickup.company, u"Logg")
        self.assertEqual(remote_order.pickup.address, None)

    def test_ValidJsonNoCustomProperties_CorrectRemoteOrderReturned(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        remote_order = remote_order_parser.parse_order(valid_json)
        self.assertEqual(remote_order.id, u"21861")
        self.assertEqual(len(remote_order.tenders), 1)
        self.assertEqual(remote_order.tenders[0].type, u"online")
        self.assertEqual(remote_order.tenders[0].value, 23.9)
        self.assertEqual(len(remote_order.items), 1)
        self.assertEqual(remote_order.items[0].part_code, u"1051")
        self.assertEqual(remote_order.items[0].quantity, 1)
        self.assertEqual(len(remote_order.items[0].parts), 2)
        self.assertEqual(remote_order.items[0].parts[0].part_code, u"6012")
        self.assertEqual(remote_order.items[0].parts[0].quantity, 1)
        self.assertEqual(remote_order.items[0].parts[1].part_code, u"9008")
        self.assertEqual(remote_order.items[0].parts[1].quantity, 1)
        self.assertEqual(len(remote_order.custom_properties), 0)
        self.assertEqual(remote_order.pickup.time, datetime(2017, 9, 1, 18, 10, 10, 0, tz.tzutc()))
        self.assertEqual(remote_order.pickup.company, u"Logg")
        self.assertEqual(remote_order.pickup.address.formattedAddress, u"Avenida Tucunaré, 1140, AP 64M")
        self.assertEqual(remote_order.pickup.address.streetName, u"Avenida Tucunaré")
        self.assertEqual(remote_order.pickup.address.streetNumber, u"1140")
        self.assertEqual(remote_order.pickup.address.complement, u"AP 64M")
        self.assertEqual(remote_order.pickup.address.neighborhood, u"Tamboré")
        self.assertEqual(remote_order.pickup.address.reference, u"Mackenzie")
        self.assertEqual(remote_order.pickup.address.city, u"Barueri")
        self.assertEqual(remote_order.pickup.address.state, u"SP")
        self.assertEqual(remote_order.pickup.address.postalCode, u"06460020")
        self.assertEqual(remote_order.pickup.address.country, u"Brasil")
        self.assertEqual(remote_order.pickup.address.latitude, -9.824966)
        self.assertEqual(remote_order.pickup.address.longitude, -67.949965)

    def test_ValidJsonEmptyCustomProperties_CorrectRemoteOrderReturned(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        remote_order = remote_order_parser.parse_order(valid_json)
        self.assertEqual(remote_order.id, u"21861")
        self.assertEqual(len(remote_order.tenders), 1)
        self.assertEqual(remote_order.tenders[0].type, u"online")
        self.assertEqual(remote_order.tenders[0].value, 23.9)
        self.assertEqual(len(remote_order.items), 1)
        self.assertEqual(remote_order.items[0].part_code, u"1051")
        self.assertEqual(len(remote_order.items[0].parts), 2)
        self.assertEqual(remote_order.items[0].parts[0].part_code, u"6012")
        self.assertEqual(remote_order.items[0].parts[0].quantity, 1)
        self.assertEqual(remote_order.items[0].parts[1].part_code, u"9008")
        self.assertEqual(remote_order.items[0].parts[1].quantity, 1)
        self.assertEqual(len(remote_order.custom_properties), 0)
        self.assertEqual(remote_order.pickup.time, datetime(2017, 9, 1, 18, 10, 10, 0, tz.tzutc()))
        self.assertEqual(remote_order.pickup.company, u"Logg")
        self.assertEqual(remote_order.pickup.address.formattedAddress, u"Avenida Tucunaré, 1140, AP 64M")
        self.assertEqual(remote_order.pickup.address.streetName, u"Avenida Tucunaré")
        self.assertEqual(remote_order.pickup.address.streetNumber, u"1140")
        self.assertEqual(remote_order.pickup.address.complement, u"AP 64M")
        self.assertEqual(remote_order.pickup.address.neighborhood, u"Tamboré")
        self.assertEqual(remote_order.pickup.address.reference, u"Mackenzie")
        self.assertEqual(remote_order.pickup.address.city, u"Barueri")
        self.assertEqual(remote_order.pickup.address.state, u"SP")
        self.assertEqual(remote_order.pickup.address.postalCode, u"06460020")
        self.assertEqual(remote_order.pickup.address.country, u"Brasil")
        self.assertEqual(remote_order.pickup.address.latitude, -9.824966)
        self.assertEqual(remote_order.pickup.address.longitude, -67.949965)

    def test_ValidJsonNoParts_CorrectRemoteOrderReturned(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        remote_order = remote_order_parser.parse_order(valid_json)
        self.assertEqual(remote_order.id, u"21861")
        self.assertEqual(len(remote_order.tenders), 1)
        self.assertEqual(remote_order.tenders[0].type, u"online")
        self.assertEqual(remote_order.tenders[0].value, 23.9)
        self.assertEqual(len(remote_order.items), 1)
        self.assertEqual(remote_order.items[0].part_code, u"1051")
        self.assertEqual(remote_order.items[0].quantity, 1)
        self.assertEqual(len(remote_order.items[0].parts), 0)
        self.assertEqual(len(remote_order.custom_properties), 2)
        self.assertTrue(u"customer_name" in remote_order.custom_properties, u"customer_name not in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_name"].value, u"Eduardo")
        self.assertTrue(u"customer_document" in remote_order.custom_properties, u"customer_document not in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_document"].value, u"32695871805")
        self.assertEqual(remote_order.pickup.time, datetime(2017, 9, 1, 18, 10, 10, 0, tz.tzutc()))
        self.assertEqual(remote_order.pickup.company, u"Logg")
        self.assertEqual(remote_order.pickup.address.formattedAddress, u"Avenida Tucunaré, 1140, AP 64M")
        self.assertEqual(remote_order.pickup.address.streetName, u"Avenida Tucunaré")
        self.assertEqual(remote_order.pickup.address.streetNumber, u"1140")
        self.assertEqual(remote_order.pickup.address.complement, u"AP 64M")
        self.assertEqual(remote_order.pickup.address.neighborhood, u"Tamboré")
        self.assertEqual(remote_order.pickup.address.reference, u"Mackenzie")
        self.assertEqual(remote_order.pickup.address.city, u"Barueri")
        self.assertEqual(remote_order.pickup.address.state, u"SP")
        self.assertEqual(remote_order.pickup.address.postalCode, u"06460020")
        self.assertEqual(remote_order.pickup.address.country, u"Brasil")
        self.assertEqual(remote_order.pickup.address.latitude, -9.824966)
        self.assertEqual(remote_order.pickup.address.longitude, -67.949965)

    def test_ValidJsonNoAddressFields_CorrectRemoteOrderReturned(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {}
        }
    }"""

        remote_order = remote_order_parser.parse_order(valid_json)
        self.assertEqual(remote_order.id, u"21861")
        self.assertEqual(len(remote_order.tenders), 1)
        self.assertEqual(remote_order.tenders[0].type, u"online")
        self.assertEqual(remote_order.tenders[0].value, 23.9)
        self.assertEqual(len(remote_order.items), 1)
        self.assertEqual(remote_order.items[0].part_code, u"1051")
        self.assertEqual(remote_order.items[0].quantity, 1)
        self.assertEqual(len(remote_order.items[0].parts), 2)
        self.assertEqual(remote_order.items[0].parts[0].part_code, u"6012")
        self.assertEqual(remote_order.items[0].parts[0].quantity, 1)
        self.assertEqual(remote_order.items[0].parts[1].part_code, u"9008")
        self.assertEqual(remote_order.items[0].parts[1].quantity, 1)
        self.assertEqual(len(remote_order.custom_properties), 2)
        self.assertTrue(u"customer_name" in remote_order.custom_properties, u"customer_name not in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_name"].value, u"Eduardo")
        self.assertTrue(u"customer_document" in remote_order.custom_properties, u"customer_document not in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_document"].value, u"32695871805")
        self.assertEqual(remote_order.pickup.time, datetime(2017, 9, 1, 18, 10, 10, 0, tz.tzutc()))
        self.assertEqual(remote_order.pickup.company, u"Logg")
        self.assertIsNone(remote_order.pickup.address.formattedAddress)
        self.assertIsNone(remote_order.pickup.address.streetName)
        self.assertIsNone(remote_order.pickup.address.streetNumber)
        self.assertIsNone(remote_order.pickup.address.complement)
        self.assertIsNone(remote_order.pickup.address.neighborhood)
        self.assertIsNone(remote_order.pickup.address.reference)
        self.assertIsNone(remote_order.pickup.address.city)
        self.assertIsNone(remote_order.pickup.address.state)
        self.assertIsNone(remote_order.pickup.address.state)
        self.assertIsNone(remote_order.pickup.address.country)
        self.assertIsNone(remote_order.pickup.address.latitude)
        self.assertIsNone(remote_order.pickup.address.longitude)

    def test_ValidJsonGeoLocationWithoutFields_CorrectRemoteOrderReturned(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil"
            }
        }
    }"""

        remote_order = remote_order_parser.parse_order(valid_json)
        self.assertEqual(remote_order.id, u"21861")
        self.assertEqual(len(remote_order.tenders), 1)
        self.assertEqual(remote_order.tenders[0].type, u"online")
        self.assertEqual(remote_order.tenders[0].value, 23.9)
        self.assertEqual(len(remote_order.items), 1)
        self.assertEqual(remote_order.items[0].part_code, u"1051")
        self.assertEqual(remote_order.items[0].quantity, 1)
        self.assertEqual(len(remote_order.items[0].parts), 2)
        self.assertEqual(remote_order.items[0].parts[0].part_code, u"6012")
        self.assertEqual(remote_order.items[0].parts[0].quantity, 1)
        self.assertEqual(remote_order.items[0].parts[1].part_code, u"9008")
        self.assertEqual(remote_order.items[0].parts[1].quantity, 1)
        self.assertEqual(len(remote_order.custom_properties), 2)
        self.assertTrue(u"customer_name" in remote_order.custom_properties, u"customer_name not in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_name"].value, u"Eduardo")
        self.assertTrue(u"customer_document" in remote_order.custom_properties, u"customer_document not in custom_properties")
        self.assertEqual(remote_order.custom_properties[u"customer_document"].value, u"32695871805")
        self.assertEqual(remote_order.pickup.time, datetime(2017, 9, 1, 18, 10, 10, 0, tz.tzutc()))
        self.assertEqual(remote_order.pickup.company, u"Logg")
        self.assertEqual(remote_order.pickup.address.formattedAddress, u"Avenida Tucunaré, 1140, AP 64M")
        self.assertEqual(remote_order.pickup.address.streetName, u"Avenida Tucunaré")
        self.assertEqual(remote_order.pickup.address.streetNumber, u"1140")
        self.assertEqual(remote_order.pickup.address.complement, u"AP 64M")
        self.assertEqual(remote_order.pickup.address.neighborhood, u"Tamboré")
        self.assertEqual(remote_order.pickup.address.reference, u"Mackenzie")
        self.assertEqual(remote_order.pickup.address.city, u"Barueri")
        self.assertEqual(remote_order.pickup.address.state, u"SP")
        self.assertEqual(remote_order.pickup.address.postalCode, u"06460020")
        self.assertEqual(remote_order.pickup.address.country, u"Brasil")
        self.assertIsNone(remote_order.pickup.address.latitude)
        self.assertIsNone(remote_order.pickup.address.longitude)

    def test_InvalidJsonNoIdTag_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        no_id_json = u"""{
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""
        try:
            remote_order_parser.parse_order(no_id_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Json without id tag")

    def test_InvalidJsonNoTendersTag_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        no_tenders_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""
        try:
            remote_order_parser.parse_order(no_tenders_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Json without tenders tag")

    def test_InvalidJsonEmptyTenders_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        no_tenders_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "tenders": [],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""
        try:
            remote_order_parser.parse_order(no_tenders_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Json with empty tenders tag")

    def test_InvalidJsonTenderWithoutType_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        no_tenders_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "tenders": [{
            "value": 23.9
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""
        try:
            remote_order_parser.parse_order(no_tenders_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Tender without type")

    def test_InvalidJsonTenderWithoutValue_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        no_tenders_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "tenders": [{
            "type": "online"
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""
        try:
            remote_order_parser.parse_order(no_tenders_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Tender without value")

    def test_InvalidJsonTenderWithInvalidType_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        no_tenders_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "tenders": [{
            "type": "invalid",
            "value": 23.9
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""
        try:
            remote_order_parser.parse_order(no_tenders_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Invalid tender type: invalid")

    def test_InvalidJsonNoPickUp_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }]
    }"""

        try:
            remote_order_parser.parse_order(valid_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Json without pickup tag")

    def test_InvalidJsonPickupWithNoTime_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        try:
            remote_order_parser.parse_order(valid_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Pickup without time")

    def test_InvalidJsonNoItems_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        try:
            remote_order_parser.parse_order(valid_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Json without items tag")

    def test_InvalidJsonEmptyItems_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        try:
            remote_order_parser.parse_order(valid_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Json with empty items tag")

    def test_InvalidJsonItemWihtoutPartCode_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        try:
            remote_order_parser.parse_order(valid_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Items without partCode")

    def test_InvalidJsonInnerItemWihtoutPartCode_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {},
                {"partCode":"9008"}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        try:
            remote_order_parser.parse_order(valid_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Items without partCode")

    def test_InvalidJsonItemWithoutQuantity_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "parts": [
                {"partCode":"9008", "quantity": 1},
                {"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        try:
            remote_order_parser.parse_order(valid_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Items without quantity")

    def test_InvalidJsonInnerItemWithoutQuantity_InvalidJsonExceptionRaised(self):
        remote_order_parser = RemoteOrderParser()
        valid_json = u"""{
        "id":"21861",
        "createAt": "2017-07-10T15:00:00.000Z",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"9008"},
                {"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        try:
            remote_order_parser.parse_order(valid_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Items without quantity")

    def test_InvalidJsonNoCreateAt_CorrectRemoteOrderReturned(self):
        remote_order_parser = RemoteOrderParser()
        invalid_json = u"""{
        "id":"21861",
        "tenders": [{
            "type":"online",
            "value": 23.9
        }],
        "items":[{
            "partCode": "1051",
            "quantity": 1,
            "parts": [
                {"partCode":"6012", "quantity": 1},{"partCode":"9008", "quantity": 1}
            ]
        }],
        "custom_properties":[
            {
            "key":"customer_name",
            "value":"Eduardo"
            }, 
            {
            "key":"customer_document",
            "value":"32695871805"
            }],
        "pickup":{
            "time":"2017-09-01T18:10:10",
            "company":"Logg",
            "address": {
                 "formattedAddress":"Avenida Tucunaré, 1140, AP 64M",
                 "streetName":"Avenida Tucunaré",
                 "streetNumber":"1140",
                 "complement":"AP 64M",
                 "neighborhood":"Tamboré",
                 "reference":"Mackenzie",
                 "city":"Barueri",
                 "state":"SP",
                 "postalCode":"06460020",
                 "country":"Brasil",
                 "latitude":-9.824966,
                 "longitude":-67.949965
            }
        }
    }"""

        try:
            remote_order_parser.parse_order(invalid_json)
            self.fail()
        except InvalidJsonException as ex:
            self.assertEqual(ex.message, "Json without createAt tag")
