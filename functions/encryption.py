import random


def encrypt_string(string):
    encrypted_line = "BACKUP"
    for i in range(2 * len(string)):
        if i % 2 == 0:
            encrypted_line += chr(ord(string[i // 2]) + 10)
        else:
            encrypted_line += chr(random.randint(10, 1000))
    return encrypted_line


def decrypt_string(string):
    string = string[6:]
    decrypted_line = ""
    for i in range(len(string)):
        if i % 2 == 0:
            decrypted_line += chr(ord(string[i]) - 10)
    return decrypted_line
