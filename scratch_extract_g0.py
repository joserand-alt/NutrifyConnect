with open('template.html', 'r', encoding='utf-8') as f:
    text = f.read()

sub = text[371500:376500]
with open('g0_cards_snippet.js', 'w', encoding='utf-8') as out:
    out.write(sub)
print("Saved g0_cards_snippet.js (length: " + str(len(sub)) + ")")
