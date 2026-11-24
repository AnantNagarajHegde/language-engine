using System;
using System.Collections.Generic;
using System.IO;
using System.Text.Json;

namespace Paridhwani.AssessmentExample
{
    // Standalone example only. No Unity API, quest effect, save, or network access.
    public sealed class AssessmentResult
    {
        public readonly string Outcome, AnswerId, ErrorCategory, CorrectionType, ReactionId;
        public AssessmentResult(string outcome,string answer,string error,string correction,string reaction)
        {Outcome=outcome;AnswerId=answer;ErrorCategory=error;CorrectionType=correction;ReactionId=reaction;}
    }

    public static class AssessmentConsumer
    {
        static void Require(bool condition) {if(!condition)throw new InvalidDataException("Assessment unavailable.");}
        static void Shape(JsonElement obj,params string[] names)
        {
            Require(obj.ValueKind==JsonValueKind.Object);
            var found=new HashSet<string>(StringComparer.Ordinal);
            foreach(var p in obj.EnumerateObject())Require(Array.IndexOf(names,p.Name)>=0 && found.Add(p.Name));
            Require(found.Count==names.Length);
        }
        static string Text(JsonElement obj,string key)
        {
            var value=obj.GetProperty(key);Require(value.ValueKind==JsonValueKind.String);
            string text=value.GetString();Require(text!=null && text.Length<=128);
            foreach(char c in text)Require((c>='a'&&c<='z')||(c>='0'&&c<='9')||c=='_');
            return text;
        }
        public static AssessmentResult Read(byte[] body,string requestId,string questId,string stepId,string expectedRevision,ISet<string> allowedAnswers)
        {
            Require(body!=null && body.Length<=65536 && allowedAnswers!=null);
            using(var document=JsonDocument.Parse(body,new JsonDocumentOptions{MaxDepth=8}))
            {
                var root=document.RootElement;
                // Errors/timeouts belong to the caller's unavailable/fallback path.
                Shape(root,"version","request_id","quest_id","step_id","status","content_revision","assessment");
                Require(root.GetProperty("version").TryGetInt32(out int version)&&version==1);
                Require(Text(root,"request_id")==requestId && Text(root,"quest_id")==questId && Text(root,"step_id")==stepId);
                Require(Text(root,"status")=="ok" && Text(root,"content_revision")==expectedRevision);
                var a=root.GetProperty("assessment");
                Shape(a,"outcome","answer_id","error_category","correction_type","reaction_id","detected_form","confidence");
                string outcome=Text(a,"outcome"),answer=Text(a,"answer_id"),error=Text(a,"error_category"),correction=Text(a,"correction_type"),reaction=Text(a,"reaction_id");
                Require(new HashSet<string>{"kanglish","kannada","english","hindi_roman","mixed","digits","noise"}.Contains(Text(a,"detected_form")));
                Require(a.GetProperty("confidence").TryGetDouble(out double confidence)&&double.IsFinite(confidence)&&confidence>=0&&confidence<=1);
                if(outcome=="not_accepted")Require(error.Length>0 && correction.Length==0 && (answer.Length==0 || allowedAnswers.Contains(answer)));
                else {Require(outcome=="accepted"||outcome=="accepted_with_correction");Require(allowedAnswers.Contains(answer)&&error.Length==0);Require((outcome=="accepted_with_correction")== (correction.Length>0));}
                // UI maps these IDs through its pinned content, with a safe fallback
                // for unknown error/reaction IDs. Never dispatch arbitrary commands.
                return new AssessmentResult(outcome,answer,error,correction,reaction);
            }
        }
        public static bool TryRead(byte[] body,string requestId,string questId,string stepId,string expectedRevision,ISet<string> allowedAnswers,out AssessmentResult result)
        {
            result=null;
            try {result=Read(body,requestId,questId,stepId,expectedRevision,allowedAnswers);return true;}
            catch(Exception e) when(e is InvalidDataException || e is JsonException || e is InvalidOperationException || e is KeyNotFoundException || e is ArgumentException)
            {return false;}
        }
    }

    public static class ConsumerChecks
    {
        public static int Main(string[] args)
        {
            string root=args[0];byte[] accepted=File.ReadAllBytes(Path.Combine(root,"accepted-response.json"));
            string revision;using(var doc=JsonDocument.Parse(accepted))revision=doc.RootElement.GetProperty("content_revision").GetString();
            var answers=new HashSet<string>{"a_tea","e_beda"};const string id="0123456789abcdef0123456789abcdef";
            if(AssessmentConsumer.Read(accepted,id,"q1_2","q1_2_a",revision,answers).Outcome!="accepted")return 1;
            var rejected=File.ReadAllBytes(Path.Combine(root,"rejected-response.json"));
            if(AssessmentConsumer.Read(rejected,id,"q1_2","q1_2_a",revision,answers).Outcome!="not_accepted")return 1;
            var corrected=File.ReadAllBytes(Path.Combine(root,"corrected-response.json"));
            if(AssessmentConsumer.Read(corrected,id,"q1_3","q1_3_a",revision,new HashSet<string>{"a_name"}).CorrectionType!="missing_possessive")return 1;
            foreach(var item in new[]{"wrong-request","wrong-quest","wrong-step","wrong-revision","foreign-answer","error-envelope","duplicate-field","command","malformed-json","typed-version"})
            {
                byte[] body=accepted;string rid=id,quest="q1_2",step="q1_2_a",rev=revision;ISet<string> allow=answers;
                if(item=="wrong-request")rid="00000000000000000000000000000000";
                if(item=="wrong-quest")quest="q2_1";
                if(item=="wrong-step")step="q1_2_b";
                if(item=="wrong-revision")rev=new string('0',64);
                if(item=="foreign-answer")allow=new HashSet<string>();
                if(item=="error-envelope")body=File.ReadAllBytes(Path.Combine(root,"unknown-step-response.json"));
                if(item=="malformed-json")body=System.Text.Encoding.UTF8.GetBytes("{}");
                if(item=="typed-version")body=System.Text.Encoding.UTF8.GetBytes(System.Text.Encoding.UTF8.GetString(body).Replace("\"version\": 1","\"version\": true"));
                if(item=="duplicate-field"||item=="command")
                {
                    string json=System.Text.Encoding.UTF8.GetString(accepted);
                    body=System.Text.Encoding.UTF8.GetBytes(json.Insert(json.LastIndexOf('}'),item=="command"?",\"effect\":\"win\"":",\"status\":\"ok\""));
                }
                if(AssessmentConsumer.TryRead(body,rid,quest,step,rev,allow,out _))return 1;
            }
            Console.WriteLine("ASSESSMENT_CONSUMER_CHECKED: 3 accepted/corrected/rejected fixtures and 10 invalid cases; no sockets or Unity calls.");return 0;
        }
    }
}
