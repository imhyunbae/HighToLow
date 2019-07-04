high = open('./new_uv_high.obj', 'r').readlines()
uv = [[float(each) for each in line[:-1].split(' ')[1:]] for line in high if line[:3] == 'vt ']

with open('./datas/uv_high.txt', 'w') as uv_high:
    for u, v in uv:
        uv_high.write('{} {}\n'.format(u, v))