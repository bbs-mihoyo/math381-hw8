import json
import numpy as np
from matplotlib import pyplot as plt
obj = json.load(open('davinci3.json'))
#table = [obj[f"0{s}"] for s in range(1)]

def count(s):
    zero = 0
    one = 0
    for bit in s:
        if bit == "1": one += 1
        else: zero += 1
    return zero, one

def result():
    for i in range(1,5):
        result = [str(i)]
        for j in range(1,5):
            z = count(obj[f"{i}{j}"])[0]
            result.append(str(z))
        print("&".join(result) + "\\\\")

def result2():
    for i in range(8):
        z = 0
        for j in range(8):
            z += count(obj[f"{i}{j}"])[0]
            #result.append(str(z))
        print("&".join([str(i), f"{round(z/80000, 2)}%"]) + "\\\\")

def hist():
    y = []
    for i in range(0, 1000000, 1000):
        z = count(obj["00"][i: i+1000])[0]
        y.append(z/1000)
    print(np.mean(y))
    print(np.std(y))
    plt.hist(y, 20)
    plt.show()

def converge():
    for key in ["00", "01", "02", "03", "04", "05", "06", "07", "52", "55"]:
        line = obj[key]
        x = np.linspace(1, 1000000, 1000000)
        y = []
        zero = 0
        for i in range(1000000):
            if line[i] == "0": zero += 1
            y.append(zero/(i+1))
        plt.plot(x, y)
        plt.ylim(0.4, 0.6)
    plt.show()

def CI():
    for i in range(8):
        line = [str(i)]
        for j in range(8):
            lower_bound = 1
            upper_bound = 0
            
            for k in range(0, 1000000, 100000):
                data = obj[f"{i}{j}"]
                z = count(data[k: k+100000])[0]
                prob = z/100000
                lower_bound = min(prob, lower_bound)
                upper_bound = max(prob, upper_bound)
            line.append(f"({round(lower_bound,3)},{round(upper_bound,3)})")
        print("&".join(line) + "\\\\")

if __name__ == "__main__": converge()