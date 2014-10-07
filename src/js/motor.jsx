/** @jsx React.DOM */

var Motor = React.createClass({
     
     getInitialState: function() {
        this.editing = false;
        var epos = new EventSource("/motor/"+this.props.mnemonic);
        epos.onmessage =  this.updateMotor;
        return { motorpos: 0, motstate: 'mottest unknown' }
     },

     moveMotor: function(event) {
        position = this.state.motorpos;
        $.post('/move?motor='+this.props.mnemonic+'&to='+position);
        this.editing = false;
     },

     handleChange: function(event) {
       this.editing = true;
       this.replaceState({motorpos: event.target.value});
     },

     render: function() {
       return <div>
              <span className="mottest">{this.props.name}:</span>
              <div><input className={this.state.motstate} value={this.state.motorpos} onChange={this.handleChange} /></div>
              <div className="mottest" onClick={this.moveMotor} >Go</div>
            </div>
     },

     updateMotor: function(e) {
        if ( this.editing ) return;
        if ( ! this.isMounted() ) return;

        motinfo = e.data;
        var motstate = this.state.motstate;

        // maybe we could use json here
        data = parseServerString(motinfo);

        // and state
        if (data.state == '2') {
            motstate = "mottest ready";
         } else if (data.state == '4' ) {
            motstate = "mottest moving";
         } else {
            motstate = "mottest unknown";
         }

        this.setState( {motorpos: data.position, motstate: motstate } );  
    },

});

