import numpy as np

phrases = ['a', 'b', 'c', 'd', 'e']

p = np.zeros((len(phrases)), dtype=float)
            
p = np.array([0.5, 0.2, 0.6, 0.8, 0.2], dtype=float)
    
p /= sum(p)

print(f"p: {p}")

searchDepth = -5

index = p.argsort()[-5:][::-1]

# print(f"{colors.BOLD + colors.BLUE}STAGE THREE | Most likely phrase is {phrases[index]} with probability {p[index]}.")

for i in range(len(index)):
    print(f"STAGE THREE | Likely phrase #{i} is {phrases[index[i]]} with probability {p[index[i]]}")
