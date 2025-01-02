import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Ellipse

# 读取 Excel 文件
def read_excel(file_path):
    excel_file = pd.ExcelFile(file_path)
    data = {
       'staircase': excel_file.parse('staircase'),
        'room': excel_file.parse('room'),
        'bed': excel_file.parse('bed'),
        'office': excel_file.parse('office')
    }
    return data

# 绘制单个病床及其对应的病人形状，并实现向门口移动
def draw_bed_with_patient(bed_row, ax, room_data, office_data):
    x = bed_row['x']
    y = bed_row['y']
    width = bed_row['width']
    height = bed_row['height']
    patient_state = bed_row['patient_state']

    # 绘制病床（矩形）
    bed_patch = Rectangle((x, y), width, height, edgecolor='black', facecolor='pink', linewidth=0.5)
    ax.add_patch(bed_patch)

    # 确定门的位置信息（这里假设每个病床所在房间或办公室只有一个门）
    room_id = None
    office_id = None
    for index, room_row in room_data.iterrows():
        if x >= room_row['x'] and x <= room_row['x'] + room_row['width'] and y >= room_row['y'] and y <= room_row['y'] + room_row['height']:
            room_id = room_row['ID']
            door_x = room_row['door_x']
            door_y = room_row['door_y']
            break
    for index, office_row in office_data.iterrows():
        if x >= office_row['x'] and x <= office_row['x'] + office_row['width'] and y >= office_row['y'] and y <= office_row['y'] + office_row['height']:
            office_id = office_row['ID']
            door_x = office_row['door_x']
            door_y = office_row['door_y']
            break

    # 根据病人状态绘制不同形状
    if patient_state == 'SAP':
        patient_x = x + width / 2
        patient_y = y + height / 2
        patient_patch = Circle((patient_x, patient_y), edgecolor='red', radius=0.1, facecolor='red')
    elif patient_state == 'SEP':
        patient_x = x + width / 2
        patient_y = y + height / 2
        patient_patch = Circle((patient_x, patient_y), edgecolor='blue', radius=0.1, facecolor='blue')
    elif patient_state == 'CP':
        patient_x = x + width / 2
        patient_y = y + height / 2
        patient_patch = Ellipse((patient_x, patient_y), width=0.4, height=0.2, edgecolor='green', facecolor='green')
    else:
        patient_state == 'BP'
        patient_x = x + 0.2
        patient_y = y + 0.1
        patient_patch = Rectangle((patient_x, patient_y), width=1.5, height=0.7, edgecolor='purple', facecolor='purple')

    # 计算移动方向和距离（简单示例，这里假设每次移动固定距离 0.1 向门靠近）
    move_distance = 0.1
    if room_id is not None or office_id is not None:
        if patient_x < door_x:
            patient_x += move_distance
        elif patient_x > door_x:
            patient_x -= move_distance
        if patient_y < door_y:
            patient_y += move_distance
        elif patient_y > door_y:
            patient_y -= move_distance

    patient_patch.center = (patient_x, patient_y)
    ax.add_patch(patient_patch)


# 绘制建筑平面图
def plot_building_plan(data):
    # 设置图片清晰度
    plt.rcParams['figure.dpi'] = 300
    # 创建画布
    plt.figure(figsize=(10, 8))
    ax = plt.gca()

    # 绘制楼梯间
    for index, row in data['staircase'].iterrows():
        x = row['x']
        y = row['y']
        width = row['width']
        height = row['height']
        door_x = row['door_x']
        door_y = row['door_y']
        door_width = row['door_width']
        # 考虑墙壁厚度，这里假设墙壁在内部和外部都有厚度
        wall_thickness = 0.37
        inner_x = x + wall_thickness
        inner_y = y + wall_thickness
        inner_width = width
        inner_height = height
        # 绘制外部矩形
        ax.add_patch(Rectangle((x, y), inner_width + wall_thickness * 2, height + wall_thickness * 2, edgecolor='black',
                               facecolor='black'))
        # 绘制内部矩形
        ax.add_patch(Rectangle((inner_x, inner_y), inner_width, inner_height, edgecolor='none', facecolor='lightgreen'))
        # 绘制门
        ax.add_patch(Rectangle((door_x, door_y), door_width, wall_thickness, edgecolor='red', facecolor='red',
                               linewidth=0.2))

    # 绘制房间
    for index, row in data['room'].iterrows():
        x = row['x']
        y = row['y']
        width = row['width']
        height = row['height']
        door_x = row['door_x']
        door_y = row['door_y']
        door_width = row['door_width']
        # 考虑墙壁厚度
        wall_thickness = 0.37
        inner_x = x + wall_thickness
        inner_y = y + wall_thickness
        inner_width = width
        inner_height = height
        # 绘制外部矩形
        ax.add_patch(Rectangle((x, y), inner_width + wall_thickness * 2, inner_height + wall_thickness * 2,
                               edgecolor='black', facecolor='black'))
        # 绘制内部矩形
        ax.add_patch(Rectangle((inner_x, inner_y), inner_width, inner_height, edgecolor='none', facecolor='lightblue'))
        # 绘制门
        ax.add_patch(Rectangle((door_x, door_y), door_width, wall_thickness, edgecolor='red', facecolor='red',
                               linewidth=0.2))

    # 绘制办公室
    for index, row in data['office'].iterrows():
        x = row['x']
        y = row['y']
        width = row['width']
        height = row['height']
        door_x = row['door_x']
        door_y = row['door_y']
        door_width = row['door_width']
        # 考虑墙壁厚度
        wall_thickness = 0.37
        inner_x = x + wall_thickness
        inner_y = y + wall_thickness
        inner_width = width
        inner_height = height
        # 绘制外部矩形
        ax.add_patch(Rectangle((x, y), inner_width + wall_thickness * 2, inner_height + wall_thickness * 2,
                               edgecolor='black', facecolor='black'))
        # 绘制内部矩形
        ax.add_patch(Rectangle((inner_x, inner_y), inner_width, inner_height, edgecolor='none', facecolor='grey'))
        # 绘制门
        ax.add_patch(Rectangle((door_x, door_y), door_width, wall_thickness, edgecolor='red', facecolor='red',
                               linewidth=0.2))

    # 绘制病床及病人形状，并传递房间和办公室数据
    for index, row in data['bed'].iterrows():
        draw_bed_with_patient(row, ax, data['room'], data['office'])

    # 设置坐标轴范围和标签
    plt.gcf().set_size_inches(10, 8)  # 设置图形的大小为宽度 10 英寸，高度 8 英寸
    plt.axis('equal')
    plt.xlim(0, 145)
    plt.ylim(0, 15)
    plt.xlabel('x 坐标')
    plt.xticks(rotation=45)
    plt.ylabel('y 坐标')
    plt.title('建筑平面图')

    # 显示图形
    plt.show()


if __name__ == "__main__":
    file_path = 'D:\研究生\医院疏散\date.xlsx'
    data = read_excel(file_path)
    plot_building_plan(data)