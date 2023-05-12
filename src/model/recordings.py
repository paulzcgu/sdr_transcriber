from marshmallow import Schema, fields
import datetime

dt_format = "%Y-%m-%d %H:%M:%S"


class Recording(object):
    def __init__(self, id, path_to_recording, team_id,
                 timestamp, msg_body, freq, confidence):
        # r.id, r.path_to_recording, r.team_id,
        # r.timestamp, r.msg_body, r.freq, r.confidence
        self.id = id
        self.path_to_recording = path_to_recording
        self.team_id = team_id
        self.timestamp = datetime.datetime.strptime(timestamp, dt_format)
        self.msg_body = msg_body
        self.freq = freq
        self.confidence = confidence


class RecordingList(object):
    def __init__(self, last_id):
        self.last_id = last_id
        self.recordings_list = []

    def append(self, recording):
        self.recordings_list.append(recording)


class RecordingSchema(Schema):
    id = fields.Int()
    path_to_recording = fields.Str()
    team_id = fields.Int()
    timestamp = fields.DateTime()
    msg_body = fields.Str()
    freq = fields.Number()
    confidence = fields.Number()


class RecordingListSchema(Schema):
    last_id = fields.Int()
    recordings_list = fields.List(fields.Nested(RecordingSchema))
