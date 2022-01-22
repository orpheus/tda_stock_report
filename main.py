import csv
import json
from os import environ
from pydoc import describe
from time import sleep, time

from bs4 import BeautifulSoup as bs4

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from soup import extract_ticker_data_from_html
from portfolios import portfolios

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


def fetch_ticker_data(ticker):
    sleep(1) # Give some padding time in between tickers
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

    def did_ticker_load(xpath):
        try:
            stock_ticker_elem = driver.find_element(By.XPATH, xpath)
            ticker_text = stock_ticker_elem.get_attribute('innerText')
            print("Ticker Text: {} == {}".format(ticker, ticker_text))
            if ticker_text == ticker:
                return True
        except:
            return False

    count = 0 # ~30sec timeout
    max_timeout_sec = 5
    while count < max_timeout_sec:
        stock_frame = did_ticker_load("//span[@class='exchange']/span[@class='symbol']")
        etf_mf_frame = did_ticker_load("//h2[@id='companyName']/span[@class='symbol']")
        
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

    print("ERROR :: {} :: Failed to find ticker in frame during frame load".format(ticker))
    return {}
        

    # ----------- write to file -------------

    # html = driver.page_source

    # with open('ticker_data/{}.html'.format(ticker), 'w') as out_file:
    #     out_file.write(html)
    #     print('Wrote {} frame html to file'.format(ticker))

    # ----------- write to file -------------


# Cache ticker data to skip repeat pulls
ticker_cache = {}


# Returns - {[ticker]: [data], ...}
def generate_report(tickers):
    print("Generating portfolio report..")
    report_map = {}
    for ticker in tickers:
        if ticker in ticker_cache:
            report_map[ticker] = ticker_cache[ticker]
        else:
            data = fetch_ticker_data(ticker)
            data['ticker'] = ticker
            data['link'] = driver.current_url

            ticker_cache[ticker] = data
            report_map[ticker] = data

    print("Portfolio report generated")
    return report_map


# Returns - {[investor]: [portfolio_report]}
def generate_portfolio_report(portfolios):
    portfolio_report = {}
    for investor in portfolios:
        print("Generating portfolio report for: {}".format(investor))
        report_map = generate_report(portfolios[investor])
        portfolio_report[investor] = report_map
    
    return portfolio_report


def ticker_data_to_row(ticker_data):
    ticker = ticker_data.get('ticker')
    profile = ticker_data.get('profile')
    company_name = ticker_data.get('company_name')
    current_price = ticker_data.get('current_price')
    market_cap = ticker_data.get('market_cap')
    avg_vol_ten_day = ticker_data.get('avg_vol_ten_day')
    eps = ticker_data.get('eps')
    p_e_ratio = ticker_data.get('p_e_ratio')
    ann_dividend_over_yield = ticker_data.get('ann_dividend_over_yield')
    percent_held_by_institutions = ticker_data.get('percent_held_by_institutions')

    link = ticker_data.get('link')
    prospectus_link = ticker_data.get('prospectus_link')
    gross_expense_ratio = ticker_data.get('gross_expense_ratio')
    net_expense_ratio = ticker_data.get('net_expense_ratio')
    total_assets = ticker_data.get('total_assets')
    distribution_yield = ticker_data.get('distribution_yield')
    fund_inception = ticker_data.get('fund_inception')
    ex_dividend_date = ticker_data.get('ex_dividend_date')
    description = ticker_data.get('description')
    description = description.strip() if description is not None else None

    market_returns = ticker_data.get('market_returns') or {'market_return': None, 'nav_return': None}
    
    mr_one_month = market_returns.get('one_month')
    mr_one_month = mr_one_month.get('market_return') if mr_one_month is not None else None

    mr_three_month = market_returns.get('three_month')
    mr_three_month = mr_three_month.get('market_return') if mr_three_month is not None else None

    mr_six_month = market_returns.get('six_month')
    mr_six_month = mr_six_month.get('market_return') if mr_six_month is not None else None

    mr_year_to_date = market_returns.get('year_to_date')
    mr_year_to_date = mr_year_to_date.get('market_return') if mr_year_to_date is not None else None

    mr_year = market_returns.get('year')
    mr_year = mr_year.get('market_return') if mr_year is not None else None

    mr_three_year = market_returns.get('three_year')
    mr_three_year = mr_three_year.get('market_return') if mr_three_year is not None else None

    mr_five_year = market_returns.get('five_year')
    mr_five_year = mr_five_year.get('market_return') if mr_five_year is not None else None

    mr_ten_year = market_returns.get('ten_year')
    mr_ten_year = mr_ten_year.get('market_return') if mr_ten_year is not None else None

    mr_inception = market_returns.get('inception')
    mr_inception = mr_inception.get('market_return') if mr_inception is not None else None

    return [
        company_name,
        ticker,
        profile,
        gross_expense_ratio,
        net_expense_ratio,
        total_assets,
        ann_dividend_over_yield,
        distribution_yield,
        fund_inception,
        mr_one_month,
        mr_three_month,
        mr_six_month,
        mr_year_to_date,
        mr_year,
        mr_three_year,
        mr_five_year,
        mr_ten_year,
        mr_inception,
        current_price,
        eps,
        p_e_ratio,
        market_cap,
        link,
        prospectus_link,
        description
    ]


header_row = [
    'Company Name',
    'Ticker',
    'Type',
    'Gross Exp Ratio',
    'Net Exp Ratio',
    'Total Assets',
    'Ann Dividend/Yield',
    'Distribution Yield',
    'Fund Inception',
    '1m MR',
    '3m MR',
    '6m MR',
    'YTD MR',
    '1yr MR',
    '3yr MR',
    '5yr MR',
    '10yr MR',
    'Inception MR',
    'Cur Price',
    'EPS',
    'P/E Ratio',
    'Market Cap',
    'Link',
    'Prospectus',
    'Description'
]


def write_portfolios_to_csv(portfolio_report):
    with open('portfolios.csv', 'w', newline='') as f:
        writer = csv.writer(f, delimiter=',')
        writer.writerow(header_row)
        for investor in portfolio_report:
            portfolio = portfolio_report[investor]
            writer.writerow([])
            writer.writerow([investor])

            for ticker in portfolio:
                writer.writerow(ticker_data_to_row(portfolio[ticker]))


def write_from_json_dump():
    with open('portfolio_report_dump.json', 'r') as data:
        portfolio_report = json.load(data)
        write_portfolios_to_csv(portfolio_report)

def run():
    print("Starting..")
    open_tdameritrade()
    login()

    portfolio_report = generate_portfolio_report(portfolios)

    # Save the json to a file to have for reference and in case of error
    with open('portfolio_report_dump.json', 'w') as f:
         f.write(json.dumps(portfolio_report))
        
    write_portfolios_to_csv(portfolio_report)

    print("Done.")


if __name__ == '__main__':
    run()
    # write_from_json_dump()
