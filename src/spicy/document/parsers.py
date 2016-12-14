import itertools
import os
from HTMLParser import HTMLParser

class ParagraphHTMLParser(HTMLParser):
    def __init__(self):
        self.now_par_id = None
        self.paragraphs = {}
        HTMLParser.__init__(self)
  
    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            for key, value in attrs:
                if key == 'id':
                    self.now_par_id = value

    def handle_endtag(self, tag):
        if tag == 'p':
            self.now_par_id = None
            
    def handle_data(self, data):
        if self.now_par_id:
            self.paragraphs[self.now_par_id] = data


class StrippingParagraphHTMLParser(HTMLParser):
    def __init__(self):
        self.paragraphs = []
        self.buffer = []
        self.tag = None
        self.tags = []
        HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag in ('p', 'h3'):
            # This shouldn't be necessary on a well-formed HTML document, but
            # it won't hurt.
            self.append_buffer()
            self.tag = tag

            # Image sources are added to paragraphes for ASCII export.
            if tag == 'img':
                attrs_dict = dict(attrs)
                src = attrs_dict.get('src', None)
                if src:
                    self.buffer.append(os.path.basename(src))
                    self.append_buffer()
                    self.tag = None

    def handle_endtag(self, tag):
        if tag in ('p', 'h3'):
            self.append_buffer()
            
    def handle_data(self, data):
        self.buffer.append(data)

    def append_buffer(self):
        if self.buffer:
            joined_buffer = self.unescape(''.join(self.buffer)).strip()
            if joined_buffer:
                self.paragraphs.append(joined_buffer)
                self.tags.append(self.tag)
            self.buffer = []

    def close(self):
        HTMLParser.close(self)
        self.append_buffer()

    def paragraphs_gen(self):
        """
        This is a generator that returns pairs of (bool, str), where
        first item is a flag that's set to True for headers.
        """
        counter = 0
        for tag, paragraph in itertools.izip(self.tags, self.paragraphs):
            yield (tag, paragraph)
            counter += 1
