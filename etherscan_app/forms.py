from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column


class FolderSelectionForm(forms.Form):
    folder = forms.ChoiceField(choices=())
    address = forms.CharField(max_length=60, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(FolderSelectionForm, self).__init__(*args)
        folder_choices = []
        folders = kwargs.get("folders")
        for folder in folders:
            folder_choice = (folder.id, folder.name)
            folder_choices.append(folder_choice)
        self.fields["folder"].choices = folder_choices
        self.fields["folder"].widget.attrs.update(style="max-width: 25%")
        self.fields["address"].initial = kwargs.get("address")
        
        self.helper = FormHelper()
        self.helper.add_input(Submit("save", "Save", css_class="btn-primary"))
        self.helper.form_method = "POST"


class FolderCreationFrom(forms.Form):
    folder = forms.CharField(label="Folder name", max_length=50)
    public = forms.ChoiceField(choices=())
    address = forms.CharField(max_length=60, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        submit_text = kwargs.get("submit_text", "Create")
        super(FolderCreationFrom, self).__init__(*args)
        self.fields["address"].initial = kwargs.get("address")
        public_choices = [("True", "Public"), ("False", "Private")]
        self.fields["public"].choices = public_choices
        self.fields["public"].widget.attrs.update(style="max-width: 50%")
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('folder'),
                Column('public')
            )
        )
        self.helper.add_input(Submit("create", submit_text, css_class="btn-primary"))
        self.helper.form_method = "POST"


class FolderRenameForm(forms.Form):
    name = forms.CharField(label="New name", max_length=50)

    def __init__(self, *args, **kwargs):
        super(FolderRenameForm, self).__init__(*args, **kwargs)
        self.fields["name"].widget.attrs.update(style="max-width: 25%")

        self.helper = FormHelper()
        self.helper.add_input(Submit("save", "Save", css_class="btn-primary"))
        self.helper.form_method = "POST"


class AliasCreationForm(forms.Form):
    alias = forms.CharField(label="Alias", max_length=20)
    address = forms.CharField(max_length=60, widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super(AliasCreationForm, self).__init__(*args)
        self.fields["alias"].widget.attrs.update(style="max-width: 25%")
        self.fields["address"].initial = kwargs.get("address")
        self.helper = FormHelper()
        self.helper.add_input(Submit("submit", "Submit", css_class="btn-primary"))
        self.helper.form_method = "POST"
