# -*- coding: utf-8 -*-

from ArticleSpider.utils.common import get_zhihu_xsrf
from scrapy.loader import ItemLoader
from urllib import parse
from ArticleSpider.items import ZhihuQuestionItem, ZhihuAnswerItem

import json
import re
import datetime
import scrapy

# with open('./spiders/cookie.json') as cookie_file:
#     cookie_json = json.loads(cookie_file.read())
#     print(cookie_json)


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"
    # start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B*%5D.is_normal%2Cadmin_closed_comment%2Creward_info%2Cis_collapsed%2Cannotation_action%2Cannotation_detail%2Ccollapse_reason%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Ccreated_time%2Cupdated_time%2Creview_info%2Cquestion%2Cexcerpt%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B*%5D.mark_infos%5B*%5D.url%3Bdata%5B*%5D.author.follower_count%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&limit={1}&offset={2}"

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        """
        提取出html页面中的所有url 并跟踪这些url进行一步爬取
        如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.headers, meta={"id": match_obj.group(2)}, callback=self.parse_question)
            # else:
                # 如果不是question页面则直接进一步跟踪
                # yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的question item
        # wap
        question_id = int(response.meta['id'])

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_css("title", ".QuestionHeader-title::text")
        item_loader.add_css("content", ".QuestionHeader-content .RichText")
        item_loader.add_value("url", response.url)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeader-Comment .Button--plain::text")
        # item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
        item_loader.add_css("topics", ".TopicLink::text")

        question_item = item_loader.load_item()
        print(question_item)
        answer_url = self.start_answer_url.format(question_id, 20, 0)
        yield scrapy.Request(answer_url, headers=self.headers, cookies=cookie_json, callback=self.parse_answer)
        yield question_item
        # if "QuestionHeader-title" in response.text:
        #     # 处理新版本
        #     match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        #     question_id = int(match_obj.group(2))
        #
        #     item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        #     item_loader.add_css("title", ".QuestionHeader-title::text")
        #     item_loader.add_css("content", ".QuestionHeader-detail")
        #     item_loader.add_value("url", response.url)
        #     item_loader.add_value("zhihu_id", question_id)
        #     item_loader.add_css("answer_num", ".List-headerText span::text")
        #     item_loader.add_css("comments_num", ".QuestionHeader-actions button::text")
        #     item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
        #     item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
        #
        #     question_item = item_loader.load_item()
        # else:
        #     # 处理老版本页面的item提取
        #     match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        #     if match_obj:
        #         question_id = int(match_obj.group(2))
        #
        #     item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        #     # item_loader.add_css("title", ".zh-question-title h2 a::text")
        #     item_loader.add_xpath("title",
        #                           "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
        #     item_loader.add_css("content", "#zh-question-detail")
        #     item_loader.add_value("url", response.url)
        #     item_loader.add_value("zhihu_id", question_id)
        #     item_loader.add_css("answer_num", "#zh-question-answer-num::text")
        #     item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
        #     # item_loader.add_css("watch_user_num", "#zh-question-side-header-wrap::text")
        #     item_loader.add_xpath("watch_user_num",
        #                           "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
        #     item_loader.add_css("topics", ".zm-tag-editor-labels a::text")
        #
        #     question_item = item_loader.load_item()

    def parse_answer(self, response):
        # 处理question的answer
        ans_json = json.loads(response.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()

            yield answer_item

        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    def start_requests(self):
        # return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login_after_captcha)]
        return [scrapy.Request('https://www.zhihu.com', headers=self.headers)]

    def login(self, response):
        response_text = response.text
        match_obj = re.search('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ''
        if match_obj:
            xsrf = (match_obj.group(1))

        if xsrf:
            post_url = "https://www.zhihu.com/login/email"
            post_data = {
                "_xsrf": xsrf,
                "phone_num": "",
                "password": "",
                "captcha": ""
            }

            import time
            t = str(int(time.time() * 1000))
            captcha_url = "https://www.zhihu.com/captcha.gif?r={0}&type=login".format(t)
            yield scrapy.Request(captcha_url, headers=self.headers, meta={"post_data": post_data},
                                 callback=self.login_after_captcha)

    def login_after_captcha(self, response):
        # with open("captcha.jpg", "wb") as f:
        #     f.write(response.body)
        #     f.close()
        #
        # from PIL import Image
        # try:
        #     im = Image.open('captcha.jpg')
        #     im.show()
        #     im.close()
        # except:
        #     pass
        #
        # captcha = input("输入验证码\n>")

        # post_data = response.meta.get("post_data", {})
        # post_url = "https://www.zhihu.com/login/phone_num"
        with open(r'G:\code\article_spider\article_spider\ArticleSpider\ArticleSpider\utils\password.txt') as file:
            email, password = file.read().strip().split('|')
        xsrf = get_zhihu_xsrf(response.text)
        print('xsrf', xsrf)
        post_url = "https://www.zhihu.com/login/email"
        post_data = {
            'email': email,
            'password': password,
            '_xsrf': xsrf
        }
        # post_data["captcha"] = captcha
        return [scrapy.FormRequest(
            url=post_url,
            formdata=post_data,
            headers=self.headers,
            callback=self.check_login
        )]

    def check_login(self, response):
        # 验证服务器的返回数据判断是否成功
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)

