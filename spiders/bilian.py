# -*- coding: utf-8 -*-
import scrapy
import re
from copy import deepcopy


class BilianSpider(scrapy.Spider):
    name = 'bilian'
    #注意此处
    allowed_domains = ['ebnew.com','ss.ebnew.com']
    keyword_s = [
        '路由器','变压器','电容器','单片机','机器手'
    ]
    #存储的格式
    sql_data = dict(
        projectcode='' ,#项目编号
        web='',#信息来源网站（例如：必联网）
        keyword='',#关键字
        detail_url='',#招标详细页网址
        title='',#第三方网站发布标题
        toptype='',#信息类型
        province='',#归属省份
        product='',#产品范畴
        industry='',#归属行业
        tendering_manner='',#招标方式
        publicity_date='',#招标公示日期
        expiry_date='', #招标截止时间
    )
    # #form表单 数据格式
    form_data = dict(
        infoClassCodes='',
        rangeType='',
        projectType='bid',
        fundSourceCodes='',
        dateType='',
        startDateCode='',
        endDateCode='',
        normIndustry='',
        normIndustryName='',
        zone='',
        zoneName='',
        zoneText='',
        key='',
        pubDateType='',
        pubDateBegin='',
        pubDateEnd='',
        sortMethod='timeDesc',
        orgName='',
        currentPage=''
    )

    #可跳过allowed_domains，请求其他页面
    def start_requests(self):
        for keyword in self.keyword_s:
            form_data = deepcopy(self.form_data)
            form_data['key'] = keyword
            form_data['currentPage'] = '1'
            request = scrapy.FormRequest(
                url = 'http://ss.ebnew.com/tradingSearch/index.htm',
                formdata = form_data,
                callback = self.parse_start
            )
            #将form_data对象保存到meta中
            request.meta['form_data'] = form_data

            yield request

        # yield scrapy.Request(
        #     url = 'http://www.ebnew.com/businessShow/642129477.html',
        #     callback = self.parse_page2
        # )
        # form_data = self.form_data
        # form_data['key'] = '路由器'
        # form_data['currentPage'] = '2'
        # yield scrapy.FormRequest(
        #     url = 'http://ss.ebnew.com/tradingSearch/index.htm',
        #     formdata = form_data ,
        #     callback = self.parse_page1,
        # )

    def parse_start(self, response):
        a_text_s = response.xpath('//form[@id = "pagerSubmitForm"]/a/text()').extract()
        page_max = max(
            [int(a_text) for a_text in a_text_s if re.match('\d+',a_text)]
        )

        self.parse_page1(response)
        # #
        #因a_text_s请求的就是页面1  所有从第二页开始请求
        for page in range(2,page_max+1):
            form_data = deepcopy(response.meta['form_data'])
            form_data['currentPage'] = str(page)
            # print(form_data['currentPage'])
            request = scrapy.FormRequest(
                url = 'http://ss.ebnew.com/tradingSearch/index.htm',
                formdata = form_data,
                callback = self.parse_page1
            )
            request.meta['form_data'] = form_data
            yield request
    def parse_page1(self,response):
        form_data = response.meta['form_data']
        keyword = form_data.get('key')
        content_x_s = response.xpath('//div[@class="ebnew-content-list"]/div')
        for content_x in content_x_s:
            sql_data = deepcopy(self.sql_data)
            #信息类型  公告/结果
            sql_data['toptype'] = content_x.xpath('./div[1]/i[1]/text()').extract_first()
            #标头
            sql_data['title'] = content_x.xpath('./div[1]/a/text()').extract_first()
            #发布日期
            sql_data['publicity_date'] = content_x.xpath('./div[1]/i[2]/text()').extract_first()
            if sql_data['publicity_date']:
                #这个正则表达式的意思为 除了0-9和- (其中的\为了防止转义) 其余转换为空字符
                sql_data['publicity_date'] = re.sub('[^0-9\-]','',sql_data['publicity_date'])
            #  招标方式
            sql_data['tendering_manner'] = content_x.xpath('./div[2]/div[1]/p[1]/span[2]/text()').extract_first()
            #招标产品
            sql_data['product'] = content_x.xpath('./div[2]/div[1]/p[2]/span[2]/text()').extract_first()
            #招标截止时间
            sql_data['expiry_date'] = content_x.xpath('./div[2]/div[2]/p[1]/span[2]/text()').extract_first()
            #招标地区
            sql_data['province'] = content_x.xpath('./div[2]/div[2]/p[2]/span[2]/text()').extract_first()
            #招标详情页 地址
            sql_data['detail_url'] = content_x.xpath('./div[1]/a/@href').extract_first()
            #关键词
            sql_data['keyword'] = keyword
            #来源
            sql_data['web'] = '必联网'
            request = scrapy.Request(
                url = sql_data['detail_url'],
                callback = self.parse_page2
            )
            request.meta['sql_data'] = sql_data

            yield request
    def parse_page2(self,response):
        sql_data = response.meta['sql_data']

        # li_x_s = response.xpath('//div[@class="position-relative"]/ul/li')

        #项目编号
        sql_data['projectcode'] = response.xpath('//div[@class="position-relative"]/ul/li[1]/span[2]/text()').extract_first()
        if not sql_data['projectcode']:
            #项目编号后为中文或英文冒号或没有冒号 也有可能有多个空格
            #项目编号可能为字母数字下划线和横线组成 长度猜一下大概10-80
            projectcode_fill = re.findall('项目编号[:：]{0,1}\s{0,3}([a-zA-Z0-9\-_]{10,80})',response.body.decode('utf-8'))
            sql_data['projectcode'] = projectcode_fill[0] if sql_data['projectcode'] else ""
        #所属行业
        sql_data['industry'] = response.xpath('//div[@class="position-relative"]/ul/li[8]/span[2]/text()').extract_first()

        yield sql_data

