from os import environ
from time import sleep, time

from bs4 import BeautifulSoup as bs4

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from soup import extract_etf_data_from_file, extract_ticker_data_from_html


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
    'SDGA',
    'AMRC',
    'SWPPX'
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


def wait_until(EC=None, timeout_msg=None, timeout=10):
    try:
        WebDriverWait(driver, timeout).until(EC)
    except TimeoutException:
        if timeout_msg:
            print(timeout_msg)
        return 1


# Use to increase the wait time of the first ticker search
first_load=True


def fetch_ticker_data(ticker):
    driver.switch_to.default_content()

    print("Fetching data for ticker: {}..".format(ticker))
    search = driver.find_element(By.ID, "siteSearch")
    search.clear()
    search.send_keys(ticker)
    search.send_keys(Keys.RETURN)
    
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.ID, 'main')))
    except TimeoutException:
        print('Page timed out waiting for main iframe to load.')
        return None

    driver.switch_to.frame('main')

    # ----------- implement code below -------------

    def did_ticker_load(xpath, for_):
        try:
            stock_ticker_elem = driver.find_element(By.XPATH, xpath)
            ticker_text = stock_ticker_elem.get_attribute('innerText')
            if ticker_text == ticker:
                return True
        except:
            return False

    count = 0 # ~30sec timeout
    while count < 30:
        stock_frame = did_ticker_load("//span[@class='exchange']/span[@class='symbol']", for_="stock frame")
        etf_mf_frame = did_ticker_load("//h2[@id='companyName']/span[@class='symbol']", for_="etf/mf frame")
        
        print(stock_frame, etf_mf_frame)
        if stock_frame or etf_mf_frame:
            profile_title = driver.find_element(By.XPATH, '/html/head/title').get_attribute('innerText')

            if profile_title == 'Mutual Fund Profiles':
                return extract_ticker_data_from_html('MF', driver.page_source)

            if profile_title == 'Stock Summary':
                return extract_ticker_data_from_html('STOCK', driver.page_source)

            if profile_title == 'ETF Profile':
                return extract_ticker_data_from_html('ETF', driver.page_source)
            
            print("ERROR :: Unknown profile_title :: {}".format(profile_title))

        count += 1
        print('Loading stock frame...')
        sleep(1)

    if count > 30:
        print("ERROR :: {} :: Failed to find ticker in frame during frame load".format(ticker))
        return None, "ERROR :: {} :: Failed to find ticker in frame during frame load".format(ticker)

    
    # determine asset type via frame title or other means

    # switch on asset type and extract data
        # ticker_data = extract_ticker_data_from_html(<asset_type>, driver.page_source)
        # global ticker_data_map
        # ticker_data_map[ticker] = ticker_data
        # return

    # ----------- remove code below -------------

    # global first_load
    # wait_time = 3 if first_load else 1

    # stock_frame = wait_until(EC.presence_of_element_located((By.ID, 'layout-header')), timeout=wait_time)
    # # if not 1 (err), then wait until ticker is located __somewhere__ then skip the rest
    # etf_frame = wait_until(EC.presence_of_element_located((By.ID, 'companyName')), timeout=wait_time)
    # # if not 1 (err), then wait until ticker is located __somewhere__ then skip the rest
    # # bond_frame etc

    # if stock_frame is not None and etf_frame is not None:
    #     return None, "Could not find Stock or ETF frame"

    # first_load = False

    # html = driver.page_source

    # with open('ticker_data/{}.html'.format(ticker), 'w') as out_file:
    #     out_file.write(html)
    #     print('Wrote {} frame html to file'.format(ticker))

 # ----------- remove code above -------------

def generate_report():
    print("Generating report..")
    report_map = {}
    for ticker in tickers:
        data = fetch_ticker_data(ticker)
        if data is None:
            return
        print(data)
        print('\n')


def run():
    print("Starting..")
    open_tdameritrade()
    login()
    generate_report()


if __name__ == '__main__':
    run()
