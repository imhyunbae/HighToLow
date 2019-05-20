import numpy as np


class Wrap:
    def __init__(self, input_path):
        high = open('./inputs/{}'.format(input_path), 'r').readlines()
        self.high_vertices = [[float(element) for element in line[:-1].split(' ')[1:]] for line in high if line[:2] == 'v ']
        low = open('./datas/default_head/face.obj', 'r').readlines()
        self.low_vertices = [[float(element) for element in line[:-1].split(' ')[2:]] for line in low if line[:3] == 'v  ']
        self.low_faces = [[int(index.split('/')[0]) for index in line[:-2].split(' ')[1:]] for line in low if line[:2] == 'f ']

        eye_l = open('./datas/default_head/eyes_l.obj', 'r').readlines()
        self.eye_l_vertices = [[float(element) for element in line[:-1].split(' ')[2:]] for line in eye_l if line[:2] == 'v ']
        self.eye_l_faces = [[int(index.split('/')[0]) for index in line[:-2].split(' ')[1:]] for line in eye_l if line[:2] == 'f ']
        eye_r = open('./datas/default_head/eyes_r.obj', 'r').readlines()
        self.eye_r_vertices = [[float(element) for element in line[:-1].split(' ')[2:]] for line in eye_r if line[:2] == 'v ']
        self.eye_r_faces = [[int(index.split('/')[0]) for index in line[:-2].split(' ')[1:]] for line in eye_r if line[:2] == 'f ']

        self.high_low_map = np.array([[int(index) for index in line[:-1].split(' ')] for line in open('./datas/high_low_map.txt').readlines()])

        self.low_eyelids_indices = [int(line[:-1]) for line in open('./datas/eyelids.txt', 'r').readlines()]
        self.low_eyelids = np.array([vertex for index, vertex in enumerate(self.low_vertices) if index in self.low_eyelids_indices])

        self.eye_scale = 1

        mouth = open('./datas/default_head/mouth.obj', 'r').readlines()
        self.mouth_vertices = [[float(element) for element in line[:-1].split(' ')[2:]] for line in mouth if line[:2] == 'v ']
        self.mouth_faces = [[int(index.split('/')[0]) for index in line[:-2].split(' ')[1:]] for line in mouth if line[:2] == 'f ']

    def face(self):
        """
        Face reshaping: 얼굴의 주요 부분(귀, 눈 안쪽 제외)을 high poly 에 맞게 reshape
        """
        for low_index, high_index in self.high_low_map:
            self.low_vertices[low_index] = self.high_vertices[high_index]

    def ear(self, ear_index):
        """
        high 와 low 의 ear border 의 표준편차를 활용해 scaling 후 ear border 의 평균값을 기준으로 ear inside 를 translation
        """
        ear = open('./datas/ears/ear_{}.obj'.format(ear_index), 'r').readlines()
        ear_vertices = np.array([[float(element) for element in line[:-1].split(' ')[2:]] for line in ear if line[:3] == 'v  '])

        ear_border_indices = [int(line[:-1]) for line in open('./datas/ear_border.txt', 'r').readlines()]
        high_ear_border_indices = [high_index for low_index, high_index in self.high_low_map if low_index in ear_border_indices]

        ear_border = np.array([vertex for index, vertex in enumerate(ear_vertices) if index in ear_border_indices])
        high_ear_border = np.array([vertex for index, vertex in enumerate(self.high_vertices) if index in high_ear_border_indices])

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
            self.low_vertices[index] = vertex

    def neck(self):
        neck = open('./datas/default_head/neck.obj', 'r').readlines()
        neck_vertices = np.array([[float(element) for element in line[:-1].split(' ')[2:]] for line in neck if line[:3] == 'v  '])
        neck_faces = [[int(index.split('/')[0]) for index in line[:-2].split(' ')[1:]] for line in neck if line[:2] == 'f ']

        face_neck_map = np.array([[int(index) for index in line.split(', ')] for line in open('./datas/face_neck_map.txt', 'r').readlines()])

        face_boundary = [vertex for index, vertex in enumerate(self.low_vertices) if index in face_neck_map[:, 0]]
        neck_boundary = [vertex for index, vertex in enumerate(neck_vertices) if index in face_neck_map[:, 1]]
        scale = np.std(np.array(face_boundary)[:, 0]) / np.std(np.array(neck_boundary)[:, 0])
        neck_vertices *= scale

        mean_face_boundary = np.mean(face_boundary, axis=0)
        mean_neck_boundary = np.mean(neck_boundary, axis=0)
        distance = mean_face_boundary - mean_neck_boundary
        neck_vertices += distance

        for low_index, low_vertex in enumerate(self.low_vertices):
            if low_index in face_neck_map[:, 0]:
                index = list(face_neck_map[:, 0]).index(low_index)
                neck_index = face_neck_map[:, 1][index]
                self.low_vertices[low_index] = neck_vertices[neck_index]

        neck_map = []
        for neck_index, neck_vertex in enumerate(neck_vertices):
            if neck_index in face_neck_map[:, 1]:
                index = list(face_neck_map[:, 1]).index(neck_index)
                neck_map.append(face_neck_map[:, 0][index])
            else:
                neck_map.append(len(self.low_vertices))
                self.low_vertices.append(neck_vertex)

        for neck_face in neck_faces:
            face = [neck_map[neck_index - 1] + 1 for neck_index in neck_face]
            self.low_faces.append(face)

    def inner_eyes(self):
        high_eyelids_indices = [high_index for low_index, high_index in self.high_low_map if low_index in self.low_eyelids_indices]
        high_eyelids = [vertex for index, vertex in enumerate(self.high_vertices) if index in high_eyelids_indices]

        self.eye_scale = np.std([high_eyelid[0] for high_eyelid in high_eyelids]) / np.std([low_eyelid[0] for low_eyelid in self.low_eyelids])
        scaled_low_eyelids = self.low_eyelids * self.eye_scale

        mean_left_low_eyelids = np.mean([low_eyelid for low_eyelid in scaled_low_eyelids if low_eyelid[0] > 0], axis=0)
        mean_left_high_eyelids = np.mean([high_eyelid for high_eyelid in high_eyelids if high_eyelid[0] > 0], axis=0)
        mean_right_low_eyelids = np.mean([low_eyelid for low_eyelid in scaled_low_eyelids if low_eyelid[0] < 0], axis=0)
        mean_right_high_eyelids = np.mean([high_eyelid for high_eyelid in high_eyelids if high_eyelid[0] < 0], axis=0)

        distance_left = mean_left_low_eyelids - mean_left_high_eyelids
        distance_right = mean_right_low_eyelids - mean_right_high_eyelids

        inner_eyes = [(int(index[:-1]), self.low_vertices[int(index[:-1])]) for index in open('./datas/inner_eyes.txt', 'r').readlines()]
        left_inner_eyes = [(index, np.array(vertex) * self.eye_scale - distance_left) for index, vertex in inner_eyes if vertex[0] > 0]
        right_inner_eyes = [(index, np.array(vertex) * self.eye_scale - distance_right) for index, vertex in inner_eyes if vertex[0] < 0]

        for index, inner_eye in left_inner_eyes + right_inner_eyes:
            self.low_vertices[index] = inner_eye

    # inner eye 의 scale 조절 left, right 따로 해야할지 생각해보고, 그 scale 대로 eyeball 도 scale 한 후
    # scale 전 inner eye와 eye ball의 거리 차이를 그대로 scale해서 적용
    def eye_balls(self):
        mean_left_eyeball = np.mean(self.eye_l_vertices, axis=0)
        mean_right_eyeball = np.mean(self.eye_r_vertices, axis=0)
        mean_left_low_eyelids = np.mean([low_eyelid for low_eyelid in self.low_eyelids if low_eyelid[0] > 0], axis=0)
        mean_right_low_eyelids = np.mean([low_eyelid for low_eyelid in self.low_eyelids if low_eyelid[0] < 0], axis=0)

        distance_left = (mean_left_eyeball - mean_left_low_eyelids) * self.eye_scale
        distance_right = (mean_right_eyeball - mean_right_low_eyelids) * self.eye_scale

        self.eye_l_vertices = np.array(self.eye_l_vertices) * self.eye_scale
        self.eye_r_vertices = np.array(self.eye_r_vertices) * self.eye_scale

        mean_left_eyeball_scaled = np.mean(self.eye_l_vertices, axis=0)
        mean_right_eyeball_scaled = np.mean(self.eye_r_vertices, axis=0)
        low_eyelids_scaled = np.array([vertex for index, vertex in enumerate(self.low_vertices) if index in self.low_eyelids_indices])
        mean_left_low_eyelids_scaled = np.mean([low_eyelid for low_eyelid in low_eyelids_scaled if low_eyelid[0] > 0], axis=0)
        mean_right_low_eyelids_scaled = np.mean([low_eyelid for low_eyelid in low_eyelids_scaled if low_eyelid[0] < 0], axis=0)

        distance_left_scaled = mean_left_low_eyelids_scaled - mean_left_eyeball_scaled
        distance_right_scaled = mean_right_low_eyelids_scaled - mean_right_eyeball_scaled

        self.eye_l_vertices += distance_left_scaled + distance_left
        self.eye_r_vertices += distance_right_scaled + distance_right

    def mouth(self):
        face_mouth_map = np.array([[int(element) for element in line[:-1].split(' ')] for line in open('./datas/mouth.txt', 'r').readlines()])
        low_mouth = np.array([vertex for index, vertex in enumerate(self.low_vertices) if index in face_mouth_map[:, 0]])
        border_mouth = np.array([vertex for index, vertex in enumerate(self.mouth_vertices) if index in face_mouth_map[:, 1]])

        std_low_mouth = np.std(low_mouth[:, 0])
        std_mouth = np.std(border_mouth[:, 0])
        scale = std_low_mouth / std_mouth

        self.mouth_vertices = np.array(self.mouth_vertices) * scale

        mean_low_mouth = np.mean(low_mouth, axis=0)
        mean_mouth = np.mean(border_mouth * scale, axis=0)

        distance = mean_low_mouth - mean_mouth
        self.mouth_vertices += distance

        # mouth_vertices = np.array([[index, vertex] for index, vertex in enumerate(self.mouth_vertices) if index not in face_mouth_map[:, 1]])

        mouth_map = []
        for mouth_index, mouth_vertex in enumerate(self.mouth_vertices):
            if mouth_index in face_mouth_map[:, 1]:
                index = list(face_mouth_map[:, 1]).index(mouth_index)
                mouth_map.append(face_mouth_map[:, 0][index])
            else:
                mouth_map.append(len(self.low_vertices))
                self.low_vertices.append(mouth_vertex)

        for mouth_face in self.mouth_faces:
            face = [mouth_map[mouth_index - 1] + 1 for mouth_index in mouth_face]
            self.low_faces.append(face)

    def save(self, output_path):
        def write_vertices_face(output, name, vertices, faces, o):
            # output.write('o {}\n'.format(name))

            for vertex in vertices:
                output.write('v  {} {} {}\n'.format(vertex[0], vertex[1], vertex[2]))

            for face in faces:
                if len(face) == 4:
                    output.write('f {} {} {} {} \n'.format(face[0] + o, face[1] + o, face[2] + o, face[3] + o))
                if len(face) == 3:
                    output.write('f {} {} {} \n'.format(face[0] + o, face[1] + o, face[2] + o))

        with open('./outputs/{}'.format(output_path), 'w') as replaced:
            offset = 0
            write_vertices_face(replaced, 'face', self.low_vertices, self.low_faces, offset)
            offset += len(self.low_vertices)
            write_vertices_face(replaced, 'eye_l', self.eye_l_vertices, self.eye_l_faces, offset)
            offset += len(self.eye_l_vertices)
            write_vertices_face(replaced, 'eye_r', self.eye_r_vertices, self.eye_r_faces, offset)
            # offset += len(self.eye_r_vertices)
            # write_vertices_face(replaced, 'mouth', self.mouth_vertices, self.mouth_face, offset)


if __name__=='__main__':
    high_name = 'cjs.obj'
    wrap = Wrap(input_path=high_name)
    wrap.face()
    wrap.ear(ear_index=8)
    wrap.neck()
    wrap.inner_eyes()
    wrap.eye_balls()
    wrap.mouth()
    wrap.save(output_path=high_name)