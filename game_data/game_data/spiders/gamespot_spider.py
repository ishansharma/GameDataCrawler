import scrapy
from dateutil.parser import parse


class GamespotSpider(scrapy.Spider):
    name = "gamespot"
    start_urls = [
        'https://www.gamespot.com/reviews/?page=1'
    ]

    def parse(self, response):
        for href in response.css('.media-game>a'):
            yield response.follow(href, self.parse_review)

        for href in response.css('.next>a'):
            yield response.follow(href, self.parse)

    def parse_review(self, response):
        def extract_with_css(query):
            return response.css(query).extract_first().strip()

        def get_article_content(query):
            review_text = ''
            for p in response.css(query).extract():
                review_text += p
            return review_text

        def get_publish_date(query):
            date_text = extract_with_css(query)

            date = parse(date_text)
            return date.strftime('%Y/%m/%d')

        def get_systems(query):
            systems = ''

            for s in response.css(query).extract():
                systems += s + ','

            return systems[:-1]

        yield {
            "title": extract_with_css(".subnav-list__item-primary>a>span::text"),
            "content": get_article_content("section.article-body p"),
            "score": extract_with_css(".gs-score__cell>span::text"),
            "published": get_publish_date("time::attr(datetime)"),
            "systems": get_systems("li.system.system--simple::text"),
            "url": response.request.url
        }
