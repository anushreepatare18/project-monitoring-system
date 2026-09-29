import os

dirs = [
    "backend/ml_core/data",
    "backend/ml_core/features",
    "backend/ml_core/training",
    "backend/ml_core/explain",
    "backend/ml_core/anomaly",
    "backend/ml_core/registry",
    "backend/ml_core/inference",
    "backend/ml_core/tests"
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    init_file = os.path.join(d, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("")

# Let's also create the root __init__.py
os.makedirs("backend/ml_core", exist_ok=True)
with open("backend/ml_core/__init__.py", "w") as f:
    f.write("")

print("Directories created successfully.")
