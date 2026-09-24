contacts = {}


while True:

    print("1. Add\n2. View\n3. Update\n4. Delete\n5. Exit")

    choice = input("Enter a number: ")

    if choice == "1":
        name = input("Name: ")
        number = input("Number: ")

        contacts[name] = number


    elif choice == "2":
        display_contacts = str(contacts).strip("{}").replace(",", "|").replace("'", "")
        print(display_contacts)


    elif choice == "3":
        name = input("Name: ")
        contacts[name] = input("New Number: ")


    elif choice == "4":
        name = input("Name: ")
        contacts.pop(name)


    elif choice == "5":
        break