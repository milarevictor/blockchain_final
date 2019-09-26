function modal() {
  var modal = document.getElementsByClassName("modal")[0],
    trigger = document.getElementsByClassName("modal-trigger")[0],
    close = document.getElementsByClassName("modal__close"); // we loops this to catch the different closers

  closeModal = function () {
    modal.classList.remove("modal--show");
    modal.classList.add("modal--hide");
    afterAnimation = function () {
      modal.classList.remove("modal--hide");
    };
    modal.addEventListener("webkitAnimationEnd", afterAnimation, false);
    modal.addEventListener("oAnimationEnd", afterAnimation, false);
    modal.addEventListener("msAnimationEnd", afterAnimation, false);
    modal.addEventListener("animationend", afterAnimation, false);
  };

  trigger.onclick = function () {
    $("a#download").click(function () {
      var log = document.getElementById("modal-content").innerHTML.toString();
      log = log.split("<p>").join("");
      log = log.split("</p>").join("\n");
      this.href = "data:text/plain;charset=UTF-8," + encodeURIComponent(log);
    });

    var event = document.getElementById("events").innerHTML.toString();
    document.getElementById("modal-content").innerHTML = "";
    modal.classList.add("modal--show");

    $.ajax({
      type: "GET",
      url: url_modal,
      data: {
        sid: simulation_id,
        e: event
      },
      beforeSend: function () {
        console.log("teste");
        $("#loading").css("visibility", "visible");
      },
      complete: function () {
        $("#loading").css("visibility", "hidden");
      },
      success: function (result) {
        result.log.forEach(function (element) {
          // console.log(element);
          document.getElementById("modal-content").innerHTML +=
            "<p>" + element + " </p>";
        });
      },
      error: function (result) {
        alert("error");
      }
    });
  };

  for (var i = 0; i < close.length; i++) {
    close[i].onclick = function () {
      closeModal();
    };
  }

  window.onclick = function (e) {
    if (e.target == modal) {
      closeModal();
    }
  };

  document.onkeyup = function (e) {
    e = e || window.event;
    if (modal.classList.contains("modal--show")) {
      if (e.keyCode == 27) {
        closeModal();
      }
    }
  };
}
modal();
