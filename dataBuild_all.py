# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import math
from enum import Enum
from datetime import datetime


# 确保模块正确导入
print(f"已导入模块: math={math}, np={np}, pd={pd}")

# 定义枚举类型
class Proxy(Enum):
    X = 'x'
    Y = 'y'
    Z = 'z'

#############def.begin################

def diff_sign(a, b):
    return (a >= 0) != (b >= 0)

# 对数函数曲线，前期斜率大，中后期斜率小
def ModuleA(moving_time=0, log_base=4, epsilon=1e-6, proxy=None):
    """
    计算沉降预测的理论累计位移，使用对数函数曲线，前期斜率大，中后期斜率小。

    参数:
        moving_time(float): 开始沉降时间，默认为0，范围0-total_days。
        log_base (float): 对数函数的底数，控制曲线形状。值越大，前期增长越快，中后期增长越慢。
                          默认值为4，推荐范围为2-10。
        epsilon (float): 避免对数函数在t=0时无定义的小偏移量。
                         默认值为1e-6，通常不需要调整。
        proxy (Proxy): 枚举类型，可选值为 Proxy.X, Proxy.Y, Proxy.Z 或 None。
                       若为None，计算并更新所有坐标的全局变量；
                       若为具体坐标，仅计算并返回该坐标的位移，同时更新对应全局变量。

    返回:
        float: 当proxy为具体坐标时返回对应位移值；当proxy为None时返回None。
    """
    global base_x, base_y, base_z
    
    # 确保参数有效
    if log_base <= 1:
        raise ValueError("log_base必须大于1")
    if epsilon <= 0 or epsilon >= 0.1:
        raise ValueError("epsilon必须在0到0.1之间")

    relative_time = days_since_start
    
    if relative_time <= moving_time:
        value = 0
    elif relative_time >= total_days:
        value = x_total if proxy in (Proxy.X, None) else \
                y_total if proxy in (Proxy.Y, None) else \
                z_total
    else:
        adjusted_time = epsilon + relative_time
        max_log = math.log(total_days + epsilon, log_base)
        current_log = math.log(adjusted_time + 1, log_base)
        log_factor = current_log / max_log
        
        value = x_total * log_factor if proxy in (Proxy.X, None) else \
                y_total * log_factor if proxy in (Proxy.Y, None) else \
                z_total * log_factor
    
    # 更新全局变量
    if proxy is None:
        base_x = value
        base_y = value
        base_z = value
        return None
    elif proxy == Proxy.X:
        base_x = value
        return value
    elif proxy == Proxy.Y:
        base_y = value
        return value
    elif proxy == Proxy.Z:
        base_z = value
        return value

