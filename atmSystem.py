import csv
import pandas as pd
import os
from datetime import datetime
import random
import time


class Account:
    def __init__(self, account_number, name, pin):
        self.account_number = account_number
        self.name = name
        self.pin = str(pin)
        self.balance = 0
        self.transaction_history = []

    def deposit(self, amount):
        self.balance += amount
        self.transaction_history.append({
            'Transaction Type': 'Deposit',
            'Amount': amount,
            'Timestamp': str(datetime.now())
        })


    def withdraw(self, amount):
        if amount <= self.balance:
            self.balance -= amount
            self.transaction_history.append({
                'Transaction Type': 'Withdraw',
                'Amount': amount,
                'Timestamp': str(datetime.now())
            })

            return True
        else:
            return False

    def transfer(self, amount, target_account):
        if amount <= self.balance:
            self.balance -= amount
            target_account.deposit(amount)
            self.transaction_history.append({
                'Transaction Type': 'Transfer',
                'Amount': amount,
                'Timestamp': str(datetime.now())
            })

            return True
        else:
            return False

    def get_balance(self):
        return self.balance

    def get_transaction_history(self):
        return self.transaction_history


class Queue:
    def __init__(self):
        self.items = []

    def enqueue(self, item):
        self.items.append(item)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)

    def display(self):
        return self.items


class TransactionNode:
    def __init__(self, transaction):
        self.transaction = transaction
        self.next = None

class TransactionLinkedList:
    def __init__(self):
        self.head = None

    def add_transaction(self, transaction):
        new_node = TransactionNode(transaction)
        if not self.head:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node

    def save_to_csv(self, account_number):
        current = self.head
        transactions = []
        while current:
            transactions.append(current.transaction)
            current = current.next
        df = pd.DataFrame(transactions)
        df.to_csv(f'transactions_{account_number}.csv', index=False)

    def display_transactions(self):
        if not self.head:
            print("No transactions to display.")
            return
        current = self.head
        print("\n*** Session Transaction Receipt ***")
        while current:
            print(f"{current.transaction['Transaction Type']} | Amount: {current.transaction['Amount']} | Timestamp: {current.transaction['Timestamp']}")
            current = current.next
        print("**********************************\n")


