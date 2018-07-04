import logging
from io import BytesIO

import requests
import scrapy
from PIL import Image
from scrapy import Request

logger=logging.getLogger(__name__)
class douban(scrapy.Spider):
    name='douban'
    allowed_domains=['douban.com']

    #重写了start_requests方法
    def start_requests(self):
        start_url='https://accounts.douban.com/login'
        #加上meta={"cookiejar":1}后，若是原先已登录成功则不在需要验证码
        return [Request(start_url, meta={"cookiejar":1},  callback=self.post_login)] 

    def post_login(self, response):  
        formdata={
            'sorce':'index_nav',
            'redir':'https://www.douban.com/',
            'form_email':'1973132883@qq.com',
            'form_password':'zh13102030032',
            'captcha-solution':None,
            'captcha-id':None,
            'login':'登录',
            }
        #采用lxml+xpath时.extract_first()不需要加
        formdata['captcha-id'] = response.xpath('//input[@name="captcha-id"]/@value').extract_first()
        captcha_image_url = response.xpath('//img[@id="captcha_image"]/@src').extract_first()
        if captcha_image_url is None:
            logger.info('登录时无验证码')
        else:
            logger.info('登录时有验证码')
            r=requests.get(captcha_image_url).content
            img=Image.open(BytesIO(r))
            img.show()
            #手动输入验证码
            formdata['captcha-solution']=input('请输入验证码：')
        logger.info('登录中。。。')
        return scrapy.FormRequest.from_response(response,formdata=formdata,callback=self.after_login)

    def after_login(self, response):  
        #验证登录是否成功
        account = response.xpath('//a[@class="bn-more"]/span/text()').extract_first()
        if account is None:
            logger.info("登录失败")
        else:
            logger.info("登录成功,当前账户为 %s" %account)