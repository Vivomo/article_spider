import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def get_zhihu_xsrf(html):
    match_obj = re.search('name="_xsrf" value="([^"]+)"', html)
    if match_obj:
        return match_obj.group(1)
    else:
        return ""


def extract_num(text):
    # 从字符串中提取出数字
    match_re = re.search("\d+", text)
    if match_re:
        nums = int(match_re.group())
    else:
        nums = 0

    return nums

if __name__ == '__main__':
    print(get_md5('http://google.com'.encode('utf-8')))
