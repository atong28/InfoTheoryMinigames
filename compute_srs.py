import numpy as np
import statistics

f = open('battleship_sq_results.txt', 'r', encoding='utf-8')
content = f.read()

data = list(map(int, content.splitlines()))

print(data)

SRS_SIZE = 1000
SRS_SAMPLES = 1000

samples = []
sampleMeans = []
for i in range(SRS_SAMPLES):
    sample = []
    for j in range(SRS_SIZE):
        result = np.random.randint(0,5000000)
        for k in range(100):
            if data[k] < result < data[k+1]:
                # print(f"Result {result} found between {data[k]} and {data[k+1]} at k={k}")
                sample += [k+1]
                break
    # print(f"Found sample of size {SRS_SIZE}: {sample}")
    print(f"{statistics.mean(sample)}")
    samples += [sample]
    sampleMeans += [statistics.mean(sample)]


print(f"Overall: {statistics.mean(sampleMeans)}")