import yfinance as yf

apple = yf.download("AAPL", period="5y")
print(apple.head())
