# coding=utf-8
import datetime as dt
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.db.models import Q
from django import http
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext_lazy as _
from spicy.core.admin import conf, defaults as admin_defaults
from spicy.core.profile.decorators import is_staff
from spicy.core.service import api
from spicy.core.siteskin.decorators import render_to, ajax_request
from spicy.utils import add_perm, change_perm, delete_perm
from spicy.utils import get_custom_model_class, NavigationFilter, load_module
from . import defaults, forms, models


DocumentModel = get_custom_model_class(defaults.CUSTOM_DOCUMENT_MODEL)


class AdminApp(conf.AdminAppBase):
    name = 'document'
    label = _('Document')
    order_number = 0

    menu_items = (
        conf.AdminLink(
            'document:admin:create', _('Create article'),
            icon_class='icon-plus-sign-alt',
            perms=add_perm(defaults.CUSTOM_DOCUMENT_MODEL)),
        conf.AdminLink(
            'document:admin:index', _('All documents'),
            icon_class='icon-list-alt',
            perms=change_perm(defaults.CUSTOM_DOCUMENT_MODEL)),
    )

    create = conf.AdminLink('document:admin:create', _('Create article'),)

    @render_to('menu.html', use_admin=True)
    def menu(self, request, *args, **kwargs):
        return dict(app=self, *args, **kwargs)

    @render_to('dashboard.html', use_admin=True)
    def dashboard(self, request, *args, **kwargs):
        return dict(app=self, *args, **kwargs)

    dashboard_links = [
        conf.AdminLink(
            'document:admin:create', _('Create article'),
            DocumentModel.on_site.count(),
            perms=add_perm(defaults.CUSTOM_DOCUMENT_MODEL)
        )]
    dashboard_lists = [
        conf.DashboardList(
            _('Recent articles'), 'document:admin:edit',
            DocumentModel.on_site.order_by('-id'), 'pub_date',
            perms=change_perm(defaults.CUSTOM_DOCUMENT_MODEL)
        )]


@is_staff(required_perms=add_perm(defaults.CUSTOM_DOCUMENT_MODEL))
@render_to('create.html', use_admin=True)
def create(request):
    message = ''

    Form = load_module(defaults.CREATE_DOCUMENT_FORM)

    if request.method == 'POST':
        form = Form(request.POST)
        if form.is_valid():
            doc = form.save()
            doc.site.add(Site.objects.get_current())
            return http.HttpResponseRedirect(
                reverse('document:admin:edit', args=[doc.pk]))
        else:
            message = u'Form validation Error: {}'.format(
                form.errors.as_text())

    else:
        form = Form(
            initial={'pub_date': dt.datetime.now(), 'owner': request.user})

    return dict(user=request.user, form=form, message=message)


@is_staff(required_perms=change_perm(defaults.CUSTOM_DOCUMENT_MODEL))
@render_to('edit.html', use_admin=True)
def edit(request, doc_id):
    messages = ''

    doc = get_object_or_404(DocumentModel, pk=doc_id)
    if not request.user.is_staff:  # and can edit documents
        if doc.owner != request.user:
            raise PermissionDenied()

    Form = load_module(defaults.EDIT_DOCUMENT_FORM)
    if request.method == 'POST':
        form = Form(request.POST, instance=doc)
        if form.is_valid():
            doc = form.save()
            form = Form(instance=doc)
    else:
        form = Form(instance=doc)

    user = doc.owner
    if not doc.owner_id:
        user = request.user

    return dict(
        messages=messages, user=user, form=form, instance=doc, tab='doc')


def _save_forms(*all_forms):
    message = settings.MESSAGES['success']
    saved = True  # XXX

    for form in all_forms:
        if form.is_valid():
            form.save()
        else:
            saved = False
            message = settings.MESSAGES['error']
    return saved, message


def _get_common_doc_list(request, nav):
    message = ''
    search_args, search_kwargs, sql = [], {}, 'TRUE'

    if getattr(nav, 'year', False):
        search_kwargs['pub_date__year'] = nav.year

    if getattr(nav, 'month', False):
        search_kwargs['pub_date__month'] = nav.month

    if getattr(nav, 'day', False):
        search_kwargs['pub_date__day'] = nav.day

    if nav.search_text:
        search_args.append(
            Q(announce__icontains=nav.search_text) |
            Q(body__icontains=nav.search_text) |
            Q(hyperlink__title__icontains=nav.search_text) |
            Q(title__icontains=nav.search_text) |
            Q(quote__icontains=nav.search_text))

    tags = list()

    if tags:
        # TODO: use where SQL from xtag.service
        # Django ORM bug with SQL sub query
        sql = (
            'exists (SELECT 1 FROM tx_provider '
            'where tx_provider.consumer_type_id=%(doc_ctype)s and '
            'tx_provider.consumer_id=pc_doc.id and '  # 1082
            'tx_provider.tag_id in (%(tags)s) )' %
            dict(
                doc_ctype=ContentType.objects.get_for_model(
                    models.Document).id,
                tags=','.join("'%s'" % tag for tag in tags),
                site_id=settings.SITE_ID)
        )

    return search_args, search_kwargs, sql, message


@is_staff(required_perms=change_perm(defaults.CUSTOM_DOCUMENT_MODEL))
@render_to('list.html', use_admin=True)
def document_list(request, list_type=None, site_domain=None):
    message = request.GET.get('message', '')

    base_url_namespace = 'document:admin:index'

    #filter_form = forms.MagazineDocumentListFilterForm(request.GET)
    accepting_filters = [
        ('search_text', ''),
        ('genre', None),
        ('year', ''),
        ('month', ''),
        ('day', ''),
    ]
    force_filter = None

    nav = NavigationFilter(
        request, default_order='-pub_date', force_filter=force_filter,
        accepting_filters=accepting_filters)

    search_args, search_kwargs = [], {}

#    search_args, search_kwargs, sql, message = \
#        _get_common_doc_list(request, nav)

#    query = lambda x: x.filter(
#        *search_args, **search_kwargs)

    form = forms.DocumentFiltersForm(request.GET)

    if nav.search_text:
        search_args.append(
            Q(title__icontains=nav.search_text) |
            Q(body__icontains=nav.search_text))

    paginator = nav.get_queryset_with_paginator(
        get_custom_model_class(defaults.CUSTOM_DOCUMENT_MODEL),
        reverse(base_url_namespace),
        search_query=(search_args, search_kwargs),
        obj_per_page=admin_defaults.ADMIN_OBJECTS_PER_PAGE
    )
    objects_list = paginator.current_page.object_list
    return {
        'nav': nav, 'list_type': list_type, 'objects_list': objects_list,
        'paginator': paginator, 'message': message, 'form': form}


@is_staff(required_perms=delete_perm(defaults.CUSTOM_DOCUMENT_MODEL))
@render_to('delete.html', use_admin=True)
def delete(request, doc_id):
    doc = get_object_or_404(DocumentModel, pk=doc_id)
    if request.method == 'POST':
        if 'confirm' in request.POST:
            doc.delete()
            return http.HttpResponseRedirect(
                reverse('document:admin:index') +
                u'?message=%s' % _(
                    'All objects have been deleted successfully'))
    return dict(instance=doc)
