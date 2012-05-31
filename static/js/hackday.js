window.chosenGraph = false

$(document).ready(function(){
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

  
  Socket.prototype.update = function(data){
    var maxPoints = 75,
        t = new Date().getTime(),
        data = JSON.parse(data),
        flot = this.parent.flot;
    // Munge data her to current flot data
    // Set max number of points
    var cdata = flot.getData();
      
    _.each(cdata, function(d,i){
      var newPoint = [t, data[i]];
      
      d.data.push(newPoint);
      if(d.data.length > maxPoints){
        d.data = d.data.slice(d.data.length - maxPoints, d.data.length);
      }
    });
    
    flot.setData(cdata);
    flot.setupGrid();
    flot.draw();
//    var start = cdata[0].data[0][0];
//    
//    var range = Math.round(((t - start) / 1000));
//    
//    this.parent.target.find('.timerange').html('In the last ' + range + ' seconds.');
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
      opts.yaxis = {
          min: -1,
          max: 1
      }
    }
    
    this.flot = $.plot(
          this.target.children('.flot-container'),
          [
           {
             color: '#00d618',
             data: [t, 0]
           }, 
           {
             color: '#f00',
             data: [t, 0]
           },  
           {
             color: '#0015ff',
             data: [t, 0]
           }, 
           {
             color: '#000',
             data: [t, 0]
           }
          ],
          opts
        );
    this.socket = new Socket(this, word, endpoint);
    
  }

  function TweetSocket(parent, word) {
    
    var self = this;
    this.parent = parent;
    
    this.endpoint = 'tweets';
    this.root = "ws://" + location.host + "/" + this.endpoint + "?hashtag=" + word;

    this.socket = new WebSocket(this.root);
    this.socket.onmessage = function(e){
      this.update(e.data);
      console.log(JSON.parse(e.data))
    }.bind(this);
 
  }
  
  TweetSocket.prototype.update = function(data){
    data = JSON.parse(data);
    
    var pos = this.parent.el.find('.tweet-positive');
    var neg= this.parent.el.find('.tweet-negative');
    var xtra = 'badge-success';
    var temp = '<div class="twitter-ind pam"><div class="mbm"><img src="<%= pic %>"/><span class="badge <%= badge%>"><%= sent%></span></div>' +
               '<div style="clear:both"><p><%= msg%></p></div></div>'
    var data = {
      pic: data[3],
      sent: data[0],
      msg: data[2]
    }
    
    if(data.sent > 0){
      data['badge'] = 'badge-success'
      var template = _.template(temp, data);
      pos.prepend(template);
    } else {

      data['badge'] = 'badge-important'
      var template = _.template(temp, data);
      neg.prepend(template);
    }
  }
  
  TweetStream.prototype.changeSocket = function(word){
    this.socket.socket.close();
    this.el.find('.tweet-positive').html("");
    this.el.find('.tweet-negative').html("");
    this.socket = new TweetSocket(this, word);
  }
  
  function TweetStream(el, word){
    this.el = $('#' + el);
    this.socket = new TweetSocket(this, word);
  }
  
  var initial = $($('.small-graph')[0]).data().word
  
  window.tweetLog = new TweetStream('twitterStream', initial);

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
  });
  
  $('.btn-graph').click(function(){
    var word = $(this).data().word;
    window.tweetLog.changeSocket(word)
  });
});