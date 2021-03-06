import logging
from multiprocessing import Process

import utils
from parser.parser import Parser
from .frontier import Frontier
from .webpage import WebPage


class Crawler(Process):
    def __init__(self,
                 user_agent: str,
                 frontier: Frontier,
                 parser: Parser,
                 max_pages_count: int = 1000,
                 max_depth: int = 10,
                 delay_ms: int = 30,
                 frontier_dump_delay_s: int = 10 * 60):
        self.user_agent = user_agent
        self.frontier = frontier
        self.parser = parser
        self.max_pages_count = max_pages_count
        self.max_depth = max_depth
        self.delay_ms = delay_ms
        self.frontier_dump_delay_s = frontier_dump_delay_s

        self.pages_count = 0

        self._logger = logging.getLogger(self.__class__.__name__)
        super().__init__()

    def run(self):
        start_time = utils.current_time_ms()
        last_dump_time = utils.current_time_ms()

        self._logger.info("Start downloading pages...")

        while not self.frontier.is_empty() and self.pages_count < self.max_pages_count:
            website = self.frontier.get_website()
            time_ms = utils.current_time_ms()

            if time_ms > last_dump_time + self.frontier_dump_delay_s * 1000:
                self.frontier.dump()
                last_dump_time = time_ms

            # skip the iteration if the waiting time has not passed yet
            crawler_delay = website.crawl_delay(self.user_agent)
            if not crawler_delay:
                crawler_delay = self.delay_ms
            if website.last_time + crawler_delay > time_ms:
                continue

            url, depth = website.get_url()
            web_page = WebPage(url)

            try:
                if web_page.load(self.user_agent):
                    # try to parse page
                    if not web_page.no_cache:
                        if self.parser.parse(web_page):
                            self.pages_count += 1
                            self._logger.debug("Successfully parsed page: {}".format(url))

                    # try to extract urls
                    if not web_page.no_follow and depth < self.max_depth:
                        self.frontier.add_urls(web_page.get_urls(), depth + 1, self.user_agent)
                else:
                    self._logger.warning("Failed to load url: {}".format(url))
            except Exception as e:
                self._logger.exception("An exception occured while loading or processing url: {}".format(url))
            # update time
            website.last_time = utils.current_time_ms()

        duration = utils.current_time_ms() - start_time
        self._logger.info("Finished downloading pages! Pages count: {} Total time: {} ms".format(self.pages_count,
                                                                                                 duration))
