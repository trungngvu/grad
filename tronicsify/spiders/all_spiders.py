# import scrapy
# from scrapy.crawler import CrawlerProcess
# from scrapy.utils.project import get_project_settings

# from tronicsify.spiders.gearvn import GearvnSpider
# from tronicsify.spiders.hacom import HacomSpider
# from tronicsify.spiders.hoanghapc import HoanghapcSpider
# from tronicsify.spiders.nguyencongpc import NguyencongpcSpider
# from tronicsify.spiders.phongvu import PhongvuSpider
# from tronicsify.spiders.tncstore import TncstoreSpider


# settings = get_project_settings()
# process = CrawlerProcess(settings)
# process.crawl(GearvnSpider)
# process.crawl(HacomSpider)
# process.crawl(NguyencongpcSpider)
# process.crawl(HoanghapcSpider)
# process.crawl(PhongvuSpider)
# process.crawl(TncstoreSpider)
# process.start()  # the script will block here until all crawling jobs are finished