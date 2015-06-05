var evtSrc = new EventSource("/event");
evtSrc.onopen = function(e){
    console.log('con openned');
    console.log(e);
}
evtSrc.onerror = function(e){
    console.log('event error');
    console.log(e);
}
evtSrc.onmessage = function(e) {
    var data=JSON.parse(e.data);
    console.log(data);
};

function isNumberKey(evt)
      {
         var charCode = (evt.which) ? evt.which : event.keyCode
         if (charCode > 31 && (charCode < 48 || charCode > 57))
            return false;
	 if (evt.key == "Enter") 
	  { //push(evt.which)
	  }
         return true;
      }
      


$(function() {
	//init();
	console.log("Loaded js function")
	//$(document.getElementsByClassName("bootstrapSwitch")).bootstrapSwitch('size', 'small');
	//$(document.getElementsByClassName("bootstrapSwitch")).bootstrapSwitch('onColor', 'success');
	//$(document.getElementsByClassName("bootstrapSwitch")).bootstrapSwitch('offColor', 'default');

	//$(document.getElementsByType("checkbox")).bootstrapSwitch();
	//$("[name='my-checkbox']").bootstrapSwitch();
	//$(document.getElementsByClassName("switch")).onColor = 'success';
})
