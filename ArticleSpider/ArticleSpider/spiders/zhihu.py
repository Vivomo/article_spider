# -*- coding: utf-8 -*-
from ArticleSpider.utils.common import get_zhihu_xsrf

import json
import re

import scrapy


class ZhihuSpider(scrapy.Spider):
    name = "zhihu"
    allowed_domains = ["www.zhihu.com"]
    start_urls = ['https://www.zhihu.com/']

    # question的第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    headers = {
        "HOST": "www.zhihu.com",
        "Referer": "https://www.zhizhu.com",
        'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        pass

    def start_requests(self):
        return [scrapy.Request('https://www.zhihu.com/#signin', headers=self.headers, callback=self.login_after_captcha)]

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

