# article_spider
文章爬虫练习

### 问题
> pip install scrapy -> Microsoft Visual C++ 14.0 is required

解决方案
http://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted 下载twisted对应版本的whl文件（如我的Twisted‑17.5.0‑cp36‑cp36m‑win_amd64.whl），cp后面是python版本，amd64代表64位，运行命令：
pip install C:\Users\CR\Downloads\Twisted-17.5.0-cp36-cp36m-win_amd64.whl
其中install后面为下载的whl文件的完整路径名
安装完成后，再次运行：
pip install Scrapy
即可成功。
> scrapy crawl (projectName) -> error
windows 系统才有的错误
解决方法 pip install pypiwin32


### scrapy 常用命令
> scrapy startproject (projectName) -> create a scrapy project
> scrapy genspider example example.com -> create a spider template for a site
> scrapy crawl (projectName) -> run project
> scrapy shell (url) -> debug url