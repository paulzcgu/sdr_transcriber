from marshmallow import Schema, fields


class Freq(object):
    def __init__(self, freq, description,
                 is_ham, is_gmrs):
        # fd.description, fd.freq, fd.is_ham, fd.is_gmrs
        self.freq = freq
        self.description = description
        self.is_ham = is_ham
        self.is_gmrs = is_gmrs


class FreqList(object):
    def __init__(self):
        self.freqs_list = []

    def append(self, freq):
        self.freqs_list.append(freq)


class FreqSchema(Schema):
    freq = fields.Number()
    description = fields.Str()
    is_ham = fields.Bool()
    is_gmrs = fields.Bool()


class FreqListSchema(Schema):
    freqs_list = fields.List(fields.Nested(FreqSchema))
