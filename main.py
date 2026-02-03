from playwright.sync_api import sync_playwright
import os

storage_path = r"C:\work\hhpro\hh_auth.json"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    if os.path.exists(storage_path):
        context = browser.new_context(storage_state=storage_path)
        page = context.new_page()
        page.goto("https://hh.ru", wait_until="domcontentloaded")

        page.locator('[data-qa="mainmenu_profileAndResumes"]').click()
        button = page.locator('[data-qa="resume-update-button resume-update-button_actions"]')
        button.wait_for(state="visible", timeout=10000)
        button.click()
        button = page.locator('[data-qa="bot-update-resume-modal__action-button"]')
        button.wait_for(state="visible", timeout=10000)
        button.click()

        input("Готово. Нажми Enter для выхода...")
    else:
        context = browser.new_context()
        page = context.new_page()
        page.goto("https://hh.ru", wait_until="domcontentloaded")

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
        page.locator('[data-qa="mainmenu_profileAndResumes"]').click()
        button = page.locator('[data-qa="resume-update-button resume-update-button_actions"]')
        button.wait_for(state="visible", timeout=10000)
        button.click()
        button = page.locator('[data-qa="bot-update-resume-modal__action-button"]')
        button.wait_for(state="visible", timeout=10000)
        button.click()
        input("Авторизация завершена. Enter — выход")

    browser.close()


