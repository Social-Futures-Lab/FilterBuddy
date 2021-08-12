from django import template

register = template.Library()

# Register the filters
@register.simple_tag(name='sidebar-active')
def indicate_active(current, reference_page, reference_arg = None):
  return 'active' if current['page'] == reference_page and (
    (current['collection'] is None and reference_arg is None) or
    (current['collection'].id == reference_arg.id)) else ''
