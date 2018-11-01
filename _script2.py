import logging
import time

# 对 basicConfig() 的调用，应该在任何记日志的调用如：debug()，info() 等之前。
# 因为它是作为一次性的简单配置工具，仅有第一次调用才会真正起作用，随后的调用不会起作用，相当于空操作。
logging.basicConfig(level=logging.INFO,filename='exampleadada.log')
logging.debug('debug1')
logging.info('info1')
logging.error('error1')
# time.sleep(5)
logging.error('errro2')
logging.info('info2')
logging.debug('debug1')

logging.error('errro3')
logging.info('info3')
logging.debug('debug3')

abs("hello")