from assessment import Assessment
import layout as keyboard

a = [None] * 5

a[1] = Assessment(keyboard.osl, keyboard.qwerty)
a[2] = Assessment(keyboard.osl, keyboard.colemak)
a[3] = Assessment(keyboard.osl, keyboard.dvorak)
a[4] = Assessment(keyboard.osl, keyboard.custom)

for i, test in enumerate(a):
    if test is None:
        continue

    test.run_on('text')
    if i == 1:
        test.one_line_headings()

    test.one_line()
