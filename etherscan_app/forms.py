from django import forms


class AddressSearchForm(forms.Form):
    address = forms.CharField(label="Address", max_length=50)
class FolderSelectionForm(forms.Form):
    folder = forms.ChoiceField(choices=())

    def __init__(self, folders, *args, **kwargs):
        super(FolderSelectionForm, self).__init__(*args, **kwargs)
        folder_choices = []
        for folder in folders: 
            folder_choice = (folder.id, folder.folder_name)
            folder_choices.append(folder_choice)
        self.fields['folder'].choices = folder_choices

class FolderCreationFrom(forms.Form):
    folder = forms.CharField(label='Folder name', max_length=50)

class FolderRenameForm(forms.Form):
    folder_name = forms.CharField(label='New name', max_length=50)

class AliasCreationForm(forms.Form):
    alias = forms.CharField(label='Alias', max_length=20)