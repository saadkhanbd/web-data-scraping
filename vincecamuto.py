#!/usr/bin/python print 'Set-Cookie:UserID="";'

'''
Saad Khan, August 14, 2014
'''

# coding: utf-8
from __future__ import absolute_import
import os
import json
import re
import string
import urlparse
import urllib
import traceback
import copy
import StringIO
import csv
import base64
import time
import pprint
import PyV8
import random

from scrapy.selector import Selector
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.contrib.spiders import Rule
from scrapyproduct.spiderlib import SSBaseSpider
from scrapyproduct.items import ProductItem, SizeItem
from scrapy.http.request import Request
from scrapy.http import FormRequest
from scrapy.http import Response
from scrapy import log
import scrapy.log
from scrapy.http.cookies import CookieJar

from scrapyproduct import toolbox

class VincecamutoSpider(SSBaseSpider):
    name = 'vincecamuto'
    long_name = "vincecamuto"
    base_url = "http://www.vincecamuto.com"
    spider_args = ""
    max_stock_level = 999    

    def start_requests(self):
        
        # delivery regions - adpated from Robert's code snippet
        # the delivery regions need to be extended by country codes - will be done later?????
        deliveryregions = {
                            # Name: (currency, [country_codes], thousands_separator)        
                            'US' : ('USD', ['us'], ","),
                            'UK' : ('GBP', ['gb'], ","),
                            'CA' : ('CAD', ['ca'], ","),
                            'ES' : ('EUR', ['es'], ","),
                            'DE' : ('EUR', ['de'], ","),
                            'BD' : ('USD', ['bd'], ","),
        }

        # language codes adapted from Roberts's code snippet
        languages = {
                            'us': 'en',
                            'gb': 'en', 
                            'ca': 'en', 
                            'es': 'en', 
                            'de': 'en', 
                            'bd': 'en',
        }
                
        crawling_regions = ['US']
                
        self.log(u'--- starting spider', scrapy.log.DEBUG)
        for CR in crawling_regions:

            # 5 countries as TESTING case
            if CR == 'US':
                
                country_code = deliveryregions[CR][1][0] # first element of list
                language_code = languages[country_code]
                currency = deliveryregions[CR][0]

                country_url = self.base_url + '/homepage'
                
                #create database entry, if not yet in database
                #createDeliveryRegion(webshop_code, region_code, currency, country_codes, country_names=[], region_url=None, spider=None)

                # register deliveryregion
                toolbox.register_deliveryregion(self, country_code, currency, deliveryregions[CR][1], country_url)

                # register warehouselocation since max_stock_level > 0
                toolbox.register_warehouselocation(self, country_code)
                
                # construct meta dictionary
                base_meta = dict()
                base_meta['deliveryregion'] = CR
                base_meta['language_code'] = language_code
                base_meta['country_code'] = country_code
                base_meta['currency'] = currency                    
                base_meta['dont_merge_cookies'] = True
                                        
                # register deliveryregion
                toolbox.register_deliveryregion(self, country_code, currency, deliveryregions[CR][1], country_url)

                # register warehouselocation since max_stock_level > 0
                toolbox.register_warehouselocation(self, country_code)

                # process cookies, request
                req = Request(  url = country_url,
                                meta = base_meta,
                                callback = self.parse_country_home_page
                )
                yield req        

    def parse_country_home_page(self, response):

        """
        Extract the main menu/category links from the home page, 
        """
 
        # main category list
        main_cats = ["shoes", "handbags", "clothing", "watches", "accessories", "fragrances", "mens", "sale"]
        #main_cats = ["sale"]
        
        # extract and set base url
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'
                        
        # extract main menu nodes
        sel = Selector(response)        
        lis = sel.xpath("//div[@class='row']/nav/ul/li/a")
        self.log(u'--- # main menus =' + str(len(lis)) + ', url=' + base_url, scrapy.log.DEBUG)

        # process main menu nodes
        for li in lis:
            try:
                # main categories:
                cat = li.xpath("text()").extract()[0].strip().lower()
                if any(cat in c for c in main_cats):
                    #print '---cat=', cat
                    caturl = li.xpath("@href").extract()[0]
                    meta = copy.deepcopy(response.meta)
                    meta["category"] = []                               
                    meta["category"].append(cat)

                    # process cookies, request
                    cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                    cookieJar.extract_cookies(response, response.request)
                    meta['cookie_jar'] = cookieJar

                    #cookies = {"crossSiteTransfer":"19159"},
                    req = Request(  url=  caturl,
                                    meta= meta,
                                    callback=self.parse_sub_cats
                    )
                    cookieJar.add_cookie_header(req)    # apply Set-Cookie
                    #if 'fragrance' in cat:             # ---for TESTING ONLY---
                    #if 'shoes' in cat:                 # ---for TESTING ONLY---
                    #if 'handbags' in cat:              # ---for TESTING ONLY---
                    #if 'shoes' in cat:                 # ---for TESTING ONLY---
                    #if 'sale' in cat:                  # ---for TESTING ONLY---
                    #if  'shoes'in cat or 'sale'in cat:  # ---for TESTING ONLY---
                    yield req

            # li may be empty or may not contain category info
            except:
                pass
                
    # parse 
    def parse_sub_cats(self, response):

        '''
        Parse the sub cats
        '''
                  
        # sub category list
        sub_cats = ["categories", "special sizes", "precious jewelry", "apparel", "shoes", "jewelry & watches", "accessories", "luggage & travel", "men's grooming", "kids", "baby"]
        sub_cats_all = True
        
        #extract and set base url
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'

        # process response
        sel = Selector(response)

        # extract current cat
        meta = copy.deepcopy(response.meta)
        captured_cat_names = meta["category"]
        # parse cats to determine the target cat
        target_cat = None
        cats = sel.xpath("//div[@class='row']/nav/ul/li")
        for cat in cats:
            catname = cat.xpath("a/text()").extract()[0].strip().lower()
            for captured_cat_name in captured_cat_names:
                if catname in captured_cat_name:
                    target_cat = cat
                    break
            if target_cat:
                break

        # if target cat found, then process
        if target_cat:
            scats = target_cat.xpath('div/div/ul/li[position() > 1]/a')
            self.log(u'---s cats =' + str(len(scats)), scrapy.log.DEBUG)
        
            # visit the cat page to yield related sub cat
            if scats:
                for scat in scats:               
                    # extract s cat, url
                    scatname = scat.xpath('text()').extract()[0].strip().lower()
                    scaturl = scat.xpath('@href').extract()[0]
                    self.log(u'--- s cat name=' + scatname +  ", url=" + scaturl, scrapy.log.DEBUG)
                    
                    meta = copy.deepcopy(response.meta)
                    meta["category"].append(scatname)
                        
                    # process cookies, request
                    cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                    cookieJar.extract_cookies(response, response.request)
                    meta['cookie_jar'] = cookieJar

                    req = Request(  url = scaturl,
                                    meta = meta,
                                    callback = self.parse_pager
                    )
                    cookieJar.add_cookie_header(req)    # apply Set-Cookie
                        
                    #if 'socks' in scatname:            # ---for TESTING ONLY---
                    #if 'boots' in scatname:            # ---for TESTING ONLY---
                    #if 'denim' in scatname:            # ---for TESTING ONLY---
                    #if 'for him' in scatname:          # ---for TESTING ONLY---
                    #if 'two by vince' in scatname:     # ---for TESTING ONLY---
                    #if 'flats' in scatname:            # ---for TESTING ONLY---
                    #if 'satchels' in scatname:         # ---for TESTING ONLY---
                    #if 'heels' in scatname:            # ---for TESTING ONLY---
                    yield req
                            
            # NO s cats, so        
            else:
                #print '--- no s cat'

                meta = copy.deepcopy(response.meta)
                # process cookies, request
                cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                cookieJar.extract_cookies(response, response.request)
                meta['cookie_jar'] = cookieJar
            
                req = Request(  url= response.url,
                                meta= meta,
                                dont_filter = True,
                                callback = self.parse_pager
                )
                cookieJar.add_cookie_header(req)    # apply Set-Cookie
                yield req
                
        else:
            print '---no target cat'

    def parse_pager(self, response):
        
        '''
        Extract pagination info per page product list as follows:

            Check first whether the response contains View All pager

            if yes,
                extract view all page url,
                construct AJAX form request with following parameters: format, size
            else
                no pagination
                contruct NORMAL request
                    
        '''
        
        #extract and set base url
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'
        
        # process response
        sel = Selector(response)

        # init layout
        pagination_layout = ''
        
        # extract display items related info
        totalpages = 1
        itemscount = 1
        viewall_url = ''
        
        # detect pagination Layout
        pager = sel.xpath('//div[@class="search-result-options"]/div/a')
        #print '---pager=', str(pager.extract())
        if pager:            
            pagertext = pager.xpath('text()').extract()[0].lower()
            #print '---pager=', str(pagertext)

            if 'view all' in pagertext:
                viewall_url = pager.xpath('@href').extract()[0]
                #print '---view all url=', viewall_url

                viewall_url_parts = viewall_url.split('?')
                viewall_url_base = viewall_url_parts[0]
                viewall_sz_info = viewall_url_parts[1]
                size = viewall_sz_info.split('=')[1]

                #print '---view all base url=', viewall_url_base                
                meta = copy.deepcopy(response.meta)
                
                # process cookies, request
                cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                cookieJar.extract_cookies(response, response.request)
                meta['cookie_jar'] = cookieJar

                # contruct the form request  1              
                req = FormRequest(  url = viewall_url,
                                    method = 'GET',
                                    formdata = {'format': 'ajax'},
                                    meta = meta,                                                        
                                    dont_filter = True,
                                    callback = self.parse_product_list_HTML
                )
                cookieJar.add_cookie_header(req)    # apply Set-Cookie
                yield req
           
        # no pagination - single page or items <= 12  
        else:
            
            #print '---no pagination='
            # re-visit the current page
            meta = copy.deepcopy(response.meta)
                
            # process cookies, request
            cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
            cookieJar.extract_cookies(response, response.request)
            meta['cookie_jar'] = cookieJar
            req = Request(  url = response.url,
                            meta = meta,                                                         
                            dont_filter = True,                                                         
                            callback = self.parse_product_list_HTML
            )
            cookieJar.add_cookie_header(req)    # apply Set-Cookie
            yield req
 

    def parse_product_list_HTML(self, response):
        """
        Extract a set of list of product from a terminal product list page.

            Each product entry may contain multiple product info, i.e., product variations
            The product variation links are mostly AJAX controlled.
            So the parse product variations list AJAX function is called            
        
        """

        #extract and set base url
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'

        # handle slelctor
        sel = Selector(response)

        # The 1st one is for ALL OTHER products
        #prods = sel.xpath('//ul[@id="search-result-items"]/li[@class="grid-tile new-row"  or @class="grid-tile"]')
        prods = sel.xpath('//div[@class="product-info"]/div[@class="product-name"]/a')
        #print '--- # of HTML prods =', len(prods)

        # STANDARD product-list format 
        if prods:
            i = 0
            for prod in prods: 
                prd_url = prod.xpath('@href').extract()[0]
                #print '---prod url=',prd_url 
         
                meta = copy.deepcopy(response.meta)
                
                # process cookies, request
                cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                cookieJar.extract_cookies(response, response.request)
                meta['cookie_jar'] = cookieJar

                req = Request(  url = prd_url,
                                meta = meta,
                                dont_filter = True,                                                         
                                callback = self.parse_product_variation_list_AJAX
                )
                cookieJar.add_cookie_header(req)        # apply Set-Cookie                    
                #if 'franka' in prd_url.lower():        #i == 0:
                #if 'kathee' in prd_url.lower():          #i == 0:
                #if 'urban-safari-jacket' in prd_url.lower():          #i == 0:
                #if 'fernanda' in prd_url.lower():          #i == 0:
                #if 'vc-fenette2' in prd_url.lower():          #i == 0:
                yield req                    
                i += 1
        
    def parse_product_variation_list_AJAX(self, response):
        
        """
        Extract a set of list of product info/variations from a terminal product list page.

        The list contains TWO types of links related to product info/variations:

            1.  Default page link without color material data - which is called as
                a normal request
                
            2.  More page links with color material data - these links are called as
                AJAX form GET request with following parameters: quantity

            
        """

        #extract and set base url
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'

        # handle slelctor
        sel = Selector(response)
        dontfilter = False       # default value for filtering duplicates                                                         

        # The 1st one is for ALL OTHER products
        prods = sel.xpath('//div[@class="product-variations"]/ul/li[1]/div[2]/ul/li')
        #print '--- # of AJAX variation prods =', len(prods)

        # STANDARD product-list format 
        if prods:

            i = 0
            for prod in prods:                
                variation_url = prod.xpath('a/@href').extract()[0]
                variation_color = prod.xpath('a/@title').extract()[0]
                #print '---prod url=',prd_url 
                meta = copy.deepcopy(response.meta)
                    
                # extract cat from bread crumb
                cats = meta['category']
                    
                # loop until SALE is found
                for cat in cats:
                    if 'sale' in cat:
                        dontfilter = True       # for sale item donot filter                                                         
                        breadcrumbs = sel.xpath('//div[@class="breadcrumb clearfix"]/a')
                        if breadcrumbs:
                            for breadcrumb in breadcrumbs:
                                scat = breadcrumb.xpath('text()').extract()[0].strip().lower()
                                meta["category"].append(scat)
                        break
                
                # process cookies, request
                cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                cookieJar.extract_cookies(response, response.request)
                meta['cookie_jar'] = cookieJar
                    
                # for the FIRST link, visit the current url
                if i == 0:
                    variation_url = response.url

                # store url in meta, and construct the form request
                meta['variation_url'] = variation_url
                meta['variation_color'] = variation_color
                req = FormRequest(  url = variation_url,
                                    method = 'GET',
                                    formdata = {'quantity': '1', 'format': 'ajax'},
                                    meta = meta,
                                    dont_filter = True,                                                                                             
                                    callback = self.parse_image_code    #self.parse_product_page
                )
                cookieJar.add_cookie_header(req)        # apply Set-Cookie
                yield req                                     
                i += 1
 
    def parse_image_code(self, response):

        # get img base code & img base code url
        #code_url = 'http://s7d9.scene7.com/is/image/VinceCamuto/KEVIADKLPNA060_SET?'
        img_base_code = self.get_img_base_code(response)
        img_code_url_base = 'http://s7d9.scene7.com/is/image/VinceCamuto/' + img_base_code +'_SET'  +'?'
        
        # create current time in mili second
        currtime = int(round(time.time() * 1000))         # milisecond
        num2= currtime - 30000
        num1 = random.randrange(18300000000000000000, 18309999999999000000)

        callback_param = 'jQuery' + str(num1) +'_' + str(num2)
        req_param = 'imageset,json'
        _param= str(currtime)
        
        meta = copy.deepcopy(response.meta)                    

        #code_url = 'http://s7d9.scebe7.com/is/image/VinceCamuto/KEVIABN001_SET?
        #callback=jQuery183018008439484927896_1409897367682
        #req=imageset,json
        #_=1409897404976'
        
        req = Request(  url = img_code_url_base + 'callback=jQuery&req=imageset,json&=_'+ str(num2),
                        meta = meta,
                        callback = self.parse_product_variation_AJAX
        )
        yield req

    def parse_product_variation_AJAX(self, response):

        # extract image codes
        img_codes_str = response.body
        img_codes_str = img_codes_str[:-1]
        img_codes_str = img_codes_str.split(":")[1]
        img_codes = img_codes_str.split(';')

        # prepare img code data
        img_codes_data = ''
        for i in range(1, len(img_codes)):
            img_code = img_codes[i].split(',')[0]
            img_code = img_code.replace('VinceCamuto/', '').replace('"}', '')
            img_codes_data += img_code + ','
        
        meta = copy.deepcopy(response.meta)
        variation_url = meta['variation_url']

        cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
        cookieJar.extract_cookies(response, response.request)
        meta['img_code_data'] = img_codes_data        
        meta['cookie_jar'] = cookieJar        
        
        req = FormRequest(  url = variation_url,
                            method = 'GET',
                            formdata = {'quantity': '1', 'format': 'ajax'},
                            meta = meta,
                            dont_filter = True,                                                         
                            callback = self.parse_product_sizes_AJAX
        )
        cookieJar.add_cookie_header(req)        # apply Set-Cookie                    
        yield req

    def parse_product_sizes_AJAX(self, response):
        
        # handle selector
        sel = Selector(response)
        meta = copy.deepcopy(response.meta)

        # set cookies
        cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
        cookieJar.extract_cookies(response, response.request)
        meta['cookie_jar'] = cookieJar        

        # set default url
        sz_url = meta['variation_url']          

        # get price range text, if any
        price_str = ''
        spnode = sel.xpath('//div[@class="product-price"]/span[@class="price-standard"]')
        if not spnode:
            spnode = sel.xpath('//div[@class="product-price"]/div')
        if spnode:
            price_str = spnode.xpath('text()').extract()[0]

        # check whether the price text is a range
        # if yes, set the request with size url
        if '-' in price_str:
            # if range price, then extract sz url to visit a size page
            # get any one size link
            #size_nodes = sel.xpath('//ul[@class="swatches clearfix size"]/li[@class="emptyswatch"]/a')
            size_nodes = sel.xpath('//ul[@class="swatches clearfix size"]/li[@class="emptyswatch" or @class="selected"]/a')
            for sz in size_nodes:
                sz_url = sz.xpath('@href').extract()[0]
                break            
        
            req = Request(  url = sz_url,
                            meta = meta,
                            dont_filter = True,                                                         
                            callback = self.parse_product_page
            )

        req = FormRequest(  url = sz_url,
                            formdata = {'quantity': '1', 'format': 'ajax'},
                            meta = meta,
                            dont_filter = True,                                                         
                            callback = self.parse_product_page
        )            
        cookieJar.add_cookie_header(req)        # apply Set-Cookie    
        yield req


    def get_url(self, response):                 

        meta = copy.deepcopy(response.meta)
        variation_url = meta['variation_url']
        return variation_url

    def get_brand(self, response):                 

        sel = Selector(response)
        brand =''
        try:
            brand = sel.xpath('//div[1]').extract()
            brand = str(brand).split('brandIcon')[1]
            brand = str(brand).split('">')[0]
            brand = brand.replace('_', ' ')
            brand = brand.lower()
            brand = string.capwords(brand)           
            #print '---', brand
            
        except:
            pass            
        return brand
        
    def get_category_breadcrumb(self, response):       
        """
        Extract category info from the response.meta
        """
        '''
        if "category" in response.meta:
            category = copy.deepcopy(response.meta["category"])
            return category
        else:
            return ""
            
        '''
        
        sel = Selector(response)
        category = []
        breadcrumbs = sel.xpath('//div[@class="breadcrumb clearfix"]/a')
        if breadcrumbs:
            for breadcrumb in breadcrumbs:
                cat = breadcrumb.xpath('text()').extract()[0].strip().lower()
                print'---cat=', cat
                category.append(cat)
        else:
                category.append('none')
            
        return category        

    def get_category(self, response):       # done
        
        """
        Extract category info from the response.meta
        """
        
        if "category" in response.meta:
            category = copy.deepcopy(response.meta["category"])

            '''
            # check whether category contains 'Sale' data
            # if yes, then retrieve actual category from breadcrumb
            for info in category:
                if "sale" in info:
                    cat = self.get_category_breadcrumb(response)
                    return cat
            '''
            # else return the normal category
            return category
        else:
            return ""

    def get_id(self, response):                 

        '''
            To obtainIDs use following tag syntax:

            //input[starts-with(@id,"prod")]/@value
            
        '''

        sel = Selector(response)
        pid =''
        raw_pid = sel.xpath('//div[@class="product-variations"]/ul/li[1]/div[1]/text()').extract()[0]
        
        if raw_pid:
             pid = raw_pid.split(':')[1].strip()            

        return pid

    def get_gender(self, category): # will fix later
        gender = ""
        level = 0
        for info in category:
            if "mens" in info and level==0:
                gender = "man"
                break
            elif "him" in info and level==1:
                gender = "man"
                break
            level += 1

        if not gender:
            gender = "woman"
            
        return gender
                     
    def get_title(self, response):
        
        title = ''
        sel = Selector(response)
        tnode = sel.xpath('//h1')

        if tnode:
            title = tnode.xpath('text()').extract()[0]
        else:
            title = 'none'
        
        return title

    def get_desc(self, response):
        
        sel = Selector(response)
        #dnode = sel.xpath("//div[@class='product-tabs']/div/p")

        #if not dnode:
        dnode = sel.xpath("//div[@class='product-tabs']/div")
            
        if dnode:
            #desc = dnode.xpath("text()").extract()[0]
            rawdesc = dnode.extract()
            desc = str(rawdesc).split('tab-content selected">')[1]
            desc = desc.split('</div>')[0]
            desc = desc.replace('\\n', '')
            desc = desc.replace('\\t', '')
            desc = desc.replace('\\r', '')
            
            if desc:
                return str(desc)
            else:
                return 'none'
            
        return 'none'

    def get_price_standard(self, response):

        standard_price = ''
        
        sel = Selector(response)
        # try with standard price
        spnode = sel.xpath('//div[@class="product-price"]/span[@class="price-standard"]')
        if not spnode:
            spnode = sel.xpath('//div[@class="product-price"]/div')

        if spnode:
            standard_price_str = spnode.xpath('text()').extract()[0]
            #print '--- s price=', standard_price
            standard_price = re.findall(r'\d+[,|\.]?\d*', standard_price_str)            
            return standard_price

        #print '---=NO STANDARD PRICE'
        return standard_price

    def get_price_sales(self, response):

        sales_price = ''
        
        sel = Selector(response)
        # try with standard price
        spnode = sel.xpath('//div[@class="product-price"]/span[@class="price-sales"]')
        #print '---test price=', str(spnode)
        if not spnode:
            spnode = sel.xpath('//div[@class="product-price"]/div')
            
        if spnode:
            sales_price_str = spnode.xpath('text()').extract()[0]
            sales_price = re.findall(r'\d+[,|\.]?\d*', sales_price_str)            
            return sales_price

        return sales_price
                
    def extract_images(self, response):     
        
        sel = Selector(response)
        image_urls = []
                
        # the server retruns a default img links
        # the is same for all product variations of a product
        # this makes direct extraction of images per product variations difficult

        # This is managed by finding the codes of images for a product variation, and then
        # correcting the default link with this codes.
        
        # Each product variation may contain 1, 2, 3 or more images. For a particular
        # product variation, each image has a code comprising.
        # For each image link, the code is extracted, and then it is combined with
        # generic link to obtain the correct image link.
        
        # The meanings of various codes are as follows:
        #
        #   img default code - the img base code of the FIRST of the default imge links
        #   img base code - the base image code of a specific product variation
        #   img sub code - the sub image code of an image of a specific product variation
        #

        # get image codes
        img_codes_data = copy.deepcopy(response.meta["img_code_data"])
        img_codes = img_codes_data.split(',')

        # extract base image link parts
        links = sel.xpath('//div[@class="product-primary-image"]/a/img')
        if not links:
            links = sel.xpath('//div[@class="carousel-inner"]/ul/li/a/img')
            #print '---img link=', str(links.extract())
             
        if links:
            for link in links:               
                # get the default image link - incorrect link
                default_img_link = link.xpath('@src').extract()[0]

                # get default part links, if image code do exist
                if img_codes_data: 
                    link_right = default_img_link.split('?')[1]
                    link_left = default_img_link.split('VinceCamuto')[0]
                    break
                else:
                    image_urls.append('http:' + default_img_link)
                    

        # loop over image codes to construct image links
        for img_code in img_codes:            
            # construct the link
            if img_code:
                img_link = link_left + 'VinceCamuto/' + img_code + '?' + link_right
                image_urls.append('http:' + img_link)
        
        # in case no image at ALL - TEST message
        if not image_urls:        
            print '---img not found'
            return 'no image'

        return image_urls

    def get_img_base_code(self, response):     
        
        sel = Selector(response)

        # xtract the base code for images for the current product variation
        img_link = sel.xpath('//div[@class="product-zoom-overlay"]/img/@src').extract()[0]
        link_left = img_link.split('?')[0]
        img_base_code = link_left.split('/')[-1]
        return img_base_code
            

    def extract_sizes(self, response):       # fixed
        
        '''
        size info are formed from product list based on a particular color-match        
        '''
        
        output = []

        sel = Selector(response)            
        #size_nodes = sel.xpath('//div[@class="product-variations"]/ul/li[2]/div[@class="value"]/ul/li[@class="emptyswatch"]/a')
        size_nodes = sel.xpath('//ul[@class="swatches clearfix size"]/li[@class="emptyswatch" or @class="selected"]/a')

        for size_node in size_nodes:
                
            size_obj = SizeItem()

            # process size id 
            sid = size_node.xpath('text()').extract()[0]
            if sid:
                size_obj['size_identifier'] = sid.strip()
            else:
                size_obj['size_identifier'] = ''

            # process size name 
            name = size_node.xpath('@title').extract()[0]
            if name:
                size_obj['size_name'] = name            
            else:
                size_obj['size_name'] = ''

            # process stock
            size_obj['stock'] = 1
            
            output.append(size_obj)

        # return the size info
        return output

    def sum_stock(self, sizes):      

        total_stock = 0
        for size in sizes:
            total_stock += size['stock']

        return total_stock
    
    def extract_color(self, response):

        '''
        color list is formed from product list constructed by
        parse_product_data. The color list comprises followings:

        '''
        
        color_val = ''
        sel = Selector(response)

        # color is retrieved in parse_product_variation_list_AJAX
        # and stord in meta
        variation_color = copy.deepcopy(response.meta["variation_color"])
        return variation_color

        '''
        #color = sel.xpath('//div[@class="product-variations"]/ul/li[1]/span/text()').extract()[0]
        color = sel.xpath('//div[@class="product-variations"]/ul/li[1]/div[2]/ul/li[@class="selected"]/a/@title').extract()[0]
        #color = sel.xpath('//div[@class="product-variations"]/ul/li[1]/div[2]/ul/li')
        if color:
            return color
            color_val = color.split(':')[1].strip()                                                                    
        return color_val
        '''

    # parse detail product page
    def parse_product_page(self, response):         # fixed

        """
        Parse the product detail page and yield the item,
        if the item full price text is null, then just return
        """

        try:                        
            # base item attributes setting
            base_i = ProductItem()
            base_i["description_text"] =  self.get_desc(response)
            base_i["url"] = self.get_url(response)
            base_i['referer_url'] = response.request.headers.get('Referer', None)
            base_i["language_code"] = response.meta["language_code"]
            base_i["country_code"] = response.meta["country_code"]

            # extract categories
            category_names = self.get_category(response)
            #print '---', category_names
            base_i['category_names'] = category_names           #[n['name'] for n in cats_js]
            base_i['category_identifiers'] = category_names     #[n['id'] for n in cats_js] # TODO: please change to actual identifiers (e.g. 'c390001')
            base_i['category_parents'] = toolbox.create_category_parents(base_i['category_identifiers'])
            base_i["gender_names"] = self.get_gender(category_names)
            
            base_i['update_details'] = True
            base_i['save_price'] = True
            base_i['add_category_and_gender'] = True
            base_i['image_urls'] = self.extract_images(response)
            base_i["brand"] = self.get_brand(response)
            
            base_i["title"] = self.get_title(response)
            #print '---title=', title
            standard_price = self.get_price_standard(response)
            sales_price = self.get_price_sales(response)
            if standard_price:
                base_i["old_price_text"] = standard_price
                base_i["new_price_text"] = sales_price
                base_i["full_price_text"] = standard_price
            else:
                base_i["old_price_text"] = sales_price
                base_i["new_price_text"] = sales_price
                base_i["full_price_text"] = sales_price
            '''    
            if not base_i["full_price_text"]:
                return
            '''
            # extract id, color per color product page
            pid = self.get_id(response)
            color = self.extract_color(response)
            stock = 0               # dummy            
            base_i["color_name"] = color
            base_i["color_code"] = color
            sizes = self.extract_sizes(response)
            base_i["size_infos"] = sizes
            sku_str = pid + '-' + color 
            base_i["sku"] = sku_str[:35] 
                      
            base_i["base_sku"] = pid
            base_i["product_id"] = pid
            #base_i["product_stock"] = str(self.sum_stock(sizes))
            base_i["identifier"] = base_i["sku"]
                
            base_i["save_availability"] = True

            yield base_i

        except Exception as e:
            log.msg('error occur at url' + response.url, level=log.ERROR)
            log.msg(str(e), level=log.ERROR)
            #log.msg(response.body, level=log.DEBUG)
            traceback.print_exc()

