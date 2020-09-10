import random
import sys
import sqlite3


class Bank:
    '''Banking system connected to its own database'''

    def __init__(self):
        self.conn = sqlite3.connect('card.s3db')
        self.cur = self.conn.cursor()
        self.create_table()
        self.main_menu()

    def create_table(self):
        self.cur.execute('''CREATE TABLE IF NOT EXISTS card (
                    id INTEGER NOT NULL PRIMARY KEY,
                    number TEXT,
                    pin TEXT,
                    balance INTEGER DEFAULT 0 );
                    ''')
        self.conn.commit()

    def generate_info(self):
        card_no = '400000'
        pin = ''
        for i in range(9):
            card_no += str(random.randint(0, 9))
        pos = 1
        luhn = 0
        for num in card_no:
            num = int(num)
            if pos % 2 != 0:
                num = 2*num
            if num > 9:
                num -= 9
            luhn += num
            pos += 1
        checksum = ((luhn//10) + 1)*10 - luhn
        card_no += str(checksum%10)
        for i in range(4):
            pin += str(random.randint(0, 9))
        return card_no, pin

    def check_luhn(self, card_no):
        pos = 1
        luhn = 0
        for num in card_no:
            num = int(num)
            if pos % 2 != 0:
                num = 2*num
            if num > 9:
                num -= 9
            luhn += num
            pos += 1
        if luhn % 10 == 0:
            return True
        return False

    def create_new_account(self):
        (card_no, pin) = self.generate_info()
        print('Your card has been created')
        print('Your card number:', card_no, sep='\n')
        print('Your card PIN:', pin, sep='\n')
        self.cur.execute(f'INSERT INTO CARD(number,pin) VALUES({card_no}, {pin});')
        self.conn.commit()

    def log_in_check(self,card_no, pin):
        self.cur.execute(f'SELECT * FROM card WHERE number={card_no} AND pin={pin};')
        return self.cur.fetchone()

    def log_in(self):
        row = self.log_in_check(input('Enter your card number:\n'), input('Enter your PIN\n'))
        if row:
            print('You have successfully logged in.')
            self.logged_in_menu(row)
        else:
            print('Wrong card number or PIN!')

    def add_income(self, row):
        income = int(input('Enter income:'))
        new_income = row[3] + income
        card_no = row[1]
        self.update_balance(card_no, new_income)
        print('Income was added!')

    def update_balance(self, account_no, new_balance):
        self.cur.execute(f'UPDATE card SET balance = {new_balance} WHERE number = {account_no}')
        self.conn.commit()

    def transfer(self, row):
        user_account = row[1]
        user_balance = row[3]
        transfer_to_account = input('Transfer\nEnter card number:')
        if not self.check_luhn(transfer_to_account):
            print('Probably you made a mistake in card number. Please try again!')
        self.cur.execute(f'SELECT number, balance FROM card WHERE number={transfer_to_account};')
        transfer_account = self.cur.fetchone()
        if transfer_account:
            money = int(input('How much money you want to transfer:'))
            if money > user_balance:
                print('Not enough money!')
            else:
                transfer_account_no = transfer_account[0]
                transfer_account_balance = transfer_account[1]
                self.update_balance(user_account, user_balance - money)
                self.update_balance(transfer_account_no, transfer_account_balance + money)
                print('Success!')
        else:
            print('Such a card does not exist.')

    def del_account(self,account):
        account_no = account[1]
        self.cur.execute(f'DELETE FROM card WHERE number = {account_no}')
        self.conn.commit()
        print('The account has been closed.')


    def logged_in_menu(self,row):
        card_no = row[1]
        pin = row[2]
        while True:
            user_input = input('1. Balance\n2. Add income\n3. Do transfer\n4. Close account\n5.Log out\n0. Exit\n')
            row = self.log_in_check(card_no, pin)
            balance = row[3]
            if user_input == '0':
                print('Bye!')
                self.conn.close()
                sys.exit()
            elif user_input == '1':
                print(balance)
            elif user_input == '2':
                self.add_income(row)
            elif user_input == '3':
                self.transfer(row)
            elif user_input == '4':
                self.del_account(row)
                break
            elif user_input == '5':
                print('You have successfully logged out.')
                break
            else:
                print('Invalid Input!')

    def main_menu(self):
        while True:
            print('''1. Create an account\n2. Log into account\n0. Exit''')
            user_input = input()
            if user_input == '0':
                print('Bye!')
                self.conn.close()
                sys.exit()
            elif user_input == '1':
                self.create_new_account()
            elif user_input == '2':
                self.log_in()


myBank = Bank()
