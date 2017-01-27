# _*_ coding: utf-8 _*_
import os
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import RequestContext

from spicy.core.service import api
from spicy.core.siteskin import defaults as sk_defaults
from spicy.utils import make_cache_key
from spicy.utils.models import get_custom_model_class
from spicy.core.siteskin.decorators import render_to

from . import defaults

DocumentModel = get_custom_model_class(defaults.CUSTOM_DOCUMENT_MODEL)

def doc_list_rss(request):
    return dict()


@render_to('spicy.document/document.html', use_siteskin=True)
def document(request, doc_id):
    doc = None

    try:
        doc = DocumentModel.objects.get(pk=doc_id)
    except DocumentModel.DoesNotExist:
        raise Http404

    if not ((request.user.is_staff or
            doc.owner == request.user) or doc.check_public()):
        raise Http404

    if doc.origin_id == settings.SITE_ID or doc.site.filter(
        id=settings.SITE_ID).exists():

        #api.register['statistic'].inc_visits(request, doc)
        #api.register['referrer'].inc_refs(request, doc)
        return dict(doc=doc, page_slug='')

    raise Http404


def document_cached_templates(request, doc_id):
    if not request.user.is_staff:
        cache_key = make_cache_key(request)
        content = cache.get(cache_key)
        doc = cache.get(cache_key + '[doc-object]')

        if content and doc:
            if doc.is_public:
                response = render_to_response(
                    doc.get_rubric_template, dict(
                        doc=doc, content=content, ),
                    context_instance=RequestContext(request))
                if doc.is_public:
                    response['Last-Modified'] = doc.utc_pub_date(
                        ).strftime('%a, %d %b %Y %H:%M:%S GMT')

                #api.register['statistic'].inc_visits(request, doc)
                #api.register['referrer'].inc_refs(request, doc)
                return response

            # for doc awner
            if doc.owner != request.user:
                raise Http404

    doc = None
    try:
        doc = DocumentModel.objects.get(pk=doc_id)
    except DocumentModel.DoesNotExist:
        raise Http404

    if not (
        request.user.is_staff or doc.owner == request.user
        ) and not doc.check_public():
        raise Http404

    if doc.origin_id == settings.SITE_ID or doc.site.filter(
        id=settings.SITE_ID).exists():
        response = render_to_response(
            doc.get_template, dict(doc=doc),
            context_instance=RequestContext(request))

        content = response.content
        if not request.user.is_staff:
            cache_key = make_cache_key(request)
            cache.set(cache_key, content, sk_defaults.CACHE_TIMEOUT)
            cache.set(
                cache_key + '[doc-object]', doc, sk_defaults.CACHE_TIMEOUT)

        response = render_to_response(
            doc.get_rubric_template,
            dict(doc=doc, content=content,),
            context_instance=RequestContext(request))
        if doc.is_public:
            response['Last-Modified'] = doc.utc_pub_date(
                ).strftime('%a, %d %b %Y %H:%M:%S GMT')

        api.register['statistic'].inc_visits(request, doc)
        api.register['referrer'].inc_refs(request, doc)
        return response
    raise Http404
