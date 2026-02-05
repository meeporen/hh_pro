from playwright.sync_api import sync_playwright
import os
import time

class Config:
    def __init__(self, storage_path: str, url: str, interval: float, headless: bool):
        self.storage_path = storage_path
        self.url = url
        self.interval = interval
        self.headless = headless

        def interval_in_hour(self):
            return int(self.interval_hours * 3600)
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

    def auto_up(self):
        self.page.locator('[data-qa="mainmenu_profileAndResumes"]').click()

        update_btn = self.page.locator(
            '[data-qa="resume-update-button resume-update-button_actions"]'
        )
        update_btn.wait_for(state="visible", timeout=10000)
        update_btn.click()

        confirm_btn = self.page.locator(
            '[data-qa="bot-update-resume-modal__action-button"]'
        )
        confirm_btn.wait_for(state="visible", timeout=10000)
        confirm_btn.click()

    def run_cycle(self):
        self.start()
        try:
            self.ensure_auth()
            self.auto_up()
        finally:
            self.close()

def main():
    STORAGE_PATH = r"C:\work\hh_pro\hh_auth.json"
    URL = "https://hh.ru"
    N_HOURS = 4.01

    config = Config(
        storage_path=STORAGE_PATH,
        url=URL,
        interval=N_HOURS,
        headless=False,
    )

    with sync_playwright() as p:
        bot = HHBot(p, config)
        print(f"Скрипт запущен. Автообновление каждые {config.interval} часов.")

        while True:
            try:
                bot.run_cycle()
                print("Резюме обновлено.")
            except Exception as e:
                print(f"Ошибка: {e}")

            print(f"Ждём {config.interval} часов до следующего обновления...")
            time.sleep(config.interval)


if __name__ == "__main__":
    main()