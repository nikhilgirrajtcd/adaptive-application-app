function createList(){
    //will make an ajax call to backend
    //var xhttp = new XMLHttpRequest();
    //xhttp.open("GET", url, true)
    var itemList = ["Eggs", "Milk", "Bread", "Cereal", "Shampoo"];
    var priceList = ["€5", "€2.50", "€3", "€3", "€4"]
    var sizeList = ["small", "small", "medium", "medium", "large"]

    var i;
    for(i = 0; i < itemList.length;i++){
        var tr = document.createElement("tr");
        var itemCol = createListCol(itemList[i]);
        var sizeCol = createListCol(sizeList[i]);
        var priceCol = createListCol(priceList[i]);
        var notNowCol = createListCheckbox("notNow");
        var notInterestedCol = createListCheckbox("notInterested");
        tr.appendChild(itemCol);
        tr.appendChild(sizeCol);
        tr.appendChild(priceCol);
        tr.appendChild(notNowCol);
        tr.appendChild(notInterestedCol);
        document.getElementById("listBody").appendChild(tr);
    }
    addRowEventListener();
    addCheckboxEventListeners("notNow", "ignored");
    addCheckboxEventListeners("notInterested", "rejected");
}
function createListCheckbox(name){
    var tableCol = document.createElement("th");
    var checkbox = document.createElement("input");
    checkbox.setAttribute("type", "checkbox");
    checkbox.setAttribute("class", name);
    tableCol.appendChild(checkbox);
    return tableCol;
}
function createListCol(value){
    var thing = document.createElement("th");
    var textNode = document.createTextNode(value);
    thing.appendChild(textNode);
    return thing;
}
function addCheckboxEventListeners(className, rowClass){
    var checkboxList = document.getElementsByClassName(className);
    var i;
    for(i=0;i<checkboxList.length;i++){
        checkboxList[i].addEventListener('click', function(ev){
            if(ev.target.tagName === "INPUT"){
                ev.target.parentElement.parentElement.classList.toggle(rowClass);
            }
        }, false);
    }

}
function addRowEventListener(){
    var list = document.getElementById('list');
    list.addEventListener('click', function(ev) {
    if(ev.target.tagName === 'TH'){
        ev.target.parentElement.classList.toggle('bought');
    }
    },false);
}