import scrapy
import tldextract
import requests
import simplejson as json
from w3lib.html import remove_tags
from application_only_auth import Client

class PeopleSpider(scrapy.Spider):
    name = "fame"
    client = ""
    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
        "CONCURRENT_REQUESTS_PER_IP": 1,
        "DOWNLOAD_DELAY": 1,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36"
    }
    start_urls = [
        "https://www.thefamouspeople.com/singers.php",
    ]

    def parse(self, response):
        self.client = Client('XMWmonO1hiqZgooIhu8JgNUXQ', 'aHk4u50HCnHzWWFgCvFdXyYZeOow4oJ8co2z7B1jcubKd0JSym')
        for person in response.css("div.tile"):
            item = dict()
            item["name"] = person.css("a::text")[-1].extract().strip()
            item["profile"] = "https:" + person.css("a::attr(href)").extract_first()

            if item["profile"] is not None:
                request = scrapy.Request(item["profile"], callback=self.profile)
                request.meta["item"] = item
                yield request
            # break
        next_page = response.xpath("//div[@class='pagination']//a[text()='Next']/@href").extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

    def profile(self, response):
        item = response.meta["item"]
        links = response.css("a.insta-social-links::attr(href)").extract()
        for link in links:
            item[tldextract.extract(link).domain + '_link'] = link[:-1]
        if "instagram" not in item:
            instagram = scrapy.Request("https://www.instagram.com/web/search/topsearch/?context=blended&query=" + item["name"],
                callback=self.instagram)
            instagram.meta["item"] = item
            yield instagram
        if "twitter" not in item:
            twitter = scrapy.Request("https://twitter.com/i/search/typeahead.json?count=1&result_type=users&q=" + item["name"],
                callback=self.twitter)
            twitter.meta["item"] = item
            yield twitter
        if "twitter" in item and "instagram" in item:
            yield item

    def instagram(self, response):
        item = response.meta["item"]
        item["instagram"] = dict()
        jsonresponse = json.loads(response.body_as_unicode())
        item["instagram"]["username"] = jsonresponse["users"][0]["user"]["username"]
        item["instagram"]["profile"] = "https://instagram.com/" + jsonresponse["users"][0]["user"]["username"]
        item["instagram"]["media"] = requests.get(item["instagram"]["profile"] + "/?__a=1").json()
        if "twitter" not in item:
            twitter = scrapy.Request("https://twitter.com/i/search/typeahead.json?count=1&result_type=users&q=" + item["name"],
                callback=self.twitter)
            twitter.meta["item"] = item
            yield twitter
        if "twitter" in item and "instagram" in item:
            yield item

    def twitter(self, response):
        item = response.meta["item"]
        item["twitter"] = dict()
        jsonresponse = json.loads(response.body_as_unicode())
        item["twitter"]["username"] = jsonresponse["users"][0]["screen_name"]
        item["twitter"]["profile"] = "https://twitter.com/" + item["twitter"]["username"]
        timeline = self.client.request("https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=" + item["twitter"]["username"] + "&count=200")
        item["twitter"]["media"] = timeline
        if "instagram" not in item:
            instagram = scrapy.Request("https://www.instagram.com/web/search/topsearch/?context=blended&query=" + item["name"],
                callback=self.instagram)
            instagram.meta["item"] = item
            yield instagram
        if "twitter" in item and "instagram" in item:
            yield item
