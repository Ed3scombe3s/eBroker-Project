import os
import csv
import time
import bcrypt
import pandas as pd
import yfinance as yf
import mplfinance as mpf


############### User Functions ############################





def Current_user(user): # Current user
    global current_user
    current_user = user

def clear(): # Clear the screen
    os.system('cls' if os.name == 'nt' else 'clear')

def creat_user(): # Create a new user
    clear()
    print("Create a new user")
    user = input("Enter your user name: ")
    user = user.capitalize()
    if user == "":
        return main()
    with open("users.txt", "r+") as file:
        for line in file:
            login_info = line.split()
            if login_info[0] == user:
                print("User already exists")
                time.sleep(2)
                return main()
    password = input("Enter your password: ")
    password = password.encode('utf-8')
    password = bcrypt.hashpw(password, bcrypt.gensalt())
    with open("users.txt", "a") as file:
        file.write(user + " " + str(password) + "\n")
    print("User created successfully!")
    add_user(user)
    time.sleep(1)
    main()

def login(): # Login to the system
    clear()
    print("Login to the system")
    user = input("Enter your user name: ")
    user = user.capitalize()
    password = input("Enter your password: ")
    with open("users.txt", "r") as file:
        for line in file:
            login_info = line.split()
            hashed = login_info[1].strip('b')
            hashed = hashed.replace("'", "")
            hashed = hashed.encode('utf-8')
            if user == login_info[0] and bcrypt.checkpw(password.encode(), hashed):
                print("Login successful!")
                Current_user(user)
                return True
        return False

def main(): # Main function
    clear()
    print("Welcome to the eTrader Platform!")
    print("1. Create a new user")
    print("2. Login")
    print("3. Exit")
    choice = input("Enter your choice: ")
    if choice == "1":
        creat_user()
    elif choice == "2":
        if login():
            LoggedIn()
        else:
            print("Login failed!")
            time.sleep(2)
            main()
    elif choice == "3":
        exit()
    else:
        clear()
        print("Invalid choice!")
        time.sleep(1)
        main()


def LoggedIn(): # Logged in menu
    clear()
    print(f'Hello, {current_user}!')
    print("1. Go to Portfolio")
    print("2. Logout")
    choice = input("Enter your choice: ")
    if choice == "1":
        Portfolio(current_user)
    elif choice == "2":
        main()
    else:
        clear()
        print("Invalid choice!")
        time.sleep(1)
        LoggedIn()









###########Portfolio Functions############




