from os import environ

from bs4 import BeautifulSoup as bs4

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


tickers = [
    'DSI',
    'CGW',
    'ESG',
    'USSG',
    'PHO',
    'ETHO',
    'VEGN',
    'KRMA',
    'ESG',
    'ESGV',
    'SUSA',
    'ERTH',
    'FIW',
    'SDGA'
]

chromedriver_path = './bin/chromedriver'
service = Service(executable=chromedriver_path)
driver = webdriver.Chrome(executable_path=chromedriver_path)

tda_user = environ.get('TDA_USER')
tda_pass = environ.get('TDA_PASS')
tda_url = "https://invest.ameritrade.com/grid/p/site#r=home"
tda_auth_page_title = "TD Ameritrade Authentication"
tda_auth_page_contains = "Authentication"

def open_tdameritrade():
    print("Opening TD Ameritrade..")
    driver.get(tda_url)
    assert "TD Ameritrade" in driver.title


def login():
    print("Logging in..")
    login_button = driver.find_element(By.CLASS_NAME, 'cafeLoginButton')
    login_button.click()

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username0")))
    except TimeoutException as e:
        print("ERROR: Was not able to find authentication page")
        print("ERROR: {}".format(e))
        driver.quit()
        return

    username_input = driver.find_element(By.ID, 'username0')
    password_input = driver.find_element(By.ID, 'password1')

    username_input.clear()
    password_input.clear()

    username_input.send_keys(tda_user)
    password_input.send_keys(tda_pass)
    password_input.send_keys(Keys.RETURN)

    driver.find_element(By.ID, 'accept').click()

    print("Waiting for manual auth entry..")
    try:
        element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "trustthisdevice0_0")))
    except TimeoutException as e:
        print("Error: TimeoutException: Could not find the `trust this device` element")
        driver.quit()
        return

    print("Auth code entered..")

    # element = driver.find_element(By.ID, "trustthisdevice0_0")
    # element.click()
    # driver.find_element(By.ID, 'accept').click()

    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "siteSearch")))
    except TimeoutException as e:
        print("Error: Timeout exception: Manual 2Auth not completed in time")
        driver.quit()
        return


def fetch_ticker_data(ticker):
    driver.switch_to.default_content()
    print("Fetching data for ticker: {}..".format(ticker))
    search = driver.find_element(By.ID, "siteSearch")
    search.clear()
    search.send_keys(ticker)
    search.send_keys(Keys.RETURN)
    # Need to sleep to allow JS to modify the page with data, else it
    # won't be found in the page source
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'main')))
    except TimeoutException:
        print('Page timed out waiting for stock page to load.')
        # driver.close()
        return 1

    driver.switch_to.frame('main')
    html = driver.page_source

    try:
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'companyName')))
    except TimeoutException:
        print('Timeout occured waiting for main iframe to load')
        return 1
 
    soup = bs4(html, "lxml")
    with open('ticker_data/{}.html'.format(ticker), 'w') as out_file:
        out_file.write(html)
        # toDo: write the correct html to static pages and use BS4 on
        # static files to get the logic correct and then import that
        # logic back here to grab all the necessary data


def generate_report():
    print("Generating report..")
    for ticker in tickers:
        ret = fetch_ticker_data(ticker)
        if ret != None:
            return 1


def run():
    print("Starting..")
    open_tdameritrade()
    login()
    generate_report()


if __name__ == '__main__':
    run()