# 修正的一次函数曲线，添加两个折点
def ModuleB(ratio1, ratio2, time_split1, time_split2, offset, proxy=None):
    """
    修正的一次函数曲线，添加两个折点，计算沉降预测的理论累计位移。

    参数:
        ratio1 (float): 第一段的比例，范围 0 到 1。
        ratio2 (float): 第二段的比例，范围 0 到 1，且 ratio1 + ratio2 <= 1。
        time_split1 (float): 第一个时间分割点，范围 0 到 1。
        time_split2 (float): 第二个时间分割点，范围 0 到 1，且 time_split1 < time_split2。
        offset (float): 随机偏移的范围，范围 0 到 0.3。
        proxy (Proxy): 枚举类型，可选值为 Proxy.X, Proxy.Y, Proxy.Z 或 None。
                       若为None，计算并更新所有坐标的全局变量；
                       若为具体坐标，仅计算并返回该坐标的位移，同时更新对应全局变量。

    返回:
        float: 当proxy为具体坐标时返回对应位移值；当proxy为None时返回None。
    """
    global base_x, base_y, base_z
    
    # 确保输入参数有效
    if not (0 <= ratio1 <= 1 and 0 <= ratio2 <= 1 and (ratio1 + ratio2) <= 1):
        raise ValueError("比例参数必须满足: 0 <= ratio1 <= 1, 0 <= ratio2 <= 1, ratio1 + ratio2 <= 1")
    if not (0 < time_split1 < time_split2 < 1):
        raise ValueError("时间分割点必须满足: 0 < time_split1 < time_split2 < 1")
    if offset < 0 or offset > 0.3:
        raise ValueError("offset参数必须在0到0.3之间")

    # 添加随机偏移
    random_ratio1 = ratio1 * (1 + np.random.uniform(-offset, offset))
    random_ratio2 = ratio2 * (1 + np.random.uniform(-offset, offset))

    # 确保随机调整后的比例仍有效
    total_ratio = random_ratio1 + random_ratio2
    if total_ratio > 1:
        scale = 1 / total_ratio
        random_ratio1 *= scale
        random_ratio2 *= scale

    # 自动计算第三段比例
    ratio3 = 1 - random_ratio1 - random_ratio2

    # 计算各段终点的理论值
    if proxy in (Proxy.X, None):
        break1_x = x_total * random_ratio1
        break2_x = x_total * (random_ratio1 + random_ratio2)
    if proxy in (Proxy.Y, None):
        break1_y = y_total * random_ratio1
        break2_y = y_total * (random_ratio1 + random_ratio2)
    if proxy in (Proxy.Z, None):
        break1_z = z_total * random_ratio1
        break2_z = z_total * (random_ratio1 + random_ratio2)

    # 计算各段的时间范围
    t1_end = time_split1 * total_days
    t2_end = time_split2 * total_days

    if days_since_start <= t1_end:
        # 第一段：0到t1_end
        value_x = break1_x * (days_since_start / t1_end) if proxy in (Proxy.X, None) else None
        value_y = break1_y * (days_since_start / t1_end) if proxy in (Proxy.Y, None) else None
        value_z = break1_z * (days_since_start / t1_end) if proxy in (Proxy.Z, None) else None
    elif days_since_start <= t2_end:
        # 第二段：t1_end到t2_end
        elapsed = days_since_start - t1_end
        duration = t2_end - t1_end
        value_x = break1_x + (break2_x - break1_x) * (elapsed / duration) if proxy in (Proxy.X, None) else None
        value_y = break1_y + (break2_y - break1_y) * (elapsed / duration) if proxy in (Proxy.Y, None) else None
        value_z = break1_z + (break2_z - break1_z) * (elapsed / duration) if proxy in (Proxy.Z, None) else None
    else:
        # 第三段：t2_end到结束
        elapsed = days_since_start - t2_end
        duration = total_days - t2_end
        value_x = break2_x + (x_total - break2_x) * (elapsed / duration) if proxy in (Proxy.X, None) else None
        value_y = break2_y + (y_total - break2_y) * (elapsed / duration) if proxy in (Proxy.Y, None) else None
        value_z = break2_z + (z_total - break2_z) * (elapsed / duration) if proxy in (Proxy.Z, None) else None

    # 更新全局变量并返回结果
    if proxy is None:
        base_x = value_x
        base_y = value_y
        base_z = value_z
        return None
    elif proxy == Proxy.X:
        base_x = value_x
        return value_x
    elif proxy == Proxy.Y:
        base_y = value_y
        return value_y
    elif proxy == Proxy.Z:
        base_z = value_z
        return value_z

