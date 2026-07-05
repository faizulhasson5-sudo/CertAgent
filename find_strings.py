lines = open('src/automation/github.py', encoding='utf-8').readlines()
triple_quote_active = False
start_line = 0
for i, line in enumerate(lines, 1):
    count = line.count('"""')
    if count % 2 == 1:
        if not triple_quote_active:
            triple_quote_active = True
            start_line = i
        else:
            triple_quote_active = False
            if i - start_line > 1:
                print(f"Triple-quoted string from line {start_line} to {i}")
