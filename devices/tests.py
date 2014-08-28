#coding: utf8

import json
import django.test
from django.db.utils import IntegrityError
from django.forms import ValidationError

from stjornbord import settings

AUTH = {'secret': settings.SYNC_SECRET}

class DeviceExportTest(django.test.TestCase):
    fixtures = ["demo_data.json", ]

    def testExportNoSyncSecret(self):
        response = self.client.get("/devices/export/")
        self.assertEqual(response.status_code, 403)
        self.assertTrue("Invalid SYNC_SECRET" in response.content)


    def testExport(self):
        response = self.client.post("/devices/export/", AUTH)
        self.assertEqual(response.status_code, 200)


    def testExportPlain(self):
        response = self.client.post("/devices/export/", AUTH)
        self.assertEqual(response.status_code, 200)

        devices = response.content.strip().split("\n")
        self.assertTrue(len(devices) > 1)

        for device in devices:
            fields = device.split("|")
            self.assertEqual(4, len(fields))


    def testExportJSON(self):
        response = self.client.post("/devices/export/json/", AUTH)
        self.assertEqual(response.status_code, 200)

        devices = json.loads(response.content)
        self.assertTrue(len(devices) > 1)

        for device in devices:
            self.assertTrue("ip" in device)
            self.assertTrue("hwaddr" in device)
            self.assertTrue("fqdn" in device)
            self.assertTrue("domain" in device)

