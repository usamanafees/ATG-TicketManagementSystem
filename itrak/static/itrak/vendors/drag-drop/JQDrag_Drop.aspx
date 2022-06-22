<%@ Page Language="C#" AutoEventWireup="true" CodeFile="JQDrag_Drop.aspx.cs" Inherits="JQDrag_Drop" %>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head id="Head1" runat="server">
    <meta charset="utf-8" />
	<meta name="author" content="Raju Dasa"/>
    <title>Drag & drop custom list items</title>
   
    <script src="jquery-1.4.4.min.js" type="text/javascript"></script>
    <script src="jquery-ui-1.8.16.min.js" type="text/javascript"></script>
    <script src="DDScript.js" type="text/javascript"></script>
     <script type="text/javascript">
        $(function () {        
            //Get data and fill first box
            var $json = <% =GetJsonData() %>;
            pageload($json);
            });
    </script>
<link type="text/css" href="DDStyle.css" rel="Stylesheet" />
</head>
<body>
    <form id="form1" runat="server">
    <div>
        <div>
            content from site: http://jqueryui.com/demos/sortable/#connect-lists
        </div>
       
        <br />
        <br />
       
        <div>          
            <div class="ContainerCenter">
                <table><tr><td>Source</td><td>Destination</td></tr></table>
                <div id="list1" class="connectedSortable">
                    <div id="div11">item 11</div>
                    <div id="div13">item<div>13</div></div>                    
                </div>
                <div id="list2" class="connectedSortable">
                </div>
            </div>         
        </div>
    <div style="clear: both;">    </div>
  
    <asp:Button Text="GetLength" runat="server" ID="btnFinal" OnClick="btnFinal_Click" OnClientClick="CreateJson()"/>
    <br />
    <asp:TextBox id="txta" runat="server" TextMode="MultiLine" Width="400"/>
    <asp:HiddenField runat="server" ID="hidJsonHolder" />
   
    </div>
    </form>
</body>
</html>
