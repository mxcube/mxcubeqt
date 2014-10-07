
function parseServerString(servstr) {

   data = {};

   arr = servstr.split(";")

   for (val in arr) {
       pair = arr[val].split(":"); 
       data[pair[0]] = pair[1];
   } 
   return(data);
}
  
