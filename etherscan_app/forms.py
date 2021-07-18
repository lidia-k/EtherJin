from django import forms

class FolderSelectionForm(forms.Form):
    folder = forms.ModelChoiceField(queryset=None)

    def __init__(self, folders, *args, **kwargs):
        super(FolderSelectionForm, self).__init__(*args, **kwargs)
        self.fields['folder'].queryset = folders.values_list('folder', flat=True)

class FolderCreationFrom(forms.Form):
    folder = forms.CharField(label='List name', max_length=50)