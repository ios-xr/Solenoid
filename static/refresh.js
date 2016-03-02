(function(){
  'use strict';
  function getInfo(){
    var Table = document.getElementById("rib");
    var rows = Table.rows.length
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
        var json = JSON.parse(xhttp.responseText);
        var keys = Object.keys(json['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix']).length
        for (var i = 0; i <keys; i++){
          if (i < rows) {
            var table = document.getElementById("rib");
            var row = table.rows[i+1];
            var cell1 = row.cells[0];
            var cell2 = row.cells[1];
            cell1.innerHTML = json['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix'][i]['prefix'];
            cell2.innerHTML = json['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix'][i]['vrf-route']['segment-route-next-hop-table']['vrf-next-hop-next-hop-address'][0]['next-hop-address']; 
          } else {
            var table = document.getElementById("rib");
            var row = table.insertRow(i+1);
            var cell1 = row.insertCell(0);
            var cell2 = row.insertCell(1);
            cell1.innerHTML = json['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix'][i]['prefix'];
            cell2.innerHTML = json['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix'][i]['vrf-route']['segment-route-next-hop-table']['vrf-next-hop-next-hop-address'][0]['next-hop-address']; 
          }
        }
      }
    };
    xhttp.open('GET', '/get_rib_json', true);
    xhttp.send();
  }
  function getInfo1(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
        var exa = JSON.parse(xhttp.responseText);
        document.getElementById("Peer_IP").innerHTML = exa['neighbor']['ip'];
        var counter = Object.keys(exa['neighbor']['message']['update']).length - 1
        var update = Object.keys(exa['neighbor']['message']['update'])[counter];
        document.getElementById("Update_Type").innerHTML = update;
        var nexthop = Object.keys(exa['neighbor']['message']['update'][update]['ipv4 unicast']);
        document.getElementById("Next_Hop").innerHTML = nexthop;
        var network = Object.keys(exa['neighbor']['message']['update'][update]['ipv4 unicast'][nexthop]);
        document.getElementById("Update_Network").innerHTML = network;
        var time = timeConverter(exa['time'])
        document.getElementById("Update_Time").innerHTML = time;
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
  setInterval(getInfo1, 5000);
  setInterval(getInfo, 10000);
}());

