"use strict"
const MODEL_URL = 'static/mainapp/lungs/model.json';

tf.loadLayersModel(MODEL_URL).then(function(model) {
  const currmodel = model;
});