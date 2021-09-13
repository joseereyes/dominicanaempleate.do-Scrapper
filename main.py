# from service.scrapper import jobs_scrapper
from service.scrapper_realtime import realtime_scrapper


app = realtime_scrapper()

# jobs_scrapper()