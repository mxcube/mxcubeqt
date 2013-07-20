// Permission is hereby granted, free of charge, to any person
// obtaining a copy of this software and associated documentation
// files (the "Software"), to deal in the Software without restriction,
// including without limitation the rights to use, copy, modify, merge,
// publish, distribute, sublicense, and/or sell copies of the Software,
// and to permit persons to whom the Software is furnished to do so,
// subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be
// included in all copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
// ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
// TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
// PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
// SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
// OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
// OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
// WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

MouseApp.Python = function(element, options) {
  this.element = $(element);
  this.setOptions(options);
  if ( this.options.init ) {
      this.init = this.options.init;
  }
  this.initWindow();
  this.setup();
};

$.extend(MouseApp.Python.prototype, MouseApp.Terminal.prototype, {
    fireOffCmd: function(cmd, func) {
      var python = this;
      $.ajax({
        error: function(XMLHttpRequest, textStatus, errorThrown) {
          if (XMLHttpRequest.status == 404) {
            python.reply({error: "Server is temporarily unavailable"});
          } else if (XMLHttpRequest.status == 500) {
            python.reply({error: "500 Internal server error"});
          } else {
            python.reply({error: "in fireOffCmd.error callback, status="+textStatus+", error="+errorThrown+", response text="+XMLHttpRequest.responseText});
          }
        },
        url: 'command',
        type: 'GET',
        success: func,
	data: { "client_id": python.session_id, "code": cmd },
        dataType: 'json'
      });
    },

    abortExecution: function() {
      var python = this;
      $.ajax({
        url: 'abort',
        type: 'GET',
        data: { "client_id": python.session_id },
        dataType: 'json'
    });
   },

    askForOutput: function() {
      var python = this;
      $.ajax({
        error: function(XMLHttpRequest, textStatus, errorThrown) {},
        url: 'output_request',
        type: 'GET',
        success: function(output) { python.write(output); },
        complete: function() { python.askForOutput(); },
        data: { "client_id": python.session_id },
        dataType: 'json'
    });
   },

    askForLogMessages: function() {
      var python = this;
      $.ajax({
        error: function(XMLHttpRequest, textStatus, errorThrown) {},
        url: 'log_msg_request',
        type: 'GET',
        success: function(msg) { jQuery("#logger:first").append("<p>"+msg+"</p>"); },
        complete: function() { python.askForLogMessages(); },
        data: { "client_id": python.session_id },
        dataType: 'json'
    });
   },

   askForHistory: function() {
      var python = this;
      $.ajax({
        error: function(XMLHttpRequest, textStatus, errorThrown) {},
        url: 'history_request',
        type: 'GET',
        success: function(history) {
                   python.history = history;
                   python.historyNum = history.length;
                   python.backupNum = python.historyNum;
                },
        data: { "client_id": python.session_id },
        dataType: 'json'
    });
   },

   askForCompletion: function(text) {
      var python = this;
      $.ajax({
        error: function(XMLHttpRequest, textStatus, errorThrown) {},
        url: 'completion_request',
        type: 'GET',
        success: function(res) {
                   var possibilities = res.possibilities
                   var cmd = res.cmd
                   if (possibilities.length == 0) {
                     python.typingOn();
                     python.cursorOn(); 
                     return;
                   }  
                   if (possibilities.length == 1) {
                     python.clearCommand();
                     python.write(cmd);
                     python.cursorOn();
                     python.typingOn();
                   } else {
                     python.cursorOff();
                     python.advanceLine();
                     var completion_text = "";
                     for(var i=0; i<possibilities.length; i++) {
                       if ((i>0) && ((i % 6) == 0)) {
                         completion_text = completion_text + possibilities[i] + "\n";
                       } else {
                         completion_text = completion_text + possibilities[i] + "\t";
                       }
                     }
                     completion_text += "\n";
                     python.write(completion_text);
                     python.advanceLine();
                     python.prompt();
                     python.write(cmd);
                     python.cursorOn();
                  }
                },
        data: { "client_id": python.session_id, "text": text },
        dataType: 'json'
    });
   },

   reply: function(res) { 
      this.executing = false;

      if (res.error == "EOF") {
          term = this;
          term.inhibitKeyboardHandling(true);
          term.cursorOff();
          $("#python").append("<textarea id='code' cols='120' rows='20'>"+res.input+"</textarea>");
          $("#python").append("<button id='exec_code' type='button'>Execute</button><button id='close_code' type='button'>Close</button>");
          var editor = new CodeMirrorUI(document.getElementById("code"), { buttons:['undo', 'redo','jump', 'reindent'] }, { autofocus: true });
          $("#close_code").click(function() {
              editor.toTextArea();
              $("#code").remove();
              $("#exec_code").remove();
              $("#close_code").remove();
              term.inhibitKeyboardHandling(false);
              term.advanceLine();
              term.prompt(); term.cursorOn(); 
          });
          $("#exec_code").click(function() {
              editor.toTextArea();
              var code_text = document.getElementById("code").value;
              $("#code").remove();
              $("#exec_code").remove();
              $("#close_code").remove();
              term.inhibitKeyboardHandling(false);
              term.advanceLine();
              term.write(code_text);
              term.executing = true;
              term.fireOffCmd(code_text, (function(res) { term.reply(res) }));
          });
          return; 
      }

      if (res.error.length > 0) {
         if (res.error == "CTRLC") {
           this.write("\033[1;4m<ctrl c>\033[m\n");
         } else {
           this.write("\033[1;4m"+res.error+"\033[m\n");
         }
      }
  
      this.cursorOff();
      this.advanceLine();
      this.cursorOn();
      this.prompt();
    },

    onKeyEnter: function() {
        this.typingOff();
        var cmd = this.getCommand();
        if (cmd) {
          this.history[this.historyNum] = cmd;
          this.backupNum = ++this.historyNum;
        }
        this.commandNum++;
        this.advanceLine();
        if (cmd) {
          var term = this;
          this.executing = true;
          this.fireOffCmd(cmd, (function(res) { term.reply(res) }));
        } else {
          this.write("\n");
          this.prompt();
        }
    },
 
    onKeyTab: function() {
      this.typingOff();
      var cmd = this.getCommand();
      if (! cmd) { cmd = ""; }
      this.askForCompletion(cmd);
    },
 
    onCtrlC: function() {
      var term = this;
      if (this.executing) {
        this.typingOff();
        this.abortExecution();
      } 
   } 
});

