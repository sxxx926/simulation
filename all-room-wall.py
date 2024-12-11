import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# 病床类
class Bed:
    def __init__(self, x, y, width, height, bedroom=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.has_patient = False
        self.bedroom = bedroom  # 关联房间对象

    def get_right_top(self):
        # 获取病床的右上角坐标
        return self.x + self.width, self.y + self.height

    def get_bounds(self):
        # 获取病床的边界
        return self.x, self.y, self.x + self.width, self.y + self.height

    def check_collision(self, patient):
        # 检查病人与病床是否发生碰撞
        px, py = patient.x, patient.y
        bed_x, bed_y, bed_right, bed_top = self.get_bounds()
        if bed_x < px < bed_right and bed_y < py < bed_top:
            return True  # 病人与病床发生碰撞
        return False  # 没有碰撞


# 病人类
class Patient:
    def distance_to_staircase(self, staircase):
        return np.sqrt((self.x - staircase.door_x) ** 2 + (self.y - staircase.door_y) ** 2)

    def __init__(self, bed, bed_index):
        self.x = bed.x + bed.width / 2
        self.y = bed.y + bed.height
        self.vx = 0
        self.vy = 0
        self.bed = bed
        self.target_dx = 0
        self.target_dy = 0
        if bed_index <= 2:
            self.speed = 0.05
        elif 3 <= bed_index < 5:
            self.speed = 0.08
        else:
            self.speed = 0.1

    def update_position(self):
        room = self.bed.bedroom
        if room is not None:
            # 先判断是否已经在房间门口附近，如果不在则朝着房间门口移动
            door_center_x = room.door_x+0.6
            door_center_y = room.door_y+1
            distance_to_door = np.sqrt((self.x - door_center_x) ** 2 + (self.y - door_center_y) ** 2)
            if distance_to_door > 0.5:
                direction_x = door_center_x - self.x
                direction_y = door_center_y - self.y
                self.vx = direction_x / distance_to_door * self.speed
                self.vy = direction_y / distance_to_door * self.speed
            else:
                # 到达房间门口后，考虑与其他病人的间距避让
                other_patients = [p for p in room.patients if p!= self]
                for other_patient in other_patients:
                    distance_to_other = np.sqrt((self.x - other_patient.x) ** 2 + (self.y - other_patient.y) ** 2)
                    if distance_to_other < 1.0:
                        avoid_x = self.x - other_patient.x
                        avoid_y = self.y - other_patient.y
                        avoidance_distance = np.sqrt(avoid_x ** 2 + avoid_y ** 2)
                        if avoidance_distance > 0:
                            self.vx += (avoid_x / avoidance_distance) * 0.1
                            self.vy += (avoid_y / avoidance_distance) * 0.1

                # 寻找距离病人最近的楼梯间并朝着其移动
                closest_staircase = self.find_closest_staircase()
                direction_x = closest_staircase.door_x - self.x
                direction_y = closest_staircase.door_y - self.y
                distance_to_stair_door = np.sqrt(direction_x ** 2 + direction_y ** 2)

                if distance_to_stair_door > 0:
                    self.vx = direction_x / distance_to_stair_door * self.speed
                    self.vy = direction_y / distance_to_stair_door * self.speed

                # 避开病床（这部分逻辑保持不变，依然要避免移动过程中和病床碰撞）
                for bed in room.beds:
                    bed_center_x = bed.x + bed.width / 2
                    bed_center_y = bed.y + bed.height / 2
                    distance_to_bed = np.sqrt((self.x - bed_center_x) ** 2 + (self.y - bed_center_y) ** 2)
                    if distance_to_bed < 1.5:
                        avoid_x = self.x - bed_center_x
                        avoid_y = self.y - bed_center_y
                        avoidance_distance = np.sqrt(avoid_x ** 2 + avoid_y ** 2)
                        if avoidance_distance > 0:
                            self.vx += (avoid_x / avoidance_distance) * self.speed
                            self.vy += (avoid_y / avoidance_distance) * self.speed

                # 判断是否到达最近的楼梯间门口
                if distance_to_stair_door <= self.speed:
                    room.patients.remove(self)

            # 更新病人位置
            self.x += self.vx
            self.y += self.vy
        else:
            print("Error: Patient's bed is not associated with a room!")

    def find_closest_staircase(self):
        # 考虑当前所在房间门口位置，筛选出合理的可到达的楼梯间
        accessible_staircases = []
        for staircase in staircases_one and staircases_two :
            # 这里可以添加更多复杂判断，比如中间是否有障碍物阻挡等，简单示例只考虑直线距离是否可到达
            is_accessible = True
            accessible_staircases.append(staircase)

        if accessible_staircases:
            return min(accessible_staircases, key=lambda s: self.distance_to_staircase(s))
        else:
            return None

class Staircase:
    def __init__(self, x, y, width, height,door_x, door_y, door_width):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width

class Office:
    def __init__(self, x, y, width, height,door_x, door_y, door_width):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width



# 房间类
class Room:
    def __init__(self, x, y, width, height, door_x, door_y, door_width, beds):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width
        self.beds = beds
        self.patients = []

        # 在初始化时，为每个病床设置所属的房间
        for bed in self.beds:
            bed.bedroom = self  # 每个病床都知道自己所在的房间

    def initialize_patients(self):
        for index, bed in enumerate(self.beds):  # 获取病床索引
            if not bed.has_patient:
                patient = Patient(bed, index)  # 传递病床索引创建病人实例
                self.patients.append(patient)
                bed.has_patient = True

height_one=5.5
height_two=3.37
staircase1 = Staircase(0, 0, 3.01, height_one,0.6,5.87,1.2)
staircase2 = Staircase(136.98, 0, 3.01, height_one,139.76,5.87,1.2)
staircase3 = Staircase(32.5, 8.49, 6.63, 3.37,38.53,8.49,1.2)
staircase4 = Staircase(61.99, 8.49, 9.445, 3.37,70.12,8.49,3.37)
staircase5 = Staircase(71.805, 8.49, 6.13, 3.37,77.705,8.49,1.8)
staircase6 = Staircase(101.23, 8.49, 6.26, 3.37,102.2,8.49,1.2)
staircases_one=[staircase1,staircase2]
staircases_two=[staircase3,staircase4,staircase5,staircase6]

office1=Office(58.87,-1,9.38,height_one,63.93,4.87,1.2)
office2=Office(68.62,-1,2.75,height_one,70.365,4.87,1.2)
office3=Office(71.87,-1,9.25,height_one,76.43,4.87,1.2)
office4=Office(0,8.49,2.88,3.37,2.65,8.49,1.2)
office5=Office(office4.x+2.88+0.37,8.49,2.88,3.37,office4.door_x+2.88+0.37,8.49,1.2)
office6=Office(office5.x+2.88+0.37,8.49,2.88,3.37,office5.door_x+2.88+0.37,8.49,1.2)
office7=Office(office6.x+2.88+0.37,8.49,2.88,3.37,office6.door_x+2.88+0.37,8.49,1.2)
office8=Office(office7.x+2.88+0.37,8.49,2.88,3.37,office7.door_x+2.88+0.37,8.49,1.2)
office9=Office(office8.x+2.88+0.37,8.49,2.88,3.37,office8.door_x+2.88+0.37,8.49,1.2)
office10=Office(office9.x+2.88+0.37,8.49,2.88,3.37,office9.door_x+2.88+0.37,8.49,1.2)
office11=Office(office10.x+2.88+0.37,8.49,2.88,3.37,office10.door_x+2.88+0.37,8.49,1.2)
office12=Office(office11.x+2.88+0.37,8.49,2.88,3.37,office11.door_x+2.88+0.37,8.49,1.2)
office13=Office(office12.x+2.88+0.37,8.49,2.88,3.37,office12.door_x+2.88+0.37,8.49,1.2)
office14=Office(39.13,8.49,2.75,3.37,40.1,8.49,1.2)
office15=Office(office14.x+2.88+0.37,8.49,2.88,3.37,office14.door_x+2.88+0.37,8.49,1.2)
office16=Office(office15.x+2.88+0.37,8.49,2.88,3.37,office15.door_x+2.88+0.37,8.49,1.2)
office17=Office(office16.x+2.88+0.37,8.49,2.88,3.37,office16.door_x+2.88+0.37,8.49,1.2)
office18=Office(office17.x+2.88+0.37,8.49,2.88,3.37,office17.door_x+2.88+0.37,8.49,1.2)
office19=Office(office18.x+2.88+0.37,8.49,2.88,3.37,office18.door_x+2.88+0.37,8.49,1.2)
office20=Office(58.87,8.49,2.75,4.5,60.615,8.49,1.2)
office21=Office(78.305,8.49,2.815,4.5,80.0825,8.49,1.2)
office22=Office(81.86,8.49,2.88,3.37,84.51,8.49,1.2)
office23=Office(office22.x+2.88+0.37,8.49,2.88,3.37,office22.door_x+2.88+0.37,8.49,1.2)
office24=Office(office23.x+2.88+0.37,8.49,2.88,3.37,office23.door_x+2.88+0.37,8.49,1.2)
office25=Office(office24.x+2.88+0.37,8.49,2.88,3.37,office24.door_x+2.88+0.37,8.49,1.2)
office26=Office(office25.x+2.88+0.37,8.49,2.88,3.37,office25.door_x+2.88+0.37,8.49,1.2)
office27=Office(office26.x+2.88+0.37,8.49,2.75,3.37,office26.door_x+2.88+0.37,8.49,1.2)
office28=Office(107.86,8.49,2.88,3.37,108.46,8.49,1.2)
office29=Office(office28.x+2.88+0.37,8.49,2.75,3.37,office28.door_x+2.88+0.37,8.49,1.2)
office30=Office(office29.x+2.88+0.37,8.49,2.75,3.37,office29.door_x+2.88+0.37,8.49,1.2)
office31=Office(office30.x+2.88+0.37,8.49,2.75,3.37,office30.door_x+2.88+0.37,8.49,1.2)
office32=Office(office31.x+2.88+0.37,8.49,2.75,3.37,office31.door_x+2.88+0.37,8.49,1.2)
office33=Office(office32.x+2.88+0.37,8.49,2.75,3.37,office32.door_x+2.88+0.37,8.49,1.2)
office34=Office(office33.x+2.88+0.37,8.49,2.75,3.37,office33.door_x+2.88+0.37,8.49,1.2)
office35=Office(office34.x+2.88+0.37,8.49,2.75,3.37,office34.door_x+2.88+0.37,8.49,1.2)
office36=Office(office35.x+2.88+0.37,8.49,2.75,3.37,office35.door_x+2.88+0.37,8.49,1.2)
office37=Office(office36.x+2.88+0.37,8.49,2.75,3.37,office36.door_x+2.88+0.37,8.49,1.2)
offices=[office1,office2,office3,office4,office5,office6,office7,office8,office9,office10,office11,office12,office13,office14,office15,office16,office17,office18,office19,office20,office21,office22,office23,office24,office25,office26,office27,office28,office29,office30,office31,office32,office33,office34,office35,office36,office37]

# 初始化房间和病床时，确保病床正确关联到房间
room1 = Room(3.38, 0, 2.88, 5.5, 5.965, 5.87, 1.2,
             [Bed(3.75, 0.705, 2, 1), Bed(3.75, 2.328, 2, 1), Bed(3.75, 4.003, 2, 1)])
room1.initialize_patients()

room2 = Room(6.565, 0, 2.88, 5.5, 9.215, 5.87, 1.2,
             [Bed(6.935, 0.705, 2, 1), Bed(6.935, 2.328, 2, 1), Bed(6.935,4.003, 2, 1)])
room2.initialize_patients()

room3 = Room(9.815, 0, 6.13, 5.5, 13.25, 5.87, 1.2,
             [Bed(10.185, 0.705, 2, 1), Bed(10.185, 2.328, 2, 1), Bed(10.185,4.003, 2, 1), Bed(14.315, 0.705, 2, 1), Bed(14.315, 2.328, 2, 1), Bed(14.315,4.003, 2, 1)])
room3.initialize_patients()

room4 = Room(16.315, 0, 6.13, 5.5, 19.75, 5.87, 1.2,
             [Bed(16.685, 0.705, 2, 1), Bed(16.685, 2.328, 2, 1), Bed(16.685,4.003, 2, 1), Bed(20.815, 0.705, 2, 1), Bed(20.815, 2.328, 2, 1), Bed(20.815,4.003, 2, 1)])
room4.initialize_patients()

room5 = Room(22.815, 0, 6.13, 5.5, 26.25, 5.87, 1.2,
             [Bed(23.185, 0.705, 2, 1), Bed(23.185, 2.328, 2, 1), Bed(23.185,4.003, 2, 1), Bed(27.315, 0.705, 2, 1), Bed(27.315, 2.328, 2, 1), Bed(27.315,4.003, 2, 1)])
room5.initialize_patients()

room6 = Room(29.315, 0, 2.88, 5.5, 31.965, 5.87, 1.2,
             [Bed(29.685, 0.705, 2, 1), Bed(29.685, 2.328, 2, 1), Bed(29.685,4.003, 2, 1)])
room6.initialize_patients()

room7 = Room(32.565, 0, 2.88, 5.5, 35.215, 5.87, 1.2,
             [Bed(32.935, 0.705, 2, 1), Bed(32.935, 2.328, 2, 1), Bed(32.935,4.003, 2, 1)])
room7.initialize_patients()

room8 = Room(35.815, 0, 6.13, 5.5, 39.25, 5.87, 1.2,
             [Bed(36.185, 0.705, 2, 1), Bed(36.185, 2.328, 2, 1), Bed(36.185,4.003, 2, 1), Bed(40.315, 0.705, 2, 1), Bed(40.315, 2.328, 2, 1), Bed(40.315,4.003, 2, 1)])
room8.initialize_patients()

room9 = Room(42.315, 0, 6.13, 5.5, 45.75, 5.87, 1.2,
             [Bed(42.685, 0.705, 2, 1), Bed(42.685, 2.328, 2, 1), Bed(42.685,4.003, 2, 1), Bed(46.815, 0.705, 2, 1), Bed(46.815, 2.328, 2, 1), Bed(46.815,4.003, 2, 1)])
room9.initialize_patients()

room10 = Room(48.815, 0, 6.13, 5.5, 52.25, 5.87, 1.2,
             [Bed(49.185, 0.705, 2, 1), Bed(49.185, 2.328, 2, 1), Bed(49.185,4.003, 2, 1), Bed(53.315, 0.705, 2, 1), Bed(53.315, 2.328, 2, 1), Bed(53.315,4.003, 2, 1)])
room10.initialize_patients()

room11 = Room(55.315, 0, 2.88, 5.5, 56.285, 5.87, 1.2,
             [Bed(56.5, 0.705, 2, 1), Bed(56.5, 2.328, 2, 1), Bed(56.5,4.003, 2, 1)])
room11.initialize_patients()

room12 = Room(81.86, 0, 2.88, 5.5, 84.445, 5.87, 1.2,
             [Bed(82.23, 0.705, 2, 1), Bed(82.23, 2.328, 2, 1), Bed(82.23,4.003, 2, 1)])
room12.initialize_patients()

room13 = Room(85.045, 0, 6.13, 5.5, 88.48, 5.87, 1.2,
             [Bed(85.415, 0.705, 2, 1), Bed(85.415, 2.328, 2, 1), Bed(85.415,4.003, 2, 1), Bed(89.545, 0.705, 2, 1), Bed(89.545, 2.328, 2, 1), Bed(89.545,4.003, 2, 1)])
room13.initialize_patients()

room14 = Room(91.545, 0, 6.13, 5.5, 94.98, 5.87, 1.2,
             [Bed(91.915, 0.705, 2, 1), Bed(91.915, 2.328, 2, 1), Bed(91.915,4.003, 2, 1), Bed(96.045, 0.705, 2, 1), Bed(96.045, 2.328, 2, 1), Bed(96.045,4.003, 2, 1)])
room14.initialize_patients()

room15 = Room(98.045, 0, 6.13, 5.5, 101.48, 5.87, 1.2,
             [Bed(98.415, 0.705, 2, 1), Bed(98.415, 2.328, 2, 1), Bed(98.415,4.003, 2, 1), Bed(102.545, 0.705, 2, 1), Bed(102.545, 2.328, 2, 1), Bed(102.545,4.003, 2, 1)])
room15.initialize_patients()

room16 = Room(104.545, 0, 2.88, 5.5, 105.515, 5.87, 1.2,
             [Bed(105.795, 0.705, 2, 1), Bed(105.795, 2.328, 2, 1), Bed(105.795,4.003, 2, 1)])
room16.initialize_patients()

room17 = Room(107.795, 0, 2.88, 5.5, 108.765, 5.87, 1.2,
             [Bed(109.045, 0.705, 2, 1), Bed(109.045, 2.328, 2, 1), Bed(109.045,4.003, 2, 1)])
room17.initialize_patients()

room18 = Room(111.045, 0, 6.13, 5.5, 114.48, 5.87, 1.2,
             [Bed(111.415, 0.705, 2, 1), Bed(111.415, 2.328, 2, 1), Bed(111.415,4.003, 2, 1),Bed(115.545, 0.705, 2, 1), Bed(115.545, 2.328, 2, 1), Bed(115.545,4.003, 2, 1)])
room18.initialize_patients()

room19 = Room(117.545, 0, 6.13, 5.5, 120.98, 5.87, 1.2,
             [Bed(117.915, 0.705, 2, 1), Bed(117.915, 2.328, 2, 1), Bed(117.915,4.003, 2, 1),Bed(122.045, 0.705, 2, 1), Bed(122.045, 2.328, 2, 1), Bed(122.045,4.003, 2, 1)])
room19.initialize_patients()

room20 = Room(124.045, 0, 6.13, 5.5, 127.48, 5.87, 1.2,
             [Bed(124.415, 0.705, 2, 1), Bed(124.415, 2.328, 2, 1), Bed(124.415,4.003, 2, 1),Bed(128.545, 0.705, 2, 1), Bed(128.545, 2.328, 2, 1), Bed(128.545,4.003, 2, 1)])
room20.initialize_patients()

room21 = Room(130.545, 0, 2.88, 5.5, 131.515, 5.87, 1.2,
             [Bed(131.795, 0.705, 2, 1), Bed(131.795, 2.328, 2, 1), Bed(131.795,4.003, 2, 1)])
room21.initialize_patients()

room22 = Room(133.795, 0, 2.815, 5.5, 136.38, 5.87, 1.2,
             [Bed(134.165, 0.705, 2, 1), Bed(134.165, 2.328, 2, 1), Bed(134.165,4.003, 2, 1)])
room22.initialize_patients()


rooms_one= [room1, room2,room6,room7,room11,room12,room16,room17,room21,room22]
rooms_two= [room3,room4,room5,room8,room9,room10,room13,room14,room15,room18,room19,room20]
# 更新病人位置
def update_patients():
    all_patients = room1.patients + room2.patients+ room3.patients + room4.patients + room5.patients + room6.patients + room7.patients + room8.patients + room9.patients + room10.patients + room11.patients +room12.patients+ room13.patients + room14.patients + room15.patients + room16.patients + room17.patients + room18.patients + room19.patients + room20.patients + room21.patients+ room22.patients
    all_evacuated = True
    for patient in all_patients:
        if patient in room1.patients or patient in room2.patients or patient in room3.patients or patient in room4.patients or patient in room5.patients or patient in room6.patients or patient in room7.patients or patient in room8.patients or patient in room9.patients or patient in room10.patients or patient in room11.patients or  patient in room12.patients or patient in room13.patients or patient in room14.patients or patient in room15.patients or patient in room16.patients or patient in room17.patients or patient in room18.patients or patient in room19.patients or patient in room20.patients or patient in room21.patients or patient in room22.patients:
            all_evacuated = False
            patient.update_position()
    return all_evacuated


# 创建图形窗口
fig, ax = plt.subplots()

def draw():
    ax.set_xlim(0, 20)  # 根据实际情况调整合适的坐标轴范围
    ax.set_ylim(-2, 20)
    ax.set_aspect('equal', adjustable='box')
    ax.cla()
    wall_thickness = 0.37
    # 绘制楼梯间
    for staircase in staircases_one:
        # 绘制楼梯的墙壁
        left_wall = plt.Rectangle((staircase.x,staircase.y), wall_thickness, staircase.height+wall_thickness*2 , color='black', lw=2, ec="black", fill=True)
        ax.add_patch(left_wall)

        right_wall = plt.Rectangle((staircase.x + staircase.width + wall_thickness, staircase.y), wall_thickness, staircase.height+wall_thickness*2, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(right_wall)

        bottom_wall = plt.Rectangle((staircase.x+wall_thickness, staircase.y), staircase.width, wall_thickness, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(bottom_wall)

        top_wall = plt.Rectangle((staircase.x + wall_thickness + staircase.door_width, staircase.y + staircase.height + wall_thickness), staircase.width - staircase.door_width, 0.37, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(top_wall)

        # 绘制楼梯的门
        door = plt.Rectangle((staircase.door_x - staircase.door_width / 2, staircase.door_y), staircase.door_width, wall_thickness,color='brown', lw=2, ec="black")
        ax.add_patch(door)

    for staircase in staircases_two:
        # 绘制楼梯的墙壁
        left_wall = plt.Rectangle((staircase.x,staircase.y), wall_thickness, staircase.height+wall_thickness*2 , color='black', lw=2, ec="black", fill=True)
        ax.add_patch(left_wall)

        right_wall = plt.Rectangle((staircase.x + staircase.width + wall_thickness, staircase.y), wall_thickness, staircase.height+wall_thickness*2, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(right_wall)

        bottom_wall = plt.Rectangle((staircase.x+wall_thickness, staircase.y), staircase.width-staircase.door_width, wall_thickness, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(bottom_wall)

        top_wall = plt.Rectangle((staircase.x + wall_thickness , staircase.y + staircase.height + wall_thickness), staircase.width , 0.37, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(top_wall)

        # 绘制楼梯的门
        door = plt.Rectangle((staircase.door_x - staircase.door_width / 2, staircase.door_y), staircase.door_width, wall_thickness,color='brown', lw=2, ec="black")
        ax.add_patch(door)

    for office in offices:
        # 绘制办公室的墙壁
        left_wall = plt.Rectangle((office.x,office.y), wall_thickness, office.height+wall_thickness*2 , color='black', lw=2, ec="black", fill=True)
        ax.add_patch(left_wall)

        right_wall = plt.Rectangle((office.x + office.width + wall_thickness, office.y), wall_thickness, office.height+wall_thickness*2, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(right_wall)

        bottom_wall = plt.Rectangle((office.x+wall_thickness, office.y), office.width, wall_thickness, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(bottom_wall)

        top_wall = plt.Rectangle((office.x+wall_thickness, office.y + office.height + wall_thickness), office.width , wall_thickness, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(top_wall)

        # 绘制办公室的门
        door = plt.Rectangle((office.door_x - office.door_width / 2, office.door_y), office.door_width, wall_thickness, color='brown', lw=2, ec="black")
        ax.add_patch(door)

    # 绘制房间的墙壁
    for room in rooms_one:

        #绘制左侧墙壁
        left_wall = plt.Rectangle((room.x, room.y), wall_thickness, room.height+wall_thickness*2 , color='black', lw=2, ec="black", fill=True)
        ax.add_patch(left_wall)
        #绘制右侧墙壁
        right_wall = plt.Rectangle((room.x + room.width + wall_thickness, room.y), wall_thickness, room.height+wall_thickness*2 , color='black', lw=2, ec="black", fill=True)
        ax.add_patch(right_wall)
        #绘制下侧墙壁
        bottom_wall = plt.Rectangle((room.x+wall_thickness, room.y), room.width , wall_thickness, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(bottom_wall)
        # 绘制上部墙壁
        top_wall = plt.Rectangle((room.x + wall_thickness, room.y + room.height + wall_thickness), room.width - room.door_width, wall_thickness, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(top_wall)

        # 绘制房间内部空间
        inner_rect = plt.Rectangle((room.x + wall_thickness, room.y + wall_thickness), room.width ,room.height , color='lightblue' , lw=2, ec="black")
        ax.add_patch(inner_rect)

        # 绘制房间的门
        door = plt.Rectangle((room.door_x - room.door_width / 2, room.door_y), room.door_width, wall_thickness, color='brown', lw=2, ec="black")
        ax.add_patch(door)

        for bed in room1.beds + room2.beds + room6.beds + room7.beds+ room11.beds + room12.beds + room16.beds + room17.beds + room21.beds+ room22.beds:
            ax.add_patch(plt.Rectangle((bed.x, bed.y), bed.width, bed.height, color='brown', lw=2, ec="black"))

    for room in rooms_two:
        # 绘制房间的墙壁
        # 绘制左侧墙壁
        left_wall = plt.Rectangle((room.x, room.y), wall_thickness, room.height + wall_thickness * 2, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(left_wall)
        # 绘制右侧墙壁
        right_wall = plt.Rectangle((room.x + room.width + wall_thickness, room.y), wall_thickness, room.height + wall_thickness * 2, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(right_wall)
        # 绘制下侧墙壁
        bottom_wall = plt.Rectangle((room.x + wall_thickness, room.y), room.width, wall_thickness, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(bottom_wall)
        # 绘制上部墙壁(左侧)
        top_wall_left = plt.Rectangle((room.x + wall_thickness, room.y + room.height + wall_thickness), room.width/2 - room.door_width/2, wall_thickness, color='black', lw=2, ec="black",fill=True)
        ax.add_patch(top_wall_left)
        # 绘制上部墙壁(右侧)
        top_wall_right = plt.Rectangle((room.x + wall_thickness + room.width/2 + room.door_width/2, room.y + room.height + wall_thickness), room.width/2 - room.door_width/2, wall_thickness, color='black', lw=2, ec="black", fill=True)
        ax.add_patch(top_wall_right)
        # 绘制房间内部空间
        inner_rect = plt.Rectangle((room.x + wall_thickness, room.y + wall_thickness), room.width, room.height,color='lightblue', lw=2)
        ax.add_patch(inner_rect)
        #绘制房间的门
        door = plt.Rectangle((room.door_x - room.door_width / 2, room.door_y), room.door_width, 0.37, color='brown', lw=2, ec="black")
        ax.add_patch(door)

    # 绘制房间的病床
    for bed in  room3.beds + room4.beds + room5.beds + room8.beds+ room9.beds + room10.beds+room13.beds + room14.beds + room15.beds + room18.beds+ room19.beds + room20.beds:
        ax.add_patch(plt.Rectangle((bed.x, bed.y), bed.width, bed.height, color='brown', lw=2, ec="black"))

        # 绘制病人（遍历所有房间的病人列表合并后的数据）
        all_patients = []
        for room in rooms_one:
            all_patients.extend(room.patients)
        for room in rooms_two:
            all_patients.extend(room.patients)
        for patient in all_patients:
            ax.plot(patient.x, patient.y, 'ro', markersize=1)

# 动画函数
def animate(i):
    if update_patients():
        ani.event_source.stop()
    draw()


ani = animation.FuncAnimation(fig, animate, frames=200, interval=50, repeat=False)
plt.show()
