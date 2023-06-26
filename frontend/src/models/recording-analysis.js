const HandEnum = {
    1: 'right',
    2: 'left',
    3: 'ambidextrous'
};

const SexEnum = {
    0: 'unknown',
    1: 'male',
    2: 'female'
};

export default class RecordingAnalysis {
    constructor(recordingObj) {
        this.id = recordingObj._id;
        this.name = recordingObj.name;
        this.notes = recordingObj.notes ? recordingObj.notes : null;

        this.channelNames = recordingObj.recording_info.ch_names;
        this.highpass = recordingObj.recording_info?.highpass
            ? recordingObj.recording_info.highpass
            : null;
        this.lowpass = recordingObj.recording_info?.lowpass
            ? recordingObj.recording_info.lowpass
            : null;
        this.measureDate = new Date(recordingObj.recording_info?.meas_date)
            .toISOString()
            .substr(0, 10);
        this.nTimes = recordingObj.recording_info.n_times;
        this.samplingFrequency = recordingObj.recording_info.sfreq;
        this.created = new Date(recordingObj.created)
            .toUTCString()
            .replace('GMT', '');

        this.subjectFirstName = recordingObj.subject_info?.first_name
            ? recordingObj.subject_info.first_name
            : null;
        this.subjectLastName = recordingObj.subject_info?.last_name
            ? recordingObj.subject_info.last_name
            : null;
        this.subjectMiddleName = recordingObj.subject_info?.middle_name
            ? recordingObj.subject_info.middle_name
            : null;
        this.subjectBirthday = recordingObj.subject_info?.birthday
            ? new Date(recordingObj.subject_info.birthday)
                  .toISOString()
                  .substr(0, 10)
            : null;
        this.subjectHand = recordingObj.subject_info?.hand
            ? HandEnum[recordingObj.subject_info.hand]
            : null;
        this.subjectSex = recordingObj.subject_info?.sex
            ? SexEnum[recordingObj.subject_info.sex]
            : null;
    }
}
