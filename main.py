from playwright.sync_api import sync_playwright
import os
import time

STORAGE_PATH = r"C:\work\hh_pro\hh_auth.json"
URL = "https://hh.ru"
N_HOURS = 4.01
INTERVAL = N_HOURS * 3600

def auto_up(page):
    page.locator('[data-qa="mainmenu_profileAndResumes"]').click()

    update_btn = page.locator(
        '[data-qa="resume-update-button resume-update-button_actions"]'
    )
    update_btn.wait_for(state="visible", timeout=10000)
    update_btn.click()

    confirm_btn = page.locator(
        '[data-qa="bot-update-resume-modal__action-button"]'
    )
    confirm_btn.wait_for(state="visible", timeout=10000)
    confirm_btn.click()

def login_and_save_state(page, context, storage_path):
    page.goto(URL, wait_until="domcontentloaded")

    page.click('[data-qa="login"]')
    page.locator('[data-qa="submit-button"]').click()

    num = input("Введите номер телефона: ")
    page.locator('[data-qa="magritte-phone-input-national-number-input"]').fill(num)
    page.locator('[data-qa="submit-button"]').click()

    code = input("Введите код OTP: ")
    otp_field = page.locator('[data-qa="applicant-login-input-otp"]')
    otp_field.click()
    otp_field.type(code)
    button = page.locator('[data-qa="applicant-login-button-code-sender"]')
    if button.is_enabled():
        button.click()

    context.storage_state(path=storage_path)

def run_cycle(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = (
        browser.new_context(storage_state=STORAGE_PATH)
        if os.path.exists(STORAGE_PATH)
        else browser.new_context()
    )
    page = context.new_page()
    page.goto(URL, wait_until="domcontentloaded")

    if not os.path.exists(STORAGE_PATH):
        login_and_save_state(page, context, STORAGE_PATH)

    auto_up(page)
    browser.close()


with sync_playwright() as p:
    print(f"Скрипт запущен. Автообновление каждые {N_HOURS} часов.")
    while True:
        try:
            run_cycle(p)
        except Exception as e:
            print(f"Ошибка: {e}")
        print(f"Ждём {N_HOURS} часов до следующего обновления...")
        time.sleep(INTERVAL)


