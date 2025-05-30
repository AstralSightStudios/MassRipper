# MassRipper

此工具用于从hci蓝牙日志中提取小米手环文件传输协议所发送的文件

本项目遵从[agpl-3.0协议](https://gnu.ac.cn/licenses/agpl-3.0.txt)

<!-- PROJECT LOGO -->
<br />

<p align="center">
  <a href="https://github.com/AstralSightStudios/MassRipper/">
    <img src="icon/icon.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">MassRipper</h3>
  <p align="center">
    一个快捷可靠的小米手环Mass传输文件恢复工具！
    <br />
    <a href="https://github.com/AstralSightStudios/MassRipper/"><strong>探索本项目的文档 »</strong></a>
    <br />
    <br />
    <a href="https://github.com/AstralSightStudios/MassRipper/issues">报告Bug</a>
    ·
    <a href="https://github.com/AstralSightStudios/MassRipper/issues">提出新特性</a>
  </p>

</p>

## 目录

- [MassRipper](#massripper)
  - [目录](#目录)
    - [使用指南](#使用指南)
          - [使用前配置要求](#使用前配置要求)
          - [安装步骤](#安装步骤)
    - [文件目录说明](#文件目录说明)
    - [作者](#作者)
    - [鸣谢](#鸣谢)

### 使用指南

* 第一步，需要进入手机开发模式并将 "启用蓝牙 HCI 信息手机日志" 选项设为开启状态
* 第二步，使用健康运动传输ota文件或传输其他文件
* 第三步，返回开发模式将 "启用蓝牙 HCI 信息手机日志" 选项设为关闭
* 第四步，将log文件(一般位于 /sdcard/mtklog/btlog/btsnoop_hci.log 或 /sdcard/btsnoop_hci.log)回传电脑
* 第五步，打开工具选择btsnoop_hci.log文件并点击解析
* 第六步，待分析完毕后左侧的文件列表会显示文件的md5，您可以点击需要的文件，选中后右侧将会显示文件完整性，如完整性为 100% 则可使用列表下方按钮立即导出，若文件完整性并非 100% 则需继续补充日志文件以增加完整性
* 提示：左上角文件菜单中可保存/加载当前已解析的数据

###### 使用前配置要求

* WireShark

###### 安装步骤

* 第一步，下载WireShark并安装
* 第二步，打开软件并解析追踪文件以检查WireShark是否可以被成功调用

### 文件目录说明

```
filetree 
├── CHANGELOG.md 变更日志
├── LICENSE.txt 许可证文件
├── README.md readme
├── /icon/ 图标文件
│  ├── icon.ico ico格式图标
│  └── icon.png png格式图标
├── control.py 界面控制逻辑
├── main.py 启动逻辑
├── ripper.py 提取逻辑
├── ui.py 界面逻辑
├── version.py 版本信息
└── requirements.txt 依赖信息

```

### 作者

- [66hh](https://github.com/66hh)

### 鸣谢

- [AstralSightStudios](https://github.com/AstralSightStudios)
- [Searchstars](https://github.com/Searchstars)
- [Best_README_template](https://github.com/shaojintian/Best_README_template)
- [WireShark](https://www.wireshark.org/)
- [PyShark](https://github.com/KimiNewt/pyshark)