import lxml.html
from lxml import etree
from lxml.cssselect import CSSSelector
import requests
import re



class PageCount(object):
    def __init__(self, url, page=None):
        self.page = page
        self.url = url

    def let_page_counting(self):
        if self.page is not None:
            return self.page
        self.page = 1
        css_selector_fail = '#app>div.base>div.bundle>div>div>main>section>div.alert_message>div.alert_message__title'
        while True:
            ful_url = self.url + str(self.page)
            if lxml.html.fromstring(requests.get(ful_url).content).cssselect(css_selector_fail):
                return self.page - 1
            self.page += 1

class Parser(object):
    """Парсер html, принимает url и колличество старниц"""
    def __init__(self, url, pages):
        self.url = url
        self.pages = [page for page in range(1, pages + 1)]

    def __iter__(self):
        """Парсит страницы"""
        css_selector = '#app>div.base>div.bundle>div>div>main>section>div._component.product_list_container>ul'    
        data = 'https://youla.ru/build/pwa/ProductPhoneNumberModal-chunk.7e7939b2.js'    
        for page in self.pages:
            ful_url = self.url + str(page)
            response = lxml.html.fromstring(requests.get(ful_url).content)
            if not response.cssselect(css_selector):
                return
            childrens = response.cssselect(css_selector).pop().getchildren()
           
            for child in childrens:
                href = child.findall('a').pop().get('href')
                description = child.findall('a').pop().get('title').strip()
                dirty_price = child.findall('a/figure/figcaption/div')[0].text_content().strip()
                price = re.search(r'(\d.+[₽руб].)|[А-Я][а-я]+', dirty_price).group().strip()
                phone_html = requests.get('https://youla.ru{}'.format(href), data=data)
                phone_validate = re.search(r'"displayPhoneNum":"\d+"', phone_html.text)
                if phone_validate is  None:
                    phone = 'Без номера телефона либо зашифрован'
                elif phone_validate is not  None: 
                    phone = phone_validate.group().split(':')[1].strip('"')
                yield description, price, phone

           

            
if __name__ == '__main__':
    run = PageCount('https://youla.ru/astrahan?q=носки&page=')   
    print(run.let_page_counting())
