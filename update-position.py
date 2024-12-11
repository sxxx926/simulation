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

    def find_closest_staircase(self):
        # 找到最近的楼梯
        accessible_staircases = []
        for staircase in staircases:
            is_accessible = True
            accessible_staircases.append(staircase)

        if accessible_staircases:
            return min(accessible_staircases, key=lambda s: self.distance_to_staircase(s))
        else:
            return None

    def distance_to_staircase(self, staircase):
        return np.sqrt((self.x - staircase.door_x) ** 2 + (self.y - staircase.door_y) ** 2)

    def social_force(self, obstacles, k_repulsion=10, k_attraction=1):
        """ 计算社会力，避免病人与障碍物发生碰撞，同时吸引病人朝目标移动 """
        force_x, force_y = 0, 0

        # 排斥力：避开墙壁和病床
        for obj in obstacles:
            obj_x, obj_y = obj.x, obj.y
            obj_width, obj_height = obj.width, obj.height
            # 计算与障碍物的距离
            dx = self.x - obj_x
            dy = self.y - obj_y
            dist = np.sqrt(dx ** 2 + dy ** 2)

            # 如果距离小于一定阈值，计算排斥力
            if dist < 1.5:  # 当距离小于1.5时产生排斥力
                repulsion_force = k_repulsion * (1 / dist - 1 / 1.5) / dist
                force_x += repulsion_force * dx / dist
                force_y += repulsion_force * dy / dist

        # 吸引力：朝着目标位置（楼梯门口）移动
        closest_staircase = self.find_closest_staircase()
        if closest_staircase:
            target_dx = closest_staircase.door_x - self.x
            target_dy = closest_staircase.door_y - self.y
            target_dist = np.sqrt(target_dx ** 2 + target_dy ** 2)

            if target_dist > 0:
                attraction_force = k_attraction * target_dist
                force_x += attraction_force * target_dx / target_dist
                force_y += attraction_force * target_dy / target_dist
            print(f"Attraction force: ({force_x}, {force_y})")
        else:
            print("No staircase found.")

        print(f"Repulsion force: ({force_x}, {force_y})")  # 打印排斥力
        return force_x, force_y

    def update_position(self):
        room = self.bed.bedroom
        if room is not None:
            # 计算病人朝房间门的方向
            direction_x = room.door_x - self.x
            direction_y = room.door_y - self.y+1
            distance_to_door = np.sqrt(direction_x ** 2 + direction_y ** 2)

            if distance_to_door > 0:
                # 正常移动方向
                self.vx = direction_x / distance_to_door * self.speed
                self.vy = direction_y / distance_to_door * self.speed

            # 避开病床
            for bed in room.beds:
                # 计算病人和病床的距离
                bed_center_x = bed.x + bed.width / 2
                bed_center_y = bed.y + bed.height / 2
                distance_to_bed = np.sqrt((self.x - bed_center_x) ** 2 + (self.y - bed_center_y) ** 2)

                # 如果病人距离病床太近，则进行避让
                if distance_to_bed < 1.25:
                    avoid_x = self.x - bed_center_x
                    avoid_y = self.y - bed_center_y
                    avoidance_distance = np.sqrt(avoid_x ** 2 + avoid_y ** 2)

                    if avoidance_distance > 0:
                        # 计算避开病床的方向
                        self.vx += (avoid_x / avoidance_distance) * self.speed
                        self.vy += (avoid_y / avoidance_distance) * self.speed

            # 更新病人位置
            self.x += self.vx
            self.y += self.vy


def update_patients():
    all_patients = room1.patients + room2.patients + room3.patients
    all_evacuated = True
    for patient in all_patients:
        if patient in room1.patients or patient in room2.patients or patient in room3.patients :
                all_evacuated = False
                patient.update_position()
    return all_evacuated


class Staircase:
    def __init__(self, x, y, width, height,door_x, door_y, door_width):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.door_x = door_x
        self.door_y = door_y
        self.door_width = door_width
        self.corridor_height = 2.25  # 新增走廊高度属性
        self.corridor_y = self.y + self.height



class Office:
    def __init__(self, x, y, width, height,door_x, door_y, door_width):
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

    def initialize_patients(self):
        for index, bed in enumerate(self.beds):  # 获取病床索引
            if not bed.has_patient:
                patient = Patient(bed, index)  # 传递病床索引创建病人实例
                self.patients.append(patient)
                bed.has_patient = True


staircase1 = Staircase(0, 0, 3.01, 5.5,0.6,5.87,1.2)
staircases=[staircase1]
office1 = Office(16.315, 0, 6.13, 5.5, 19.75, 5.87, 1.2)
offices=[office1]
corridor1=Corridor(0.37,6.24,16.315,2.25)

# 初始化房间和病床时，确保病床正确关联到房间
room1 = Room(3.38, 0, 2.88, 5.5, 5.965, 5.87, 1.2,
             [Bed(3.75, 0.705, 2, 1), Bed(3.75, 2.328, 2, 1), Bed(3.75, 4.003, 2, 1)],staircase1)
room1.initialize_patients()

room2 = Room(6.565, 0, 2.88, 5.5, 9.215, 5.87, 1.2,
             [Bed(6.935, 0.705, 2, 1), Bed(6.935, 2.328, 2, 1), Bed(6.935,4.003, 2, 1)],staircase1)
