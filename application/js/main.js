var video_socket = null;
var jpeg_frame = new Image();
var jpeg_data = "";
var pixelsPerMmY = 1;
var pixelsPerMmZ = 1;
var centring = false; 
var mouse_x = 0;
var mouse_y = 0;
                

$(document).ready(function() {
  setup();
});


var set_light = function(put_in) {
  $.ajax({
    error: function(XMLHttpRequest, textStatus, errorThrown) { alert(textStatus) },
    url: 'set_light',
    data: { "put_in": put_in },
    type: 'GET',
    success: function(res) {
      update_gui(res);
    },
    dataType: "json" });
}

var set_light_in = function() { set_light(1); }
var set_light_out = function() { set_light(0); }

var set_zoom = function() {
  var selected_zoom = $(this).find(":selected").val();
  $.ajax({
    error: function(XMLHttpRequest, textStatus, errorThrown) { alert(textStatus) },
    url: 'set_zoom',
    type: 'GET',
    data: { "zoom_level": selected_zoom*20 },
    success: function(res) {
      update_gui(res);
    },
    dataType: "json" });
}

var set_light_level = function() {
  $.ajax({
    error: function(XMLHttpRequest, textStatus, errorThrown) { alert(textStatus) },
    url: 'set_light_level',
    type: 'GET',
    data: { "light_level": $("#light").val() },
    success: function(res) {
      update_gui(res);
    },
    dataType: "json" });
}

var do_login = function() {
  $.ajax({
    error: function(XMLHttpRequest, textStatus, errorThrown) { alert(textStatus) },
    url: 'login',
    type: 'GET',
    data: { "username": $("#username").val(), "password": $("#password").val() },
    success: function(res) {
      if (res.ok) {
        $("#collect_button").attr("disabled", false);
      } else {
        $("#collect_button").attr("disabled", true); 
        alert(res.err);
      }
    },
    dataType: "json" });
}

var update_gui = function(res) {
      $("#transmission").val(res.transmission);
      $("#resolution").val(res.resolution);
      $("#energy").val(res.energy);
      if (res.light_state == "out") {
        $("#lightout").button('toggle');
      } else if (res.light_state == "in") {
        $("#lightin").button("toggle");
      }
      $("#light").val(res.light);
      $("#zoom").val(res.zoom);
      pixelsPerMmY = res.pixelsPerMmY
      pixelsPerMmZ = res.pixelsPerMmZ
}

var draw_sample_video = function() {
       var img_canvas = document.getElementById('sample_view')
       var img_context = img_canvas.getContext("2d");

       img_context.drawImage(jpeg_frame, 0, 0, 659, 493);
       img_context.strokeStyle = "#FF0000" //red
       img_context.beginPath();
       img_context.moveTo((659/2)-20,493/2);
       img_context.lineTo((659/2)+20,493/2);
       img_context.moveTo(659/2,(493/2)-20);
       img_context.lineTo(659/2,(493/2)+20);
       img_context.stroke();
       img_context.closePath();

       img_context.beginPath();
       img_context.strokeStyle = "#7FFF00" //chartreuse
       img_context.fillStyle = "#7FFF00" //chartreuse
       img_context.rect(10,493-110,3,100);
       img_context.rect(10,493-7,100,3);
       img_context.fill();
       img_context.stroke();
       img_context.closePath();

       if (centring) {
         img_context.strokeStyle="#FFFF00" //yellow
         img_context.beginPath();
         img_context.moveTo(0,mouse_y);
         img_context.lineTo(659,mouse_y);
         img_context.moveTo(mouse_x,0);
         img_context.lineTo(mouse_x,493);
         img_context.stroke();
         img_context.closePath();
      }
}
jpeg_frame.onload=draw_sample_video;

var ev_canvas = function(ev) {
       var img_canvas = document.getElementById('sample_view');
       mouse_x = ev.pageX-img_canvas.offsetLeft;
       mouse_y = ev.pageY-img_canvas.offsetTop;

       if (ev.type == "mouseup") {
         if (centring) {
           centring = false;
           $.ajax({
             error: function(XMLHttpRequest, textStatus, errorThrown) { alert(textStatus) },
             url: 'centring',
             type: 'GET',
             data: { "X":mouse_x, "Y": mouse_y },
             success: function(res) {
               centring = res.continue;
               /*draw_sample_video(); */
             },
             dataType: "json"
           })
         }
       }
}

var start_centring = function() {
  centring = true;
  mouse_x = 0;
  mouse_y = 0;
}

var get_state = function() {
  $.ajax({
             error: function(XMLHttpRequest, textStatus, errorThrown) { alert(textStatus) },
             url: 'state',
             type: 'GET',
             success: function(res) {
               update_gui(res);
               setTimeout(get_state, 100);
             },
             dataType: "json"
           })
}


function setup() {
   var img_canvas = document.getElementById('sample_view')
   var img_context = img_canvas.getContext("2d");
   img_context.fillStyle="#808080"
   img_context.fillRect(0,0,659,493)
   img_canvas.addEventListener('mousemove', ev_canvas, false);
   img_canvas.addEventListener('mouseup',   ev_canvas, false);

   $.ajax({
    error: function(XMLHttpRequest, textStatus, errorThrown) { alert(textStatus) },
    url: 'init',
    type: 'GET',
    success: function(res) {
      update_gui(res);

      $("#collect_button").attr("disabled", true);
      $("#lightin").click(set_light_in);
      $("#lightout").click(set_light_out);
      $("#zoom").change(set_zoom);
      $("#set_light_level").click(set_light_level);
      $("#login_button").click(do_login);
      $("#centre_button").click(start_centring);

      var video_source = new EventSource("sample_video_stream");
      function display_sample_video() {
          jpeg_frame.src = "data:image/jpeg;base64,"+jpeg_data;
      };
      video_source.addEventListener("message", function(e) {
        jpeg_data = e.data;
        //jpeg_frame.src="data:image/jpeg;base64,"+jpeg_data;
        mozRequestAnimationFrame(display_sample_video);
      }, false);
 
    },
    dataType: "json" }) 
};
