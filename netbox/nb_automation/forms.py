from django import forms

class ExcelRegionImportForm(forms.Form):
    file = forms.FileField(
        label='Excel (.xlsx) with Region column',
        help_text='Загрузите .xlsx с заголовком столбца "Region"',
        widget=forms.ClearableFileInput(attrs={'accept': '.xlsx'})
    )
    dry_run = forms.BooleanField(
        label='Пробный прогон (без записи)',
        required=False,
        initial=False
    )
