#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# author:gelin
# datetime:2021/4/29 1:13 上午
# software: PyCharm

"""
标签映射
"""


csl_label_map = {"0": "不相关", "1": "很相关"}

wsc_label_map = {"false": "错误", "true": "正确"}

iflytek_label_map ={'银行': '银行',
                    '社区服务': '社区',
                    '电商': '电商',
                    '支付': '支付',
                    '经营养成': '经营',
                    '卡牌': '卡牌',
                    '借贷': '借贷',
                    '驾校': '驾校',
                    '理财': '理财',
                    '职考': '职考',
                    '新闻': '新闻',
                    '旅游资讯': '旅游',
                    '公共交通': '交通',
                    '魔幻': '魔幻',
                    '医疗服务': '医疗',
                    '影像剪辑': '影像',
                    '动作类': '动作',
                    '工具': '工具',
                    '体育竞技': '体育',
                    '小说': '小说',
                    '运动健身': '运动',
                    '相机': '相机',
                    '辅助工具': '工具',
                    '快递物流': '快递',
                    '高等教育': '教育',
                    '股票': '股票',
                    '菜谱': '菜谱',
                    '行车辅助': '行车',
                    '仙侠': '仙侠',
                    '亲子儿童': '亲子',
                    '购物咨询': '购物',
                    '射击游戏': '射击',
                    '漫画': '漫画',
                    '中小学': '小学',
                    '同城服务': '同城',
                    '成人教育': '成人',
                    '求职': '求职',
                    '电子产品': '电子',
                    '艺术': '艺术',
                    '薅羊毛': '赚钱',
                    '约会社交': '约会',
                    '经营': '经营',
                    '兼职': '兼职',
                    '短视频': '视频',
                    '音乐': '音乐',
                    '英语': '英语',
                    '棋牌中心': '棋牌',
                    '摄影修图': '摄影',
                    '养生保健': '养生',
                    '办公': '办公',
                    '政务': '政务',
                    '视频': '视频',
                    '论坛圈子': '论坛',
                    '彩票': '彩票',
                    '直播': '直播',
                    '其他': '其他',
                    '休闲益智': '休闲',
                    '策略': '策略',
                    '即时通讯': '通讯',
                    '汽车交易': '买车',
                    '违章': '违章',
                    '地图导航': '地图',
                    '民航': '民航',
                    '电台': '电台',
                    '语言(非英语)': '语言',
                    '搞笑': '搞笑',
                    '婚恋社交': '婚恋',
                    '社区超市': '超市',
                    '日常养车': '养车',
                    '杂志': '杂志',
                    '视频教育': '在线',
                    '家政': '家政',
                    '影视娱乐': '影视',
                    '装修家居': '装修',
                    '体育咨讯': '资讯',
                    '社交工具': '社交',
                    '餐饮店': '餐饮',
                    '美颜': '美颜',
                    '问诊挂号': '挂号',
                    '飞行空战': '飞行',
                    '综合预定': '预定',
                    '电影票务': '票务',
                    '笔记': '笔记',
                    '买房': '买房',
                    '外卖': '外卖',
                    '母婴': '母婴',
                    '打车': '打车',
                    '情侣社交': '情侣',
                    '日程管理': '日程',
                    '租车': '租车',
                    '微博博客': '博客',
                    '百科': '百科',
                    '绘画': '绘画',
                    '铁路': '铁路',
                    '生活社交': '生活',
                    '租房': '租房',
                    '酒店': '酒店',
                    '保险': '保险',
                    '问答交流': '问答',
                    '收款': '收款',
                    'MOBA': '竞技',
                    'K歌': '唱歌',
                    '技术': '技术',
                    '减肥瘦身': '减肥',
                    '工作社交': '工作',
                    '团购': '团购',
                    '记账': '记账',
                    '女性': '女性',
                    '公务员': '公务',
                    '二手': '二手',
                    '美妆美业': '美妆',
                    '汽车咨询': '汽车',
                    '行程管理': '行程',
                    '免费WIFI': '免费',
                    '教辅': '教辅',
                    '成人': '两性',
                    '出国': '出国',
                    '婚庆': '婚庆',
                    '民宿短租': '民宿'}

tnews_label_map = {'news_tech': '科技', 'news_entertainment': '娱乐', 'news_car': '汽车', 'news_travel': '旅游',
                   'news_finance': '财经', 'news_edu': '教育', 'news_world': '国际', 'news_house': '房产',
                   'news_game': '电竞', 'news_military': '军事', 'news_story': '故事', 'news_culture': '文化',
                   'news_sports': '体育', 'news_agriculture': '农业', 'news_stock': '股票'}

csldcp_label_map ={'材料科学与工程': '材料',
                             '作物学': '作物',
                             '口腔医学': '口腔',
                             '药学': '药学',
                             '教育学': '教育',
                             '水利工程': '水利',
                             '理论经济学': '理经',
                             '食品科学与工程': '食品',
                             '畜牧学/兽医学': '畜牧',
                             '体育学': '体育',
                             '核科学与技术': '核科',
                             '力学': '力学',
                             '园艺学': '园艺',
                             '水产': '水产',
                             '法学': '法学',
                             '地质学/地质资源与地质工程': '地质',
                             '石油与天然气工程': '石油',
                             '农林经济管理': '农林',
                             '信息与通信工程': '通信',
                             '图书馆、情报与档案管理': '图书',
                             '政治学': '政治',
                             '电气工程': '电气',
                             '海洋科学': '海洋',
                             '民族学': '民族',
                             '航空宇航科学与技术': '航空',
                             '化学/化学工程与技术': '化学',
                             '哲学': '哲学',
                             '公共卫生与预防医学': '卫生',
                             '艺术学': '艺术',
                             '农业工程': '农工',
                             '船舶与海洋工程': '船舶',
                             '计算机科学与技术': '计科',
                             '冶金工程': '冶金',
                             '交通运输工程': '交通',
                             '动力工程及工程热物理': '动力',
                             '纺织科学与工程': '纺织',
                             '建筑学': '建筑',
                             '环境科学与工程': '环境',
                             '公共管理': '公管',
                             '数学': '数学',
                             '物理学': '物理',
                             '林学/林业工程': '林学',
                             '心理学': '心理',
                             '历史学': '历史',
                             '工商管理': '工管',
                             '应用经济学': '应经',
                             '中医学/中药学': '中医',
                             '天文学': '天文',
                             '机械工程': '机械',
                             '土木工程': '土木',
                             '光学工程': '光学',
                             '地理学': '地理',
                             '农业资源利用': '农业',
                             '生物学/生物科学与工程': '生物',
                             '兵器科学与技术': '兵器',
                             '矿业工程': '矿业',
                             '大气科学': '大气',
                             '基础医学/临床医学': '基础',
                             '电子科学与技术': '电子',
                             '测绘科学与技术': '测绘',
                             '控制科学与工程': '控制',
                             '军事学': '军事',
                             '中国语言文学': '中文',
                             '新闻传播学': '新闻',
                             '社会学': '社会',
                             '地球物理学': '地球',
                             '植物保护': '植保'}
