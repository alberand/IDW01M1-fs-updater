
/* Extract IP address regex */
var re_ip = RegExp('ip_ipaddr = [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')

console.log(re_ip.exec(document.getElementById('devconf').innerHTML))
