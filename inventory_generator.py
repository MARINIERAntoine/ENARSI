with open("inventory.txt", "w") as inv:
    for i in range(1, 19):
        inv.write("R{} 192.168.1.32 {}\n".format(i, 32768 + i))
