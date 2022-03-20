document.addEventListener('DOMContentLoaded', function() {
    var path = window.location.pathname;
    var list = path.split("/");
    var page = list[list.length - 2];

    // console.log('addEventListener');
    // console.log('path: ' + path);
    // console.log('list: ' + list);
    // console.log('page: ' + page); 

    // Load only the events for the current page
    if (page == 'index' || page == '') {
      document.querySelector('.add-game').addEventListener('click', addGame);
    }
    else if (page == 'game') {
      document.querySelector('.add-vote-history').addEventListener('click', addVoteHistory);
      document.querySelector('.set-current-story').addEventListener('click', setCurrentStory);
      document.querySelector('.toggle-voting').addEventListener('click', toggleVoting);
      document.querySelector('.my-vote').addEventListener('click', vote);
      document.querySelector('.add-invite').addEventListener('click', addInvite);

      // Subscribe to the mqtt channel to receive any game_state changes---------------
      // console.log('Connecting mqtt client')
      const clientId = 'mqttjs_' + Math.random().toString(16).substr(2, 8);
      client = new Paho.MQTT.Client("broker.hivemq.com", Number(8000), clientId);

      // set callback handlers
      client.onConnectionLost = onConnectionLost;
      client.onMessageArrived = onMessageArrived;

      // connect the client
      client.connect({onSuccess:onConnect});

      // called when the client connects
      function onConnect() {
        console.log(`onConnect()`)
        game_id = document.getElementById('game-id').getAttribute('value');
        console.log(`onConnect() - subscribing to poker/${game_id}`);
        client.subscribe(`poker/game/${game_id}`);
      }

      // called when the client loses its connection
      function onConnectionLost(responseObject) {
        if (responseObject.errorCode !== 0) {
          console.log("onConnectionLost:"+responseObject.errorMessage);
          // alert('You just lost your connection (sorry), refresh after your internet as been resotred.');
        }
      }

      // called when a message arrives
      function onMessageArrived(message) {
        update_view_ui(message.payloadString);
      }

    }
})


function update_view_ui(game_state) {
  console.log('update_ui(game_state):' + JSON.stringify(game_state, null, 2));
  game_state_json = '';

  // trap and skip any invalid json passed in
  try {
    game_state_json = JSON.parse(game_state);
  } catch(e) {
    console.log(e);
    return;
  }

  // Update the Toggle button and vote visibility for each player -------------
  // console.log('is_voting:' + game_state_json.is_voting);

  if (game_state_json.is_voting) {
    document.getElementById('toggle-voting-btn').innerHTML = "visibility_off";
  }
  else {
    document.getElementById('toggle-voting-btn').innerHTML = "visibility";
  }

  // Update the Current Story -----------------------------------------------
  // console.log('story:' + game_state_json.story);
  document.getElementById('current-story').innerHTML = game_state_json.story;  // on page display
  document.getElementById('current-story-modal').value = game_state_json.story;  // default when adding history

  // Update the History list -----------------------------------------------
  // console.log('history: ' + JSON.stringify(game_state_json.history, null, 2))
  tbody = "";

  for (let [key, value] of Object.entries(game_state_json.history)) {
    // console.log(`history - ${key}: ${JSON.stringify(value, null, 2)}`);
    history_row = `<tr><td>${value.story}</td><td>${value.value}</td></tr>`;
    tbody = tbody + history_row;
  }

  // console.log('tbody:' + tbody);
  document.getElementById('history').innerHTML = tbody;

  // Player joined/left, voted or voting toggled ---------------------------
  // console.log('players:' + JSON.stringify(game_state_json.players, null, 2));
  tbody = "";

  for (let [key, value] of Object.entries(game_state_json.players)) {
    // console.log(`player - ${key}: ${JSON.stringify(value, null, 2)}`);

    if (game_state_json.is_voting) {
      if (value.vote == "") {
        player_row = `<tr id=${key}><td class="username">${value.username}</td><td><i class="material-icons tiny">check_box_outline_blank</i></td></tr>`;    
      }
      else {
        player_row = `<tr id=${key}><td class="username">${value.username}</td><td><i class="material-icons tiny">check_box</i></td></tr>`;   
      }
    }
    else {
      player_row = `<tr id=${key}><td class="username">${value.username}</td><td class="vote">${value.vote}</td></tr>`;
    }
    tbody = tbody + player_row;
  }

  // console.log('tbody:' + tbody);
  document.getElementById('players').innerHTML = tbody;

}
  

