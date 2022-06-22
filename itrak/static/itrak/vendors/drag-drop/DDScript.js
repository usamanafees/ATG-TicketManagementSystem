/*
* Created by Raju Dasa on 30-oct-2011
* www.RajuDasa.blogspot.com
* free source, change code for ur purpose.
*/
function dragload()
{            
    // $("#list1").empty().addItems($json);
        
    $("#list1, #list2").sortable({
        connectWith: ".connectedSortable",
         beforeStop: function(event, ui) {
             ui.helper.removeClass("selectedItem");
             ui.helper.off();
         },
        change: function(event, ui) {  //for issue solving                    
            var placeHolder = ui.helper.children(".ui-sortable-placeholder");
            if(placeHolder){
                placeHolder.detach().appendTo(ui.helper.parent());
            }
        },
        start: function(event, ui) { 
            if(ui.helper){
                var cnt = ui.helper.parent().children(".selectedItem:not(.ui-sortable-placeholder)").length;
                if(cnt > 1)
                {
                    var parent = ui.helper.parent();
                    var childs = parent.children("div.selectedItem:not(.ui-sortable-placeholder)");
                    $.each(childs, function(index, child) {
                        child = $(child);
                        if(ui.helper.attr('id') != child.attr('id'))
                        { 
                            child = child.detach();
                            child.appendTo(ui.helper);
                            child.css("margin","0px").css("padding","0px"); //addClass not working
                        }
                    });
                }
            }
         },
        stop: function(event, ui) {  
            //console.log(ui.helper);
            if(ui.item){
                var cnt = $(ui.item[0]).children("div").length;
                if(cnt > 0)
                {
                    //ui.helper is null
                    var dropItem = $(ui.item[0]);
                    $.each(dropItem.children("div"), function(index, child) {                                                               
                            child = $(child).detach();
                            child.insertAfter(dropItem);
                            child.removeClass("selectedItem");
                            child.css("margin","").css("padding","");
                    });
                }
            }
         }
    }).disableSelection();

    jQuery.fn.extend({
        live: function (event, callback) {
           if (this.selector) {
                jQuery(document).on(event, this.selector, callback);
            }
            return this;
        }
    });

    //click color handling
   $("#list1>div, #list2>div").live("click",function(e){
   if(!e.ctrlKey)
   {
       $(this).parent().children().removeClass("selectedItem"); 
   }
   $(this).toggleClass("selectedItem"); 
   });           
}
  
//custom jq function/plugin : used instead of template plugin
$.fn.addItems = function(data) {
return this.each(function() {
	var parent = this;
	$.each(data, function(index, itemData) {
		$("<div>")
       .text(itemData.name)
       .attr("id", "div"+itemData.id)
       .appendTo(parent); 
	});
});
};

//finally create json
var json;
function CreateJson()
{
    json = "[";
    $.each( $("#list2>div"), function(index, div) {
        var $div = $(div);
        if(index>0) json += ",";
        json += '{"id":' + $div.attr('id').replace("div","");
        json += ',"name":"' + $div.text() + '"}';
    });
    json = json + "]";
    $("#hidJsonHolder").val(json);
    return json;
}