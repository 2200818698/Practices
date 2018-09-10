from selenium import webdriver
import time
driver = webdriver.Chrome()     # 打开 Chrome 浏览器

driver.get("https://v.jin10.com/")
driver.find_element_by_link_text(u"首页").click()
driver.find_element_by_link_text(u"金十早报").click()
driver.find_element_by_link_text(u"华尔街TIMES").click()
driver.find_element_by_link_text(u"金十访谈间").click()
driver.find_element_by_link_text(u"国外精选").click()
driver.find_element_by_link_text(u"金十译讯").click()
driver.find_element_by_link_text(u"财经街访").click()
driver.find_element_by_link_text(u"老板说的对").click()
driver.find_element_by_link_text(u"金十财知道").click()
driver.find_element_by_link_text(u"她在开啥车").click()
print("\n======================\n=================深度报告\n\n",driver.page_source)
# driver.find_element_by_link_text(u"全球贸易战").click()
# driver.find_element_by_link_text(u"欧佩克动态").click()
# driver.find_element_by_link_text(u"英国政坛危机").click()
# driver.find_element_by_link_text(u"美联储那些事").click()
# driver.find_element_by_link_text(u"伊朗制裁之争").click()
# driver.find_element_by_link_text(u"CFTC持仓秘密").click()
# driver.find_element_by_link_text(u"土耳其危机").click()
# driver.find_element_by_link_text(u"新兴市场大逃亡").click()

driver.close()
