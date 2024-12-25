import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

wall_thickness=0.37
#楼梯类
class Staircase:
    def __init__(self, x, y, width, height, door_x, door_y, door_width):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width

    # 获取楼梯间的出口坐标
    def get_exit_coordinates(self):
        # 获取楼梯间的出口坐标
        return self.door_x ,self.door_y

    def is_within_bounds(self, x, y):
        # 检查人是否在楼梯间内
        return (self.x + wall_thickness <= x <= self.x + wall_thickness + self.width and
                self.y + wall_thickness <= y <= self.y + wall_thickness + self.height)
#办公室类
class Office:
    def __init__(self, x, y, width, height, door_x, door_y, door_width):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width

#病床类
class Bed:
    def __init__(self, x, y, width, height, bedroom=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.has_patient = False
        self.bedroom = bedroom  # 关联房间对象
# 房间类
class Room:
    def __init__(self, x, y, width, height, door_x, door_y, door_width, beds,  staircase=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width
        self.beds = beds
        self.patients = []
        self.staircase = staircase  # 关联楼梯对象

        # 在初始化时，为每个病床设置所属的房间
        for bed in self.beds:
            bed.bedroom = self  # 每个病床都知道自己所在的房间
    #初始化病人
    def initialize_patients(self):
        obstacles = []
        for bed in self.beds:
            obstacle_x = bed.x
            obstacle_y = bed.y
            obstacle_right = bed.x + bed.width
            obstacle_top = bed.y + bed.height
            obstacles.append((obstacle_x, obstacle_y, obstacle_right, obstacle_top))
        for wall in all_walls:
            obstacle_x = wall.get_x()
            obstacle_y = wall.get_y()
            obstacle_right = wall.get_x() + wall.get_width()
            obstacle_top = wall.get_y() + wall.get_height()
            obstacles.append((obstacle_x, obstacle_y, obstacle_right, obstacle_top))
        for index, bed in enumerate(self.beds):  # 获取病床索引
            patient = Patient(bed, index, obstacles=obstacles)
            self.patients.append(patient)
            bed.has_patient = True


# 病人类
class Patient:
    def __init__(self, bed, speed=0.05, avoidance_coefficient=0.5, avoidance_distance=1.5, obstacles=[]):
        self.x = bed.x + bed.width / 2
        self.y = bed.y + bed.height
        self.vx = 0
        self.vy = 0
        self.bed = bed
        self.target_dx = 0
        self.target_dy = 0
        self.speed = speed
        self.avoidance_coefficient = avoidance_coefficient
        self.avoidance_distance = avoidance_distance
        self.room = bed.bedroom
        self.obstacles = obstacles

    def find_closest_staircase(self):
        closest_distance = float('inf')
        closest_staircase = None
        for staircase in staircases:
            distance = np.sqrt((self.x - staircase.door_x) ** 2 + (self.y - staircase.door_y) ** 2)
            is_blocked = False
            for obstacle_x, obstacle_y, obstacle_right, obstacle_top in self.obstacles:
                if obstacle_x < self.x < obstacle_right and obstacle_y < self.y < obstacle_top:
                    is_blocked = True
                    break
            if not is_blocked and distance < closest_distance:
                closest_distance = distance
                closest_staircase = staircase
        return closest_staircase

    def update_position(self, obstacle_bounds):
        room = self.bed.bedroom
        if room is not None:
            # 先判断是否已经在房间门口附近，如果不在则朝着房间门口移动
            door_center_x = room.door_x
            door_center_y = room.door_y + 1
            distance_to_door = np.sqrt((self.x - door_center_x) ** 2 + (self.y - door_center_y) ** 2)
            # 未到达房间门口，继续向门口移动
            if distance_to_door > 0.3:
                direction_x = door_center_x - self.x
                direction_y = door_center_y - self.y
                self.vx = direction_x / distance_to_door * self.speed
                self.vy = direction_y / distance_to_door * self.speed
            else:
                # 到达房间门口后，考虑与其他病人的间距避让
                other_patients = [p for p in room.patients if p != self]
                for other_patient in other_patients:
                    distance_to_other = np.sqrt((self.x - other_patient.x) ** 2 + (self.y - other_patient.y) ** 2)
                    if distance_to_other < 0.25:
                        avoid_x = self.x - other_patient.x
                        avoid_y = self.y - other_patient.y
                        avoidance_distance = np.sqrt(avoid_x ** 2 + avoid_y ** 2)
                        if avoidance_distance > 0:
                            self.vx += (avoid_x / avoidance_distance) * 0.1
                            self.vy += (avoid_y / avoidance_distance) * 0.1

                # 寻找距离病人最近的楼梯间并朝着其移动
                closest_staircase = self.find_closest_staircase()
                if closest_staircase is not None:
                    direction_x = closest_staircase.door_x - self.x
                    direction_y = closest_staircase.door_y - self.y
                    distance_to_stair_door = np.sqrt(direction_x ** 2 + direction_y ** 2)

                    if distance_to_stair_door > 0:
                        self.vx = direction_x / distance_to_stair_door * self.speed
                        self.vy = direction_y / distance_to_stair_door * self.speed

                    # 判断是否到达最近的楼梯间门口
                    if distance_to_stair_door <= self.speed:
                        room.patients.remove(self)
                else:
                    # 处理没有找到可到达楼梯间的情况，例如可以打印一条日志
                    print("No accessible staircase found for this patient.")

            # 更新病人位置
            self.x += self.vx
            self.y += self.vy
        else:
            print("Error: Patient's bed is not associated with a room!")

    def avoid_obstacle(self, obstacle_x, obstacle_y, obstacle_right, obstacle_top):
        # 检查与障碍物的碰撞
        if obstacle_x < self.x < obstacle_right and obstacle_y < self.y < obstacle_top:
            avoid_x = self.x - (obstacle_x + obstacle_right) / 2
            avoid_y = self.y - (obstacle_y + obstacle_top) / 2
            avoidance_distance = np.sqrt(avoid_x ** 2 + avoid_y ** 2)
            if avoidance_distance > 0:
                # 减小避障力度
                self.vx += (avoid_x / avoidance_distance) * self.speed * 0.5
                self.vy += (avoid_y / avoidance_distance) * self.speed * 0.5
            return True
        return False




def update_patients():
    all_patients = room1.patients + room2.patients + room3.patients
    all_evacuated = True
    for patient in all_patients:
        if patient in patient.room.patients:  # 直接判断病人是否还在其所在房间的病人列表中
            all_evacuated = False
            patient.update_position(all_patients)  # 将所有病人列表传递给 update_position 方法
    return all_evacuated

staircase1 = Staircase(0, 0, 3.01, 5.5,0.6,5.87,1.2)
staircases=[staircase1]
office1 = Office(16.315, 0, 6.13, 5.5, 19.75, 5.87, 1.2)
offices=[office1]
all_walls = []
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

rooms_one = [room1, room2]
rooms_two=[room3]
some_interaction_distance = 1.0  # 行人之间相互作用距离阈值
some_interaction_coefficient = 0.3  # 行人之间相互作用系数

# 创建图形窗口
fig, ax = plt.subplots()

def draw():
    ax.set_xlim(0, 20)
    ax.set_ylim(-2, 20)
    ax.set_aspect('equal', adjustable='box')
    ax.cla()

    def draw_rect(ax, x, y, width, height, color, lw, ec, fill=False):
        rect = plt.Rectangle((x, y), width, height, color=color, lw=lw, ec=ec, fill=fill)
        ax.add_patch(rect)
        return rect
    for staircase in staircases:
        # 绘制楼梯的墙壁
        #左侧
        staircase_left_wall=draw_rect(ax, staircase.x, staircase.y, wall_thickness, staircase.height + wall_thickness * 2, 'black', 2, "black", fill=True)
        all_walls.append(staircase_left_wall)
        #右侧
        staircase_right_wall=draw_rect(ax, staircase.x + staircase.width + wall_thickness, staircase.y, wall_thickness, staircase.height + wall_thickness * 2, 'black', 2, "black", fill=True)
        all_walls.append(staircase_right_wall)
        #下侧
        staircase_bottom_wall=draw_rect(ax, staircase.x + wall_thickness, staircase.y, staircase.width, wall_thickness, 'black', 2, "black",fill=True)
        all_walls.append(staircase_bottom_wall)
        #上侧
        staircase_top_wall=draw_rect(ax, staircase.x + wall_thickness + staircase.door_width,staircase.y + staircase.height + wall_thickness, staircase.width - staircase.door_width, wall_thickness,'black', 2, "black", fill=True)
        all_walls.append(staircase_top_wall)
        #楼梯门
        draw_rect(ax, staircase.x+wall_thickness, staircase.door_y, staircase.door_width, wall_thickness, 'brown', 2, "brown",fill=True)



    for office in offices:
        # 绘制办公室的墙壁
        #左侧
        office_left_wall = draw_rect(ax,office.x,office.y, wall_thickness, office.height+wall_thickness*2 , color='black', lw=2, ec="black", fill=True)
        all_walls.append(office_left_wall)
        #右侧
        office_right_wall = draw_rect(ax,office.x + office.width + wall_thickness, office.y, wall_thickness, office.height+wall_thickness*2, color='black', lw=2, ec="black", fill=True)
        all_walls.append(office_right_wall)
        #下侧
        office_bottom_wall = draw_rect(ax,office.x + wall_thickness, office.y, office.width, wall_thickness, color='black', lw=2, ec="black", fill=True)
        all_walls.append(office_bottom_wall)
        #上侧（左半部分）
        office_top_left_wall = draw_rect(ax,office.x + wall_thickness, office.y + office.height + wall_thickness, office.width/2 - office.door_width/2, wall_thickness, color='black', lw=2, ec="black", fill=True)
        all_walls.append(office_top_left_wall)
        #上侧（右半部分）
        office_top_right_wall = draw_rect(ax, office.x + wall_thickness+ office.width/2 + office.door_width/2, office.y+ office.height + wall_thickness, office.width / 2 - office.door_width / 2, wall_thickness, color='black', lw=2, ec="black", fill=True)
        all_walls.append(office_top_right_wall)
        #门
        draw_rect(ax,office.x+wall_thickness+office.width/2 -office.door_width/2 , office.door_y, office.door_width, wall_thickness, color='brown', lw=2, ec="brown",fill=True)

    for room in rooms_one:
        # 绘制房间的墙壁(门在右侧)
        # 左侧
        rooms_one_left_wall = draw_rect(ax, room.x, room.y, wall_thickness, room.height + wall_thickness * 2, color='black', lw=2,ec="black", fill=True)
        all_walls.append(rooms_one_left_wall)
        # 右侧
        rooms_one_right_wall = draw_rect(ax, room.x + room.width + wall_thickness, room.y, wall_thickness,room.height + wall_thickness * 2, color='black', lw=2, ec="black", fill=True)
        all_walls.append(rooms_one_right_wall)
        # 下侧
        rooms_one_bottom_wall = draw_rect(ax, room.x + wall_thickness, room.y, room.width, wall_thickness, color='black', lw=2,ec="black", fill=True)
        all_walls.append(rooms_one_bottom_wall)
        #上侧
        rooms_one_top_wall = draw_rect(ax, room.x + wall_thickness ,room.y + room.height + wall_thickness, room.width - room.door_width,wall_thickness, 'black', 2, "black", fill=True)
        all_walls.append(rooms_one_top_wall)
        # 门
        draw_rect(ax, room.x + wall_thickness + room.width - room.door_width , room.door_y,room.door_width, wall_thickness, color='brown', lw=2, ec="brown", fill=True)
        # 房间内部空间
        draw_rect(ax,room.x + wall_thickness, room.y + wall_thickness,room.width, room.height, color='lightblue', lw=1,ec='lightblue', fill=True)


    for bed in room1.beds + room2.beds  :
        ax.add_patch(plt.Rectangle((bed.x, bed.y), bed.width, bed.height, color='brown', lw=1, ec="black"))

    for room in rooms_two:
        # 绘制房间的墙壁(门在中间)
        # 左侧
        rooms_two_left_wall = draw_rect(ax, room.x, room.y, wall_thickness, room.height + wall_thickness * 2, color='black', lw=2, ec="black",fill=True)
        all_walls.append(rooms_two_left_wall)
        # 右侧
        rooms_two_right_wall = draw_rect(ax, room.x + room.width + wall_thickness, room.y, wall_thickness, room.height + wall_thickness * 2, color='black', lw=2, ec="black", fill=True)
        all_walls.append(rooms_two_right_wall)
        # 下侧
        rooms_two_bottom_wall = draw_rect(ax, room.x + wall_thickness, room.y, room.width, wall_thickness, color='black', lw=2, ec="black", fill=True)
        all_walls.append(rooms_two_bottom_wall)
        # 上侧（左半部分）
        rooms_two_top_left_wall = draw_rect(ax, room.x + wall_thickness, room.y + room.height + wall_thickness, room.width / 2 - room.door_width / 2, wall_thickness, color='black', lw=2, ec="black", fill=True)
        all_walls.append(rooms_two_top_left_wall)
        # 上侧（右半部分）
        rooms_two_top_right_wall = draw_rect(ax, room.x + wall_thickness + room.width / 2 + room.door_width / 2, room.y + room.height + wall_thickness, room.width / 2 - room.door_width / 2, wall_thickness,color='black', lw=2, ec="black", fill=True)
        all_walls.append(rooms_two_top_right_wall)
        # 门
        draw_rect(ax, room.x + wall_thickness + room.width / 2 - room.door_width / 2, room.door_y,room.door_width, wall_thickness, color='brown', lw=2, ec="brown", fill=True)
        # 房间内部空间
        draw_rect(ax, room.x + wall_thickness, room.y + wall_thickness, room.width, room.height, color='lightblue', lw=1, ec='lightblue', fill=True)


    # 绘制房间的病床
    for bed in  room3.beds :
        ax.add_patch(plt.Rectangle((bed.x, bed.y), bed.width, bed.height, color='brown', lw=1, ec="black"))


    # 绘制病人（遍历所有房间的病人列表合并后的数据）
    all_patients = []
    for room in rooms_one :
        all_patients.extend(room.patients)
    for room in rooms_two :
        all_patients.extend(room.patients)
    for patient in all_patients:
        ax.plot(patient.x, patient.y, 'ro', markersize=2)

# 动画函数
def animate(i):
    if update_patients():
        ani.event_source.stop()
    draw()


ani = animation.FuncAnimation(fig, animate, frames=200, interval=50, repeat=False)
plt.show()
