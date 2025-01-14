import json

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import select
import traceback

# 用抛出异常来判断一个元素存不存在太慢了，需要等5秒钟
# def isElementExist(ele):
#     flag = True
#     result = EC.presence_of_element_located((By.XPATH, '//tbody[@id="queryLeftTable"]/tr[1]/td[13]/a'))
#     try:
#         # ele.find_element(by=By.CLASS_NAME, value='btn72')
#         result(ele)
#         return flag
#     except:
#         flag = False
#         return flag


def isElementExist(driver):
    flag=True
    ele = driver.find_elements(by=By.CLASS_NAME, value='btn72')
    if len(ele) == 0:
        flag = False
        return flag
    if len(ele) == 1:
        return flag
    else:
        flag = False
        return flag


jsonFileName = "12306Cookies.json"

def get_ticket(conf, driver, url):
    # 过网站检测，没加这句的话，账号密码登录时滑动验证码过不了，但二维码登录不受影响
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": """Object.defineProperty(navigator, 'webdriver', {
          get: () => undefined})"""})
    driver.minimize_window()

    # 从 JSON 文件中读取 cookies
    with open(jsonFileName, 'r') as file:
        cookies = json.load(file)
        # 将 cookies 添加到浏览器中
        for cookie in cookies:
            if 'domain' in cookie:
                domain = cookie['domain']

                # 根据 domain 切换到相应的网页
                if domain == "kyfw.12306.cn":
                    driver.get("https://kyfw.12306.cn")
                    # 添加 cookie
                    try:
                        driver.add_cookie(cookie)
                    except Exception as e:
                        print(f"Error adding cookie: {e}")

    #登录态
    hasLoginState = False
    myIndexUrl = "https://kyfw.12306.cn/otn/view/index.html"
    driver.get(myIndexUrl)
    driver.implicitly_wait(5)
    time.sleep(2)


    print("刷新页面")
    driver.refresh()
    driver.implicitly_wait(5)
    print(f"driver.current_url:{driver.current_url}")

    if driver.current_url == myIndexUrl:
        print("有登录态")
        hasLoginState = True



    # 判断是否有登录态,没有登录态就扫码保存cookie,后续无需重复扫码
    if not hasLoginState:
        print("无登录态")
        #driver.delete_all_cookies()
        driver.get(url)
        # 最多等待5秒使页面加载进来，隐式等待
        driver.implicitly_wait(5)

        # 获取并点击右上角登录按钮
        login = driver.find_element(by=By.ID, value='J-btn-login')
        login.click()
        driver.implicitly_wait(10)

        # # 账号密码登录
        # username_tag = driver.find_element(by=By.ID, value='J-userName')
        # username_tag.send_keys(conf.username)
        # password_tag = driver.find_element(by=By.ID, value='J-password')
        # password_tag.send_keys(conf.password)
        # login_now = driver.find_element(by=By.ID, value='J-login')
        # login_now.click()
        # time.sleep(20)

        # # 过滑动验证码
        # picture_start = driver.find_element(by=By.ID, value='nc_1_n1z')
        # # 移动到相应的位置，并左键鼠标按住往右边拖
        # ActionChains(driver).move_to_element(picture_start).click_and_hold(picture_start).move_by_offset(300, 0).release().perform()
        #
        #
        # 扫码登录
        scan_QR = driver.find_element(by=By.XPATH, value='//*[@id="toolbar_Div"]/div[2]/div[2]/ul/li[2]/a')
        scan_QR.click()
        driver.implicitly_wait(10)

        start_wait_time = time.time()
        scan_QR_url = driver.current_url
        # 扫码后会自动跳转页面
        while True:
            if start_wait_time+300 <= time.time():
                print("长时间不登陆(超过5分钟),结束程序!")
                return
            if scan_QR_url != driver.current_url:
                print(f"已扫码登录,跳转页面:{driver.current_url}")
                break

        time.sleep(5)
        cookie_cfg = []
        ret = setDomainCookie(driver.execute_script("return document.cookie;"),"kyfw.12306.cn")
        cookie_cfg.extend(ret)

        loginSuccessUrl = driver.current_url
        driver.get(url=url)
        driver.implicitly_wait(10)
        time.sleep(5)

        ret = setDomainCookie(driver.execute_script("return document.cookie;"),".12306.cn")
        cookie_cfg.extend(ret)

        # 将 cookies 保存到 JSON 文件
        print(driver.get_cookies())
        with open(jsonFileName, 'w') as file:
            file.write(json.dumps(cookie_cfg))

        driver.get(url=loginSuccessUrl)
        driver.implicitly_wait(10)


    # 点提示框
    # driver.find_element(by=By.XPATH, value='//div[@class="dzp-confirm"]/div[2]/div[3]/a').click()
    # driver.implicitly_wait(5)

    # 点击车票预订跳转到预订车票页面
    #driver.find_element(by=By.XPATH, value='//*[@id="link_for_ticket"]').click()
    driver.get("https://kyfw.12306.cn/otn/leftTicket/init")
    driver.implicitly_wait(10)

    # 输入出发地和目的地信息
    # 出发地
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').click()
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').clear()
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').send_keys(conf.fromstation)
    time.sleep(1)
    driver.find_element(by=By.XPATH, value='//*[@id="fromStationText"]').send_keys(Keys.ENTER)

    # 目的地
    destination_tag = driver.find_element(by=By.XPATH, value='//*[@id="toStationText"]')
    destination_tag.click()
    destination_tag.clear()
    destination_tag.send_keys(conf.destination)
    time.sleep(1)
    destination_tag.send_keys(Keys.ENTER)
    driver.implicitly_wait(5)

    # 出发日期
    date_tag = driver.find_element(by=By.XPATH, value='//*[@id="train_date"]')
    date_tag.click()
    date_tag.clear()
    date_tag.send_keys(conf.date)
    time.sleep(1)
    query_tag = driver.find_element(by=By.XPATH, value='//*[@id="query_ticket"]')

    start = time.time()

    while True:
        driver.implicitly_wait(5)
        # 点击查询

        driver.execute_script("$(arguments[0]).click()", query_tag)

        # 判断页面中有没有“预订”按钮，如果没有预订按钮就不断查询直到车票开售
        if not isElementExist(driver):
            # 车票处于待开售状态
            print(f"现在是{time.strftime('%H:%M:%S', time.localtime())}，还未开始售票")
            # 每隔两分钟刷新一次，否则3分钟内无购票操作12306系统会自动登出
            if time.time() - start >= 120:
                driver.refresh()
                start = time.time()
            # 延时1秒防止过于快速地点击导致查询超时，当然偶尔还是会出现超时现象，不过超时也没关系，一般等待6秒之后就会继续自动查询
            time.sleep(1)
            continue

        # 获取所有车票
        tickets = driver.find_elements(by=By.XPATH, value='//*[@id="queryLeftTable"]/tr')
        # 每张车票有两个tr，但是第二个tr没什么用
        tickets = [tickets[i] for i in range(len(tickets) - 1) if i % 2 == 0]
        #print(tickets)
        try:
            for ticket in tickets:
                # 如果车票的车次等于想要的车次并且硬卧的状态不是候补则点击预订
                #if ticket.find_element(by=By.CLASS_NAME,value='cdz').text== conf.fromstation:
                    #print(ticket.find_element(by=By.CLASS_NAME,value='number').text)
                    # value = '//td[8]'表示硬卧，td[10]表示硬座
                if ticket.find_element(by=By.CLASS_NAME,value='number').text == conf.trainnumber and ticket.find_element(by=By.XPATH, value='//td[8]').text != "候补":
                    # 点击预订
                    #print(ticket.find_element(by=By.CLASS_NAME,value='cdz').text)
                    #time.sleep(1)

                    try:ticket.find_element(by=By.CLASS_NAME, value='btn72').click()
                    except:break

                    # 这里之后就不能继续使用ticket.find_element()了，因为页面进行了跳转，会出现stale element reference: element is not attached to the page document的错误
                    # 我们可以使用driver.find_element()
                    # 选择乘车人，如果是学生，则需要确认购买学生票
                    driver.find_element(by=By.XPATH, value='//*[@id="normalPassenger_0"]').click()
                    # 点击确认购买学生票，如果不是学生，把这行注释了就行
                    #driver.find_element(by=By.XPATH, value='//*[@id="dialog_xsertcj_ok"]').click()
                    # 第二个乘车人
                    # driver.find_element(by=By.XPATH, value='//*[@id="normalPassenger_1"]').click()
                    # 如果第二个乘车人也是学生，则需要点击确认第二个人也购买学生票
                    # driver.find_element(by=By.XPATH, value='//*[@id="dialog_xsertcj_ok"]').click()
                    # 提交订单
                    driver.find_element(by=By.XPATH, value='//*[@id="submitOrder_id"]').click()
                    # 选座  F座
                    #time.sleep(1)
                    #move = driver.find_element(By.ID, value='1F')
                    #ActionChains(driver).move_to_element(move).perform()
                    # time.sleep(1)
                    #这里直接使用id和xpath定位不到，所以直接加上他的路径,可以不用这么长，但是懒得删
                    driver.find_element(by=By.XPATH, value='//html/body/div[5]/div/div[5]/div[1]/div/div[2]/div[2]/div[3]/div[2]/div[2]/ul[2]/li[2]/a[@id="1F"]').click()
                    # 确认提交订单，然后这里和上面是一样的
                    driver.find_element(by=By.XPATH, value='//html/body/div[5]/div/div[5]/div[1]/div/div[2]/div[2]/div[8]/a[2][@id="qr_submit_id"]').click()
                    print(f"{conf.trainnumber}次列车抢票成功，请尽快在10分钟内支付！")
                    return
        except Exception as e:
            print(f"err:{e}")
            print(traceback.format_exc())
            # time.sleep(600)
            return


def setDomainCookie(str,domain):
    ret = []
    arr = str.split("; ")
    for ss in arr:
        name, value = ss.split('=', 1)
        ret.append({'domain': domain, 'name': name.strip(), 'value': value.strip(), 'path': '/'})

    return ret

class Config:
    def __init__(self):
        # 账号
        self.username = 'xxxx'
        # 密码
        self.password = 'xxxx'
        # 出发地
        self.fromstation = '深圳'
        # 目的地
        self.destination = '梧州'
        # 出发日期
        self.date = '2025-01-12'
        # 车次   例如Z146,G127
        self.trainnumber = 'G2918'


if __name__ == '__main__':
    # 有关车票的配置信息保存在该类里
    # 请事先在config.py里填好相关信息
    conf = Config()

    url = 'https://www.12306.cn/index/'

    # driver文件要放在同级目录下
    s = Service(r'chromedriver.exe')
    driver = webdriver.Chrome(service=s)
    get_ticket(conf, driver, url)
    time.sleep(10)
    driver.quit()
