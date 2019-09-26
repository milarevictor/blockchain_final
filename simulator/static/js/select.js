$("#bitcoin").click(function(e) {
  $("#personalizado").prop("checked", false);
  document.getElementById("bitcoin_box").className = "box-selected";
  document.getElementById("personalizado_box").className = "box-not-selected";
  document.getElementById("bitcoin_title").className = "title-selected";
  document.getElementById("bitcoin_description").className =
    "description-selected";
  document.getElementById("personalizado_title").className =
    "title-not-selected";
  document.getElementById("personalizado_description").className =
    "description-not-selected";
  document.getElementById("simulName").value = "Bitcoin";
  document.getElementById("energyCos").value = "0.43";
  document.getElementById("energyCons").value = "1.3";
  document.getElementById("ownCP").value = "14";
  document.getElementById("minersCP").value = "14";
  document.getElementById("medProb").value = "0.8";
  document.getElementById("reward").value = "562505.875";
  document.getElementById("avgTime").value = "10";
});
$("#personalizado").click(function(e) {
  $("#bitcoin").prop("checked", false);
  document.getElementById("personalizado_box").className = "box-selected";
  document.getElementById("bitcoin_box").className = "box-not-selected";
  document.getElementById("bitcoin_title").className = "title-not-selected";
  document.getElementById("bitcoin_description").className =
    "description-not-selected";
  document.getElementById("personalizado_title").className = "title-selected";
  document.getElementById("personalizado_description").className =
    "description-selected";
  document.getElementById("simulName").value = "";
  document.getElementById("energyCos").value = "";
  document.getElementById("energyCons").value = "";
  document.getElementById("ownCP").value = "";
  document.getElementById("minersCP").value = "";
  document.getElementById("medProb").value = "";
  document.getElementById("reward").value = "";
  document.getElementById("avgTime").value = "";
});
