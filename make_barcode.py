import xml.etree.ElementTree as ET
from django.http.response import JsonResponse
import  barcode
from style import models 
from miniwms.settings import MEDIA_ROOT

import barcode	


def make_custom_barcode(style_code):
    sty=models.Style.objects.get(code = style_code)
    upload_dir = 'barcode/'+str(sty.code)
    barcode_dir = MEDIA_ROOT+'/'+upload_dir
    code1 = barcode.generate('ean13',sty.code,
                        writer=barcode.writer.SVGWriter(),
                        output=barcode_dir,
                        writer_options={"background": "white",
                                        "module_width": 0.7,
                                        "module_height": 30,
                                        'text_distance':7
                                        },
                        )
    # 注册命名空间
    ET.register_namespace('', "http://www.w3.org/2000/svg")
    namespace = "{http://www.w3.org/2000/svg}"
    # 解析svg
    tree = ET.parse(barcode_dir+'.svg')
    # 获取root
    root=tree.getroot()

    # 添加边框
    border = ET.Element('polyline',{'points':'5,5 295,5 295,65 5,65 5,5','stroke':'black','stroke-width':'2','fill':'none'})
    root.append(border)
    # 添加文字

    size_text = ET.Element("text",{'x':'10','y':'45','fill':'black','font-size':'50'})
    size_text.text = sty.size.size
    root.append(size_text)

    color_text= ET.Element("text",{'x':'60','y':'45','fill':'black','font-size':'30'})
    color_text.text = sty.color.color
    root.append(color_text)

    type_text = ET.Element("text",{'x':'140','y':'45','fill':'black','font-size':'30'})
    type_text.text = sty.type.name
    root.append(type_text)

    g=root.find(namespace+"g")
    for i in g.findall(namespace+'rect'):
        # 更改条形码高度
        if i.attrib['height']=='100%':
            continue
        i.attrib['height']='13.000mm'
        i.attrib['y']='20.000mm'
    g.find(namespace+'text').attrib['style']="fill:black;font-size:10pt;text-anchor:middle;"

    # 写入文件
    tree.write(barcode_dir+'.svg')
    return upload_dir


# with sqlite3.connect("db.sqlite3") as conn:
#     conn.row_factory = sqlite3.Row
#     cursor = conn.cursor()
#     cursor.execute("select * from style_style")
#     style_info = cursor.fetchall()
    
#     # print('style:', list(style_info))
#     data = []
#     start=datetime.datetime.now()
#     for i in style_info:
#         data.append(dict(zip(i.keys(), i)))
#         # print(data)
#     end = datetime.datetime.now()
#     print('time:', start, end)
    
# print(json.dumps(data))
