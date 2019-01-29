import requests, re, base64, unicodedata ,pytesseract
from bs4 import BeautifulSoup
from io import BytesIO
from PIL import Image

def clean_image_noise(img):

    img = img.convert("RGBA")
    pixdata = img.load()

    #Clean the background noise, if color != white, then set to black.

    for y in xrange(img.size[1]):
        for x in xrange(img.size[0]):
            if pixdata[x, y] == (0, 0, 0, 255):
                pixdata[x, y] = (255, 255, 255, 255)


    width, height = img.size
    new_size = width*8, height*8
    img = img.resize(new_size, Image.LANCZOS)
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 155 else 255, '1')

    return img

def fetch_image(headers):
    request = requests.get('http://challenge01.root-me.org/programmation/ch8/', headers=headers)
    dom_tree = BeautifulSoup(request.text, 'html.parser')
    image_src = dom_tree.img['src']

    base64_data = re.sub('^data:image/.+;base64,', '', image_src)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)
    img = Image.open(image_data)

    return img

def get_captcha_value_and_submit(img, headers):

    headers['Referer'] = 'http://challenge01.root-me.org/programmation/ch8/'
    headers['Cookie'] = 'PHPSESSID=i0enc8t6egnc2g4h67cj0j9pq0'

    captcha_value =  pytesseract.image_to_string(img)
    captcha_value = unicodedata.normalize('NFKD', captcha_value).encode('ascii', 'ignore')
    # print(captcha_value)
    payload = {'cametu': captcha_value}
    # payload = urllib.urlencode(payload)
    print('Sending payload {} ...'.format(payload))
    request = requests.post('http://challenge01.root-me.org/programmation/ch8/', data=payload, headers=headers)

    return request.text

if __name__ == '__main__':

    headers= {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7',
    }

    response = 'Failed'

    while('Failed' in response):

        img = fetch_image(headers)
        img = clean_image_noise(img)
        response = get_captcha_value_and_submit(img, headers)

    print(response)
