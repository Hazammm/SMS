import re

with open('frontend/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

# remove strings
text = re.sub(r'".*?"', '""', text)
text = re.sub(r"'.*?'", "''", text)
text = re.sub(r'`.*?`', '``', text, flags=re.DOTALL)
# remove comments
text = re.sub(r'//.*', '', text)
text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)

print("B:", text.count('{'), text.count('}'))
print("P:", text.count('('), text.count(')'))
print("S:", text.count('['), text.count(']'))
