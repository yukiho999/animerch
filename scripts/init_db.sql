-- ============================================
-- 二次元周边信息聚合平台 — 完整建表脚本
-- ============================================

CREATE DATABASE IF NOT EXISTS animerch
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE animerch;

-- 1. IP 总表
CREATE TABLE IF NOT EXISTS ip (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(200) NOT NULL COMMENT 'IP名称',
    aliases     JSON COMMENT '别名列表 ["魔道","mdzs"]',
    category    VARCHAR(50) COMMENT '动漫/小说/游戏/国产原创',
    cover_url   VARCHAR(1000) COMMENT '封面图URL',
    description TEXT COMMENT '简介',
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. 周边正式表（人工确认后数据）
CREATE TABLE IF NOT EXISTS merch (
    id                BIGINT AUTO_INCREMENT PRIMARY KEY,
    ip_id             BIGINT NOT NULL COMMENT '所属IP',
    name              VARCHAR(500) NOT NULL COMMENT '周边名称',
    category          ENUM('吧唧','色纸','亚克力立牌','粘土人','挂件','文件夹','海报','立牌','其他') COMMENT '制品种类',
    official_price    DECIMAL(10,2) COMMENT '官方发售价',
    release_date      DATE COMMENT '发售日期',
    release_method    ENUM('通贩','场贩','受注','限定','抽选','未知') DEFAULT '未知' COMMENT '发售方式',
    is_discontinued   TINYINT(1) DEFAULT 0 COMMENT '是否绝版 0=在售 1=绝版',
    attributes        JSON COMMENT '扩展属性 {"工艺":["烫金"],"尺寸":"58mm","材质":"马口铁"}',
    image_url         VARCHAR(2000) COMMENT '图片URL',
    source_platform   VARCHAR(50) DEFAULT 'weibo' COMMENT '来源平台',
    source_url        VARCHAR(2000) COMMENT '来源链接',
    original_post_id  BIGINT COMMENT '关联 post_raw.id',
    status            ENUM('active','hidden') DEFAULT 'active' COMMENT '展示状态',
    created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at        DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ip (ip_id),
    INDEX idx_category (category),
    INDEX idx_release_date (release_date),
    INDEX idx_is_discontinued (is_discontinued),
    INDEX idx_status (status),
    CONSTRAINT fk_merch_ip FOREIGN KEY (ip_id) REFERENCES ip(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. 工艺标签表
CREATE TABLE IF NOT EXISTS craft_tag (
    id   BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE COMMENT '工艺名称'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. 周边-工艺 多对多关联
CREATE TABLE IF NOT EXISTS merch_craft (
    merch_id BIGINT NOT NULL,
    craft_id BIGINT NOT NULL,
    PRIMARY KEY (merch_id, craft_id),
    CONSTRAINT fk_mc_merch FOREIGN KEY (merch_id) REFERENCES merch(id) ON DELETE CASCADE,
    CONSTRAINT fk_mc_craft FOREIGN KEY (craft_id) REFERENCES craft_tag(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. 原始帖子表（爬虫直接入库）
CREATE TABLE IF NOT EXISTS post_raw (
    id            BIGINT AUTO_INCREMENT PRIMARY KEY,
    platform      VARCHAR(50) NOT NULL DEFAULT 'weibo' COMMENT '平台',
    post_id       VARCHAR(100) NOT NULL COMMENT '平台帖子ID',
    author_name   VARCHAR(200) COMMENT '发帖账号名',
    author_uid    VARCHAR(100) COMMENT '发帖账号UID',
    title         VARCHAR(1000) COMMENT '帖子标题/摘要',
    content       TEXT COMMENT '正文全文',
    images        JSON COMMENT '图片URL列表',
    video_url     VARCHAR(2000) COMMENT '视频URL',
    post_url      VARCHAR(2000) COMMENT '帖子链接',
    post_time     DATETIME COMMENT '发帖时间',
    raw_json      JSON COMMENT '原始API返回完整JSON',
    status        ENUM('pending','parsed','approved','rejected','error') DEFAULT 'pending' COMMENT '处理状态',
    error_msg     TEXT COMMENT '错误信息',
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_post (platform, post_id),
    INDEX idx_status (status),
    INDEX idx_post_time (post_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. 帖子解析结果表（NLP填充，待审核）
CREATE TABLE IF NOT EXISTS merch_post (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    post_raw_id     BIGINT NOT NULL UNIQUE COMMENT '关联原始帖子',
    ip_name_hint    VARCHAR(200) COMMENT 'NLP识别的IP名',
    ip_id           BIGINT COMMENT '匹配到的IP ID',
    merch_name      VARCHAR(500) COMMENT '周边名称',
    category_hint   VARCHAR(50) COMMENT 'NLP识别的品类原文',
    category        ENUM('吧唧','色纸','亚克力立牌','粘土人','挂件','文件夹','海报','立牌','其他') COMMENT '制品种类',
    official_price  DECIMAL(10,2) COMMENT '识别价格',
    release_date    DATE COMMENT '识别发售日期',
    release_method  ENUM('通贩','场贩','受注','限定','抽选','未知') DEFAULT '未知' COMMENT '发售方式',
    craft_keywords  JSON COMMENT '提取的工艺关键词 ["烫金","银葱"]',
    attributes      JSON COMMENT '其他属性',
    confidence      DECIMAL(3,2) DEFAULT 0.00 COMMENT 'NLP置信度',
    need_review     TINYINT(1) DEFAULT 1 COMMENT '是否需要人工审核',
    review_status   ENUM('pending','approved','rejected','edited') DEFAULT 'pending' COMMENT '审核状态',
    reviewed_by     VARCHAR(50) COMMENT '审核人',
    reviewed_at     DATETIME COMMENT '审核时间',
    created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_review_status (review_status),
    INDEX idx_ip_id (ip_id),
    CONSTRAINT fk_mp_post FOREIGN KEY (post_raw_id) REFERENCES post_raw(id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
