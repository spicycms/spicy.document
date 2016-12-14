# *-* coding: utf-8 *-*
import os
import re
from . import defaults, parsers, utils
from datetime import datetime
from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.syndication.views import Feed
from django.shortcuts import get_object_or_404
from django.utils import feedgenerator
from django.utils.xmlutils import SimplerXMLGenerator
from pytz import timezone
from spicy.core.service import api
from spicy.utils import cdata, CDATA_RE


Document = utils.get_concrete_document()
tz = timezone(settings.TIME_ZONE)
CDATA_RE = re.compile(u'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F%s]')
cdata = lambda s: '<![CDATA[%s]]>' % CDATA_RE.sub(
    ' ', s).replace(']]>', ']]]]><![CDATA[>')

class SXG(SimplerXMLGenerator):
    def addQuickElementCDATA(self, name, contents=None, attrs=None):
        if attrs is None:
            attrs = {}
        self.startElement(name, attrs)
        if contents:
            self._write(cdata(contents))
        self.endElement(name)


class CDATAWriter(object):
    def write(self, outfile, encoding):
        handler = SXG(outfile, encoding)
        handler.startDocument()
        is_rss = hasattr(self, 'rss_attributes')
        if is_rss:
            handler.startElement(u"rss", self.rss_attributes())
            handler.startElement(u"channel", self.root_attributes())
        else:
            handler.startElement('feed', self.root_attributes())

        self.add_root_elements(handler)
        self.write_items(handler)

        if is_rss:
            self.endChannelElement(handler)
            handler.endElement(u"rss")
        else:
            handler.endElement(u'feed')


class DocListRSS(Feed):
    #TODO: copyright?

    def get_object(self, request, *args, **kwargs):
        self.link = request.path
        self.feed_image = kwargs.pop('feed_image', None)
        return args, kwargs

    def title(self, obj):
        return defaults.RSS_TITLE

    def items(self, obj):
        args, kwargs = obj
        return Document.objects.filter(*args, **kwargs).select_related()[
            :defaults.DEFAULT_RSS_LEN]

    def item_link(self, item):
        if item:
            return item.get_absolute_url()
        return ''

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return tz.localize(item.created)

    def item_enclosure_url(self, item):
        width, height = defaults.DOC_THUMB_SIZE
        thumb = ''#item.url
        return (
            'http://%s%s' % (Site.objects.get_current().domain, thumb)
            if thumb else '')

    item_enclosure_length = 0
    item_enclosure_mime_type = 'image/jpeg'

    def item_description(self, item):
        return CDATA_RE.sub(
            ' ', item.get_first_paragraph())

    def item_categories(self, item):
        try:
            return [tag.name for tag in item.tags.all()]
        except AttributeError:
            return ''

    def feed_extra_kwargs(self, obj):
        return {'image_url': self.feed_image}


class MediaFeedGenerator(feedgenerator.Rss201rev2Feed):
    def add_item_elements(self, handler, item):
        super(MediaFeedGenerator, self).add_item_elements(handler, item)

        for enclosure in item.get('enclosures', ()):
            handler.addQuickElement(u'enclosure', attrs=enclosure)

    def add_root_elements(self, handler):
        super(MediaFeedGenerator, self).add_root_elements(handler)
        if self.feed['image_url']:
            handler.startElement(u'image', {})
            handler.addQuickElement(u"url", self.feed['image_url'])
            handler.addQuickElement(u"title", self.feed['title'])
            handler.addQuickElement(u"link", self.feed['link'])
            handler.endElement(u'image')


class MediaDocListRSS(DocListRSS):
    domain = None
    feed_type = MediaFeedGenerator

    def items(self, obj):
        return super(MediaDocListRSS, self).items(obj)

    @classmethod
    def add_media(cls, path, type_prefix, enclosures):
        if not path:
            return

        if cls.domain is None:
            cls.domain = Site.objects.get_current().domain
        try:
            ext = os.path.splitext(path)[1][1:]
        except Exception:
            ext = None

        result = {'url': 'http://%s%s' % (cls.domain, path), 'length': '0'}
        if ext:
            result['type'] = '%s/%s' % (
                type_prefix, ('jpeg' if ext == 'jpg' else ext))
        result['title'] = path
        enclosures.append(result)

    def item_enclosure_list(self, item):
        enclosures = []
        if item.preview_id:
            width, height = defaults.DOC_THUMB_SIZE
            thumb = get_thumbnail_or_404(width, height, item, 'preview', False)
            self.add_media(thumb, 'image', enclosures)

        #for telecast in item.telecasts:
        #    self.add_media(
        #        telecast.media.get_absolute_url(), 'video', enclosures)

        #if item.audio_id:
        #    self.add_media(item.audio.get_absolute_url(), 'audio', enclosures)

        return enclosures

    def item_extra_kwargs(self, item):
        extra = super(MediaDocListRSS, self).item_extra_kwargs(item)
        extra['enclosures'] = self.item_enclosure_list(item)
        return extra


