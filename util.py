# from scipy.spatial.distance import euclidean
#
# high = open('./datas/high.ply', 'r').readlines()
#
# high_vertices = [[float(element) for element in line[:-1].split(' ')[:3]] for line in high[14:14+53149]]
# high_faces = [[int(index) for index in line[:-1].split(' ')[1:]] for line in high if line[:2] == '3 ']
#
# with open('./datas/high.obj', 'w') as high_obj:
#     for vertex in high_vertices:
#         high_obj.write('v {} {} {}\n'.format(vertex[0], vertex[1], vertex[2]))
#
#     for face in high_faces:
#         high_obj.write('f {} {} {}\n'.format(face[0] + 1, face[1] + 1, face[2] + 1))

# import numpy as np
# from scipy.spatial.distance import euclidean
#
# mapping = np.array([[int(index) for index in line[:-1].split(' ')] for line in open('./datas/high_low_map.txt').readlines()])
# low_mapping = list(mapping[:, 0])
# high_mapping = list(mapping[:, 1])
#
# high = open('./inputs/lsy.obj', 'r').readlines()
# high_vertices = [[float(element) for element in line[:-1].split(' ')[1:]] for line in high if line[:2] == 'v ']
# high_coordinates = [[float(element) for element in line[:-1].split(' ')[1:]] for line in high if line[:3] == 'vt ']
# high_faces = [[[int(index) for index in element.split('/')] for element in line[:-1].split(' ')[1:]] for line in high if line[:2] == 'f ']
#
# low_path = './outputs/lsy.obj'
# low = open(low_path, 'r').readlines()
# low_vertices = [[float(element) for element in line[:-1].split(' ')[2:]] for line in low if line[:2] == 'v ']
# low_coordinates = [[float(element) for element in line[:-1].split(' ')[1:3]] for line in low if line[:3] == 'vt ']
# low_faces = [[[int(index) for index in element.split('/')] for element in line[:-1].split(' ')[1:]] for line in low if line[:2] == 'f ']
# low_loops = [[[int(index) for index in element.split('/')][1] for element in line[:-1].split(' ')[1:]] for line in low if line[:2] == 'f ']
#
# face_after_attach = [int(line[:-1]) for line in open('./datas/face_after_attach.txt', 'r').readlines()]
#
# vc_map = [None] * len(low_vertices)
# for low_face in low_faces:
#     for vertex_index, coordinate_index in low_face:
#         if vc_map[vertex_index-1] == None:
#             vc_map[vertex_index-1] = []
#         if coordinate_index-1 not in vc_map[vertex_index-1]:
#             vc_map[vertex_index-1].append(coordinate_index-1)
#
# # high_vc_map = [None] * len(high_vertices)
# # for high_face in high_faces:
# #     for vertex_index, coordinate_index in high_face:
# #         if high_vc_map[vertex_index-1] == None:
# #             high_vc_map[vertex_index-1] = []
# #         if coordinate_index-1 not in high_vc_map[vertex_index-1]:
# #             high_vc_map[vertex_index-1].append(coordinate_index-1)
#
# for each_index, each in enumerate(vc_map):
#     if each is not None and len(each) > 0 and each_index in low_mapping:
#         map_index = low_mapping.index(each_index)
#         high_index = high_mapping[map_index]
#         high_coordinates[high_index] = low_coordinates[each[0]]
#
# uv_high = [line[:-1].split(' ') for line in open('./datas/uv_high.txt', 'r').readlines()]
# uv_high = [[int(index), float(u), float(v)]for index, u, v in uv_high]
# last_index = int(uv_high[-1][0])
#
# target_vertices = np.array([[index, vertex] for index, vertex in enumerate(high_vertices) if index in high_mapping])
# for high_index, high_vertex in enumerate(high_vertices):
#     if high_index <= last_index:
#         continue
#
#     def get_weights(A, B, C, P):
#         delta = np.linalg.norm(np.cross(A - B, A - C))
#         a = np.linalg.norm(np.cross(B - P, C - P)) / delta
#         b = np.linalg.norm(np.cross(C - P, A - P)) / delta
#         c = np.linalg.norm(np.cross(A - P, B - P)) / delta
#         return a, b, c
#
#     if high_index not in high_mapping:
#         tuples = [[index, euclidean(high_vertex, vertex)] for index, vertex in target_vertices]
#         distances = np.array(tuples)[:, 1]
#         distances.sort()
#         indices = [list(np.array(tuples)[:, 1]).index(distance) for distance in distances]
#         indices = [int(np.array(tuples)[:, 0][index]) for index in indices]
#         adjacent_vertices = [np.array(high_vertices[index]) for index in indices]
#         adjacent_coordinates = [np.array(high_coordinates[index]) for index in indices]
#         a, b, c = 0.0, 0.0, 0.0
#         i, j, k = 0, 1, 2
#         A, B, C = adjacent_vertices[i], adjacent_vertices[j], adjacent_vertices[k]
#         P = np.array(high_vertex)
#
#         while True:
#             PA, PB, PC = np.linalg.norm(A - P), np.linalg.norm(B - P), np.linalg.norm(C - P)
#             total = PA + PB + PC
#             a, b, c = total / PA, total / PB, total / PC
#             total = a + b + c
#             a, b, c = a / total, b / total, c / total
#
#             co_A, co_B, co_C = adjacent_coordinates[i], adjacent_coordinates[j], adjacent_coordinates[k]
#             co_P = a * co_A + b * co_B + c * co_C
#             co_a, co_b, co_c = get_weights(co_A, co_B, co_C, co_P)
#
#             if abs(co_a + co_b + co_c - 1.0) > 0.000001:
#                 minimum = min([i, j, k])
#                 index = [i, j, k].index(minimum)
#                 if minimum == 0:
#                     i = max([i, j, k]) + 1
#                     A = adjacent_vertices[i]
#                 elif minimum == 1:
#                     j = max([i, j, k]) + 1
#                     B = adjacent_vertices[j]
#                 elif minimum == 2:
#                     k = max([i, j, k]) + 1
#                     C = adjacent_vertices[k]
#                 print('high_index: {}, repeating'.format(high_index))
#             else:
#                 high_coordinates[high_index] = co_P
#                 uv_high.append([high_index, co_P[0], co_P[1]])
#                 break
#     else:
#         uv_high.append([high_index, ])
#
#     if high_index % 200 == 0:
#         with open('./datas/uv_high.txt', 'w') as file:
#             for each in uv_high:
#                 file.write('{} {} {}\n'.format(each[0], each[1], each[2]))
#
#     print('high_index: {}, done'.format(high_index))
#
# with open('./datas/uv_high.txt', 'w') as file:
#     for each in uv_high:
#         file.write('{} {} {}\n'.format(each[0], each[1], each[2]))
#
# with open(low_path.replace('.obj', '_c.obj'), 'w') as converted:
#     [converted.write('v {} {} {}\n'.format(vertex[0], vertex[1], vertex[2])) for vertex in high_vertices]
#     [converted.write('vt {} {}\n'.format(coordinate[0], coordinate[1])) for coordinate in high_coordinates]
#     for face in high_faces:
#         line = 'f'
#         for vertex_index, coordinate_index in face:
#             line += ' {}/{}'.format(vertex_index, coordinate_index)
#         converted.write(line + '\n')

import os
from scipy.misc import imread, imsave
import numpy as np

normals_name = [name for name in os.listdir('./outputs/automation') if 'normal' in name and 'png' in name]
for normal_name in normals_name:
    path = './outputs/automation/{}'.format(normal_name)
    normal = np.array(imread(path))[:,:,:3]
    # normal = [[[h[0], h[1], h[2]] for h in w] for w in normal]
    imsave(path.replace('.png', '.tga'), normal)