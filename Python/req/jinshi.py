from selenium import webdriver
import time
driver = webdriver.Chrome()     # 打开 Chrome 浏览器

driver.get("https://xnews.jin10.com/#/")
driver.find_element_by_link_text(u"参考首页").click()
print("\n======================\n=================参考首页\n\n",driver.page_source)
driver.find_element_by_link_text(u"大事件").click()
print("\n======================\n=================大事件\n\n",driver.page_source)
driver.find_element_by_link_text(u"突发行情").click()
print("\n======================\n=================突发行情\n\n",driver.page_source)
driver.find_element_by_link_text(u"攻略分析").click()
print("\n======================\n=================攻略分析\n\n",driver.page_source)
driver.find_element_by_link_text(u"金十独家").click()
print("\n======================\n=================金十独家\n\n",driver.page_source)
driver.find_element_by_link_text(u"深度报告").click()
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
