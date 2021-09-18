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
    else if (page == 'view') {
      document.querySelector('.add-vote-history').addEventListener('click', addVoteHistory);
      document.querySelector('.set-current-story').addEventListener('click', setCurrentStory);
      document.querySelector('.toggle-voting').addEventListener('click', toggleVoting);
      document.querySelector('.myvote').addEventListener('click', vote);
    }
  });

  
function vote(e) {
  const current_user_id = document.getElementById('current_user_id').getAttribute('value');
  const game_id = document.getElementById('game-id').getAttribute('value');
  var current_vote = e.target.innerHTML;
  var my_vote = document.getElementById(`${current_user_id}`).children[1];

  // console.log('vote');
  // console.log('current_user_id: ' + current_user_id);
  // console.log('game_id: ' + game_id);
  // console.log('current_vote: ' + current_vote);
  // console.log('my_vote.innerHTML: ' + my_vote.innerHTML);

  const xhr = new XMLHttpRequest();
  xhr.open('PUT', `/users/${current_user_id}`, true);
 
  xhr.onload = function() {
    if(this.status === 200) {
      const response_json = JSON.parse(this.response);
      my_vote.innerHTML = response_json.vote;
    }
  }
  
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'vote': `${current_vote}`, 'current_game_id': `${game_id}`}));
  e.preventDefault();
}


function addVoteHistory(e) {
  const story = document.getElementById('current-story-modal').value;
  const vote = document.getElementById('vote').value;
  const game_id = document.getElementById('game-id').getAttribute('value');

  // console.log('addHistory');
  // console.log('game_id: ' + game_id);
  // console.log('story: ' + story);
  // console.log('vote: ' + vote);   

  const xhr = new XMLHttpRequest();
  xhr.open('POST', `/games/${game_id}/history`, true);
  
  xhr.onload = function() {
    if(this.status === 200) {
      const response_json = JSON.parse(this.response);
      var history_tbody = document.getElementById('history-tbody');
      var row = history_tbody.insertRow(0);
      var story_cell = row.insertCell(0);
      var vote_cell = row.insertCell(1);
      story_cell.innerHTML = response_json['story'];
      vote_cell.innerHTML = response_json['value'];
    }
  }
  
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
  xhr.open('PUT', `/games/${game_id}`, true);
  
  xhr.onload = function() {
    if(this.status === 200) {
      const response_json = JSON.parse(this.response);
      document.getElementById('current-story').innerHTML = response_json['story'];
      // change the default story on the AddHistory modal
      document.getElementById('current-story-modal').value = response_json['story'];
    }
  }
  
  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'story': `${story}`}));
  e.preventDefault();
}


function toggleVoting(e) {
  const current_user_id = document.getElementById('current_user_id').getAttribute('value');
  const game_id = document.getElementById('game-id').getAttribute('value');
  var toggle_voting_btn = document.getElementById('toggle-voting-btn');

  // console.log('toggleVoting');
  // console.log('current_user_id: ' + current_user_id);
  // console.log('game_id: ' + game_id);
  // console.log('toggle_voting_btn: ' + toggle_voting_btn.innerHTML);

  const xhr = new XMLHttpRequest();
  xhr.open('PUT', `/games/${game_id}/togglevote`, true);

  xhr.onload = function() {
    if(this.status === 200) {
      const response_json = JSON.parse(this.response);

      // Toggle the view voting button
      if (response_json.is_voting) {
        toggle_voting_btn.innerHTML = "visibility_off";
      }
      else {
        toggle_voting_btn.innerHTML = "visibility";
      }
    }
  }

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
  xhr.open('POST', `/games`, true);
 
  xhr.onload = function() {
    if(this.status === 200) {
      var gametable = document.querySelector('.games');
      const hl = document.createElement('a');
      var row = gametable.insertRow(0);
      var cell1 = row.insertCell(0);
      var cell2 = row.insertCell(1);
      const response_json = JSON.parse(xhr.responseText);
      let current_datetime = new Date(response_json.last_used_date);

      hl.href = 'view/' + response_json.id;
      hl.appendChild(document.createTextNode(response_json.name));
      cell1.appendChild(hl);
      cell2.innerHTML = formatDateTime(current_datetime);
    }
  }
  

  xhr.setRequestHeader('Content-Type', 'application/json');
  xhr.send(JSON.stringify({'name': `${game}`, 'owner_id': `${current_user_id}`}));
  e.preventDefault();
}
