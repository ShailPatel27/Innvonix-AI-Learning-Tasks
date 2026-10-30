import time
import random
import os

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
ORANGE = "\033[38;5;208m"
PINK = "\033[38;5;201m"
GOLD = "\033[38;2;255;215;0m"
MINT = "\033[38;2;152;255;152m"
RESET = "\033[0m"

markers = [f'{RED}X{RESET}', f'{GREEN}O{RESET}']
user_marker = ''
cpu_marker = ''
selectable_choices = []
selected_choices = {}
board = ""
current_turn = ""


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    
def title():
   
    colors = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, ORANGE, PINK, GOLD, MINT]
    temp_colors = colors
    c1 = random.choice(temp_colors)
    temp_colors.remove(c1)
    c2 = random.choice(temp_colors)
    temp_colors.remove(c2)
    c3 = random.choice(temp_colors)
    temp_colors.remove(c3)
    c4 = random.choice(temp_colors)
    print(f'''           {c1}Tic{RESET}{c2}-{RESET}{c3}Tac{RESET}{c2}-{RESET}{c4}Toe{RESET} ''')

def game():
    global markers
    global user_marker
    global cpu_marker
    global selectable_choices
    global selected_choices
    global board
    global current_turn
    
    clear()
    
    title()
    
    user_marker = random.choice(markers)
    cpu_marker = markers[1] if user_marker == markers[0] else markers[0]

    current_turn = random.choice(['user', 'cpu'])

    selectable_choices = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    selected_choices = {'user': [], 'cpu': []}

    board_list = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

    def print_board():
        b = board_list
        print(f'''
            {b[7]} | {b[8]} | {b[9]}
            --|---|--
            {b[4]} | {b[5]} | {b[6]}
            --|---|--
            {b[1]} | {b[2]} | {b[3]}
        ''')
    print_board()

    def update_board(choice, marker):
        board_list[int(choice)] = marker
        print_board()
        
    def turn(choice, marker):
        global selectable_choices
        global selected_choices
        global current_turn
        
        selected_choices[current_turn].append(choice)
        selectable_choices.remove(choice)
        
        update_board(choice, marker)
        

    def user_turn():
        choice = input("Enter choice: ")
        
        if(choice in selected_choices['user']):
            print("Space is already filled please pick another one!")
            user_turn()
            
        elif(choice not in selectable_choices):
            print("please enter a valid number")
            user_turn()
            
        else:
            clear()
            title()
            turn(choice, user_marker)


    def cpu_turn():
        
        time.sleep(0.25)
        
        print("Thinking", end="")
        time.sleep(0.25)
        print(".", end="")
        time.sleep(0.25)
        print(".", end="")
        time.sleep(0.25)
        print(".")
        time.sleep(0.5)
        
        choice = random.choice(selectable_choices)
        
        clear()
        title()
        turn(choice, cpu_marker)
        
    def won():
        print(f'''{GOLD}⠀⠀⠀⠀⢀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⣀⠀ ''')
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
        print('''⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⡇⠀⠀⠀⠀⠀    ''')
        time.sleep(0.1)
        print('''⠀⠀⠀⠀⠀⠀⠀⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀  ⡇⠀⠀⠀⠀⠀⠀   ''')
        time.sleep(0.1)
        print(f'''⠀⠀⠀⠀⠀⠀⠀⠓⠲⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⠶⠖⠃     {RESET}''')
        
    
    def lost():
        print(f'''{RED}██╗      ██████╗ ███████╗███████╗██████╗ ██╗''')
        time.sleep(0.1)
        print('''██║     ██╔═══██╗██╔════╝██╔════╝██╔══██╗██║''')
        time.sleep(0.1)
        print('''██║     ██║   ██║███████╗█████╗  ██████╔╝██║''')
        time.sleep(0.1)
        print('''██║     ██║   ██║╚════██║██╔══╝  ██╔══██╗╚═╝''')
        time.sleep(0.1)
        print('''███████╗╚██████╔╝███████║███████╗██║  ██║██╗''')
        time.sleep(0.1)
        print(f'''╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝{RESET}''')
        
    def tie():
        print(f'''{BLUE}⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⣿⣿⣿⣿⣷⡀⠀⠀⠀⠀⠀''')
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
        print(f'''⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠶⡶⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀{RESET}''')
        
    def win_check(player):
    
        winning_combos = [
            ['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9'],  # Rows
            ['1', '4', '7'], ['2', '5', '8'], ['3', '6', '9'],  # Cols
            ['1', '5', '9'], ['3', '5', '7']                    # Diagonals
        ]
        

        selected = selected_choices[player]
        for combo in winning_combos:
            if all(x in selected for x in combo):
                clear()
                title()
                print_board()
                if(player == 'user'):
                    print(f"{GREEN}You Won!{RESET}\n")
                    won()
                else:
                    print(f"{RED}You Lost!{RESET}\n")
                    lost()
                return True
            
        if selectable_choices == []:
            clear()
            title()
            print_board()
            print(f"{YELLOW}Its a Tie!{RESET}\n")
            tie()
    
            return True
        return False
    
    def main():
        global current_turn
        
        marker = user_marker if current_turn == 'user' else cpu_marker
        
        print(f"{YELLOW}{current_turn}'s turn{RESET} ({marker})")
        
        user_turn() if current_turn == 'user' else cpu_turn()
        
        won = win_check(current_turn)
        if won == True: return
        
        current_turn = 'user' if current_turn == 'cpu' else 'cpu'
        
        main()
        
    main()

def again():
    while True:
        choice = input("\nDo you want to play again? (y/n) ").lower()
        if choice == 'y':
            clear()
            title()
            return True
        if choice == 'n':
            print("Thanks for playing!")
            return False
        print("Please enter 'y' or 'n'")

while True:
    game()
    if not again(): break