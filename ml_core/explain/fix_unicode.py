"""Fix all remaining unicode/special chars in run_pipeline.py"""
import re

path = "ml_core/run_pipeline.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "\u2192": "->",
    "\u2714": "[OK]",
    "\u25b6": ">",
    "\u26a0": "[!]",
    "\u2248": "~",
    "\u2264": "<=",
    "\u2265": ">=",
    "\u2500": "-",
    "\u2501": "-",
    "\u2502": "|",
    "\u2190": "<-",
    "\u00e2\u0080\u0094": "--",
}
for char, rep in replacements.items():
    content = content.replace(char, rep)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Done")
