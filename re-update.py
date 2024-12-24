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

# 病人类
class Patient:
    def __init__(self, bed, bed_index, speed=0.05, avoidance_coefficient=0.5, door_offset=2, avoidance_distance=1.5, obstacles=[]):
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
        self.corridor = self.room.corridor
        self.staircase = self.room.staircase
        self.at_corridor = False
        self.at_staircase = False
        self.corridor_target_x, self.corridor_target_y = self.corridor.get_exit_coordinates()

        if self.staircase is not None:
            self.staircase_target_x, self.staircase_target_y = self.staircase.get_entry_coordinates()
        else:
            self.staircase_target_x, self.staircase_target_y = self.corridor_target_x, self.corridor_target_y  # 如果没有楼梯间，目标就是走廊出口
        self.obstacles = obstacles  # 接收包含病床和墙壁的 obstacles 列表

    def update_position(self, all_patients):  # 添加 all_patients 参数

        if not self.at_corridor:
            self.move_towards_target(self.corridor_target_x, self.corridor_target_y, self.corridor)
        elif not self.at_staircase and self.staircase is not None:
            self.move_towards_target(self.staircase_target_x, self.staircase_target_y, self.staircase)
        else:
            self.move_towards_staircase_exit()

        self.apply_avoidance_force()  # 将 all_patients 传递给 apply_avoidance_force 方法
        self.x += self.vx
        self.y += self.vy

        if not self.at_corridor and self.corridor.is_within_bounds(self.x, self.y):
            self.at_corridor = True
        elif not self.at_staircase and self.staircase is not None and self.staircase.is_within_bounds(self.x, self.y):
            self.at_staircase = True
        elif self.at_staircase and self.staircase.get_exit_coordinates()[0] <= self.x:
            self.room.patients.remove(self)

        all_patients_list = all_patients  # 获取到 all_patients 列表
        self.apply_avoidance_force()  # 传递提取出来的 all_patients 列表给 apply_avoidance_force 方法
        self.x += self.vx
        self.y += self.vy

        if not self.at_corridor and self.corridor.is_within_bounds(self.x, self.y):
            self.at_corridor = True
        elif not self.at_staircase and self.staircase is not None and self.staircase.is_within_bounds(self.x, self.y):
            self.at_staircase = True
        elif self.at_staircase and self.staircase.get_exit_coordinates()[0] <= self.x:
            self.room.patients.remove(self)

    def move_towards_target(self, target_x, target_y, target_area):
        direction_x = target_x - self.x
        direction_y = target_y - self.y
        distance_to_target = np.sqrt(direction_x ** 2 + direction_y ** 2)

        # 根据距离目标的距离调整吸引力系数，这里简单示例为距离越远，系数越大
        attraction_coefficient = 1 / (distance_to_target + 1)  # 避免距离为0时分母为0，这里加1，可根据实际调整

        if distance_to_target > 0:
            self.vx = direction_x / distance_to_target * self.speed * attraction_coefficient
            self.vy = direction_y / distance_to_target * self.speed * attraction_coefficient

        return self.vx, self.vy


    def move_towards_staircase_exit(self):
        if self.staircase is not None:
            target_x, target_y = self.staircase.get_exit_coordinates()
            direction_x = target_x - self.x
            direction_y = target_y - self.y
            distance_to_target = np.sqrt(direction_x ** 2 + direction_y ** 2)

            # 根据距离目标的距离调整吸引力系数，这里简单示例为距离越远，系数越大
            attraction_coefficient = 1 / (distance_to_target + 1)  # 避免距离为0时分母为0，这里加1，可根据实际调整

            if distance_to_target > 0:
                self.vx = direction_x / distance_to_target * self.speed * attraction_coefficient
                self.vy = direction_y / distance_to_target * self.speed * attraction_coefficient

        return self.vx, self.vy

    def apply_avoidance_force(self):
        # 考虑行人之间的相互作用力（社会力模型中行人之间的相互影响）
        def apply_avoidance_force(self, all_patients):  # 保持只接收一个额外参数的定义
            for other_patient in [p for p in all_patients if p!= self]:
                distance_to_other = np.sqrt((self.x - other_patient.x) ** 2 + (self.y - other_patient.y) ** 2)
                if distance_to_other < some_interaction_distance:  # 自定义的相互作用距离阈值
                    interaction_force_x = self.x - other_patient.x
                    interaction_force_y = self.y - other_patient.y
                    interaction_distance = np.sqrt(interaction_force_x ** 2 + interaction_force_y ** 2)

                if interaction_distance > 0:
                    self.vx += (interaction_force_x / interaction_distance) * some_interaction_coefficient * self.speed
                    self.vy += (interaction_force_y / interaction_distance) * some_interaction_coefficient * self.speed

        # 考虑避让障碍物（病床、墙壁等）的力
        for obstacle in self.obstacles:
            if isinstance(obstacle, Bed):
                center_x = obstacle.x + obstacle.width / 2
                center_y = obstacle.y + obstacle.height / 2
            elif isinstance(obstacle, Staircase):
                center_x = obstacle.door_x + obstacle.door_width / 2
                center_y = obstacle.door_y
            elif isinstance(obstacle, plt.Rectangle):  # 假设墙壁对象是 matplotlib 的矩形对象，根据实际调整类型判断
                center_x = obstacle.get_x() + obstacle.get_width() / 2
                center_y = obstacle.get_y() + obstacle.get_height() / 2

            distance_to_obstacle = np.sqrt((self.x - center_x) ** 2 + (self.y - center_y) ** 2)

            if distance_to_obstacle < self.avoidance_distance:
                avoid_x = self.x - center_x
                avoid_y = self.y - center_y
                avoidance_distance = np.sqrt(avoid_x ** 2 + avoid_y ** 2)

                if avoidance_distance > 0:
                    self.vx += (avoid_x / avoidance_distance) * self.avoidance_coefficient * self.speed
                    self.vy += (avoid_y / avoidance_distance) * self.avoidance_coefficient * self.speed


