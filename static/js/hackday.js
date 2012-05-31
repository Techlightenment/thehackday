$(document).ready(function(){
  
  var smallGraphs = [];
  
  function Socket(parent, word, endpoint) {
    //biggraph
    this.parent = parent;
    this.target = $('#' + target);
    this.endpoint = endpoint;
    this.root = 'endpoint';
    this.socket = new WebSocket(this.root + '/' + this.endpoint);
    
    this.socket.onmessage = function(e){
      this.update(e.data);
    }
  }
  //5333
  Socket.prototype.update = function(data){
    var maxPoints = 400;
    // Munge data her to current flot data
    // Set max number of points
    var cdata = this.parent.flot.getData();
    
    _.each(cdata, function(d,i){
      var newPoint = [data.time, data.data[i]];
      
      d.concat(newPoint)
      
      if(d.length > maxPoints){
        d.slice(0, maxPoints - d.length);
      }
      
      this.parent.flot.update();
      this.parent.flot.draw();
    });
  }
  
  function Graph(word, target, endpoint){
    this.word = word;
    this.target = $('#' + target);
    this.flot = $.plot(
          this.target.find('.flot-container'),
          [],
          {}
        );
    
    this.socket = new Socket(this, word, endpoint);
    
  }

  _.each($('.small-graph'), function(v, i){
    var el = v,
        word = el.data.word,
        endpoint = el.data.endpoint;
    
    var g = new Graph(word, el, endpoint);
    
  })
  
});