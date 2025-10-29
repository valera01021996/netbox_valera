from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelBulkEditForm
from .models import APKService
from utilities.forms.rendering import FieldSet

class APKServiceForm(NetBoxModelForm):
    class Meta:
        model = APKService
        fields = ('name', 'description')


class APKServiceBulkEditForm(NetBoxModelBulkEditForm):
    model = APKService
    description = forms.CharField(required=False)
    nullable_fields = ('description',)
    fieldsets = (
        FieldSet('description', name='General'),
    )