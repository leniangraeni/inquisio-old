from scrapy import Spider
from scrapy import Request

from datetime import datetime

from berita_scraper.items import BeritaScraperItem

class KompasSpider(Spider):
	name = 'kompas'
	allowed_domains = ['kompas.com']
	start_urls = [
		'https://indeks.kompas.com',
		]

	# METHOD INISIASI
	def __init__(self, kategori="all", tanggal=None):
		self.kategori = kategori
		self.tanggal = tanggal if tanggal is not None else datetime.now().strftime("%Y-%m-%d")

	# METHOD REQUEST PERTAMA
	def start_requests(self):
		for url in self.start_urls:
			absolute_url = url + "/?site={}&date={}".format(k=self.kategori, t=self.tanggal)
			
			# Request URL
			yield Request(url=absolute_url, callback=self.parse)

	# METHOD PARSE UTAMA
	def parse(self, response):
		# Ekstraksi URL dari artikel dan request ke URL artikel
		daftar_url_berita = response.xpath('//a[@class="article__link"]/@href').extract()
		for url_berita in daftar_url_berita:
			absolute_url_berita = url_berita + '?page=all'
			yield Request(url=absolute_url_berita, callback=self.parse_info)

		# Request ke halaman berikutnya
		url_halaman_berikutnya = response.xpath('//a[@rel="next"]/@href').extract_first()
		absolute_url_halaman_berikutnya = response.urljoin(url_halaman_berikutnya)
		yield Request(url=absolute_url_halaman_berikutnya, callback=self.parse)

	# METHOD PARSE INFO
	def parse_info(self, response):
		item = BeritaScraperItem({
					'judul'		: response.xpath('//h1[@class="read__title"]/text()').extract_first(),
					'kategori'	: response.xpath('//li[@class="breadcrumb__item"]/a/span/text()').extract()[1:],
					'tanggal'	: response.xpath('//div[@class="read__time"]/text()').extract_first(),
					'isi'		: response.xpath('//div[@class="read__content"]/p//text()').extract(),
					'jumlah_sk'	: response.xpath('//div[@class="total_comment_share"]/text()').extract_first(),
					})
		yield item
