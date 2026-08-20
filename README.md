# ROS2 五只小海龟链式跟随

基于 **ROS2 + turtlesim + Python** 实现的五只小海龟链式跟随项目。

> 本仓库为“五只小海龟跟随”任务

## 效果

```text
turtle1 → turtle2 → turtle3 → turtle4 → turtle5
```

- `turtle1`：领航海龟，可以通过键盘控制
- `turtle2`：跟随 `turtle1`
- `turtle3`：跟随 `turtle2`
- `turtle4`：跟随 `turtle3`
- `turtle5`：跟随 `turtle4`

项目明确给出了上述链式跟随关系，并说明跟随控制根据两只海龟之间的距离和角度偏差进行比例控制。fileciteturn0file0L25-L29

## 环境

- Ubuntu 22.04
- ROS 2
- Python 3
- turtlesim

## 目录结构

```text
.
├── README.md
├── LICENSE
├── .gitignore
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── turtle_follower
├── turtle_follower/
│   ├── __init__.py
│   └── turtle_follower.py
└── launch/
    └── turtle_follower.launch.py
```

## 1. 安装依赖

```bash
sudo apt update
sudo apt install ros-${ROS_DISTRO}-turtlesim
```

## 2. 放入 ROS2 工作空间

```bash
mkdir -p ~/turtle_follower_ws/src
cd ~/turtle_follower_ws/src
git clone <你的 GitHub 仓库地址>.git turtle_follower
```

然后编译：

```bash
cd ~/turtle_follower_ws
source /opt/ros/${ROS_DISTRO}/setup.bash
colcon build --symlink-install
source install/setup.bash
```

如果出现找不到包或可执行文件的问题，重新执行：

```bash
source ~/turtle_follower_ws/install/setup.bash
```

## 3. 运行

### 推荐：一条命令启动

```bash
ros2 launch turtle_follower turtle_follower.launch.py
```

启动后会同时打开 turtlesim 和五只海龟跟随节点。

然后使用键盘控制 `turtle1`：

```text
↑  前进
↓  后退
←  左转
→  右转
```

后面的四只海龟会依次跟随。

### 手动启动

终端 1：

```bash
source /opt/ros/${ROS_DISTRO}/setup.bash
ros2 run turtlesim turtlesim_node
```

终端 2：

```bash
source ~/turtle_follower_ws/install/setup.bash
ros2 run turtle_follower turtle_follower
```

## 4. 核心原理

### ROS2 Service：生成海龟

节点通过 `/spawn` 服务创建 `turtle2`～`turtle5`。

### ROS2 Topic：获得位姿

节点订阅：

```text
/turtle1/pose
/turtle2/pose
/turtle3/pose
/turtle4/pose
/turtle5/pose
```

从 `Pose` 消息中获取：

- `x`
- `y`
- `theta`

### 链式跟随关系

```text
turtle2 ← turtle1
turtle3 ← turtle2
turtle4 ← turtle3
turtle5 ← turtle4
```

### 比例控制

目标位置差：

```python
dx = leader.x - follower.x
dy = leader.y - follower.y
```

距离：

```python
distance = sqrt(dx**2 + dy**2)
```

目标方向：

```python
target_angle = atan2(dy, dx)
```

角度误差归一化到 `[-π, π]` 后，根据比例关系计算速度：

```python
linear.x = min(0.5 * distance, 2.0)
angular.z = 4.0 * angle_diff
```

最后发布到对应海龟的 `/cmd_vel` 话题。

## 5. 调试命令

查看节点：

```bash
ros2 node list
```

查看话题：

```bash
ros2 topic list
```

查看海龟位姿：

```bash
ros2 topic echo /turtle1/pose
```

查看跟随海龟的速度指令：

```bash
ros2 topic echo /turtle2/cmd_vel
```

查看服务：

```bash
ros2 service list
```

## 6. 项目特点

- ROS2 Service + Topic 通信
- Python 编写控制节点
- 五只海龟链式多智能体跟随
- 基于比例控制的实时运动控制
- 无 URDF / RViz 额外依赖，项目结构更轻量

## 7. GitHub 上传

在项目根目录执行：

```bash
git init
git add .
git commit -m "feat: add ROS2 five turtle follower"
git branch -M main
git remote add origin https://github.com/你的用户名/turtle_follower_ros2.git
git push -u origin main
```

## 8. 后续可以继续改进的方向

- 增加跟随距离阈值，避免海龟过度靠近
- 增加速度限幅和角速度限幅
- 将比例系数改成 ROS2 参数，可运行时调整
- 增加轨迹记录和可视化
- 从简单 P 控制进一步升级为 PID 控制

## 致谢

项目对原机器人操作系统课程实验中的“小海龟跟随”任务进行改进，从单独的小海龟跟随任务创新性地拓展为五只小海龟跟随任务，代码结构在保留实验核心思路的基础上进行了 GitHub 项目化整理。