class Staircase:
    def __init__(self, x, y, width, height, door_x, door_y, door_width):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width
        self.corridor_height = 2.25  # 新增走廊高度属性
        self.corridor_y = self.y + self.height

    def get_entry_coordinates(self):
        # 获取楼梯间的入口坐标，即走廊的起点
        return self.x, self.corridor_y

    def get_exit_coordinates(self):
        # 获取楼梯间的出口坐标，即走廊的末端
        return self.x + self.width, self.corridor_y

    def is_within_bounds(self, x, y):
        # 检查点是否在楼梯间内
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)


class Office:
    def __init__(self, x, y, width, height, door_x, door_y, door_width):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width
        self.corridor_height = 2.25  # 新增走廊高度属性
        self.corridor_y = self.y + self.height

class Corridor:
    def __init__(self, x, y, width, height):
        self.x = x  # 走廊的起始x坐标
        self.y = y  # 走廊的起始y坐标
        self.width = width  # 走廊的宽度
        self.height = height  # 走廊的高度

    def is_within_bounds(self, x, y):
        # 检查点是否在走廊内
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def get_exit_coordinates(self):
        # 获取走廊出口的坐标，即走廊的末端
        return self.x + self.width, self.y + self.height


# 房间类
class Room:
    def __init__(self, x, y, width, height, door_x, door_y, door_width, beds, corridor, staircase=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width
        self.beds = beds
        self.patients = []
        self.corridor = corridor  # 关联走廊对象
        self.staircase = staircase  # 关联楼梯对象

        # 在初始化时，为每个病床设置所属的房间
        for bed in self.beds:
            bed.bedroom = self  # 每个病床都知道自己所在的房间

    def initialize_patients(self, all_walls):  # 修改方法定义，添加 all_walls 参数
        obstacles = []
        obstacles.extend(self.beds)
        obstacles.extend(all_walls)

        for index, bed in enumerate(self.beds):  # 获取病床索引
            if not bed.has_patient:
                patient = Patient(bed, index, obstacles=obstacles)  # 将包含病床和墙壁的 obstacles 列表传递给 Patient 类构造函数
                self.patients.append(patient)
                bed.has_patient = True


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
corridor1=Corridor(0.37,6.24,16.315,2.25)
all_walls = []
# 初始化房间和病床时，确保病床正确关联到房间
room1 = Room(3.38, 0, 2.88, 5.5, 5.965, 5.87, 1.2,
             [Bed(3.75, 0.705, 2, 1), Bed(3.75, 2.328, 2, 1), Bed(3.75, 4.003, 2, 1)],staircase1)
room1.initialize_patients(all_walls)

room2 = Room(6.565, 0, 2.88, 5.5, 9.215, 5.87, 1.2,
             [Bed(6.935, 0.705, 2, 1), Bed(6.935, 2.328, 2, 1), Bed(6.935,4.003, 2, 1)],staircase1)
room2.initialize_patients(all_walls)

room3 = Room(9.815, 0, 6.13, 5.5, 13.25, 5.87, 1.2,
             [Bed(10.185, 0.705, 2, 1), Bed(10.185, 2.328, 2, 1), Bed(10.185,4.003, 2, 1), Bed(14.315, 0.705, 2, 1), Bed(14.315, 2.328, 2, 1), Bed(14.315,4.003, 2, 1)],staircase1)
room3.initialize_patients(all_walls)

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
    wall_thickness = 0.37
    #绘制走廊
    corridor = plt.Rectangle((staircase1.x + wall_thickness, staircase1.y+wall_thickness*2+staircase1.height), staircase1.width+room1.width+room2.width+room3.width+office1.width+wall_thickness*5, 2.25, color='gray', lw=2, ec="black")  # 走廊颜色设为灰色示例
    ax.add_patch(corridor)

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
