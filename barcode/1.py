import barcode


# barcode模块能自动计算验证码
import matplotlib.pyplot as plt
import barcode
from barcode.writer import ImageWriter
for i in range(10):
    s='11223322332'+str(i) # 生成条形码的数字
    code1 = barcode.get('ean13',s,writer=ImageWriter() ) # 生成条形码
    code1.save(i) # 保存文件'erer'
