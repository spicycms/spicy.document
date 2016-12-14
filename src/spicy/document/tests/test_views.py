from django.conf import settings

from django.test import TestCase

from django.core.urlresolvers import reverse

#from django.contrib.auth.models import User
from django.contrib.sites.models import Site

from django.contrib.webdesign.lorem_ipsum import paragraphs, words

from presscenter.models import Document, Hyperlink

from datetime import datetime


class PresscenterViewsTestCase(TestCase):
    fixtures = ['profile_testdata.json']

    def setUp(self):
        self.doc = Document.objects.create(
            'test doc 1', pub_date='2010-03-05 14:59')

        self.pub_date = datetime.strptime(
            '2010-03-05 14:59', "%Y-%m-%d %H:%M")

    def test_title(self):
        doc = Document.objects.get(
            title='test doc 1', pub_date=self.pub_date)
        self.assertEqual(doc.title, 'test doc 1')
        
        doc.title = 'changed title'
        self.assert_(Document.objects.get(
            title='changed title', pub_date=self.pub_date))
        
    def test_create(self):
        self.client.login(username='superuser', password='password')

        response = self.client.get(reverse('presscenter:admin:create'))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(reverse('presscenter:admin:create'), {
                'announce': paragraphs(5), 
                'title': 'test doc 1',
                'site': Site.objects.get_current().id,
                'pub_date': self.pub_date.strftime("%Y-%m-%d %H:%M")})
        self.assertEqual(response.status_code, 200)
        self.assert_("Dublicate document title in the same publication date."
                     in response.content)

        response = self.client.post(reverse('presscenter:admin:create'), {
                'announce': paragraphs(5), 
                'title': 'test article title',
                'site': Site.objects.get_current().id,
                'pub_date': self.pub_date.strftime("%Y-%m-%d %H:%M")})

        self.assertEqual(response.status_code, 302)
        self.assert_(
            Document.objects.get(title='test article title', pub_date=self.pub_date))
    
    def test_edit(self):
        self.client.login(username='superuser', password='password')

        response = self.client.get(
            reverse('presscenter:admin:edit', args=[self.doc.id]))
        self.assertEqual(response.status_code, 200)
        
        response = self.client.post(
            reverse('presscenter:admin:edit', args=[self.doc.id]), {
                'announce': paragraphs(5), 
                'title': 'test article title',
                'site': Site.objects.get_current().id,
                'pub_date': self.pub_date.strftime("%Y-%m-%d %H:%M")})

        self.assertEqual(response.status_code, 200)
        #self.assert_(
        #    Document.objects.get(title='test article title', pub_date=self.pub_date))
    
