export default class ClassificationSegment {
    constructor(classificationObj) {
        this.nr = classificationObj.nr;
        this.prob = (classificationObj.prob * 100).toFixed(2);
        this.startTime = classificationObj.start_time;
        this.stopTime = classificationObj.stop_time;
        this.std = (classificationObj?.std * 100).toFixed(2);
    }
}
