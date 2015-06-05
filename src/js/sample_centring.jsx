/** @jsx React.DOM */



var sample_centring = { energy: { label: "Energy", default_value: 123984 },
                        resolution: { label: "Resolution", default_value: 1.150 },
                        trans: { label: "Transmission", default_value: 100.0 },
                        beam_size: { label: "Beam Size", default_value: 120 } } 

var SampleCentring = React.createClass({
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
                    <b className="panel-title pull-left">Sample Position</b>
                  </div>
                    	<div className="panel-body">
		    				<EditableField_sample key="omega" id="omega" name="Omega" value="250.00" />
                      		<EditableField_sample key="kappa" id="kappa" name="Kappa" value="0.00" />
                     		<EditableField_sample key="phi" id="phitablezaxis" name="Phi" value="0.00" /> 
                      		<EditableField_sample key="holder" id="holder" name="Holder length" value="21.627" />   
                 	</div>
                </div>
    }
});

var SampleCentringInd = React.createClass({
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
							<p class="text-left" id="omega" >und</p>				
							<p class="text-left" id="kappa" >und</p>
							<p class="text-left" id="phitablezaxis" >und</p>
							<p class="text-left" id="holder" >und</p>
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