class ATMSystem:
    def __init__(self):
        self.accounts = {}
        self.queue = Queue()
        self.load_accounts()

    def load_accounts(self):
       try:
           if os.path.exists('accounts.csv'):
               df = pd.read_csv('accounts.csv', header=0)
               for index, row in df.iterrows():
                   account_number = str(row['Account Number'])
                   if account_number not in self.accounts:
                       account = Account(account_number, row['Name'], row['PIN'])
                       self.accounts[account_number] = account

                   self.accounts[account_number].balance = row['Balance']


                   try:
                       with open(f'transactions_{account_number}.csv', 'r') as csvfile:
                           reader = csv.DictReader(csvfile)
                           for row in reader:
                               self.accounts[account_number].transaction_history.append(row)
                   except FileNotFoundError:
                       pass
       except Exception as e:
           print(f"Error loading accounts: {e}")
    def save_accounts(self):
        account_data = []
        for account in self.accounts.values():
            account_data.append({
                'Account Number': account.account_number,
                'Name': account.name,
                'PIN': account.pin,
                'Balance': account.balance
            })
        df = pd.DataFrame(account_data)
        df.to_csv('accounts.csv', index=False)

    def generate_account_number(self):
        return str(10000000 + len(self.accounts))
        #account_no = random.randint(10000000, 99999999)
        #return account_no
    def create_account(self):
        account_number = self.generate_account_number()
        name = input("Enter your name: ")
        pin = int(input("Set a 4-digit PIN: "))
        while len(str(pin)) != 4 or not str(pin).isdigit():
          print("PIN must be a 4-digit number.")
          pin = int(input("Set a 4-digit PIN: "))

        new_account = Account(account_number, name, pin)
        self.accounts[account_number] = new_account
        self.save_accounts()
        print(f"Account created successfully! Your account number is {account_number}.")
        self.setup_queue_for_user(new_account.account_number)
        self.transaction_menu(new_account)

    def setup_queue_for_user(self, user_account_number):
      self.queue = Queue()
      account_numbers = list(self.accounts.keys())
      total_accounts = len(account_numbers)
      if total_accounts > 1:
          num_accounts_to_queue = random.randint(1, total_accounts - 1)
      else:
          num_accounts_to_queue = 0
      random_accounts = random.sample(account_numbers, min(num_accounts_to_queue, len(account_numbers)))
      if user_account_number in random_accounts:
          random_accounts.remove(user_account_number)

      random_accounts.append(user_account_number)
      random.shuffle(random_accounts)
      for acc_num in random_accounts:
          self.queue.enqueue(acc_num)


    def display_queue_messages(self):
        queue_list = self.queue.display()
        for idx, account_number in enumerate(queue_list):
            if account_number != queue_list[-1]:
                position = len(queue_list) - idx
                print(f"You are in queue position {position}")
                time.sleep(3)
        print("Your turn!")

    def transaction_menu(self, account):
        transaction_list = TransactionLinkedList()
        self.display_queue_messages()

        while True:
            print("\nTransaction Menu:")
            print("1. Withdraw")
            print("2. Deposit")
            print("3. Check Balance")
            print("4. Transfer")
            print("5. Mini Statement")
            print("6. Exit")
            choice = input("Choose an option: ")

            if choice == '1':
                amount = float(input("Enter amount to withdraw: "))
                if account.withdraw(amount):
                    print(f"Withdrawal successful! New balance: {account.get_balance()}")
                    transaction_list.add_transaction({'Transaction Type': 'Withdraw', 'Amount': amount, 'Timestamp': str(datetime.now())})
                    self.save_accounts()
                else:
                    print("Insufficient balance!")

            elif choice == '2':
                amount = float(input("Enter amount to deposit: "))
                account.deposit(amount)
                print(f"Deposit successful! New balance: {account.get_balance()}")
                transaction_list.add_transaction({'Transaction Type': 'Deposit', 'Amount': amount, 'Timestamp': str(datetime.now())})
                self.save_accounts()

            elif choice == '3':
                print(f"Current balance: {account.get_balance()}")

            elif choice == '4':
                target_account_number = input("Enter target account number for transfer: ")
                if target_account_number == account.account_number:
                    print("You cannot transfer to the same account.")
                elif target_account_number in self.accounts:
                    amount = float(input("Enter amount to transfer: "))
                    if account.transfer(amount, self.accounts[target_account_number]):
                        print(f"Transfer successful! New balance: {account.get_balance()}")
                        transaction_list.add_transaction({'Transaction Type': 'Transfer', 'Amount': amount, 'Timestamp': str(datetime.now())})
                        self.save_accounts()
                    else:
                        print("Insufficient balance!")
                else:
                    print("Account not found!")


            elif choice == '5':
                print("Transaction History:")
                for transaction in account.get_transaction_history():
                    print(transaction)
            elif choice == '6':
                print("Exiting...")
                transaction_list.display_transactions()
                transaction_list.save_to_csv(account.account_number)
                break

            else:
                print("Invalid option. Please try again.")
            transaction_list.save_to_csv(account.account_number)
    def login(self):
        account_number = input("Enter your account number: ")
        if account_number in self.accounts:
            for attempt in range(3):
                pin = input("Enter your PIN: ")
                if self.accounts[account_number].pin == pin:
                    print("PIN verified!")
                    self.setup_queue_for_user(account_number)
                    self.transaction_menu(self.accounts[account_number])
                    return
                else:
                    print(f"Incorrect PIN! You have {2 - attempt} attempts left.")
            print("Too many incorrect attempts. Exiting...")
        else:
            create_new = input("Account not found! Would you like to create a new account? (yes/no): ")
            if create_new.lower() == 'yes':
                self.create_account()
            else:
                print("Exiting...")


if __name__ == "__main__":
    atm = ATMSystem()
    while True:
        print("\nWelcome to the ATM System!")
        atm.login()
