from re import S
from bs4 import BeautifulSoup as bs4

def extract_ticker_data_from_html(asset_type, html):
    if asset_type == 'STOCK':
        return extract_stock_data(html)
    
    if asset_type == 'MF':
        return extract_mutual_fund_data(html)

    if asset_type == 'ETF':
        return extract_etf_data(html)


def extract_etf_data_from_file(html_file_path="ticker_data/DSI.html"):
    with open(html_file_path) as fp:
        return extract_etf_data(fp)


def extract_mutual_fund_data_from_file(html_file_path="ticker_data/SWPPX.html"):
    with open(html_file_path) as fp:
        return extract_mutual_fund_data(fp)


def extract_stock_data_from_file(html_file_path="ticker_data/AMRC.html"):
    with open(html_file_path) as fp:
        return extract_stock_data(fp)


def extract_etf_data(html):
    # toDo: add ticker name as arg
    soup = bs4(html, 'lxml')

    def get_sum_data(text):
        ret = soup.find(text=text)
        if ret.parent.name == 'a':
            return ret.parent.parent.next_sibling.next_sibling.text
        return ret.parent.next_sibling.next_sibling.text

    def get_market_return(tr):
        title = tr.td
        market_return = title.next_sibling.next_sibling
        nav_return = market_return.next_sibling.next_sibling
        return {'market_return': market_return.text, 'nav_return': nav_return.text}

    profile = soup.title.text
    company_name = soup.find('h2', id='companyName').text
    prospectus_link = 'research.ameritrade.com' + soup.find('a', 'prospectusText')['href']
    gross_expense_ratio = get_sum_data('Gross Expense Ratio')
    net_expense_ratio = get_sum_data('Net Expense Ratio')
    total_assets = get_sum_data('Total Assets')
    distribution_yield = get_sum_data('Distribution Yield (TTM)')
    ann_dividend_over_yield = get_sum_data('Ann. Dividend/Yield')
    ex_dividend_date = get_sum_data('Ex-Dividend Date')
    fund_inception = get_sum_data('Fund Inception')
    current_price = soup.find('div', id='quoteContainer').div.div.text
    description = soup.find(id='module-trailingTotalReturns').previous_sibling.previous_sibling.next_element.next_element.next_element.next_element

    market_return_table = soup.find(id='table-trailingTotalReturnsTable').tbody
    market_return_rows = market_return_table.find_all('tr')
    market_returns = {
        'one_month': get_market_return(market_return_rows[0]),
        'three_month': get_market_return(market_return_rows[1]),
        'six_month': get_market_return(market_return_rows[2]),
        'year_to_date': get_market_return(market_return_rows[3]),
        'year': get_market_return(market_return_rows[4]),
        'three_year': get_market_return(market_return_rows[5]),
        'five_year': get_market_return(market_return_rows[6]),
        'ten_year': get_market_return(market_return_rows[7]),
        'inception': get_market_return(market_return_rows[8])
    }

    ticker_data = {
        'profile': profile,
        'company_name': company_name,
        'prospectus_link': prospectus_link,
        'gross_expense_ratio': gross_expense_ratio,
        'net_expense_ratio': net_expense_ratio,
        'total_assets': total_assets,
        'distribution_yield': distribution_yield,
        'ann_dividend_over_yield': ann_dividend_over_yield,
        'ex_dividend_date': ex_dividend_date,
        'fund_inception': fund_inception,
        'current_price': current_price,
        'description': description,
        'market_returns': market_returns
    }

    return ticker_data


def extract_mutual_fund_data(html):
    # toDo: add ticker name as arg
    soup = bs4(html, 'lxml')

    def get_market_return(tr):
        title = tr.td
        market_return = title.next_sibling.next_sibling
        nav_return = market_return.next_sibling.next_sibling
        return {'market_return': market_return.text, 'nav_return': nav_return.text}

    def get_sum_data(text):
        ret = soup.find(text=text)
        return ret.parent.next_sibling.next_sibling.text


    profile = soup.title.text
    company_name = soup.find('h2', id='companyName').text
    prospectus_link = 'research.ameritrade.com' + soup.find('a', 'prospectusText')['href']
    gross_expense_ratio = get_sum_data('Gross Expense Ratio')
    net_expense_ratio = get_sum_data('Net Expense Ratio')
    total_assets = get_sum_data('Total Assets')
    distribution_yield = get_sum_data('Distribution Yield (TTM)')
    fund_inception = get_sum_data('Fund Inception')
    current_price = soup.find('div', id='quoteContainer').div.div.text
    ## Different than ETF
    description = soup.find(id='module-trailingTotalReturns').previous_sibling.previous_sibling.previous_sibling.previous_sibling.next_element.next_element.next_element.next_element

    market_return_table = soup.find(id='table-trailingTotalReturnsTable').tbody
    market_return_rows = market_return_table.find_all('tr')
    market_returns = {
        'one_month': get_market_return(market_return_rows[0]),
        'three_month': get_market_return(market_return_rows[1]),
        ## Different than ETF -- doesn't have six_month
        'year_to_date': get_market_return(market_return_rows[2]),
        'year': get_market_return(market_return_rows[3]),
        'three_year': get_market_return(market_return_rows[4]),
        'five_year': get_market_return(market_return_rows[5]),
        'ten_year': get_market_return(market_return_rows[6]),
        'inception': get_market_return(market_return_rows[7])
    }

    ticker_data = {
        'profile': profile,
        'company_name': company_name,
        'prospectus_link': prospectus_link,
        'gross_expense_ratio': gross_expense_ratio,
        'net_expense_ratio': net_expense_ratio,
        'total_assets': total_assets,
        'distribution_yield': distribution_yield,
        'fund_inception': fund_inception,
        'current_price': current_price,
        'description': description,
        'market_returns': market_returns
    }

    return ticker_data


def extract_stock_data(html):
    # toDo: add ticker name as arg
    soup = bs4(html, 'lxml')
    
    def get_sum_data(text):
        ret = soup.find(text=text)
        if ret.parent.name == 'a':
            return ret.parent.parent.parent.next_sibling.text
        return ret.parent.next_sibling.text

    profile = soup.title.text
    company_name = soup.find('span', 'stock-title').text
    current_price = soup.find(text='Closing Price').parent.next_sibling.text
    market_cap = get_sum_data('Market Cap')
    avg_vol_ten_day = get_sum_data('Avg Vol (10-day)')
    eps = get_sum_data('EPS (TTM, GAAP)')
    p_e_ratio = get_sum_data('P/E Ratio (TTM, GAAP)')
    ann_dividend_over_yield = get_sum_data('Annual Dividend/Yield')
    percent_held_by_institutions = get_sum_data('% Held by Institutions')

    ticker_data = {
        'profile': profile,
        'company_name': company_name,
        'market_cap': market_cap,
        'avg_vol_ten_day': avg_vol_ten_day,
        'avg_vol_ten_day': avg_vol_ten_day,
        'eps': eps,
        'p_e_ratio': p_e_ratio,
        'ann_dividend_over_yield': ann_dividend_over_yield,
        'current_price': current_price,
        'percent_held_by_institutions': percent_held_by_institutions
    }

    return ticker_data

if __name__ == '__main__':
    # print(extract_stock_data_from_file())
    # print(extract_mutual_fund_data_from_file())
    print(extract_etf_data_from_file())