# 修正的二次函数曲线，添加X轴初始偏移
def ModuleC(ratio_shift = 2000,proxy=None):
    """
    修正的二次函数曲线，添加X轴初始偏移，计算沉降预测的理论累计位移。

    参数:
        ratio_shift: 斜率调整，推荐范围：（-4000,4000）
        proxy (Proxy): 枚举类型，可选值为 Proxy.X, Proxy.Y, Proxy.Z 或 None。
                       若为None，计算并更新所有坐标的全局变量；
                       若为具体坐标，仅计算并返回该坐标的位移，同时更新对应全局变量。

    返回:
        float: 当proxy为具体坐标时返回对应位移值；当proxy为None时返回None。
    """
    global base_x, base_y, base_z
    
    if proxy in (Proxy.X, None):
        ratio_x = x_total / (math.pow(total_days, 2) - ratio_shift)
        displacement_x = - ratio_x * math.pow(days_since_start - total_days, 2) + x_total
        if diff_sign(displacement_x, x_total):
            displacement_x = np.sign(x_total) * 0.03  # 保持符号一致的小数值
    if proxy in (Proxy.Y, None):
        ratio_y = y_total / (math.pow(total_days, 2) - ratio_shift)
        displacement_y = - ratio_y * math.pow(days_since_start - total_days, 2) + y_total
        if diff_sign(displacement_y, y_total):
            displacement_y = np.sign(y_total) * 0.04  # 保持符号一致的小数值
    if proxy in (Proxy.Z, None):
        ratio_z = z_total / (math.pow(total_days, 2) - ratio_shift)
        displacement_z = - ratio_z * math.pow(days_since_start - total_days, 2) + z_total
        if diff_sign(displacement_z, z_total):
            displacement_z = np.sign(z_total) * 0.05  # 保持符号一致的小数值

    # 更新全局变量并返回结果
    if proxy is None:
        base_x = displacement_x
        base_y = displacement_y
        base_z = displacement_z
        return None
    elif proxy == Proxy.X:
        base_x = displacement_x
        return displacement_x
    elif proxy == Proxy.Y:
        base_y = displacement_y
        return displacement_y
    elif proxy == Proxy.Z:
        base_z = displacement_z
        return displacement_z

# 二次函数曲线
def ModuleD(proxy=None):
    """
    二次函数曲线，计算沉降预测的理论累计位移。

    参数:
        proxy (Proxy): 枚举类型，可选值为 Proxy.X, Proxy.Y, Proxy.Z 或 None。
                       若为None，计算并更新所有坐标的全局变量；
                       若为具体坐标，仅计算并返回该坐标的位移，同时更新对应全局变量。

    返回:
        float: 当proxy为具体坐标时返回对应位移值；当proxy为None时返回None。
    """
    global base_x, base_y, base_z
    
    if proxy in (Proxy.X, None):
        ratio_x = x_total / math.pow(total_days, 2)
        displacement_x = - ratio_x * math.pow(days_since_start - total_days, 2) + x_total
    if proxy in (Proxy.Y, None):
        ratio_y = y_total / math.pow(total_days, 2)
        displacement_y = - ratio_y * math.pow(days_since_start - total_days, 2) + y_total
    if proxy in (Proxy.Z, None):
        ratio_z = z_total / math.pow(total_days, 2)
        displacement_z = - ratio_z * math.pow(days_since_start - total_days, 2) + z_total

    # 更新全局变量并返回结果
    if proxy is None:
        base_x = displacement_x
        base_y = displacement_y
        base_z = displacement_z
        return None
    elif proxy == Proxy.X:
        base_x = displacement_x
        return displacement_x
    elif proxy == Proxy.Y:
        base_y = displacement_y
        return displacement_y
    elif proxy == Proxy.Z:
        base_z = displacement_z
        return displacement_z

#############def.end#################

# 读取数据
excel_file = pd.ExcelFile('./data/花垣沉降原始数据_汇总_0512.xlsx')
sheet1 = excel_file.parse('Sheet1')
sheet2 = excel_file.parse('Sheet2')

# 处理Sheet1数据，分离起始和结束数据
start_date = datetime(2024, 10, 14)
end_date = datetime(2025, 5, 13)
total_days = (end_date - start_date).days
building_time = 98 / total_days  #施工期98天占比
build_after = ( total_days - building_time ) / total_days  #监测期占比
# 提取起始数据
start_data = sheet1[sheet1['日期'] == start_date].copy()
start_data['点名'] = start_data['点名'].str.strip()
# 单位转换：米转毫米
start_data[['X', 'Y', 'Z']] *= 1000

# 提取结束数据
end_data = sheet1[sheet1['日期'] == end_date].copy()
end_data['点名'] = end_data['点名'].str.strip()
# 单位转换：米转毫米
end_data[['X', 'Y', 'Z']] *= 1000

# 合并起始和结束数据
combined_data = pd.merge(start_data, end_data, on='点名', suffixes=('_start', '_end'))

# 计算各方向总位移
combined_data['X_total'] = combined_data['X_start'] - combined_data['X_end']
combined_data['Y_total'] = combined_data['Y_start'] - combined_data['Y_end']
combined_data['Z_total'] = combined_data['Z_start'] - combined_data['Z_end']

