from All_Functions import * # Import all functions from functions.py




#def creates_file if it doesn't exist
############################################################################################################
with open("users.txt", "a+") as file:
    pass
############################################################################################################



#Make sure data_base exists
############################################################################################################
def does_file_exist(filename):
    return os.path.exists(filename)

if does_file_exist("users_portfolio.csv"):
    pass
else:
    with open("users_portfolio.csv", "w+", newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["user", "Balance","Open_Position", "stock_ticker", "shares", "open_price", "type"])
############################################################################################################




main()