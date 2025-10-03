pen = [None] * 5
for i in range(5):
            pen[i] = [5]*5
print(pen)

for i in range(5):
        for f in range(5):
                pen[i][f] = -pen[i][f]
print(pen)