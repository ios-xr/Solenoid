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
        if (keys<rows) {
          do {
            var table = document.getElementById("rib");
            table.deleteRow(keys + 1);
          } while (keys < rows);
        }
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
        var time = timeConverter(exa['time']);
        var old_time = Table.rows[rows_l+1].cells[4].innerHTML;
        if (time != old_time){
          var row = Table.insertRow(rows_l)
          row.insertCell(0).innerHTML = exa['neighbor']['ip'];
          var counter = Object.keys(exa['neighbor']['message']['update']).length - 1
          var update = Object.keys(exa['neighbor']['message']['update'])[counter];
          row.insertCell(1).innerHTML = update;
          var nexthop = Object.keys(exa['neighbor']['message']['update'][update]['ipv4 unicast']);
          row.insertCell(2).innerHTML = nexthop;
          var network = Object.keys(exa['neighbor']['message']['update'][update]['ipv4 unicast'][nexthop]);
          row.insertCell(3).innerHTML = network;
          row.insertCell(4).innerHTML = time;
        }
        if (rows_l > 6){
          Table.deleteRow(1)
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
  setInterval(getInfo1, 5000);
  setInterval(getInfo, 10000);
}());

