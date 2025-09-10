from decimal import Decimal
from itertools import product
import pandas as pd

# Load CSV into a DataFrame
df = pd.read_csv("stocks_database.csv")
candidateArray = []

data_arrays = []

for _, row in df.iterrows():
    price = row["Price"]
    metrics = [
        row["Earnings Yield (/10)"],
        row["PEG"],
        row["Debt/Equity"],
        row["Revenue Growth (/10)"],
        row["FCF Yield (/10)"]
    ]
    data_arrays.append([price, metrics])

print (data_arrays)

def guesser_polynomial(step, minimum, maximum, inputs, desired_output):
    # Convert inputs to Decimals
    inputs = [Decimal(x) for x in inputs]

    # Generate the range of values
    values = []
    current = minimum
    while current <= maximum:
        values.append(current)
        current += step

    steps = len(inputs) * 2
    candidates=0
    candidateArray = []

    for combo in product(values, repeat=steps):
        result = Decimal(0)
        arr = list(combo)

        for i, x in enumerate(inputs):
            coef = arr[2*i]
            exp = int(arr[2*i+1])  # safe exponent as int
            term = coef * (x ** exp)  # all Decimal
            result += term

        if desired_output * Decimal("0.99") <= result <= desired_output * Decimal("1.01"):
            print(f"{arr}, result = {result} coef/exp")
            candidateArray.append([result,[arr]])
            candidates += 1
    print(candidates)
# Example usage
guesser_polynomial(
    Decimal("1.0"),
    Decimal("-1.0"),
    Decimal("3.0"),
    [0.26952301485309643,-11.042543809909692,1.872326602282704,0.20219940775141212,0.31285728724418443],        # these will be converted to Decimal inside
    Decimal("234.35"),
)

matches = 0
best = 0
bestCandidate = []
for candidate in candidateArray:
    matches = 0
    for test in data_arrays:
        res = 0
        for i in range(int(len(test[1])/2)):
            res += candidate[i] * test[1][i] ** candidate[i + 1]
        if test[0] * Decimal("0.99") <= res <= test[0] * Decimal("1.01"):
            matches += 1
            print(res + " " + test[0])
    if (matches > best):
        best = matches
        bestCandidate = candidate
print(best)
print(bestCandidate)

