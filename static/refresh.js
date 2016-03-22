(function(){
  'use strict';
  function getInfo(){
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
      if (xhttp.readyState == 4 && xhttp.status == 200) {
    var newData = ""
        var json = JSON.parse(xhttp.responseText);
        var keys = Object.keys(json['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix']).length
        for (var i = 0; i < keys; i++){
      newData += "<tr><td>" + json['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix'][i]['prefix'] + "</td>";
      console.log(json);

      newData += "<td>" + json['Cisco-IOS-XR-ip-static-cfg:vrf-prefixes']['vrf-prefix'][i]['vrf-route']['vrf-next-hop-table']['vrf-next-hop-next-hop-address'][0]['next-hop-address'];
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
        var time = timeConverter(exa['time']);
        var old_time = Table.rows[1].cells[4].innerHTML;
        if (time != old_time){
          var  row = Table.insertRow(1)
          row.insertCell(0).innerHTML = exa['neighbor']['ip'];
          var counter = Object.keys(exa['neighbor']['message']['update']).length - 1
          var update = Object.keys(exa['neighbor']['message']['update'])[counter];
          row.insertCell(1).innerHTML = update;
          var nexthop = Object.keys(exa['neighbor']['message']['update'][update]['ipv4 unicast']);
          if (counter == 0){
            row.insertCell(2).innerHTML = " ";
            var network = Object.keys(exa['neighbor']['message']['update'][update]['ipv4 unicast'][nexthop]);
            row.insertCell(3).innerHTML = nexthop;
            row.insertCell(4).innerHTML = time;
         } else {
            row.insertCell(2).innerHTML = nexthop;
            var network = Object.keys(exa['neighbor']['message']['update'][update]['ipv4 unicast'][nexthop]);
            row.insertCell(3).innerHTML = network;
            row.insertCell(4).innerHTML = time;
         }
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
