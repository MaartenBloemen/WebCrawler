from scraper import WebScrapeJob

'''job = WebScrapeJob('www2.telenet.be', ['https://www2.telenet.be/nl/'], [])
job.start()'''


job = WebScrapeJob('proximus.be', ['https://www.proximus.be/nl/id_personal/particulieren.html'], [], -1)
job.start()
