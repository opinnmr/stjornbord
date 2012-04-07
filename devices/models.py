from django.db import models
from django.forms import fields
from stjornbord.settings import LAN_DOMAIN
import re
import string
import time

IP_RANGE = (100, 200)

# Mac Address field
# http://djangosnippets.org/snippets/1337/
# Modified: enforce upper case A-F

MAC_RE = r'^([0-9A-F]{2}(:?|$)){6}$'
mac_re = re.compile(MAC_RE)

class MACAddressFormField(fields.RegexField):
    default_error_messages = {
        'invalid': u'Enter a valid MAC address.',
    }

    def __init__(self, *args, **kwargs):
        super(MACAddressFormField, self).__init__(mac_re, *args, **kwargs)

class MACAddressField(models.Field):
    empty_strings_allowed = False
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 17
        super(MACAddressField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'form_class': MACAddressFormField}
        defaults.update(kwargs)
        return super(MACAddressField, self).formfield(**defaults)

COUNTER_DEVICES = "devices"

class Counter(models.Model):
    name  = models.CharField(max_length=100)
    value = models.IntegerField()

    def __unicode__(self):
        return self.name
        
def update_counter(name):
    cnt = Counter.objects.get(name=name)
    cnt.value = time.time()
    cnt.save()

class Subdomain(models.Model):
    name = models.CharField(max_length=100)
    dns  = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.dns

class Prefix(models.Model):
    name      = models.CharField(max_length=100)
    dns       = models.CharField(max_length=20)
    subdomain = models.ForeignKey(Subdomain)
    
    def __unicode__(self):
        return self.dns

class Vlan(models.Model):
    name    = models.CharField(max_length=100)
    network = models.IPAddressField()
    
    def __unicode__(self):
        return self.name

class Device(models.Model):
    subdomain = models.ForeignKey(Subdomain)
    prefix    = models.ForeignKey(Prefix)
    vlan      = models.ForeignKey(Vlan)
    name      = models.CharField(max_length=10, blank=True)
    tag       = models.CharField(max_length=20, blank=True)
    description= models.CharField(max_length=150, blank=True)
    ipaddr    = models.IPAddressField(unique=True, blank=True)
    hwaddr    = MACAddressField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Get the first available IP address in this network
        if not self.ipaddr:
            self.ipaddr = get_next_ip(self.vlan)

        # Get the first available name with this prefix.
        if not self.name:
            self.name = get_next_name(self.prefix)
        
        update_counter(COUNTER_DEVICES)    
        
        models.Model.save(self, *args, **kwargs)

    def delete(self, *args, **kwargs):
        update_counter(COUNTER_DEVICES)    
        models.Model.delete(self, *args, **kwargs)
    
    def __unicode__(self):
        return self.get_fqdn()

    def get_fqdn(self):
        return "%s%s.%s.%s" % (self.prefix.dns, self.name, self.subdomain.dns, LAN_DOMAIN)
    
    class Meta:
        unique_together = (("subdomain", "prefix", "vlan", "name"), )

def get_next_ip(vlan):
    """
    Search through all IP address in a particular vlan and
    find the first available one, in the allowed range.
    """
    if not isinstance(vlan, Vlan):
        vlan = Vlan.objects.get(pk=vlan)

    # Search through IP addresses
    in_use = set([x.ipaddr for x in Device.objects.filter(vlan=vlan)])
    for offset in range(*IP_RANGE):
        # For some reason, django stores IP addressess as
        # unicode, so we need to so string magic
        ip = "%s.%s" % (vlan.network[:vlan.network.rindex(".")], offset)
        if ip not in in_use:
            return ip
    
    raise RuntimeException("No IP addresses left in vlan %s" % vlan)

def get_next_name(prefix):
    """
    Search through all IP address in a particular vlan and
    find the first available one, in the allowed range.
    """
    if not isinstance(prefix, Prefix):
        prefix = Prefix.objects.get(pk=prefix)

    # Search through IP addresses
    in_use = set([x.name for x in Device.objects.filter(prefix=prefix)])
    for num in range(1000):
        num = string.zfill(num, 2)
        if num not in in_use:
            return num

    raise RuntimeException("No name left in namespace %s" % prefix)




