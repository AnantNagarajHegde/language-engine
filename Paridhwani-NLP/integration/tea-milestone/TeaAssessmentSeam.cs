using System;
using System.Collections.Generic;
using System.Text.RegularExpressions;
using Paridhwani;
using Paridhwani.AssessmentExample;

namespace Paridhwani.TeaMilestoneExample
{
    // Isolated test seam, not attached to TeaStallSession or the game's UI.
    public sealed class TeaAssessmentPolicy
    {
        public bool? AdvanceAccepted,AdvanceCorrections,AllowCodeMixing;
    }
    public sealed class PendingTeaAssessment
    {
        internal readonly long Generation;
        internal readonly TeaTurn Turn;
        internal readonly string RequestId,Input;
        internal bool Consumed;
        internal PendingTeaAssessment(long generation,TeaTurn turn,string id,string input)
        {Generation=generation;Turn=turn;RequestId=id;Input=input;}
    }
    public sealed class TeaAssessmentSeam
    {
        readonly ITeaConversationProvider provider;
        readonly TeaProgress progress;
        readonly TeaAssessmentPolicy policy;
        readonly string revision;
        long generation;
        readonly HashSet<string> usedIds=new HashSet<string>(StringComparer.Ordinal);
        public TeaTurn Turn {get;private set;}
        public TeaAssessmentSeam(ITeaConversationProvider provider,TeaProgress progress,TeaAssessmentPolicy policy,string revision)
        {this.provider=provider;this.progress=progress;this.policy=policy;this.revision=revision;Turn=provider.Start(progress);}
        public PendingTeaAssessment Begin(string id,string input)
        {
            generation++;
            // No conductor-thanks/greeting conflation and no implicit later-turn mapping.
            return Turn?.Id=="order" && id!=null && Regex.IsMatch(id,"^[0-9a-f]{32}$") && usedIds.Add(id)?new PendingTeaAssessment(generation,Turn,id,input):null;
        }
        public void CancelOrSuspend(){generation++;}
        // Notebook/original-line/cancel/new-turn/leave should invalidate pending work.
        // Real UI event wiring remains pending; callers retain normal authored choices.
        public void ChooseAuthored(int index)
        {generation++;Turn=provider.Reply(Turn,index,progress);}
        static string Normalize(string value)=>Regex.Replace(Regex.Replace((value??"").ToLowerInvariant(),"[^a-z ]"," ")," +"," ").Trim();
        public string Deliver(PendingTeaAssessment pending,byte[] bytes)
        {
            if(pending==null || pending.Consumed || pending.Generation!=generation || !ReferenceEquals(Turn,pending.Turn))return "stale";
            pending.Consumed=true;
            if(!AssessmentConsumer.TryRead(bytes,pending.RequestId,"q1_2","q1_2_a",revision,new HashSet<string>{"a_tea","e_beda","e_nimage"},out var assessment))return "unavailable";
            if(assessment.Outcome=="not_accepted")return "rejected";
            string text=Normalize(pending.Input);
            int choice=-1;
            bool mixed=text=="tea beku";
            if(new HashSet<string>{"nanage chaha beku","chaha beku","cha","tea beku"}.Contains(text))choice=0;
            if(new HashSet<string>{"nanage neeru beku","neeru beku"}.Contains(text))choice=1;
            // a_tea is also returned for coffee/milk/food. It is NOT a drink command.
            if(choice<0 || assessment.AnswerId!="a_tea")return "unsupported-item-or-input";
            if(mixed && !policy.AllowCodeMixing.HasValue)return "policy-pending";
            if(mixed && !policy.AllowCodeMixing.Value)return "code-mixing-disabled";
            bool? advance=assessment.Outcome=="accepted_with_correction"?policy.AdvanceCorrections:policy.AdvanceAccepted;
            if(!advance.HasValue)return "policy-pending";
            if(!advance.Value)return "feedback-only";
            // Revalidate the local authored slot, not a server-supplied effect.
            string effect=choice==0?"tea":"water";
            string roman=choice==0?"nanage chaha beku":"nanage neeru beku";
            if(Turn.Id!="order" || Turn.Choices.Count!=3 || Turn.Choices[choice].Effect!=effect || Normalize(Turn.Choices[choice].Line.Roman)!=roman || Turn.Choices[choice].Next!="served")return "mapping-mismatch";
            Turn=provider.Reply(Turn,choice,progress);generation++;
            return "advanced";
        }
    }
}
