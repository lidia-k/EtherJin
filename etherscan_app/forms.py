from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class AddressSearchForm(forms.Form):
    address = forms.CharField(label="Address", max_length=50)

    def __init__(self, *args, **kwargs):
        super(AddressSearchForm, self).__init__(*args, **kwargs)
        self.fields['address'].widget.attrs.update(style='max-width: 25%')

        self.helper = FormHelper()
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn-primary'))
        self.helper.form_method = 'POST'
class FolderSelectionForm(forms.Form):
    folder = forms.ModelChoiceField(queryset=None)

    def __init__(self, folders, *args, **kwargs):
        super(FolderSelectionForm, self).__init__(*args, **kwargs)
        self.fields['folder'].queryset = folders.values_list('folder_name', flat=True)
        self.fields['folder'].widget.attrs.update(style='max-width: 25%')

        self.helper = FormHelper()
        self.helper.add_input(Submit('save', 'Save', css_class='btn-primary'))
        self.helper.form_method = 'POST'
class FolderCreationFrom(forms.Form):
    folder = forms.CharField(label='Folder name', max_length=50)


    def __init__(self, *args, **kwargs):
        submit_text = kwargs.get('submit_text', 'Create')
        kwargs = {}
        super(FolderCreationFrom, self).__init__(*args, **kwargs)
        self.fields['folder'].widget.attrs.update(style='max-width: 25%')

        self.helper = FormHelper()
        self.helper.add_input(Submit('create', submit_text, css_class='btn-primary'))
        self.helper.form_method = 'POST'

class FolderRenameForm(forms.Form):

    folder_name = forms.CharField(label='New name', max_length=50)

    def __init__(self, *args, **kwargs):
        super(FolderRenameForm, self).__init__(*args, **kwargs)
        self.fields['folder_name'].widget.attrs.update(style='max-width: 25%')

        self.helper = FormHelper()
        self.helper.add_input(Submit('save', 'Save', css_class='btn-primary'))
        self.helper.form_method = 'POST'
