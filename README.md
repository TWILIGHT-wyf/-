# 数据库课程设计 - 外卖管理平台系统

这是一个基于 Vue.js 和 Flask 的外卖管理平台系统，实现了用户、商家和骑手三方角色的功能需求。

## 项目简介

本项目是一个完整的外卖管理系统，旨在实现对外卖订单的全流程管理。通过设计合理的数据库结构和用户友好的界面，提供了用户下单、商家接单、骑手配送等核心功能，实现了外卖全流程的数字化管理。

## 系统架构

系统采用前后端分离架构：

- 前端：基于 Vue.js 框架，使用 Element UI 组件库构建用户界面
- 后端：使用 Flask 框架提供 RESTful API 服务
- 数据库：Microsoft SQL Server 数据库存储系统数据
- 认证：JWT 令牌认证机制保障系统安全

## 功能特点

### 用户端

- 用户注册与登录：支持用户账号创建和身份验证
- 商家浏览：查看所有可用商家及其菜品信息
- 订单管理：创建订单、查看订单状态(未发货/配送中/已完成)
- 个人中心：管理个人信息、修改密码

### 商家端

- 店铺管理：创建和维护店铺信息、上传店铺图片
- 菜品管理：添加、修改、删除菜品信息
- 订单处理：接收订单、更新订单状态
- 数据统计：查看月销量等业务数据

### 骑手端

- 订单接取：查看并接取未配送订单
- 配送管理：管理正在配送的订单
- 订单完成：标记订单为已送达状态
- 个人中心：管理个人信息

## 技术栈

### 前端

- Vue.js 2.x：前端框架
- Element UI：UI 组件库
- Vue Router：前端路由管理
- Axios：HTTP 请求库

### 后端

- Flask：Python Web 框架
- SQLAlchemy：ORM 框架
- PyJWT：JWT 认证
- Redis：缓存

### 数据库

- Microsoft SQL Server：关系型数据库

## 安装与使用

### 系统要求

- Python 3.8+
- Node.js 12+
- Microsoft SQL Server
- Redis (可选)

### 安装步骤

1. 克隆仓库到本地

```bash
git clone https://github.com/TWILIGHT-wyf/Database-Course-Project.git
cd 数据库课程设计
```

2. 安装后端依赖

```bash
cd sqlweb/backcode_wyf
pip install -r requirements.txt
```

3. 安装前端依赖

```bash
cd ../front_wyf/wyf
npm install
```

4. 配置数据库

   - 在`sqlweb/backcode_wyf/config_wyf.py`中配置您的数据库连接信息

5. 启动系统

```bash
# 在项目根目录执行
python sqlweb/run_wyf.py
```

系统将自动启动前端和后端服务，并在浏览器中打开应用。

## 数据库设计

系统包含以下核心表：

- Users_wyf：用户信息
- Vendors_wyf：商家信息
- Riders_wyf：骑手信息
- Dishes_wyf：菜品信息
- Orders_wyf：订单信息
- OrderDetails_wyf：订单详情

## 贡献指南

欢迎提交 Issue 或 Pull Request 来完善本项目。请确保代码符合项目的编码规范和设计风格。

## 开发者

 (TWILIGHT-wyf)
