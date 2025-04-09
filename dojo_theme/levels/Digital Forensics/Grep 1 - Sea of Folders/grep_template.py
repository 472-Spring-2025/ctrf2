import os
import shutil
import random
import yaml

with open("input.yml", "r") as file:
    config = yaml.safe_load(file)
num_dirs = int(config["num_dirs"])
sub_levels = int(config["num_subs"])
words = config["words"]
if words != None:
    words = words.split(",")
winning_sol = config["winning_solution"]
if winning_sol != None:
    winning_sol = winning_sol.split(",")

def get_path(num_array):
    path = ""
    if words:
        for i in num_array:
            path = path + "/" + words[i]
    else:
        for i in num_array:
            path = path + "/folder" + str(i)
    return path

def get_path_rand(num_array, folder_space):
    path = ""
    if words:
        used_arr = []
        count = 0
        for i in num_array:
            used_arr.append(folder_space[i][count])
            count += 1
        for i in used_arr:
            path = path + "/" + words[i]
    else:
        for i in num_array:
            path = path + "/folder" + str(i)
    return path

def arr_incriment(arr, idx, num_dirs):
    if idx < 0:
        return arr
    init_arr[idx] += 1
    if init_arr[idx] == num_dirs:
        init_arr[idx] = 0
        arr = arr_incriment(arr, idx - 1, num_dirs)
    return arr

base = "output"
extra = ""



try:
    shutil.rmtree(base)
    os.mkdir(base)
except Exception:
    os.mkdir(base)
if(winning_sol):
    winning_sol_vec = []
    for word in winning_sol:
        winning_sol_vec.append(words.index(word))
    
folder_space = [winning_sol_vec]
for i in range(num_dirs - 1):
    new_row = []
    for j in range(sub_levels):
        rand_int = random.randint(0, len(words) - 1)
        col = []
        for num in range(len(folder_space)):
            col.append(folder_space[num][j])
        while(rand_int in col):
            rand_int = (rand_int + 1) % (num_dirs - 1)
        new_row.append(rand_int)
    folder_space.append(new_row)




init_arr = []
end_arr = []
for i in range(sub_levels):
    init_arr.append(0)
    end_arr.append(num_dirs - 1)

if(winning_sol):
    extra = get_path(winning_sol_vec)
    os.makedirs(base+extra, exist_ok=True)
while(init_arr != end_arr):
    extra = get_path_rand(init_arr, folder_space)
    os.makedirs(base+extra, exist_ok=True)
    idx = len(init_arr) - 1
    arr_incriment(init_arr, idx, num_dirs)

for i in range(len(end_arr)):
    end_arr[i] = random.randint(0, num_dirs - 1)
if(winning_sol):
    end_arr = winning_sol_vec
extra = get_path(end_arr)
#fin = open("../../input/exec/sample1", "r")
flag = ""
with open("/flag", "w") as fout:
    flag = fout.readline()
with open(base+extra+flag, "w") as fout:
    fout.write(flag)


    


