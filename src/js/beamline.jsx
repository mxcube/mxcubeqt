/** @jsx React.DOM */



var beamline_params = { energy: { label: "Energy", default_value: 123984 },
                        resolution: { label: "Resolution", default_value: 1.150 },
                        trans: { label: "Transmission", default_value: 100.0 },
                        beam_size: { label: "Beam Size", default_value: 120 } } 

var BeamLine = React.createClass({
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
                    <b className="panel-title pull-left">Beamline setup</b>
                  </div>
                    	<div className="panel-body">
		    				<EditableField_bl key="energy" id="energy" name="Energy" value="12.3984" />
                      		<EditableField_bl key="resolution" id="resolution" name="Resolution" value="1.150" />
                     		<EditableField_bl key="trans" id="transmission" name="Transmission" value="100.0" /> 
                      		<EditableField_bl key="beam_size" id="beam_size" name="Beam size" value="120.0" />
                      		<EditableField_bl key="apert_hor" id="apert_hor" name="Apert" value="1.0" />
                      		
                 	</div>
                </div>
    }
});

var BeamLineInd = React.createClass({
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
							<p class="text-left" id="energy" >und</p>				
							<p class="text-left" id="resol" >und</p>
							<p class="text-left" id="trans" >und</p>
							<p class="text-left" id="beamsize" >und</p>
							<p class="text-left" id="apert_hor" >und</p>
							
                 	</div>
                </div>
    }
});



var EditableField_bl = React.createClass({
	
   componentDidMount: function() {
      $(this.refs.editable.getDOMNode()).editable();
   }, 

   render: function() {
       return <p>{this.props.name}: <a href="#" ref="editable"  data-name={this.props.name} data-pk={this.props.id} data-url="/beam_line_update" data-type="text" data-title="Edit value">{this.props.value}</a></p>
   } 
})



