with open(r'C:\Users\DELL\Desktop\Dash_InfectoCast\temp_test.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []

for idx, line in enumerate(lines):
    i = 0
    in_str = None
    while i < len(line):
        c = line[i]
        if in_str:
            if c == '\\':
                i += 2
                continue
            elif c == in_str:
                in_str = None
        else:
            if c in ('"', "'", '`'):
                in_str = c
            elif c == '/' and i + 1 < len(line) and line[i+1] == '/':
                break
            elif c == '{':
                stack.append((idx + 1, line.strip()[:80]))
            elif c == '}':
                if stack:
                    stack.pop()
                else:
                    print(f"Unmatched closing brace at line {idx+1}")
        i += 1

print(f"Unclosed braces count: {len(stack)}")
for item in stack:
    print(f"Line {item[0]}: {item[1]}")
