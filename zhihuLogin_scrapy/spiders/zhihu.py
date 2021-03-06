# -*- coding: utf-8 -*-
import scrapy
from scrapy import FormRequest,Request
import json
import hmac
from hashlib import sha1
import time

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    captcha_url = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
    base_url = 'https://www.zhihu.com/signin'
    login_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'

    '''处理签名'''
    def get_signature(self, grantType, clientId, source, timestamp):
        #new(key,message,算法)
        hm = hmac.new(b'd1b964811afb40118a12068ff74a12f4', None, sha1)  
        '''添加加密的内容'''
        hm.update(str.encode(grantType))  
        hm.update(str.encode(clientId))
        hm.update(str.encode(source))
        hm.update(str.encode(timestamp))

        #返回加密后的散列值
        return str(hm.hexdigest())   

    def start_requests(self):

        #获取验证码状态
    	yield Request(self.captcha_url,meta={'cookiejar':1},callback=self.captcha_status_parse)  

    def captcha_status_parse(self,response):

    	grantType = 'password'
    	clientId = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    	source = 'com.zhihu.web'
        # 毫秒级时间戳 签名只按这个时间戳变化
    	timestamp = str(int(round(time.time() * 1000)))  

    	#print(response.text)

    	captcha=json.loads(response.text)
        #false没有验证码
    	print(captcha['show_captcha'])   

    	if not captcha['show_captcha']:
            signature=self.get_signature(grantType,clientId,source,timestamp)
            '''传递的参数'''
            data = {
    		"username":"+8613168802062",
    		"password":"ljy199400585756",
    		'captcha':"",
    		"client_id":clientId,
    		"grant_type":grantType,
    		"timestamp":timestamp,
    		"source":source,
    		"signature":signature,
    		"lang":"en",
    		"ref_source":"other_",
    		"utm_source":""
    	    }
            #登录界面
            yield Request(self.base_url,meta={'cookiejar':response.meta['cookiejar'],'data':data},callback=self.login_request)   

    	else:
            #分析验证码
            yield Request(self.captcha_url,method='PUT',meta={'cookiejar':response.meta['cookiejar']},callback=self.captcha_parse)   
    		
    def captcha_parse(self,response):

    	#组合验证码图片数据，写入本地，在本地中打开
    	captcha = json.loads(response.text)
    	img_data = captcha['img_base64']
    	img = 'data:image/jpg;base64,'+img_data
    	img = bytes(img,encoding='utf-8')
    	with open('cap.gif','wb') as file:
            file.write(img)

    	captcha = input('captcha:')
        #验证是否成功
    	yield FormRequest(self.captcha_url,formdata={'input_text':captcha},meta={'cookiejar':response.meta['cookiejar'],'cap':captcha},callback=self.captcha_res)   #post验证码，若成功才能登录

    def captcha_res(self,response):
    	captcha = json.loads(response.text)

    	flag = captcha['success']

    	if flag:
            grantType = 'password'
            clientId = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
            source = 'com.zhihu.web'
            timestamp = str(int(round(time.time() * 1000)))
            signature=self.get_signature(grantType,clientId,source,timestamp)
            data = {
    		"username":"+8613168802062",
    		"password":"ljy199400585756",
    		'captcha':response.meta['cap'],
    		"client_id":clientId,
    		"grant_type":grantType,
    		"timestamp":timestamp,
            "source":source,
            "signature":signature,
            "lang":"en",
            "ref_source":"other_",
            "utm_source":""
            }
            yield Request(self.base_url,meta={'cookiejar':response.meta['cookiejar'],'data':data},callback=self.login_request)

    def login_request(self,response):

    	print(response.meta['data'])
        #post表单
    	yield FormRequest(self.login_url,formdata=response.meta['data'],meta={'cookiejar':response.meta['cookiejar']},callback=self.parse)   

    def parse(self,response):
    	'''检测是否登录成功'''
    	url='https://www.zhihu.com/'
    	yield Request(url,meta={'cookiejar':response.meta['cookiejar']},callback=self.after_login)

    def after_login(self,response):
    	print(response.url)