def add_user(user):
    with open('users_portfolio.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([user, 10_000, "No", "N/A", 0, 0, "N/A"])

def Balance(user):
    with open('users_portfolio.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == user:
                row[1] = float(row[1])
                print(f"Balance is: {row[1]:.2f}")
                global balance
                balance = row[1]
                balance = float(balance)
                

def Opened_Position(user):
    with open('users_portfolio.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == user:
                global postion_opened
                if row[2] == "Yes":
                    print(f"You have an opened {row[6].upper()} position")
                    print(f"Stock Ticker: {row[3]}")
                    print(f"Shares: {row[4]}")
                    print(f"Open Price: {row[5]}")

                    ticker = row[3]
                    price = get_live_price(ticker)
                    print(f"{ticker}'s Current price: {price}")

                    
                    postion_opened = True
                else:
                    postion_opened = False
                    print("You don't have any opened position")


def Open_Position(user):
    clear()
    print("1. Open a Long position")
    print("2. Open a Short position")
    print("3. Exit")

    option = input("Enter your option: ")
    global type
    if option == "1":
        type = "long"
        ticker, shares, open_price, new_balance = Open_a_pos(balance, user)
        update_user_portfolio(user, new_balance, "Yes", ticker, shares, open_price, type)
        Portfolio(user)

    elif option == "2":
        type = "short"
        ticker, shares, open_price, new_balance = Open_a_pos(balance, user)
        update_user_portfolio(user, new_balance, "Yes", ticker, shares, open_price, type)
        Portfolio(user)

    
    elif option == "3":
        Portfolio(user)
    else:
        clear()
        print("Invalid option!")
        time.sleep(1)
        Open_Position(user)


def Current_PNL(user):
    with open('users_portfolio.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == user:
                if row[2] == "Yes":
                    ticker = row[3]
                    price = get_live_price(ticker)
                    shares = row[4]
                    open_price = row[5]
                    type = row[6]
                    shares = float(shares)
                    open_price = float(open_price)
                    price = float(price)
                    if type == "long":
                        PNL = (price - open_price) * shares
                        print(f"Current PnL: {PNL:.2f}\n")
                    elif type == "short":
                        PNL = (open_price - price) * shares
                        print(f"Current PnL: {PNL:.2f}\n")
                else:
                    print("\n")


def Open_a_pos(balance, user):
    try:
        ticker = str(input("Enter the ticker symbol(meta, aapl, msft, tsla, amzn): "))
        open_price = get_live_price(ticker)
        print(f"{ticker}'s Current price: {open_price}")
        invest = int(input("Enter the amount of money you want to invest: "))
        if invest > balance:
            print("You don't have enough money!")
            time.sleep(1)
            Open_a_pos(user)
        shares = invest / open_price
        new_balance = balance - invest
        return ticker, shares, open_price, new_balance
    except:
        print("Invalid ticker!")
        time.sleep(1)
        Portfolio(user)

def Close_Position(user):
    clear()
    global balance
    with open('users_portfolio.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[0] == user:
                ticker = row[3]
                shares = float(row[4])
                open_price = float(row[5])
                type = row[6]
                close_price = get_live_price(ticker)
                close_price = float(close_price)
                invested = shares * open_price
                if type == "long":
                    profit = (close_price - open_price) * shares
                    new_balance = balance + invested + profit
                    update_user_portfolio(user, new_balance, "No", "N/A", 0, 0, "N/A") 

                elif type == "short":
                    profit = (open_price - close_price) * shares
                    new_balance = balance + invested + profit
                    
                else:
                    print("You don't have any opened position")
                    time.sleep(2)
                    Portfolio(user)

                update_user_portfolio(user, new_balance, "No", "N/A", 0, 0, "N/A") 
                print(f"You opened a {type} position on {ticker} of {shares:.4f} shares at a price of {open_price} for {invested:.2f} dollars")
                print(f"You sold your {shares:.4f} shares of {ticker} at {close_price} for a total of {invested + profit:.2f} dollars")
                print(f"Profit: {profit:.2f}")
                input("\nPress enter to continue")
                Portfolio(user)

def Portfolio(user):
    clear()
    print(f"{user}'s Portfolio")

    #check users balance
    Balance(user)
    
    #show if user has any open positions
    Opened_Position(user)

    Current_PNL(user)


    print("1. Open a position")
    print("2. Close current position")
    print("3. Live chart")
    print("4. Get live stock price")
    print("5. Back to main menu")
    print("\nPress Enter to refresh")

    option = input("Enter your option: ")
    if option == "1":
        if postion_opened == True:
            print("You already have an opened position!")
            time.sleep(1)
            Portfolio(user)
        else:
            Open_Position(user)

    elif option == "2":
        Close_Position(user)

    elif option == "3":
        try:
            data, ticker= get_market_data()
            plot_market_data(data, ticker)
            Portfolio(user)
        except:
            clear()
            print("Something went wrong!")
            time.sleep(2)
            Portfolio(user)

    elif option == "4":
        ticker = str(input("Enter the ticker symbol(meta, aapl, msft, tsla, amzn): "))
        i = 0
        clear()
        while  i < 10:
            price = get_live_price(ticker)
            print(f"{ticker}'s Current price: {price}")
            time.sleep(0.5)
            i += 1
            
        Portfolio(user)

    elif option == "5":
        LoggedIn()
    
    elif option == "":
        Portfolio(user)
    
    else:
        clear()
        print("Invalid option!")
        time.sleep(1)
        Portfolio(user)



def update_user_portfolio(user, balance, opened_position, ticker, shares, open_price, type):
    with open('users_portfolio.csv', 'r') as file:
        reader = csv.reader(file)
        lines = list(reader)
        for row in lines:
            if row[0] == user:
                row[1] = balance
                row[2] = opened_position
                row[3] = ticker
                row[4] = shares
                row[5] = open_price
                row[6] = type

    with open('users_portfolio.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(lines)


#################Market Data Functions####################




def ask_user():
    ticker = str(input("Enter the ticker symbol(meta, aapl, msft, tsla, amzn): "))
    ticker = ticker.upper()
    period = str(input("Enter the period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max): "))
    interval = str(input("Enter the interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo): "))
    return ticker, period, interval



def get_market_data():
    ticker, period, interval = ask_user()
    #get live market data
    data = yf.download(tickers=ticker, period=period, interval=interval)
    return data , ticker


def plot_market_data(data , ticker):
    #declare figure
    mpf.plot(data, type='candle', style='yahoo', title=ticker, ylabel='Stock Price (USD per Shares)', volume=True, mav=(2,5))



def get_live_price(ticker):
    #get live price
    live_price = yf.Ticker(ticker)
    live_price = live_price.info['regularMarketPrice']
    return live_price




# Path: Final Project\main.py