import sys
sys.path.append(r"/home/student/project-one/Code/Backend") # fix for local relative imports
from repository.DataRepository import DataRepository
from flask_socketio import SocketIO, emit, send
from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Qsz9532/*-'
socketio = SocketIO(app, cors_allowed_origins="*", logger=False,
                    engineio_logger=False, ping_timeout=1)
CORS(app)

# API ENDPOINTS
@app.route('/')
def index():
    return 'ping'

############ ALL ############
@app.route('/data', methods=['GET', 'POST', 'DELETE'])
def get_data():
    if request.method == 'GET':
        return jsonify(data=DataRepository.get_all_data())
    elif request.method == 'POST':
        data = DataRepository.json_or_formdata(request)
        new_id = DataRepository.add_data(data.get('temp'), data.get('light'), data.get('sound'), data.get('airquality'))
        socketio.emit('B2F_latest_data', {'data': data})
        return jsonify(readingid=new_id), 201

@app.route('/data/latest')
def get_latest_data():
    return jsonify(DataRepository.get_latest_data())

@app.route('/data/<date>')
def get_data_by_date(date):
    return jsonify(date=date, data=DataRepository.get_all_data(date + '%'))

@app.route('/data/<date>/average')
def get_data_by_date_avg(date):
    return jsonify(DataRepository.get_daily_average(date))

@app.route('/data/<date>/average/hourly')
def get_data_by_date_avg_hourly(date):
    return jsonify(data=DataRepository.get_hourly_average(date))

############ TEMP ############
@app.route('/data/temp')
def get_temp():
    return jsonify(data=DataRepository.get_temp())

@app.route('/data/temp/<date>')
def get_temp_by_date(date):
    return jsonify(date=date, data=DataRepository.get_temp(date + '%'))

############ LIGHT ############
@app.route('/data/light')
def get_light():
    return jsonify(data=DataRepository.get_light())

@app.route('/data/light/<date>')
def get_light_by_date(date):
    return jsonify(date=date, data=DataRepository.get_light(date + '%'))

############ SOUND ############
@app.route('/data/sound')
def get_sound():
    return jsonify(data=DataRepository.get_sound())

@app.route('/data/sound/<date>')
def get_sound_by_date(date):
    return jsonify(date=date, data=DataRepository.get_sound(date + '%'))

############ AIR ############
@app.route('/data/air')
def get_air():
    return jsonify(data=DataRepository.get_air())

@app.route('/data/air/<date>')
def get_air_by_date(date):
    return jsonify(date=date, data=DataRepository.get_air(date + '%'))

############ ALARM ############

@app.route('/alarms', methods=['GET', 'POST'])
def get_alarms():
    if request.method == 'GET':
        return jsonify(data=DataRepository.get_all_alarms())
    elif request.method == 'POST':
        data = DataRepository.json_or_formdata(request)
        new_id = DataRepository.add_alarm(data.get('name'), data.get('date'))
        socketio.emit('B2F_added_alarm', {'id': new_id})
        return jsonify(alarm_id=new_id), 201

@app.route('/alarm/<id>', methods=['GET', 'PUT', 'DELETE'])
def update_alarm_status(id):
    if request.method == 'GET':
        return jsonify(data=DataRepository.get_alarm_by_id(id))
    elif request.method == 'PUT':
        data = DataRepository.json_or_formdata(request)
        response = DataRepository.update_alarm_status(id, data.get('active'))
        socketio.emit('B2F_update_alarm_status', {'id':id, 'active': data.get('active')})
        return jsonify(response=response), 201
    elif request.method == 'DELETE':
        DataRepository.delete_alarm(id)
        socketio.emit('B2F_deleted_alarm', {'id': id})
        return jsonify(response='alarm deleted')


############ RGB ############

@app.route('/rgb', methods=['GET', 'PUT'])
def get_rgb():
    if request.method == 'GET':
        data = DataRepository.get_rgb_settings()
        return jsonify({'data': {'hex':data['hex'], 'rgb': {'r':data['r'],'g':data['g'],'b':data['b']}}})
    elif request.method == 'PUT':
        data = DataRepository.json_or_formdata(request)
        response = DataRepository.update_rgb_settings(data.get('r'), data.get('g'), data.get('b'), data.get('hex'))
        socketio.emit('B2F_update_rgb_settings', {'rgb': {'r': 0, 'g': 0, 'b': 0}, 'hex': '#000'})
        return jsonify(response=response), 201



######## SOCKET IO ##########
@socketio.on('connect')
def initial_connection():
    print('A new client connect')
    latest_data = DataRepository.get_latest_data()
    rgb = DataRepository.get_rgb_settings()
    emit('B2F_latest_data', {'data': latest_data}, broadcast=True)
    emit('RGB_update', { 'r': rgb['r'], 'g': rgb['g'], 'b': rgb['b'] }, broadcast=True)

# client -> server -> client, echo
# reviece latest data from sensors client, forward to web interface client
@socketio.on('B2F_latest_data')
def latest_data(payload):
    emit('B2F_latest_data', payload, broadcast=True)
@socketio.on('RGB_update')
def latest_data(payload):
    emit('RGB_update', payload, broadcast=True)


# start app
if __name__ == '__main__':
    print('******* API started *******')
    socketio.run(app, debug=True, host='0.0.0.0')
