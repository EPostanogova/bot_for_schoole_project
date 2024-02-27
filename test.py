predlog = input()
p=predlog.lower()
r=''.join(p.split())
print(r)
a=0
for i in range(len(p)//2):
    if p[i] == p[-i - 1] :
        a += 1
        print()

    else:
        a=0

if a>0 :
    print('совпало')

#     elif p[i] == p[-i - 1] and len(p) % 2 == 0:
#         a = 2
#     else:
#         a = 3
#
# if a == 1:
#     print('Читается одинаково с двух концов')
# if a == 2:
#     print('Читается одинаково с середины до концов')
# if a == 3:
#     print('Увы, нет изюминки')