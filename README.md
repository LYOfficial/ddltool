# ddltool
> 一款 Windows 桌面端的简易 DDL 截止时间计时小工具。
>
> 基于 Python 开发，使用 pyinstaller 封装完成。



![bf8a8f9c8b120d10c633c14c447db6e7.png](https://pic.awa.ms/f/2025/04/26/680cf411f1417.png)
![203a71e02d6df42f57d55261263b1c30.png](https://pic.awa.ms/f/2025/04/26/680cf41282957.png)
![6858e66a647ad0922f1b63055f5fab30.png](https://pic.awa.ms/f/2025/04/26/680cf41302634.png)



## 🚀 调整和改进

已有功能：

- [x] 浮窗展示
- [x] 双击打开设置
- [x] 新增/编辑/删除 项目
- [x] 快捷选择日期
- [x] 鼠标自由拖动浮窗
- [x] 右键选择关闭
- [x] 开机自启动设置
- [x] 窗口位置及大小自定义
- [x] 窗口背景颜色自定义
- [x] 字体/字号/字粗/字颜色 自定义
- [x] 窗口出题自定义
- [x] 窗口透明度调整

该项目仍在开发中，下一次更新将侧重于以下任务：

- [x] 打包封装
- [ ] 项目编辑bug
- [ ] 项目删除bug
- [ ] 右键打开设置
- [ ] 覆盖更广的双击位置
- [ ] 快捷时间选择
- [ ] 界面美化
- [ ] 背景透明



## 💻 开发

1.克隆仓库

```
git clone https://github.com/LYOfficial/ddltool.git
```

2.安装库文件 (python >= 3.10)

```
pip install ttkthemes tkcalendar
```

3.安装封装工具

```
pip install pyinstaller
```

4.进行代码开发

文件架构如下

```
ddltool/
├── ddltool.py          # 应用入口文件
├── gui/
│   ├── __init__.py     # 标识gui文件夹是一个Python包
│   ├── display_window.py # 显示截止日期信息的窗口代码
│   └── settings_window.py# 设置和管理截止日期的窗口代码
├── data/
│   ├── ddl_items.json  # 存储截止日期项目的JSON文件
│   └── settings.json   # 存储应用设置的JSON文件 (窗口位置, 自启动等)
├── utils/
│   ├── __init__.py     # 标识utils文件夹是一个Python包
│   ├── data_manager.py # 负责加载和保存数据/设置
│   └── system_helper.py# 负责处理系统相关功能 (如开机自启动)
├── icon.ico            # 项目LOGO
├── start.bat           # 快捷启动
└── README.md           # 项目说明文件
```

5.封装

```
python -m PyInstaller --windowed --onedir --add-data "data;data" ddltool.py
```

或包含 icon 进行封装

```
python -m PyInstaller --windowed --onedir --add-data "data;data" --icon="icon.ico" ddltool.py
```



## 🤝 贡献者

我们感谢以下为这个项目做出贡献的人：

<table>
  <tr>
    <td align="center">
      <a href="#" title="defina o título do link">
        <img src="https://avatars.githubusercontent.com/u/79127081?v=4" width="100px;" alt="Foto do Iuri Silva no GitHub"/><br>
        <sub>
          <b>LYOfficial</b>
        </sub>
      </a>
    </td>

  </tr>
</table>



## 📝 许可证

该项目已获得许可。有关详细信息，请参阅 [LICENSE](https://github.com/LYOfficial/ddltool/blob/main/LICENSE) 文件。
