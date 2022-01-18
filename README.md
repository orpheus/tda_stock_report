# Equity Report Bot

Generate a report of equity asset properties given a list of tickers

## Double-check Selenium Chrome Driver

Please make sure you have Chrome 97 installed or install the latest
[ChromeDriver](https://sites.google.com/chromium.org/driver/downloads?authuser=0)
and put it in the `bin/` folder

## Create VENV

`source bin/venv`

## Install Deps

`pip3 install -r requirements.txt`

## Env Vars

Either export these before the `run` command or prefix the run command
with them

```
TDA_USER=titanroark
TDA_PASS=password
```

## Run

`python3 main.py`


## TDA Authentication

The script will login to TD Ameritrade and hit an authentication page in
which it will send a confirmation code to your phone. The script will
wait 30 seconds for you to get the code and enter it until it times out.
It waits for the page to render the search input with `id=siteSearch`
