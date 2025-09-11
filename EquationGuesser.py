import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_percentage_error, r2_score

# --- Load dataset ---
df = pd.read_csv("stocks_database.csv")

# Features & target
feature_labels = [
    "Earnings Yield",
    "PEG",
    "Debt/Equity",
    "Revenue Growth (/10)",
    "FCF Yield"
]
X = df[feature_labels].fillna(0)
y = df["Price"].fillna(0)

# --- Scale features ---
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --- Polynomial features ---
poly = PolynomialFeatures(degree=2, include_bias=False)
X_poly = poly.fit_transform(X_scaled)
feature_names = poly.get_feature_names_out(feature_labels)

# --- Train/test split ---
X_train, X_test, y_train, y_test = train_test_split(
    X_poly, y, test_size=0.2, random_state=42
)

# --- Train model ---
model = Ridge(alpha=1.0)
model.fit(X_train, y_train)

# --- Evaluate ---
y_pred = model.predict(X_test)
mape = mean_absolute_percentage_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("MAPE:", round(mape * 100, 2), "%")
print("R²:", round(r2, 3))

# --- Build the function string ---
coeffs = model.coef_
intercept = model.intercept_

equation = f"Price ≈ {intercept:.3f}"
for name, coef in zip(feature_names, coeffs):
    if abs(coef) > 1e-6:  # skip near-zero coefficients
        equation += f" + ({coef:.3f} × {name})"

print("\n--- Learned Function ---")
print(equation)