class MediaRSSFeedGenerator(CDATAWriter, feedgenerator.Rss201rev2Feed):
    def rss_attributes(self):
        attributes = super(MediaRSSFeedGenerator, self).rss_attributes()
        attributes['xmlns:media'] = u'http://search.yahoo.com/mrss/'
        return attributes

    def add_item_elements(self, handler, item):
        super(MediaRSSFeedGenerator, self).add_item_elements(handler, item)

        medias = item['media']
        domain = Site.objects.get_current().domain

        for media in medias:
            if isinstance(media, list):
                cur_medias = media
                handler.startElement('media:group', {})
                group_started = True
            else:
                cur_medias = [media]
                group_started = False

            if group_started:
                for cur_media in cur_medias:
                    type_ = cur_media.get('type')
                    if type_ and type_.startswith('video/'):
                        cur_media['default'] = True
                        break

            for cur_media in cur_medias:
                media_attrs = {
                    'url': cur_media['url'], 'lang': 'ru'}
                type_ = cur_media.get('type')
                if type_:
                    media_attrs['type'] = type_

                # Mark default media for content group.
                is_default = cur_media.get('default')
                if is_default:
                    media_attrs['isDefault'] = 'true'

                handler.startElement('media:content', media_attrs)
                handler.addQuickElementCDATA(
                    'media:title', cur_media['title'], {'type': 'html'})
                handler.addQuickElementCDATA(
                    'media:description', cur_media['desc'], {'type': 'html'})

                if type_.startswith('video/') and cur_media[
                        'media'].preview_id:
                    handler.addQuickElement(
                        u'media:thumbnail',
                        attrs={
                            'url': 'http://{0}{1}'.format(
                                domain,
                                cur_media[
                                    'media'].preview.get_absolute_url())})

                keywords = cur_media.get('keywords')
                if keywords:
                    handler.addQuickElementCData('media:keywords', keywords)
                handler.endElement('media:content')

            if group_started:
                handler.endElement('media:group')

    def add_root_elements(self, handler):
        super(MediaRSSFeedGenerator, self).add_root_elements(handler)
        if self.feed['image_url']:
            handler.startElement(u'image', {})
            handler.addQuickElement(u"url", self.feed['image_url'])
            handler.addQuickElement(u"title", self.feed['title'])
            handler.addQuickElement(u"link", self.feed['link'])
            handler.endElement(u'image')


class MediaRSSFeed(DocListRSS):
    feed_type = MediaRSSFeedGenerator

    title = defaults.MEDIA_RSS_TITLE
    description = defaults.MEDIA_RSS_DESCRIPTION
    domain = None

    def link(self):
        return 'http://%s' % Site.objects.get_current().domain

    def items(self, obj):
        args, kwargs = obj
        query = Document.objects.filter(
            *args, **kwargs).select_related('image')
        if defaults.MEDIA_RSS_LEN is not None:
            query = query[:defaults.MEDIA_RSS_LEN]
        return query

    def item_link(self, item):
        return item.get_absolute_url()

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return tz.localize(item.created)

    def item_description(self, item):
        return CDATA_RE.sub(' ', item.get_first_paragraph())

    def item_extra_kwargs(self, item):
        return {'media': self.item_media(item)}

    @classmethod
    def add_media(self, cls, enclosures, prov=None, item=None):
        path = cls.url
        media = cls

        if not path:
            return
        
        domain = Site.objects.get_current().domain

        try:
            ext = os.path.splitext(path)[1][1:]
        except Exception:
            ext = None

        result = {
            'url': 'http://%s%s' % (domain, path), 'media': media}
        if ext:
            result['type'] = '%s/%s' % (
                'image', ('jpeg' if ext == 'jpg' else ext))

        result['title'] = (
            (prov and (prov.title or prov.media.title)) or
            item.title)
        result['desc'] = (
            (prov and (prov.alt or prov.media.alt)))

        enclosures.append(result)
        return result

    def item_media(self, item):
        medias = []
        if item.image:
            self.add_media(item.image, medias, item=item)
        if item.get_images():
            for item in item.get_images():
                self.add_media(item.mediafile, medias, prov=item)

        return medias


