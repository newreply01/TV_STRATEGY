const lw = require('lightweight-charts');
console.log(Object.keys(lw));
const chartKeys = Object.keys(lw.createChart(document.createElement('div')));
console.log("CHART KEYS:", chartKeys);
