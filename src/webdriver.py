from selenium import webdriver
import time
import json

class QQMusicWebdriver():
    def __init__(self):
        self.browser = webdriver.Chrome()
        self.browser.get('https://y.qq.com/')
        self.account = ''  # your qq id
        self.password = '' # your password
    
    def login(self):
        ''' simulate login '''

        self._close_pop_window()
        self._find('//a[@class="top_login__link js_login"]').click()

        while not self._is_element_exist('//iframe[@id="frame_tips"]'):
            continue
        self.browser.switch_to.frame('frame_tips')

        while not self._is_element_exist('//iframe[@id="ptlogin_iframe"]'):
            continue
        self.browser.switch_to.frame('ptlogin_iframe')

        while not self._is_element_exist('//a[@id="switcher_plogin"]'):
            continue

        flag = True
        while flag:
            try:
                self._find('//a[@id="switcher_plogin"]').click()
                flag = False
            except:
                flag = True

        # time.sleep(2)
        # self._find('//a[@id="switcher_plogin"]').click()

        while not self._is_element_exist('//input[@id="u"]'):
            continue
        self._find('//input[@id="u"]').send_keys(self.account)
        self._find('//input[@id="p"]').send_keys(self.password)

        self._find('//a[@class="login_button"]').click()
        self.browser.switch_to.default_content()

        while not self._is_element_exist('//img[@class="top_login__cover js_user_img"]'):
            continue

        cookie = self.browser.get_cookies()
        
        # jsonCookies = json.dumps(cookie)
        with open('userdata/cookie/cookie.json', 'w') as f:
            json.dump(cookie, f, indent=1)

        print('Login succeed. Cookies have been written to userdata/cookie/cookie.json')


    def _close_pop_window(self):
        ''' close window that pops up at beginning '''
        while True:
            try:
                self._find('//a[@class="popup__close"]').click()
                break
            except:
                continue
        
    def _find(self, xpath):
        ''' find element by xpath rule '''
        return self.browser.find_element_by_xpath(xpath)

    def _is_element_exist(self, xpath):
        ''' if element exists (using xpath rule) '''
        try:
            self._find(xpath)
            return True
        except:
            return False


driver = QQMusicWebdriver()
driver.login()
    

