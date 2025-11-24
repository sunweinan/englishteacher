# 数据库结构设计概要

本方案围绕商城与安装配置的需求，定义了精简且易扩展的数据结构，尽可能通过少量查询获取常用数据。

## 核心业务表
- **users**：用户及管理员账户，`username` 唯一索引，含 `role` 字段区分权限。
- **products**：商品/课程，包含价格与库存。
- **orders**：订单主表，保存订单金额与状态。
- **order_items**：订单明细，关联商品与数量。
- **payments**：支付记录，关联订单，保存支付渠道与通知内容。

## 配置与扩展
- **system_settings**：配置键值表，按 `category + key` 唯一约束，存放站点域名、IP、后端端口等服务器信息，可一次性批量读取减少多次查询。
- **integration_configs**：外部集成配置（如微信支付、短信服务），存储在 JSON 字段中并按 `provider` 建立索引，便于按需加载单条记录。

## 查询优化要点
- 关键业务字段（如 `users.username`、`orders.user_id`、`order_items.order_id`、`payments.order_id`、`system_settings.category/key`、`integration_configs.provider`）均建立索引或唯一约束，以减少查找次数。
- 配置类数据集中在 `system_settings` 与 `integration_configs`，前端或服务端可通过单次查询加载后缓存，避免多表或多次访问。
- 订单与支付拆分主表/明细，便于统计时按需联表，日常读取商品列表和配置数据无需跨表，保持轻量。

## 安装与预置数据
- 安装向导会根据填写的信息创建数据库、账号与上述表，并写入 `system_settings`、`integration_configs`、管理员账户及示例商品等预装数据，便于开箱即用。
