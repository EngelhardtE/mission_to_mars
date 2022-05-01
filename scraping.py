from splinter import Browser, browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import datetime as dt
from webdriver_manager.chrome import ChromeDriverManager

def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    images_urls = mars_hemis(browser)
    data = {
        'news_title' : news_title,
        'news_paragraph' : news_paragraph,
        'featured_image' : featured_image(browser),
        'facts' : mars_facts(),
        'hemispheres' : images_urls,
        'last_modified' : dt.datetime.now()
    }
    browser.quit()
    return data
def mars_news(browser):
    url = 'https://data-class-mars.s3.amazonaws.com/Mars/index.html'
    browser.visit(url)
    browser.is_element_present_by_css('div.list_text', wait_time=1)
    html = browser.html
    news_soup = soup(html, 'html.parser')
    try:
        slide_elem = news_soup.select_one('div.list_text')
        news_title = slide_elem.find('div', class_='content_title').get_text()
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    except AttributeError:
        return None, None
    return news_title, news_p
def featured_image(browser):
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
    except AttributeError:
        return None 
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
    return img_url
def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None
    df.columns = ['Description','Mars','Earth']
    df.set_index('Description', inplace=True)

    return df.to_html()
def mars_hemis(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    images_urls = []
    for i in range(4):
        hemispheres = {}
        browser.find_by_css('a.product-item h3')[i].click()
        element = browser.find_link_by_text('Sample').first
        img_url = element['href']
        title = browser.find_by_css('h2.title').text
        hemispheres['img_url'] = img_url 
        hemispheres['title'] = title
        images_urls.append(hemispheres)
        browser.back()
    return images_urls
if __name__ == "__main__":
    print(scrape_all())