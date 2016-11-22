(function(){
  'use strict';
  function getInfo(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
    var newData = ""
        var json = JSON.parse(xhttp.responseText);
        var keys = Object.keys(json['Cisco-IOS-XR-ip-static-cfg:router-static']['default-vrf']['address-family']['vrfipv4']['vrf-unicast']['vrf-prefixes']['vrf-prefix']).length
        for (var i = 0; i < keys; i++){
      newData += "<tr><td>" + json['Cisco-IOS-XR-ip-static-cfg:router-static']['default-vrf']['address-family']['vrfipv4']['vrf-unicast']['vrf-prefixes']['vrf-prefix'][i]['prefix'] + "</td>";
      newData += "<td>" + json['Cisco-IOS-XR-ip-static-cfg:router-static']['default-vrf']['address-family']['vrfipv4']['vrf-unicast']['vrf-prefixes']['vrf-prefix'][i]['vrf-route']['vrf-next-hop-table']['vrf-next-hop-next-hop-address'][0]['next-hop-address'];
      newData += "</td></tr>\n"
    }

  $('#rib tbody').html(newData);

      }
    };
    xhttp.open('GET', '/get_rib_json', true);
    xhttp.send();
  }
  function getInfo1(){
    var Table = document.getElementById("exa");
    var rows_l = Table.rows.length
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
        var exa = JSON.parse(xhttp.responseText);
	console.log(exa);
        var time = timeConverter(exa['time']);
        var old_time = Table.rows[1].cells[4].innerHTML;
        if (time != old_time){
          var  row = Table.insertRow(1)
          row.style.color = exa['color'];
          row.insertCell(0).innerHTML = exa['peer_ip'];
          row.insertCell(1).innerHTML = exa['update_type'];
          row.insertCell(2).innerHTML = exa['nexthop'];
          row.insertCell(3).innerHTML = exa['network'];
          row.insertCell(4).innerHTML = time;
        }
      }
    };
    xhttp.open('GET', '/get_exa_json', true);
    xhttp.send();
  }
  function timeConverter(UNIX_timestamp){
    var a = new Date(UNIX_timestamp * 1000);
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var year = a.getFullYear();
    var month = months[a.getMonth()];
    var date = a.getDate();
    var hour = a.getHours();
    var min = a.getMinutes();
    var sec = a.getSeconds();
    var time = date + ' ' + month + ' ' + year + ' ' + hour + ':' + min + ':' + sec ;
    return time;
  }
  setInterval(getInfo1, 1000);
  setInterval(getInfo, 2000);
}());
function getprefix(){
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (xhttp.readyState == 4 && xhttp.status == 200) {
  var newData = ""
      var lines = xhttp.responseText.split('\n');
      for (var line in lines){
    newData += "<tr><td>" + lines[line] + "</td>";
  }

$('#prefix tbody').html(newData);

    }
  };
  xhttp.open('GET', '/prefix_change', true);
  xhttp.send();
}
$(document).ready(getprefix)
