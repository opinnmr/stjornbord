# coding: utf-8
import json
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from stjornbord.devices.models import Device, Counter
from stjornbord.settings import LAN_DOMAIN
from stjornbord.utils import verify_sync_secret

@csrf_exempt
@verify_sync_secret
def export(request, fmt=None):
    devices = Device.objects.filter(active=True).select_related()

    if fmt == "json":
        return _export_json(devices)
    return _export_csv(devices)

def _export_csv(devices):
    response = HttpResponse(mimetype="text/plain")

    for device in devices:
        exp = []
        exp.append(device.hwaddr)
        exp.append(device.ipaddr)
        exp.append(device.get_fqdn())
        exp.append("%s.%s" % (device.subdomain.dns, LAN_DOMAIN))
        response.write("%s\n" % "|".join(exp))

    return response

def _export_json(devices):
    response = HttpResponse(mimetype="application/json")
    export = []
    for device in devices:
        export.append({
            "hwaddr": device.hwaddr,
            "ip": device.ipaddr,
            "fqdn": device.get_fqdn(),
            "domain": "%s.%s" % (device.subdomain.dns, LAN_DOMAIN)
        })

    json.dump(export, response)
    return response

@csrf_exempt
@verify_sync_secret
def counter(request, name):
    counter = get_object_or_404(Counter, name=name)
    response = HttpResponse(mimetype="text/plain")
    response.write(counter.value)
    return response