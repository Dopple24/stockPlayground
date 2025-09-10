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
        row["Earnings Yield"],
        row["PEG"],
        row["Debt/Equity"],
        row["Revenue Growth (/10)"],
        row["FCF Yield"]
    ]
    data_arrays.append([price, metrics])

#print (data_arrays)

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
            #print(f"{arr}, result = {result} coef/exp")
            candidateArray.append([result,arr])
    print(candidates)
    return candidateArray
# Example usage
candidateArray = guesser_polynomial(
    Decimal("2.0"),
    Decimal("-3.0"),
    Decimal("7.0"),
    [2.7405650037434386,2.3481156413410527,0.17639506345366093,1.4932156232406721,1.9272389865962702],        # these will be converted to Decimal inside
    Decimal("499.885"),
)

matches = 0
best = 0
bestCandidate = []
for candidate in candidateArray:
    matches = 0
    for test in data_arrays:
        if test[0] == 499.885:
            continue
        res = 0
        for i in range(int(len(candidate[1])/2)):
            coef = Decimal(candidate[1][2 * i])  # make sure coef is Decimal
            exp = int(candidate[1][2 * i + 1])  # exponent is safe as int
            term = coef * (Decimal(test[1][i]) ** exp)  # cast base to Decimal too
            res += term
        if Decimal(str(test[0])) * Decimal("0.9") <= res <= Decimal(str(test[0])) * Decimal("1.1"):
            matches += 1
            print(f"res: {res} + expected: {test[0]}")
    if matches > best:
        best = matches
        bestCandidate = candidate
print(best)
print(bestCandidate)

