from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
import re
from datetime import datetime
import os
import time

class Config:
    def __init__(self, storage_path: str, url: str, headless: bool):
        self.storage_path = storage_path
        self.url = url
        self.headless = headless

class HHBot:
    def __init__(self, playwright, config: Config):
        self.playwright = playwright
        self.config = config

        self.browser = None
        self.context = None
        self.page = None

    def start(self):
        self.browser = self.playwright.chromium.launch(headless=self.config.headless)
        if os.path.exists(self.config.storage_path):
            self.context = self.browser.new_context(
                storage_state=self.config.storage_path
            )
        else:
            self.context = self.browser.new_context()
        self.page = self.context.new_page()
        self.page.goto(self.config.url, wait_until="domcontentloaded")

    def close(self):
        try:
            if self.browser:
                self.browser.close()
        finally:
            self.browser = None
            self.context = None
            self.page = None

    def ensure_auth(self):
        if not os.path.exists(self.config.storage_path):
            self.login_and_save_state()

    def login_and_save_state(self):
        self.page.goto(self.config.url, wait_until="domcontentloaded")

        self.page.click('[data-qa="login"]')
        self.page.locator('[data-qa="submit-button"]').click()

        num = input("Введите номер телефона: ")
        self.page.locator('[data-qa="magritte-phone-input-national-number-input"]').fill(num)
        self.page.locator('[data-qa="submit-button"]').click()

        code = input("Введите код OTP: ")
        otp_field = self.page.locator('[data-qa="applicant-login-input-otp"]')
        otp_field.click()
        otp_field.type(code)
        button = self.page.locator('[data-qa="applicant-login-button-code-sender"]')
        if button.is_enabled():
            button.click()

        self.context.storage_state(path=self.config.storage_path)

    def auto_up(self) -> bool:
        self.page.locator('[data-qa="mainmenu_profileAndResumes"]').click()

        update_btn = self.page.locator(
            '[data-qa="resume-update-button resume-update-button_actions"]'
        )

        try:
            update_btn.wait_for(state="visible", timeout=10000)
        except PlaywrightTimeoutError:
            return False

        update_btn.click()

        confirm_btn = self.page.locator(
            '[data-qa="bot-update-resume-modal__action-button"]'
        )
        confirm_btn.wait_for(state="visible", timeout=10000)
        confirm_btn.click()
        return True

    def check_time(self) -> int:
        text = self.page.locator('[data-qa="title-description"]').first.inner_text()

        time_match = re.search(r'\d{2}:\d{2}', text)
        if not time_match:
            return 60

        h, m = map(int, time_match.group(0).split(':'))
        target_sec = h * 3600 + m * 60

        now = datetime.now()
        now_sec = now.hour * 3600 + now.minute * 60 + now.second

        delta = target_sec - now_sec

        if delta < 0:
            delta += 24 * 3600

        return delta + 10

    def run_cycle(self) -> bool:
        self.start()
        try:
            self.ensure_auth()
            update = self.auto_up()
            if update:
                wait_sec = 4*3600+30
                return wait_sec
            else:
                wait_sec = self.check_time()

            return wait_sec

        finally:
            self.close()

def main():
    STORAGE_PATH = r"C:\work\hh_pro\hh_auth.json"
    URL = "https://hh.ru"

    config = Config(
        storage_path=STORAGE_PATH,
        url=URL,
        headless=False,
    )

    with sync_playwright() as p:
        bot = HHBot(p, config)
        print(f"Скрипт запущен. Автообновление каждые часов.")

        while True:
            try:
                wait_sec = bot.run_cycle()
            except Exception as e:
                print(f"Ошибка в цикле: {e}")
                wait_sec = 300

            print(f"Ждём {wait_sec // 60} минут до следующей попытки")
            time.sleep(wait_sec)


if __name__ == "__main__":
    main()