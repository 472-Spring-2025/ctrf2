import random
import string

def generate_random_string(length=30):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

word_list = ["experiment", "attachment", "overcharge", "projection", "connection", "commitment", 
            "understand", "provincial", "discourage", "systematic", "withdrawal", "generation", 
            "vegetation", "restaurant", "memorandum", "reluctance", "tournament", "foundation"]

for word in word_list:
        with open(f"files/{word}.txt", "w") as file:
           file.write(f"flag{{" + generate_random_string(30) + "}")

chosen_file = word_list[random.randint(0, len(word_list) - 1)]
shift = random.randint(4, 16)

shifted_word = ""
for char in chosen_file:
    shifted_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
    shifted_word += shifted_char
    
print(f"Decrypt this word: " + shifted_word)

with open(f"files/{chosen_file}.txt", "r") as file:
    chosen_flag = file.read().strip()

input_flag = input("Input flag: " )
while input_flag != chosen_flag:
    input_flag = input("Incorrect Flag - Try Again: " )

print("Congratulations! You found the flag!")