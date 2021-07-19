from django import forms

class AddressSearchForm(forms.Form):
    address = forms.CharField(label="Address", max_length=50)
class FolderSelectionForm(forms.Form):
    folder = forms.ModelChoiceField(queryset=None)

    def __init__(self, folders, *args, **kwargs):
        super(FolderSelectionForm, self).__init__(*args, **kwargs)
        self.fields['folder'].queryset = folders.values_list('folder', flat=True)

class FolderCreationFrom(forms.Form):
    folder = forms.CharField(label='Folder name', max_length=50)

class FolderRenameForm(forms.Form):
    folder_name = forms.CharField(label='New name', max_length=50)