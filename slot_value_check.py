import re
from calendar import monthrange
from datetime import datetime, timedelta
from slot_value_check.true_fake_mapping import TrueFakeMapping


class SlotValueCheck:
    def __init__(self):
        self.month_mapping = {
            '一': '1',
            '二': '2',
            '三': '3',
            '四': '4',
            '五': '5',
            '六': '6',
            '七': '7',
            '八': '8',
            '九': '9',
            '十': '10',
            '十一': '11',
            '十二': '12',
        }
        self.day_mapping = {
            '一': '1',
            '二': '2',
            '三': '3',
            '四': '4',
            '五': '5',
            '六': '6',
            '七': '7',
            '八': '8',
            '九': '9',
            '十': '10',
            '十一': '11',
            '十二': '12',
            '十三': '13',
            '十四': '14',
            '十五': '15',
            '十六': '16',
            '十七': '17',
            '十八': '18',
            '十九': '19',
            '二十': '20',
            '二十一': '21',
            '二十二': '22',
            '二十三': '23',
            '二十四': '24',
            '二十五': '25',
            '二十六': '26',
            '二十七': '27',
            '二十八': '28',
            '二十九': '29',
            '三十': '30',
            '三十一': '31',
        }

    def sentence_empty(self, row_text):
        """
            row_text is empty
        :param row_text: 文本
        :return: bool
        """
        if len(row_text.strip().replace(' ', '')):
            return True
        return False

    def check_week(self, cur_week):
        if len(re.findall(r'下', cur_week)) > 0:
            return None
        cur_weeks = datetime.now().isoweekday()
        back_week = re.findall(r'上', cur_week)
        lazy_week = {}
        for index in range(1, 8, 1):
            for cur_mapping in ['周', '星期']:
                lazy_week[cur_mapping.__add__(str(index))] = datetime.now() + timedelta(days=index - cur_weeks)
        for index, zh in enumerate(['一', '二', '三', '四', '五', '六', '末']):
            for cur_mapping in ['周', '星期']:
                lazy_week[cur_mapping.__add__(zh)] = lazy_week['周'.__add__(str(index + 1))]
        for cur_mapping in ['周', '星期']:
            lazy_week[cur_mapping.__add__('天')] = lazy_week['周一']
            lazy_week[cur_mapping.__add__('日')] = lazy_week['周一']

        for cur_w, cur_value in zip(lazy_week.keys(), lazy_week.values()):
            if str(cur_w) in cur_week:  # 需要处理的带有星期的字符串
                date_str = cur_value
                if len(back_week) > 0:
                    for _ in back_week:
                        date_str -= timedelta(days=7)
                return date_str.strftime("%Y-%m-%d")  # 只说了上周
        # return cur_week  # 无法匹配到任何一个规则
        # 只说了上周/这周，这周相当于今天
        if len(back_week) > 0:
            back_date = datetime.now()
            for _ in back_week:
                back_date -= timedelta(days=7)
            return back_date.strftime("%Y-%m-%d")
        return None

    def start_date_check(self, start_date):  # 接口规范：[yyyy-MM-dd]
        """
            对日期槽值进行检测
            :param start_date: 识别出来的日期槽值
            :return:
        """
        # 1、固定的几种（合法的）说法，不包含具体的时间如：今天，昨天
        general_date = {'今天': datetime.now().strftime('%Y-%m-%d'),
                        '昨天': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d'),
                        '昨': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
                        }
        # 包含具体的年份
        detect_year_missing = r'[0-9]{2,4}年'  # 最多识别4个，一个完整的年份最多也就4位
        # detect_month = r'[0-9]{1,6}月'  # 识别月份，可能用户说出了年份但是没有说出“年”
        # detect_day = r'[0-9]{1,2}日'  # 识别日，可能用户输出了月份但是没有输出‘月’
        detect_month = r'[(1|2|3|4|5|6|7|8|9|10|11|12) (一|二|三|四|五|六|七|八|九|十|十一|十二)]月'
        detect_day = r'[(1|2|3|4|5|6|7|8|9|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31) ' \
                     r'(一|二|三|四|五|六|七|八|九|十|十一|十二|十三|十四|十五|十六|十七|十八|十九|二十|二十一|二十二' \
                     r'二十三|二十四|二十五|二十六|二十七|二十八|二十九|三十|三十一)]日'
        inleagel_date = r'{明|后|下一|下|下个|过}'  # 不合法的表述
        y_m_d = {
            'year': [],
            'month': [],
            'day': []
        }  # ['我要看2018年2月1日的电影']
        assert isinstance(start_date, list) and len(start_date) > 0  # 传进来的是个代表日期的list
        now_time = datetime.now()  # 获取当前日期
        for cur_date in start_date:
            for (cur_key, cur_value) in zip(general_date.keys(), general_date.values()):  # 与具体时间无关的过去时间的表述
                if cur_key in cur_date:  # 与具体时间无关的过去时间的表述
                    yey_mom_dydy = cur_value.split('-')
                    y_m_d['year'] = yey_mom_dydy[0]
                    y_m_d['month'] = yey_mom_dydy[1]
                    y_m_d['day'] = yey_mom_dydy[2]
            if len(re.findall(inleagel_date, cur_date)) > 0:  # 不合法的表述
                continue
            if len(y_m_d['year']) > 0:
                continue
            print('cur_date:', cur_date)
            week_test = self.check_week(cur_date)
            print('week_test:', week_test)
            if week_test is not None:
                week_test = week_test.split('-')
                y_m_d['year'] = week_test[0]
                y_m_d['month'] = week_test[1]
                y_m_d['day'] = week_test[2]
                continue
            # 对包含具体年月日日期进行判别
            detect_year_missing = re.findall(detect_year_missing, cur_date)

            get_cur_month = re.findall(detect_month, cur_date)  # 查找到月份
            for index, cur_month in enumerate(get_cur_month):
                for cur_m in self.month_mapping.keys():
                    if cur_m in cur_month:
                        get_cur_month[index] = get_cur_month[index].replace(cur_m, self.month_mapping[cur_m])

            get_cur_day = re.findall(detect_day, cur_date)  # 得到日，考虑到了用户漏了“月” 112日
            for index, cur_day in enumerate(get_cur_day):
                for cur_d in self.day_mapping.keys():
                    if cur_d in cur_day:
                        get_cur_month[index] = get_cur_month[index].replace(cur_m, self.day_mapping[cur_m])

            if len(detect_year_missing) > 0:  # 用户提到了"年" 08年、2018年
                detect_year_missing = detect_year_missing[0].replace('年', '')  # 获取 08 2018
                assert len(detect_year_missing) == 4  # 在送到网络之前所有的年份已经进行了对齐，这里就不需要进行判断
                if now_time.year < int(detect_year_missing):  # 年份错误,
                    continue
                else:
                    y_m_d['year'] = detect_year_missing  # 年份合理

            try:
                if len(get_cur_day) > 0:
                    _get_cur_day = get_cur_day[0].replace('日', '')  # 获取日
                if len(get_cur_month) > 0:  # 提到了月
                    _get_cur_month = get_cur_month[0].replace('月', '')  # 得到月份 0812月(等价于：2018年12月)，12月

                    if (len(_get_cur_month) >= 1) and (len(_get_cur_month) <= 2):  # 12月
                        if (int(_get_cur_month) < 12) and (int(_get_cur_month) >= 1):  # 月份合法
                            if len(y_m_d['year']) == 0:
                                y_m_d['year'] = str(now_time.year)  # 默认为当前年  2018
                            y_m_d['month'] = _get_cur_month  # 得到当前月     12
                            # 查看日期是否合法
                            _, dates = monthrange(now_time.year, int(_get_cur_month))  # 获取当前年份有多少天
                            if len(_get_cur_day) > 0:
                                if (int(_get_cur_day) <= dates) and (int(_get_cur_day) >= 1):  # 日合法
                                    y_m_d['day'] = _get_cur_day  # 得到当前日     1
                            else:
                                y_m_d['day'] = now_time.day  # 没有提到日，那么设置为系统日期
                        else:
                            continue  # 该时间不合法，继续查找下一个
                    else:

                        if (2 < len(_get_cur_month)) and (len(_get_cur_month) <= 4):  # 用户可能说了 0812月需要提取08 和 12
                            yea, mon = _get_cur_month[:2], _get_cur_month[2:]
                            if int(yea) > int(str(now_time.year)[2:]):
                                y_m_d['year'] = '19'.__add__(yea)
                            else:
                                y_m_d['year'] = str(now_time.year)[:2].__add__(yea)
                            if (int(mon) >= 1) and (int(mon) <= 12):
                                y_m_d['month'] = mon  # 得到当前月     12
                            else:
                                continue  # 月份不合法
                        else:
                            if (len(_get_cur_month) >= 4) and (len(_get_cur_month) <= 5):  # 201812月 20181月
                                yea, mon = _get_cur_month[:4], _get_cur_month[4:]
                                if int(yea) < now_time.year:
                                    y_m_d['year'] = yea
                                else:
                                    continue  # 不符合要求
                                if (int(mon) >= 1) and (int(mon) <= 12):
                                    y_m_d['month'] = mon  # 得到当前月
                                else:
                                    continue
                            else:
                                continue
                # else:  # 没有提到年也没有提到月，只是提到了日
                _get_cur_day = get_cur_day[0].replace('日', '')  # 获取日
                _, dates = monthrange(now_time.year, now_time.month)  # 获取当前年份有多少天
                try:
                    if len(_get_cur_day) > 0:
                        if int(_get_cur_day) <= dates:
                            if len(y_m_d['year']) == 0:
                                y_m_d['year'] = str(now_time.year)
                            if len(y_m_d['month']) == 0:
                                y_m_d['month'] = str(now_time.month)
                            y_m_d['day'] = str(_get_cur_day)
                    else:
                        continue
                except Exception:
                    raise Exception
            except Exception:
                print()
        res = ''
        # for cur_value in y_m_d.values():
        print(y_m_d)
        # for cur_value in y_m_d.values():
        #     print('cur_value:', cur_value)
        #     if len(cur_value) > 0:
        #         if isinstance(cur_value, list):
        #             res = res.__add__('-').__add__(cur_value[0])
        #         else:
        #             res = res.__add__('-').__add__(cur_value)
        #     else:
        #         res = res.__add__('-00')
        years = y_m_d['year']
        months = y_m_d['month']
        days = y_m_d['day']
        print(years, months, days)
        if len(years) == 0:
            years = ''
        if len(months) == 0:
            months = ''
        if len(days) == 0:
            days = ''
        # return res[1:]
        date_time = []
        for index, curr in enumerate([years, months, days]):
            if not curr.__eq__(''):
                date_time.append(curr)
        return '-'.join(date_time)

    def joint_time(self, time1, times):
        if not time1:
            return times
        bigger_time = ['傍晚', '晚上', '晚间', '深夜']
        find = False
        if times.__eq__('00:00:00'):
            return times
        else:
            for cur in bigger_time:
                if time1 in cur:
                    find = True
                    if times and len(times) > 0:
                        split_time = times.split(':')
                        int_time = int(split_time[0])
                        print('find')
                        return str(12 + int_time).__add__(':').__add__(':'.join(split_time[1:]))
                    else:
                        return '00:00:00'
            if not find:
                return times

    def start_time_end_time_check(self, start_time, end_time=None):
        """
        开始、结束时间的检测
        :param start_time:
        :param end_time:
        :return:
        """
        assert isinstance(start_time, list)
        general_time = {
            '凌晨': [24, 0, 1, 2, 3, 4, 5],
            '早上': [6, 7, 8, 9],
            '早晨': [6, 7, 8, 9],
            '上午': [9, 10, 11, 12],
            '中午': [9, 10, 11, 12],
            '下午': [13, 14, 15, 16],
            '傍晚': [17, 18, 19],
            '晚上': [20, 21, 22, 23],
            '晚间': [20, 21, 22, 23],
            '深夜': [23, 24, 1, 2, 3, 4, 5]
        }
        time_value = []
        for cur_time in start_time:  # 传过来的time是一个列表
            try:
                # 拿到具体的时间
                sp_time = re.findall(r'[0-9]+[:][0-9]*', cur_time)
                hour = re.findall(r'[0-9]+[点|时]', cur_time)
                minite = re.findall(r'[0-9]+分', cur_time)
                sec = re.findall(r'[0-9]+秒', cur_time)
                spe_mini = re.findall(r'{ |点半|点一刻}', cur_time)
                bigger_time = re.findall(r'{凌晨|早上|早晨|上午|中午|下午|傍晚|晚上|晚间|深夜}', cur_time)
                cur_time_value = ''  # time 8:30:20
                print('data:', (bigger_time, sp_time, hour, spe_mini, minite, sec))
                if len(sp_time) > 0:
                    cur_time_value = cur_time_value.__add__(sp_time[0]).__add__(':00')
                    if len(sec) > 0:
                        cur_time_value = cur_time_value.__add__(sp_time[0][:-1])
                    time_value.append([bigger_time[0], cur_time_value])
                    continue
                else:
                    for index, cur_time in enumerate([hour, minite, sec]):
                        if len(cur_time) > 0:
                            cur_time_value = cur_time_value.__add__(':'.__add__(cur_time[0][:-1]))
                        else:
                            cur_time_value = cur_time_value.__add__(':00')
                    cur_time_value = cur_time_value[1:]
                    if len(bigger_time) > 0:
                        time_value.append([bigger_time[0], cur_time_value])  # 至于上午 16点是不是合法的说法由DM兜住。
                    else:
                        time_value.append([None, cur_time_value])
                    # 处理包含 bigger_time， 拼接
                    # self.joint_time(time_value[0], time_value[1])
                    time_value = self.joint_time(time_value[0][0], time_value[0][1])
            except Exception:
                print('time error......')
        return time_value

    @staticmethod
    def start_channelname_mapping(row_text):
        """
            对文本中的中央台进行替换如：中央台----->CCTV1，央视十二套----->CCTV12
        :param row_text:
        :return:
        """
        detect_channel = r'[a-zA-Z]+[-]?[一 二 三 四 五 六 七 八 九 十 十一 十二 十三 十四 十五]+[套 台]*'  # CCTV一 CCTV-一
        detect_channe2 = r'(中央台|央视台|中央|央视)+(.*)[一 二 三 四 五 六 七 八 九 十 十一 十二 十三 十四 十五' \
                         r'1 2 3 4 5 6 7 8 9 10 11 12 13 14 15]+[电视台 台 套]*'  # 中央一 中央-一
        detect_channe3 = r'(中央电视台|央视台|中央台|中央|央视)+(.*)(军事农业频道|军事农业|社会与法频道|社会与法' \
                         r'|电视剧频道|电视剧|军事频道|军事|农业频道|农业|农业财经频道|农业财经|体育频道|体育|综艺频道' \
                         r'|综艺|音乐频道|音乐|戏曲频道|戏曲|少儿频道|少儿|科教频道|科教|电影频道|电影|国际频道|国际|' \
                         r'财经频道|财经|纪录频道|纪录|综合频道|综合)*'
        detect_channe4 = r'(.*)(军事农业频道|军事农业|社会与法频道|社会与法' \
                         r'|电视剧频道|电视剧|军事频道|军事|农业频道|农业|农业财经频道|农业财经|体育频道|体育|综艺频道' \
                         r'|综艺|音乐频道|音乐|戏曲频道|戏曲|少儿频道|少儿|科教频道|科教|电影频道|电影|国际频道|国际|' \
                         r'财经频道|财经|纪录频道|纪录|综合频道|综合)*'  # 只说了财经频道
        if isinstance(row_text, list):
            row_text = row_text[0]  # 传过来的不一定是str
        row_text = row_text.upper()
        res = re.findall(detect_channe2, row_text)
        res1 = re.findall(detect_channel, row_text)
        res3 = re.findall(detect_channe3, row_text)
        res4 = re.findall(detect_channe4, row_text)
        print('res3:', res3)
        ischeck4 = True
        for cur_ in res3:
            tmp = list(filter(lambda x: len(x.strip()) > 0, cur_))
            if len(tmp) == 1:
                row_text = row_text.replace(tmp[0], 'CCTV-1')
                ischeck4 = False
            else:
                row_text = row_text.replace(tmp[0], 'CCTV')
                ischeck4 = False
        # 中央
        for _ in res:
            if '中央' in row_text:
                row_text = row_text.replace('中央', 'CCTV')
            for index, zh_spoken in enumerate(['十五', '十四', '十三', '十二', '十一', '十', '九', '八', '七', '六', '五', '四',
                                               '三', '二', '一']):
                if zh_spoken in row_text:
                    row_text = row_text.replace(zh_spoken, str(15 - index))
                    break
            if '台' in row_text:
                row_text = row_text.replace('台', '')
            # if (not '台' in row_text) and (not '套' in row_text):
            #     row_text = row_text.__add__('套')
            if '套' in row_text:
                row_text = row_text.replace('套', '')
        # CCTV
        for _ in res1:
            place_kepping = ''
            for index, zh_spoken in enumerate(['十五', '十四', '十三', '十二', '十一', '十', '九', '八', '七', '六', '五', '四',
                                               '三', '二', '一']):
                if zh_spoken in row_text:
                    place_kepping = str(15 - index)
                    row_text = row_text.replace(zh_spoken, str(15 - index))
                    break
            if '台' in row_text:
                row_text = row_text.replace('台', '套')
            if (not ('台' in row_text)) and (not ('套' in row_text)):
                row_text = row_text.replace(place_kepping, place_kepping.__add__('套'))
        print('这儿返回的：', row_text)
        return row_text

    @staticmethod
    def year_time_checking(text):
        # print(start_date_check(['我要看2018年的新闻联播']))
        detect_year = r'[0-9]+年'  # 可能年份没有说全
        detect_time_hour = r'[一 二 三 四 五 六 七 八 九 十 十一 十二 十三 十四 十五 十六 十七 十八 十九 二十 二十一 二十二 ' \
                           r'二十三 二十四]+[点 时]+'  # 小时是中文
        special = r'(去年|前年|上个月|上周)'
        res = re.findall(detect_year, text)
        res1 = re.findall(detect_time_hour, text)
        for cur_miss in res:
            cur_miss = cur_miss[:-1]
            if len(cur_miss) == 2:
                now_y = int(str(datetime.now().year)[2:])
                if now_y < int(cur_miss):
                    text = text.replace(cur_miss, '19'.__add__(cur_miss))
                else:
                    text = text.replace(cur_miss, str(datetime.now().year)[:2].__add__(cur_miss))
            elif len(cur_miss) == 4:
                if datetime.now().year <= int(cur_miss):
                    text = text.replace(cur_miss, str(datetime.now().year)) # 默认当前年份。
        for _ in res1:
            if '时' in text:
                text = text.replace('时', '点')
            for index, zh_spoken in enumerate(['二十四', '二十三', '二十二', '二十一', '二十', '十九', '十八', '十七',
                                               '十六', '十五', '十四', '十三', '十二', '十一', '十', '九', '八', '七', '六',
                                               '五', '四', '三', '二', '一']):
                if zh_spoken in text:
                    text = text.replace(zh_spoken, str(24 - index))
                    break
        return text