room2.initialize_patients()

room3 = Room(9.815, 0, 6.13, 5.5, 13.25, 5.87, 1.2,
             [Bed(10.185, 0.705, 2, 1), Bed(10.185, 2.328, 2, 1), Bed(10.185,4.003, 2, 1), Bed(14.315, 0.705, 2, 1), Bed(14.315, 2.328, 2, 1), Bed(14.315,4.003, 2, 1)],staircase1)
room3.initialize_patients()

rooms_one = [room1, room2]
rooms_two=[room3]


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
        draw_rect(ax, staircase.x, staircase.y, wall_thickness, staircase.height + wall_thickness * 2, 'black', 2, "black", fill=True)
        #右侧
        draw_rect(ax, staircase.x + staircase.width + wall_thickness, staircase.y, wall_thickness, staircase.height + wall_thickness * 2, 'black', 2, "black", fill=True)
        #下侧
        draw_rect(ax, staircase.x + wall_thickness, staircase.y, staircase.width, wall_thickness, 'black', 2, "black",fill=True)
        #上侧
        draw_rect(ax, staircase.x + wall_thickness + staircase.door_width,staircase.y + staircase.height + wall_thickness, staircase.width - staircase.door_width, wall_thickness,'black', 2, "black", fill=True)
        #楼梯门
        draw_rect(ax, staircase.x+wall_thickness, staircase.door_y, staircase.door_width, wall_thickness, 'brown', 2, "brown",fill=True)



    for office in offices:
        # 绘制办公室的墙壁
        #左侧
        draw_rect(ax,office.x,office.y, wall_thickness, office.height+wall_thickness*2 , color='black', lw=2, ec="black", fill=True)
        #右侧
        draw_rect(ax,office.x + office.width + wall_thickness, office.y, wall_thickness, office.height+wall_thickness*2, color='black', lw=2, ec="black", fill=True)
        #下侧
        draw_rect(ax,office.x + wall_thickness, office.y, office.width, wall_thickness, color='black', lw=2, ec="black", fill=True)
        #上侧（左半部分）
        draw_rect(ax,office.x + wall_thickness, office.y + office.height + wall_thickness, office.width/2 - office.door_width/2, wall_thickness, color='black', lw=2, ec="black", fill=True)
        #上侧（右半部分）
        draw_rect(ax, office.x + wall_thickness+ office.width/2 + office.door_width/2, office.y+ office.height + wall_thickness, office.width / 2 - office.door_width / 2, wall_thickness, color='black', lw=2, ec="black", fill=True)
        #门
        draw_rect(ax,office.x+wall_thickness+office.width/2 -office.door_width/2 , office.door_y, office.door_width, wall_thickness, color='brown', lw=2, ec="brown",fill=True)

    for room in rooms_one:
        # 绘制房间的墙壁(门在右侧)
        # 左侧
        draw_rect(ax, room.x, room.y, wall_thickness, room.height + wall_thickness * 2, color='black', lw=2,ec="black", fill=True)
        # 右侧
        draw_rect(ax, room.x + room.width + wall_thickness, room.y, wall_thickness,room.height + wall_thickness * 2, color='black', lw=2, ec="black", fill=True)
        # 下侧
        draw_rect(ax, room.x + wall_thickness, room.y, room.width, wall_thickness, color='black', lw=2,ec="black", fill=True)
        #上侧
        draw_rect(ax, room.x + wall_thickness ,room.y + room.height + wall_thickness, room.width - room.door_width,wall_thickness, 'black', 2, "black", fill=True)
        # 门
        draw_rect(ax, room.x + wall_thickness + room.width - room.door_width , room.door_y,room.door_width, wall_thickness, color='brown', lw=2, ec="brown", fill=True)
        # 房间内部空间
        draw_rect(ax,room.x + wall_thickness, room.y + wall_thickness,room.width, room.height, color='lightblue', lw=1,ec='lightblue', fill=True)


    for bed in room1.beds + room2.beds  :
        ax.add_patch(plt.Rectangle((bed.x, bed.y), bed.width, bed.height, color='brown', lw=1, ec="black"))

    for room in rooms_two:
        # 绘制房间的墙壁(门在中间)
        # 左侧
        draw_rect(ax, room.x, room.y, wall_thickness, room.height + wall_thickness * 2, color='black', lw=2, ec="black",fill=True)
        # 右侧
        draw_rect(ax, room.x + room.width + wall_thickness, room.y, wall_thickness, room.height + wall_thickness * 2, color='black', lw=2, ec="black", fill=True)
        # 下侧
        draw_rect(ax, room.x + wall_thickness, room.y, room.width, wall_thickness, color='black', lw=2, ec="black", fill=True)
        # 上侧（左半部分）
        draw_rect(ax, room.x + wall_thickness, room.y + room.height + wall_thickness, room.width / 2 - room.door_width / 2, wall_thickness, color='black', lw=2, ec="black", fill=True)
        # 上侧（右半部分）
        draw_rect(ax, room.x + wall_thickness + room.width / 2 + room.door_width / 2, room.y + room.height + wall_thickness, room.width / 2 - room.door_width / 2, wall_thickness,color='black', lw=2, ec="black", fill=True)
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
