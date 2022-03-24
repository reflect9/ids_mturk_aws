
    
function ajaxGet(reqJson){
  /* Example usage. 
    ajaxGet({"action":"add", "PersonID":"asdf", "JSON":JSON.stringify({'a':1234,'b':234})})
  */
    $.getJSON('ajaxGet',reqJson, (data)=>{
      console.log(data);
    });
    
}