class YandexFeed(MediaRSSFeedGenerator):
    def rss_attributes(self):
        attributes = super(YandexFeed, self).rss_attributes()
        attributes['xmlns:yandex'] = u'http://news.yandex.ru'
        return attributes

    def add_item_elements(self, handler, item):
        if item['yandex:full-text'] is not None:
            handler.addQuickElementCDATA(
                u'yandex:full-text', item['yandex:full-text'])
        handler.addQuickElement(u'author', unicode(item['author']))

        super(YandexFeed, self).add_item_elements(handler, item)


class YandexRSS(MediaRSSFeed):
    feed_type = YandexFeed

    title = defaults.YANDEX_RSS_TITLE
    description = defaults.YANDEX_RSS_DESCRIPTION
    link = defaults.YANDEX_RSS_LINK

    def items(self, obj):
        args, kwargs = obj
        return Document.objects.filter(
            *args, **kwargs
            ).select_related().order_by(
            '-created')[:defaults.YANDEX_RSS_LEN]

    def item_yandex_full_text(self, item):
        body = item.content
        parser = parsers.StrippingParagraphHTMLParser()
        parser.feed(body)
        return '\n'.join(parser.paragraphs)

    def feed_image(self):
        return ''

    def item_extra_kwargs(self, item):
        text = self.item_yandex_full_text(item)
        return {
            'yandex:full-text': text, 'media': self.item_media(item),
            'author': item.owner_name()}


class DocumentProviderRSS(Feed):
    def __init__(self, model):
        self.model = model
        super(DocumentProviderRSS, self).__init__()

    def get_object(self, request, consumer_type, consumer_id):
        return get_object_or_404(
            self.model, consumer_type__model=consumer_type,
            consumer_id=consumer_id)

    def link(self, obj):
        url = obj.url
        site = 'http://%s/' % Site.objects.get_current().domain
        if url:
            return site + url
        else:
            return site

    def title(self, obj):
        return obj.title

    def items(self, obj):
        return Document.objects.filter(
            is_public=True, pub_date__lte=datetime.now(),
            documentproviderrelateddocs__is_public=True,
            documentproviderrelateddocs__provider=obj).order_by(
            'documentproviderrelateddocs__order_lv')

    def item_link(self, item):
        return item.get_absolute_url()

    def item_pubdate(self, item):
        return tz.localize(item.pub_date)

    def item_title(self, item):
        return item.title

    def item_enclosure_url(self, item):
        width, height = defaults.DOC_THUMB_SIZE
        thumb = get_thumbnail_or_404(
            width, height, item, 'preview', create=False)
        if thumb:
            return (
                'http://%s%s' % (Site.objects.get_current().domain, thumb)
                if thumb else '')
    item_enclosure_length = 0
    item_enclosure_mime_type = 'image/jpeg'

    def item_description(self, item):
        return item.get_announce()


class InterfaxFeed(CDATAWriter, feedgenerator.Rss201rev2Feed):
    def add_item_elements(self, handler, item):
        if item['content'] is not None:
            handler.addQuickElementCDATA(u'content', item['content'])

        super(InterfaxFeed, self).add_item_elements(handler, item)


class InterfaxRSS(Feed):
    feed_type = InterfaxFeed

    title = defaults.YANDEX_RSS_TITLE
    description = defaults.YANDEX_RSS_DESCRIPTION
    link = defaults.INTERFAX_RSS_LINK

    def items(self):
        return Document.objects.filter(
            created__lte=datetime.now()
            ).order_by('-created').select_related(
            'preview')[:defaults.YANDEX_RSS_LEN]

    def item_link(self, item):
        if item:
            return item.get_absolute_url()
        return ''

    def item_title(self, item):
        return item.title

    def item_pubdate(self, item):
        return tz.localize(item.created)

    def item_enclosure_url(self, item):
        thumb = item.image
        return (
            'http://%s%s' % (Site.objects.get_current().domain, thumb.url)
            ) if thumb else ''
    item_enclosure_mime_type = 'image/jpeg'
    item_enclosure_length = 0

    def item_description(self, item):
        return item.announce or item.get_first_paragraph()

    def item_content_full_text(self, item):
        return item.get_announce()

    def item_extra_kwargs(self, item):
        return {
            #'content:encoded':self.item_yandex_full_text(item),
            'content':self.item_content_full_text(item)}
