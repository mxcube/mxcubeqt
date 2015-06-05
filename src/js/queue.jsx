/** @jsx React.DOM */

var QueueItem = React.createClass({

   render: function() {
       var idref = "queue_item"+this.props.key;
       var idhref = "#"+idref; 
       var fields = [];

       if (this.props.data.fields) {
         var flds = this.props.data.fields;
         for (field_name in flds) {
         	console.log(idref)
             var field = flds[field_name];
             var label = field.label;
             var value = field.default_value;
             fields.push( <EditableFieldQ key={field_name} id={idref} name={label} value={value} /> );
         }
       }

 		
       return <div className="panel panel-default">
                <div className="panel-heading clearfix">
                  <b className="panel-title pull-left">
                    <a data-toggle="collapse" data-parent="#accordion" href={idhref}>
                     {this.props.data.text}
                    </a>
                  </b>
               </div>
               <div id={idref} className="panel-collapse collapse out">
                 <div className="panel-body">
                   {fields}
                 </div>
               </div>
             </div>
     },
});

var Queue = React.createClass({

     run_queue: function() {
     	console.log("****************************")
     	//console.log(this.state.data)
         //console.log( document.getElementById("queue_item1"))
		//console.log(this.props.queue_items) //this is an array [sample; dc; sample; dc;....]
		
	    $.ajax({
        	url: '/run_queue',
       		data: "nope",
    		type: 'GET',
        	success: function(res) {
            //alert(res);
        	},
       		error: function(error) {
         		console.log(error);
        	},
   		});
     },
     
         
     getDefaultProps: function() {
       return { "queue_items": [] }
     }, 
     
     _add_queue_item: function(item) {
       this.props.queue_items.push(item);
       this.forceUpdate();
     },
     
     
     componentWillMount: function() {
        window.app_dispatcher.on("queue:new_item", this._add_queue_item);
     },
     componentWillUnMount: function() {
       window.app_dispatcher.off("queue:new_item", this._add_queue_item);
     },
     
     render: function() {
         var queue_items = [];
         var execute_queue_button = "btn btn-xs";
         for (i in this.props.queue_items) {
           var item = this.props.queue_items[i];
           queue_items.push(<QueueItem data={item} key={i}/>); 
         }         
		
         if (queue_items.length>0) execute_queue_button += " btn-primary";

         return <div className="panel panel-default"  id="Queue">
                  <div className="panel-heading clearfix">
                    <b className="panel-title pull-left">Tasks</b>
                    <div className="btn-group pull-right">
                      <button type="button" className={execute_queue_button} id="RunQueue" onClick={this.run_queue} >Run Queue</button>
                    </div>
                  </div>
                  <div className="panel-body">
                    { queue_items }
                  </div>
               </div>
    }
});


var EditableFieldQ = React.createClass({
	
   componentDidMount: function() {
      $(this.refs.editable.getDOMNode()).editable();
   }, 

   render: function() {
       return <p>{this.props.name}: <a href="#" ref="editable"  data-name={this.props.name} data-pk={this.props.id} data-url="/sample_field_update" data-type="text" data-title="Edit value">{this.props.value}</a></p>
   } 
})
