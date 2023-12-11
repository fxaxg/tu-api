from flask import Flask, request, jsonify, render_template
import ddddocr
import requests
import re  # 导入正则表达式库

debug = True  # 是否开启接口调试模式

app = Flask(__name__)
ocr = ddddocr.DdddOcr(beta=True, show_ad=False)


@app.route('/api/code_ocr', methods=['POST'])
def api_code_ocr():
    try:
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                return jsonify(code=400, result="", msg="未选择文件")
            image = file.read()
        elif 'image_url' in request.form:
            image_url = request.form['image_url']
            # 简单验证URL格式
            if not re.match(r'^https?://', image_url):
                return jsonify(code=400, result="", msg="无效的URL格式")

            response = requests.get(image_url, proxies={"http": None, "https": None})
            if response.status_code == 200:
                image = response.content
            else:
                return jsonify(code=400, result="", msg="从URL加载图片时出错")
        else:
            return jsonify(code=400, result="", msg="未提供图片或图片URL")

        res = ocr.classification(image)
        return jsonify(code=200, result=res, msg="识别成功")

    except Exception as e:
        msg = debug and str(e) or "识别失败,内部错误"
        return jsonify(code=500, result="", msg=msg)


@app.route('/code_ocr', methods=['get'])
def code_ocr():
    return render_template('code_ocr.html')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    print("老子来咯")
    app.run(port=2888, debug=True)