function vote(e) {
  const current_user_id = document.getElementById('current_user_id').getAttribute('value');
  const game_id = document.getElementById('game-id').getAttribute('value');
  var current_vote = e.target.innerHTML;

  console.log('vote');
  console.log('current_user_id: ' + current_user_id);
  console.log('game_id: ' + game_id);
  console.log('current_vote: ' + current_vote);

  const xhr = new XMLHttpRequest();
  xhr.open('PUT', `/api/users/${current_user_id}/vote`, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'vote': `${current_vote}`, 'current_game_id': `${game_id}`}));
  e.preventDefault();
}


function addInvite(e) {
  const email = document.getElementById('email').value;
  const game_id = document.getElementById('game-id').getAttribute('value');

  console.log('addInvite');
  console.log('game_id: ' + game_id);
  console.log('email: ' + email);   

  const xhr = new XMLHttpRequest();
  xhr.open('POST', `/api/players`, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'game_id': `${game_id}`,'email': `${email}`}));
  e.preventDefault();    
}



// parser.add_argument('user_id', type=str, required=True, help='user_id problem (required)')
// parser.add_argument('game_id', type=str, required=True, help='game_id problem (required)')
// parser.add_argument('invite_token', type=str, required=True, help='invite_token problem (required)')

// parser.add_argument('invite_date', type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f'), required=False, help='invite_date problem (not required)')
// parser.add_argument('is_playing', type=bool, required=False, help='is_playing problem (not required)')
// parser.add_argument('email', type=str, required=False, help='email problem (not required)')
// parser.add_argument('vote', type=str, required=False, help='vote problem (not required)')
// parser.add_argument('vote_date', type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f'), required=False, help='vote_date problem (not required)')
// parser.add_argument('last_used_date', type=lambda s: datetime.strptime(s, '%Y-%m-%d %H:%M:%S.%f'), required=False, help='last_used_date problem (not required)')





function addVoteHistory(e) {
  const story = document.getElementById('current-story-modal').value;
  const vote = document.getElementById('vote').value;
  const game_id = document.getElementById('game-id').getAttribute('value');

  // console.log('addHistory');
  // console.log('game_id: ' + game_id);
  // console.log('story: ' + story);
  // console.log('vote: ' + vote);   

  const xhr = new XMLHttpRequest();
  xhr.open('POST', `/api/games/${game_id}/history`, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'story': `${story}`, 'value': `${vote}`}));
  e.preventDefault();    
}


function setCurrentStory(e) {
  const story = document.getElementById('story').value;
  const game_id = document.getElementById('game-id').getAttribute('value');

  // console.log('setCurrentStory');
  // console.log('game_id: ' + game_id);
  // console.log('story: ' + story);

  const xhr = new XMLHttpRequest();
  xhr.open('PUT', `/api/games/${game_id}/setstory`, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'story': `${story}`}));
  e.preventDefault();
}


function toggleVoting(e) {
  const game_id = document.getElementById('game-id').getAttribute('value');

  // console.log('toggleVoting');
  // console.log('game_id: ' + game_id);

  const xhr = new XMLHttpRequest();
  xhr.open('PUT', `/api/games/${game_id}/togglevote`, true);
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send();
  e.preventDefault();
}


// yyyy-mm-dd hh:mm for the Games list
function formatDateTime(date) {
  var d = new Date(date),
      month = '' + (d.getMonth() + 1),
      day = '' + d.getDate(),
      year = d.getFullYear(),
      hours = d.getHours(),
      minutes = d.getMinutes();

  return month.padStart(2, '0') + "/" + day.padStart(2, '0') + " " + hours + ":" + minutes;
}


function addGame(e) {
  const game = document.getElementById('game').value;
  const current_user_id = document.getElementById('current_user_id').getAttribute('value');

  // console.log('addGame');
  // console.log('game: ' + game);
  // console.log('current_user_id: ' + current_user_id);

  const xhr = new XMLHttpRequest();
  xhr.open('POST', `/api/games`, true);
 
  xhr.onload = function() {
    if(this.status === 200) {
      var gametable = document.querySelector('.games');
      var hl = document.createElement('a');
      console.log('h1-1', h1)
      var row = gametable.insertRow(0);
      var cell1 = row.insertCell(0);
      var cell2 = row.insertCell(1);
      const response_json = JSON.parse(xhr.responseText);
      let current_datetime = new Date(response_json.last_used_date);

      hl.href = 'game/' + response_json.id;
      console.log('h1-2', h1)
      hl.appendChild(document.createTextNode(response_json.name));
      cell1.appendChild(hl);
      cell2.innerHTML = formatDateTime(current_datetime);
    }
  }

  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'name': `${game}`, 'owner_id': `${current_user_id}`}));
  e.preventDefault();
}
