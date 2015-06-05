/** @jsx React.DOM */

var Search = React.createClass({
     render: function() {
         return <div className="search input-group" role="search">
                  <input type="search" className="form-control" placeholder="Search"/>
                  <span className="input-group-btn">
                    <button className="btn btn-default" type="button">&nbsp;
                      <span className="glyphicon glyphicon-search"></span>
                      <span className="sr-only">Search</span>
                    </button>
                  </span>
                </div>
    }
});

var SampleList = React.createClass({
     getInitialState: function() {
       return { "authorized_samples": [] }
     },

     check_sc: function() {
       this.setState({ "authorized_samples": [444182,444185] });
     },

     render: function() {
        var id = 0;
        var samples = this.props.samples.map(function(sample) {
             id += 1;
             var can_mount = (this.state.authorized_samples.indexOf(sample.sampleId) >= 0);
             return <Sample sample={sample} key={id} can_mount={can_mount}/>;
        }.bind(this));
        return <div>
                 <Search/>
                 <button type="button" className="btn btn-primary btn-block top7" onClick={this.check_sc}>
                   <span className="glyphicon glyphicon-refresh"></span> Check sample changer
                 </button>
                 <div className="panel-group top5">{samples}</div>
               </div>
     },
});

var Sample = React.createClass({
     add_mount_task: function() {
       window.app_dispatcher.trigger("queue:new_item", { "kind":"sample", "text": "Mount "+this.props.sample.sampleName, fields:{} });
       //everytime a new sample is loaded into the queue its name is sent to the server
       $.ajax({
       //error: function(XMLHttpRequest, textStatus, errorThrown) { alert(textStatus) },
       url: 'sample_field_update',
       type: 'POST',
       data: { "Type":"Sample", "Name":this.props.sample.sampleName },
       dataType: "json" });  
     },

     render: function() {
       var idref = "sample"+this.props.key;
       var idhref = "#"+idref;
       var fields = [];
       var fieldno = 0;
       var hiddenfields = ['sampleId', 'sampleName' ];

       for (field in this.props.sample) { 
           if (hiddenfields.indexOf(field) >= 0) continue;
           var value = this.props.sample[field];
           fields.push( <EditableField key={fieldno} sampleid={this.props.sample.sampleId} name={field} value={value} /> );
           fieldno += 1;
       }
       
       var mount_button = "";
       if (this.props.can_mount) {
         mount_button = <div className="btn-group pull-right">
                          <a href="#" className="btn btn-success btn-xs" onClick={this.add_mount_task}>Mount</a>
                        </div>
       } 

       return <div className="panel panel-default">
                <div className="panel-heading clearfix">
                  <b className="panel-title pull-left">
                    <a data-toggle="collapse" data-parent="#accordion" href={idhref}>
                     {this.props.sample.sampleName}
                    </a>
                  </b>
                  { mount_button }
               </div>
               <div id={idref} className="panel-collapse collapse out">
                 <div className="panel-body">
                   {fields}
                 </div>
               </div>
             </div>
     },

});

var EditableField = React.createClass({
	
   componentDidMount: function() {
      $(this.refs.editable.getDOMNode()).editable();
   }, 

   render: function() {
       return <p>{this.props.name}: <a href="#" ref="editable"  data-name={this.props.name} data-pk={this.props.sampleid} data-url="/sample_field_update" data-type="text" data-title="Edit value">{this.props.value}</a></p>
   } 
})
