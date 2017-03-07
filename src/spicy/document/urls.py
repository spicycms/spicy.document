from django.conf.urls import patterns, include, url
from . import feeds, defaults


doc_list_rss = feeds.DocListRSS()


public_urls = patterns(
    '',
    url(r'^rss/$', feeds.DocListRSS(), name='doc-list-rss'),
)

for category in defaults.RSS_CATEGORIES:
    public_urls += patterns(
        '',
        url(r'^(?P<category>%s)/rss/$' % category, feeds.DocListRSS(),
            name='doc-list-rss'),
    )

public_urls += patterns(
    'spicy.document.views',
    url(r'^a(?P<doc_id>\d+)/$', 'document', name='doc'),
    #url(r'^create/$', 'create_article', name='create'),
)

admin_urls = patterns(
    'spicy.document.admin',

    # classic document
    url(r'^list/$', 'document_list', name='index'),
    url(r'^list/(?P<site_domain>[.\w]+)/$', 'document_list', name='index'),

    url(r'^create/$', 'create', name='create'),
    url(r'^edit/(?P<doc_id>\d+)/$', 'edit', name='edit'),
    #url(r'^edit/(?P<doc_id>\d+)/comments/$', 'edit_comments',
    #    name='edit-comments'),
    url(r'^(?P<doc_id>\d+)/delete/$', 'delete', name='delete'),
    #url(r'^edit/(?P<doc_id>\d+)/history/$', 'edit_doc_history', name='edit-doc-history'),
)


urlpatterns = patterns(
    '',
    url(r'^admin/document/', include(admin_urls, namespace='admin')),
    url(r'^', include(public_urls, namespace='public'))
)
