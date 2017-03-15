# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.translation import ugettext_lazy as _


DOCUMENT_TEMPLATES_PATH = getattr(
    settings, 'DOCUMENT_TEMPLATES_PATH', 'document/templates')


DEFAULT_RSS_LEN = 25

TEXT_LENGHT = getattr(settings, 'TEXT_LENGHT', 1024*20)

SEARCH_LIMIT = getattr(settings, 'SEARCH_LIMIT', 20)

DEFAULTS_DOCS_PER_PAGE = getattr(settings, 'DEFAULTS_DOCS_PER_PAGE', 30)
RSS_TITLE = getattr(settings, 'RSS_TITLE', _("feeds RSS"))
DEFAULTS_DOCS_PER_PAGE_ALL = getattr(
    settings, 'DEFAULTS_DOCS_PER_PAGE_ALL', 40)
MAX_SUGGESTIONS = getattr(settings, 'MAX_SUGGESTIONS', 5)
# Large values may give too long cache keys.

#DEFAULTS_DOCS_PER_BLOCK = 20

SIMILAR_DOCS_BY_STORY_LIMIT = 5

DEFAULT_PUB_POINT = 'index'
PUBLICATION_POINT = (
    ('index', _('Index page title')),
    ('rss', _('Rss feed')),
    ('yandex', _('Yandex newsline'))
    )

DEFAULT_DOC_TEMPLATE = 'generic'
DOC_TEMPLATES = (
    ('generic', _('Generic doc/article/magazine/article')),
    ('gallery', _('Gallery template')),
    ('interview', _('Online interview')),
    ('telecast', _('Telecast template')),
    ('leasing', _('Leasing template')),
    ('poll', _('Poll template')),
    )

PARTNERS_BLOCKS_RIGHT = getattr(settings, 'PARTNERS_BLOCKS_RIGHT', (
    'partners-right-1',
    'partners-right-2',
    'partners-right-3',
    'partners-right-6',
))

AUTOSAVE_TIMEOUT = getattr(settings, 'AUTOSAVE_TIMEOUT', 20)

DEFAULT_DOC_PRIORITY = 'middle'
DOC_PRIORITY = (
    ('high', 'high'),
    ('middle', 'middle'),
)

DOCUMENT_PROVIDER_MODEL_HTML_CLASSES = getattr(
    settings, 'DOCUMENT_PROVIDER_MODEL_HTML_CLASSES', ())
STORIES_PER_DAY = 5


# RSS
YANDEX_RSS_LEN = 50
YANDEX_RSS_DESCRIPTION = getattr(settings, 'YANDEX_RSS_DESCRIPTION', '')
YANDEX_RSS_TITLE = getattr(settings, 'YANDEX_RSS_TITLE', '')
YANDEX_RSS_LINK = 'http://example.com/yandex/rss/'
INTERFAX_RSS_LINK = 'http://example.com/interfax/rss/'
MEDIA_RSS_TITLE = getattr(settings, 'MEDIA_RSS_TITLE', u'Media rss title')
MEDIA_RSS_DESCRIPTION = getattr(
    settings, 'MEDIA_RSS_DESCRIPTION', u'Media rss description')
MEDIA_RSS_LEN = 200

DOC_THUMB_SIZE = 300, 200
GALLERY_FULL_SIZE = 625, 625
GALLERY_THUMB_SIZE = 120, 70
BOOKS_THUMB_SIZE = 80, 108
SIMILAR_THUMB_SIZE = 160, 95
PRIMARY_DOCS_THUMB_SIZE = 120, 70
RELATED_DOCS_THUMB_SIZE = 120, 80
DOC_LIST_THUMB_SIZE = 120, 70

MAX_SLUG_ATTEMPTS = 10
# Maximum number of attempts for making a unique slug.

