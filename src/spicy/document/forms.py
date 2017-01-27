# -*- coding: utf-8 -*-
from . import defaults
from django import forms
from django.contrib.sites.models import Site
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext_lazy as _
from spicy.core.service import forms as service_forms
from spicy.core.siteskin.fields import SanitizingCharField
from spicy.core.siteskin.widgets import AutoCompleteChooser
from spicy.utils.models import get_custom_model_class
from ckeditor.widgets import CKEditorWidget

Document = get_custom_model_class(defaults.CUSTOM_DOCUMENT_MODEL)
DocumentProviderModel = get_custom_model_class(
    defaults.CUSTOM_DOCUMENT_PROVIDER_MODEL)
DocumentProviderRelatedDoc = get_custom_model_class(
    defaults.CUSTOM_DOCUMENT_PROVIDER_RELATED_DOC_MODEL)


class DocumentForm(forms.ModelForm):
    #title = forms.CharField(label=_('Title'), max_length=255, required=True)
    #body = SanitizingCharField(label=_('Document body'))

    class Meta:
        model = Document
        fields = ('title', 'pub_date', 'body', 'draft', 'is_public',
            'enable_comments', 'is_sitemap', 'registration_required',
            'preview', 'preview2')
        widgets = {
            'body': CKEditorWidget(),#forms.Textarea(attrs=dict(rows=20)),
            'pub_date': forms.DateTimeInput(format='%Y-%m-%d %H:%i')}


class CreateDocumentForm(DocumentForm):

    class Meta:
        model = Document
        fields = ('title', 'pub_date', 'body', 'draft', 'is_public',
            'enable_comments', 'is_sitemap', 'registration_required',
            'preview', 'preview2')
        widgets = {
            'body': CKEditorWidget(),#forms.Textarea(attrs=dict(rows=20)),
            'pub_date': forms.DateTimeInput(format='%Y-%m-%d %H:%i')}

    def save(self, *args, **kwargs):
        doc = super(CreateDocumentForm, self).save(*args, **kwargs)
        doc.create_slug()
        doc.origin = Site.objects.get_current()
        if kwargs.get('commit', True):
            doc.save()

        self.instance = doc
        return doc


class DocumentListForm(forms.ModelForm):
    order_lv = forms.IntegerField(
        label='', widget=forms.TextInput(attrs={'size': 2}))

    class Meta:
        model = Document
        fields = ('order_lv', )


class DocumentProviderForm(service_forms.ContentProviderForm):

    class Meta:
        model = DocumentProviderModel
        fields = ('title', 'url', 'template', 'block_html_class')


class DocumentProviderCreateForm(forms.ModelForm):

    class Meta:
        model = DocumentProviderModel
        exclude = ('url', 'title', 'template')


class DocumentProviderRelatedDocForm(forms.ModelForm):
    doc = forms.ModelChoiceField(
        queryset=Document.objects, widget=AutoCompleteChooser())

    def __init__(self, *args, **kwargs):
        super(DocumentProviderRelatedDocForm, self).__init__(*args, **kwargs)
        if self.instance.doc:
            self.__old_related_doc_pk = self.instance.doc.pk
        else:
            self.__old_related_doc_pk = None

    def save(self, *args, **kwargs):
        doc = super(DocumentProviderRelatedDocForm, self).save(*args, **kwargs)

        if (
                self.__old_related_doc_pk is None or
                self.__old_related_doc_pk != doc.doc.pk):
            doc.title = doc.doc.title
            doc.is_public = doc.doc.is_public
            doc.url = doc.doc.get_absolute_url()

        doc.save()
        return doc

    class Meta:
        model = DocumentProviderRelatedDoc
        #exclude = ('provider',)


class DocumentFiltersForm(forms.Form):
    search_text = forms.CharField(max_length=100, required=False)


RelatedDocumentProviderFormSet = inlineformset_factory(
    DocumentProviderModel, DocumentProviderRelatedDoc,
    form=DocumentProviderRelatedDocForm, fk_name="provider", extra=1,
    can_delete=True)


class DocumentPreviewSettingsForm(forms.ModelForm):

    class Meta:
        model = Document
        fields = 'preview_shown',
        widgets = {
            'preview_shown': forms.CheckboxInput(attrs={'class': 'icheck'})}

DocumentPreviewSettingsForm.base_fields['preview_shown'].label = _(
    'Display preview in templates')
