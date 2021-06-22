from django import forms
from django.contrib import admin
from django.contrib.contenttypes.models import ContentType

from utilities.forms import ContentTypeChoiceField, ContentTypeMultipleChoiceField, LaxURLField
from .models import CustomLink, ExportTemplate, JobResult, Webhook
from .utils import FeatureQuery


#
# Webhooks
#

class WebhookForm(forms.ModelForm):
    content_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('webhooks')
    )
    payload_url = LaxURLField(
        label='URL'
    )

    class Meta:
        model = Webhook
        exclude = ()


@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'models', 'payload_url', 'http_content_type', 'enabled', 'type_create', 'type_update', 'type_delete',
        'ssl_verification',
    ]
    list_filter = [
        'enabled', 'type_create', 'type_update', 'type_delete', 'content_types',
    ]
    form = WebhookForm
    fieldsets = (
        (None, {
            'fields': ('name', 'content_types', 'enabled')
        }),
        ('Events', {
            'fields': ('type_create', 'type_update', 'type_delete')
        }),
        ('HTTP Request', {
            'fields': (
                'payload_url', 'http_method', 'http_content_type', 'additional_headers', 'body_template', 'secret',
            ),
            'classes': ('monospace',)
        }),
        ('SSL', {
            'fields': ('ssl_verification', 'ca_file_path')
        })
    )

    def models(self, obj):
        return ', '.join([ct.name for ct in obj.content_types.all()])


#
# Custom links
#

class CustomLinkForm(forms.ModelForm):
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_links')
    )

    class Meta:
        model = CustomLink
        exclude = []
        widgets = {
            'link_text': forms.Textarea,
            'link_url': forms.Textarea,
        }
        help_texts = {
            'weight': 'A numeric weight to influence the ordering of this link among its peers. Lower weights appear '
                      'first in a list.',
            'link_text': 'Jinja2 template code for the link text. Reference the object as <code>{{ obj }}</code>. '
                         'Links which render as empty text will not be displayed.',
            'link_url': 'Jinja2 template code for the link URL. Reference the object as <code>{{ obj }}</code>.',
        }


@admin.register(CustomLink)
class CustomLinkAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Custom Link', {
            'fields': ('content_type', 'name', 'group_name', 'weight', 'button_class', 'new_window')
        }),
        ('Templates', {
            'fields': ('link_text', 'link_url'),
            'classes': ('monospace',)
        })
    )
    list_display = [
        'name', 'content_type', 'group_name', 'weight',
    ]
    list_filter = [
        'content_type',
    ]
    form = CustomLinkForm


#
# Export templates
#

class ExportTemplateForm(forms.ModelForm):
    content_type = ContentTypeChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=FeatureQuery('custom_links')
    )

    class Meta:
        model = ExportTemplate
        exclude = []


@admin.register(ExportTemplate)
class ExportTemplateAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Export Template', {
            'fields': ('content_type', 'name', 'description', 'mime_type', 'file_extension', 'as_attachment')
        }),
        ('Content', {
            'fields': ('template_code',),
            'classes': ('monospace',)
        })
    )
    list_display = [
        'name', 'content_type', 'description', 'mime_type', 'file_extension', 'as_attachment',
    ]
    list_filter = [
        'content_type',
    ]
    form = ExportTemplateForm


#
# Reports
#

@admin.register(JobResult)
class JobResultAdmin(admin.ModelAdmin):
    list_display = [
        'obj_type', 'name', 'created', 'completed', 'user', 'status',
    ]
    fields = [
        'obj_type', 'name', 'created', 'completed', 'user', 'status', 'data', 'job_id'
    ]
    list_filter = [
        'status',
    ]
    readonly_fields = fields

    def has_add_permission(self, request):
        return False
