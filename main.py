import numpy as np

# Parameter
ear_index = 15
high_name = 'lsy.obj'

# Load
high = open('./inputs/{}'.format(high_name), 'r').readlines()
# high = open('./datas/high.ply', 'r').readlines()
high_vertices = [[float(element) for element in line[:-1].split(' ')[1:]] for line in high if line[:2] == 'v ']
# high_vertices = [[float(element) for element in each[:-1].split(' ')][:3] for each in high[14:14+53149]]
low = open('./datas/default_head/face.obj', 'r').readlines()
low_vertices = [[float(element) for element in line[:-1].split(' ')[2:]] for line in low if line[:3] == 'v  ']
# low_vertices = [[float(element) for element in line[:-1].split(' ')[:3]] for line in low[14:14+2026]]
low_faces = [[int(index.split('/')[0]) for index in line[:-2].split(' ')[1:]] for line in low if line[:2] == 'f ']

low_eyelids_indices = [int(line[:-1]) for line in open('./datas/eyelids.txt', 'r').readlines()]
low_eyelids = np.array([vertex for index, vertex in enumerate(low_vertices) if index in low_eyelids_indices])

# Face reshaping: 얼굴의 주요 부분(귀, 눈 안쪽 제외)을 high poly 에 맞게 reshape
with open('./datas/high_low_map.txt') as mapping:
    high_low_map = np.array([[int(index) for index in line[:-1].split(' ')] for line in mapping.readlines()])

    for low_index, high_index in high_low_map:
        low_vertices[low_index] = high_vertices[high_index]

# Ear: high 와 low 의 ear border 의 표준편차를 활용해 scaling 후 ear border 의 평균값을 기준으로 ear inside 를 translation
with open('./datas/ears/ear_{}.obj'.format(ear_index), 'r') as ear:
    ear_vertices = np.array([[float(element) for element in line[:-1].split(' ')[2:]] for line in ear.readlines() if line[:3] == 'v  '])

    ear_border_indices = [int(line[:-1]) for line in open('./datas/ear_border.txt', 'r').readlines()]
    high_ear_border_indices = [high_index for low_index, high_index in high_low_map if low_index in ear_border_indices]

    ear_border = np.array([vertex for index, vertex in enumerate(ear_vertices) if index in ear_border_indices])
    high_ear_border = np.array([vertex for index, vertex in enumerate(high_vertices) if index in high_ear_border_indices])

    std_ear_border = np.std(ear_border[:, 2])
    high_std_ear_border = np.std(high_ear_border[:, 2])

    scale = high_std_ear_border / std_ear_border
    ear_vertices *= scale
    ear_border *= scale

    mean_left_high_ear_border = np.mean([each for each in high_ear_border if each[0] > 0], axis=0)
    mean_right_high_ear_border = np.mean([each for each in high_ear_border if each[0] < 0], axis=0)
    mean_left_ear_border = np.mean([each for each in ear_border if each[0] > 0], axis=0)
    mean_right_ear_border = np.mean([each for each in ear_border if each[0] < 0], axis=0)

    left_translation = mean_left_ear_border - mean_left_high_ear_border
    right_translation = mean_right_ear_border - mean_right_high_ear_border

    ear_inside_indices = [int(line[:-1]) for line in open('./datas/ear_inside.txt', 'r').readlines()]
    ear_inside = [(index, ear_vertex) for index, ear_vertex in enumerate(ear_vertices) if index in ear_inside_indices]

    left_ear_inside = [(index, each - left_translation) for index, each in ear_inside if each[0] > 0]
    right_ear_inside = [(index, each - right_translation) for index, each in ear_inside if each[0] < 0]

    for index, vertex in left_ear_inside + right_ear_inside:
        low_vertices[index] = vertex

