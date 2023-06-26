export default class RecordingListItem {
    constructor(_id, name, created, subject_full_name) {
        this._id = _id;
        this.name = name;
        this.created = new Date(created).toUTCString().replace('GMT', '');
        this.subject_full_name = subject_full_name;
    }
}
