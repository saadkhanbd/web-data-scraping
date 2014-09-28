#!/usr/bin/python print 'Set-Cookie:UserID="";'

'''
Saad Khan, August 20, 2014
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

class ElietahariSpider(SSBaseSpider):
    name = 'elietahari'
    long_name = "elietahari"
    base_url = "http://www.elietahari.com"
    spider_args = ""
    max_stock_level = 999    
    ctxt = PyV8.JSContext()                 # create a context with an implicit global object


    '''
    def __init__(self, *args, **kwargs):
        self.ctxt = PyV8.JSContext()         # create a context with an implicit global object
    '''
    
    def start_requests(self):
        
        # delivery regions - adpated from Robert's code snippet
        deliveryregionsAll = {
                            # Name: (currency, [country_codes], thousands_separator)        
                            'AG' : ('USD', ['AG'], '.'),
                            'AW' : ('USD', ['AW'], '.'),
                            'AU' : ('AUD', ['AU'], '.'),
                            'AT' : ('EUR', ['AT'], '.'),
                            'BH' : ('BHD', ['BH'], '.'),
                            'BD' : ('BDT', ['BD'], '.'),
                            'BB' : ('BBD', ['BB'], '.'),
                            'BE' : ('EUR', ['BE'], '.'),
                            'BZ' : ('BZD', ['BZ'], '.'),
                            'BM' : ('USD', ['BM'], '.'),
                            'BO' : ('BOB', ['BO'], '.'),
                            'BR' : ('USD', ['BR'], '.'),
                            'BN' : ('USD', ['BN'], '.'),
                            'BG' : ('BGN', ['BG'], '.'),
                            'KH' : ('KHR', ['KH'], '.'),
                            'CA' : ('CAD', ['CA'], '.'),
                            'KY' : ('KYD', ['KY'], '.'),
                            'CL' : ('CLP', ['CL'], '.'),
                            'CN' : ('CNY', ['CN'], '.'),
                            'CO' : ('COP', ['CO'], '.'),
                            'CR' : ('CRC', ['CR'], '.'),
                            'HR' : ('HRK', ['HR'], '.'),
                            'CY' : ('EUR', ['CY'], '.'),
                            'CZ' : ('CZK', ['CZ'], '.'),
                            'DK' : ('DKK', ['DK'], '.'),
                            'DM' : ('USD', ['DM'], '.'),
                            'DO' : ('DOP', ['DO'], '.'),
                            'EC' : ('USD', ['EC'], '.'),
                            'EG' : ('EGP', ['EG'], '.'),
                            'SV' : ('USD', ['SV'], '.'),
                            'EE' : ('EUR', ['EE'], '.'),
                            'FI' : ('EUR', ['FI'], '.'),
                            'FR' : ('EUR', ['FR'], '.'),
                            'GF' : ('EUR', ['GF'], '.'),
                            'DE' : ('EUR', ['DE'], '.'),
                            'GI' : ('GBP', ['GI'], '.'),
                            'GR' : ('EUR', ['GR'], '.'),
                            'GD' : ('USD', ['GD'], '.'),
                            'GP' : ('EUR', ['GP'], '.'),
                            'GT' : ('GTQ', ['GT'], '.'),
                            'GG' : ('GBP', ['GG'], '.'),
                            'HN' : ('HNL', ['HN'], '.'),
                            'HK' : ('HKD', ['HK'], '.'),
                            'HU' : ('HUF', ['HU'], '.'),
                            'IS' : ('EUR', ['IS'], '.'),
                            'IN' : ('INR', ['IN'], '.'),
                            'ID' : ('IDR', ['ID'], '.'),
                            'IE' : ('EUR', ['IE'], '.'),
                            'IL' : ('ILS', ['IL'], '.'),
                            'IT' : ('EUR', ['IT'], '.'),
                            'JM' : ('JMD', ['JM'], '.'),
                            'JP' : ('JPY', ['JP'], '.'),
                            'JE' : ('GBP', ['JE'], '.'),
                            'JO' : ('JOD', ['JO'], '.'),
                            'KR' : ('KRW', ['KR'], '.'),
                            'KW' : ('KWD', ['KW'], '.'),
                            'LV' : ('EUR', ['LV'], '.'),
                            'LI' : ('CHF', ['LI'], '.'),
                            'LT' : ('LTL', ['LT'], '.'),
                            'LU' : ('EUR', ['LU'], '.'),
                            'MO' : ('HKD', ['MO'], '.'),
                            'MV' : ('MVR', ['MV'], '.'),
                            'MT' : ('EUR', ['MT'], '.'),
                            'MQ' : ('EUR', ['MQ'], '.'),
                            'MX' : ('MXN', ['MX'], '.'),
                            'MC' : ('EUR', ['MC'], '.'),
                            'MS' : ('USD', ['MS'], '.'),
                            'NL' : ('EUR', ['NL'], '.'),
                            'NZ' : ('NZD', ['NZ'], '.'),
                            'NI' : ('NIO', ['NI'], '.'),
                            'NO' : ('NOK', ['NO'], '.'),
                            'OM' : ('OMR', ['OM'], '.'),
                            'PK' : ('PKR', ['PK'], '.'),
                            'PA' : ('PAB', ['PA'], '.'),
                            'PY' : ('PYG', ['PY'], '.'),
                            'PE' : ('PEN', ['PE'], '.'),
                            'PH' : ('PHP', ['PH'], '.'),
                            'PL' : ('PLN', ['PL'], '.'),
                            'PT' : ('EUR', ['PT'], '.'),
                            'QA' : ('QAR', ['QA'], '.'),
                            'RO' : ('RON', ['RO'], '.'),
                            'RU' : ('RUB', ['RU'], '.'),
                            'RE' : ('EUR', ['RE'], '.'),
                            'KN' : ('USD', ['KN'], '.'),
                            'LC' : ('USD', ['LC'], '.'),
                            'SA' : ('SAR', ['SA'], '.'),
                            'SG' : ('SGD', ['SG'], '.'),
                            'SK' : ('EUR', ['SK'], '.'),
                            'SI' : ('EUR', ['SI'], '.'),
                            'ZA' : ('ZAR', ['ZA'], '.'),
                            'ES' : ('EUR', ['ES'], '.'),
                            'LK' : ('LKR', ['LK'], '.'),
                            'SE' : ('SEK', ['SE'], '.'),
                            'CH' : ('CHF', ['CH'], '.'),
                            'TW' : ('TWD', ['TW'], '.'),
                            'TH' : ('THB', ['TH'], '.'),
                            'TT' : ('USD', ['TT'], '.'),
                            'TR' : ('TRY', ['TR'], '.'),
                            'TC' : ('USD', ['TC'], '.'),
                            'AE' : ('AED', ['AE'], '.'),
                            'GB' : ('GBP', ['GB'], '.'),
                            'US' : ('USD', ['US'], '.'),
        }


        languagesAll = {
                            'AG': 'en',
                            'AW': 'en',
                            'AU': 'en',
                            'AT': 'en',
                            'BH': 'en',
                            'BD': 'en',
                            'BB': 'en',
                            'BE': 'en',
                            'BZ': 'en',
                            'BM': 'en',
                            'BO': 'en',
                            'BR': 'en',
                            'BN': 'en',
                            'BG': 'en',
                            'KH': 'en',
                            'CA': 'en',
                            'KY': 'en',
                            'CL': 'en',
                            'CN': 'en',
                            'CO': 'en',
                            'CR': 'en',
                            'HR': 'en',
                            'CY': 'en',
                            'CZ': 'en',
                            'DK': 'en',
                            'DM': 'en',
                            'DO': 'en',
                            'EC': 'en',
                            'EG': 'en',
                            'SV': 'en',
                            'EE': 'en',
                            'FI': 'en',
                            'FR': 'en',
                            'GF': 'en',
                            'DE': 'en',
                            'GI': 'en',
                            'GR': 'en',
                            'GD': 'en',
                            'GP': 'en',
                            'GT': 'en',
                            'GG': 'en',
                            'HN': 'en',
                            'HK': 'en',
                            'HU': 'en',
                            'IS': 'en',
                            'IN': 'en',
                            'ID': 'en',
                            'IE': 'en',
                            'IL': 'en',
                            'IT': 'en',
                            'JM': 'en',
                            'JP': 'en',
                            'JE': 'en',
                            'JO': 'en',
                            'KR': 'en',
                            'KW': 'en',
                            'LV': 'en',
                            'LI': 'en',
                            'LT': 'en',
                            'LU': 'en',
                            'MO': 'en',
                            'MV': 'en',
                            'MT': 'en',
                            'MQ': 'en',
                            'MX': 'en',
                            'MC': 'en',
                            'MS': 'en',
                            'NL': 'en',
                            'NZ': 'en',
                            'NI': 'en',
                            'NO': 'en',
                            'OM': 'en',
                            'PK': 'en',
                            'PA': 'en',
                            'PY': 'en',
                            'PE': 'en',
                            'PH': 'en',
                            'PL': 'en',
                            'PT': 'en',
                            'QA': 'en',
                            'RO': 'en',
                            'RU': 'en',
                            'RE': 'en',
                            'KN': 'en',
                            'LC': 'en',
                            'SA': 'en',
                            'SG': 'en',
                            'SK': 'en',
                            'SI': 'en',
                            'ZA': 'en',
                            'ES': 'en',
                            'LK': 'en',
                            'SE': 'en',
                            'CH': 'en',
                            'TW': 'en',
                            'TH': 'en',
                            'TT': 'en',
                            'TR': 'en',
                            'TC': 'en',
                            'AE': 'en',
                            'GB': 'en',
                            'US': 'en',
        }

                
        crawling_regionsAll = ['AG',
                            'AW',
                            'AU',
                            'AT',
                            'BH',
                            'BD',
                            'BB',
                            'BE',
                            'BZ',
                            'BM',
                            'BO',
                            'BR',
                            'BN',
                            'BG',
                            'KH',
                            'CA',
                            'KY',
                            'CL',
                            'CN',
                            'CO',
                            'CR',
                            'HR',
                            'CY',
                            'CZ',
                            'DK',
                            'DM',
                            'DO',
                            'EC',
                            'EG',
                            'SV',
                            'EE',
                            'FI',
                            'FR',
                            'GF',
                            'DE',
                            'GI',
                            'GR',
                            'GD',
                            'GP',
                            'GT',
                            'GG',
                            'HN',
                            'HK',
                            'HU',
                            'IS',
                            'IN',
                            'ID',
                            'IE',
                            'IL',
                            'IT',
                            'JM',
                            'JP',
                            'JE',
                            'JO',
                            'KR',
                            'KW',
                            'LV',
                            'LI',
                            'LT',
                            'LU',
                            'MO',
                            'MV',
                            'MT',
                            'MQ',
                            'MX',
                            'MC',
                            'MS',
                            'NL',
                            'NZ',
                            'NI',
                            'NO',
                            'OM',
                            'PK',
                            'PA',
                            'PY',
                            'PE',
                            'PH',
                            'PL',
                            'PT',
                            'QA',
                            'RO',
                            'RU',
                            'RE',
                            'KN',
                            'LC',
                            'SA',
                            'SG',
                            'SK',
                            'SI',
                            'ZA',
                            'ES',
                            'LK',
                            'SE',
                            'CH',
                            'TW',
                            'TH',
                            'TT',
                            'TR',
                            'TC',
                            'AE',
                            'GB',
                            'US'
        ]


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

        #crawling_regions = ['US', 'UK', 'CA', 'DE', 'ES']
        crawling_regions = ['US']
                
        self.log(u'--- starting spider', scrapy.log.DEBUG)

        # EDIT following for ALL regions
        for CR in crawling_regionsAll:
        #for CR in crawling_regions:

            # 5 countries as TESTING case
            if True: #CR == 'CA' or CR == 'UK' or CR == 'US' or CR == 'DE' or CR =='ES':

                '''
                CODE for ALL countries
                ----------------------
                '''
                country_code = deliveryregionsAll[CR][1][0] # first element of list
                language_code = languagesAll[country_code]
                currency = deliveryregionsAll[CR][0]
 

                '''
                CODE for RESTRICTED countries
                -----------------------------
                country_code = deliveryregions[CR][1][0]    # first element of list
                language_code = languages[country_code]
                currency = deliveryregions[CR][0]
                '''
                
                country_url = self.base_url
                
                #create database entry, if not yet in database
                #createDeliveryRegion(webshop_code, region_code, currency, country_codes, country_names=[], region_url=None, spider=None)
               
                # construct meta dictionary
                base_meta = dict()
                base_meta['deliveryregion'] = CR
                base_meta['language_code'] = language_code
                base_meta['country_code'] = country_code
                base_meta['currency'] = currency                                                            
                base_meta['dont_merge_cookies'] = True
                                        
                # register deliveryregion - code for ALL COUNTIRS
                toolbox.register_deliveryregion(self, country_code, currency, deliveryregionsAll[CR][1], country_url)
                #toolbox.register_deliveryregion(self, country_code, currency, deliveryregions[CR][1], country_url)
                # register warehouselocation since max_stock_level > 0
                toolbox.register_warehouselocation(self, country_code)

                # process cookies, request
                req = Request(  url = country_url,
                                meta = base_meta,
                                dont_filter = True,
                                callback = self.choose_country_form
                )
                yield req        

    def choose_country_form(self, response):

        '''
            Visit the country chooser form page
            To extract form action url, 
        '''

        country_form_url = 'http://www.elietahari.com/on/demandware.store/Sites-elietahari_us-Site/en_US/International-ContextChooserModal'
        meta = copy.deepcopy(response.meta)

        # process cookies, request
        cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
        cookieJar.extract_cookies(response, response.request)
        meta['cookie_jar'] = cookieJar
        meta['dont_merge_cookies'] = False
                                                                  
        # construct the request  1              
        req = Request(  url = country_form_url,
                        meta = meta,                                                        
                        dont_filter = True,
                        callback = self.set_country
        )                                
        cookieJar.add_cookie_header(req)    # apply Set-Cookie
        yield req

    def set_country(self, response):

        '''

        To set a specific country:

            Extract the country chooser form action/link with appropriate
            time parameter from the response,

            And then contruct the AJAX request using POST form request with
            appropriate parameters.

            The request parameters for US are:

                'dwfrm_countrytwoletter_country': 'US',
                'dwfrm_countrytwoletter_save': ''
            
            The request parameters for OTHER countries are:

                'dwfrm_countrytwoletter_country': country_code.upper(),
                'dwfrm_countrytwoletter_currency':currency.upper(),
                'dwfrm_countrytwoletter_save': ''
                
        '''
        
        # extract form action url
        sel = Selector(response)
        form_url = sel.xpath('//form/@action').extract()[0]

        '''
        # extract country, currency codes
        countries = sel.xpath('//form/div[2]/select/option')
        #'US' : ('USD', ['us'], ","),
        fn = open('country.txt', 'w+')
        print '---# countries=', str(len(countries))
        for country in countries:
            country_code = country.xpath('@value').extract()[0]
            currency_code = country.xpath('@data-currency').extract()[0]
            print 'country=', country_code, '---currency=', currency_code
            fn.write("'" + country_code + "' : " + "('" + currency_code + "', ['" + country_code + "'], " + "'." + "')," + "\n")
        
        # extract country, language codes
        countries = sel.xpath('//form/div[2]/select/option')
        #                            'us': 'en',
        fn = open('language.txt', 'w+')
        print '---# countries=', str(len(countries))
        for country in countries:
            country_code = country.xpath('@value').extract()[0]
            currency_code = country.xpath('@data-currency').extract()[0]
            print 'country=', country_code, '---currency=', currency_code
            fn.write("                            '" + country_code + "': " + "'en" +"'," + "\n")
        
        # extract CR
        countries = sel.xpath('//form/div[2]/select/option')
        #                            'US',
        fn = open('cr.txt', 'w+')
        print '---# countries=', str(len(countries))
        for country in countries:
            country_code = country.xpath('@value').extract()[0]
            currency_code = country.xpath('@data-currency').extract()[0]
            print 'country=', country_code, '---currency=', currency_code
            fn.write("                            '" + country_code + "'," + "\n")
        '''
               
        meta = copy.deepcopy(response.meta)

        # process cookies, request
        cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
        cookieJar.extract_cookies(response, response.request)
        meta['cookie_jar'] = cookieJar
        meta['dont_merge_cookies'] = False
        country_code = meta['country_code']
        currency = meta['currency']
                                                                  
        # construct the AJAX/form request  1
        if 'us' in country_code:
            req = FormRequest(  url = form_url,
                                method = 'POST',
                                formdata = { 'dwfrm_countrytwoletter_country': 'US',
                                             'dwfrm_countrytwoletter_save': ''
                                },
                                meta = meta,                                                        
                                callback = self.parse_ship_to_country
            )
        else:
            req = FormRequest(  url = form_url,
                                method = 'POST',
                                formdata = { 'dwfrm_countrytwoletter_country': country_code.upper(),
                                             'dwfrm_countrytwoletter_currency':currency.upper(),
                                             'dwfrm_countrytwoletter_save': ''
                                },
                                meta = meta,                                                        
                                callback = self.parse_ship_to_country
            )
            
        cookieJar.add_cookie_header(req)    # apply Set-Cookie
        yield req

    def parse_ship_to_country(self, response):

        '''

            after setting the country
            visit the Home page/base url
            
        '''
        
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'
        
        meta = copy.deepcopy(response.meta)
        meta['dont_merge_cookies'] = False
        country_code = meta['country_code']
        
        # process cookies, request
        cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
        cookieJar.extract_cookies(response, response.request)
        meta['cookie_jar'] = cookieJar
        
        country_url = self.base_url + '/en-' + country_code.upper() + '/catalog'
        req = Request(  url = self.base_url,
                        meta = meta,
                        dont_filter = True,
                        callback = self.parse_country_home_page
        )
        cookieJar.add_cookie_header(req)    # apply Set-Cookie
        yield req        


    def parse_country_home_page(self, response):

        """
        Extract the main menu/category links from the home page, 
        """
 
        # main category list
        main_cats = ["women", "men", "shoes", "sale", "what"]
        
        # extract and set base url
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'
                        
        # extract main menu nodes
        sel = Selector(response)        
        lis = sel.xpath("//div[@class='categorymenu']/ul/li")
        self.log(u'--- # main menus =' + str(len(lis)) + ', url=' + base_url, scrapy.log.DEBUG)

        # process main menu nodes
        for li in lis:
            try:
                # main categories:
                cat = li.xpath("./a/text()").extract()[0].strip().lower()
                if any(cat in c for c in main_cats):
                    caturl = li.xpath("./a/@href").extract()[0]
                    meta = copy.deepcopy(response.meta)
                    meta["category"] = []                               
                    meta["category"].append(cat)                    

                    # process cookies, request
                    cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                    cookieJar.extract_cookies(response, response.request)
                    meta['dont_merge_cookies'] = True
                    meta['cookie_jar'] = cookieJar
                    
                    req = Request(  url=  caturl,
                                    meta= meta,
                                    dont_filter = True,
                                    callback=self.parse_sub_cats
                    )                    
                    cookieJar.add_cookie_header(req)    # apply Set-Cookie
                    #if 'man' in cat:                   # ---for TESTING ONLY---
                    #if cat == 'men':                    # ---for TESTING ONLY---
                    #if 'sale' in cat:                   # ---for TESTING ONLY---
                    yield req

            # li may be empty or may not contain category info
            except:
                pass
                
    def parse_sub_cats(self, response):

        '''
        Parse the sub cats
        '''
                  
        # sub category list
        sub_cats = ["categories", "special sizes", "precious jewelry", "apparel", "shoes", "jewelry & watches", "accessories", "luggage & travel", "men's grooming", "kids", "baby"]
        all_sub_cats = True
        
        #extract and set base url
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'

        # process response
        sel = Selector(response)
        
        # parse s cats
        #scats = sel.xpath('//ul[@class="categoryMenu"]/li/ul/li')   
        scats = sel.xpath('//ul[@class="categoryMenu"]/li')   
        self.log(u'--- s cats =' + str(len(scats)), scrapy.log.DEBUG)
        #print '---s cats=', str(len(scats))
        
        # visit the cat page to yield related sub cat
        if scats:            
            for scat in scats:                
                scatname = scat.xpath('h6/text()').extract()[0].strip().lower()
                meta = copy.deepcopy(response.meta)
                meta["category"].append(scatname)

                # extract next menu layer - s s cat
                sscats = scat.xpath('ul/li')
                if sscats:
                    for sscat in sscats:                
                        sscatname = sscat.xpath('a/text()').extract()[0].strip().lower()
                        if 'all' not in sscatname:
                            sscaturl = sscat.xpath('a/@href').extract()[0]
                            self.log(u'--- s s cat name=' + sscatname +  ", url=" + sscaturl, scrapy.log.DEBUG)
                            print '--- s s cat name=' + sscatname +  ", url=" + sscaturl
                            #print '---s cat name=', scatname

                            # process cats
                            meta = copy.deepcopy(response.meta)
                            meta["category"].append(sscatname)
                        
                            # process cookies, request
                            cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                            cookieJar.extract_cookies(response, response.request)
                            meta['dont_merge_cookies'] = True
                            meta['cookie_jar'] = cookieJar
                    
                            # process request
                            req = Request(  url= sscaturl,
                                            meta= meta,
                                            dont_filter = True,
                                            callback=self.parse_pager
                            )
                            cookieJar.add_cookie_header(req)    # apply Set-Cookie                        
                            #if 'women' in scatname and 'dresses' in sscatname:   # ---for TESTING ONLY---
                            #if 'women' in scatname and 'dresses' in sscatname:   # ---for TESTING ONLY---
                            yield req
                           
        # NO s cats, so        
        else:
            pass


    def parse_sub_cats_backup(self, response):

        '''
        Parse the sub cats
        '''
                  
        # sub category list
        sub_cats = ["categories", "special sizes", "precious jewelry", "apparel", "shoes", "jewelry & watches", "accessories", "luggage & travel", "men's grooming", "kids", "baby"]
        all_sub_cats = True
        
        #extract and set base url
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'

        # process response
        sel = Selector(response)
        
        # parse s cats
        scats = sel.xpath('//ul[@class="categoryMenu"]/li/ul/li')   
        self.log(u'--- s cats =' + str(len(scats)), scrapy.log.DEBUG)
        #print '---s cats=', str(len(scats))
        
        # visit the cat page to yield related sub cat
        if scats:
            
            for scat in scats:
                
                # extract s cat, url
                try:
                    scatname = scat.xpath('a/text()').extract()[0].strip().lower()
                    #if any(scatname in sc for sc in sub_cats):
                    if all_sub_cats:
                        scaturl = scat.xpath('a/@href').extract()[0]
                        self.log(u'--- s cat name=' + scatname +  ", url=" + scaturl, scrapy.log.DEBUG)
                        print '--- s cat name=' + scatname +  ", url=" + scaturl
                        #print '---s cat name=', scatname

                        # process cookies, request
                        meta = copy.deepcopy(response.meta)
                        cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                        cookieJar.extract_cookies(response, response.request)
                        meta['dont_merge_cookies'] = True
                        meta['cookie_jar'] = cookieJar
                    
                        meta["category"].append(scatname)
                        req = Request(  url= scaturl,
                                        meta= meta,
                                        dont_filter = True,
                                        callback=self.parse_pager
                        )
                        cookieJar.add_cookie_header(req)    # apply Set-Cookie
                        
                        #if 'wear to work' in scatname:   # ---for TESTING ONLY---
                        #if 'jackets' in scatname:   # ---for TESTING ONLY---
                        yield req
                        
                except:                    
                    pass                    
                            
        # NO s cats, so        
        else:
            pass

                          
    def parse_pager(self, response):
        
        '''
        Extract pagination info per page product list as follows:

            This string will be used to prepare the encoded *data* to be passed with POST FormRequest.
            The pagination info (page offset, category id) is set by setting the following variables of
            the above data structure:

                    PageOffset
                    CategoryID
                
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
        pager = sel.xpath('//div[@class="pagination"]/ul/li[@class="view-all"]/a')
        if pager:
            
            pagertext = pager.xpath('text()').extract()[0].lower()

            if 'view all' in pagertext:
                viewall_url = pager.xpath('@href').extract()[0]
                #print '---view all url=', viewall_url

                meta = copy.deepcopy(response.meta)
                
                # process cookies, request
                cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                cookieJar.extract_cookies(response, response.request)
                meta['cookie_jar'] = cookieJar

                # construct the form request  1              
                req = Request(  url = viewall_url,
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
        """
        
        #extract and set base url
        part_url = response.url.split('.com')[0]
        base_url = part_url + '.com'

        # handle slelctor
        sel = Selector(response)
        
        # The 1st one is for ALL OTHER products
        #prods = sel.xpath('//div[@class="productlisting"]/div[@class="product producttile"]')
        prods = sel.xpath('//div[@class="product producttile"]/div[@class="image"]/div[2]/ul/li[@class="gridimageqv"]/a')
        #print '--- # of HTML prods =', len(prods)

        # STANDARD product-list format 
        if prods:
            i = 0
            for prod in prods:                
                try:
                    #http://www.elietahari.com/en_US/lane-dress/E9165614.html?start=1&dwvar_E9165614_color=001&cgid=women-shop-dresses&PathToProduct=women-shop-dresses
                    prd_url = prod.xpath('@href').extract()[0]
                    #print '--- url =', prd_url
                    
                    meta = copy.deepcopy(response.meta)                    

                    cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
                    cookieJar.extract_cookies(response, response.request)
                    meta['dont_merge_cookies'] = True
                    meta['cookie_jar'] = cookieJar

                    req = Request(  url = prd_url,
                                    meta = meta,
                                    dont_filter = True,
                                    callback = self.parse_product_page
                    )
                    cookieJar.add_cookie_header(req)    # apply Set-Cookie
                    #if 'eileen-fisher-three-quarter-sleeve-colorblock-v-neck' in prd_url.lower():   # --- for TESTING ONLY ---
                    #if 'teanna' in prd_url:
                    yield req
                    
                except:
                    pass
                i += 1
                
    def get_brand(self, response):                 

        return 'Elie Tahari'


    def extract_category(self, response):       
        """
        Extract category info from the response.meta
        """
        sel = Selector(response)
        category = []
        breadcrumbs = sel.xpath('//div[@class="breadcrumb"]/a')
        if breadcrumbs:
            for breadcrumb in breadcrumbs:
                cat = breadcrumb.xpath('text()').extract()[0].strip().lower()
                category.append(cat)
            
        return category        

    def get_title(self, response):                 

        sel = Selector(response)
        title =''
        # FIRST try: with h2[1] = designer name, h2[2] = product title
        try:
            ttl = sel.xpath('//h1[@class="pdp-productname"]').extract()
            title_str = str(ttl)
            title = title_str.split('-->')[1]
            title = title.replace('\\t', '').replace('\\r', '').replace('\\n', '').replace('</h1>', '') 
            
        except:
            pass            
        return title

    def extract_desc(self, response):                  
        sel = Selector(response)
        try:
            desc = sel.xpath('//div[@class="tab-content selected"]/p[@class="longdesc"]/text()').extract()[0]
            return desc
        
        except:            
            return 'n/a'

    def extract_gender(self, category):
        gender = ""
        level = 0
        for info in category:
            if info == "men" or info == 'him':
                gender = "man"
                break
            elif "women" in info or info == 'her':
                gender = "woman"
                break
            level += 1
            
        return gender
                    
    def get_id(self, response):                 

        '''
        The following item does not have stylenumber, so the id has to be parsed from
        the respevtive url:
        
            http://www.elietahari.com/en_US/dorene-sweater/E961D504.html?dwvar_E961D504_color=H3X&start=6&cgid=women-shop-sweaters_and_knits&PathToProduct=women-shop-sweaters_and_knits
            
        '''

        sel = Selector(response)
        pid =''
        
        '''
        raw_pid = sel.xpath('//div[@class="tab-content selected"]/p[@class="stylenumber"]/text()').extract()[0]

        # check whether pid exists in selected tab area
        if raw_pid:
            pid = raw_pid.split(':')[1]
        '''
        
        
        # parse id from url - it is safest
        # for StyleNumber may be missing for some items
        # 
        url = response.url
        raw_pid = url.split('.html?')[0]
        pid = raw_pid.split('/')[5]
            
        #print '---get id=', pid
        return pid

    def get_price_standard(self, response): 
        
        sel = Selector(response)
        std_price = ''
        
        # try with standard price
        spnode = sel.xpath('//div[@class="standardprice"]')
        #print '---test price=', str(spnode)
        if spnode:
            std_price_str = spnode.xpath('text()').extract()[0]
            #print '--- s price=', normal_price_str
            std_price = re.findall(r'\d+[,|\.]?\d*', std_price_str)            
            return std_price
        
        return std_price

    def get_price_sale(self, response):

        sel = Selector(response)
        sale_price = ''
        
        # try with standard price
        spnode = sel.xpath('//div[@class="salesprice"]')
        #print '---test price=', str(spnode)
        if spnode:
            sale_price_str = spnode.xpath('text()').extract()[0]
            #print '--- s price=', normal_price_str
            sale_price = re.findall(r'\d+[,|\.]?\d*', sale_price_str)            
            return sale_price
        
        return sale_price

    def extract_images(self, response):     
        
        sel = Selector(response)
        image_urls = []
        
        #data.imageUrl = "http://cdn.fluidretail.net/customers/c1444/E319M604/E319M604_PDP/zoom_variation_BE8_view_RA1_2396x2792.jpg";
        img_url_src = sel.xpath('//div[@class="fluidExperienceWrapper"]/div/img/@src').extract()[0]

        JSscript = sel.xpath('//div[@class="productdetailcolumn productimages"]/script/text()').extract()[0]
        img_link = JSscript.split('data.imageUrl = "')[1]
        img_url_js = img_link.split('";')[0]
        #print '---url=', img_url_src
        return img_url_src
                            
    def extract_color(self, response):

        '''
        color list is formed from product list constructed by
        parse_product_data. The color list comprises followings:

            pid, color, stock_per_color
            
        calculate stock separately
        '''
        
        sel = Selector(response)
        color_vals = []

        colorcode = ''
            
        color = sel.xpath('//div[@class="swatches color"]/ul/li[@class="selected "]/a')
        if color:
            colorcode = color.xpath('text()').extract()[0]
        #print '---color=', colorcode
                                                    
        return colorcode

    def extract_sizes(self, response):       # fixed
        
        '''
        size info are formed from product list based on a particular color-match
        
        sample product data:
           ('0','prod167560188','sku150410881','X-SMALL (4)','MULTI DANRIDGE','Dandridge Mixed-Print Silk Half-Sleeve Caftan Dress',false,0,'',2,'3','/category/images/prod_stock1.gif','In Stock','Only 2 Left',new Array(),'','false',9999,'null');

        The 4th entry in the list is the SIZE, 16th entry is the STOCK 
        '''
        
        sel = Selector(response)
        output = []
        sizes = sel.xpath('//div[@class="swatches size"]/ul[@class="swatchesdisplay"]/li[@class="emptyswatch"]/a')

        for size in sizes:

            size_obj = SizeItem()

            # process size id 
            sizecode = size.xpath('text()').extract()[0]
            if sizecode:
                size_obj['size_identifier'] = sizecode
            else:
                size_obj['size_identifier'] = ''

            # process size name 
            sizename = size.xpath('@title').extract()[0]
            if sizename:
                size_obj['size_name'] = sizename            
            else:
                size_obj['size_name'] = ''

            # process size stock 
            size_obj['stock'] = 1   # default value
            
            output.append(size_obj)

        # return the size info
        return output


    # parse detail product page
    def parse_product_page(self, response):         # fixed

        """
        Parse the product detail page and yield the item,
        if the item full price text is null, then just return
        """

        try:
                        
            # base item attributes setting
            base_i = ProductItem()
            base_i["description_text"] =  self.extract_desc(response)
            base_i["url"] = response.url
            base_i['referer_url'] = response.request.headers.get('Referer', None)
            base_i["language_code"] = response.meta["language_code"]
            base_i["country_code"] = response.meta["country_code"]

            # extract categories
            category_names = self.extract_category(response)
            base_i["gender_names"] = self.extract_gender(category_names)
            base_i['category_names'] = category_names  #[n['name'] for n in cats_js]
            base_i['category_identifiers'] = category_names #[n['id'] for n in cats_js] # TODO: please change to actual identifiers (e.g. 'c390001')
            base_i['category_parents'] = toolbox.create_category_parents(base_i['category_identifiers'])
            
            base_i['update_details'] = True
            base_i['save_price'] = True
            base_i['add_category_and_gender'] = True
            base_i['image_urls'] = self.extract_images(response)
            base_i["brand"] = self.get_brand(response)
            
            base_i["title"] = self.get_title(response)
            #print '---title=', title
            stdprice = self.get_price_standard(response)
            saleprice = self.get_price_sale(response)
            if stdprice:
                base_i["old_price_text"] = stdprice
                base_i["full_price_text"] = stdprice
                base_i["new_price_text"] = saleprice
            else:
                base_i["old_price_text"] = saleprice
                base_i["full_price_text"] = saleprice
                base_i["new_price_text"] = saleprice
                
            if not base_i["full_price_text"]:
                return
            
            # multiple colors with multiple sizes may exist
            color = self.extract_color(response)
            pid = self.get_id(response)
            base_i["color_name"] = color
            base_i["color_code"] = color                
            base_i["size_infos"] = self.extract_sizes(response)                    
            base_i["sku"] = pid + '-' + color 
                      
            base_i["base_sku"] = pid
            #base_i["product_id"] = pid
            #base_i["product_stock"] = 0
            base_i["identifier"] = base_i["sku"]
                
            base_i["save_availability"] = True

            yield base_i
            
            
        except Exception as e:
            log.msg('error occur at url' + response.url, level=log.ERROR)
            log.msg(str(e), level=log.ERROR)
            #log.msg(response.body, level=log.DEBUG)
            traceback.print_exc()

