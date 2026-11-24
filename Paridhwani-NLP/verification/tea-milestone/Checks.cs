using System;
using System.IO;
using System.Text;
using System.Text.Json;
using Paridhwani;
using Paridhwani.TeaMilestoneExample;

public sealed class TestProgressCodec : ITeaProgressCodec
{
    static readonly JsonSerializerOptions Options=new JsonSerializerOptions{IncludeFields=true,IgnoreReadOnlyProperties=true};
    public string Encode(TeaProgress p)=>JsonSerializer.Serialize(p,Options);
    public TeaProgress Decode(string json)=>JsonSerializer.Deserialize<TeaProgress>(json,Options);
}
public static class TeaMilestoneChecks
{
    static int checks;static string root,revision;
    static readonly TestProgressCodec codec=new TestProgressCodec();
    static void Check(bool condition,string message){checks++;if(!condition)throw new Exception(message);}
    static byte[] Response(string name)=>File.ReadAllBytes(Path.Combine(root,name+"-response.json"));
    static PendingTeaAssessment Begin(TeaAssessmentSeam seam,string name)
    {
        byte[] bytes=File.ReadAllBytes(Path.Combine(root,name+"-request.json"));
        using(var doc=JsonDocument.Parse(bytes))
            return seam.Begin(doc.RootElement.GetProperty("request_id").GetString(),doc.RootElement.GetProperty("learner_text").GetString());
    }
    static TeaAssessmentPolicy Policy(bool? advance=true,bool? corrected=false,bool? mixed=false)=>new TeaAssessmentPolicy{AdvanceAccepted=advance,AdvanceCorrections=corrected,AllowCodeMixing=mixed};
    static TeaAssessmentSeam New(out TeaProgress p,TeaAssessmentPolicy policy=null,string rev=null)
    {
        p=new TeaProgress{english=false,roman=true,textScale=1.2f,arrivalAcknowledged=true};
        var seam=new TeaAssessmentSeam(new LocalTeaConversation(),p,policy??Policy(),rev??revision);
        Check(seam.Turn.Id=="hello","real story starts at greeting");
        Check(seam.Begin(new string('a',32),"Namaskara")==null,"greeting has no fabricated curriculum mapping");
        seam.ChooseAuthored(0);Check(p.greeted && seam.Turn.Id=="order","actual authored greeting advances to order");return seam;
    }
    static void NoMutation(TeaAssessmentSeam seam,TeaProgress p,PendingTeaAssessment pending,byte[] body,string expected)
    {
        string before=codec.Encode(p);var turn=seam.Turn;string choices=JsonSerializer.Serialize(turn.Choices.Count);
        Check(seam.Deliver(pending,body)==expected,"decision "+expected);
        Check(codec.Encode(p)==before && ReferenceEquals(turn,seam.Turn) && JsonSerializer.Serialize(turn.Choices.Count)==choices,"non-advance preserves entire real progress and fallback choices");
    }
    public static int Main(string[] args)
    {
        root=args[0];using(var doc=JsonDocument.Parse(Response("tea")))revision=doc.RootElement.GetProperty("content_revision").GetString();
        foreach(string drink in new[]{"tea","water"})
        {
            var seam=New(out var p);var pending=Begin(seam,drink);Check(seam.Deliver(pending,Response(drink))=="advanced","advance "+drink);
            Check(p.drinkOrdered && p.drink==drink && !p.directionsKnown && seam.Turn.Id=="served","real provider chooses correct drink only");
            Check(!p.english && p.roman && p.textScale==1.2f,"language/help preferences preserved");
            string snapshot=codec.Encode(p);Check(seam.Deliver(pending,Response(drink))=="stale" && codec.Encode(p)==snapshot,"duplicate cannot advance again");
            string savePath=Path.Combine(root,"save-"+drink+"-"+Guid.NewGuid().ToString("N")+".json");
            var store=new TeaSaveStore(savePath,codec);Check(store.Write(p,out _),"actual save store write");
            Check(store.TryRestore(out var restored,out _) && restored.drink==drink && restored.greeted && restored.arrivalAcknowledged && !restored.directionsKnown && !restored.english,"actual save restore with injected non-native codec");
        }
        foreach(string name in new[]{"coffee","milk","chapati"})
        {var seam=New(out var p);NoMutation(seam,p,Begin(seam,name),Response(name),"unsupported-item-or-input");seam.ChooseAuthored(1);Check(p.drink=="water","unsupported item still allows authored water fallback");}
        foreach(string name in new[]{"rejected","greeting","malformed-input"})
        {var seam=New(out var p);NoMutation(seam,p,Begin(seam,name),Response(name),"rejected");seam.ChooseAuthored(2);Check(seam.Turn.Id=="clarify" && !p.drinkOrdered,"authored refusal stays valid despite lesson rejection");seam.ChooseAuthored(0);Check(p.drink=="water","clarification water fallback");}
        foreach(bool? advance in new bool?[]{null,false,true})
        {var seam=New(out var p,Policy(advance));string expected=!advance.HasValue?"policy-pending":advance.Value?"advanced":"feedback-only";var pending=Begin(seam,"tea");if(advance==true)Check(seam.Deliver(pending,Response("tea"))==expected,"explicit accepted advancement policy");else NoMutation(seam,p,pending,Response("tea"),expected);}
        {var seam=New(out var p,new TeaAssessmentPolicy());NoMutation(seam,p,Begin(seam,"tea"),Response("tea"),"policy-pending");}
        foreach(bool? correction in new bool?[]{null,false,true})
        {var seam=New(out var p,Policy(true,correction));var pending=Begin(seam,"correction");string expected=!correction.HasValue?"policy-pending":correction.Value?"advanced":"feedback-only";if(correction==true)Check(seam.Deliver(pending,Response("correction"))==expected && p.drink=="tea","explicit correction advance");else NoMutation(seam,p,pending,Response("correction"),expected);}
        foreach(bool? mixed in new bool?[]{null,false,true})
        {var seam=New(out var p,Policy(true,false,mixed));var pending=Begin(seam,"english-mix");string expected=!mixed.HasValue?"policy-pending":mixed.Value?"advanced":"code-mixing-disabled";if(mixed==true)Check(seam.Deliver(pending,Response("english-mix"))==expected && p.drink=="tea","explicit mixing policy");else NoMutation(seam,p,pending,Response("english-mix"),expected);}
        foreach(string fault in new[]{"wrong-revision","malformed","error","wrong-id","command","duplicate-property"})
        {
            var seam=New(out var p,rev:fault=="wrong-revision"?new string('0',64):null);var pending=Begin(seam,"tea");byte[] body=Response("tea");
            if(fault=="malformed")body=Encoding.UTF8.GetBytes("{");if(fault=="error")body=Response("error");
            if(fault=="wrong-id")body=Response("water");
            if(fault=="command"||fault=="duplicate-property"){string json=Encoding.UTF8.GetString(body);body=Encoding.UTF8.GetBytes(json.Insert(json.LastIndexOf('}'),fault=="command"?",\"effect\":\"water\"":",\"status\":\"ok\""));}
            NoMutation(seam,p,pending,body,"unavailable");seam.ChooseAuthored(0);Check(p.drink=="tea","offline/error keeps normal choice available");
        }
        foreach(string action in new[]{"cancel","notebook","original-line","leave","newer-request","authored-choice"})
        {
            var seam=New(out var p);var old=Begin(seam,"tea");
            if(action=="newer-request")Begin(seam,"water");else if(action=="authored-choice")seam.ChooseAuthored(2);else seam.CancelOrSuspend();
            NoMutation(seam,p,old,Response("tea"),"stale");
        }
        {var seam=New(out var p);var pending=Begin(seam,"tea");seam.Turn.Choices[0].Effect="directions";NoMutation(seam,p,pending,Response("tea"),"mapping-mismatch");}
        {var seam=New(out var p);Begin(seam,"tea");Check(Begin(seam,"tea")==null,"reused request ID rejected");}
        {
            var seam=New(out var p,Policy(false));string path=Path.Combine(root,"feedback-save-"+Guid.NewGuid().ToString("N")+".json");var store=new TeaSaveStore(path,codec);
            Check(store.Write(p,out _),"save before feedback");string before=File.ReadAllText(path);
            NoMutation(seam,p,Begin(seam,"tea"),Response("tea"),"feedback-only");Check(File.ReadAllText(path)==before,"feedback does not rewrite save");
        }
        Console.WriteLine("TEA_MILESTONE_CHECKED: "+checks+" assertions; real Python assessment JSON + current TeaConversation/TeaProgress/TeaSaveStore source; isolated adapter only.");
        Console.WriteLine("PENDING: gameplay policy decisions, production attachment, live transport, native UI/help events and native JsonUtility acceptance.");
        return 0;
    }
}
