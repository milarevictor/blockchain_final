$("#prev_event").click(function (e) {
  var prev_event = parseInt(document.getElementById('events').innerHTML.toString()) - 1;
  var time = "";
  set_content(time, prev_event, "next_event");
});

$("#next_event").click(function (e) {
  var next_event = parseInt(document.getElementById('events').innerHTML.toString()) + 1;
  var time = "";
  set_content(time, next_event, "next_event");
});

$("#prev_time").click(function (e) {
  var prev_time = parseInt(document.getElementById('time_trans').innerHTML.toString()) - 1;
  var event = "";
  set_content(prev_time, event, "next_time");
});

$("#next_time").click(function (e) {
  var next_time = parseInt(document.getElementById('time_trans').innerHTML.toString()) + 1;
  var event = "";
  set_content(next_time, event, "next_time");
});

$("#ir_time").click(function (e) {
  var time = $("#time").val();
  var event = "";
  set_content(time, event, "next_time");
});

$("#ir_event").click(function (e) {
  var event = $("#event").val();
  var time = "";
  set_content(time, event, "next_event");
});

function set_content(time, event, operation) {
  $.ajax({
    type: "GET",
    url: url_to_call,
    data: {
      sid: simulation_id,
      e: event,
      t: time,
      operation: operation
    },
    beforeSend: function () {
      $("#loading").css("visibility", "visible");
    },
    complete: function () {
      $("#loading").css("visibility", "hidden");
    },
    success: function (result) {
      resetCanvas();
      setValues(result);
      var ctx = document.getElementById("graph").getContext("2d");
      var config = {
        type: "line",
        data: {
          labels: result.dados_graph.label,
          datasets: [
            {
              // label: false,
              // backgroundColor: window.chartColors.red,
              // borderColor: window.chartColors.red,
              data: result.dados_graph.data,
              fill: false,
              pointRadius: 0
            }
          ]
        },
        options: {
          legend: {
            display: false
          },
          responsive: true,
          title: {
            display: false
          },
          scales: {
            xAxes: [
              {
                display: true,
                scaleLabel: {
                  display: true,
                  labelString: "Tempo (Minutos)"
                },
                ticks: {
                  autoSkip: true,
                  maxTicksLimit: 10
                }
              }
            ],
            yAxes: [
              {
                display: true,
                scaleLabel: {
                  display: true,
                  labelString: "Lucro/Prejuízo"
                },
                ticks: {
                  min: result.dados_graph.min_value,
                  max: result.dados_graph.max_value,
                  // forces step size
                  stepSize: result.dados_graph.steps,
                  callback: function (value) {
                    return addCommas(value);
                  }
                }
              }
            ]
          }
        }
      };
      // console.log(typeof graph);
      // if (typeof graph != "undefined") {
      //   console.log('destroy');
      //   graph.destroy();
      // }
      var graph = new Chart(ctx, config);
    },
    error: function (result) {
      alert("error");
    }
  });
}
function addCommas(nStr) {
  // console.log("comma");
  nStr += "";
  nStr = nStr.replace(".", ",");
  x = nStr.split(",");
  x1 = x[0];
  x2 = x.length > 1 ? "," + x[1] + "0" : ",00";
  var rgx = /(\d+)(\d{3})/;
  while (rgx.test(x1)) {
    x1 = x1.replace(rgx, "$1" + "." + "$2");
  }
  positive = x1.split("-");
  formatted =
    positive.length > 1 ? "- R$ " + positive[1] + x2 : "R$ " + x1 + x2;
  return formatted;
}
function resetCanvas() {
  $('#graph').remove(); // this is my <canvas> element
  $('#graph-container').append('<canvas id="graph" height="500px">a</canvas>');
}