import math, os, sys, getopt
import urllib.request, urllib.parse, requests
from lxml import html
from html.parser import HTMLParser

##################################################
## Parser Classes

# Parses the gallery for
# title
# number of pages
# number of images
class GalleryParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.num_pages=0
        self.num_images=0
        self.title=''
        self.title_encountered = False

        #Search for the string which displays the number of images in the
        #gallery.
        self.images_string_encountered = False

    def handle_starttag(self, tag, attrs):
        if(tag == 'h1'): # Finding the title: <h1 id='gn'> TITLE </h1>
            for name, val in attrs:
                if(name == 'id' and val == 'gn'):
                    self.title_encountered = True
                    break
        elif(tag == 'p'): # Get number of images and pages
            for name, val in attrs:
                if(name == 'class' and val == 'gpc'):
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

# Parses each page of the gallery for the link url
class GalleryImageLinkParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.is_next_link_image = False
        self.urls = []

    def handle_starttag(self, tag, attrs):
        if tag == 'div':
            for name, val in attrs:
                if name == 'class' and val == 'gdtm':
                    self.is_next_link_image = True
                    break
        elif self.is_next_link_image and tag == 'a':
            for name, val in attrs:
                if name == 'href':
                    self.urls.append(val)
                    self.is_next_link_image = False
                    break

    def handle_endtag(self, tag):
        return

    def handle_data(self, data):
        return

# parses the link for the actual image url
class ImageParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.image_url = ''
        self.is_next_link_image = False

    def handle_starttag(self, tag, attrs):
        if HD:
            if tag == 'div':
                for name, val in attrs:
                    if(name == 'id' and val == 'i7'):
                        self.is_next_link_image = True
            elif tag == 'a' and self.is_next_link_image:
                for name, val in attrs:
                    if name == 'href':
                        self.image_url = val
                        self.is_next_link_image = False
                        # print(val)
        else:
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


    def handle_endtag(self, tag):
        # print("Encountered an end tag :", tag)
        return

    def handle_data(self, data):
        # print("Encountered some data  :", data)
        return

##################################################

##################################################
## Initialization + handle command line arguments

username = ''
password = ''

HD = False

gallery_urls = sys.argv[1:] # list of arguments from terminal
current_directory = os.path.dirname(os.path.realpath(__file__))
output_directory = os.path.join(current_directory, 'hget_downloads')

def print_usage():
    print('\nOptions and arguments:')
    print('-h --help          : print this help info.')
    print('--hd               : get the hd original images (requires logging in).')
    print('-o --output DIR    : set output directory to DIR.')
    print('-p --password PASS : set password to PASS')
    print('-u --username USER : set username to USER')
    print('\nDownload galleries (default directory is ./hget_downloads/):\n\n', '   python hget.py URL1 URL2...\n')
    print('    python hget.py URL... -o /path/to/directory\n')
    print('    python hget.py URLs... --hd --username Username --password Password -o /path/to/directory/')

# if no arguments then exit
if len(sys.argv) == 1:
    print_usage()
    sys.exit()

# get all the options
try:
    opts, args = getopt.getopt(sys.argv[1:], "ho:p:u:", ['help', 'hd', 'output=', 'username=', 'password='])
except getopt.GetoptError:
    print('Option error!')
    print_usage()
    sys.exit(2)

for opt, arg in opts:
    if opt in ('-h', '--help'):
        print_usage()
        sys.exit()
    elif opt in ('--hd'):
        HD = True
    elif opt in ('-o', '--output'):
        if os.path.isabs(arg):
            # if path is absolute, replace the output directory
            output_directory = arg
        else:
            output_directory = os.path.join(current_directory, arg)
    elif opt in ('-u', '--username'):
        username = arg
    elif opt in ('-p', '--password'):
        password = arg

    # remove opt and arg from the list of arguments
    if(opt != ''):
        gallery_urls.remove(opt)

    if(arg != ''):
        gallery_urls.remove(arg)

gallery_urls = list(set(gallery_urls)) # remove duplicate urls

if len(gallery_urls) == 0:
    print('No URLs.')
    print_usage()
    sys.exit()

headers={"User-Agent":"Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
         'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
         'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
         'Accept-Encoding': 'none',
         'Accept-Language': 'en-US,en;q=0.8',
         'Connection': 'keep-alive'}


session = requests.Session()

if username == '' or password == '':
    print('No Login.')
else:
    print('Logging in...')

    login_url = 'https://forums.e-hentai.org/index.php?act=Login&CODE=01'

    login = session.get(login_url)
    login_html = html.fromstring(login.text)
    hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
    form = {x.attrib["name"]: x.attrib["value"] for x in hidden_inputs}
    form['UserName'] = username
    form['PassWord'] = password

    response = session.post(login_url, data=form)

    headers['Cookie'] = "; ".join('%s=%s' % (k,v) for k,v in session.cookies.get_dict().items())

# print(headers['Cookie'])
# print(session.cookies)

#####################################################

#####################################################
## Function to download a gallery

def download_gallery(url):

    gallery_parser = GalleryParser()
    link_parser = GalleryImageLinkParser()
    image_parser = ImageParser()

    request = urllib.request.Request(url, None, headers)

    with urllib.request.urlopen(request) as response:
        html = str(response.read().decode('utf8'))
        gallery_parser.feed(html)

    print('Title:', gallery_parser.title)
    print('Number of pages:', gallery_parser.num_pages)
    print('Number of images:', gallery_parser.num_images)

    # Make sure the directory exists
    gallery_directory = os.path.join(output_directory, gallery_parser.title)

    if(os.path.exists(gallery_directory)):
        print('Directory ', gallery_directory, 'already exists.')
        print('Skipping.')
        return
    else:
        os.makedirs(gallery_directory, exist_ok=True)
        print('Directory:', gallery_directory, 'created.')

    # parse each page of the gallery
    for i in range(0, gallery_parser.num_pages):
        # print(url+'?p='+str(i))
        request = urllib.request.Request(url+'?p='+str(i), None, headers)

        with urllib.request.urlopen(request) as response:
            html = str(response.read().decode('utf8'))
            link_parser.feed(html)

    # parse each link for its image url
    img_urls = []
    for url in link_parser.urls:
        request = urllib.request.Request(url, None, headers)

        with urllib.request.urlopen(request) as response:
            html = str(response.read().decode('utf8'))
            print("Finding image url: ", len(img_urls),'/', gallery_parser.num_images, end='\r')
            image_parser.feed(html)
            img_urls.append(image_parser.image_url)


    # Download the images
    for id, url in enumerate(img_urls):
        print("Downloading image: ", id+1, '/', gallery_parser.num_images, end='\r')

        if HD:
            filepath = os.path.join(gallery_directory, str(id+1)+'.jpg')
            request = urllib.request.Request(url, None, headers)

            with urllib.request.urlopen(request) as response:
                data = response.read()

                with open(filepath, 'wb') as f:
                    f.write(data)
        else:
            filename = url.rsplit('/', 1)[1]
            try:
                filepath = os.path.join(gallery_directory, filename)
                urllib.request.urlretrieve(url, filepath)
            except:
                print("Timedout on page: ", id+1, '/', gallery_parser.num_images, " File: ", filename)

        # except:
        #      print("Timedout on page: ", id+1, '/', gallery_parser.num_images, " File: ", filename)

##############################################

##############################################
### Download everything

# Print urls
print("\nURLS:")
for url in gallery_urls:
      print(url.rstrip())

# Download each gallery
for i, url in enumerate(gallery_urls):
    print('\n' + str(i+1) + '.', 'Downloading', url)
    download_gallery(url.rstrip()) # remove white space
