from bs4 import BeautifulSoup as bs4

def extract_ticker_data_from_html(ticker, asset_type, html):
    print("Switch on asset type (stock, etf, bond, etc")
    # extract_stock_data
    # extract_etf_data
    # etc


def extract_etf_data_from_file(html_file_path="ticker_data/DSI.html"):
    with open(html_file_path) as fp:
        return extract_etf_data(fp)


# Works for Mutual Funds
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


if __name__ == '__main__':
    print(extract_etf_data_from_file())