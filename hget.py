import math
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class GalleryParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.num_pages=0
        self.num_images=0
        self.title=''
        self.title_encountered = False

        # Galleries have 2 identical tables to change the page
        self.images_string_encountered = False

    def handle_starttag(self, tag, attrs):
        if(tag == 'h1'): # Finding the title: <h1 id='gn'> TITLE </h1>
            for attr in attrs:
                if(attr[0] == 'id' and attr[1] == 'gn'):
                    self.title_encountered = True
                    break
        elif(tag == 'p'): # Get number of images and pages
            for attr in attrs:
                if(attr[0] == 'class' and attr[1] == 'gpc'):
                    self.images_string_encountered = True
                    break

        # print("Encountered a start tag:", tag)
        # for attr in attrs:
        #     print("     attr:", attr)

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        return

    def handle_data(self, data):
        if(self.title_encountered): # Get the title
            self.title = str(data)
            self.title_encountered = False
        elif(self.images_string_encountered): # Get the number of images,
                                              # and the number of pages in the
                                              # gallery
            str_arr = str(data).split(" ")
            self.num_images = int(str_arr[-2])
            self.num_pages = math.ceil(self.num_images/40.0)
            self.images_string_encountered = False

        # print("Encountered some data  :", data)

class GalleryImageLinkParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_next_link_image = False
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if(tag == 'div'):
            for attr in attrs:
                if(attr[0] == 'class' and attr[1] == 'gdtm'):
                    self.is_next_link_image = True
                    break
        elif(self.is_next_link_image and tag == 'a'):
            for attr in attrs:
                if(attr[0] == 'href'):
                    self.urls.append(attr[1])
                    self.is_next_link_image = False
                    break

    def handle_endtag(self, tag):
        return

    def handle_data(self, data):
        return

class ImageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.image_url = ''

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag)
        # for attr in attrs:
        #     print("     attr:", attr)
        if(tag == 'img'):
            src = ''
            should_keep = False
            for attr in attrs:
                if(attr[0] == 'id' and attr[1] == 'img'):
                    should_keep = True
                elif(attr[0] == 'src'):
                    src = attr[1]
            if(should_keep):
                self.image_url = src
        return

    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        return

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        return

gallery_parser = GalleryParser()
link_parser = GalleryImageLinkParser()
image_parser = ImageParser()

url = 'https://e-hentai.org/g/939026/3594918bd8/index.html'

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

request = urllib.request.Request(url, None, headers)

with urllib.request.urlopen(request) as response:
    html = str(response.read().decode('utf8'))
    gallery_parser.feed(html)

print(gallery_parser.title)
print(gallery_parser.num_pages)
print(gallery_parser.num_images)

img_urls = []
for i in range(0, gallery_parser.num_pages):
    request = urllib.request.Request(url+'?p='+str(i), None, headers)

    with urllib.request.urlopen(request) as response:
        html = str(response.read().decode('utf8'))
        link_parser.feed(html)

    print(link_parser.urls)

    for url in link_parser.urls:
        request = urllib.request.Request(url, None, headers)

        with urllib.request.urlopen(request) as response:
            html = str(response.read().decode('utf8'))
            image_parser.feed(html)
            img_urls.append(image_parser.image_url)

print(img_urls)