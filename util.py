from scipy.spatial.distance import euclidean

high = open('./datas/high.ply', 'r').readlines()

high_vertices = [[float(element) for element in line[:-1].split(' ')[:3]] for line in high[14:14+53149]]
high_faces = [[int(index) for index in line[:-1].split(' ')[1:]] for line in high if line[:2] == '3 ']

with open('./datas/high.obj', 'w') as high_obj:
    for vertex in high_vertices:
        high_obj.write('v {} {} {}\n'.format(vertex[0], vertex[1], vertex[2]))

    for face in high_faces:
        high_obj.write('f {} {} {}\n'.format(face[0] + 1, face[1] + 1, face[2] + 1))
