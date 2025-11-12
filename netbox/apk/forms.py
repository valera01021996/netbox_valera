from netbox.forms import NetBoxModelForm, NetBoxModelBulkEditForm
from django import forms
from utilities.forms.rendering import FieldSet
from .models import APKName, APKEntry

class APKNameForm(NetBoxModelForm):
    class Meta:
        model = APKName
        fields = ("name", "description")

class APKNameBulkEditForm(NetBoxModelBulkEditForm):
    model = APKName
    description = forms.CharField(required=False, widget=forms.Textarea)
    fieldsets = (FieldSet("description", name="General"),)
    nullable_fields = ("description",)


class APKEntryForm(NetBoxModelForm):
    class Meta:
        model = APKEntry
        fields = (
            "apk_name", "apk_type", "operator", "contract",
            "ports_count", "capacity_mbps", "ports_type", "specs",
        )

class APKEntryBulkEditForm(NetBoxModelBulkEditForm):
    model = APKEntry
    contract = forms.CharField(required=False)
    specs = forms.CharField(required=False, widget=forms.Textarea)
    fieldsets = (FieldSet("contract", "specs", name="General"),)
    nullable_fields = ("contract", "specs")