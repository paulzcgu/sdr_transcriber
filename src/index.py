from flask import Flask, request
from flask_cors import CORS
from database import Database_client
from enum import Enum

from model.freq import Freq, FreqList, FreqListSchema
from model.recordings import Recording, RecordingList, RecordingListSchema

app = Flask(__name__)
CORS(app)

DB_PATH = "/Users/zcgu/sdr_transcriber/data/sdr_transcriber"


@app.route('/recordings', methods=["GET"])
def get_rocordings():
    if not request.args:
        data, code = _get_recording_data(0)
    else:
        data, code = _get_recording_data(request.args["lastId"])
    return data, code


@app.route('/freq', methods=["GET"])
def get_freqs():
    data, code = _get_freq_data()
    return data, code


def _get_recording_data(lastid, sort="DESC"):
    _db_client = Database_client(DB_PATH)
    sql_query = "SELECT r.id, r.path_to_recording, r.team_id, r.timestamp, " \
                "r.msg_body, r.freq, r.confidence FROM recording " \
                "r WHERE r.id > {} ORDER BY r.id {}".format(lastid, sort)
    _db_client.query(sql_query)
    rows = _db_client.fetchall()
    recording_list = RecordingList(lastid)
    for row in rows:
        rec = Recording(row[0], row[1], row[2],
                        row[3], row[4], row[5], row[6])
        recording_list.append(rec)
    schema = RecordingListSchema()
    data = schema.dump(recording_list)
    return data, 200


def _get_freq_data():
    _db_client = Database_client(DB_PATH)
    sql_query = "SELECT fd.description, fd.freq, fd.is_ham, fd.is_gmrs" \
                " FROM freq_description fd "
    _db_client.query(sql_query)
    rows = _db_client.fetchall()
    freq_list = FreqList()
    for row in rows:
        rec = Freq(row[0], row[1], row[2], row[3])
        freq_list.append(rec)
    schema = FreqListSchema()
    data = schema.dump(freq_list)
    return data, 200


class SortOrder(Enum):
    ASC = "ASC"
    DESC = "DESC"


if __name__ == "__main__":
    app.run()
