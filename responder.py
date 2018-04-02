# Author: Guo Jiansheng, Zhang Chang

from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField
from wtforms.validators import Required
import xlwt, os ,time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
bootstrap = Bootstrap(app)

player_info   = {"default_name":"default_ip","default_name2":"default_ip2"}
order         = 0
start_sign    = 0
administrator = []
results       = []

class NameForm(FlaskForm):
    name = StringField('用户名', validators=[Required()])
    password = PasswordField('密码', validators=[Required()])
    submit = SubmitField('登录')
    
class PlayerForm(FlaskForm):
    name = StringField('姓名', validators=[Required()])

def admin_check(ip_addr):
    for ip in administrator:
        if ip == ip_addr:
            return 1
        else:
            return 0
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/Administrator/start/')
def start():
    if not admin_check(request.remote_addr):
        return render_template('limit.html')
    global start_sign
    global order
    global results
    start_sign = 1
    order = 0
    results = []
    return render_template('welcome.html', start = start_sign)

@app.route('/Administrator/stop/')
def stop():
    if not admin_check(request.remote_addr):
        return render_template('limit.html')
    global start_sign
    start_sign = 0

    return render_template('welcome.html', start = start_sign)

@app.route('/Administrator/result/')
def result():
    if not admin_check(request.remote_addr):
        return render_template('limit.html')

    return render_template('result.html', result = results)

@app.route('/Administrator/export/')
def export():
    book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    sheet = book.add_sheet('result', cell_overwrite_ok=True)
    sheet.write(0, 0, '名次')
    sheet.write(0, 1, '姓名')
    index = 1
    path = os.path.split(os.path.realpath(__file__))[0]
    for item in results:
        sheet.write(index,0,str(index))
        sheet.write(index,1,item)
        index = index + 1
    path = path + '\\result_{time}.xls'.format(time = time.strftime('%Y-%m-%d_%H-%M-%S',time.localtime(time.time())))
    book.save(path)
    return render_template('welcome.html', export = 1, start = start_sign)

@app.route('/user/', methods=['GET', 'POST'])
def user():
    global administrator
    global start_sign
    name = None
    password = None
    form = NameForm()
    admin_ip = request.remote_addr
    if request.method == "GET" and (not admin_check(admin_ip)):
        return render_template('user.html', form = form)
    elif admin_check(admin_ip):
        return render_template('welcome.html', start = start_sign)
    if form.validate_on_submit():
        name = form.name.data
        password = form.password.data
        if name == 'admin' and password == 'admin':

            administrator.append(admin_ip)
            return render_template('welcome.html')
        else:
            return '<h1>name or password is error!</h1>'
    else:
        return render_template('input_error.html')

@app.route('/player_sign_in/', methods=['GET', 'POST'])
def player_sign_in():
    ip = request.remote_addr
    form = PlayerForm()
    global player_info
    if request.method == "GET":
        return render_template('player_sign_in.html',form = form, register=0)
    else:
        name = form.name.data
        for key, value in player_info.items():
            if key == name:
                return render_template('player_sign_in.html', form=form, register=2)
        player_info[name] = ip

        return render_template('player_sign_in.html', form=form, register=1)
    
@app.route('/player/',methods=['GET','POST'])
def player():
    player_ip = request.remote_addr
    print(player_ip)
    global player_info
    for key,value in player_info.items():
        if value==player_ip:
            print(key)
            username=key
    if request.method == 'GET':
        return render_template('player.html', message=username)

@app.route('/test',methods=['GET','POST']) 
def test():
    player_ip = request.remote_addr
    
    global player_info
    for key,value in player_info.items():
        if value==player_ip:
            print(key)
            username=key
    return render_template('test.html',username=username)


@app.route('/player_result',methods=['GET','POST']) 
def player_result():
    global start_sign
    global order
    global player_info
    global results
    flag=0
    player_ip = request.remote_addr
    order = order+1
    
    for key,value in player_info.items():
        if value==player_ip:
            username=key
    if 0==start_sign:
        return render_template('player_result.html',message="警告：抢答暂未开始，请在管理员说开始之后再抢答")
    else:
        for name in results:
            if name == username:
                flag = 1
            else:
                flag = 0
        if flag == 0:
            results.append(username)
        else:
            return render_template('player_result.html', message="您已经抢答过了！")
        if 1 == order:
            return render_template('player_result.html',message="恭喜，抢答成功！是时候展现真正的手速了")
        else:
            print(order)
            return render_template('player_result.html',message="抱歉，慢了一点点……")

@app.route('/refresh/')
def refresh():
    global results
    if results:
        return render_template('first.html', name = results[0])
    else:
        return render_template('welcome.html', start = start_sign)

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = int("80"),
        threaded=True
        )