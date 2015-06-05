/** @jsx React.DOM */



var sample_centring = { energy: { label: "Energy", default_value: 123984 },
                        resolution: { label: "Resolution", default_value: 1.150 },
                        trans: { label: "Transmission", default_value: 100.0 },
                        beam_size: { label: "Beam Size", default_value: 120 } } 

var SampleVideo = React.createClass({
     getDefaultProps: function() {
         return { disabled: true };
     },
  
     componentWillMount: function() {
        window.app_dispatcher.on("queue:new_item", this._add_queue_item);
     },
     componentWillUnMount: function() {
       window.app_dispatcher.off("queue:new_item", this._add_queue_item);
     },
 
     render: function() {
         return <div className="panel panel-default">
                  <div className="panel-heading clearfix">
                    <b className="panel-title pull-left">Sample Video</b>
                  </div>
                    	<div className="panel-body">
		    				<EditableField_sample key="light" id="light" name="Light" value="1.00" />
                      		<EditableField_sample key="focus" id="focus" name="Focus" value="-0.640" />
                     		<EditableField_sample key="frontlight" id="frontlight" name="Front light" value="2.00" /> 
                      		<EditableField_sample key="zoom" id="zoom" name="Zoom" value="1" />   
                 	</div>
                </div>
    }
});

var SampleVideoInd = React.createClass({
     getDefaultProps: function() {
         return { disabled: true };
     },
  
     componentWillMount: function() {
        window.app_dispatcher.on("queue:new_item", this._add_queue_item);
     },
     componentWillUnMount: function() {
       window.app_dispatcher.off("queue:new_item", this._add_queue_item);
     },
 
     render: function() {
         return <div className="panel panel-default">
                  <div className="panel-heading clearfix">
                    <b className="panel-title pull-left">Current</b>
                  </div>
                    	<div className="panel-body">
							<p class="text-left" id="light" >und</p>				
							<p class="text-left" id="focus" >und</p>
							<p class="text-left" id="frontlight" >und</p>
							<p class="text-left" id="zoom" >und</p>
                 	</div>
                </div>
    }
});



var EditableField_sample = React.createClass({
	
   componentDidMount: function() {
      $(this.refs.editable.getDOMNode()).editable();
   }, 

   render: function() {
       return <p>{this.props.name}: <a href="#" ref="editable"  data-name={this.props.name} data-pk={this.props.id} data-url="/beam_line_update" data-type="text" data-title="Edit value">{this.props.value}</a></p>
   } 
})



