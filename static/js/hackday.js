$(document).ready(function(){
  
  var smallGraphs = [];
  
  function Socket(parent, word, endpoint) {
    //biggraph
    var self = this;
    this.parent = parent;
    this.endpoint = endpoint;
    this.root = "ws://" + location.host + "/" + endpoint + "?hashtag=" + word;
    
    this.socket = new WebSocket(this.root);
    this.socket.onmessage = function(e){
      this.update(e.data);
    }.bind(this)
  }
  //5333
  Socket.prototype.update = function(data){
    var maxPoints = 300,
        t = new Date().getTime(),
        data = JSON.parse(data),
        flot = this.parent.flot;
    // Munge data her to current flot data
    // Set max number of points
    var cdata = flot.getData();
      
    _.each(cdata, function(d,i){
      var newPoint = [t, data[i]];
      
      d.data.push(newPoint);
      console.log(d.data.length)
      console.log(maxPoints);
      if(d.data.length > maxPoints){
        console.log(d.data.length);
        d.data = d.data.slice(d.data.length - maxPoints, d.data.length);
        console.log(d.data.length);
      }
    });
    
    flot.setData(cdata);
    flot.setupGrid();
    flot.draw();
    var start = cdata[0].data[0][0];
    
    var range = Math.round(((t - start) / 1000));
    
    this.parent.target.find('.timerange').html('In the last ' + range + ' seconds.');
  }
  
  function Graph(word, el, endpoint, neg){
    var t = new Date().getTime();
    this.word = word;
    this.target = el;
    
    var opts = {
        xaxis: {
        show: false
      },
      yaxis: {
        min: 0
      }
    }
    
    if(neg){
      delete opts.yaxis.min
    }
    
    this.flot = $.plot(
          this.target.children('.flot-container'),
          [[[t, 0]], [[t, 0]], [[t, 0]], [[t, 0]]],
          opts
        );
    this.socket = new Socket(this, word, endpoint);
    
  }

  _.each($('.small-graph'), function(v, i){
    var el = $(v),
        word = el.data().word,
        neg = el.data().neg,
        endpoint = el.data().endpoint;
    
    var g = new Graph(word, el, endpoint, neg);
  })
  
  _.each($('.big-graph'), function(v, i){
    var el = $(v),
        word = el.data().word,
        neg = el.data().neg,
        endpoint = el.data().endpoint;
    
    var g = new Graph(word, el, endpoint, neg);
  })
  
});