class SlotLazyMapping:
    """
    回看,直播，点播，模糊， 指令等槽的相关映射
    """
    def __init__(self):
        self.turnfake_mapping = TrueFakeMapping()
        self.slot_value_cheak = SlotValueCheck()
        self.map_config = self.lazy_map()
        self.map_slot_params_per = self.lazy_map()
        self.pre_mapping = {
            # 'zhibo', 'dianbo', 'huikan', 'mohu'
            'zhibo': 'live',
            'dianbo': 'video',
            'huikan': 'tvback',
            'zhiling': 'instruction',
            'mohu': 'unclear'
        }

    def lazy_map(self):
        return{
            'tvback': {'channelName': [self.turnfake_mapping.all_channel_name_mapping,
                                       self.turnfake_mapping.filtered_sen
                                       ],  # 过滤中央台和地方台
                       'channelNo': None,
                       'startDate': self.slot_value_cheak.start_date_check,
                       'startTime': self.slot_value_cheak.start_time_end_time_check,
                       'endTime': None,
                       'name': None
                       },
            'video': {'videoName': None,
                      'category': None,
                      'modifier': None,
                      'persons': None,
                      'area': None,
                      'season': None,
                      'episode': None,
                      'startyear': None,
                      'endyear': None
                      },
            'live': {'channelName': [self.turnfake_mapping.all_channel_name_mapping,
                                     self.turnfake_mapping.filtered_sen,
                                       ],
                     'channelNo': None
                     },
            'instruction': {'cmdValue': None,
                            'cmdParam': None
                            },
            'unclear': {'channelName': [self.turnfake_mapping.all_channel_name_mapping,
                                        self.turnfake_mapping.filtered_sen,
                                       ],
                        'channelNo': None,
                        'startDate': self.slot_value_cheak.start_date_check,
                        'startTime': self.slot_value_cheak.start_time_end_time_check,
                        'endTime': None,
                        'name': None,
                        'videoName': None,
                        'category': None,
                        'modifier': None,
                        'persons': None,
                        'area': None,
                        'season': None,
                        'episode': None,
                        'startyear': None,
                        'endyear': None,
                        'cmdValue': None,
                        'cmdParam': None
                        }  # 模糊包含了所有的槽位.
        }


# ss = SlotValueCheck()
# sss = ss.start_date_check(start_date=['1082年'])
# print(sss)
# ss = SlotValueCheck()
# print(ss.start_date_check(['我要看上周的湖南卫视']))
# # print('date_time:', ss.start_time_end_time_check(['我要看2017年的湖南卫视']))