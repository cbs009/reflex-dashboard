import reflex as rx
print("Attributes in rx:")
for attr in dir(rx):
    if "js" in attr.lower() or "code" in attr.lower() or "var" in attr.lower():
        print(attr)
