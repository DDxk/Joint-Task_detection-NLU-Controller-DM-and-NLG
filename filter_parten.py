import re
from slot_value_check.slot_value_check import SlotValueCheck
from slot_value_check.true_fake_mapping import TrueFakeMapping


class FilterRule:
    def __init__(self):
        self.rule = {
            'rule1': r'[a-zA-Z]+',  # 匹配所由得英文串 如，我想看CCTV一台昨天的焦点访谈----->['CCTV']
            # 匹配所由得数字和时间如，'我想看2018年晚上6点半和6:45分的新闻联播'------> ['2018', '6', '6:45']
            # 'rule2': r'[0-9]+[:]?[0-9]*',  # 6:30的新闻联播2018年的  6:30 2018
            'rule2': r'[0-9]+[:]?[0-9]+',  # 6:30的新闻联播2018年的  6:30
            # 'rule3': r'\d+',  # 6:30的新闻联播2018年的  2018
        }
        self.cctv_filter = TrueFakeMapping()

    def cut_sentence(self, sentence):
        """
         通过正则取切分句子，粒度更大
        :param sentence: 待切分的句子
        :return: 切分后的句子
        """
        sentence = self.cctv_filter.province_channel_fake_check(sentence)  # 频道别名的替换，如，芒果台------>湖南卫视
        sentence = SlotValueCheck.start_channelname_mapping(sentence)  # 央视频道的转换产生CCTV
        print('new sentence2:', sentence)
        sentence = SlotValueCheck.year_time_checking(sentence)  # 对年份和时间的过滤
        # sentence = self.cctv_filter.filtered_sen(sentence)  # 具体频道的转换
        print('new sentence3:', sentence)

        elements = []
        for cur_rule in self.rule.values():
            elements.extend(re.findall(cur_rule, sentence))

        # 寻找切分出来的子串在原串中的位置
        margin = []
        if len(elements) > 0:
            indexs = {}
            for ind, cur_elem in enumerate(elements):
                indexs[(re.search(cur_elem, sentence).span())] = ind
            indexs = sorted(zip(indexs.keys(), indexs.values()), reverse=False)  # 我想看2018年晚上6点半和6:45分的cctv新闻联播
            char_index = 0
            index_sle = 0
            while char_index < len(sentence):
                while index_sle < len(indexs):
                    if char_index < indexs[index_sle][0][0]:
                        margin.append(sentence[char_index])
                        char_index += 1
                    else:
                        margin.append(elements[indexs[index_sle][1]])
                        char_index = indexs[index_sle][0][1]
                        index_sle += 1
                        break
                if index_sle == len(indexs):
                    break
            latested = indexs[-1][0][1]
            while latested < len(sentence):
                margin.append(sentence[latested])
                latested += 1
        else:
            latested = 0
            while latested < len(sentence):
                margin.append(sentence[latested])
                latested += 1
        print('返回的 margin:', margin)
        return margin

