using System;
using System.Collections.Generic;
using System.Linq;
using System.Web;
using System.Web.UI;
using System.Web.UI.WebControls;
using System.Web.Script.Serialization;

public partial class JQDrag_Drop : System.Web.UI.Page
{
    protected void Page_Load(object sender, EventArgs e)
    {

    }
    protected string GetJsonData()
    {
        List<Person> personList = new List<Person>
        {
            new Person{name="raj", id=1},
            new Person{name="ramu", id=2},
            new Person{name="prakash", id=3},
            new Person{name="rakesh", id=4},
            new Person{name="satish", id=5}            
        };

        List<Person> someList = (from item in personList
                       select new Person{ id = item.id, name = item.name }).ToList<Person>();

        JavaScriptSerializer jsSer = new JavaScriptSerializer();
        string str = jsSer.Serialize(someList);

        return str;
    }

    protected void btnFinal_Click(object sender, EventArgs e)
    {
        JavaScriptSerializer jsSer = new JavaScriptSerializer();
        object obj = jsSer.DeserializeObject(hidJsonHolder.Value); 
        Person[] listPerson = jsSer.ConvertToType<Person[]>(obj);
        //int count = listPerson.Length;
        foreach (Person p in listPerson)
        { txta.Text += p.ToString(); }
    }

    //class for DTO
    class Person
    {
        public string name { get; set; }
        public int id { get; set; }
       public override string  ToString()
        {
            return string.Format("[id={0};name={1}]\n", id, name);
          //return base.ToString();
        }
    }
}