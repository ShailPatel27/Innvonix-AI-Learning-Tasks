import time
import random
import os

class TicTacToe:

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE    = "\033[34m"
    RESET = "\033[0m"

    def __init__(self):
        self.markers = [f'{self.RED}X{self.RESET}', f'{self.GREEN}O{self.RESET}']
        self.user_marker = ''
        self.cpu_marker = ''
        self.selectable_choices = []
        self.selected_choices = {}
        self.current_turn = ""

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def game(self):

        self.clear()

        self.user_marker = random.choice(self.markers)
        self.cpu_marker = self.markers[1] if self.user_marker == self.markers[0] else self.markers[0]

        self.current_turn = random.choice(['user', 'cpu'])

        self.selectable_choices = ['1','2','3','4','5','6','7','8','9']
        self.selected_choices = {'user': [], 'cpu': []}

        self.board_list = ['0','1','2','3','4','5','6','7','8','9']

        self.print_board()

        self.main()

    def print_board(self):
        b = self.board_list

        print(f'''
            {b[7]} | {b[8]} | {b[9]}
            --|---|--
            {b[4]} | {b[5]} | {b[6]}
            --|---|--
            {b[1]} | {b[2]} | {b[3]}
        ''')

    def update_board(self, choice, marker):
        self.board_list[int(choice)] = marker
        self.print_board()

    def turn(self, choice, marker):

        self.selected_choices[self.current_turn].append(choice)

        self.selectable_choices.remove(choice)

        self.update_board(choice, marker)

    def user_turn(self):

        choice = input("Enter choice: ")

        if(choice in self.selected_choices['user'] or choice in self.selected_choices['cpu']):
            print("Space is already filled please pick another one!")
            self.user_turn()

        elif(choice not in self.selectable_choices):
            print("please enter a valid number")
            self.user_turn()

        else:
            self.clear()
            self.turn(choice, self.user_marker)

    def cpu_turn(self):

        time.sleep(0.25)

        print("Thinking", end="")
        time.sleep(0.25)
        print(".", end="")
        time.sleep(0.25)
        print(".", end="")
        time.sleep(0.25)
        print(".")
        time.sleep(0.5)

        choice = random.choice(self.selectable_choices)

        self.clear()

        self.turn(choice, self.cpu_marker)

    def won(self):

        print(f'''{self.YELLOW}⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⠀ ''')
        time.sleep(0.1)
        print('''⢠⣤⣤⣤⣼⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠀⠀⣿⣄⣤⣤⣠''')
        time.sleep(0.1)
        print('''⢸⠀⡶⠶⠾⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀ ⠀⡷⠶⠶⡆⡼''')
        time.sleep(0.1)
        print('''⠈⡇⢷⠀⠀⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⠀⠀⢰⠇⠀⢸⢁⡗''')
        time.sleep(0.1)
        print('''⠀⢹⡘⡆⠀⢹⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⠀⠀⡸⠀⢀⡏⡼⠀''')
        time.sleep(0.1)
        print('''⠀⠀⢳⡙⣆⠈⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⠀⢠⠇⢀⠞⡼⠁⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠙⣌⠳⣼⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⣞⡴⣫⠞⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠈⠓⢮⣻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ⡼⣩⠞⠉⠀⠀⠀ ''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠉⠛⣆⠀⠀⠀⠀⠀⠀⠀⠀  ⢠⠞⠋⠁⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⢤⣀⠀⠀⠀⢀⣠⠖⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀ ''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⡇⡏⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⢸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ ''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠖⠒⠓⠚⠓⠒⣦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⣀⣠⣞⣉⣉⣉⣉⣉⣉⣉⣉⣉⣉⣙⣆⣀⡀⠀⠀⠀ ''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⡇⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⡇⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print(f'''⠀⠀⠀⠀⠀⠀⠀⠓⠲⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⠖⠃{self.RESET}''')

    def lost(self):

        print(f'''{self.RED}██╗      ██████╗ ███████╗███████╗██████╗ ██╗''')
        time.sleep(0.1)
        print('''██║     ██╔═══██╗██╔════╝██╔════╝██╔══██╗██║''')
        time.sleep(0.1)
        print('''██║     ██║   ██║███████╗█████╗  ██████╔╝██║''')
        time.sleep(0.1)
        print('''██║     ██║   ██║╚════██║██╔══╝  ██╔══██╗╚═╝''')
        time.sleep(0.1)
        print('''███████╗╚██████╔╝███████║███████╗██║  ██║██╗''')
        time.sleep(0.1)
        print(f'''╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝{self.RESET}''')
        
    def tie(self):
        print(f'''{self.BLUE}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⠃⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠿⠿⠿⠿⠏⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣶⣶⣦⠀⠀⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣙⣉⣉⣤⡀⠀⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠿⠇⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢉⣉⣠⣤⣴⣶⡀⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⠿⠟⠁⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢈⣉⣭⣤⣤⣶⣶⣧⠀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿⠿⠿⠛⠛⢉⡀⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣉⣠⣤⣴⣶⣾⣿⣿⡇⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠚⢿⣿⣿⠿⠿⠛⠋⠉⠁⠀⠀⠀⠀⠀''')
        time.sleep(0.1)
        print(f'''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠶⡶⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀{self.RESET}''')


    def win_check(self, player):

        winning_combos = [
            ['1','2','3'],['4','5','6'],['7','8','9'],
            ['1','4','7'],['2','5','8'],['3','6','9'],
            ['1','5','9'],['3','5','7']
        ]

        selected = self.selected_choices[player]

        for combo in winning_combos:

            if all(x in selected for x in combo):

                self.clear()
                self.print_board()

                if(player == 'user'):
                    print(f"{self.GREEN}You Won!{self.RESET}\n")
                    self.won()

                else:
                    print(f"{self.RED}You Lost!{self.RESET}\n")
                    self.lost()

                return True

        if self.selectable_choices == []:
            self.clear()
            self.print_board()
            print(f"{self.YELLOW}Its a Tie!{self.RESET}\n")
            
            self.tie()
            return True

        return False

    def main(self):

        marker = self.user_marker if self.current_turn == 'user' else self.cpu_marker

        print(f"{self.YELLOW}{self.current_turn}'s turn{self.RESET} ({marker})")

        self.user_turn() if self.current_turn == 'user' else self.cpu_turn()

        won = self.win_check(self.current_turn)

        if won == True:
            return

        self.current_turn = 'user' if self.current_turn == 'cpu' else 'cpu'

        self.main()

    def again(self):

        while True:

            choice = input("\nDo you want to play again? (y/n) ").lower()

            if choice == 'y':
                self.clear()
                return True

            if choice == 'n':
                print("Thanks for playing!")
                return False

            print("Please enter 'y' or 'n'")


game = TicTacToe()

while True:
    game.game()
    if not game.again():
        break