# Neck
with open('./datas/default_head/neck.obj', 'r') as neck:
    neck = neck.readlines()
    neck_vertices = np.array([[float(element) for element in line[:-1].split(' ')[2:]] for line in neck if line[:3] == 'v  '])
    neck_faces = [[int(index.split('/')[0]) for index in line[:-2].split(' ')[1:]] for line in neck if line[:2] == 'f ']

    face_neck_map = np.array([[int(index) for index in line.split(', ')] for line in open('./datas/face_neck_map.txt', 'r').readlines()])

    face_boundary = [vertex for index, vertex in enumerate(low_vertices) if index in face_neck_map[:, 0]]
    neck_boundary = [vertex for index, vertex in enumerate(neck_vertices) if index in face_neck_map[:, 1]]
    scale = np.std(np.array(face_boundary)[:, 0]) / np.std(np.array(neck_boundary)[:, 0])
    neck_vertices *= scale

    mean_face_boundary = np.mean(face_boundary, axis=0)
    mean_neck_boundary = np.mean(neck_boundary, axis=0)
    distance = mean_face_boundary - mean_neck_boundary
    neck_vertices += distance

    for low_index, low_vertex in enumerate(low_vertices):
        if low_index in face_neck_map[:, 0]:
            index = list(face_neck_map[:, 0]).index(low_index)
            neck_index = face_neck_map[:, 1][index]
            low_vertices[low_index] = neck_vertices[neck_index]

    neck_map = []
    for neck_index, neck_vertex in enumerate(neck_vertices):
        if neck_index in face_neck_map[:, 1]:
            index = list(face_neck_map[:, 1]).index(neck_index)
            neck_map.append(face_neck_map[:, 0][index])
        else:
            neck_map.append(len(low_vertices))
            low_vertices.append(neck_vertex)

    for neck_face in neck_faces:
        face = [neck_map[neck_index - 1] + 1 for neck_index in neck_face]
        low_faces.append(face)

# Inner eyes
if True:
    high_eyelids_indices = [high_index for low_index, high_index in high_low_map if low_index in low_eyelids_indices]
    high_eyelids = [vertex for index, vertex in enumerate(high_vertices) if index in high_eyelids_indices]

    scale = np.std([high_eyelid[0] for high_eyelid in high_eyelids]) / np.std([low_eyelid[0] for low_eyelid in low_eyelids])
    low_eyelids *= scale

    mean_left_low_eyelids = np.mean([low_eyelid for low_eyelid in low_eyelids if low_eyelid[0] > 0], axis=0)
    mean_left_high_eyelids = np.mean([high_eyelid for high_eyelid in high_eyelids if high_eyelid[0] > 0], axis=0)
    mean_right_low_eyelids = np.mean([low_eyelid for low_eyelid in low_eyelids if low_eyelid[0] < 0], axis=0)
    mean_right_high_eyelids = np.mean([high_eyelid for high_eyelid in high_eyelids if high_eyelid[0] < 0], axis=0)

    distance_left = mean_left_low_eyelids - mean_left_high_eyelids
    distance_right = mean_right_low_eyelids - mean_right_high_eyelids

    inner_eyes = [(int(index[:-1]), low_vertices[int(index[:-1])]) for index in open('./datas/inner_eyes.txt', 'r').readlines()]
    left_inner_eyes = [(index, np.array(vertex) * scale - distance_left) for index, vertex in inner_eyes if vertex[0] > 0]
    right_inner_eyes = [(index, np.array(vertex) * scale - distance_right) for index, vertex in inner_eyes if vertex[0] < 0]

    for index, inner_eye in left_inner_eyes + right_inner_eyes:
        low_vertices[index] = inner_eye

# save
with open('./outputs/{}'.format(high_name), 'w') as replaced:
    for low_vertex in low_vertices:
        replaced.write('v  {} {} {}\n'.format(low_vertex[0], low_vertex[1], low_vertex[2]))

    for low_face in low_faces:
        if len(low_face) == 4:
            replaced.write('f {} {} {} {} \n'.format(low_face[0], low_face[1], low_face[2], low_face[3]))
        if len(low_face) == 3:
            replaced.write('f {} {} {} \n'.format(low_face[0], low_face[1], low_face[2]))
