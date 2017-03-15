from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.db.models import ImageField

from . import abs, defaults

if defaults.USE_DEFAULT_DOCUMENT_MODEL:
    class DefaultDocument(abs.AbstractDocument):
        class Meta(abs.AbstractDocument.Meta):
            abstract = False
            db_table = 'pc_doc'


if defaults.USE_DEFAULT_DOCUMENT_PROVIDER_MODEL:
    from spicy.core.service.models import ContentProviderModel

    class DefaultDocumentProviderModel(ContentProviderModel):
        title = models.CharField(_('Title'), max_length=255, blank=True)
        url = models.CharField(_('Url'), max_length=255, blank=True)
        block_html_class = models.CharField(
            _('HTML class'), max_length=255, blank=True, null=True)

        def delete(self, *args, **kwargs):
            self.documentproviderrelateddoc_set.all().delete()
            return super(
                DefaultDocumentProviderModel, self).delete(*args, **kwargs)

        class Meta:
            db_table = 'pc_doc_provider'


if defaults.USE_DEFAULT_DOCUMENT_PROVIDER_RELATED_DOC_MODEL:
    class DefaultDocumentProviderRelatedDoc(abs.AbstractRelatedDocument):
        arrow_up = models.BooleanField(_('Arrow up'), default=False)
        number = models.IntegerField(_('Number'), default=0)

        provider = models.ForeignKey(
            defaults.CUSTOM_DOCUMENT_PROVIDER_MODEL)

        class Meta:
            db_table = 'pc_doc_provider_docs'
            ordering = ['order_lv']
            unique_together = (('provider', 'doc'),)
