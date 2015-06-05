/** @jsx React.DOM */



var diff_params = { energy: { label: "Energy", default_value: 123984 },
                        resolution: { label: "Resolution", default_value: 1.150 },
                        trans: { label: "Transmission", default_value: 100.0 },
                        beam_size: { label: "Beam Size", default_value: 120 } } 

var Diff = React.createClass({
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
                    <b className="panel-title pull-left">Diffractometer</b>
                  </div>
                    	<div className="panel-body">
                    	<canvas width="200" height="100" id="sample_ova"> <p>Canvas froga</p> </canvas>
						<button className="btn-group pull-right" id="collect_button"> <a>collect</a> </button>
						<button className="btn-group pull-right" id="lightin"> <a>lightin</a> </button>
						<button className="btn-group pull-right" id="lightout"> <a>lightout</a> </button>
						<button className="btn-group pull-right" id="zoom"> <a>zoom</a> </button>
						<button className="btn-group pull-right" id="set_light_level"> <a>set_light_level</a> </button>
						<button className="btn-group pull-right" id="centre_button"> <a>centre_button</a> </button>
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



