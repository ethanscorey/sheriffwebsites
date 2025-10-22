# Scrapy settings for sheriffwebsites project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from dotenv import load_dotenv

load_dotenv()

BOT_NAME = "sheriffwebsites"

SPIDER_MODULES = ["sheriffwebsites.spiders"]
NEWSPIDER_MODULE = "sheriffwebsites.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
# USER_AGENT = "sheriffwebsites (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Concurrency and throttling settings
# CONCURRENT_REQUESTS = 16
CONCURRENT_REQUESTS_PER_IP = 1
DOWNLOAD_DELAY = 10

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
# DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
# }

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    "sheriffwebsites.middlewares.SheriffwebsitesSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    "sheriffwebsites.middlewares.SheriffwebsitesDownloaderMiddleware": 543,
# }

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES = {
#    "sheriffwebsites.pipelines.SheriffwebsitesPipeline": 300,
# }

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = "httpcache"
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
FEED_EXPORT_ENCODING = "utf-8"

SHERIFF_SITES = {
    "Bryan": {
        "site": "https://bryancountyso.com",
        "results_key": "querybookings",
        "key": "bookie",
    },
    "Caddo": {"site": "https://caddocountysheriff.com", "key": "bookie"},
    "Canadian": {"site": "https://www.ccsheriff.net", "key": "bookie"},
    "Carter": {
        "site": "https://cartercountysheriff.us",
        "results_key": "querybookings",
        "key": "querybookie",
    },
    "Cimarron": {
        "site": "https://cimarroncoso.gov",
        "results_key": "querybookings",
        "key": "querybookie",
    },
    "Craig": {"site": "https://craigcountyso.com", "key": "bookie"},
    "Creek": {
        "site": "https://creekcountysheriff.gov",
        "results_key": "querybookings",
        "booking_key": "InmateId",
        "key": "querybookie",
    },
    "Custer": {
        "site": "https://custercountysheriff.com",
        "results_key": "querybookings",
        "key": "bookie",
    },
    "Delaware": {"site": "https://delcosheriff.org", "key": "bookie"},
    "Lincoln": {
        "site": "https://lincolncountysheriffok.gov",
        "results_key": "querybookings",
        "key": "querybookie",
        "booking_key": "InmateId",
    },
    "Logan": {"site": "https://logancountyso.org", "key": "bookie"},
    "Love": {
        "site": "https://lovecosheriff.com",
        "results_key": "querybookings",
        "key": "querybookie",
    },
    "Major": {"site": "https://majorcosheriff.com", "key": "bookie"},
    "Pawnee": {
        "site": "https://www.pawneecountysheriff.com",
        "results_key": "querybookings",
        "key": "bookie",
    },
    "Payne": {
        "site": "https://paynecountyok.gov",
        "results_key": "querybookings",
        "key": "querybookie",
    },
    "Sequoyah": {"site": "https://www.scsok.org", "key": "bookie"},
    "Wagoner": {
        "site": "https://wagonercountyso.org",
        "booking_endpoint": "/dmxConnect/api/Booking/getBookie.php",
        "key": "queryInmate",
    },
    "Washington": {"site": "https://www.washingtoncosheriff.com", "key": "bookie"},
}

FEEDS = {
    "az://my-container/exports/%(name)s/%(time)s.csv": {
        "format": "csv",
        "encoding": "utf-8",
        "item_classes": ["sheriffwebsites.items.BookingItem"],
    }
}

FEED_STORAGES = {"az": "sheriffwebsites.feedstorages.azure_blob.AzureBlobFeedStorage"}
