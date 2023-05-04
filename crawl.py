import requests
import asyncio
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
import time

def main():
    crawler = Crawler()
    place = input("Enter place:\n")

if __name__ == "__main__":
    main()

class Crawler:
    def __init__(self):
        self.browser = (
            sync_playwright()
            .start()
            .chromium.launch(
                headless=False,
            )
        )

        self.page = self.browser.new_page()
        self.page.set_viewport_size({"width": 1280, "height": 1080})

    def get_page(self):
        return self.page

    def go_to_page(self, url, wait_selector=None):
        self.page.goto(url=url if "://" in url else "http://" + url)
        self.client = self.page.context.new_cdp_session(self.page)
        self.page_element_buffer = {}
        if wait_selector:
            self.page.wait_for_selector(wait_selector)

    def scroll(self, direction):
        if direction == "up":
            self.page.evaluate(
                "(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop - window.innerHeight;"
            )
        elif direction == "down":
            self.page.evaluate(
                "(document.scrollingElement || document.body).scrollTop = (document.scrollingElement || document.body).scrollTop + window.innerHeight;"
            )

    def click(self, id):
        # Inject javascript into the page which removes the target= attribute from all links
        js = """
        links = document.getElementsByTagName("a");
        for (var i = 0; i < links.length; i++) {
            links[i].removeAttribute("target");
        }
        """
        self.page.evaluate(js)

        element = self.page_element_buffer.get(int(id))
        if element:
            x = element.get("center_x")
            y = element.get("center_y")
            
            self.page.mouse.click(x, y)
        else:
            print("Could not find element")
        print('clicking', id)

    def type(self, id, text):
        self.click(id)
        self.page.keyboard.type(text)
        print('typing', id, text)

    def enter(self):
        self.page.keyboard.press("Enter")