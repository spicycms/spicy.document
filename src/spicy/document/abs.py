import datetime
import re
import os
import time
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.forms import ValidationError
from django.utils.html import strip_tags
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from spicy.core.profile.defaults import CUSTOM_USER_MODEL
from spicy.core.service import api, models as service_models
from spicy.core.trash.models import TrashModel, NonTrashManager
from spicy.utils import strip_invalid_chars, cached_property, make_slug
from spicy.redactor.utils import render_plugins
from urllib2 import urlparse
from . import defaults, parsers


class PubManager(NonTrashManager, CurrentSiteManager):

    def get_query_set(self):
        return super(PubManager, self).get_query_set().filter(
            is_public=True, pub_date__lte=datetime.datetime.now())


class AbstractDocument(
        TrashModel, service_models.CustomAbstractModel):
    owner = models.ForeignKey(
        CUSTOM_USER_MODEL, verbose_name=_('Owner'),
        blank=True, null=True,
        related_name='%(app_label)s_%(class)ss_articles')
    pub_date = models.DateTimeField(
        _('Publication date'), blank=False, null=False)
    is_public = models.BooleanField(_('Is public'), default=False)
    enable_comments = models.BooleanField(_('enable comments'), default=False)
    is_sitemap = models.BooleanField(
        default=False, verbose_name=_('Do not add this page to sitemap.xml'))
    registration_required = models.BooleanField(
        _('registration required'),
        help_text=_(
            "If this is checked, only logged-in users will be able to view "
            "the page."),
        default=False)
    title = models.CharField(
        _('Title'), max_length=255, blank=True, null=False)
    slug = models.SlugField(_('Slug'), max_length=255, blank=False, null=False)
    draft = models.TextField(_('Draft & sources'), blank=True)
    body = models.TextField(_('Document body'), blank=True)
    rendered_body = models.TextField(
        _('Rendered document body (Publication text)'), blank=True)
    site = models.ManyToManyField(
        Site, blank=True, related_name='%(app_label)s_%(class)ss_site')
    origin = models.ForeignKey(
        Site, related_name='%(app_label)s_%(class)ss_origin',
        default=settings.SITE_ID)
    preview_shown = models.BooleanField(default=True)

    # mediacenter app
    photos_has_been_attached = models.BooleanField(
        _('Photos have been attached'), default=False)
    videos_has_been_attached = models.BooleanField(
        _('Videos have been attached'), default=False)
    audios_has_been_attached = models.BooleanField(
        _('Audios have been attached'), default=False)

    # comments app
    views_cnt = models.PositiveIntegerField(
        _('Views counter'), blank=True, default=0)
    comments_cnt = models.IntegerField(
        _('Comments counter'), default=0, blank=True)

    on_site = CurrentSiteManager(field_name='site')
    objects = NonTrashManager()
    pub_objects = PubManager()

    def get_main_content(self):
        # For spicy.seo
        return self.body

    def check_public(self):
        from django.utils.timezone import now
        if self.pub_date > now():
            return False
        return self.is_public

    @cached_property
    def get_rubric_template(self):
        return os.path.join(
            defaults.DOCUMENT_TEMPLATES_PATH, 'doc_default_base.html')

    @cached_property
    def get_template(self):
        return os.path.join(defaults.DOCUMENT_TEMPLATES_PATH, 'default.html')

    @cached_property
    def get_title(self):
        return self.title

    def save(self, *args, **kwargs):
        return super(AbstractDocument, self).save(*args, **kwargs)

    @cached_property
    def includes(self):
        return api.register['media'][self].get_instances(
            self, view_type='include')

    def render_body(self):
        return render_plugins(self, 'body')

    def strip_tags_body(self):
        body = strip_tags(self.body)
        if body == 'None':
            body = ''
        content_re = re.compile(
            "\[inc\s.+\]")
        result = content_re.sub('', strip_invalid_chars(body))
        return mark_safe(result)

    def render_body_no_includes(self):
        content_re = re.compile("\[inc\s.+\]")
        return content_re.sub('', strip_invalid_chars(self.body))

    def render_body_for_rss(self):
        body = self.render_body()
        return body

    def short_pub_date(self):
        today = datetime.date.today()
        return self.pub_date.strftime(
            '%H:%M' if self.pub_date.date() == today
            else '%d / %m')

    def get_first_paragraph(self):
        parser = parsers.StrippingParagraphHTMLParser()
        parser.feed(self.render_body_no_includes())
        parser.close()
        if parser.paragraphs:
            return parser.paragraphs[0]
        else:
            return ""

    # TODO: cache this?
    def get_body_paragraphes(self):
        """
        Returnes all paragraphes in document body that has id.
        Result is a dictinary with paragraph_id as a key
        and paragraph data as value.
        """
        parser = parsers.ParagraphHTMLParser()
        parser.feed(self.render_body())
        parser.close()
        return parser.paragraphs

    def get_body_paragraph(self, paragraph_id):
        try:
            return self.get_body_paragraphes()[paragraph_id]
        except KeyError:
            return None

    def get_all_paragraph(self):
        parser = parsers.StrippingParagraphHTMLParser()
        parser.feed(self.render_body())
        parser.close()
        if parser.paragraphs:
            return parser.paragraphs
        else:
            return ""

    def get_comments_cnt(self):
        if self.forum_topic:
            return self.forum_topic.comments_cnt
        else:
            return 0

    @cached_property
    def comments(self):
        return api.register['comment'][self].get_instances(self)

    @cached_property
    def comments_for_paragraph(self, paragraph_id):
        return api.register['comment'][self].get_instances(self)

    @models.permalink
    def get_absolute_url(self, pub_point=None):
        return ('document:public:doc', (), {'doc_id': self.pk})

    def __unicode__(self):
        return u'[%s] %s' % (
            (self.pub_date.strftime('%Y/%m/%d %H:%M') if self.pub_date else
             'not published'), self.title)

    def validate_unique(self, exclude=None):
        try:
            super(AbstractDocument, self).validate_unique(exclude)
        except ValidationError, error:
            errors = error.message_dict
        else:
            errors = {}

        if not exclude or not 'slug' in exclude:
            if self.__class__.objects.filter(
                    pub_date__year=self.pub_date.year,
                    pub_date__month=self.pub_date.month,
                    pub_date__day=self.pub_date.day,
                    slug=self.slug).exclude(pk=self.pk).exists():
                slug_errors = errors.get('slug', [])
                slug_errors.append(_(
                    'Document with the same slug, publication date and issue '
                    'already exists.'))
                errors['slug'] = slug_errors

        if errors:
            raise ValidationError(errors)

    def delete(self, *args, **kwargs):
        if self.is_deleted or not kwargs.get('trash', True):
            media_prov = api.register['media'].get_provider(self)
            media_prov.get_instances(self).delete()
        return super(AbstractDocument, self).delete(*args, **kwargs)

    def create_slug(self):
        """
        Create a unique slug for current online doc or article.
        """
        base_slug = make_slug(self.title)
        date = self.pub_date
        for i in xrange(defaults.MAX_SLUG_ATTEMPTS):
            slug = base_slug if i == 0 else ('%s_%i' % (base_slug, i))
            filters = dict(
                slug=slug, pub_date__year=date.year,
                pub_date__month=date.month, pub_date__day=date.day)

            if not self.__class__.objects.filter(**filters).exclude(
                    pk=self.pk).exists():
                break
        else:
            # The impossible happened - can't find a unique slug. Use current
            # time in milliseconds for slug.
            slug = unicode(time.time()).replace('.', '')
        self.slug = slug

    @cached_property
    def next(self):
        try:
            return self.__class__.pub_objects.filter(
                pk__gt=self.pk).order_by('id')[0]
        except IndexError:
            return None

    @cached_property
    def prev(self):
        try:
            return self.__class__.pub_objects.filter(
                pk__lt=self.pk).order_by('-id')[0]
        except IndexError:
            return None

    class Meta:
        db_table = 'pc_doc'
        ordering = ['-pub_date']
        verbose_name = _('Document')
        abstract = True
        permissions = (
            ('change_media', _('Change media')),
        )


class AbstractRelatedDocument(models.Model):
    #provider = models.ForeignKey(DefineYourProviderModel)
    title = models.CharField(_('Title'), max_length=255, blank=True)
    url = models.CharField(_('Url'), max_length=255, blank=True)
    order_lv = models.IntegerField(_('Order level'), default=0)
    doc = models.ForeignKey(
        defaults.CUSTOM_DOCUMENT_MODEL, related_name='%(class)ss',
        null=True, blank=True)
    is_public = models.BooleanField(_('Is public'), default=False)

    class Meta:
        ordering = ['-order_lv']
        abstract = True