# 处理Sheet2时间点并排序
sheet2['项目时间'] = pd.to_datetime(sheet2['项目时间'])
sheet2 = sheet2.sort_values('项目时间').reset_index(drop=True)

# 生成所有监测点列表
points = combined_data['点名'].tolist()

# 初始化结果列表
result = []

for point in points:
    # 获取该监测点的总位移
    point_data = combined_data[combined_data['点名'] == point].iloc[0]
    x_total = point_data['X_total']
    y_total = point_data['Y_total']
    z_total = point_data['Z_total']

    # 生成每个时间点的预测数据
    prev_x = point_data['X_start']
    prev_y = point_data['Y_start']
    prev_z = point_data['Z_start']
    prev_date = start_date.date()
    prev_cumulative_x = 0
    prev_cumulative_y = 0
    prev_cumulative_z = 0

    for idx, date in enumerate(sheet2['项目时间']):
        current_date = date.date()
        days_since_start = (current_date - start_date.date()).days

        # 计算理论累计位移
        if days_since_start == 0:
            # 起始点
            cumulative_x = 0
            cumulative_y = 0
            cumulative_z = 0
        elif days_since_start >= total_days:
            # 结束点
            cumulative_x = x_total
            cumulative_y = y_total
            cumulative_z = z_total
        else:
            # 中间点，添加随机噪声

            point_shift = int(point[2:]) #利用点名序号做参数偏移调整

            # 新增：根据点名选择Module
            if point.startswith('JC') and int(point[2:]) <= 3:
                # JC01-JC03使用ModuleB
                ModuleB(0.01 * (71 + point_shift),0.01 * (20 - point_shift),1/3*building_time,building_time,0.03,proxy=Proxy.X)
                ModuleB(0.01 * (71 + point_shift),0.01 * (20 - point_shift),1/3*building_time,building_time,0.03,proxy=Proxy.Y)
                ModuleB(0.01 * (71 + point_shift),0.01 * (20 - point_shift),1/3*building_time,building_time,0.03,proxy=Proxy.Z)
            elif point.startswith('JC') and int(point[2:]) <= 5:
                # JC04-JC05使用ModuleC
                ModuleC(ratio_shift = 100 * (20 + point_shift),proxy=Proxy.X)
                ModuleC(ratio_shift = 100 * (20 + point_shift),proxy=Proxy.Y)
                ModuleC(ratio_shift = 100 * (20 + point_shift),proxy=Proxy.Z)
            elif point.startswith('JC') and int(point[2:]) <= 7:
                # JC06-JC07使用调参ModuleA
                ModuleB(0.01 * (6 + point_shift),0.01 * (82 - point_shift),1/4*building_time,building_time,0.03,proxy=Proxy.X)
                ModuleB(0.01 * (6 + point_shift),0.01 * (82 - point_shift),1/4*building_time,building_time,0.03,proxy=Proxy.Y)
                ModuleB(0.01 * (6 + point_shift),0.01 * (82 - point_shift),1/4*building_time,building_time,0.03,proxy=Proxy.Z)
            else:
                # JC08-JC12使用ModuleA
                ModuleB(0.01 * (6 + point_shift),0.01 * (82 - point_shift),1/4*building_time,building_time,0.03,proxy=Proxy.X)
                ModuleB(0.01 * (6 + point_shift),0.01 * (82 - point_shift),1/4*building_time,building_time,0.03,proxy=Proxy.Y)
                ModuleB(0.01 * (6 + point_shift),0.01 * (82 - point_shift),1/4*building_time,building_time,0.03,proxy=Proxy.Z)

            # 添加噪声（正态分布，标准差为总位移的0.5%）
            noise_x = np.random.normal(0, abs(x_total) * 0.005)
            noise_y = np.random.normal(0, abs(y_total) * 0.005)
            noise_z = np.random.normal(0, abs(z_total) * 0.005)

            cumulative_x = base_x + noise_x
            cumulative_y = base_y + noise_y
            cumulative_z = base_z + noise_z

        # 计算本次位移和速率
        if idx == 0:
            # 起始点
            delta_x = 0
            delta_y = 0
            delta_z = 0
            rate_x = 0
            rate_y = 0
            rate_z = 0
        else:
            days_interval = (current_date - prev_date).days
            if days_interval == 0:
                # 同一天，避免除以零
                delta_x = 0
                delta_y = 0
                delta_z = 0
                rate_x = 0
                rate_y = 0
                rate_z = 0
            else:
                delta_x = cumulative_x - prev_cumulative_x
                delta_y = cumulative_y - prev_cumulative_y
                delta_z = cumulative_z - prev_cumulative_z
                
                # 确保速率不超过x,x,z的最大值
                max_rates = {
                    'x': 1.444823,
                    'y': 1.789352,
                    'z': 1.977057
                    }

                # 用于生成随机调整量的函数
                def get_random_adjustment():
                    return abs(np.random.normal(0.2, 0.2))

                # 分别处理X、Y、Z方向的位移限制
                for direction in ['x', 'y', 'z']:
                    # 获取当前方向的变量
                    delta = locals()[f'delta_{direction}']
                    max_rate = max_rates[direction]
                    days = days_interval
                    
                    # 如果位移速率超过最大值，则进行调整
                    if abs(delta / days) > max_rate:
                        # 根据位移方向确定调整方式
                        if delta > 0:
                            adjusted_delta = max_rate * days - get_random_adjustment()
                        else:
                            adjusted_delta = -max_rate * days + get_random_adjustment()
                        
                        # 更新位移值
                        locals()[f'delta_{direction}'] = adjusted_delta

                # 更新累积位移
                cumulative_x = prev_cumulative_x + delta_x
                cumulative_y = prev_cumulative_y + delta_y
                cumulative_z = prev_cumulative_z + delta_z

                # 计算速率
                rate_x = delta_x / days_interval
                rate_y = delta_y / days_interval
                rate_z = delta_z / days_interval

        # 更新当前值
        current_x = point_data['X_start'] - cumulative_x
        current_y = point_data['Y_start'] - cumulative_y
        current_z = point_data['Z_start'] - cumulative_z

        # 记录结果，将 X、Y、Z 转换回米
        result.append({
            '日期': current_date.strftime('%Y-%m-%d'),
            '点名': point,
            'X': current_x / 1000,
            'X_本次位移(mm)': delta_x,
            'X_位移速率(mm/d)': rate_x,
            'X_累计位移(mm)': cumulative_x,
            'Y': current_y / 1000,
            'Y_本次位移(mm)': delta_y,
            'Y_位移速率(mm/d)': rate_y,
            'Y_累计位移(mm)': cumulative_y,
            'Z': current_z / 1000,
            'Z_本次下沉(mm)': delta_z,
            'Z_沉降速率(mm/d)': rate_z,
            'Z_累计下沉(mm)': cumulative_z
        })

        # 更新上一次的值
        prev_cumulative_x = cumulative_x
        prev_cumulative_y = cumulative_y
        prev_cumulative_z = cumulative_z
        prev_date = current_date

# 转换为DataFrame
result_df = pd.DataFrame(result)

# 调整日期列格式
result_df['日期'] = pd.to_datetime(result_df['日期'], format='%Y-%m-%d')

# 按日期和点名列进行排序
point_order = [f'JC{i:02d}' for i in range(1, 13)]
result_df['点名'] = pd.Categorical(result_df['点名'], categories=point_order, ordered=True)
result_df = result_df.sort_values(by=['日期', '点名'])

# 再将日期列转换回指定格式
result_df['日期'] = result_df['日期'].dt.strftime('%Y-%m-%d')

# 按指定顺序排列列
columns_order = [
    '日期', '点名', 'X', 'X_本次位移(mm)', 'X_位移速率(mm/d)', 'X_累计位移(mm)',
    'Y', 'Y_本次位移(mm)', 'Y_位移速率(mm/d)', 'Y_累计位移(mm)',
    'Z', 'Z_本次下沉(mm)', 'Z_沉降速率(mm/d)', 'Z_累计下沉(mm)'
]
result_df = result_df[columns_order]

# 保存到Excel文件
result_df.to_excel('./output/花垣沉降预测数据_汇总_0512.xlsx', index=False)
    