TWITTER_ACCOUNT = getattr(settings, 'TWITTER_ACCOUNT', 'deephunt_ru')
TWITTER_TIMEOUT = getattr(settings, 'TWITTER_TIMEOUT', 2)
TWITTER_CACHE_PERIOD = getattr(settings, 'TWITTER_CACHE_PERIOD', 1*60)
TWITTER_TWEETS_SHOWN = getattr(settings, 'TWITTER_TWEETS_SHOWN', 5)

# FTP export account.
FTP_EXPORT_HOST = getattr(settings, 'FTP_EXPORT_HOST', None)
FTP_EXPORT_USER = getattr(settings, 'FTP_EXPORT_USER', '')
FTP_EXPORT_PASSWORD = getattr(settings, 'FTP_EXPORT_PASSWORD', '')
FTP_SLUG_OVERRIDE = getattr(
    settings, 'FTP_SLUG_OVERRIDE',
    {'russian_reporter': 'reporter', 'd-stroke': 'd', 'siberia': 'sibir',
     'northwest': 'sever', 'countries': 'countrie', 'magazine_auto': 'auto'})

TWITTER_TIME_DELTA = getattr(settings, 'TWITTER_TIME_DELTA', 4)

PARTNERS_IN_FEED_FROM = getattr(settings, 'PARTNERS_IN_FEED_FROM', 6)
PARTNERS_IN_FEED_TO = getattr(settings, 'PARTNERS_IN_FEED_TO', 17)

DOC_SHARE_PARTNER_ID = getattr(settings, 'DOC_SHARE_PARTNER_ID', None)

YANDEX_MAPS_API_KEY = getattr(settings, 'YANDEX_MAPS_API_KEY', '')
GOOGLE_EARTH_API_KEY = getattr(settings, 'GOOGLE_EARTH_API_KEY', '')

PUBLIC_ARTICLE_LIBRARY_TITLE = getattr(
    settings, 'PULIC_ARTICLE_LIBRARY_TITLE', _('Public article: %s'))

GET_DOCS_LIST_ONLY_WITH = (
    (1, _('preview')),
    (2, _('photos')),
    (3, _('videos')),
    (4, _('audios'))
)
USE_DEFAULT_DOCUMENT_MODEL = getattr(
    settings, 'USE_DEFAULT_DOCUMENT_MODEL', True)
CUSTOM_DOCUMENT_MODEL = (
    'document.DefaultDocument' if USE_DEFAULT_DOCUMENT_MODEL else
    settings.CUSTOM_DOCUMENT_MODEL)
CREATE_DOCUMENT_FORM = getattr(
    settings, 'CREATE_DOCUMENT_FORM',
    'spicy.document.forms.CreateDocumentForm')

EDIT_DOCUMENT_FORM = getattr(
    settings, 'EDIT_DOCUMENT_FORM', 'spicy.document.forms.DocumentForm')

RSS_CATEGORIES = getattr(
    settings, 'RSS_CATEGORIES',
    ('news', 'blog')
)

USE_DEFAULT_DOCUMENT_PROVIDER_MODEL = getattr(
    settings, 'USE_DEFAULT_DOCUMENT_PROVIDER_MODEL', True)
CUSTOM_DOCUMENT_PROVIDER_MODEL = (
    'document.DefaultDocumentProviderModel'
    if USE_DEFAULT_DOCUMENT_PROVIDER_MODEL
    else settings.CUSTOM_DOCUMENT_PROVIDER_MODEL)

USE_DEFAULT_DOCUMENT_PROVIDER_RELATED_DOC_MODEL = getattr(
    settings, 'USE_DEFAULT_DOCUMENT_PROVIDER_RELATED_DOC_MODEL', True)
CUSTOM_DOCUMENT_PROVIDER_RELATED_DOC_MODEL = (
    'document.DefaultDocumentProviderRelatedDoc'
    if USE_DEFAULT_DOCUMENT_PROVIDER_RELATED_DOC_MODEL
    else settings.CUSTOM_DOCUMENT_PROVIDER_RELATED_DOC_MODEL)
