import imghdr

from flask import Flask, request, jsonify, render_template
import ddddocr
import requests
import re  # 导入正则表达式库

app = Flask(__name__)
ocr = ddddocr.DdddOcr(beta=True, show_ad=False)


# 校验图片是否合规
def invalid_image(image):
    """
    校验图片是否合规。
    参数:
        image: 要校验的图片内容
    返回:
        True: 图片不合规
        False: 图片合规
    """
    if len(image) > 1024 * 1024 * 2:  # 2MB
        return True
    # 文件类型校验
    allowed_extensions = ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg', 'tif', 'ico']
    file_type = imghdr.what(None, h=image)
    if file_type not in allowed_extensions:
        return True
    return False


# 从URL获取图片内容及cookies
def fetch_image(image_url):
    """
    从给定的URL获取图片。
    参数:
        image_url: 图片的URL
    返回:
        图片内容和cookies（如果有的话）
    """
    response = requests.get(image_url, proxies={"http": None, "https": None})
    if response.status_code == 200:
        return response.content, response.cookies.get_dict()
    return None, {}


# 对图片执行OCR识别
def ocr_image(image):
    """
    对提供的图片进行OCR识别。
    参数:
        image: 要识别的图片内容
    返回:
        识别结果
    """
    return ocr.classification(image)


# OCR API路由
@app.route('/api/code_ocr', methods=['POST'])
def api_code_ocr():
    """
    API端点，处理图片OCR识别请求。
    接收文件上传或图片URL。
    """
    try:
        cookies = {}
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify(code=400, result="", msg="未选择文件")

            image = file.read()  # 读取一次文件内容
            if invalid_image(image):
                return jsonify(code=400, result="", msg="无效的图片")
        elif 'image_url' in request.form:
            image_url = request.form['image_url']
            if not re.match(r'^https?://', image_url):
                return jsonify(code=400, result="", msg="无效的URL格式")
            image, cookies = fetch_image(image_url)
            if image is None:
                return jsonify(code=400, result="", msg="从URL加载图片时出错")
        else:
            return jsonify(code=400, result="", msg="未提供图片或图片URL")

        res = ocr_image(image)
        return jsonify(code=200, result=res, cookies=cookies, msg="识别成功")

    except Exception as e:
        debug = True  # 是否开启接口调试模式
        print(e)
        msg = str(e) if debug else "识别失败,内部错误"
        return jsonify(code=500, result="", msg=msg)


# 其他网页路由
@app.route('/code_ocr', methods=['GET'])
def code_ocr():
    """返回OCR页面的模板。"""
    return render_template('code_ocr.html')


@app.errorhandler(404)
def page_not_found(e):
    """自定义404页面。"""
    return render_template('404.html'), 404


@app.route('/')
def index():
    """返回主页模板。"""
    return render_template('index.html')


# 启动应用
if __name__ == '__main__':
    app.run(port=2888, debug=False, host='0.0.0.0')
