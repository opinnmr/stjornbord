from django import template
from stjornbord.settings import MEDIA_URL
register = template.Library()

@register.inclusion_tag('ou/filter.html', takes_context=True)
def listing_filter(context, title, filter_name):
    filter_items    = context['filter_items']
    items           = filter_items.get(filter_name, {})

    filters         = context['filters'].copy()
    value           = filters.pop(filter_name, None)

    other_filters = "&".join( ["%s=%s" % (k, v) for k, v in filters.items()] )
    
    return {
        'title': title,
        'filter_name': filter_name,
        'value': value,
        'items': items,
        'other_filters': other_filters
        }

@register.simple_tag
def append_filter(filters):
    url = ""
    for k, v in filters.items():
        url += "&%s=%s" % (k, v)
    return url